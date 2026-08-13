from __future__ import annotations

import io
import os
import re

import pytesseract

from PIL import Image, ImageEnhance, ImageFilter


# ============================================================
# TESSERACT CONFIGURATION
# ============================================================

# Windows → use local Tesseract installation.
# Render/Linux → use Tesseract available in PATH.
if os.name == "nt":
    pytesseract.pytesseract.tesseract_cmd = (
        r"C:\Program Files\Tesseract-OCR\tesseract.exe"
    )

class OCRService:

    def __init__(self):
        pass

    def preprocess_image(self, image):

        image = image.convert("L")

        image = image.resize(
            (
                image.width * 4,
                image.height * 4
            )
        )

        image = ImageEnhance.Contrast(
            image
        ).enhance(2)

        image = ImageEnhance.Sharpness(
            image
        ).enhance(3)

        image = image.filter(
            ImageFilter.SHARPEN
        )

        return image

    def clean_text(self, text):

        text = re.sub(
            r"[^\w\s.,!?@#%:/\-]",
            " ",
            text
        )

        text = re.sub(
            r"\s+",
            " ",
            text
        )

        return text.strip()

    def detect_publisher(self, text: str) -> dict:
        """
        Detect the visible publisher/source from OCR text.

        Priority:
        1. Known publisher names
        2. Social-media handles
        3. Generic visible source name from the beginning of OCR text

        Never invent a publisher when there is no reasonable source signal.
        """

        if not text:
            return {
                "publisher": None,
                "confidence": 0,
                "method": None,
            }

        normalized = text.lower()

        # =========================================================
        # 1. KNOWN PUBLISHERS
        # =========================================================

        publishers = {
            "tv9 kannada": "TV9 Kannada",
            "tv9kannada": "TV9 Kannada",
            "tv9": "TV9",

            "rvcj": "RVCJ",

            "ndtv": "NDTV",
            "bbc news": "BBC News",
            "bbc": "BBC",
            "cnn": "CNN",
            "reuters": "Reuters",

            "times of india": "Times of India",
            "the times of india": "Times of India",

            "india today": "India Today",
            "india tv": "India TV",

            "hindustan times": "Hindustan Times",
            "the hindu": "The Hindu",

            "news18": "News18",
            "aaj tak": "Aaj Tak",
            "zee news": "Zee News",
            "abp news": "ABP News",

            "republic tv": "Republic TV",
            "republic bharat": "Republic Bharat",

            "the indian express": "The Indian Express",
            "indian express": "The Indian Express",
        }

        candidates = sorted(
            publishers.items(),
            key=lambda item: len(item[0]),
            reverse=True,
        )

        for keyword, publisher in candidates:

            if keyword in normalized:

                return {
                    "publisher": publisher,
                    "confidence": 95,
                    "method": "ocr_known_publisher",
                }

        # =========================================================
        # 2. SOCIAL MEDIA HANDLE
        # =========================================================

        handles = re.findall(
            r"@([A-Za-z0-9_\.]{3,40})",
            text,
        )

        if handles:

            handle = handles[0]

            # Don't treat random @ symbols as publishers.
            if handle.lower() not in {
                "user",
                "gmail",
                "instagram",
                "twitter",
                "facebook",
            }:

                publisher = handle

                # Convert common handle style into readable name.
                publisher = publisher.replace("_", " ").strip()

                return {
                    "publisher": publisher,
                    "confidence": 80,
                    "method": "ocr_social_handle",
                }

        # =========================================================
        # 3. GENERIC VISIBLE SOURCE
        # =========================================================

        lines = [
            line.strip()
            for line in text.splitlines()
            if line.strip()
        ]

        ignored = {
            "breaking",
            "live",
            "exclusive",
            "watch live",
            "subscribe",
            "suggested for you",
            "follow",
            "share",
            "comment",
            "like",
            "repost",
            "reply",
            "views",
        }

        for line in lines[:12]:

            clean = re.sub(
                r"[^A-Za-z0-9&.'@ _-]",
                "",
                line,
            ).strip()

            if len(clean) < 4:
                continue

            if len(clean) > 50:
                continue

            lower = clean.lower()

            if lower in ignored:
                continue

            words = clean.split()

            # A short, clean OCR line is a possible visible source.
            if 1 <= len(words) <= 6:

                return {
                    "publisher": clean,
                    "confidence": 65,
                    "method": "ocr_visible_source",
                }

        # =========================================================
        # 4. NOTHING RELIABLE FOUND
        # =========================================================

        return {
            "publisher": None,
            "confidence": 0,
            "method": None,
        }
        
    def extract_text_from_image(self, image_bytes):

        try:

            image = Image.open(
                io.BytesIO(image_bytes)
            )

            processed = self.preprocess_image(
                image
            )

            raw_text = pytesseract.image_to_string(
                processed,
                config="--psm 6"
            )

            cleaned = self.clean_text(
                raw_text
            )

            publisher_info = self.detect_publisher(
                cleaned
            )

            return {

                "status": "success",

                "extracted_text": cleaned,

                "post_text": cleaned,

                "engagement_text": "",

                "ordered_values": {},

                "raw_text": raw_text,

                "confidence": 90,

                "publisher":
                    publisher_info["publisher"],

                "publisher_confidence":
                    publisher_info["confidence"],

                "publisher_detection_method":
                    publisher_info["method"],

                "word_count":
                    len(cleaned.split()),

                "language": "Unknown",

                "ready_for_analysis": True

            }

        except Exception as e:

            return {

                "status": "error",

                "message": str(e)

            }


ocr_service = OCRService()
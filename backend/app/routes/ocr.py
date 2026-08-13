from __future__ import annotations

import io
import os
import re

import pytesseract
from fastapi import APIRouter, File, HTTPException, UploadFile
from PIL import Image, ImageEnhance, ImageFilter


# ============================================================
# TESSERACT CONFIGURATION
# ============================================================

# Windows:
# Use the locally installed Tesseract path.
#
# Render/Linux:
# Do NOT set a Windows path.
# Tesseract will be found automatically from PATH.
if os.name == "nt":
    pytesseract.pytesseract.tesseract_cmd = (
        r"C:\Program Files\Tesseract-OCR\tesseract.exe"
    )


router = APIRouter()


# ============================================================
# OCR SERVICE
# ============================================================

class OCRService:

    def __init__(self):
        pass

    # ========================================================
    # IMAGE PREPROCESSING
    # ========================================================

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

    # ========================================================
    # TEXT CLEANING
    # ========================================================

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

    # ========================================================
    # PUBLISHER DETECTION
    # ========================================================

    def detect_publisher(self, text: str) -> dict:

        """
        Detect the visible publisher/source from OCR text.

        Priority:
        1. Known publisher names
        2. Social-media handles
        3. Generic visible source name

        Never invent a publisher when there is no reliable signal.
        """

        if not text:

            return {
                "publisher": None,
                "confidence": 0,
                "method": None,
            }

        normalized = text.lower()

        # =====================================================
        # 1. KNOWN PUBLISHERS
        # =====================================================

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

        # =====================================================
        # 2. SOCIAL MEDIA HANDLE
        # =====================================================

        handles = re.findall(
            r"@([A-Za-z0-9_.]{3,40})",
            text,
        )

        ignored_handles = {
            "user",
            "gmail",
            "instagram",
            "twitter",
            "facebook",
        }

        for handle in handles:

            if handle.lower() in ignored_handles:
                continue

            publisher = handle.replace(
                "_",
                " ",
            ).strip()

            if publisher:

                return {
                    "publisher": publisher,
                    "confidence": 80,
                    "method": "ocr_social_handle",
                }

        # =====================================================
        # 3. GENERIC VISIBLE SOURCE
        # =====================================================

        lines = [
            line.strip()
            for line in text.splitlines()
            if line.strip()
        ]

        ignored_phrases = (
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
        )

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

            if any(
                phrase in lower
                for phrase in ignored_phrases
            ):
                continue

            words = clean.split()

            if 1 <= len(words) <= 6:

                return {
                    "publisher": clean,
                    "confidence": 65,
                    "method": "ocr_visible_source",
                }

        # =====================================================
        # 4. NOTHING RELIABLE FOUND
        # =====================================================

        return {
            "publisher": None,
            "confidence": 0,
            "method": None,
        }

    # ========================================================
    # OCR EXTRACTION
    # ========================================================

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

                "ready_for_analysis": True,
            }

        except Exception as e:

            return {

                "status": "error",

                "message": str(e),
            }


# ============================================================
# SERVICE INSTANCE
# ============================================================

ocr_service = OCRService()


# ============================================================
# OCR API ENDPOINT
# ============================================================

@router.post("/")
async def extract_ocr(
    file: UploadFile = File(...)
):

    if not file.filename:

        raise HTTPException(
            status_code=400,
            detail="No file provided."
        )

    try:

        image_bytes = await file.read()

        if not image_bytes:

            raise HTTPException(
                status_code=400,
                detail="Uploaded file is empty."
            )

        result = ocr_service.extract_text_from_image(
            image_bytes
        )

        if result.get("status") == "error":

            raise HTTPException(
                status_code=500,
                detail=result.get(
                    "message",
                    "OCR processing failed."
                )
            )

        return result

    except HTTPException:
        raise

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )
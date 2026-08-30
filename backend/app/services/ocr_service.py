from __future__ import annotations

import io
import logging
import os
import re

import pytesseract
from PIL import Image, ImageEnhance, ImageFilter, UnidentifiedImageError


logger = logging.getLogger(__name__)

if os.name == "nt":
    pytesseract.pytesseract.tesseract_cmd = (
        r"C:\Program Files\Tesseract-OCR\tesseract.exe"
    )


class OCRService:

    MAX_FILE_SIZE = 10 * 1024 * 1024
    MAX_INPUT_PIXELS = 20_000_000
    MAX_DIMENSION = 5000
    MAX_PROCESSED_DIMENSION = 3000

    ALLOWED_FORMATS = {
        "JPEG",
        "PNG",
        "WEBP",
        "BMP",
        "TIFF",
    }

    def preprocess_image(self, image):

        image = image.convert("L")

        scale = 4

        target_width = image.width * scale
        target_height = image.height * scale

        longest_side = max(
            target_width,
            target_height
        )

        if longest_side > self.MAX_PROCESSED_DIMENSION:

            ratio = (
                self.MAX_PROCESSED_DIMENSION /
                longest_side
            )

            target_width = max(
                1,
                int(target_width * ratio)
            )

            target_height = max(
                1,
                int(target_height * ratio)
            )

        image = image.resize(
            (
                target_width,
                target_height
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

        if not text:
            return {
                "publisher": None,
                "confidence": 0,
                "method": None,
            }

        normalized = text.lower()

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

        handles = re.findall(
            r"@([A-Za-z0-9_\.]{3,40})",
            text,
        )

        if handles:

            handle = handles[0]

            if handle.lower() not in {
                "user",
                "gmail",
                "instagram",
                "twitter",
                "facebook",
            }:

                publisher = (
                    handle
                    .replace("_", " ")
                    .strip()
                )

                return {
                    "publisher": publisher,
                    "confidence": 80,
                    "method": "ocr_social_handle",
                }

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

            if 1 <= len(words) <= 6:

                return {
                    "publisher": clean,
                    "confidence": 65,
                    "method": "ocr_visible_source",
                }

        return {
            "publisher": None,
            "confidence": 0,
            "method": None,
        }

    def calculate_ocr_confidence(self, data):

        confidences = []

        for value in data.get("conf", []):

            try:
                confidence = float(value)

                if confidence >= 0:
                    confidences.append(
                        confidence
                    )

            except (
                TypeError,
                ValueError
            ):
                continue

        if not confidences:
            return None

        return round(
            sum(confidences) /
            len(confidences),
            2
        )

    def validate_image(self, image_bytes):

        if not image_bytes:
            raise ValueError(
                "Empty image file."
            )

        if len(image_bytes) > self.MAX_FILE_SIZE:
            raise ValueError(
                "Image file is too large. Maximum allowed size is 10 MB."
            )

        try:

            image = Image.open(
                io.BytesIO(image_bytes)
            )

            image.verify()

        except UnidentifiedImageError:

            raise ValueError(
                "Invalid or unsupported image file."
            )

        except Exception:

            raise ValueError(
                "Unable to read the image file."
            )

        image = Image.open(
            io.BytesIO(image_bytes)
        )

        if image.format not in self.ALLOWED_FORMATS:
            raise ValueError(
                "Unsupported image format."
            )

        if image.width <= 0 or image.height <= 0:
            raise ValueError(
                "Invalid image dimensions."
            )

        if (
            image.width > self.MAX_DIMENSION
            or image.height > self.MAX_DIMENSION
        ):
            raise ValueError(
                "Image dimensions are too large. "
                "Maximum dimension is 5000 pixels."
            )

        if (
            image.width * image.height
            > self.MAX_INPUT_PIXELS
        ):
            raise ValueError(
                "Image contains too many pixels."
            )

        return image

    def extract_text_from_image(self, image_bytes):

        try:

            image = self.validate_image(
                image_bytes
            )

            processed = self.preprocess_image(
                image
            )

            ocr_data = pytesseract.image_to_data(
                processed,
                config="--psm 6",
                output_type=pytesseract.Output.DICT,
            )

            raw_text = pytesseract.image_to_string(
                processed,
                config="--psm 6"
            )

            cleaned = self.clean_text(
                raw_text
            )

            ocr_confidence = (
                self.calculate_ocr_confidence(
                    ocr_data
                )
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
                "confidence": ocr_confidence,
                "publisher": publisher_info["publisher"],
                "publisher_confidence": publisher_info["confidence"],
                "publisher_detection_method": publisher_info["method"],
                "word_count": len(cleaned.split()),
                "language": "Unknown",
                "ready_for_analysis": True,
            }

        except Exception as e:

            logger.exception(
                "OCR processing failed: %s",
                e
            )

            return {
                "status": "error",
                "message": str(e),
            }


ocr_service = OCRService()
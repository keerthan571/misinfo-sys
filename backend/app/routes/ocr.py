from __future__ import annotations

import io
import re

import pytesseract

from PIL import Image, ImageEnhance, ImageFilter


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
        Detect publisher only when the publisher name
        is explicitly present in OCR text.

        The system never guesses a publisher.
        """

        if not text:
            return {
                "publisher": None,
                "confidence": 0,
                "method": None,
            }

        normalized = text.lower()

        publishers = {
            "ndtv": "NDTV",
            "rvcj": "RVCJ",
            "bbc": "BBC",
            "cnn": "CNN",
            "reuters": "Reuters",
            "times of india": "Times of India",
            "the times of india": "Times of India",
            "india today": "India Today",
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
            reverse=True
        )

        for keyword, publisher in candidates:

            if keyword in normalized:

                return {
                    "publisher": publisher,
                    "confidence": 95,
                    "method": "ocr_text",
                }

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
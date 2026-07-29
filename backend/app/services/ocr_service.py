import io
import re

import pytesseract
from PIL import Image, ImageEnhance, ImageFilter


pytesseract.pytesseract.tesseract_cmd = (
    r"C:\Program Files\Tesseract-OCR\tesseract.exe"
)


class OCRService:
    OCR_CONFIG = "--psm 6"

    @staticmethod
    def clean_text(text: str) -> str:
        """Remove extra spaces and newlines."""
        return re.sub(r"\s+", " ", text).strip()

    @staticmethod
    def calculate_confidence(image: Image.Image) -> int:
        """Calculate average OCR confidence."""
        try:
            data = pytesseract.image_to_data(
                image,
                output_type=pytesseract.Output.DICT,
            )

            confidences = [
                int(conf)
                for conf in data["conf"]
                if conf != "-1" and int(conf) > 0
            ]

            if not confidences:
                return 0

            return int(sum(confidences) / len(confidences))

        except Exception:
            return 0

    def preprocess_image(self, image: Image.Image) -> Image.Image:
        """Improve image quality before OCR."""

        image = image.convert("L")

        image = image.resize(
            (image.width * 2, image.height * 2)
        )

        image = ImageEnhance.Contrast(image).enhance(2)

        image = image.filter(ImageFilter.SHARPEN)

        return image

    def extract_text_from_image(
        self,
        image_bytes: bytes,
    ) -> dict:

        if not image_bytes:
            return {
                "status": "error",
                "message": "No image provided.",
            }

        try:
            image = Image.open(
                io.BytesIO(image_bytes)
            )

            image = self.preprocess_image(image)

            raw_text = pytesseract.image_to_string(
                image,
                config=self.OCR_CONFIG,
            )

            # ================= DEBUG =================
            print("=" * 60)
            print("RAW OCR OUTPUT:")
            print(repr(raw_text))
            print("=" * 60)

            cleaned_text = self.clean_text(raw_text)

            print("CLEANED OCR OUTPUT:")
            print(repr(cleaned_text))
            print("=" * 60)
            # =========================================

            confidence = self.calculate_confidence(image)

            return {
                "status": "success",
                "extracted_text": cleaned_text,
                "confidence": confidence,
                "word_count": len(cleaned_text.split()),
                "language": "Unknown",
                "ready_for_analysis": bool(cleaned_text),
            }

        except Exception as e:
            print("=" * 60)
            print("OCR EXCEPTION:")
            print(str(e))
            print("=" * 60)

            return {
                "status": "error",
                "message": "OCR processing failed.",
                "error": str(e),
            }


ocr_service = OCRService()
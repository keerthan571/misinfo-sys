import io

import pytesseract
from PIL import Image


class OCRService:

    def __init__(self):
        pass

    def extract_text_from_image(self, image_bytes: bytes):
        """
        Extract text from an uploaded image using Tesseract OCR.
        """

        try:
            if not image_bytes:
                return {
                    "status": "error",
                    "message": "No image provided."
                }

            image = Image.open(io.BytesIO(image_bytes)).convert("RGB")

            text = pytesseract.image_to_string(image).strip()

            return {
                "status": "success",
                "extracted_text": text
            }

        except Exception as e:
            return {
                "status": "error",
                "message": "Make sure Tesseract OCR is installed and added to PATH.",
                "error": str(e)
            }


ocr_service = OCRService()
import pytesseract
from PIL import Image
import io

class OCRService:
    def __init__(self):
        pass

    def extract_text_from_image(self, image_bytes: bytes):
        """
        Extracts text from an uploaded image using Tesseract OCR.
        Students must install Tesseract OCR on their system for this to work.
        """
        try:
            image = Image.open(io.BytesIO(image_bytes))
            # Perform OCR
            text = pytesseract.image_to_string(image)
            return {"extracted_text": text.strip()}
        except Exception as e:
            return {"error": str(e), "message": "Make sure Tesseract is installed and added to PATH."}

ocr_service = OCRService()

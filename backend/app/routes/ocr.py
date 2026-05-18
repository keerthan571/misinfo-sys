from fastapi import APIRouter, UploadFile, File
from ..services.ocr_service import ocr_service

router = APIRouter()

@router.post("/")
async def extract_text(file: UploadFile = File(...)):
    """
    Endpoint to extract text from an uploaded image using OCR.
    """
    image_bytes = await file.read()
    result = ocr_service.extract_text_from_image(image_bytes)
    return result

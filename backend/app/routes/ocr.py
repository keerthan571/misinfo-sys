from fastapi import APIRouter, UploadFile, File
from ..services.ocr_service import ocr_service

router = APIRouter()


@router.post("/")
async def extract_text(file: UploadFile = File(...)):
    """
    Extract text from an uploaded image using OCR.
    """

    # Validate uploaded file
    if not file.content_type or not file.content_type.startswith("image/"):
        return {
            "status": "error",
            "message": "Please upload a valid image file."
        }

    image_bytes = await file.read()

    return ocr_service.extract_text_from_image(image_bytes)
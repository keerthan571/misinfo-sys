from fastapi import APIRouter, UploadFile, File
from datetime import datetime, timezone
import uuid

from ..services.ocr_service import ocr_service
from ..database.mongodb import ocr_history_collection


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


    ocr_result = (
        ocr_service
        .extract_text_from_image(image_bytes)
    )


    # -------------------------
    # Save OCR History
    # Member 1 Collection
    # -------------------------

    ocr_document = {

        "analysis_id": str(uuid.uuid4()),

        "userId": "test_user",

        "image_name": file.filename,

        "extracted_text": ocr_result.get(
            "extracted_text",
            ""
        ),

        "confidence": 98,

        "timestamp": datetime.now(
            timezone.utc
        ).isoformat()

    }


    result = ocr_history_collection.insert_one(
        ocr_document
    )


    print(
        "OCR MongoDB inserted ID:",
        result.inserted_id
    )


    return ocr_result
from datetime import datetime, timezone
from time import perf_counter
import uuid

from fastapi import (
    APIRouter,
    Depends,
    File,
    HTTPException,
    UploadFile,
    status,
)

from app.auth.dependencies import get_current_user
from ..database.mongodb import ocr_history_collection
from ..services.ocr_service import ocr_service

router=APIRouter()

MAX_FILE_SIZE=10*1024*1024


@router.post("/")
async def extract_text(
    file:UploadFile=File(...),
    current_user=Depends(get_current_user),
):

    start_time=perf_counter()

    if file is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No image uploaded."
        )

    if (
        not file.content_type
        or not file.content_type.startswith("image/")
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Please upload a valid image."
        )

    image_bytes=await file.read()

    if not image_bytes:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded image is empty."
        )

    if len(image_bytes)>MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="Image size exceeds 10 MB."
        )

    try:

        ocr_result=ocr_service.extract_text_from_image(
            image_bytes
        )

    except Exception as e:

        print("OCR Error:",e)

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="OCR processing failed."
        )

    processing_time=round(
        perf_counter()-start_time,
        2
    )

    ocr_document={
        "analysis_id":str(uuid.uuid4()),
        "userId":current_user["email"],
        "image_name":file.filename,
        "content_type":file.content_type,
        "image_size":len(image_bytes),
        "extracted_text":ocr_result.get(
            "extracted_text",
            ""
        ),
        "confidence":ocr_result.get(
            "confidence",
            0
        ),
        "word_count":ocr_result.get(
            "word_count",
            0
        ),
        "language":ocr_result.get(
            "language",
            "Unknown"
        ),
        "processing_time":processing_time,
        "timestamp":datetime.now(
            timezone.utc
        ).isoformat()
    }

    try:

        result=ocr_history_collection.insert_one(
            ocr_document
        )

        print(f"OCR Saved | ID={result.inserted_id}")

    except Exception as db_error:

        print(f"OCR MongoDB Error: {db_error}")

    print("OCR RESULT:")
    print(ocr_result)

    return {
        **ocr_result,
        "processing_time":processing_time,
        "analysis_id":ocr_document["analysis_id"],
    }
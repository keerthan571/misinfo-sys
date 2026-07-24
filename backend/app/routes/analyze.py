from fastapi import APIRouter, UploadFile, File, Form
from datetime import datetime, timezone
import uuid

from ..services.nlp_service import nlp_service
from ..services.ocr_service import ocr_service
from ..services.prediction_service import prediction_service
from ..services.fact_verification_service import verify_claim


router = APIRouter()


@router.post("/")
async def analyze(
    text: str = Form(None),
    image: UploadFile = File(None)
):

    analysis_id = str(uuid.uuid4())

    analysis_time = datetime.now(
        timezone.utc
    ).isoformat()


    # Default fixed response structure

    response = {

        "analysis_id": analysis_id,

        "analysis_time": analysis_time,


        "detection": {
            "status": "failed",
            "prediction": "",
            "confidence": 0,
            "reason": ""
        },


        "fact_verification": {
            "status": "failed",
            "claim": "",
            "verdict": "",
            "reason": "",
            "confidence": 0,
            "sources": []
        },


        "ocr": {
            "used": False,
            "extracted_text": "",
            "confidence": 0
        },


        "prediction": {
            "status": "failed",
            "predicted_reach": 0,
            "risk_level": "",
            "virality_score": 0
        },


        "graph": {
            "nodes": [],
            "edges": []
        }

    }


    final_text = text or ""


    # -------------------------
    # OCR
    # -------------------------

    if image:

        image_bytes = await image.read()

        ocr_result = (
            ocr_service
            .extract_text_from_image(image_bytes)
        )


        if ocr_result.get("status") == "success":

            extracted = ocr_result.get(
                "extracted_text",
                ""
            )

            response["ocr"] = {

                "used": True,

                "extracted_text": extracted,

                "confidence": 98
            }


            if not final_text:

                final_text = extracted



    # -------------------------
    # NLP Detection + Fact Check
    # -------------------------

    if final_text:


        detection_result = (
            nlp_service
            .analyze_text(final_text)
        )


        response["detection"] = {

            "status": detection_result.get(
                "status",
                "success"
            ),

            "prediction": detection_result.get(
                "prediction",
                ""
            ),

            "confidence": int(
                str(
                    detection_result.get(
                        "confidence",
                        "0"
                    )
                ).replace("%","")
            ),

            "reason": detection_result.get(
                "reason",
                ""
            )
        }



        fact_result = (
            verify_claim(final_text)
        )


        response["fact_verification"] = {

            "status": fact_result.get(
                "status",
                "failed"
            ),

            "claim": fact_result.get(
                "claim",
                ""
            ),

            "verdict": fact_result.get(
                "verdict",
                ""
            ),

            "reason": fact_result.get(
                "reason",
                ""
            ),

            "confidence": int(
                str(
                    fact_result.get(
                        "confidence",
                        "0"
                    )
                ).replace("%","")
            ),

            "sources": fact_result.get(
                "sources",
                []
            )

        }



    # -------------------------
    # Prediction
    # -------------------------

    prediction_result = (
        prediction_service
        .predict_spread(
            {
                "initial_likes": 0,
                "initial_shares": 0,
                "comments": 0,
                "follower_count": 0
            }
        )
    )


    prediction_data = prediction_result.get(
        "data",
        {}
    )


    response["prediction"] = {

        "status": prediction_result.get(
            "status",
            "success"
        ),

        "predicted_reach": prediction_data.get(
            "predicted_reach",
            0
        ),

        "risk_level": prediction_data.get(
            "risk_level",
            ""
        ),

        "virality_score": prediction_data.get(
            "virality_score",
            0
        )

    }


    return {

        "status": "success",

        "analysis": response

    }
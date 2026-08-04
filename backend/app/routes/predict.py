from fastapi import APIRouter, Depends
from pydantic import BaseModel
from datetime import datetime, timezone
import uuid

from app.auth.dependencies import get_current_user
from app.services.prediction_service import prediction_service
from app.services.spread_factor_service import spread_factor_service
from app.database.mongodb import spread_predictions_collection


router = APIRouter()


class PredictRequest(BaseModel):

    engagement: dict

    detection: dict = {}

    platform: str = "Unknown"



@router.post("/")
def predict_spread(
    request: PredictRequest,
    current_user=Depends(get_current_user)
):


    engagement = request.engagement


    spread_analysis = spread_factor_service.analyze(
        engagement,
        request.detection,
        request.platform
    )


    prediction_result = prediction_service.predict_spread({

        **engagement,

        "spread_score":
        spread_analysis["metrics"]["spread_score"],

        "risk_score":
        request.detection.get(
            "risk_score",
            0
        ),

        "emotion_score":0,

        "manipulation_score":0

    })


    prediction_document = {

        "analysis_id":
        str(uuid.uuid4()),

        "user":
        current_user.get("email"),


        "engagement":
        engagement,


        "prediction":
        prediction_result["data"],


        "timestamp":
        datetime.now(
            timezone.utc
        ).isoformat()

    }


    spread_predictions_collection.insert_one(
        prediction_document
    )


    return {

        "prediction":
        prediction_result,

        "spread_analysis":
        spread_analysis

    }
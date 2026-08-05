from fastapi import APIRouter, Depends
from app.auth.dependencies import get_current_user
from app.services.prediction_service import prediction_service
from app.services.spread_factor_service import spread_factor_service

router = APIRouter()


@router.post("/")
async def predict(
    data: dict,
    current_user=Depends(get_current_user)
):

    engagement = data.get(
        "engagement",
        {}
    )

    detection = data.get(
        "detection",
        {}
    )

    platform = data.get(
        "platform",
        "Unknown"
    )


    spread_analysis = spread_factor_service.analyze(
        engagement,
        detection,
        platform
    )


    prediction = prediction_service.predict_spread(
        {
            **engagement,

            "spread_score":
            spread_analysis["metrics"]["spread_score"],

            "risk_score":
            detection.get(
                "risk_score",
                0
            ),

            "emotion_score":0,

            "manipulation_score":0
        }
    )


    return {
        "prediction":prediction,
        "spread_analysis":spread_analysis
    }
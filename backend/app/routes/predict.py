from fastapi import APIRouter, Depends
from pydantic import BaseModel
from datetime import datetime, timezone
import uuid

from app.auth.dependencies import get_current_user
from app.services.prediction_service import prediction_service
from app.services.spread_factor_service import spread_factor_service
from app.services.graph.graph_generator import graph_generator
from app.database.mongodb import spread_predictions_collection, analysis_collection

router = APIRouter()

class PredictRequest(BaseModel):
    analysis_id: str
    engagement: dict
    detection: dict = {}
    platform: str = "Unknown"

@router.post("/")
def predict_spread(
    request: PredictRequest,
    current_user=Depends(get_current_user)
):
    engagement = request.engagement

    existing_analysis = analysis_collection.find_one(
        {
            "analysis_id": request.analysis_id,
            "email": current_user.get("email")
        }
    )

    if not existing_analysis:
        return {
            "error": "Analysis not found."
        }

    spread_analysis = spread_factor_service.analyze(
        engagement,
        request.detection,
        request.platform
    )

    prediction_result = prediction_service.predict_spread(
        {
            **engagement,
            "spread_score":
                spread_analysis["metrics"]["spread_score"],
            "risk_score":
                request.detection.get(
                    "risk_score",
                    0
                ),
            "emotion_score": 0,
            "manipulation_score": 0
        }
    )

    existing_publisher = existing_analysis.get(
        "publisher"
    )

    graph = graph_generator.generate(
        {
            "analysis": {
                "text":
                    existing_analysis.get(
                        "text",
                        ""
                    ),
                "platform":
                    request.platform,
                "publisher":
                    existing_publisher,
                "publisher_confidence":
                    existing_analysis.get(
                        "publisher_confidence",
                        0
                    )
            },
            "engagement": engagement,
            "spread_prediction":
                prediction_result["data"]
        }
    )

    analysis_collection.update_one(
        {
            "analysis_id": request.analysis_id,
            "email": current_user.get("email")
        },
        {
            "$set": {
                "engagement": engagement,
                "spread_analysis": spread_analysis,
                "prediction": prediction_result["data"],
                "graph": graph,
                "metadata.graph_generated_once": True,
                "metadata.graph_generated_from_verified_engagement": True,
                "metadata.updated_at":
                    datetime.now(
                        timezone.utc
                    ).isoformat()
            }
        }
    )

    prediction_document = {
        "analysis_id":
            request.analysis_id,
        "prediction_id":
            str(uuid.uuid4()),
        "user":
            current_user.get("email"),
        "platform":
            request.platform,
        "engagement":
            engagement,
        "spread_analysis":
            spread_analysis,
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
            spread_analysis,
        "graph":
            graph,
        "analysis_id":
            request.analysis_id
    }
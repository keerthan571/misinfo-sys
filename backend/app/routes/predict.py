from fastapi import APIRouter
from pydantic import BaseModel
from datetime import datetime, timezone
import uuid

from ..services.prediction_service import prediction_service
from ..database.mongodb import spread_predictions_collection


router = APIRouter()


class PredictRequest(BaseModel):

    initial_likes: int

    initial_shares: int

    comments: int

    follower_count: int



@router.post("/")
def predict_spread(request: PredictRequest):

    """
    Endpoint to predict spread of misinformation.
    """


    prediction_result = prediction_service.predict_spread({

        "initial_likes": request.initial_likes,

        "initial_shares": request.initial_shares,

        "comments": request.comments,

        "follower_count": request.follower_count

    })


    prediction_data = prediction_result.get(
        "data",
        {}
    )


    # -------------------------
    # Save Prediction History
    # Member 1 Collection
    # -------------------------

    prediction_document = {


        "analysis_id": str(uuid.uuid4()),


        "userId": "test_user",


        "initial_likes": request.initial_likes,


        "initial_shares": request.initial_shares,


        "comments": request.comments,


        "follower_count": request.follower_count,


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
        ),


        "timestamp": datetime.now(
            timezone.utc
        ).isoformat()

    }



    result = spread_predictions_collection.insert_one(
        prediction_document
    )


    print(
        "Prediction MongoDB inserted ID:",
        result.inserted_id
    )


    return prediction_result
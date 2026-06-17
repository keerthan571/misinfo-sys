from fastapi import APIRouter
from pydantic import BaseModel
from ..services.prediction_service import prediction_service

router = APIRouter()

class PredictRequest(BaseModel):
    initial_likes: int
    account_age_days: int

@router.post("/")
def predict_spread(request: PredictRequest):
    """
    Endpoint to predict the spread of a post.
    """
    result = prediction_service.predict_spread({
        "initial_likes": request.initial_likes,
        "account_age_days": request.account_age_days
    })
    return result

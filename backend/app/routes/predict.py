from fastapi import APIRouter
from pydantic import BaseModel
from ..services.prediction_service import prediction_service

router = APIRouter()


class PredictRequest(BaseModel):
    initial_likes: int
    initial_shares: int
    comments: int
    follower_count: int
    account_age_days: int


@router.post("/")
def predict_spread(request: PredictRequest):
    """
    Predict misinformation spread and virality risk.
    """

    result = prediction_service.predict_spread({
        "initial_likes": request.initial_likes,
        "initial_shares": request.initial_shares,
        "comments": request.comments,
        "followeri copied_count": request.follower_count,
        "account_age_days": request.account_age_days
    })

    return result
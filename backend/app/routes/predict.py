from fastapi import APIRouter
from pydantic import BaseModel

from ..services.prediction_service import prediction_service

router = APIRouter()


class PredictRequest(BaseModel):
    initial_likes: int
    initial_shares: int
    comments: int
    follower_count: int


@router.post("/")
def predict_spread(request: PredictRequest):
    """
    Endpoint to predict the spread of a post.
    """

    return prediction_service.predict_spread({
        "initial_likes": request.initial_likes,
        "initial_shares": request.initial_shares,
        "comments": request.comments,
        "follower_count": request.follower_count
    })
from fastapi import APIRouter
from pydantic import BaseModel
from ..services.influence_service import influence_service

router = APIRouter()

class InfluenceRequest(BaseModel):
    topic: str

@router.post("/")
def detect_influence(request: InfluenceRequest):
    """
    Endpoint to detect key influencers for a given topic.
    """
    result = influence_service.detect_influencers(request.topic)
    return result

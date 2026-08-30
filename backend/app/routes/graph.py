from fastapi import APIRouter
from pydantic import BaseModel

from app.services.graph.graph_generator import graph_generator

router = APIRouter()


class GraphRequest(BaseModel):
    analysis: dict
    engagement: dict
    spread_prediction: dict


@router.post("/")
def get_graph(request: GraphRequest):
    return graph_generator.generate({
        "analysis": request.analysis,
        "engagement": request.engagement,
        "spread_prediction": request.spread_prediction,
    })
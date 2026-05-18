from fastapi import APIRouter
from pydantic import BaseModel
from ..services.graph_service import graph_service

router = APIRouter()

class GraphRequest(BaseModel):
    post_id: str

@router.post("/")
def get_graph(request: GraphRequest):
    """
    Endpoint to retrieve the propagation graph for a given post.
    """
    result = graph_service.get_propagation_graph(request.post_id)
    return result

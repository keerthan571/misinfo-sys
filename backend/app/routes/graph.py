from fastapi import APIRouter
from pydantic import BaseModel


router = APIRouter()

# Request Model
class GraphRequest(BaseModel):
    content: str
    reposts: int


# API Endpoint
@router.post("/")
def get_graph(request: GraphRequest):
    """
    Generate propagation graph based on content and repost count
    """
    result = build_graph(request.content, request.reposts)
    return result
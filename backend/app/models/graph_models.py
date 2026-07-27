from pydantic import BaseModel
from typing import List, Optional


class GraphNode(BaseModel):
    id: str
    label: str
    type: str

    followers: int = 0

    influence: float = 0.0

    pagerank: float = 0.0

    engagement: float = 0.0

    verified: bool = False

    cluster: Optional[int] = None


class GraphEdge(BaseModel):
    source: str

    target: str

    weight: float

    interaction: str


class GraphResponse(BaseModel):
    nodes: List[GraphNode]

    edges: List[GraphEdge]
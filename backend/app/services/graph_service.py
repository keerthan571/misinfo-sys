from typing import Any
from app.services.graph.graph_generator import GraphGenerator

_generator = GraphGenerator()

def build_graph(analysis_data: dict[str, Any]) -> dict[str, Any]:
    """
    Build the misinformation propagation graph.

    Pipeline

        Analysis Result
               │
               ▼
        GraphGenerator
               │
               ▼
      PropagationEngine
               │
               ▼
     InfluenceDetection
               │
               ▼
      CommunityDetector
               │
               ▼
       GraphSerializer
               │
               ▼
          Graph JSON
    """
    return _generator.generate(analysis_data)
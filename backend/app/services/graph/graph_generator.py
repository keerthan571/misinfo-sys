from __future__ import annotations

from typing import Any

from app.services.graph.community_detector import CommunityDetector
from app.services.graph.graph_config import GraphConfig
from app.services.graph.graph_serializer import GraphSerializer
from app.services.graph.influence_detection import InfluenceDetection
from app.services.graph.propagation_engine import PropagationEngine


class GraphGenerator:
    def __init__(self) -> None:
        self.config: GraphConfig = GraphConfig()
        self.engine: PropagationEngine = PropagationEngine(self.config)

    def generate(self, analysis_result: dict[str, Any]) -> dict[str, Any]:
        graph = self.engine.generate(
            analysis=analysis_result.get("analysis", {}),
            engagement=analysis_result.get("engagement", {}),
            spread_prediction=analysis_result.get("spread_prediction", {}),
        )

        influence = InfluenceDetection(graph).analyze()
        communities = CommunityDetector(graph).analyze()

        return GraphSerializer(graph).serialize(
            influence=influence,
            communities=communities,
        )
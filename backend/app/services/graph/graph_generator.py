from __future__ import annotations

from typing import Any

from app.services.graph.graph_config import GraphConfig
from app.services.graph.propagation_engine import PropagationEngine
from app.services.graph.influence_detection import InfluenceDetection
from app.services.graph.community_detector import CommunityDetector
from app.services.graph.graph_serializer import GraphSerializer


class GraphGenerator:
    """
    Graph Generation Pipeline

    Analysis Result
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
        API Response
    """

    def __init__(self):
        self.config = GraphConfig()

    def generate(
        self,
        result: dict[str, Any],
    ) -> dict[str, Any]:

        analysis = result.get("analysis", {})
        engagement = result.get("engagement", {})
        spread_prediction = result.get(
            "spread_prediction",
            {},
        )

        # ==============================================================
        # Build Propagation Graph
        # ==============================================================

        graph = PropagationEngine(
            self.config
        ).generate(
            analysis=analysis,
            engagement=engagement,
            spread_prediction=spread_prediction,
        )

        # ==============================================================
        # Influence Analysis
        # ==============================================================

        influence = InfluenceDetection(
            graph
        ).analyze()

        # ==============================================================
        # Community Detection
        # ==============================================================

        communities = CommunityDetector(
            graph
        ).analyze()

        # ==============================================================
        # Serialize Response
        # ==============================================================

        return GraphSerializer(
            graph
        ).serialize(
            influence=influence,
            communities=communities,
        )
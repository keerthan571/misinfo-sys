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

    @staticmethod
    def _extract_audience_exposure_result(
        analysis_result: dict[str, Any],
    ) -> dict[str, Any] | None:
        """Find the current Future Audience Exposure result without
        interpreting legacy spread-prediction fields as exposure values.

        The current prediction pipeline stores the forecast under
        spread_prediction['experimental_audience_forecast'].
        Direct aliases are accepted for API/backward compatibility.
        """
        analysis = analysis_result.get("analysis", {})
        direct_candidates = (
            # Current forecast endpoint persists its result as
            # analysis document field `future_audience`.
            analysis_result.get("future_audience"),
            analysis.get("future_audience") if isinstance(analysis, dict) else None,
            analysis_result.get("experimental_audience_forecast"),
            analysis_result.get("future_audience_exposure"),
            analysis_result.get("audience_exposure_result"),
        )
        for candidate in direct_candidates:
            if isinstance(candidate, dict):
                return candidate

        spread_prediction = analysis_result.get("spread_prediction")
        if isinstance(spread_prediction, dict):
            nested_candidates = (
                spread_prediction.get("experimental_audience_forecast"),
                spread_prediction.get("future_audience"),
                spread_prediction.get("future_audience_exposure"),
                spread_prediction.get("audience_exposure_result"),
            )
            for candidate in nested_candidates:
                if isinstance(candidate, dict):
                    return candidate

        # Some callers may already provide a forecast-shaped result directly
        # as spread_prediction. Accept it only when it contains the explicit
        # predicted exposure field, not merely a legacy spread label/score.
        if (
            isinstance(spread_prediction, dict)
            and "predicted_audience_exposure" in spread_prediction
        ):
            return spread_prediction

        return None

    def generate(self, analysis_result: dict[str, Any]) -> dict[str, Any]:
        analysis = analysis_result.get("analysis", {})
        engagement = analysis_result.get("engagement", {})
        audience_exposure_result = self._extract_audience_exposure_result(
            analysis_result
        )

        # The engine accepts the current forecast's audience_exposure_proxy
        # and predicted_views fields as well as the explicit graph alias
        # predicted_audience_exposure. Invalid or failed forecasts use the
        # existing safe compatibility fallback.
        graph = self.engine.generate(
            analysis=analysis,
            engagement=engagement,
            audience_exposure_result=audience_exposure_result,
        )

        influence = InfluenceDetection(graph).analyze()
        communities = CommunityDetector(graph).analyze()

        return GraphSerializer(graph).serialize(
            influence=influence,
            communities=communities,
        )


graph_generator = GraphGenerator()

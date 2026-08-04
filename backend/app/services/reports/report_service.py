from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any, Dict

from app.models.report_model import (
    AnalysisSummary,
    CommunitySummary,
    EngagementMetrics,
    FactVerification,
    GraphStatistics,
    ReportMetadata,
    ReportModel,
    SpreadPrediction,
    TopInfluencer,
)


class ReportService:
    """
    Builds a complete report from the
    analysis output and graph output.
    """

    def generate_report(
        self,
        analysis: Dict[str, Any],
        graph: Dict[str, Any],
    ) -> ReportModel:

        analysis_data = analysis.get("analysis", {})
        final_result = analysis_data.get("final_result", {})

        metadata = ReportMetadata(
            report_id=str(uuid.uuid4()),
            generated_at=datetime.utcnow(),
        )

        analysis_summary = AnalysisSummary(
            label=final_result.get("label", "Unknown"),
            confidence=final_result.get("confidence", 0),
            risk_level=final_result.get("risk_level", "Low"),
            summary=final_result.get("summary", ""),
        )

        engagement_data = analysis_data.get(
            "engagement",
            {},
        )

        engagement = EngagementMetrics(
            likes=engagement_data.get("likes", 0),
            shares=engagement_data.get("shares", 0),
            comments=engagement_data.get("comments", 0),
            views=engagement_data.get("views", 0),
            bookmarks=engagement_data.get("bookmarks", 0),
        )

        prediction_data = (
            analysis_data
            .get("prediction", {})
            .get("data", {})
        )

        prediction = SpreadPrediction(
            predicted_reach=prediction_data.get(
                "predicted_reach",
                0,
            ),
            spread_probability=prediction_data.get(
                "spread_probability",
                0,
            ),
            virality_score=prediction_data.get(
                "virality_score",
                0,
            ),
            estimated_influencers=prediction_data.get(
                "estimated_influencers",
                0,
            ),
        )

        verification = analysis_data.get(
            "fact_verification",
            {},
        )

        fact = FactVerification(
            verdict=verification.get("verdict", ""),
            confidence=verification.get("confidence", ""),
            reason=verification.get("reason", ""),
            sources=verification.get("sources", []),
        )

        graph_statistics = graph.get(
            "statistics",
            {},
        )

        statistics = GraphStatistics(
            node_count=graph_statistics.get(
                "node_count",
                0,
            ),
            edge_count=graph_statistics.get(
                "edge_count",
                0,
            ),
            density=graph_statistics.get(
                "density",
                0,
            ),
        )

        influencers = [
            TopInfluencer(
                id=item["id"],
                label=item["label"],
                followers=item["followers"],
                score=item["score"],
            )
            for item in graph.get(
                "influence",
                {},
            ).get(
                "top_influencers",
                [],
            )
        ]

        communities = [
            CommunitySummary(
                community_id=item["community_id"],
                size=item["size"],
                leaders=item["leaders"],
                bots=item["bots"],
                influencers=item["influencers"],
                average_followers=item["average_followers"],
                risk_score=item["risk_score"],
            )
            for item in graph.get(
                "communities",
                {},
            ).get(
                "summary",
                [],
            )
        ]

        return ReportModel(
            metadata=metadata,
            analysis=analysis_summary,
            engagement=engagement,
            prediction=prediction,
            fact_verification=fact,
            graph_statistics=statistics,
            top_influencers=influencers,
            communities=communities,
            raw_data={
                "analysis": analysis,
                "graph": graph,
            },
        )
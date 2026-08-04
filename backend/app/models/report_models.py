from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class ReportMetadata(BaseModel):
    report_id: str
    generated_at: datetime = Field(default_factory=datetime.utcnow)
    generated_by: str = "AI Misinformation Analysis System"
    version: str = "1.0"


class AnalysisSummary(BaseModel):
    label: str
    confidence: float
    risk_level: str
    summary: str


class EngagementMetrics(BaseModel):
    likes: int = 0
    shares: int = 0
    comments: int = 0
    views: int = 0
    bookmarks: int = 0


class SpreadPrediction(BaseModel):
    predicted_reach: int = 0
    spread_probability: float = 0.0
    virality_score: float = 0.0
    estimated_influencers: int = 0


class FactVerification(BaseModel):
    verdict: str = ""
    confidence: str = ""
    reason: str = ""
    sources: List[str] = Field(default_factory=list)


class GraphStatistics(BaseModel):
    node_count: int = 0
    edge_count: int = 0
    density: float = 0.0


class TopInfluencer(BaseModel):
    id: str
    label: str
    followers: int = 0
    score: float = 0.0


class CommunitySummary(BaseModel):
    community_id: int
    size: int
    leaders: int
    bots: int
    influencers: int
    average_followers: float
    risk_score: float


class ReportModel(BaseModel):
    metadata: ReportMetadata
    analysis: AnalysisSummary
    engagement: EngagementMetrics
    prediction: SpreadPrediction
    fact_verification: FactVerification
    graph_statistics: GraphStatistics
    top_influencers: List[TopInfluencer] = Field(default_factory=list)
    communities: List[CommunitySummary] = Field(default_factory=list)
    raw_data: Optional[Dict[str, Any]] = None
from __future__ import annotations


class GraphConfig:
    """
    Configuration for misinformation propagation graph generation.
    """

    # ==========================
    # Node Types
    # ==========================

    SOURCE_NODE = "source"
    INFLUENCER_NODE = "influencer"
    USER_NODE = "user"

    # ==========================
    # Edge Types
    # ==========================

    PUBLISH_EDGE = "publish"
    SHARE_EDGE = "share"
    CASCADE_EDGE = "cascade"
    BRIDGE_EDGE = "bridge"
    BOT_EDGE = "bot"

    # ==========================
    # Graph Size
    # ==========================

    MIN_NODES = 25
    MAX_NODES = 100

    MIN_INFLUENCERS = 2
    MAX_INFLUENCER_RATIO = 0.20

    MIN_FOLLOWERS = 100

    # ==========================
    # Edge Weights
    # ==========================

    MIN_EDGE_WEIGHT = 0.10
    MAX_EDGE_WEIGHT = 1.00

    # ==========================
    # Engagement Formula
    # ==========================

    ENGAGEMENT_WEIGHTS = {
        "likes": 1,
        "shares": 3,
        "comments": 2,
    }

    # ==========================
    # Risk Multipliers
    # ==========================

    _RISK_MULTIPLIER = {
        "Low": 0.8,
        "Medium": 1.0,
        "High": 1.3,
    }

    # ==========================
    # Bot Density
    # Smaller interval = more bots
    # ==========================

    _BOT_INTERVAL = {
        "Low": 10,
        "Medium": 7,
        "High": 5,
    }

    # ==========================
    # Bot Amplification
    # ==========================

    _BOT_EDGE_MULTIPLIER = {
        "Low": 1.10,
        "Medium": 1.25,
        "High": 1.50,
    }

    # ======================================================
    # Helper Functions
    # ======================================================

    def risk_multiplier(self, risk_level: str) -> float:
        return self._RISK_MULTIPLIER.get(risk_level, 1.0)

    def bot_interval(self, risk_level: str) -> int:
        return self._BOT_INTERVAL.get(risk_level, 7)

    def bot_edge_multiplier(self, risk_level: str) -> float:
        return self._BOT_EDGE_MULTIPLIER.get(risk_level, 1.25)
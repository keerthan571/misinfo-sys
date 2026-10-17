from __future__ import annotations


class GraphConfig:
    """
    Configuration for simulated propagation graph generation.

    Spreading levels come from dated engagement observations.
    Risk scores and legacy spread predictions are not graph inputs.
    """

    # Node types
    SOURCE_NODE = "source"
    INFLUENCER_NODE = "influencer"
    USER_NODE = "user"
    BOT_NODE = "bot"

    # Edge types
    PUBLISH_EDGE = "publish"
    SHARE_EDGE = "share"
    CASCADE_EDGE = "cascade"
    BRIDGE_EDGE = "bridge"
    BOT_EDGE = "bot"

    # Graph size limits
    MIN_NODES = 25
    MAX_NODES = 100

    MIN_INFLUENCERS = 2
    MAX_INFLUENCER_RATIO = 0.20

    MIN_FOLLOWERS = 100

    # Edge weights
    MIN_EDGE_WEIGHT = 0.10
    MAX_EDGE_WEIGHT = 1.00

    # Engagement metrics used by the revised spreading-level logic
    ENGAGEMENT_METRICS = (
        "views",
        "likes",
        "comments",
        "shares",
        "reposts",
        "bookmarks",
        "replies",
        "quotes",
        "reactions",
    )

    # Engagement weights are retained for compatibility or future
    # explicitly defined graph scoring; they are not a substitute
    # for dated-observation growth.
    ENGAGEMENT_WEIGHTS = {
        "views": 1,
        "likes": 1,
        "comments": 2,
        "shares": 3,
        "reposts": 3,
        "bookmarks": 1,
        "replies": 2,
        "quotes": 2,
        "reactions": 1,
    }

    # Spreading-level settings for simulated graph structure.
    SPREADING_LEVEL_WEIGHTS = {
        "Low": 0.20,
        "Medium": 0.55,
        "High": 0.90,
        "Insufficient historical data": 0.25,
    }

    # Bot nodes are simulation placeholders only, not detected accounts.
    # Keep their count small and bounded.
    SIMULATED_BOT_RATIO = {
        "Low": 0.01,
        "Medium": 0.02,
        "High": 0.03,
        "Insufficient historical data": 0.0,
    }

export const GRAPH_LIMITS = {
    MIN_NODES: 10,
    MAX_NODES: 100,
    MAX_EDGES: 250
};

export const NODE_TYPES = Object.freeze({
    CLAIM: "claim",
    INFLUENCER: "influencer",
    USER: "user",
    BOT: "bot"
});

export const NODE_COLORS = Object.freeze({
    claim: "#EF4444",
    influencer: "#F59E0B",
    user: "#3B82F6",
    bot: "#8B5CF6"
});

export const PLATFORMS = Object.freeze({
    TWITTER: "Twitter",
    FACEBOOK: "Facebook",
    INSTAGRAM: "Instagram",
    WHATSAPP: "WhatsApp",
    UNKNOWN: "Unknown"
});

export const GRAPH_LAYOUT = {
    LEVEL_GAP: 180,
    NODE_GAP: 220,
    RANDOM_OFFSET: 50
};

export const NODE_SIZE = {
    CLAIM: 70,
    INFLUENCER: 60,
    USER: 45,
    BOT: 45
};

export const EDGE_TYPES = {
    SHARE: "share",
    RESHARE: "reshare"
};

export const EDGE_STYLE = {
    TYPE: "smoothstep",
    ANIMATED: true,
    MARKER_END: true
};

export const RISK_LEVELS = Object.freeze({
    LOW: "Low",
    MEDIUM: "Medium",
    HIGH: "High",
    UNKNOWN: "Unknown"
});

export const RISK_COLORS = Object.freeze({
    Low: "#22C55E",
    Medium: "#F59E0B",
    High: "#EF4444",
    Unknown: "#9CA3AF"
});

export const GRAPH_FEATURES = {
    ANIMATIONS: true,
    CONTROLS: true,
    MINIMAP: true,
    BACKGROUND: true,
    CROSS_EDGES: true
};

export const DEFAULT_NODE_DATA = {
    level: 0,
    followers: 0,
    influenceScore: 0,
    shareProbability: 0,
    verified: false,
    viral: false,
    community: 0,
    platform: PLATFORMS.UNKNOWN
};

export const DEBUG = {
    LOGS: false,
    PARAMETERS: false,
    GENERATION_TIME: false
};
// Static configuration for the Graph Generation Engine.
// Dynamic calculations belong in ParameterEngine.js.

export const GRAPH_LIMITS = {
  MIN_NODES: 10,
  MAX_NODES: 100,
  MAX_EDGES: 250,
};

export const NODE_TYPES = Object.freeze({
  ORIGIN: "origin",
  INFLUENCER: "influencer",
  NORMAL: "normal",
  TERMINAL: "terminal",
});

export const PLATFORMS = Object.freeze({
  TWITTER: "Twitter",
  FACEBOOK: "Facebook",
  INSTAGRAM: "Instagram",
  WHATSAPP: "WhatsApp",
  UNKNOWN: "Unknown",
});

export const NODE_COLORS = Object.freeze({
  origin: "#2563EB",
  influencer: "#F59E0B",
  normal: "#10B981",
  terminal: "#9CA3AF",
});

export const RISK_COLORS = Object.freeze({
  Low: "#22C55E",
  Medium: "#F59E0B",
  High: "#EF4444",
  Unknown: "#9CA3AF",
});

export const NODE_SIZE_CONFIG = {
  BASE: 45,
  ORIGIN_BONUS: 20,
  INFLUENCER_BONUS: 10,
};

export const EDGE_CONFIG = {
  TYPE: "smoothstep",
  ANIMATED: true,
  MARKER_END: true,
};

export const LAYOUT_CONFIG = {
  HORIZONTAL_SPACING: 220,
  VERTICAL_SPACING: 150,
  RANDOM_OFFSET: 60,
};

export const GRAPH_FEATURES = {
  ENABLE_ANIMATIONS: true,
  ENABLE_MINIMAP: true,
  ENABLE_CONTROLS: true,
  ENABLE_BACKGROUND: true,
  ENABLE_SECONDARY_CLUSTERS: true,
  ENABLE_CROSS_CONNECTIONS: true,
};

export const DEFAULT_NODE_DATA = {
  shared: true,
  level: 0,
  degree: 0,
  influenceScore: 0,
  platform: PLATFORMS.UNKNOWN,
};

export const MASS_SPREAD_LABELS = Object.freeze({
  LOW: "Low",
  MEDIUM: "Medium",
  HIGH: "High",
  UNKNOWN: "Unknown",
});

export const DEBUG_CONFIG = {
  ENABLE_LOGS: false,
  SHOW_PARAMETERS: false,
  SHOW_GENERATION_TIME: false,
};
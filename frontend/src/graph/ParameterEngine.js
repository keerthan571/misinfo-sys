import { GRAPH_LIMITS, NODE_SIZE_CONFIG } from "./constants";

/**
 * Converts backend response into graph generation parameters.
 * This is the only module responsible for graph mathematics.
 */
class ParameterEngine {
  constructor(apiResponse = {}) {
    this.analysis = apiResponse.analysis ?? {};
    this.engagement = apiResponse.engagement ?? {};
    this.spread = apiResponse.spread_prediction ?? {};
    this.metadata = apiResponse.metadata ?? {};
  }

  clamp(value, min, max) {
    return Math.max(min, Math.min(max, value));
  }

  normalizeProbability(value) {
    return this.clamp(Number(value) || 0, 0, 1);
  }

  normalizePercentage(value) {
    return this.clamp(Number(value) || 0, 0, 100);
  }

  calculateTotalNodes() {
    const reach = Math.max(
      1,
      Number(this.spread.predicted_reach) || 1
    );

    const nodes = Math.sqrt(reach) / 6;

    return Math.round(
      this.clamp(
        nodes,
        GRAPH_LIMITS.MIN_NODES,
        GRAPH_LIMITS.MAX_NODES
      )
    );
  }

  calculateGraphDepth() {
    return this.clamp(
      Number(this.spread.expected_depth) || 3,
      2,
      8
    );
  }

  calculateBranchFactor() {
    const virality = this.normalizePercentage(
      this.spread.virality_score
    );

    return Number(
      (1 + (virality / 100) * 4).toFixed(2)
    );
  }

  calculateInfluencerCount(totalNodes) {
    const estimated =
      Number(this.spread.estimated_influencers) || 1;

    return Math.round(
      this.clamp(
        estimated,
        1,
        Math.max(1, totalNodes * 0.2)
      )
    );
  }

  calculateClusterCount() {
    const risk =
      this.spread.risk_of_mass_spread?.toLowerCase() ??
      "unknown";

    switch (risk) {
      case "high":
        return 4;

      case "medium":
        return 3;

      case "low":
        return 2;

      default:
        return 1;
    }
  }

  calculateCrossEdgeProbability() {
    const virality =
      this.normalizePercentage(
        this.spread.virality_score
      ) / 100;

    const probability =
      this.normalizeProbability(
        this.spread.spread_probability
      );

    return Number(
      (virality * probability).toFixed(2)
    );
  }

  calculateDensity() {
    const views =
      Math.max(
        1,
        Number(this.engagement.views) || 1
      );

    const interactions =
      (Number(this.engagement.shares) || 0) +
      (Number(this.engagement.comments) || 0);

    return Number(
      this.clamp(
        interactions / views,
        0,
        1
      ).toFixed(2)
    );
  }

  calculateRandomness() {
    const confidence =
      this.normalizePercentage(
        this.analysis.confidence
      );

    return Number(
      (1 - confidence / 100).toFixed(2)
    );
  }

  calculateAverageNodeSize() {
    const virality =
      this.normalizePercentage(
        this.spread.virality_score
      );

    return Math.round(
      NODE_SIZE_CONFIG.BASE +
        virality * 0.2
    );
  }

  generateSeed() {
    const analysisId =
      this.metadata.analysis_id || "default";

    const timestamp =
      this.metadata.timestamp ||
      Date.now().toString();

    return `${analysisId}-${timestamp}`;
  }

  build() {
    const totalNodes =
      this.calculateTotalNodes();

    return {
      // Existing parameters
      totalNodes,

      graphDepth:
        this.calculateGraphDepth(),

      branchFactor:
        this.calculateBranchFactor(),

      influencerCount:
        this.calculateInfluencerCount(
          totalNodes
        ),

      clusterCount:
        this.calculateClusterCount(),

      crossEdgeProbability:
        this.calculateCrossEdgeProbability(),

      nodeDensity:
        this.calculateDensity(),

      randomness:
        this.calculateRandomness(),

      averageNodeSize:
        this.calculateAverageNodeSize(),

      simulationSeed:
        this.generateSeed(),

      platform:
        this.engagement.platform ||
        "Unknown",

      riskLevel:
        this.analysis.risk_level ||
        "Unknown",

      verificationStatus:
        this.analysis.verification_status ||
        "Unknown",

      prediction:
        this.analysis.prediction ||
        "Unknown",

      // -------- NEW PARAMETERS --------

      viralityScore:
        this.normalizePercentage(
          this.spread.virality_score
        ),

      spreadProbability:
        this.normalizeProbability(
          this.spread.spread_probability
        ),

      predictedReach:
        Number(
          this.spread.predicted_reach
        ) || 0,

      expectedDepth:
        Number(
          this.spread.expected_depth
        ) || 0,

      estimatedReposts:
        Number(
          this.spread.estimated_reposts
        ) || 0,

      estimatedInfluencers:
        Number(
          this.spread.estimated_influencers
        ) || 0,

      predictedLifetimeHours:
        Number(
          this.spread.predicted_lifetime_hours
        ) || 0,

      riskOfMassSpread:
        this.spread.risk_of_mass_spread ||
        "Unknown",
    };
  }
}

/**
 * Public API
 */
export function buildParameters(apiResponse) {
  return new ParameterEngine(apiResponse).build();
}
import { GRAPH_LIMITS } from "./constants";

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

    percentage(value) {
        return this.clamp(Number(value) || 0, 0, 100);
    }

    probability(value) {
        return this.clamp(Number(value) || 0, 0, 1);
    }

    graph() {
        const reach = Math.max(1, Number(this.spread.predicted_reach) || 1);
        const totalNodes = Math.round(
            this.clamp(
                Math.sqrt(reach) / 6,
                GRAPH_LIMITS.MIN_NODES,
                GRAPH_LIMITS.MAX_NODES
            )
        );

        return {
            totalNodes,
            depth: this.clamp(Number(this.spread.expected_depth) || 3, 2, 8),
            branchFactor: Number(
                (1 + (this.percentage(this.spread.virality_score) / 100) * 4).toFixed(2)
            ),
            density: this.calculateDensity()
        };
    }

    composition(graph) {
        const influencers = this.calculateInfluencers(graph.totalNodes);
        const bots = this.calculateBots(graph.totalNodes);
        const users = Math.max(
            1,
            graph.totalNodes - influencers - bots - 1
        );

        return {
            claims: 1,
            influencers,
            users,
            bots,
            communities: this.calculateCommunities()
        };
    }

    propagation() {
        return {
            riskLevel: this.analysis.risk_level ?? "Unknown",
            prediction: this.analysis.prediction ?? "Unknown",
            confidence: this.percentage(this.analysis.confidence),
            viralityScore: this.percentage(this.spread.virality_score),
            spreadProbability: this.probability(this.spread.spread_probability),
            predictedReach: Number(this.spread.predicted_reach) || 0,
            expectedDepth: Number(this.spread.expected_depth) || 0,
            estimatedReposts: Number(this.spread.estimated_reposts) || 0,
            lifetimeHours: Number(this.spread.predicted_lifetime_hours) || 0
        };
    }

    followers() {
        return {
            influencer: {
                min: 100000,
                max: 1000000
            },
            user: {
                min: 200,
                max: 10000
            },
            bot: {
                min: 0,
                max: 500
            }
        };
    }

    influence() {
        return {
            average: Math.round(this.percentage(this.spread.virality_score) * 0.6),
            maximum: this.percentage(this.spread.virality_score)
        };
    }

    metadataInfo() {
        return {
            platform: this.engagement.platform ?? "Unknown",
            verification: this.analysis.verification_status ?? "Unknown",
            seed: this.generateSeed()
        };
    }

    calculateDensity() {
        const views = Math.max(1, Number(this.engagement.views) || 1);
        const interactions =
            (Number(this.engagement.shares) || 0) +
            (Number(this.engagement.comments) || 0);

        return Number(
            this.clamp(interactions / views, 0, 1).toFixed(2)
        );
    }

    calculateInfluencers(totalNodes) {
        const estimated = Number(this.spread.estimated_influencers) || 2;

        return Math.round(
            this.clamp(
                estimated,
                2,
                Math.max(2, Math.floor(totalNodes * 0.2))
            )
        );
    }

    calculateBots(totalNodes) {
        const risk = (this.analysis.risk_level || "").toLowerCase();

        if (risk === "high")
            return Math.max(2, Math.round(totalNodes * 0.12));

        if (risk === "medium")
            return Math.max(1, Math.round(totalNodes * 0.06));

        return 0;
    }

    calculateCommunities() {
        const risk = (this.analysis.risk_level || "").toLowerCase();

        if (risk === "high") return 4;
        if (risk === "medium") return 3;
        if (risk === "low") return 2;

        return 1;
    }

    generateSeed() {
        return `${this.metadata.analysis_id || "analysis"}-${this.metadata.timestamp || Date.now()}`;
    }

    build() {
        const graph = this.graph();

        return {
            graph,
            composition: this.composition(graph),
            propagation: this.propagation(),
            followers: this.followers(),
            influence: this.influence(),
            metadata: this.metadataInfo()
        };
    }
}

export function buildParameters(apiResponse) {
    return new ParameterEngine(apiResponse).build();
}
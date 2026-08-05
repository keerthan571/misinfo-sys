import {
    GRAPH_LIMITS,
    GRAPH_LAYOUT,
    PROPAGATION_RULES,
} from "./constants";

export default class ParameterEngine {
    constructor(apiResponse = {}) {

        this.analysisData = apiResponse.final_result ?? {};

        this.engagement =
            apiResponse.verified_engagement ??
            apiResponse.engagement ??
            {};

        this.spread =
            apiResponse.prediction?.data ??
            apiResponse.prediction ??
            {};

        this.metadata =
            apiResponse.metadata ??
            {};

        this.platform =
            apiResponse.platform?.platform ??
            "Unknown";
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
    normalizeLog(value, maxValue) {

        value = Math.max(0, Number(value) || 0);

        return this.clamp(
            (
                Math.log10(value + 1) /
                Math.log10(maxValue + 1)
            ) * 100,
            0,
            100
        );
    }

    normalizeReach() {

        return this.normalizeLog(
            this.spread.predicted_reach,
            100000
        );
    }

    normalizeViews() {

        return this.normalizeLog(
            this.engagement.views,
            100000
        );
    }

    normalizeShares() {

        return this.normalizeLog(
            this.engagement.shares,
            100
        );
    }

    calculatePropagationScore() {

        const weights =
            PROPAGATION_RULES.SCORE_WEIGHTS;

        const reach =
            this.normalizeReach();

        const views =
            this.normalizeViews();

        const shares =
            this.normalizeShares();

        const virality =
            this.percentage(
                this.spread.virality_score
            );

        const probability =
            this.probability(
                this.spread.spread_probability
            ) * 100;

        const score =
            reach * weights.reach +
            views * weights.views +
            shares * weights.shares +
            virality * weights.virality +
            probability * weights.probability;

        return Number(score.toFixed(2));
    }

    calculateTotalNodes(score) {

        const min =
            GRAPH_LIMITS.MIN_NODES;

        const max =
            GRAPH_LIMITS.MAX_NODES;

        const nodes =
            Math.round(
                min +
                (score / 100) *
                (max - min)
            );

        return this.clamp(
            nodes,
            min,
            max
        );
    }
    
    calculateBranchFactor() {

        const shares =
            Number(this.engagement.shares) || 0;

        const virality =
            this.percentage(
                this.spread.virality_score
            );

        const confidence =
            this.percentage(
                this.analysisData.confidence
            );

        const probability =
            this.probability(
                this.spread.spread_probability
            );

        let factor =
            PROPAGATION_RULES.BRANCHING.BASE;

        if (shares > 20)
            factor++;

        if (virality > 60)
            factor++;

        if (probability > 0.60)
            factor++;

        if (confidence > 80)
            factor++;

        return this.clamp(
            factor,
            PROPAGATION_RULES.BRANCHING.BASE,
            PROPAGATION_RULES.BRANCHING.MAX
        );
    }

    calculateInfluencers() {

        const followers =
            Number(this.engagement.followers) || 0;

        const tier =
            PROPAGATION_RULES.FOLLOWER_TIERS.find(
                t => followers <= t.max
            );

        return tier?.influencers ?? 1;
    }

    graph() {

        const propagationScore =
            this.calculatePropagationScore();

        return {

            propagationScore,

            totalNodes:
                this.calculateTotalNodes(
                    propagationScore
                ),

            depth: (() => {

                const probability =
                    this.probability(
                        this.spread.spread_probability
                    );

                const expected =
                    Number(
                        this.spread.expected_depth
                    ) || 5;

                return this.clamp(
                    Math.round(
                        expected +
                        probability * 2
                    ),
                    4,
                    8
                );

            })(),

            branchFactor:
                this.calculateBranchFactor(),

            density:
                this.calculateDensity()
        };
    }

    composition(graph) {
        const influencers = this.calculateInfluencers();
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
            riskLevel: this.analysisData.risk_level ?? "Unknown",
            prediction: this.analysisData.prediction ?? "Unknown",
            confidence: this.percentage(this.analysisData.confidence),
            viralityScore: this.percentage(this.spread.virality_score),
            spreadProbability: this.probability(this.spread.spread_probability),
            predictedReach: Number(this.spread.predicted_reach) || 0,
            expectedDepth: Number(this.spread.expected_depth) || 0,
            estimatedReposts: Number(this.spread.estimated_reposts) || 0,
            lifetimeHours: Number(this.spread.predicted_lifetime_hours) || 0
        };
    }
    simulation() {

        const propagationScore =
            this.calculatePropagationScore();

        const probability =
            this.probability(
                this.spread.spread_probability
            );

        const risk =
            (this.analysisData.risk_level || "")
                .toLowerCase();

        return {

            propagationScore,

            maxChildren:
                this.calculateBranchFactor(),

            botProbability:
                PROPAGATION_RULES.BOT_PERCENTAGE[risk] ?? 0,

            influencerProbability:
                Math.min(
                    0.8,
                    0.25 + probability
                ),

            communitySpread:
                Number(
                    (
                        propagationScore / 100
                    ).toFixed(2)
                ),

            cascadeDecay:
            Number(
            (
            0.15 +
            (1 - probability) * 0.5
            ).toFixed(2)
            )
        };
    }

    layout() {

        return {

            direction: "TB",

            levelGap:
                GRAPH_LAYOUT.LEVEL_GAP,

            nodeGap:
                GRAPH_LAYOUT.NODE_GAP,

            randomOffset:
                GRAPH_LAYOUT.RANDOM_OFFSET
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

    initialInfluence() {
        const virality =
            this.percentage(
                this.spread.virality_score
            );

        const confidence =
            this.percentage(
                this.analysisData.confidence
            );

        const base =
            Math.max(
                40,
                Math.round(
                    virality * 0.7 +
                    confidence * 0.3
                )
            );

        return {
            average: Math.round(
                base * 0.75
            ),
            maximum: base
        };
    }

    metadataInfo() {
        return {
            platform: this.platform,
            verification: this.analysisData.verification_status ?? "Unknown",
            seed: this.generateSeed()
        };
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

        const engagementRate =
            interactions / views;

        return Number(
            this.clamp(
                engagementRate * 8,
                0.15,
                0.85
            ).toFixed(2)
        );
    }

    calculateBots(totalNodes) {

        const risk =
            (this.analysisData.risk_level || "")
                .toLowerCase();

        const probability =
            this.probability(
                this.spread.spread_probability
            );

        const percentage =
            (
                PROPAGATION_RULES.BOT_PERCENTAGE[risk]
                ?? 0
            ) * (0.6 + probability);

        return Math.round(
            totalNodes * percentage
        );
    }

    calculateCommunities() {

        const risk =
            (this.analysisData.risk_level || "")
                .toLowerCase();

        const virality =
            this.percentage(
                this.spread.virality_score
            );

        let communities =
            PROPAGATION_RULES.COMMUNITIES[risk] ?? 2;

        if (virality > 70)
            communities++;

        return this.clamp(
            communities,
            2,
            5
        );
    }

    generateSeed() {
        return `${this.metadata.analysis_id || "analysis"}-${this.metadata.timestamp || Date.now()}`;
    }
    analysis() {
        return {
            pageRankIterations: 20,
            dampingFactor: 0.85
        };
    }
    generate() {

        const graph = this.graph();

        return {

            graph,

            composition: this.composition(graph),

            propagation: this.propagation(),

            simulation: this.simulation(),

            followers: this.followers(),

            initialInfluence: this.initialInfluence(),

            layout: this.layout(),

            metadata: this.metadataInfo(),

            analysis: this.analysis(),
        };
    }
}
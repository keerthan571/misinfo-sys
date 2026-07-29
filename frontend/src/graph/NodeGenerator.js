import {
    NODE_TYPES,
    NODE_COLORS,
    DEFAULT_NODE_DATA,
    GRAPH_LAYOUT,
    PLATFORMS
} from "./constants";

import {
    uuid,
    createSeededRandom,
    randomInt,
    randomFloat,
    randomChoice,
    generatePosition
} from "./GraphUtils";

export default class NodeGenerator {
    constructor(blueprint) {
        this.blueprint = blueprint;
        this.nodes = [];
        this.random = createSeededRandom(
            blueprint.metadata.seed || "misinfo"
        );
        this.nodeIndex = 1;
    }

    generate() {
        const claimNode = this.createClaimNode();

        this.nodes.push(claimNode);

        this.buildPropagationTree(
            claimNode.id,
            1,
            this.blueprint.graph.depth
        );

        return this.nodes;
    }

    createClaimNode() {
        return {
            id: uuid("claim"),
            type: NODE_TYPES.CLAIM,
            position: {
                x: 0,
                y: 0
            },
            data: {
                ...DEFAULT_NODE_DATA,
                id: this.nodeIndex++,
                label: "Original Claim",
                nodeType: NODE_TYPES.CLAIM,
                color: NODE_COLORS.claim,
                followers: 0,
                influenceScore: 100,
                shareProbability: 1,
                verified: false,
                viral: true,
                community: 0,
                platform:
                    this.blueprint.metadata.platform ||
                    PLATFORMS.UNKNOWN,
                parentId: null,
                level: 0,
                createdAt: this.generateTimestamp(0)
            }
        };
    }

    buildPropagationTree(parentId, level, maxDepth) {
        if (
            this.nodes.length >=
            this.blueprint.graph.totalNodes
        ) {
            return;
        }
        if (level > maxDepth) return;

        const remaining =
            this.blueprint.graph.totalNodes -
            this.nodes.length;

        const childCount = Math.min(
            remaining,
            this.calculateChildren(level)
        );

        for (let i = 0; i < childCount; i++) {
            const nodeType = this.resolveNodeType(level);

            const node = this.createNode(
                nodeType,
                parentId,
                level
            );

            this.nodes.push(node);

            this.buildPropagationTree(
                node.id,
                level + 1,
                maxDepth
            );
        }
    }

    calculateChildren(level) {
        const probability =
            this.blueprint.propagation.spreadProbability;

        const decay = Math.max(
            1,
            this.blueprint.graph.depth - level + 1
        );

        const maxChildren = Math.max(
            1,
            Math.round(probability * decay)
        );

        return randomInt(
            this.random,
            1,
            maxChildren
        );
    }

    resolveNodeType(level) {
        if (level === 1) {
            return NODE_TYPES.INFLUENCER;
        }

        const botRatio =
            this.blueprint.composition.botRatio;

        if (
            randomFloat(this.random, 0, 1) < botRatio
        ) {
            return NODE_TYPES.BOT;
        }

        return NODE_TYPES.USER;
    }

    createNode(type, parentId, level) {
        const position = generatePosition(
            this.random,
            level,
            GRAPH_LAYOUT.LEVEL_GAP,
            GRAPH_LAYOUT.NODE_GAP
        );

        return {
            id: uuid(type),
            type,
            position,
            data: {
                ...DEFAULT_NODE_DATA,
                id: this.nodeIndex++,
                label: this.generateLabel(type),
                nodeType: type,
                color: this.resolveColor(type),
                parentId,
                level,
                followers: this.generateFollowers(type),
                influenceScore:
                    this.generateInfluence(type),
                shareProbability:
                    this.generateShareProbability(type),
                verified: this.isVerified(type),
                viral: false,
                community: this.generateCommunity(),
                platform: randomChoice(
                    this.random,
                    this.platforms
                ),
                createdAt: this.generateTimestamp(level)
            }
        };
    }
    generateLabel(type) {
      switch (type) {
        case NODE_TYPES.INFLUENCER:
          return `Influencer ${this.nodeIndex}`;

        case NODE_TYPES.BOT:
          return `Bot ${this.nodeIndex}`;

        case NODE_TYPES.USER:
          return `User ${this.nodeIndex}`;

        default:
          return `Node ${this.nodeIndex}`;
      }
    }

    generateFollowers(type) {
        switch (type) {
            case NODE_TYPES.INFLUENCER:
                return randomInt(
                    this.random,
                    50000,
                    500000
                );

            case NODE_TYPES.BOT:
                return randomInt(
                    this.random,
                    50,
                    1000
                );

            default:
                return randomInt(
                    this.random,
                    100,
                    10000
                );
        }
    }

    generateInfluence(type) {
        switch (type) {
            case NODE_TYPES.INFLUENCER:
                return Number(
                  randomFloat(
                        this.random,
                        75,
                        100
                    ).toFixed(1)
                );

            case NODE_TYPES.BOT:
              return Number(
                  randomFloat(
                      this.random,
                      40,
                      80
                  ).toFixed(1)
              );

            default:
                return Number(
                    randomFloat(
                        this.random,
                        20,
                        70
                    ).toFixed(1)
                );
        }
    }

    generateShareProbability(type) {
        const base =
            this.blueprint.propagation.spreadProbability;
        let value;

        switch (type) {
            case NODE_TYPES.INFLUENCER:
                return Number(
                    Math.min(
                        1,
                        value
                    ).toFixed(2)
                );

            case NODE_TYPES.BOT:
                return Number(
                    Math.min(
                        1,
                        value
                    ).toFixed(2)
                );

            default:
                return Number(
                    Math.min(
                        1,
                        value
                    ).toFixed(2)
                );
        }
    }

    resolveColor(type) {
        switch (type) {
            case NODE_TYPES.CLAIM:
                return NODE_COLORS.claim;

            case NODE_TYPES.INFLUENCER:
                return NODE_COLORS.influencer;

            case NODE_TYPES.BOT:
                return NODE_COLORS.bot;

            default:
                return NODE_COLORS.user;
        }
    }

    isVerified(type) {
        if (type !== NODE_TYPES.INFLUENCER)
            return false;

        return (
            randomFloat(this.random, 0, 1) < 0.35
        );
    }

    generateCommunity() {
        return randomInt(
            this.random,
            1,
            6
        );
    }

    generateTimestamp(level) {
        const start = Date.now();

        const delay =
            level *
            randomInt(
                this.random,
                10,
                120
            ) *
            1000;

        return new Date(
            start + delay
        ).toISOString();
    }

    getNodes() {
        return this.nodes;
    }
}
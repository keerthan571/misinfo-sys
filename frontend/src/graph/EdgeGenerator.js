import { EDGE_STYLE } from "./constants";

import {
    createSeededRandom,
    randomFloat,
    randomInt
} from "./GraphUtils";

export default class EdgeGenerator {

    constructor(nodes, blueprint) {

        this.nodes =
            [...nodes].sort(
                (a, b) =>
                    String(a.id).localeCompare(
                        String(b.id)
                    )
            );

        this.blueprint = blueprint;

        this.edges = [];

        this.edgeSet = new Set();

        this.random =
            createSeededRandom(
                blueprint.metadata.seed +
                "_edges"
            );

        this.nodeMap =
            new Map(
                this.nodes.map(
                    node => [
                        node.id,
                        node
                    ]
                )
            );

        this.levelMap =
            this.groupNodesByLevel();

        this.communityMap =
            this.groupNodesByCommunity();

        this.branchColors =
            new Map();

        this.branchColorIndex = 0;

        this.branchPalette = [
            "#3b82f6",
            "#22c55e",
            "#f59e0b",
            "#a855f7",
            "#ef4444",
            "#06b6d4",
            "#ec4899",
            "#84cc16",
            "#f97316",
            "#6366f1"
        ];

        this.randomEdgeColors = [
            "#14b8a6",
            "#e879f9",
            "#fb7185",
            "#38bdf8",
            "#c084fc",
            "#fbbf24"
        ];
    }

    generate() {

        this.buildTreeEdges();

        if (
            this.blueprint.graph.density >
            0.35
        ) {
            this.buildCrossEdges();
        }

        if (
            this.blueprint.composition.communities >
            1
        ) {
            this.buildCommunityEdges();
        }

        if (
            this.blueprint.propagation.spreadProbability >
            0.55
        ) {
            this.buildReshareEdges();
        }

        return this.edges;
    }

    groupNodesByLevel() {

        const map = new Map();

        this.nodes.forEach(node => {

            const level =
                node.data.level;

            if (!map.has(level)) {
                map.set(level, []);
            }

            map.get(level).push(node);
        });

        return map;
    }

    groupNodesByCommunity() {

        const map = new Map();

        this.nodes.forEach(node => {

            const community =
                node.data.community;

            if (!map.has(community)) {
                map.set(community, []);
            }

            map.get(community).push(node);
        });

        return map;
    }

    buildTreeEdges() {

        this.nodes.forEach(node => {

            if (!node.data.parentId) {
                return;
            }

            const parent =
                this.nodeMap.get(
                    node.data.parentId
                );

            if (!parent) {
                return;
            }

            this.createEdge(
                parent,
                node,
                "tree"
            );
        });
    }

    getBranchKey(node) {

        let current = node;

        while (
            current &&
            current.data.level > 1 &&
            current.data.parentId
        ) {

            const parent =
                this.nodeMap.get(
                    current.data.parentId
                );

            if (!parent) {
                break;
            }

            current = parent;
        }

        return current?.id || node.id;
    }

    getBranchColor(node) {

        const branchKey =
            this.getBranchKey(node);

        if (
            this.branchColors.has(
                branchKey
            )
        ) {
            return this.branchColors.get(
                branchKey
            );
        }

        const color =
            this.branchPalette[
                this.branchColorIndex %
                this.branchPalette.length
            ];

        this.branchColorIndex++;

        this.branchColors.set(
            branchKey,
            color
        );

        return color;
    }

    getRandomEdgeColor() {

        const index =
            Math.floor(
                this.random() *
                this.randomEdgeColors.length
            );

        return this.randomEdgeColors[
            index
        ];
    }

    buildCrossEdges() {

        const probability =
            Math.min(
                0.15,
                0.05 +
                this.blueprint
                    .propagation
                    .spreadProbability *
                0.10
            );

        this.nodes.forEach(
            target => {

                if (
                    target.data.level <= 0
                ) {
                    return;
                }

                if (
                    this.random() >
                    probability
                ) {
                    return;
                }

                const candidates =
                    this.nodes.filter(
                        node =>
                            node.data.level ===
                                target.data.level - 1 &&
                            node.id !== target.id &&
                            node.id !==
                                target.data.parentId
                    );

                if (
                    !candidates.length
                ) {
                    return;
                }

                candidates.sort(
                    (a, b) =>
                        (
                            b.data.influenceScore -
                            a.data.influenceScore
                        ) ||
                        String(a.id).localeCompare(
                            String(b.id)
                        )
                );

                this.createEdge(
                    candidates[0],
                    target,
                    "cross"
                );
            }
        );
    }

    buildCommunityEdges() {

        const groups = {};

        this.nodes.forEach(node => {

            const community =
                node.data.community;

            if (!groups[community]) {
                groups[community] = [];
            }

            groups[community].push(node);
        });

        Object.keys(groups)
            .sort()
            .forEach(key => {

                const nodes =
                    groups[key];

                nodes.sort(
                    (a, b) =>
                        (
                            b.data.influenceScore -
                            a.data.influenceScore
                        ) ||
                        String(a.id).localeCompare(
                            String(b.id)
                        )
                );

                for (
                    let i = 1;
                    i < nodes.length;
                    i++
                ) {

                    if (
                        this.random() >
                        0.35
                    ) {
                        continue;
                    }

                    const hub =
                        nodes[
                            randomInt(
                                this.random,
                                0,
                                Math.min(
                                    2,
                                    i - 1
                                )
                            )
                        ];

                    this.createEdge(
                        hub,
                        nodes[i],
                        "community"
                    );
                }
            });
    }

    buildReshareEdges() {

        this.nodes.forEach(
            source => {

                if (
                    source.data.level === 0
                ) {
                    return;
                }

                if (
                    this.random() >
                    source.data
                        .shareProbability
                ) {
                    return;
                }

                const communityNodes =
                    this.communityMap.get(
                        source.data.community
                    ) || [];

                const candidates =
                    communityNodes.filter(
                        node =>
                            node.data.level ===
                                source.data.level - 1 &&
                            node.id !== source.id &&
                            node.id !==
                                source.data.parentId
                    );

                if (
                    !candidates.length
                ) {
                    return;
                }

                candidates.sort(
                    (a, b) =>
                        (
                            b.data.influenceScore -
                            a.data.influenceScore
                        ) ||
                        String(a.id).localeCompare(
                            String(b.id)
                        )
                );

                this.createEdge(
                    source,
                    candidates[0],
                    "reshare"
                );
            }
        );
    }

    createEdge(
        source,
        target,
        type
    ) {

        if (!source || !target) {
            return;
        }

        if (
            source.id === target.id
        ) {
            return;
        }

        const key =
            [
                source.id,
                target.id
            ]
                .sort()
                .join("-");

        if (
            this.edgeSet.has(key)
        ) {
            return;
        }

        this.edgeSet.add(key);

        const weight =
            this.calculateWeight(
                source,
                target
            );

        const delay =
            this.calculateDelay(
                source
            );

        let color;

        if (type === "tree") {

            color =
                this.getBranchColor(
                    target
                );

        } else {

            color =
                this.getRandomEdgeColor();
        }

        let opacity = 0.75;

        let strokeWidth =
            Math.max(
                1.8,
                weight
            );

        if (type === "tree") {

            opacity = 0.95;

            strokeWidth =
                Math.max(
                    2.4,
                    weight
                );
        }

        if (type === "reshare") {

            opacity = 0.55;

            strokeWidth = 1.8;
        }

        if (
            type === "cross" ||
            type === "community"
        ) {

            opacity = 0.45;

            strokeWidth = 1.5;
        }

        this.edges.push({

            id:
                `edge-${source.id}-${target.id}-${type}`,

            source:
                source.id,

            target:
                target.id,

            type:
                "smoothstep",

            animated:
                type === "tree" ||
                type === "reshare",

            data: {

                interaction:
                    type,

                weight,

                delay
            },

            style: {

                stroke:
                    color,

                strokeWidth,

                opacity
            }
        });
    }

    calculateWeight(
        source,
        target
    ) {

        const probability =
            (
                source.data.shareProbability +
                target.data.shareProbability
            ) / 2;

        const influence =
            (
                source.data.influenceScore +
                target.data.influenceScore
            ) / 2;

        const followers =
            Math.min(
                source.data.followers,
                100000
            ) / 100000;

        return Number(
            (
                probability * 4 +
                influence / 30 +
                followers * 1.2
            ).toFixed(2)
        );
    }

    calculateDelay(source) {

        const base =
            randomFloat(
                this.random,
                15,
                60
            );

        return Math.max(
            5,
            Math.round(
                (
                    base +
                    source.data.level * 10
                ) /
                Math.max(
                    source.data
                        .shareProbability,
                    0.1
                )
            )
        );
    }

    getEdges() {
        return this.edges;
    }
}
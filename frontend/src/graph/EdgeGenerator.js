import { EDGE_STYLE } from "./constants";
import {
    uuid,
    createSeededRandom,
    randomFloat,
    randomInt
} from "./GraphUtils";

export default class EdgeGenerator {
    constructor(nodes, blueprint) {
        this.nodes = nodes;
        this.blueprint = blueprint;

        this.edges = [];
        this.edgeSet = new Set();

        this.random = createSeededRandom(
            blueprint.metadata.seed + "_edges"
        );

        this.nodeMap = new Map(
            nodes.map(node => [node.id, node])
        );

        this.levelMap = this.groupNodesByLevel();

        this.communityMap = this.groupNodesByCommunity();
    }

    generate() {
        this.buildTreeEdges();

        if (this.blueprint.graph.density > 0.35)
            this.buildCrossEdges();

        if (this.blueprint.composition.communities > 1)
            this.buildCommunityEdges();

        if (
            this.blueprint.propagation.spreadProbability > 0.55
        )
            this.buildReshareEdges();

        return this.edges;
    }

    groupNodesByLevel() {
        const map = new Map();

        this.nodes.forEach(node => {
            const level = node.data.level;

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
            if (!node.data.parentId) return;

            const parent =
                this.nodeMap.get(node.data.parentId);

            if (!parent) return;

            this.createEdge(
                parent,
                node,
                "tree"
            );
        });
    }

    buildCrossEdges() {

        const probability =
            Math.min(
                0.15,
                0.05 +
                this.blueprint.propagation.spreadProbability * 0.10
            );

        this.nodes.forEach(target => {

            // Skip root node
            if (target.data.level <= 0)
                return;

            // Random chance of creating a cross edge
            if (this.random() > probability)
                return;

            const candidates =
                this.nodes.filter(node =>
                    node.data.level === target.data.level - 1 &&
                    node.id !== target.id &&
                    node.id !== target.data.parentId
                );

            if (!candidates.length)
                return;

            candidates.sort(
                (a, b) =>
                    b.data.influenceScore -
                    a.data.influenceScore
            );

            const source = candidates[0];

            this.createEdge(
                source,
                target,
                "cross"
            );

        });

    }

    buildCommunityEdges() {

        const groups = {};

        this.nodes.forEach(node => {

            const community = node.data.community;

            if (!groups[community])
                groups[community] = [];

            groups[community].push(node);

        });

        Object.values(groups).forEach(nodes => {

            nodes.sort(
                (a, b) =>
                    b.data.influenceScore -
                    a.data.influenceScore
            );

            for (let i = 1; i < nodes.length; i++) {

                if (this.random() > 0.35)
                    continue;

                const hub =
                    nodes[
                    randomInt(
                        this.random,
                        0,
                        Math.min(2, i - 1)
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

        this.nodes.forEach(source => {

            if (source.data.level === 0)
                return;

            if (
                this.random() >
                source.data.shareProbability
            )
                return;


            const communityNodes =
                this.communityMap.get(
                    source.data.community
                ) || [];

            const candidates =
                communityNodes.filter(node =>
                    node.data.level === source.data.level - 1 &&
                    node.id !== source.id &&
                    node.id !== source.data.parentId
                );

            if (!candidates.length)
                return;

            candidates.sort(
                (a, b) =>
                    b.data.influenceScore -
                    a.data.influenceScore
            );

            const target = candidates[0];

            this.createEdge(
                source,
                target,
                "reshare"
            );

        });

    }

    createEdge(source, target, type) {

        if (!source || !target)
            return;

        if (source.id === target.id)
            return;

        const key =
            [source.id, target.id]
                .sort()
                .join("-");

        if (this.edgeSet.has(key))
            return;

        this.edgeSet.add(key);

        const weight =
            this.calculateWeight(
                source,
                target
            );

        const delay =
            this.calculateDelay(source);

        const colors = {

            tree: "#3b82f6",

            cross: "#10b981",

            community: "#8b5cf6",

            reshare: "#f59e0b"

        };

        this.edges.push({

            id: uuid("edge"),

            source: source.id,

            target: target.id,

            type: "smoothstep",

            animated:
                type === "tree" ||
                type === "reshare",

            data: {

                interaction: type,

                weight,

                delay

            },

            style: {

                stroke:
                    colors[type] ||
                    "#94a3b8",

                strokeWidth:
                    type === "reshare"
                        ? 1.2
                        : weight,

                opacity:
                    type === "tree"
                        ? 0.95
                        : type === "reshare"
                            ? 0.35
                            : 0.60

            }

        });

    }

    calculateWeight(source, target) {
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
                    source.data.shareProbability,
                    0.1
                )
            )
        );
    }

    getEdges() {
        return this.edges;
    }
}
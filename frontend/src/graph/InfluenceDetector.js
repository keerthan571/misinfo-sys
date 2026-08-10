export default class InfluenceDetector {

    constructor(nodes, edges, blueprint) {
        this.nodes = nodes;
        this.edges = edges;
        this.blueprint = blueprint;

        this.nodeMap = new Map();
        this.adjacency = new Map();
        this.inDegree = new Map();
    }

    detect() {

        this.initialize();
        this.calculateDegree();
        this.calculateReach();
        this.calculatePageRank();
        this.calculateInfluence();

        return this.rankNodes();
    }

    initialize() {

        this.nodes.forEach(node => {

            this.nodeMap.set(node.id, node);

            this.adjacency.set(
                node.id,
                []
            );

            this.inDegree.set(
                node.id,
                0
            );
        });

        this.edges.forEach(edge => {

            if (
                !this.adjacency.has(edge.source) ||
                !this.inDegree.has(edge.target)
            ) {
                return;
            }

            this.adjacency
                .get(edge.source)
                .push(edge.target);

            this.inDegree.set(
                edge.target,
                this.inDegree.get(edge.target) + 1
            );
        });
    }

    calculateDegree() {

        this.nodes.forEach(node => {

            const outgoing =
                this.adjacency.get(node.id) || [];

            const incoming =
                this.inDegree.get(node.id) || 0;

            node.data.outDegree =
                outgoing.length;

            node.data.inDegree =
                incoming;

            node.data.degree =
                outgoing.length + incoming;
        });
    }

    calculateReach() {

        this.nodes.forEach(node => {

            const visited = new Set();

            this.dfs(
                node.id,
                visited
            );

            node.data.reach =
                Math.max(
                    0,
                    visited.size - 1
                );

            const shareProbability =
                Number(
                    node.data.shareProbability
                ) || 0;

            node.data.weightedReach =
                node.data.reach *
                (
                    shareProbability > 1
                        ? shareProbability / 100
                        : shareProbability
                );
        });
    }

    dfs(nodeId, visited) {

        if (visited.has(nodeId)) {
            return;
        }

        visited.add(nodeId);

        const neighbours =
            this.adjacency.get(nodeId) || [];

        neighbours.forEach(next =>
            this.dfs(
                next,
                visited
            )
        );
    }

    calculatePageRank() {

        const damping =
            this.blueprint?.analysis?.dampingFactor ??
            0.85;

        const iterations =
            this.blueprint?.analysis?.pageRankIterations ??
            20;

        const total =
            this.nodes.length;

        if (total === 0) {
            return;
        }

        this.nodes.forEach(node => {

            node.data.pageRank =
                1 / total;
        });

        for (
            let i = 0;
            i < iterations;
            i++
        ) {

            const next =
                new Map();

            this.nodes.forEach(node => {

                next.set(
                    node.id,
                    (1 - damping) / total
                );
            });

            this.nodes.forEach(node => {

                const outgoing =
                    this.adjacency.get(node.id) || [];

                if (!outgoing.length) {
                    return;
                }

                const contribution =
                    (
                        node.data.pageRank *
                        damping
                    ) /
                    outgoing.length;

                outgoing.forEach(target => {

                    if (!next.has(target)) {
                        return;
                    }

                    next.set(
                        target,
                        next.get(target) +
                        contribution
                    );
                });
            });

            this.nodes.forEach(node => {

                node.data.pageRank =
                    next.get(node.id) ?? 0;
            });
        }
    }

    calculateInfluence() {

        if (!this.nodes.length) {
            return;
        }

        const maxDegree =
            Math.max(
                ...this.nodes.map(node =>
                    Number(
                        node.data.degree
                    ) || 0
                ),
                1
            );

        const maxReach =
            Math.max(
                ...this.nodes.map(node =>
                    Number(
                        node.data.reach
                    ) || 0
                ),
                1
            );

        const maxFollowers =
            Math.max(
                ...this.nodes.map(node =>
                    Number(
                        node.data.followers
                    ) || 0
                ),
                1
            );

        const maxPageRank =
            Math.max(
                ...this.nodes.map(node =>
                    Number(
                        node.data.pageRank
                    ) || 0
                ),
                0.000000001
            );

        this.nodes.forEach(node => {

            const data =
                node.data;

            const pageRankScore =
                (
                    (
                        Number(
                            data.pageRank
                        ) || 0
                    ) /
                    maxPageRank
                ) * 100;

            const reachScore =
                (
                    (
                        Number(
                            data.reach
                        ) || 0
                    ) /
                    maxReach
                ) * 100;

            const degreeScore =
                (
                    (
                        Number(
                            data.degree
                        ) || 0
                    ) /
                    maxDegree
                ) * 100;

            let shareProbability =
                Number(
                    data.shareProbability
                ) || 0;

            if (shareProbability <= 1) {
                shareProbability *= 100;
            }

            shareProbability =
                Math.min(
                    Math.max(
                        shareProbability,
                        0
                    ),
                    100
                );

            const followerScore =
                (
                    (
                        Number(
                            data.followers
                        ) || 0
                    ) /
                    maxFollowers
                ) * 100;

            const aiInfluence =
                Math.min(
                    Math.max(
                        Number(
                            data.influenceScore
                        ) || 0,
                        0
                    ),
                    100
                );

            const finalScore =
                pageRankScore * 0.25 +
                reachScore * 0.20 +
                degreeScore * 0.20 +
                shareProbability * 0.15 +
                followerScore * 0.10 +
                aiInfluence * 0.10;

            data.pageRankScore =
                Number(
                    pageRankScore.toFixed(2)
                );

            data.reachScore =
                Number(
                    reachScore.toFixed(2)
                );

            data.degreeScore =
                Number(
                    degreeScore.toFixed(2)
                );

            data.followerScore =
                Number(
                    followerScore.toFixed(2)
                );

            data.networkInfluence =
                Number(
                    finalScore.toFixed(2)
                );
        });

        const maxInfluence =
            Math.max(
                ...this.nodes.map(node =>
                    Number(
                        node.data.networkInfluence
                    ) || 0
                ),
                0
            );

        this.nodes.forEach(node => {

            const influence =
                Number(
                    node.data.networkInfluence
                ) || 0;

            node.data.networkInfluencePercent =
                maxInfluence > 0
                    ? Number(
                        (
                            influence /
                            maxInfluence *
                            100
                        ).toFixed(2)
                    )
                    : 0;
        });
    }

    rankNodes() {

        const ranked =
            [...this.nodes]
                .filter(node =>
                    Number(
                        node.data.level
                    ) > 0
                )
                .sort(
                    (a, b) =>
                        (
                            Number(
                                b.data.networkInfluence
                            ) || 0
                        ) -
                        (
                            Number(
                                a.data.networkInfluence
                            ) || 0
                        )
                );

        ranked.forEach(
            (node, index) => {

                node.data.rank =
                    index + 1;

                node.data.isTopInfluencer =
                    index < 10;
            }
        );

        this.rankedNodes =
            ranked;

        return ranked;
    }

    getTopInfluencers(limit = 10) {

        if (!this.rankedNodes) {
            return [];
        }

        return this.rankedNodes.slice(
            0,
            limit
        );
    }

    getAnalytics() {

        const totalNodes =
            this.nodes.length;

        const totalEdges =
            this.edges.length;

        const averageInfluence =
            totalNodes === 0
                ? 0
                : Number(
                    (
                        this.nodes.reduce(
                            (sum, node) =>
                                sum +
                                (
                                    Number(
                                        node.data.networkInfluence
                                    ) || 0
                                ),
                            0
                        ) /
                        totalNodes
                    ).toFixed(2)
                );

        const highestInfluence =
            totalNodes === 0
                ? 0
                : Math.max(
                    ...this.nodes.map(
                        node =>
                            Number(
                                node.data.networkInfluence
                            ) || 0
                    )
                );

        const averageReach =
            totalNodes === 0
                ? 0
                : Number(
                    (
                        this.nodes.reduce(
                            (sum, node) =>
                                sum +
                                (
                                    Number(
                                        node.data.reach
                                    ) || 0
                                ),
                            0
                        ) /
                        totalNodes
                    ).toFixed(2)
                );

        const averageDegree =
            totalNodes === 0
                ? 0
                : Number(
                    (
                        this.nodes.reduce(
                            (sum, node) =>
                                sum +
                                (
                                    Number(
                                        node.data.degree
                                    ) || 0
                                ),
                            0
                        ) /
                        totalNodes
                    ).toFixed(2)
                );

        const spreadEfficiency =
            Number(
                (
                    averageReach /
                    Math.max(
                        averageDegree,
                        1
                    )
                ).toFixed(2)
            );

        return {

            totalNodes,

            totalEdges,

            averageInfluence,

            highestInfluence,

            averageReach,

            averageDegree,

            density:
                totalNodes > 1
                    ? Number(
                        (
                            totalEdges /
                            (
                                totalNodes *
                                (totalNodes - 1)
                            )
                        ).toFixed(4)
                    )
                    : 0,

            spreadEfficiency,

            largestCommunity:
                this.findLargestCommunity(),

            topInfluencers:
                this.getTopInfluencers(5)
        };
    }

    findLargestCommunity() {

        const communities =
            new Map();

        this.nodes.forEach(node => {

            const community =
                node.data.community;

            communities.set(
                community,
                (
                    communities.get(
                        community
                    ) || 0
                ) + 1
            );
        });

        let largest = {
            community: "",
            size: 0
        };

        communities.forEach(
            (size, community) => {

                if (
                    size >
                    largest.size
                ) {

                    largest = {
                        community,
                        size
                    };
                }
            }
        );

        return `${largest.community} (${largest.size} nodes)`;
    }

    getNodes() {
        return this.nodes;
    }

    getEdges() {
        return this.edges;
    }
}
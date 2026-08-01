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
            this.adjacency.set(node.id, []);
            this.inDegree.set(node.id, 0);
        });

        this.edges.forEach(edge => {
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
            node.data.outDegree =
                this.adjacency.get(node.id).length;

            node.data.inDegree =
                this.inDegree.get(node.id);

            node.data.degree =
                node.data.outDegree +
                node.data.inDegree;
        });
    }

    calculateReach() {
        this.nodes.forEach(node => {
            const visited = new Set();

            this.dfs(node.id, visited);

            node.data.reach =
            Math.max(
                0,
                visited.size - 1
            );

            node.data.weightedReach =
            node.data.reach *
            (
                node.data.shareProbability ??
                1
            );
        });
    }

    dfs(nodeId, visited) {
        if (visited.has(nodeId))
            return;

        visited.add(nodeId);

        const neighbours =
            this.adjacency.get(nodeId) || [];

        neighbours.forEach(next =>
            this.dfs(next, visited)
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

        if (total === 0)
            return;

        // Initialize PageRank
        this.nodes.forEach(node => {
            node.data.pageRank =
                1 / total;
        });

        // Iterative PageRank
        for (let i = 0; i < iterations; i++) {

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
                    this.adjacency.get(node.id);

                if (!outgoing.length)
                    return;

                const contribution =
                    (node.data.pageRank * damping) /
                    outgoing.length;

                outgoing.forEach(target => {

                    next.set(
                        target,
                        next.get(target) + contribution
                    );

                });

            });

            this.nodes.forEach(node => {

                node.data.pageRank =
                    next.get(node.id);

            });
        }
    }

    calculateInfluence() {

        let maxRank = 0;

        this.nodes.forEach(node => {

            if (node.data.pageRank > maxRank) {
                maxRank = node.data.pageRank;
            }

        });

        this.nodes.forEach(node => {

            const pageRank =
                maxRank === 0
                    ? 0
                    : (node.data.pageRank / maxRank) * 100;

            node.data.pageRankScore =
                Number(
                    pageRank.toFixed(2)
                );

            const baseInfluence =
                node.data.influenceScore;

            const followers =
                Math.min(
                    node.data.followers,
                    100000
                ) / 1000;

            const finalScore =
                baseInfluence * 0.25 +
                node.data.pageRankScore * 0.35 +
                node.data.degree * 1.20 +
                node.data.weightedReach * 0.35 +
                followers * 0.08;

            node.data.networkInfluence =
                Number(
                    finalScore.toFixed(2)
                );

        });

        const maxInfluence =
            Math.max(
                ...this.nodes.map(
                    node =>
                        node.data.networkInfluence
                )
            );

        this.nodes.forEach(node => {

            node.data.networkInfluencePercent =
                maxInfluence === 0
                    ? 0
                    : Number(
                        (
                            node.data.networkInfluence /
                            maxInfluence *
                            100
                        ).toFixed(2)
                    );

        });

    }

    rankNodes() {
        const ranked =
            [...this.nodes]
                .filter(node => node.data.level > 0)
                .sort(
                    (a, b) =>
                        b.data.networkInfluence -
                        a.data.networkInfluence
                );

        ranked.forEach((node, index) => {
            node.data.rank = index + 1;
            node.data.isTopInfluencer =
                index < 10;
        });

        this.rankedNodes = ranked;

        return ranked;
    }

    getTopInfluencers(limit = 10) {
        if (!this.rankedNodes) {
            return [];
        }

        return this.rankedNodes.slice(0, limit);
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
                                node.data.networkInfluence,
                            0
                        ) / totalNodes
                    ).toFixed(2)
                );

        const highestInfluence =
            totalNodes === 0
                ? 0
                : Math.max(
                    ...this.nodes.map(
                        node =>
                            node.data.networkInfluence
                    )
                );

        const averageReach =
          totalNodes === 0
              ? 0
              : Number(
                    (
                        this.nodes.reduce(
                            (sum, node) =>
                                sum + node.data.reach,
                            0
                        ) / totalNodes
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
                                node.data.degree,
                            0
                        ) / totalNodes
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
                (communities.get(community) || 0) + 1
            );

        });

        let largest = {
            community: "",
            size: 0
        };

        communities.forEach(
            (size, community) => {

                if (size > largest.size) {

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
export default class InfluenceDetector {
  constructor(nodes, edges) {
    this.nodes = nodes;
    this.edges = edges;

    this.nodeMap = new Map();
    this.adjacency = new Map();
  }

  /**
   * Public API
   */
  detect() {
    this.initialize();

    this.calculateDegree();

    this.calculateReach();

    this.calculateInfluenceScore();

    return this.getTopInfluencers();
  }

  /**
   * Build lookup structures.
   */
  initialize() {
    this.nodes.forEach((node) => {
      this.nodeMap.set(node.id, node);

      this.adjacency.set(node.id, []);
    });

    this.edges.forEach((edge) => {
      if (this.adjacency.has(edge.source)) {
        this.adjacency
          .get(edge.source)
          .push(edge.target);
      }
    });
  }

  /**
   * Degree centrality.
   */
  calculateDegree() {
    this.nodes.forEach((node) => {
      node.data.degree = 0;
    });

    this.edges.forEach((edge) => {
      const source = this.nodeMap.get(edge.source);
      const target = this.nodeMap.get(edge.target);

      if (source) source.data.degree++;

      if (target) target.data.degree++;
    });
  }

  /**
   * Reach score using outgoing edges.
   */
  calculateReach() {
    this.nodes.forEach((node) => {
      node.data.reach =
        this.adjacency.get(node.id).length;
    });
  }

  /**
   * Weighted influence score.
   */
  /**
 * Calculates influence using a PageRank-inspired algorithm.
 */
calculateInfluenceScore() {
    const damping = 0.85;
    const iterations = 20;
    const n = this.nodes.length;

    // Initial rank
    this.nodes.forEach((node) => {
        node.data.pageRank = 1 / n;
    });

    for (let iter = 0; iter < iterations; iter++) {
        const newRanks = new Map();

        this.nodes.forEach((node) => {
        newRanks.set(node.id, (1 - damping) / n);
        });

        this.nodes.forEach((node) => {
        const outgoing = this.adjacency.get(node.id);

        if (!outgoing || outgoing.length === 0) return;

        const contribution =
            (node.data.pageRank * damping) /
            outgoing.length;

        outgoing.forEach((targetId) => {
            newRanks.set(
            targetId,
            newRanks.get(targetId) + contribution
            );
        });
        });

        this.nodes.forEach((node) => {
        node.data.pageRank = newRanks.get(node.id);
        });
    }

    // Normalize PageRank to 0–100
    const maxRank = Math.max(
        ...this.nodes.map((n) => n.data.pageRank)
    );

    this.nodes.forEach((node) => {
        node.data.pageRankScore =
        (node.data.pageRank / maxRank) * 100;
    });

    // Final influence score
    this.nodes.forEach((node) => {
        const degree = node.data.degree || 0;

        const followers = node.data.followers || 0;

        const engagement =
        (node.data.engagement?.likes || 0) +
        (node.data.engagement?.shares || 0) +
        (node.data.engagement?.comments || 0);

        const pageRank = node.data.pageRankScore;

        const score =
        pageRank * 0.45 +
        degree * 2.0 +
        followers * 0.0008 +
        engagement * 0.02;

        node.data.influenceScore = Math.round(score);
    });
    }
    /**
   * Returns the top influencers after ranking
   * every node by its influence score.
   */
getTopInfluencers() {
    const ranked = [...this.nodes]
        .filter((node) => node.data.level > 0)
        .sort(
        (a, b) =>
            b.data.influenceScore -
            a.data.influenceScore
        );

    ranked.forEach((node, index) => {
        node.data.rank = index + 1;
        node.data.isInfluencer = index < 10;

        if (index < 10) {
        node.style = {
            ...node.style,
            border: "3px solid #FFD700",
            borderRadius: "50%",
        };
        }
    });

    return ranked.slice(0, 10);
    }
  /**
   * Returns useful analytics for dashboard.
   */
  getAnalytics() {
    const totalNodes = this.nodes.length;

    const totalEdges = this.edges.length;

    const averageInfluence =
        Math.round(
        this.nodes.reduce(
            (sum, node) =>
            sum + node.data.influenceScore,
            0
        ) / totalNodes
        );

    const highestInfluence =
        Math.max(
        ...this.nodes.map(
            (n) => n.data.influenceScore
        )
        );

    const averagePageRank =
        this.nodes.reduce(
        (sum, node) =>
            sum + node.data.pageRank,
        0
        ) / totalNodes;

    return {
        totalNodes,
        totalEdges,
        averageInfluence,
        highestInfluence,
        averagePageRank,
    };
  } 
  /**
   * Getter.
   */
  getNodes() {
    return this.nodes;
  }

  /**
   * Getter.
   */
  getEdges() {
    return this.edges;
  }
}
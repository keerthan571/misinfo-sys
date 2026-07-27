import {
  uuid,
  polarToCartesian,
  distributeNodes,
  createSeededRandom,
  randomFloat,
} from "./GraphUtils";

import {
  NODE_TYPES,
  NODE_COLORS,
  LAYOUT_CONFIG,
  DEFAULT_NODE_DATA,
} from "./constants";

export default class NodeGenerator {
  constructor(parameters) {
    this.params = parameters;
    this.random = createSeededRandom(parameters.simulationSeed);
    this.parentCapacity = new Map();
    this.nodes = [];
    this.nodeLevels = [];
    this.nodeIndex = 0;
  }

  /**
   * Public API
   */
    generate() {
        this.createOriginNode();

        this.generatePropagationLevels();

        this.assignInfluencers();

        return this.nodes;
    }
  /**
   * Root node
   */
  createOriginNode() {
    const origin = {
      id: "origin",
      type: "default",

      position: {
        x: 0,
        y: 0,
      },

      data: {
        ...DEFAULT_NODE_DATA,

        label: "Source",

        type: NODE_TYPES.ORIGIN,

        level: 0,

        color: NODE_COLORS.origin,

        size: this.params.averageNodeSize * 1.8,

        influenceScore: 100,

        shared: true,

        degree: 0,

        platform: this.params.platform,

        createdAt: Date.now(),
      },
    };

    this.nodes.push(origin);

    this.nodeLevels.push([origin]);
  }

  /**
   * Creates every propagation level.
   */
  generatePropagationLevels() {
    const distribution = distributeNodes(
      this.params.totalNodes,
      this.params.graphDepth
    );

    for (let level = 1; level <= this.params.graphDepth; level++) {
      const count = distribution[level - 1];

      const nodes = this.generateLevel(level, count);

      this.nodeLevels.push(nodes);

      this.nodes.push(...nodes);
    }
  }
  calculateParentCapacity(parent) {
    const probability = parent.data.shareProbability;
    const influence = parent.data.influenceScore;
    const followers = parent.data.followers;

    const capacity =
        probability * 4 +
        influence / 25 +
        followers / 5000;

    return Math.max(1, Math.round(capacity));
    }
  /**
   * Generates one propagation layer.
   */
  generateLevel(level, count) {
    const levelNodes = [];

    const parents = [...this.nodeLevels[level - 1]];

    let currentX = -count * 90;

    parents.forEach((parent) => {
        let capacity = this.calculateParentCapacity(parent);

        while (capacity > 0 && levelNodes.length < count) {
        const position = {
            x: currentX + randomFloat(-20, 20),
            y:
            level * LAYOUT_CONFIG.LEVEL_GAP +
            randomFloat(-10, 10),
        };

        const node = this.createPropagationNode(
            level,
            position,
            parent
        );

        levelNodes.push(node);

        currentX += 180;

        capacity--;
        }
    });

    return levelNodes;
    }
    /**
   * Creates a single propagation node.
   */
  createPropagationNode(level, position, parent) {
    this.nodeIndex++;

    const nodeType = this.resolveNodeType(level);

    const influence = this.generateInfluence(level);

    const size =
        this.params.averageNodeSize +
        influence * 0.25 +
        randomFloat(-4, 4);

    const id = uuid("node");

    const followers = this.generateFollowers(level, influence);

    const node = {
        id,

        type: "default",

        position,

        draggable: false,

        selectable: true,

        data: {
        ...DEFAULT_NODE_DATA,

        id,

        label: `${nodeType}_${this.nodeIndex}`,

        username: `user_${this.nodeIndex}`,

        type: nodeType,

        level,

        depth: level,

        parentId: parent.id,

        children: 0,

        platform: this.params.platform,

        influenceScore: influence,

        size,

        degree: 0,

        shared: true,

        verified:
            nodetype === node_types.media
                ? true
                : this.random() < 0.12,

        followers,

        engagement: this.generateEngagement(influence),

        color: this.resolveColor(nodeType),

        // Timeline
        delay: Math.round(this.random() * 180),

        shareTime: 0,

        // Propagation
        shareProbability: 0,

        // Community
        cluster: null,

        createdAt:
            Date.now() +
            level * 1000 +
            this.nodeIndex,
        },
    };

    // Calculate share time based on parent
    node.data.shareTime =
        parent.data.shareTime + node.data.delay;

    // Probability that this node reshapes the post
    node.data.shareProbability =
        this.calculateShareProbability(node);
    return node;
    }

  /**
   * Decide which type of account this node represents.
   */
  resolveNodeType(level) {
    const r = this.random();

    if (level === 1 && r < 0.12)
      return NODE_TYPES.INFLUENCER;

    if (r < 0.03)
      return NODE_TYPES.BOT;

    if (r < 0.10)
      return NODE_TYPES.MEDIA;

    if (r < 0.18)
      return NODE_TYPES.INFLUENCER;

    return NODE_TYPES.USER;
  }

  /**
   * Initial influence score.
   */
  generateInfluence(level) {
    const decay =
      100 /
      (level + 1);

    return Math.round(
      decay +
      this.random() * 30
    );
  }

  /**
   * Followers roughly correlate with influence.
   */
  generateFollowers(level, influence) {
    const base =
        this.params.predictedReach /
        this.params.totalNodes;

    const multiplier = Math.max(
        1,
        influence / 30
    );

    return Math.round(
        base *
        multiplier *
        (1 + this.random())
    );
    }

  /**
   * Initial engagement.
   */
  generateEngagement(influence) {
    return {
      likes: Math.round(
        influence * randomFloat(6, 12)
      ),

      shares: Math.round(
        influence * randomFloat(2, 6)
      ),

      comments: Math.round(
        influence * randomFloat(1, 4)
      ),

      views: Math.round(
        influence * randomFloat(25, 80)
      ),
    };
  }

  /**
   * Node colour.
   */
  resolveColor(type) {
    switch (type) {
      case NODE_TYPES.ORIGIN:
        return NODE_COLORS.origin;

      case NODE_TYPES.INFLUENCER:
        return NODE_COLORS.influencer;

      case NODE_TYPES.MEDIA:
        return NODE_COLORS.media;

      case NODE_TYPES.BOT:
        return NODE_COLORS.bot;

      default:
        return NODE_COLORS.user;
    }
  }  /**
   * Marks the top N nodes as influencers based on
   * their initial influence score.
   */
  assignInfluencers() {
    const candidates = this.nodes
      .filter((node) => node.data.level > 0)
      .sort(
        (a, b) =>
          b.data.influenceScore - a.data.influenceScore
      );

    const count = Math.min(
      this.params.influencerCount,
      candidates.length
    );

    for (let i = 0; i < count; i++) {
      const node = candidates[i];

      node.data.type = NODE_TYPES.INFLUENCER;
      node.data.color = NODE_COLORS.influencer;

      node.data.influenceScore = Math.min(
        100,
        node.data.influenceScore + 20
      );

      node.data.followers = Math.round(
        node.data.followers * 2
      );
    }
  }

  /**
   * Optional graph statistics.
   */
  buildStatistics() {
    return {
      totalNodes: this.nodes.length,

      levels: this.nodeLevels.length,

      averageInfluence:
        this.nodes.reduce(
          (sum, node) =>
            sum + node.data.influenceScore,
          0
        ) / this.nodes.length,
    };
  }

  /**
   * Public getter for grouped levels.
   */
  getLevels() {
    return this.nodeLevels;
  }

  /**
   * Public getter for generated nodes.
   */
  getNodes() {
    return this.nodes;
  }
}
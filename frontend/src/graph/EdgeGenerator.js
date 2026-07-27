import { uuid, createSeededRandom } from "./GraphUtils";
import { EDGE_CONFIG } from "./constants";

export default class EdgeGenerator {
    constructor(nodes, parameters) {
        this.nodes = nodes;
        this.params = parameters;

        this.edges = [];

        this.edgeSet = new Set();

        this.levelMap = this.groupNodesByLevel();

        // Deterministic random generator
        this.random = createSeededRandom(
            parameters.simulationSeed + "_edges"
        );

        // Values from backend
        this.virality =
            parameters.viralityScore ?? 50;

        this.spreadProbability =
            parameters.spreadProbability ?? 0.5;

        this.predictedReach =
            parameters.predictedReach ?? 5000;
    }

  /**
   * Public API
   */
  generate() {

    this.buildPropagationTree();

    this.buildCrossLevelConnections();

    this.buildCommunityConnections();

    this.addSecondaryPropagation();

    return this.edges;

   }

  /**
   * Group nodes by propagation level.
   */
  groupNodesByLevel() {
    const map = new Map();

    this.nodes.forEach((node) => {
      const level = node.data.level;

      if (!map.has(level)) {
        map.set(level, []);
      }

      map.get(level).push(node);
    });

    return map;
  }

  /**
   * Main propagation tree.
   *
   * Every node (except origin)
   * has exactly one parent.
   */
  buildPropagationTree() {
    const maxLevel = Math.max(...this.levelMap.keys());

    for (let level = 1; level <= maxLevel; level++) {
        const parents = this.levelMap.get(level - 1) || [];
        const children = this.levelMap.get(level) || [];

        if (!parents.length || !children.length) continue;

        // Higher influence parents get more children
        const parentPool = [];

        parents.forEach((parent) => {
        const capacity = Math.max(
            1,
            Math.round(
            parent.data.shareProbability * 5 +
            parent.data.influenceScore / 20
            )
        );

        for (let i = 0; i < capacity; i++) {
            parentPool.push(parent);
        }
        });

        children.forEach((child) => {
        const parent =
            parentPool[
            Math.floor(this.random() * parentPool.length)
            ];

        this.addEdge(parent, child, "tree");
        });
    }
    }

  /**
   * Additional sharing between nearby levels.
   */
   buildCrossLevelConnections() {

        const probability =
            Math.min(
                0.95,
                this.spreadProbability *
                (this.virality / 100)
            );

        const maxLevel = Math.max(
            ...Array.from(this.levelMap.keys())
        );

        for (let level = 1; level <= maxLevel; level++) {

            const previous =
                this.levelMap.get(level - 1) || [];

            const current =
                this.levelMap.get(level) || [];

            previous.forEach(source => {

                current.forEach(target => {

                    if (this.random() > probability)
                        return;

                    this.addEdge(
                        source,
                        target,
                        "cross"
                    );

                });

            });

        }

    }
        /**
     * Creates community connections inside the
     * same propagation level to simulate
     * interactions between users.
     */
    buildCommunityConnections() {
        const probability = 0.15;

        this.levelMap.forEach((nodes, level) => {
        if (level === 0) return;

        for (let i = 0; i < nodes.length; i++) {
            for (let j = i + 1; j < nodes.length; j++) {
            if (this.random() > probability) continue;

            const source = nodes[i];
            const target = nodes[j];

            this.addEdge(source, target);

            source.data.degree++;
            target.data.degree++;
            }
        }
        });
    }
    addSecondaryPropagation() {

    const nodes =
        this.nodes.filter(
            n=>n.data.level>0
        );

    nodes.forEach(source=>{

        if(
            this.random()>
            source.data.shareProbability
        )
            return;

        const candidates=
            nodes.filter(n=>

                n.id!==source.id &&

                Math.abs(
                    n.data.level-
                    source.data.level
                )<=1

            );

        if(!candidates.length)
            return;

        const target=
            candidates[
                Math.floor(
                    this.random()*
                    candidates.length
                )
            ];

        this.addEdge(
            source,
            target,
            "reshare"
        );

    });

}

  /**
   * Safely adds an edge.
   */
  addEdge(source, target, propagationType = "tree") {

        if (!source || !target)
            return;

        if (source.id === target.id)
            return;

        const key =
            `${source.id}-${target.id}`;

        if (this.edgeSet.has(key))
            return;

        this.edgeSet.add(key);

        const influenceFactor =
            (
                source.data.influenceScore +
                target.data.influenceScore
            ) / 200;

        const probability =
            this.spreadProbability *
            influenceFactor;

        const engagement =
            (source.data.engagement.likes||0)+
            (source.data.engagement.shares||0);

            const weight=

            (
            probability*5+

            source.data.influenceScore/25+

            engagement/200

            ).toFixed(2);

        this.edges.push({

            id: uuid("edge"),

            source: source.id,

            target: target.id,

            type: EDGE_CONFIG.TYPE,

            animated:
                propagationType !== "community",

            style: {

                strokeWidth: weight,

                opacity:

                Math.min(

                1,

                0.25+

                weight/10

                )

            },

            data: {

                propagationType,

                probability,

                weight,

                delay:
                Math.max(
                5,
                Math.round(
                120-
                source.data.influenceScore+
                this.random()*20
                )

                )

            }

        });

    }

  /**
   * Graph statistics.
   */
  getStatistics() {
    return {
      totalEdges: this.edges.length,

      averageDegree:
        this.nodes.reduce(
          (sum, node) => sum + node.data.degree,
          0
        ) / this.nodes.length,
    };
  }

  /**
   * Getter.
   */
  getEdges() {
    return this.edges;
  }
}
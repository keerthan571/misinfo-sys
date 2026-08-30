import { createSeededRandom, randomFloat } from "./GraphUtils";

export default class EdgeGenerator {

    constructor(nodes, blueprint) {

        /*
         * Keep node ordering deterministic.
         *
         * Same blueprint seed + same nodes
         * = same edges every time.
         */
        this.nodes = [...nodes].sort(
            (a, b) =>
                String(a.id).localeCompare(
                    String(b.id),
                    undefined,
                    { numeric: true }
                )
        );

        this.blueprint = blueprint;

        this.edges = [];

        this.edgeSet = new Set();

        /*
         * Deterministic RNG is retained for
         * deterministic edge delay/weight calculation.
         */
        this.random = createSeededRandom(
            `${blueprint.metadata.seed}_edges`
        );

        this.nodeMap = new Map(
            this.nodes.map(
                node => [node.id, node]
            )
        );
    }

    generate() {

        /*
         * ============================================================
         * ONLY THE REAL PROPAGATION TREE
         * ============================================================
         *
         * Every propagation event already contains parentId.
         *
         * Therefore:
         *
         *     parent -> child
         *
         * is the ONLY visual connection we create.
         *
         * NO cross edges.
         * NO community edges.
         * NO bridge edges.
         * NO random secondary connections.
         *
         * This guarantees a clean propagation tree.
         */
        this.buildTreeEdges();

        return this.edges;
    }

    buildTreeEdges() {

        this.nodes.forEach(node => {

            const parentId =
                node.data?.parentId ??
                node.parentId ??
                null;

            /*
             * Root/source has no parent.
             */
            if (!parentId) {
                return;
            }

            const parent =
                this.nodeMap.get(
                    parentId
                );

            /*
             * Ignore invalid parent references.
             */
            if (!parent) {
                return;
            }

            this.createEdge(
                parent,
                node
            );
        });
    }

    createEdge(
        source,
        target
    ) {

        if (!source || !target) {
            return;
        }

        if (source.id === target.id) {
            return;
        }

        const key =
            `${source.id}->${target.id}`;

        /*
         * Never create duplicate connections.
         */
        if (this.edgeSet.has(key)) {
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

        /*
         * ============================================================
         * ALL EDGES ARE IDENTICAL VISUALLY
         * ============================================================
         */

        this.edges.push({

            id:
                `edge-${source.id}-${target.id}`,

            source:
                source.id,

            target:
                target.id,

            /*
             * Straight line.
             */
            type:
                "straight",

            /*
             * No animation.
             */
            animated:
                false,

            data: {

                /*
                 * Keep tree as the interaction type.
                 */
                interaction:
                    "tree",

                weight,

                delay,

                color:
                    "#ffffff"
            },

            style: {

                stroke:
                    "#ffffff",

                strokeWidth:
                    2,

                opacity:
                    0.9
            }
        });
    }

    calculateWeight(
        source,
        target
    ) {

        const sourceProbability =
            Number(
                source.data?.shareProbability || 0
            );

        const targetProbability =
            Number(
                target.data?.shareProbability || 0
            );

        const probability =
            (
                sourceProbability +
                targetProbability
            ) / 2;

        const sourceInfluence =
            Number(
                source.data?.influenceScore || 0
            );

        const targetInfluence =
            Number(
                target.data?.influenceScore || 0
            );

        const influence =
            (
                sourceInfluence +
                targetInfluence
            ) / 2;

        const followers =
            Math.min(
                Number(
                    source.data?.followers || 0
                ),
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

    calculateDelay(
        source
    ) {

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
                    Number(
                        source.data?.level || 0
                    ) * 10
                ) /
                Math.max(
                    Number(
                        source.data?.shareProbability || 0
                    ),
                    0.1
                )
            )
        );
    }

    getEdges() {
        return this.edges;
    }
}
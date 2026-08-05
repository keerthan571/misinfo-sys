import ELK from "elkjs/lib/elk.bundled.js";

const elk = new ELK();

export default class ELKLayoutEngine {

    static async layout(nodes, edges) {

        const graph = {
            id: "root",

            layoutOptions: {

                "elk.algorithm": "layered",

                "elk.direction": "DOWN",

                "elk.spacing.nodeNode": "110",

                "elk.layered.spacing.nodeNodeBetweenLayers": "190",

                "elk.edgeRouting": "ORTHOGONAL",

                "elk.layered.nodePlacement.strategy":
                    "NETWORK_SIMPLEX",

                "elk.layered.crossingMinimization.strategy":
                    "LAYER_SWEEP",

                "elk.padding":
                    "[top=60,left=60,bottom=60,right=60]"
            },

            children: nodes.map(node => ({
                id: node.id,
                width: 220,
                height: 110
            })),

            edges: edges
                .filter(edge =>
                    edge.data.interaction === "tree"
                )
                .map(edge => ({
                    id: edge.id,
                    sources: [edge.source],
                    targets: [edge.target]
                }))
        };

        const layout =
            await elk.layout(graph);

        const positions =
            new Map();

        layout.children.forEach(node => {

            positions.set(node.id, {
                x: node.x,
                y: node.y
            });

        });

        return nodes.map(node => ({
            ...node,
            position:
                positions.get(node.id) ?? {
                    x: 0,
                    y: 0
                }
        }));
    }
}
export default class ELKLayoutEngine {
    static async layout(nodes, edges) {
        if (!nodes || nodes.length === 0) {
            return [];
        }

        const nodeMap = new Map(
            nodes.map(node => [node.id, node])
        );

        const hierarchyInteractions = new Set([
            "publish",
            "share",
            "bot"
        ]);

        const treeEdges = edges.filter(edge => {
            const interaction =
                edge?.data?.interaction ||
                edge?.interaction;

            return hierarchyInteractions.has(
                interaction
            );
        });

        const childrenMap = new Map();

        nodes.forEach(node => {
            childrenMap.set(node.id, []);
        });

        treeEdges.forEach(edge => {
            if (
                nodeMap.has(edge.source) &&
                nodeMap.has(edge.target) &&
                edge.source !== edge.target
            ) {
                childrenMap
                    .get(edge.source)
                    .push(edge.target);
            }
        });

        const childIds = new Set();

        treeEdges.forEach(edge => {
            if (
                nodeMap.has(edge.source) &&
                nodeMap.has(edge.target)
            ) {
                childIds.add(edge.target);
            }
        });

        const roots = nodes.filter(
            node => !childIds.has(node.id)
        );

        const NODE_WIDTH = 220;
        const NODE_HEIGHT = 130;

        const HORIZONTAL_GAP = 100;
        const VERTICAL_GAP = 150;
        const ROOT_GAP = 250;

        const positions = new Map();

        const subtreeWidths = new Map();

        const calculateWidth = nodeId => {
            const children =
                childrenMap.get(nodeId) || [];

            if (children.length === 0) {
                subtreeWidths.set(
                    nodeId,
                    NODE_WIDTH
                );

                return NODE_WIDTH;
            }

            let width = 0;

            children.forEach(
                (childId, index) => {
                    width += calculateWidth(
                        childId
                    );

                    if (
                        index <
                        children.length - 1
                    ) {
                        width +=
                            HORIZONTAL_GAP;
                    }
                }
            );

            width = Math.max(
                NODE_WIDTH,
                width
            );

            subtreeWidths.set(
                nodeId,
                width
            );

            return width;
        };

        roots.forEach(root => {
            calculateWidth(root.id);
        });

        const placeNode = (
            nodeId,
            depth,
            left
        ) => {
            const children =
                childrenMap.get(nodeId) || [];

            const subtreeWidth =
                subtreeWidths.get(
                    nodeId
                ) || NODE_WIDTH;

            const nodeX =
                left +
                (
                    subtreeWidth -
                    NODE_WIDTH
                ) / 2;

            positions.set(
                nodeId,
                {
                    x: nodeX,
                    y:
                        depth *
                        (
                            NODE_HEIGHT +
                            VERTICAL_GAP
                        )
                }
            );

            let childLeft = left;

            children.forEach(childId => {
                const childWidth =
                    subtreeWidths.get(
                        childId
                    ) || NODE_WIDTH;

                placeNode(
                    childId,
                    depth + 1,
                    childLeft
                );

                childLeft +=
                    childWidth +
                    HORIZONTAL_GAP;
            });
        };

        let currentX = 0;

        roots.forEach(root => {
            const rootWidth =
                subtreeWidths.get(
                    root.id
                ) || NODE_WIDTH;

            placeNode(
                root.id,
                0,
                currentX
            );

            currentX +=
                rootWidth +
                ROOT_GAP;
        });

        nodes.forEach(
            (node, index) => {
                if (!positions.has(node.id)) {
                    positions.set(
                        node.id,
                        {
                            x:
                                index *
                                (
                                    NODE_WIDTH +
                                    HORIZONTAL_GAP
                                ),

                            y: 0
                        }
                    );
                }
            }
        );

        return nodes.map(node => {
            const position =
                positions.get(
                    node.id
                );

            return {
                ...node,

                position: {
                    x:
                        position.x + 100,

                    y:
                        position.y + 80
                }
            };
        });
    }
}
export default class ELKLayoutEngine {

    static async layout(nodes, edges) {

        if (!nodes || nodes.length === 0) {
            return [];
        }

        const nodeMap = new Map(
            nodes.map(node => [node.id, node])
        );

        /*
         * =====================================================
         * USE ONLY PROPAGATION TREE EDGES
         * =====================================================
         */

        const treeEdges = edges.filter(edge => {

            const interaction =
                edge?.data?.interaction ??
                edge?.interaction ??
                edge?.edgeType;

            return interaction === "tree";
        });

        /*
         * =====================================================
         * BUILD PARENT -> CHILDREN
         * =====================================================
         */

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

                const children =
                    childrenMap.get(edge.source);

                if (!children.includes(edge.target)) {
                    children.push(edge.target);
                }
            }
        });

        /*
         * =====================================================
         * FIND ROOT
         * =====================================================
         */

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

        /*
         * =====================================================
         * LAYOUT SETTINGS
         * =====================================================
         */

        const NODE_WIDTH = 250;
        const NODE_HEIGHT = 130;

        /*
         * Horizontal distance between cards.
         */
        const HORIZONTAL_GAP = 35;

        /*
         * Vertical distance between generations.
         */
        const VERTICAL_GAP = 75;

        /*
         * =====================================================
         * CALCULATE DEPTH
         * =====================================================
         */

        const depthMap = new Map();

        const assignDepth = (nodeId, depth) => {

            /*
             * If already assigned, keep the shallowest level.
             */
            if (depthMap.has(nodeId)) {

                if (
                    depth >=
                    depthMap.get(nodeId)
                ) {
                    return;
                }
            }

            depthMap.set(
                nodeId,
                depth
            );

            const children =
                childrenMap.get(nodeId) || [];

            children.forEach(childId => {

                assignDepth(
                    childId,
                    depth + 1
                );

            });
        };

        roots.forEach(root => {

            assignDepth(
                root.id,
                0
            );

        });

        /*
         * Safety fallback.
         */
        nodes.forEach(node => {

            if (!depthMap.has(node.id)) {

                depthMap.set(
                    node.id,
                    0
                );

            }

        });

        /*
         * =====================================================
         * GROUP NODES BY LEVEL
         * =====================================================
         */

        const levels = new Map();

        nodes.forEach(node => {

            const depth =
                depthMap.get(node.id) ?? 0;

            if (!levels.has(depth)) {
                levels.set(
                    depth,
                    []
                );
            }

            levels
                .get(depth)
                .push(node);

        });

        /*
         * =====================================================
         * ORDER EACH LEVEL
         * =====================================================
         *
         * Keep children close to their parent.
         *
         * We order each level according to the position
         * of its parent in the previous level.
         */

        const nodeOrder = new Map();

        /*
         * Root order.
         */
        roots.forEach(
            (root, index) => {
                nodeOrder.set(
                    root.id,
                    index
                );
            }
        );

        /*
         * Process levels from top to bottom.
         */
        const maxDepth =
            Math.max(
                ...Array.from(
                    levels.keys()
                )
            );

        for (
            let depth = 1;
            depth <= maxDepth;
            depth++
        ) {

            const levelNodes =
                levels.get(depth) || [];

            levelNodes.sort(
                (a, b) => {

                    const parentA =
                        treeEdges.find(
                            edge =>
                                edge.target ===
                                a.id
                        )?.source;

                    const parentB =
                        treeEdges.find(
                            edge =>
                                edge.target ===
                                b.id
                        )?.source;

                    const orderA =
                        nodeOrder.get(
                            parentA
                        ) ?? 999999;

                    const orderB =
                        nodeOrder.get(
                            parentB
                        ) ?? 999999;

                    if (
                        orderA !==
                        orderB
                    ) {
                        return (
                            orderA -
                            orderB
                        );
                    }

                    return (
                        a.id.localeCompare(
                            b.id
                        )
                    );
                }
            );

            levelNodes.forEach(
                (node, index) => {

                    nodeOrder.set(
                        node.id,
                        index
                    );

                }
            );

        }

        /*
         * =====================================================
         * PLACE NODES
         * =====================================================
         *
         * EVERY DEPTH GETS ITS OWN HORIZONTAL ROW.
         *
         * This is the important part.
         */

        const positions = new Map();

        levels.forEach(
            (levelNodes, depth) => {

                const count =
                    levelNodes.length;

                const totalWidth =
                    count *
                    NODE_WIDTH +
                    Math.max(
                        0,
                        count - 1
                    ) *
                    HORIZONTAL_GAP;

                /*
                 * Center the complete row.
                 */
                const startX =
                    -totalWidth / 2;

                levelNodes.forEach(
                    (node, index) => {

                        positions.set(
                            node.id,
                            {
                                x:
                                    startX +
                                    index *
                                    (
                                        NODE_WIDTH +
                                        HORIZONTAL_GAP
                                    ),

                                y:
                                    depth *
                                    (
                                        NODE_HEIGHT +
                                        VERTICAL_GAP
                                    )
                            }
                        );

                    }
                );

            }
        );

        /*
         * =====================================================
         * FINAL SAFETY
         * =====================================================
         */

        nodes.forEach(
            (node, index) => {

                if (
                    !positions.has(
                        node.id
                    )
                ) {

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

        /*
         * =====================================================
         * RETURN REACT FLOW NODES
         * =====================================================
         */

        return nodes.map(node => {

            const position =
                positions.get(
                    node.id
                );

            return {

                ...node,

                position: {
                    x:
                        position.x +
                        500,

                    y:
                        position.y +
                        80
                }

            };

        });

    }

}
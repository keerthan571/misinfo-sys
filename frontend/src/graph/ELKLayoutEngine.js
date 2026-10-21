
export default class ELKLayoutEngine {
    static async layout(nodes, edges) {
        if (!nodes || nodes.length === 0) {
            return [];
        }

        const safeEdges = Array.isArray(edges) ? edges : [];

        const nodeMap = new Map(
            nodes.map((node) => [node.id, node])
        );

        // Use only valid propagation-tree edges.
        const treeEdges = safeEdges.filter((edge) => {
            const interaction =
                edge?.data?.interaction ??
                edge?.interaction ??
                edge?.edgeType;

            return (
                interaction === "tree" &&
                nodeMap.has(edge.source) &&
                nodeMap.has(edge.target) &&
                edge.source !== edge.target
            );
        });

        // Build parent-child relationships.
        const childrenMap = new Map(
            nodes.map((node) => [node.id, []])
        );

        const parentMap = new Map();

        treeEdges.forEach((edge) => {
            const children = childrenMap.get(edge.source);

            if (children && !children.includes(edge.target)) {
                children.push(edge.target);
            }

            if (!parentMap.has(edge.target)) {
                parentMap.set(edge.target, edge.source);
            }
        });

        // Find root nodes.
        const childIds = new Set(parentMap.keys());

        let roots = nodes.filter(
            (node) => !childIds.has(node.id)
        );

        // Handle graphs that contain only cycles.
        if (roots.length === 0) {
            roots = [nodes[0]];
        }

        // Match the actual GraphNode.css card dimensions.
        const NODE_WIDTH = 290;
        const NODE_HEIGHT = 140;

        // Increased spacing to prevent adjacent cards from touching.
        const HORIZONTAL_GAP = 100;
        const VERTICAL_GAP = 110;
        const OUTER_PADDING = 100;

        // Calculate the depth of every node.
        const depthMap = new Map();

        const assignDepth = (nodeId, depth, path = new Set()) => {
            // Prevent cycles from causing infinite recursion.
            if (path.has(nodeId)) {
                return;
            }

            const previousDepth = depthMap.get(nodeId);

            // Keep the shallowest discovered depth.
            if (
                previousDepth !== undefined &&
                previousDepth <= depth
            ) {
                return;
            }

            depthMap.set(nodeId, depth);

            const nextPath = new Set(path);
            nextPath.add(nodeId);

            const children = childrenMap.get(nodeId) || [];

            children.forEach((childId) => {
                assignDepth(childId, depth + 1, nextPath);
            });
        };

        roots.forEach((root) => {
            assignDepth(root.id, 0);
        });

        // Give any remaining disconnected nodes a safe depth.
        nodes.forEach((node) => {
            if (!depthMap.has(node.id)) {
                depthMap.set(node.id, 0);
            }
        });

        // Group nodes by generation.
        const levels = new Map();

        nodes.forEach((node) => {
            const depth = depthMap.get(node.id) ?? 0;

            if (!levels.has(depth)) {
                levels.set(depth, []);
            }

            levels.get(depth).push(node);
        });

        // Preserve input order as a stable fallback.
        const originalOrder = new Map(
            nodes.map((node, index) => [node.id, index])
        );

        const nodeOrder = new Map();

        roots.forEach((root, index) => {
            nodeOrder.set(root.id, index);
        });

        const maxDepth = Math.max(
            0,
            ...Array.from(levels.keys())
        );

        // Order each level by its parent's position.
        for (let depth = 1; depth <= maxDepth; depth++) {
            const levelNodes = levels.get(depth) || [];

            levelNodes.sort((a, b) => {
                const parentA = parentMap.get(a.id);
                const parentB = parentMap.get(b.id);

                const orderA =
                    nodeOrder.get(parentA) ??
                    originalOrder.get(a.id) ??
                    0;

                const orderB =
                    nodeOrder.get(parentB) ??
                    originalOrder.get(b.id) ??
                    0;

                if (orderA !== orderB) {
                    return orderA - orderB;
                }

                return (
                    (originalOrder.get(a.id) ?? 0) -
                    (originalOrder.get(b.id) ?? 0)
                );
            });

            levelNodes.forEach((node, index) => {
                nodeOrder.set(node.id, index);
            });
        }

        // Position nodes in evenly spaced horizontal rows.
        const positions = new Map();

        const maxLevelWidth = Math.max(
            NODE_WIDTH,
            ...Array.from(levels.values()).map((levelNodes) => {
                return (
                    levelNodes.length * NODE_WIDTH +
                    Math.max(0, levelNodes.length - 1) *
                        HORIZONTAL_GAP
                );
            })
        );

        levels.forEach((levelNodes, depth) => {
            const count = levelNodes.length;

            const rowWidth =
                count * NODE_WIDTH +
                Math.max(0, count - 1) * HORIZONTAL_GAP;

            // Center each generation against the widest generation.
            const startX = (maxLevelWidth - rowWidth) / 2;

            levelNodes.forEach((node, index) => {
                positions.set(node.id, {
                    x:
                        OUTER_PADDING +
                        startX +
                        index * (NODE_WIDTH + HORIZONTAL_GAP),

                    y:
                        OUTER_PADDING +
                        depth * (NODE_HEIGHT + VERTICAL_GAP),
                });
            });
        });

        // Final fallback for any missing position.
        nodes.forEach((node, index) => {
            if (!positions.has(node.id)) {
                positions.set(node.id, {
                    x:
                        OUTER_PADDING +
                        index * (NODE_WIDTH + HORIZONTAL_GAP),

                    y: OUTER_PADDING,
                });
            }
        });

        // Return nodes in React Flow format.
        return nodes.map((node) => ({
            ...node,
            position: positions.get(node.id),
        }));
    }
}

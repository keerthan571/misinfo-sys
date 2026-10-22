
const NODE_WIDTH = 190;
const DEFAULT_NODE_HEIGHT = 104;
const HORIZONTAL_GAP = 72;
const VERTICAL_GAP = 30;
const SIDE_PADDING = 36;
const TOP_PADDING = 36;
const ROOT_GAP = 56;
const DEBUG = false;

const EDGE_COLORS = {
    source: "#22c55e",
    influencer: "#f59e0b",
    user: "#3b82f6",
};

const normalizeType = (value) =>
    String(value ?? "")
        .trim()
        .toLowerCase()
        .replace(/[\s-]+/g, "_");

const getType = (node) =>
    normalizeType(
        node?.data?.nodeType ??
        node?.data?.node_type ??
        node?.data?.role ??
        node?.data?.node_role ??
        node?.data?.type ??
        node?.nodeType ??
        node?.type ??
        "user"
    );

const isSource = (node) =>
    ["source", "claim", "origin"].includes(getType(node));

const isInfluencer = (node) =>
    ["influencer", "micro_influencer", "community_leader"].includes(
        getType(node)
    );

export default class ELKLayoutEngine {
    static async layout(nodes, edges) {
        if (!Array.isArray(nodes) || nodes.length === 0) return [];

        const validNodes = nodes.filter(
            (node) => node && node.id != null
        );

        if (!validNodes.length) return [];

        const nodeMap = new Map(
            validNodes.map((node) => [String(node.id), node])
        );

        const order = new Map(
            validNodes.map((node, index) => [
                String(node.id),
                index,
            ])
        );

        const getNodeHeight = (id) => {
            const node = nodeMap.get(String(id));

            const height =
                node?.measured?.height ??
                node?.height ??
                node?.style?.height;

            const numericHeight = Number(height);

            return Number.isFinite(numericHeight) && numericHeight > 0
                ? numericHeight
                : DEFAULT_NODE_HEIGHT;
        };

        const byOrder = (a, b) =>
            order.get(a) - order.get(b);

        // 1. Build directed adjacency from edges and parentId.
        const outgoing = new Map(
            validNodes.map((node) => [String(node.id), []])
        );

        const hasIncoming = new Set();

        const addLink = (fromId, toId) => {
            const from = String(fromId ?? "");
            const to = String(toId ?? "");

            if (
                !nodeMap.has(from) ||
                !nodeMap.has(to) ||
                from === to
            ) {
                return;
            }

            if (!outgoing.get(from).includes(to)) {
                outgoing.get(from).push(to);
            }

            hasIncoming.add(to);
        };

        for (const edge of Array.isArray(edges) ? edges : []) {
            addLink(edge?.source, edge?.target);
        }

        for (const node of validNodes) {
            const parentId =
                node.data?.parentId ??
                node.parentId ??
                node.data?.parent_id ??
                node.parent_id ??
                null;

            if (parentId != null) {
                addLink(parentId, node.id);
            }
        }

        // 2. Find the source and build a cycle-safe forest.
        const primaryRoot = String(
            validNodes.find(isSource)?.id ??
            validNodes.find(
                (node) => !hasIncoming.has(String(node.id))
            )?.id ??
            validNodes[0].id
        );

        const layoutChildren = new Map(
            validNodes.map((node) => [String(node.id), []])
        );

        const parentMap = new Map();
        const visited = new Set();
        const bfsOrder = [];
        const componentRoots = [];

        const sortChildren = (parentId, ids) =>
            ids.sort((a, b) => {
                if (isSource(nodeMap.get(parentId))) {
                    const aRank = isInfluencer(nodeMap.get(a)) ? 0 : 1;
                    const bRank = isInfluencer(nodeMap.get(b)) ? 0 : 1;

                    if (aRank !== bRank) {
                        return aRank - bRank;
                    }
                }

                return byOrder(a, b);
            });

        const buildComponent = (rootId) => {
            if (visited.has(rootId)) return;

            componentRoots.push(rootId);
            visited.add(rootId);

            const queue = [rootId];

            for (let head = 0; head < queue.length; head++) {
                const id = queue[head];
                bfsOrder.push(id);

                const kids = [];

                for (const childId of outgoing.get(id) || []) {
                    if (visited.has(childId)) continue;

                    visited.add(childId);
                    parentMap.set(childId, id);
                    kids.push(childId);
                }

                sortChildren(id, kids);
                layoutChildren.set(id, kids);
                queue.push(...kids);
            }
        };

        buildComponent(primaryRoot);

        const rest = validNodes
            .map((node) => String(node.id))
            .sort(byOrder);

        for (const id of rest) {
            if (!hasIncoming.has(id)) {
                buildComponent(id);
            }
        }

        for (const id of rest) {
            buildComponent(id);
        }

        // 3. Calculate subtree spans from leaves to root.
        const spanOf = new Map();

        const groupSpan = (ids) =>
            ids.reduce(
                (total, id) =>
                    total + (spanOf.get(id) ?? getNodeHeight(id)),
                0
            ) + Math.max(0, ids.length - 1) * VERTICAL_GAP;

        for (let i = bfsOrder.length - 1; i >= 0; i--) {
            const id = bfsOrder[i];
            const kids = layoutChildren.get(id) || [];

            spanOf.set(
                id,
                Math.max(getNodeHeight(id), groupSpan(kids))
            );
        }

        // 4. Position each subtree in left-to-right columns.
        const positions = new Map();
        const placed = new Set();

        const xForDepth = (depth) =>
            SIDE_PADDING + depth * (NODE_WIDTH + HORIZONTAL_GAP);

        const placeSubtree = (rootId, rootCenterY, rootDepth) => {
            const queue = [{
                id: rootId,
                centerY: rootCenterY,
                depth: rootDepth,
            }];

            for (let head = 0; head < queue.length; head++) {
                const { id, centerY, depth } = queue[head];

                if (placed.has(id)) continue;
                placed.add(id);

                positions.set(id, {
                    x: xForDepth(depth),
                    y: centerY - getNodeHeight(id) / 2,
                });

                const kids = layoutChildren.get(id) || [];
                if (kids.length === 0) continue;

                const totalSpan = groupSpan(kids);
                let cursor = centerY - totalSpan / 2;

                for (const childId of kids) {
                    const childSpan =
                        spanOf.get(childId) ?? getNodeHeight(childId);

                    queue.push({
                        id: childId,
                        centerY: cursor + childSpan / 2,
                        depth: depth + 1,
                    });

                    cursor += childSpan + VERTICAL_GAP;
                }
            }
        };

        // 5. Position the source and its first propagation tier.
        const primaryChildren =
            layoutChildren.get(primaryRoot) || [];

        const typedInfluencers = primaryChildren.filter((id) =>
            isInfluencer(nodeMap.get(id))
        );

        // If roles are absent, use all direct source children.
        const firstTier =
            typedInfluencers.length > 0
                ? typedInfluencers
                : primaryChildren;

        const otherChildren = primaryChildren.filter(
            (id) => !firstTier.includes(id)
        );

        if (firstTier.length > 0) {
            const spans = firstTier.map(
                (id) => spanOf.get(id) ?? getNodeHeight(id)
            );

            // Calculate symmetrical center offsets for first-tier nodes.
            const offsets = [];
            let cursor = 0;

            for (let i = 0; i < spans.length; i++) {
                if (i > 0) {
                    cursor +=
                        spans[i - 1] / 2 +
                        VERTICAL_GAP +
                        spans[i] / 2;
                }

                offsets.push(cursor);
            }

            const midpoint =
                (offsets[0] + offsets[offsets.length - 1]) / 2;

            for (let i = 0; i < offsets.length; i++) {
                offsets[i] -= midpoint;
            }

            const maxHalfSpan = Math.max(
                getNodeHeight(primaryRoot) / 2,
                ...offsets.map(
                    (offset, i) => Math.abs(offset) + spans[i] / 2
                )
            );

            const sourceCenterY = TOP_PADDING + maxHalfSpan;

            positions.set(primaryRoot, {
                x: xForDepth(0),
                y: sourceCenterY - getNodeHeight(primaryRoot) / 2,
            });

            placed.add(primaryRoot);

            for (let i = 0; i < firstTier.length; i++) {
                placeSubtree(
                    firstTier[i],
                    sourceCenterY + offsets[i],
                    1
                );
            }

            let nextTop =
                sourceCenterY + maxHalfSpan + VERTICAL_GAP;

            for (const id of otherChildren) {
                const span = spanOf.get(id) ?? getNodeHeight(id);

                placeSubtree(id, nextTop + span / 2, 1);
                nextTop += span + VERTICAL_GAP;
            }
        } else {
            const rootSpan =
                spanOf.get(primaryRoot) ?? getNodeHeight(primaryRoot);

            placeSubtree(
                primaryRoot,
                TOP_PADDING + rootSpan / 2,
                0
            );
        }

        // 6. Position disconnected components below the main tree.
        let nextTop =
            Math.max(
                TOP_PADDING,
                ...Array.from(positions.entries()).map(
                    ([id, position]) =>
                        position.y + getNodeHeight(id)
                )
            ) + ROOT_GAP;

        for (const rootId of componentRoots) {
            if (placed.has(rootId)) continue;

            const rootSpan =
                spanOf.get(rootId) ?? getNodeHeight(rootId);

            placeSubtree(rootId, nextTop + rootSpan / 2, 0);
            nextTop += rootSpan + ROOT_GAP;
        }

        // 7. Preserve node data and set horizontal edge handles.
        const result = validNodes.map((node, index) => {
            const position = positions.get(String(node.id)) ?? {
                x: SIDE_PADDING + index * (NODE_WIDTH + HORIZONTAL_GAP),
                y: TOP_PADDING,
            };

            return {
                ...node,
                sourcePosition: "right",
                targetPosition: "left",
                position: {
                    x: Math.round(position.x),
                    y: Math.round(position.y),
                },
            };
        });

        if (DEBUG) {
            console.table(
                result.map((node) => ({
                    id: String(node.id),
                    type: getType(node),
                    parentId: parentMap.get(String(node.id)) ?? null,
                    x: node.position.x,
                    y: node.position.y,
                }))
            );
        }

        return result;
    }

    // Optional edge styling helper.
    static styleEdges(nodes, edges) {
        const nodeMap = new Map(
            (nodes || []).map((node) => [String(node.id), node])
        );

        return (edges || []).map((edge) => {
            const sourceNode = nodeMap.get(String(edge.source));

            const kind = isSource(sourceNode)
                ? "source"
                : isInfluencer(sourceNode)
                    ? "influencer"
                    : "user";

            const color = EDGE_COLORS[kind];

            return {
                ...edge,
                type: "smoothstep",
                style: {
                    ...(edge.style || {}),
                    stroke: color,
                    strokeWidth: 2,
                },
                markerEnd: {
                    type: "arrowclosed",
                    color,
                },
            };
        });
    }
}

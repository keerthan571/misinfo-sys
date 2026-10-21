/*
 * ELKLayoutEngine.js
 *
 * Left-to-right propagation tree layout.
 *
 * Target look:
 *   Source  ->  Influencer  ->  users (above/below)  ->  users (above/below)
 *
 * Rules:
 * 1. One direct influencer: source and influencer share a centerline.
 * 2. Multiple direct influencers: balanced above/below the source.
 * 3. Descendants branch to the right and are centered on their parent.
 * 4. Subtree height is used for spacing, never as a node's own height.
 * 5. Existing nodes and their data are preserved.
 *
 * IMPORTANT CHANGE vs. the old version:
 * The hierarchy is now built from ANY directed edge (source -> target) by
 * walking outward from the primary source (BFS). The old version only
 * accepted edges whose interaction was "tree", so influencer -> user edges
 * with other interaction names were ignored and those nodes were dumped
 * in a stack at the bottom instead of branching to the right.
 */

const NODE_WIDTH = 290;
const NODE_HEIGHT = 190;

const HORIZONTAL_GAP = 100;
const VERTICAL_GAP = 55;
const SIDE_PADDING = 50;
const TOP_PADDING = 50;
const ROOT_GAP = 100;

const DEBUG = false;

const EDGE_COLORS = {
  source: "#22c55e", // green  : source -> influencer
  influencer: "#f59e0b", // amber  : influencer -> users
  user: "#3b82f6", // blue   : user -> user
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

    const validNodes = nodes.filter((node) => node && node.id != null);
    if (!validNodes.length) return [];

    const nodeMap = new Map(validNodes.map((n) => [String(n.id), n]));
    const order = new Map(validNodes.map((n, i) => [String(n.id), i]));
    const byOrder = (a, b) => order.get(a) - order.get(b);

    // ---------------------------------------------------------
    // 1. Directed adjacency from every edge (+ parentId fallback).
    // ---------------------------------------------------------

    const outgoing = new Map(validNodes.map((n) => [String(n.id), []]));
    const hasIncoming = new Set();

    const addLink = (fromId, toId) => {
      const from = String(fromId ?? "");
      const to = String(toId ?? "");
      if (!nodeMap.has(from) || !nodeMap.has(to) || from === to) return;
      if (!outgoing.get(from).includes(to)) outgoing.get(from).push(to);
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
      if (parentId != null) addLink(parentId, node.id);
    }

    // ---------------------------------------------------------
    // 2. Cycle-safe BFS forest. Parent = first (shallowest) discoverer.
    //    Under the source, direct influencers are ordered first.
    // ---------------------------------------------------------

    const primaryRoot = String(
      validNodes.find(isSource)?.id ??
        validNodes.find((n) => !hasIncoming.has(String(n.id)))?.id ??
        validNodes[0].id
    );

    const layoutChildren = new Map(validNodes.map((n) => [String(n.id), []]));
    const parentMap = new Map();
    const visited = new Set();
    const bfsOrder = []; // parents always appear before their children
    const componentRoots = [];

    const sortChildren = (parentId, ids) =>
      ids.sort((a, b) => {
        if (isSource(nodeMap.get(parentId))) {
          const ar = isInfluencer(nodeMap.get(a)) ? 0 : 1;
          const br = isInfluencer(nodeMap.get(b)) ? 0 : 1;
          if (ar !== br) return ar - br;
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

    // Other components: true roots first, then anything left (cycles).
    const rest = validNodes.map((n) => String(n.id)).sort(byOrder);
    for (const id of rest) {
      if (!hasIncoming.has(id)) buildComponent(id);
    }
    for (const id of rest) buildComponent(id);

    // ---------------------------------------------------------
    // 3. Vertical span of each subtree (children before parents).
    //    This is a layout span, NOT the card's height.
    // ---------------------------------------------------------

    const spanOf = new Map();
    const groupSpan = (ids) =>
      ids.reduce((t, id) => t + (spanOf.get(id) ?? NODE_HEIGHT), 0) +
      Math.max(0, ids.length - 1) * VERTICAL_GAP;

    for (let i = bfsOrder.length - 1; i >= 0; i--) {
      const id = bfsOrder[i];
      const kids = layoutChildren.get(id) || [];
      spanOf.set(id, Math.max(NODE_HEIGHT, groupSpan(kids)));
    }

    // ---------------------------------------------------------
    // 4. Positioning. Children are stacked as a group that is
    //    centered on the parent's centerline.
    // ---------------------------------------------------------

    const positions = new Map();
    const placed = new Set();

    const xForDepth = (depth) =>
      SIDE_PADDING + depth * (NODE_WIDTH + HORIZONTAL_GAP);

    const placeSubtree = (rootId, rootCenterY, rootDepth) => {
      const queue = [{ id: rootId, centerY: rootCenterY, depth: rootDepth }];

      for (let head = 0; head < queue.length; head++) {
        const { id, centerY, depth } = queue[head];
        if (placed.has(id)) continue;
        placed.add(id);

        positions.set(id, {
          x: xForDepth(depth),
          y: centerY - NODE_HEIGHT / 2,
        });

        const kids = layoutChildren.get(id) || [];
        let cursor = centerY - groupSpan(kids) / 2;

        for (const childId of kids) {
          const span = spanOf.get(childId) ?? NODE_HEIGHT;
          queue.push({
            id: childId,
            centerY: cursor + span / 2,
            depth: depth + 1,
          });
          cursor += span + VERTICAL_GAP;
        }
      }
    };

    // ---------------------------------------------------------
    // 5. Primary source: direct influencers balanced around it.
    // ---------------------------------------------------------

    const primaryChildren = layoutChildren.get(primaryRoot) || [];
    const directInfluencers = primaryChildren.filter((id) =>
      isInfluencer(nodeMap.get(id))
    );
    const otherChildren = primaryChildren.filter(
      (id) => !directInfluencers.includes(id)
    );

    if (directInfluencers.length > 0) {
      const infSpan = groupSpan(directInfluencers);
      const sourceCenterY = TOP_PADDING + infSpan / 2;

      positions.set(primaryRoot, {
        x: xForDepth(0),
        y: sourceCenterY - NODE_HEIGHT / 2,
      });
      placed.add(primaryRoot);

      // 1 influencer -> same centerline as source (and its children
      // are centered on that same line). N influencers -> balanced.
      let cursor = sourceCenterY - infSpan / 2;
      for (const id of directInfluencers) {
        const span = spanOf.get(id) ?? NODE_HEIGHT;
        placeSubtree(id, cursor + span / 2, 1);
        cursor += span + VERTICAL_GAP;
      }

      // Any non-influencer children of the source go below.
      cursor = sourceCenterY + infSpan / 2 + VERTICAL_GAP;
      for (const id of otherChildren) {
        const span = spanOf.get(id) ?? NODE_HEIGHT;
        placeSubtree(id, cursor + span / 2, 1);
        cursor += span + VERTICAL_GAP;
      }
    } else {
      const rootSpan = spanOf.get(primaryRoot) ?? NODE_HEIGHT;
      placeSubtree(primaryRoot, TOP_PADDING + rootSpan / 2, 0);
    }

    // ---------------------------------------------------------
    // 6. Disconnected components go underneath.
    // ---------------------------------------------------------

    let nextTop =
      Math.max(
        TOP_PADDING,
        ...Array.from(positions.values()).map((p) => p.y + NODE_HEIGHT)
      ) + ROOT_GAP;

    for (const rootId of componentRoots) {
      if (placed.has(rootId)) continue;
      const span = spanOf.get(rootId) ?? NODE_HEIGHT;
      placeSubtree(rootId, nextTop + span / 2, 0);
      nextTop += span + ROOT_GAP;
    }

    // ---------------------------------------------------------
    // 7. Return nodes with positions; preserve original data.
    //    Handles are set so edges leave from the right side and
    //    enter on the left side (left-to-right flow).
    // ---------------------------------------------------------

    const result = validNodes.map((node, index) => {
      const p = positions.get(String(node.id)) ?? {
        x: SIDE_PADDING + index * (NODE_WIDTH + HORIZONTAL_GAP),
        y: TOP_PADDING,
      };

      return {
        ...node,
        sourcePosition: "right",
        targetPosition: "left",
        position: { x: Math.round(p.x), y: Math.round(p.y) },
      };
    });

    if (DEBUG) {
      console.table(
        result.map((n) => ({
          id: String(n.id),
          type: getType(n),
          parentId: parentMap.get(String(n.id)) ?? null,
          x: n.position.x,
          y: n.position.y,
        }))
      );
    }

    return result;
  }

  /*
   * Optional helper: gives edges the elbow look and colors from the
   * reference image (green from source, amber from influencer, blue
   * between users). Call after layout:
   *
   *   const laidOut = await ELKLayoutEngine.layout(nodes, edges);
   *   const styled  = ELKLayoutEngine.styleEdges(laidOut, edges);
   */
  static styleEdges(nodes, edges) {
    const nodeMap = new Map((nodes || []).map((n) => [String(n.id), n]));

    return (edges || []).map((edge) => {
      const src = nodeMap.get(String(edge.source));
      const kind = isSource(src)
        ? "source"
        : isInfluencer(src)
        ? "influencer"
        : "user";
      const color = EDGE_COLORS[kind];

      return {
        ...edge,
        type: "smoothstep",
        style: { ...(edge.style || {}), stroke: color, strokeWidth: 2 },
        markerEnd: { type: "arrowclosed", color },
      };
    });
  }
}

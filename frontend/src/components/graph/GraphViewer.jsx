import { useEffect, useMemo, useState } from "react";
import ReactFlow, {
  Background,
  Controls,
  MiniMap,
  useNodesInitialized,
  useReactFlow,
} from "reactflow";

import "reactflow/dist/style.css";

import GraphNode from "./GraphNode";
import GraphGenerator from "../../graph/GraphGenerator";
import ELKLayoutEngine from "../../graph/ELKLayoutEngine";

function InfoCard({ title, value }) {
  return (
    <div>
      <div className="text-sm text-slate-400">
        {title}
      </div>

      <div className="text-lg font-semibold text-white mt-2 break-all">
        {value ?? "-"}
      </div>
    </div>
  );
}

function getNodeDisplayName(data = {}) {
  const candidates = [
    data.username,
    data.displayName,
    data.display_name,
    data.accountName,
    data.author,
    data.handle,
    data.sourceName,
    data.publisher,
    data.name,
  ];

  for (const value of candidates) {
    if (!value) continue;

    const text = String(value).trim();

    if (!text) continue;

    if (/^user\s*\d+$/i.test(text)) continue;
    if (/^micro influencer\s*\d+$/i.test(text)) continue;
    if (/^community leader\s*\d+$/i.test(text)) continue;
    if (/^influencer\s*\d+$/i.test(text)) continue;

    return text;
  }

  if (data.label) {
    return String(data.label);
  }

  const type = String(
    data.nodeType ||
    data.node_type ||
    data.role ||
    ""
  ).toLowerCase();

  if (
    type === "micro_influencer"
  ) {
    return "Micro Influencer";
  }

  if (
    type === "community_leader"
  ) {
    return "Community Leader";
  }

  if (
    type === "influencer"
  ) {
    return "Influencer";
  }

  if (type === "bot") {
    return "Bot Account";
  }

  if (
    type === "source" ||
    type === "claim"
  ) {
    return "Original Source";
  }

  return "User";
}


function getNodeRole(data = {}) {
  const role = String(
    data.role ||
    data.node_role ||
    ""
  ).toLowerCase();

  const type = String(
    data.nodeType ||
    data.node_type ||
    data.type ||
    ""
  ).toLowerCase();

  if (
    role === "micro_influencer" ||
    type === "micro_influencer"
  ) {
    return "Micro Influencer";
  }

  if (
    role === "community_leader" ||
    type === "community_leader"
  ) {
    return "Community Leader";
  }

  if (
    role === "influencer" ||
    type === "influencer"
  ) {
    return "Influencer";
  }

  if (
    role === "bot" ||
    type === "bot" ||
    data.isBot
  ) {
    return "Bot Account";
  }

  if (
    role === "source" ||
    role === "publisher" ||
    type === "source" ||
    type === "claim"
  ) {
    return "Original Publisher";
  }

  return "User";
}
/*
 * Automatically centers the complete graph
 * after ReactFlow has finished initializing nodes.
 */
function GraphViewportController({ nodes, pdfMode }) {
  const {
    fitView,
    getNodes
  } = useReactFlow();

  const nodesInitialized =
    useNodesInitialized();

  useEffect(() => {

    if (
      !nodes.length ||
      !nodesInitialized
    ) {
      return;
    }

    const fitGraph = () => {

      const currentNodes =
        getNodes();

      if (!currentNodes.length) {
        return;
      }

      fitView({
        nodes: currentNodes,
        padding: pdfMode
          ? 0.08
          : 0.18,
        duration: 0,
        minZoom: 0.08,
        maxZoom: 1.2,
      });
    };

    const timer1 =
      setTimeout(
        fitGraph,
        100
      );

    const timer2 =
      setTimeout(
        fitGraph,
        400
      );

    const timer3 =
      setTimeout(
        fitGraph,
        800
      );

    return () => {

      clearTimeout(timer1);
      clearTimeout(timer2);
      clearTimeout(timer3);

    };

  }, [
    nodes,
    nodesInitialized,
    fitView,
    getNodes,
    pdfMode
  ]);

  return null;
}
/*
 * Convert a saved backend graph into the same
 * ReactFlow node structure used by GraphNode.jsx.
 *
 * IMPORTANT:
 * This does NOT generate anything.
 * It only adapts already-saved graph data.
 */
function normalizeEdgeType(edge) {
  return {
    ...edge,

    type: "smoothstep",
  };
}

function normalizeSavedGraph(
  savedGraph,
  analysis
) {
  if (
    !savedGraph ||
    !Array.isArray(savedGraph.nodes) ||
    !Array.isArray(savedGraph.edges)
  ) {
    return null;
  }

  const sourceName =
    analysis?.publisher ||
    analysis?.publisher_name ||
    analysis?.source?.name ||
    analysis?.source?.username ||
    analysis?.source?.display_name ||
    analysis?.source?.displayName ||
    analysis?.source?.author ||
    analysis?.source?.handle ||
    analysis?.source?.accountName ||
    analysis?.ocr?.publisher ||
    analysis?.ocr?.publisher_name ||
    analysis?.ocr?.source_name ||
    analysis?.ocr?.author ||
    "Original Source";

  const sourceFollowers =
    analysis?.engagement?.followers ??
    null;

  const normalizedNodes =
    savedGraph.nodes.map(
      (node, index) => {

        const originalData =
          node.data || {};

        const nodeType =
          originalData.nodeType ||
          originalData.node_type ||
          node.type ||
          (
            index === 0
              ? "claim"
              : "user"
          );

        const isClaim =
          nodeType === "claim" ||
          nodeType === "source";

        const rawFollowers =
          originalData.followers ??
          node.followers ??
          (
            isClaim
              ? sourceFollowers
              : null
          );

        const followers =
          rawFollowers !== null &&
            rawFollowers !== undefined &&
            rawFollowers !== ""
            ? Number(rawFollowers)
            : null;

        const influenceScore =
          Number(
            originalData.influenceScore ??
            originalData.influence ??
            node.influence ??
            0
          );

        const networkInfluencePercent =
          Number(
            originalData.networkInfluencePercent ??
            originalData.networkInfluence ??
            0
          );

        const reach =
          Number(
            originalData.reach ??
            0
          );

        const community =
          originalData.community ??
          node.community ??
          "-";

        const verified =
          Boolean(
            originalData.verified ??
            node.verified ??
            false
          );

        const isBot =
          Boolean(
            originalData.isBot ??
            originalData.bot ??
            node.bot ??
            false
          );

        let displayName =
          originalData.username ||
          originalData.displayName ||
          originalData.display_name ||
          originalData.accountName ||
          originalData.author ||
          originalData.handle ||
          originalData.sourceName ||
          originalData.publisher ||
          node.username ||
          node.displayName ||
          node.display_name ||
          node.accountName ||
          node.author ||
          node.handle ||
          node.sourceName ||
          node.publisher ||
          null;
        /*
         * The root/claim node represents the
         * original publisher.
         *
         * Prefer the actual detected publisher.
         */
        if (isClaim) {
          displayName =
            sourceName;
        }

        const formattedFollowers =
          followers >= 1000000
            ? `${(
              followers / 1000000
            ).toFixed(1)}M`
            : followers >= 1000
              ? `${(
                followers / 1000
              ).toFixed(1)}K`
              : followers.toString();

        const roleLabel = getNodeRole({
          ...originalData,
          nodeType,
          isBot,
        });

        const resolvedDisplayName = getNodeDisplayName({
          ...originalData,

          username:
            originalData.username ||
            node.username ||
            null,

          displayName:
            originalData.displayName ||
            node.displayName ||
            null,

          sourceName:
            originalData.sourceName ||
            (isClaim ? sourceName : null),

          publisher:
            originalData.publisher ||
            (isClaim ? sourceName : null),
        });



        const actualLabel =
          resolvedDisplayName ||
          displayName ||
          originalData.label ||
          node.label ||
          roleLabel;

        return {
          ...node,

          /*
           * ReactFlow custom node.
           */
          type: "custom",

          /*
           * Preserve saved position if one exists.
           * Otherwise provide a deterministic fallback.
           */
          position:
            node.position || {
              x: 0,
              y: index * 120,
            },

          data: {
            /*
             * Start with backend-provided data.
             */
            ...originalData,

            /*
             * =====================================================
             * DISPLAY IDENTITY
             * =====================================================
             */

            label: actualLabel,

            displayName:
              originalData.displayName ??
              node.displayName ??
              displayName,

            username:
              originalData.username ??
              node.username ??
              null,

            sourceName:
              originalData.sourceName ??
              node.sourceName ??
              (isClaim ? sourceName : null),

            publisher:
              originalData.publisher ??
              node.publisher ??
              (isClaim ? sourceName : null),

            accountName:
              originalData.accountName ??
              node.accountName ??
              null,

            author:
              originalData.author ??
              node.author ??
              null,

            handle:
              originalData.handle ??
              node.handle ??
              null,

            /*
             * =====================================================
             * NODE TYPE / ROLE
             * =====================================================
             */

            nodeType:
              originalData.nodeType ??
              originalData.node_type ??
              node.nodeType ??
              node.node_type ??
              nodeType,

            role:
              originalData.role ??
              originalData.node_role ??
              node.role ??
              roleLabel,

            /*
             * =====================================================
             * FOLLOWERS
             *
             * IMPORTANT:
             * Do NOT invent followers.
             * Facebook/Twitter will remain null unless backend
             * actually supplied a value.
             * =====================================================
             */

            followers:
              originalData.followers ??
              node.followers ??
              null,

            /*
             * =====================================================
             * INFLUENCE
             * =====================================================
             */

            influenceScore:
              originalData.influenceScore ??
              originalData.influence_score ??
              originalData.influence ??
              node.influenceScore ??
              node.influence_score ??
              node.influence ??
              0,

            networkInfluence:
              originalData.networkInfluence ??
              originalData.network_influence ??
              node.networkInfluence ??
              node.network_influence ??
              originalData.networkInfluencePercent ??
              node.networkInfluencePercent ??
              originalData.influenceScore ??
              node.influenceScore ??
              0,

            networkInfluencePercent:
              originalData.networkInfluencePercent ??
              originalData.network_influence_percent ??
              node.networkInfluencePercent ??
              node.network_influence_percent ??
              originalData.networkInfluence ??
              node.networkInfluence ??
              originalData.influenceScore ??
              node.influenceScore ??
              0,

            /*
             * =====================================================
             * REACH
             * =====================================================
             */

            reach:
              originalData.reach ??
              originalData.weightedReach ??
              originalData.weighted_reach ??
              node.reach ??
              node.weightedReach ??
              node.weighted_reach ??
              null,

            weightedReach:
              originalData.weightedReach ??
              originalData.weighted_reach ??
              node.weightedReach ??
              node.weighted_reach ??
              node.reach ??
              null,

            /*
             * =====================================================
             * PAGERANK
             * =====================================================
             */

            pageRank:
              originalData.pageRank ??
              originalData.page_rank ??
              originalData.pagerank ??
              originalData.page_rank_score ??
              node.pageRank ??
              node.page_rank ??
              node.pagerank ??
              node.pageRankScore ??
              null,

            /*
             * =====================================================
             * SHARE PROBABILITY
             * =====================================================
             */

            shareProbability:
              originalData.shareProbability ??
              originalData.share_probability ??
              node.shareProbability ??
              node.share_probability ??
              null,

            /*
             * =====================================================
             * COMMUNITY
             * =====================================================
             */

            community:
              originalData.community ??
              originalData.community_id ??
              node.community ??
              node.community_id ??
              null,

            /*
             * =====================================================
             * PLATFORM
             * =====================================================
             */

            platform:
              originalData.platform ??
              node.platform ??
              null,

            /*
             * =====================================================
             * FLAGS
             * =====================================================
             */

            verified:
              originalData.verified ??
              node.verified ??
              false,

            isBot:
              originalData.isBot ??
              originalData.is_bot ??
              node.isBot ??
              node.is_bot ??
              node.bot ??
              false,

            isViral:
              originalData.isViral ??
              originalData.is_viral ??
              node.isViral ??
              node.is_viral ??
              node.viral ??
              false,

            isLeader:
              originalData.isLeader ??
              originalData.is_leader ??
              node.isLeader ??
              node.is_leader ??
              node.leader ??
              false,

            /*
             * =====================================================
             * LEVEL / PARENT
             * =====================================================
             */

            level:
              originalData.level ??
              node.level ??
              null,

            parentId:
              originalData.parentId ??
              node.parentId ??
              null,

            /*
             * =====================================================
             * FORMATTED FOLLOWERS
             * =====================================================
             */

            formattedFollowers:
              (
                originalData.followers ??
                node.followers
              ) != null
                ? (
                  Number(
                    originalData.followers ??
                    node.followers
                  ) >= 1000000
                    ? `${(
                      Number(
                        originalData.followers ??
                        node.followers
                      ) / 1000000
                    ).toFixed(1)}M`
                    : Number(
                      originalData.followers ??
                      node.followers
                    ) >= 1000
                      ? `${(
                        Number(
                          originalData.followers ??
                          node.followers
                        ) / 1000
                      ).toFixed(1)}K`
                      : String(
                        originalData.followers ??
                        node.followers
                      )
                )
                : "Not available",
          },
        };
      }
    );

  const normalizedEdges =
    savedGraph.edges.map(
      (edge, index) => ({
        ...edge,

        id:
          edge.id ||
          `saved-edge-${index}`,

        type: "smoothstep",

        data: {
          ...(edge.data || {}),

          interaction:
            edge.data?.interaction ||
            edge.interaction ||
            "share",
        },
      })
    );

  const branchColors = [
    "#3b82f6",
    "#22c55e",
    "#f59e0b",
    "#a855f7",
    "#ef4444",
    "#06b6d4",
    "#ec4899",
    "#84cc16",
    "#f97316",
    "#6366f1"
  ];

  const secondaryColors = [
    "#14b8a6",
    "#e879f9",
    "#fb7185",
    "#38bdf8",
    "#c084fc",
    "#fbbf24"
  ];

  const primaryInteractions = [
    "publish",
    "share",
    "cascade",
    "bot",
    "tree"
  ];

  const secondaryInteractions = [
    "bridge",
    "cross",
    "community",
    "reshare"
  ];

  const savedNodes =
    Array.isArray(savedGraph.nodes)
      ? savedGraph.nodes
      : [];

  const savedNodeMap =
    new Map(
      savedNodes.map(node => [
        node.id,
        node
      ])
    );

  const treeEdges =
    savedGraph.edges.filter(edge => {

      const interaction =
        edge?.data?.interaction ||
        edge?.interaction ||
        "";

      return primaryInteractions.includes(
        interaction
      );
    });

  const parentMap = new Map();

  treeEdges.forEach(edge => {

    if (
      edge.source &&
      edge.target
    ) {
      parentMap.set(
        edge.target,
        edge.source
      );
    }
  });

  const branchMap = new Map();

  function getBranchRoot(nodeId) {

    if (!nodeId) {
      return null;
    }

    if (branchMap.has(nodeId)) {
      return branchMap.get(nodeId);
    }

    let current = nodeId;
    const visited = new Set();

    while (
      parentMap.has(current) &&
      !visited.has(current)
    ) {

      visited.add(current);

      const parent =
        parentMap.get(current);

      if (!parent) {
        break;
      }

      current = parent;
    }

    let branchRoot = current;

    const path = [];
    current = nodeId;

    while (
      current &&
      !visited.has(`path-${current}`)
    ) {

      path.push(current);

      visited.add(`path-${current}`);

      const parent =
        parentMap.get(current);

      if (!parent) {
        break;
      }

      current = parent;
    }

    if (path.length > 1) {
      branchRoot =
        path[path.length - 2];
    }

    branchMap.set(
      nodeId,
      branchRoot
    );

    return branchRoot;
  }

  const branchColorMap =
    new Map();

  let branchColorIndex = 0;

  function getBranchColor(
    source,
    target
  ) {

    const branchRoot =
      getBranchRoot(target) ||
      getBranchRoot(source) ||
      source;

    if (
      branchColorMap.has(branchRoot)
    ) {
      return branchColorMap.get(
        branchRoot
      );
    }

    const color =
      branchColors[
      branchColorIndex %
      branchColors.length
      ];

    branchColorIndex++;

    branchColorMap.set(
      branchRoot,
      color
    );

    return color;
  }

  function getSecondaryColor(
    edge,
    index
  ) {

    const key =
      `${edge.source}-${edge.target}-${index}`;

    let hash = 0;

    for (
      let i = 0;
      i < key.length;
      i++
    ) {
      hash =
        (
          hash * 31 +
          key.charCodeAt(i)
        ) >>> 0;
    }

    return secondaryColors[
      hash %
      secondaryColors.length
    ];
  }

  const analytics =
    savedGraph.analytics ||
    {
      totalNodes:
        savedGraph.statistics?.node_count ??
        normalizedNodes.length,

      totalEdges:
        savedGraph.statistics?.edge_count ??
        normalizedEdges.length,

      averageInfluence:
        0,

      density:
        savedGraph.statistics?.density ??
        0,

      spreadEfficiency:
        0,

      largestCommunity:
        "-",
    };

  /*
   * Saved backend graphs may store influence
   * differently from the frontend detector.
   *
   * If influencers are already saved, preserve them.
   */
  const savedInfluencers =
    Array.isArray(savedGraph.influencers)
      ? savedGraph.influencers
      : Array.isArray(
        savedGraph.influence?.top_influencers
      )
        ? savedGraph.influence.top_influencers
        : [];

  let influencers =
    savedInfluencers
      .map((influencer, index) => {

        const graphNode =
          normalizedNodes.find(
            node =>
              node.id === influencer.id
          );

        const rawScore =
          Number(
            influencer.score ??
            influencer.influenceScore ??
            influencer.networkInfluence ??
            0
          );

        const scorePercent =
          rawScore <= 1
            ? rawScore * 100
            : rawScore;

        if (graphNode) {

          const influencerName =
            influencer.username ||
            influencer.displayName ||
            influencer.display_name ||
            influencer.accountName ||
            influencer.author ||
            influencer.handle ||
            influencer.sourceName ||
            influencer.publisher ||
            graphNode.data?.username ||
            graphNode.data?.displayName ||
            graphNode.data?.display_name ||
            graphNode.data?.accountName ||
            graphNode.data?.author ||
            graphNode.data?.handle ||
            graphNode.data?.sourceName ||
            graphNode.data?.publisher ||
            getNodeDisplayName(graphNode.data);

          const influencerRole =
            getNodeRole({
              ...graphNode.data,

              role:
                influencer.role ??
                influencer.node_role ??
                graphNode.data?.role ??
                graphNode.data?.node_role,

              nodeType:
                influencer.nodeType ??
                influencer.type ??
                graphNode.data?.nodeType ??
                graphNode.data?.node_type,

              isBot:
                influencer.isBot ??
                graphNode.data?.isBot ??
                false,
            });

          const fallbackName =
            influencer.sourceName ||
            influencer.publisher ||
            influencer.accountName ||
            influencer.username ||
            influencer.displayName ||
            influencer.author ||
            influencer.handle ||
            null;

          const fallbackType =
            influencer.type ||
            influencer.nodeType ||
            "influencer";

          return {
            ...graphNode,

            data: {
              ...graphNode.data,

              displayName:
                influencerName,

              sourceName:
                influencer.sourceName ||
                graphNode.data?.sourceName ||
                null,

              publisher:
                influencer.publisher ||
                graphNode.data?.publisher ||
                null,

              accountName:
                influencer.accountName ||
                graphNode.data?.accountName ||
                null,

              username:
                influencer.username ||
                graphNode.data?.username ||
                null,

              author:
                influencer.author ||
                graphNode.data?.author ||
                null,

              label:
                graphNode.data?.label ||
                influencer.label ||
                influencerName,

              nodeType:
                graphNode.data?.nodeType ||
                influencer.nodeType ||
                influencer.type ||
                "influencer",

              role: influencerRole,

              influenceScore: Number(scorePercent.toFixed(2)),

              networkInfluence: Number(scorePercent.toFixed(2)),

              networkInfluencePercent: Number(
                scorePercent.toFixed(2)
              ),

              rank:
                influencer.rank ??
                index + 1,
            }
          };
        }

        return {
          id:
            influencer.id ||
            `influencer-${index}`,

          type: "custom",

          position: {
            x: 0,
            y: 0,
          },
          data: {

            id:
              influencer.id,

            displayName:
              fallbackName ||
              getNodeDisplayName({
                nodeType: fallbackType
              }),

            sourceName:
              influencer.sourceName ||
              null,

            publisher:
              influencer.publisher ||
              null,

            accountName:
              influencer.accountName ||
              null,

            username:
              influencer.username ||
              null,

            author:
              influencer.author ||
              null,

            nodeType:
              fallbackType,

            label:
              getNodeRole({
                nodeType: fallbackType,
                isBot:
                  fallbackType === "bot"
              }),

            followers:

              Number(
                influencer.followers || 0
              ),

            formattedFollowers:
              Number(
                influencer.followers || 0
              ).toLocaleString(),

            influenceScore:
              Number(
                scorePercent.toFixed(2)
              ),

            networkInfluence:
              Number(
                scorePercent.toFixed(2)
              ),

            networkInfluencePercent:
              Number(
                scorePercent.toFixed(2)
              ),

            reach:
              Number(
                influencer.reach || 0
              ),

            community:
              influencer.community ??
              "-",

            verified: false,

            isBot: false,

            viral: false,

            shareProbability: 0,

            pageRank: 0,

            pageRankScore: 0,

            rank:
              influencer.rank ??
              index + 1,
          }
        };
      })
      .filter(Boolean);


  /*
   * If backend did not provide influencers,
   * derive them from the actual graph nodes.
   */
  if (!influencers.length) {
    influencers = [...normalizedNodes]
      .filter(node => {
        const data = node.data || {};

        const type = String(
          data.nodeType ||
          data.node_type ||
          ""
        ).toLowerCase();

        const role = String(
          data.role ||
          ""
        ).toLowerCase();

        return (
          type === "influencer" ||
          type === "micro_influencer" ||
          type === "community_leader" ||
          role === "influencer" ||
          role === "micro_influencer" ||
          role === "community_leader"
        );
      })
      .sort(
        (a, b) =>
          Number(
            b.data?.networkInfluencePercent ??
            b.data?.networkInfluence ??
            b.data?.influenceScore ??
            0
          ) -
          Number(
            a.data?.networkInfluencePercent ??
            a.data?.networkInfluence ??
            a.data?.influenceScore ??
            0
          )
      )
      .slice(0, 10);
  }

  return {
    blueprint:
      savedGraph.blueprint ||
      null,

    nodes:
      normalizedNodes,

    edges:
      normalizedEdges,

    influencers,

    analytics,
  };
}


export default function GraphViewer({
  analysis,
  graph = null,
  interactive = true,
  pdfMode = false,
  showControls = true,
  graphHeight = "760px",
}) {

  const [nodes, setNodes] = useState([]);
  const [edges, setEdges] = useState([]);

  const [analytics, setAnalytics] = useState(null);
  const [influencers, setInfluencers] = useState([]);
  const [blueprint, setBlueprint] = useState(null);

  const [selectedNode, setSelectedNode] =
    useState(null);


  /*
   * Load graph.
   *
   * PRIORITY:
   *
   * 1. Explicit saved graph
   * 2. analysis.graph
   * 3. Generate only when there is NO saved graph
   *
   * This is the critical consistency fix.
   */
  useEffect(() => {

    if (!analysis && !graph) {
      return;
    }

    let cancelled = false;

    const loadGraph = async () => {

      try {

        /*
         * =================================================
         * STEP 1
         * USE SAVED GRAPH
         * =================================================
         */

        const savedGraph =
          graph ||
          analysis?.graph ||
          null;

        if (
          savedGraph &&
          Array.isArray(
            savedGraph.nodes
          ) &&
          Array.isArray(
            savedGraph.edges
          )
        ) {

          const normalized =
            normalizeSavedGraph(
              savedGraph,
              analysis
            );

          /*
           * IMPORTANT:
           * Saved backend graphs do not contain reliable
           * React Flow positions.
           *
           * Run the saved graph through ELK before
           * displaying it.
           */
          const laidOutNodes =
            await ELKLayoutEngine.layout(
              normalized.nodes,
              normalized.edges
            );

          setNodes(laidOutNodes);
          setEdges(normalized.edges);

          setAnalytics(normalized.analytics);
          setInfluencers(normalized.influencers);
          setBlueprint(normalized.blueprint);

          /*
           * VERY IMPORTANT:
           *
           * We return here.
           *
           * GraphGenerator.generate()
           * MUST NOT run when a saved graph exists.
           */
          return;
        }


        /*
         * =================================================
         * STEP 2
         * GENERATE NEW GRAPH ONLY WHEN REQUIRED
         * =================================================
         */

        if (!analysis) {
          return;
        }

        const generatedGraph =
          await GraphGenerator.generate(
            analysis
          );

        if (cancelled) {
          return;
        }

        const reactNodes =
          generatedGraph.nodes.map(
            node => ({
              ...node,
              type: "custom",
            })
          );

        setNodes(
          reactNodes
        );

        setEdges(
          generatedGraph.edges.map(
            (edge, index) => ({
              ...edge,

              id:
                edge.id ||
                `generated-edge-${index}`,

              type: "smoothstep",

              data: {
                ...(edge.data || {}),

                interaction:
                  edge.data?.interaction ||
                  edge.interaction ||
                  "share",
              },
            })
          )
        );

        setAnalytics(
          generatedGraph.analytics
        );

        setInfluencers(
          generatedGraph.influencers
        );

        setBlueprint(
          generatedGraph.blueprint
        );

      } catch (error) {

        console.error(
          "GRAPH GENERATION ERROR:",
          error
        );

        if (!cancelled) {

          setNodes([]);
          setEdges([]);

          setAnalytics(null);
          setInfluencers([]);
          setBlueprint(null);
        }
      }
    };

    loadGraph();

    return () => {
      cancelled = true;
    };

  }, [
    analysis,
    graph,
  ]);


  const nodeTypes = useMemo(
    () => ({
      custom: GraphNode,
    }),
    []
  );


  const closeDetails = () => {
    setSelectedNode(null);
  };

  const safeEdges = useMemo(() => {
    return (edges || []).map((edge, index) => ({
      ...edge,

      id: edge.id || `edge-${index}`,

      type: "smoothstep",

      data: {
        ...(edge.data || {}),
        interaction:
          edge.data?.interaction ||
          edge.interaction ||
          "share",
      },
    }));
  }, [edges]);


  const selectedData = {
    ...(selectedNode?.data?.originalData || {}),
    ...(selectedNode?.data?.nodeData || {}),
    ...(selectedNode?.data || {}),
    ...(selectedNode?.originalData || {}),
  };

  const selectedUsername =
    getNodeDisplayName(selectedData);

  const selectedRole =
    getNodeRole(selectedData);

  const rawFollowers =
    selectedData.followers ??
    selectedData.followerCount ??
    selectedData.follower_count ??
    null;

  const selectedFollowers =
    rawFollowers !== null &&
      rawFollowers !== undefined &&
      rawFollowers !== ""
      ? Number(rawFollowers)
      : null;

  const selectedInfluence =
    Number(
      selectedData.networkInfluencePercent ??
      selectedData.network_influence_percent ??
      selectedData.networkInfluence ??
      selectedData.network_influence ??
      selectedData.influenceScore ??
      selectedData.influence_score ??
      selectedData.score ??
      0
    );

  const selectedReach =
    Number(
      selectedData.reach ??
      selectedData.weightedReach ??
      selectedData.weighted_reach ??
      0
    );

  const selectedCommunity =
    selectedData.community ??
    selectedData.community_id ??
    null;

  const rawPageRank =
    selectedData.pageRank ??
    selectedData.page_rank ??
    selectedData.pagerank ??
    selectedData.page_rank_score ??
    null;

  const selectedPageRank =
    rawPageRank !== null &&
      rawPageRank !== undefined &&
      rawPageRank !== ""
      ? Number(rawPageRank)
      : null;

  const rawShareProbability =
    selectedData.shareProbability ??
    selectedData.share_probability ??
    null;

  const selectedShareProbability =
    rawShareProbability !== null &&
      rawShareProbability !== undefined
      ? Number(rawShareProbability)
      : null;

  return (
    <div className="space-y-6">


      {/* =====================================================
          SUMMARY CARDS
      ===================================================== */}

      <div className="grid grid-cols-2 lg:grid-cols-4 gap-5">

        <div className="bg-slate-800 rounded-xl p-5">

          <h3 className="text-slate-400 text-sm">
            Prediction
          </h3>

          <p className="text-2xl font-bold text-green-400">
            {analysis?.final_result?.label || "-"}
          </p>

        </div>


        <div className="bg-slate-800 rounded-xl p-5">

          <h3 className="text-slate-400 text-sm">
            Confidence
          </h3>

          <p className="text-2xl font-bold text-blue-400">
            {analysis?.final_result?.confidence ?? 0}%
          </p>

        </div>


        <div className="bg-slate-800 rounded-xl p-5">

          <h3 className="text-slate-400 text-sm">
            Risk Level
          </h3>

          <p className="text-2xl font-bold text-red-400">
            {analysis?.final_result?.risk_level || "-"}
          </p>

        </div>


        <div className="bg-slate-800 rounded-xl p-5">

          <h3 className="text-slate-400 text-sm">
            Predicted Reach
          </h3>

          <p className="text-2xl font-bold text-cyan-400">

            {(
              analysis?.prediction?.data
                ?.predicted_reach ??
              analysis?.prediction
                ?.predicted_reach ??
              0
            ).toLocaleString()}

          </p>

        </div>

      </div>


      {/* =====================================================
          GRAPH
      ===================================================== */}

      <div
        id="graph-container"
        className={`bg-slate-800 rounded-xl shadow-2xl border border-slate-700 transition-all duration-300 ${interactive && selectedNode
          ? "mr-[420px]"
          : ""
          }`}
        style={{
          height: graphHeight,
          width: "100%",
        }}
      >

        <ReactFlow
          nodes={nodes}
          edges={safeEdges}
          nodeTypes={nodeTypes}
          fitView
          minZoom={0.02}
          maxZoom={2}
          onNodeClick={
            interactive
              ? (_, node) => {
                console.log("========== CLICKED NODE ==========");
                console.log("FULL NODE:", node);
                console.log("NODE DATA:", node?.data);
                console.log("NODE ID:", node?.id);
                setSelectedNode(node);
              }
              : undefined
          }
        >

          <GraphViewportController
            nodes={nodes}
            pdfMode={pdfMode}
          />


          {!pdfMode && (
            <MiniMap
              pannable
              zoomable
              nodeStrokeWidth={3}
            />
          )}


          {showControls && !pdfMode && (
            <Controls
              showInteractive={false}
              position="bottom-left"
            />
          )}


          <Background
            gap={24}
            size={1}
          />

        </ReactFlow>

      </div>


      {/* =====================================================
          NODE DETAILS
      ===================================================== */}

      {interactive && selectedNode && (

        <div className="fixed top-0 right-0 h-screen w-[420px] bg-slate-900 border-l border-slate-700 shadow-2xl z-50 overflow-y-auto">

          <div className="sticky top-0 bg-slate-900 border-b border-slate-700 p-6 flex justify-between items-center">

            <div>

              <h2 className="text-2xl font-bold text-white">
                Node Details
              </h2>

              <p className="text-slate-400 text-sm mt-1">
                Propagation Node Information
              </p>

            </div>


            <button
              onClick={closeDetails}
              className="text-3xl text-slate-400 hover:text-red-400"
            >
              ×
            </button>

          </div>


          <div className="p-6 space-y-4">

            <InfoCard
              title="Username"
              value={selectedUsername}
            />

            <InfoCard
              title="Role"
              value={selectedRole}
            />

            <InfoCard
              title="Followers"
              value={selectedFollowers !== null &&
                Number.isFinite(selectedFollowers)
                ? selectedFollowers.toLocaleString()
                : "Not available"
              }
            />

            <InfoCard
              title="Network Influence"
              value={
                selectedInfluence !== null &&
                  Number.isFinite(selectedInfluence)
                  ? `${selectedInfluence.toFixed(2)}%`
                  : "Not available"
              }
            />

            <InfoCard
              title="Reach"
              value={
                selectedReach > 0
                  ? selectedReach.toLocaleString()
                  : "Not available"
              }
            />

            <InfoCard
              title="Community"
              value={
                selectedCommunity !== null &&
                  selectedCommunity !== undefined
                  ? selectedCommunity
                  : "Not available"
              }
            />

            <InfoCard
              title="PageRank"
              value={
                selectedPageRank > 0
                  ? selectedPageRank.toFixed(4)
                  : "Not available"
              }
            />

            <InfoCard
              title="Share Probability"
              value={
                selectedShareProbability !== null &&
                  Number.isFinite(selectedShareProbability)
                  ? `${(
                    selectedShareProbability * 100
                  ).toFixed(2)}%`
                  : "Not available"
              }
            />

            <InfoCard
              title="Platform"
              value={
                selectedData.platform ||
                "-"
              }
            />

            <InfoCard
              title="Verified"
              value={
                selectedData.verified
                  ? "Yes ✔"
                  : "No"
              }
            />

            <InfoCard
              title="Bot"
              value={
                selectedData.isBot
                  ? "Yes 🤖"
                  : "No"
              }
            />

            <InfoCard
              title="Created"
              value={
                selectedData.createdAt
                  ? new Date(
                    selectedData.createdAt
                  ).toLocaleString()
                  : "-"
              }
            />

            <InfoCard
              title="Node ID"
              value={selectedNode.id}
            />

          </div>

        </div>
      )}


      {/* =====================================================
          ANALYTICS
      ===================================================== */}

      {!pdfMode && (

        <div className="grid lg:grid-cols-2 gap-6">


          {/* Graph Analytics */}

          <div className="bg-slate-800 rounded-xl p-6">

            <h2 className="text-xl font-bold text-white mb-5">
              Graph Analytics
            </h2>

            <div className="space-y-3 text-slate-300">

              <p>
                Total Nodes :{" "}
                {analytics?.totalNodes ?? 0}
              </p>

              <p>
                Total Edges :{" "}
                {analytics?.totalEdges ?? 0}
              </p>

              <p>
                Average Influence :{" "}
                {analytics?.averageInfluence ?? 0}
              </p>

              <p>
                Graph Density :{" "}
                {analytics?.density ?? 0}
              </p>

              <p>
                Spread Efficiency :{" "}
                {analytics?.spreadEfficiency ?? 0}
              </p>

              <p>
                <strong>
                  Largest Community:
                </strong>{" "}
                {analytics?.largestCommunity ?? "-"}
              </p>

            </div>

          </div>


          {/* Top Influencers */}

          <div className="bg-slate-800 rounded-xl p-6">

            <h2 className="text-xl font-bold text-white mb-5">
              Top Influencers
            </h2>

            <div className="space-y-4">

              {influencers.length > 0 ? (
                influencers
                  .slice(0, 5)
                  .map((node, index) => {
                    const data = node?.data || {};

                    const name =
                      getNodeDisplayName(data);

                    const role =
                      getNodeRole(data);

                    const followers =
                      Number(data.followers || 0);

                    const score =
                      Number(
                        data.networkInfluencePercent ??
                        data.networkInfluence ??
                        data.influenceScore ??
                        0
                      );

                    return (
                      <div
                        key={
                          node.id ||
                          `influencer-${index}`
                        }
                        className="flex justify-between items-start border-b border-slate-700 pb-3"
                      >
                        <div className="min-w-0">
                          <div className="font-semibold text-white truncate">
                            {name}
                          </div>

                          <div className="text-xs text-slate-400">
                            {role}
                          </div>

                          <div className="text-xs text-slate-500">
                            {followers.toLocaleString()} followers
                          </div>
                        </div>

                        <div className="font-bold text-yellow-400">
                          {Math.min(100, Math.max(0, score)).toFixed(0)}%
                        </div>
                      </div>
                    );
                  })
              ) : (
                <div className="py-8 text-center text-slate-400">
                  No influencers detected
                </div>
              )}

            </div>

          </div>

        </div>

      )}

    </div>
  );
}
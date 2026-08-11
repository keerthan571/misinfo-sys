import { useEffect, useMemo, useState } from "react";
import ReactFlow, {
  Background,
  Controls,
  useNodesInitialized,
  useReactFlow,
} from "reactflow";

import "reactflow/dist/style.css";

import GraphNode from "./GraphNode";
import GraphGenerator from "../../graph/GraphGenerator";
import ELKLayoutEngine from "../../graph/ELKLayoutEngine";

function InfoCard({ title, value }) {
  return (
    <div className="bg-slate-800/70 border border-slate-700/70 rounded-xl p-4">
      <div className="text-xs font-semibold uppercase tracking-wider text-slate-500">
        {title}
      </div>
      <div className="text-base font-semibold text-slate-100 mt-2 break-all">
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
function GraphControls() {
  const { zoomIn, zoomOut, fitView } = useReactFlow();

  return (
    <div className="absolute top-5 left-5 z-[1000] flex flex-col overflow-hidden rounded-xl border border-slate-600 bg-slate-900/95 shadow-2xl">
      <button
        type="button"
        onClick={() => zoomIn({ duration: 200 })}
        className="flex h-11 w-11 items-center justify-center border-b border-slate-700 text-2xl font-semibold text-white transition hover:bg-blue-600"
        title="Zoom in"
      >
        +
      </button>
      <button
        type="button"
        onClick={() => zoomOut({ duration: 200 })}
        className="flex h-11 w-11 items-center justify-center border-b border-slate-700 text-2xl font-semibold text-white transition hover:bg-blue-600"
        title="Zoom out"
      >
        −
      </button>
      <button
        type="button"
        onClick={() => fitView({ padding: 0.08, duration: 300 })}
        className="flex h-11 w-11 items-center justify-center text-lg font-semibold text-white transition hover:bg-blue-600"
        title="Fit view"
      >
        ⛶
      </button>
    </div>
  );
}

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
        padding: pdfMode ? 0.04 : 0.06,
        duration: 0,
        minZoom: pdfMode ? 0.02 : 0.12,
        maxZoom: 1.5,
      });
    };

    const timer = setTimeout(fitGraph, 300);

    return () => {
      clearTimeout(timer);
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

    type: "default",
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
              (
                isClaim
                  ? sourceFollowers
                  : null
              ),

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
      (edge, index) => {

        const targetNode =
          savedGraph.nodes.find(
            node =>
              node.id === edge.target
          );

        const targetParentId =
          targetNode?.data?.parentId ??
          targetNode?.parentId ??
          null;

        let interaction =
          edge.data?.interaction ||
          edge.interaction ||
          edge.edgeType ||
          null;

        if (!interaction) {

          if (
            targetParentId &&
            targetParentId === edge.source
          ) {
            interaction = "tree";
          } else {
            interaction = "cross";
          }
        }

        return {
          ...edge,

          id:
            edge.id ||
            `saved-edge-${index}`,

          type: "default",

          data: {
            ...(edge.data || {}),

            interaction,
          },
        };
      }
    );

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
  graphHeight = "850px",
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

              type: "default",

              data: {
                ...(edge.data || {}),

                interaction:
                  edge.data?.interaction ||
                  edge.interaction ||
                  edge.edgeType ||
                  edge.type ||
                  null,
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

    const fallbackColors = {
      tree: "#3b82f6",
      publish: "#22c55e",
      share: "#f59e0b",
      cascade: "#a855f7",
      bot: "#ef4444",

      cross: "#38bdf8",
      community: "#fbbf24",
      reshare: "#fb7185",
      bridge: "#c084fc",
    };

    return (edges || []).map(
      (edge, index) => {

        const interaction =
          edge?.data?.interaction ||
          edge?.interaction ||
          edge?.edgeType ||
          "share";

        /*
         * =====================================================
         * IMPORTANT
         *
         * EdgeGenerator ALREADY assigns the correct color.
         *
         * DO NOT generate another branch color here.
         *
         * Priority:
         * 1. edge.data.color
         * 2. edge.style.stroke
         * 3. fallback interaction color
         * =====================================================
         */

        const edgeColor =
          edge?.data?.color ||
          edge?.style?.stroke ||
          fallbackColors[interaction] ||
          "#94a3b8";

        const isPrimary =
          interaction === "tree" ||
          interaction === "publish" ||
          interaction === "share" ||
          interaction === "cascade" ||
          interaction === "bot";

        return {

          ...edge,

          id:
            edge.id ||
            `edge-${index}`,

          /*
           * React Flow default edge =
           * curved Bezier edge.
           */
          type: "default",

          /*
           * Preserve generator animation.
           */
          animated:
            edge.animated ??
            (
              interaction === "tree" ||
              interaction === "reshare"
            ),

          style: {

            ...(edge.style || {}),

            /*
             * USE THE COLOR GENERATED BY EDGEGENERATOR.
             */
            stroke: edgeColor,

            strokeWidth:
              edge.style?.strokeWidth ||
              (
                isPrimary
                  ? 2.5
                  : 1.8
              ),

            opacity:
              edge.style?.opacity ??
              (
                isPrimary
                  ? 0.9
                  : 0.65
              ),

          },

          data: {

            ...(edge.data || {}),

            interaction,

            /*
             * Keep the actual edge color available.
             */
            color: edgeColor,

          },

        };

      }
    );

  }, [edges]);


  const selectedData = {
    ...(selectedNode?.data?.originalData || {}),
    ...(selectedNode?.data?.nodeData || {}),
    ...(selectedNode?.data || {}),
    ...(selectedNode?.originalData || {}),
  };

  const selectedNodeType = String(
    selectedData.nodeType ||
    selectedData.node_type ||
    selectedNode?.type ||
    ""
  ).toLowerCase();

  const isSourceNode =
    selectedNodeType === "claim" ||
    selectedNodeType === "source" ||
    selectedNodeType === "origin";

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

        <div className="relative overflow-hidden bg-slate-800/90 border border-blue-500/20 rounded-2xl p-6 shadow-lg hover:border-blue-400/40 hover:-translate-y-0.5 transition-all duration-200">

          <div className="absolute right-5 top-5 w-10 h-10 rounded-xl bg-blue-500/10 border border-blue-500/20 flex items-center justify-center">
            <span className="text-blue-400 text-lg">✓</span>
          </div>

          <h3 className="text-xs font-semibold uppercase tracking-wider text-slate-500">
            Prediction
          </h3>

          <p className="text-2xl font-bold text-blue-400 mt-5 pr-12">
            {analysis?.final_result?.label || "-"}
          </p>

          <div className="w-full h-px bg-slate-700/70 mt-5" />

          <p className="text-xs text-slate-500 mt-3">
            AI classification result
          </p>

        </div>


        <div className="relative overflow-hidden bg-slate-800/90 border border-cyan-500/20 rounded-2xl p-6 shadow-lg hover:border-cyan-400/40 hover:-translate-y-0.5 transition-all duration-200">

          <div className="absolute right-5 top-5 w-10 h-10 rounded-xl bg-cyan-500/10 border border-cyan-500/20 flex items-center justify-center">
            <span className="text-cyan-400 text-lg">◉</span>
          </div>

          <h3 className="text-xs font-semibold uppercase tracking-wider text-slate-500">
            Confidence
          </h3>

          <p className="text-4xl font-bold text-cyan-400 mt-4">
            {analysis?.final_result?.confidence ?? 0}%
          </p>

          <div className="mt-5 h-2 bg-slate-900 rounded-full overflow-hidden">
            <div
              className="h-full bg-cyan-400 rounded-full"
              style={{
                width: `${Math.min(
                  Math.max(
                    Number(
                      analysis?.final_result?.confidence ?? 0
                    ),
                    0
                  ),
                  100
                )}%`,
              }}
            />
          </div>

          <p className="text-xs text-slate-500 mt-3">
            Model confidence
          </p>

        </div>


        <div className="relative overflow-hidden bg-slate-800/90 border border-emerald-500/20 rounded-2xl p-6 shadow-lg hover:border-emerald-400/40 hover:-translate-y-0.5 transition-all duration-200">

          <div className="absolute right-5 top-5 w-10 h-10 rounded-xl bg-emerald-500/10 border border-emerald-500/20 flex items-center justify-center">
            <span className="text-emerald-400 text-lg">!</span>
          </div>

          <h3 className="text-xs font-semibold uppercase tracking-wider text-slate-500">
            Risk Level
          </h3>

          <p
            className={`text-3xl font-bold mt-4 ${String(
              analysis?.final_result?.risk_level || ""
            ).toLowerCase() === "high"
              ? "text-red-400"
              : String(
                analysis?.final_result?.risk_level || ""
              ).toLowerCase() === "medium"
                ? "text-yellow-400"
                : "text-emerald-400"
              }`}
          >
            {analysis?.final_result?.risk_level || "-"}
          </p>

          <div className="w-full h-px bg-slate-700/70 mt-5" />

          <p className="text-xs text-slate-500 mt-3">
            Propagation risk assessment
          </p>

        </div>


        <div className="relative overflow-hidden bg-slate-800/90 border border-violet-500/20 rounded-2xl p-6 shadow-lg hover:border-violet-400/40 hover:-translate-y-0.5 transition-all duration-200">

          <div className="absolute right-5 top-5 w-10 h-10 rounded-xl bg-violet-500/10 border border-violet-500/20 flex items-center justify-center">
            <span className="text-violet-400 text-lg">↗</span>
          </div>

          <h3 className="text-xs font-semibold uppercase tracking-wider text-slate-500">
            Predicted Reach
          </h3>

          <p className="text-4xl font-bold text-violet-400 mt-4">
            {(
              analysis?.prediction?.data
                ?.predicted_reach ??
              analysis?.prediction
                ?.predicted_reach ??
              0
            ).toLocaleString()}
          </p>

          <div className="w-full h-px bg-slate-700/70 mt-5" />

          <p className="text-xs text-slate-500 mt-3">
            Estimated network exposure
          </p>

        </div>

      </div>


      {/* =====================================================
          GRAPH
      ===================================================== */}

      <div
        id="graph-container"
        className={`bg-slate-800/90 rounded-3xl shadow-2xl border border-slate-700/70 overflow-hidden transition-all duration-300 ${interactive && selectedNode
          ? "mr-[420px]"
          : ""
          }`}
        style={{
          height: graphHeight,
          width: "100%",
        }}
      >
        <div className="px-6 py-5 border-b border-slate-700/70 bg-slate-800/80">
          <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">

            <div>
              <p className="text-xs font-semibold uppercase tracking-wider text-blue-400">
                Network Visualization
              </p>

              <h2 className="text-xl font-bold text-white mt-1">
                Propagation Network
              </h2>

              <p className="text-sm text-slate-500 mt-1">
                Visual representation of information spread through the network
              </p>
            </div>

            <div className="flex items-center gap-3">

              <span className="px-3 py-2 rounded-xl bg-slate-900 border border-slate-700 text-sm text-slate-300">
                {nodes.length} Nodes
              </span>

              <span className="px-3 py-2 rounded-xl bg-slate-900 border border-slate-700 text-sm text-slate-300">
                {safeEdges.length} Connections
              </span>

            </div>

          </div>
        </div>
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

          {!pdfMode && <GraphControls />}



          <Background
            gap={28}
            size={1}
            color="#334155"
          />
        </ReactFlow>
        <div className="px-6 py-4 border-t border-slate-700/70 bg-slate-800/80">
          <div className="flex flex-wrap items-center gap-x-6 gap-y-2 text-xs text-slate-400">

            <span className="font-semibold uppercase tracking-wider text-slate-500">
              Legend
            </span>

            <span className="flex items-center gap-2">
              <span className="w-2.5 h-2.5 rounded-full bg-blue-400" />
              Source
            </span>

            <span className="flex items-center gap-2">
              <span className="w-2.5 h-2.5 rounded-full bg-violet-400" />
              Influencer
            </span>

            <span className="flex items-center gap-2">
              <span className="w-2.5 h-2.5 rounded-full bg-red-400" />
              Bot
            </span>

            <span className="flex items-center gap-2">
              <span className="w-2.5 h-2.5 rounded-full bg-cyan-400" />
              User
            </span>

            <span className="flex items-center gap-2">
              <span className="w-2.5 h-2.5 rounded-full bg-emerald-400" />
              Community Leader
            </span>

          </div>
        </div>
      </div>


      {/* =====================================================
          NODE DETAILS
      ===================================================== */}

      {interactive && selectedNode && (

        <div className="fixed top-0 right-0 h-screen w-[420px] max-w-[92vw] bg-slate-900 border-l border-slate-700/80 shadow-2xl z-50 overflow-y-auto">

          <div className="sticky top-0 bg-slate-900/95 backdrop-blur-md border-b border-slate-700/70 p-6 flex justify-between items-center z-10">

            <div>

              <p className="text-xs font-semibold uppercase tracking-wider text-blue-400">
                Node Details
              </p>

              <h2 className="text-xl font-bold text-white mt-1">
                Propagation Node
              </h2>

              <p className="text-slate-400 text-sm mt-1">
                Propagation Node Information
              </p>

            </div>


            <button
              onClick={closeDetails}
              className="w-10 h-10 rounded-xl bg-slate-800 border border-slate-700 text-xl text-slate-400 hover:text-white hover:border-slate-600 transition flex items-center justify-center"
            >
              ×
            </button>

          </div>


          <div className="p-6 space-y-3">

            <InfoCard
              title={isSourceNode ? "Publisher" : "Username"}
              value={selectedUsername}
            />

            <InfoCard
              title="Role"
              value={selectedRole}
            />

            {!isSourceNode && (
              <InfoCard
                title="Followers"
                value={
                  selectedFollowers !== null &&
                    Number.isFinite(selectedFollowers)
                    ? selectedFollowers.toLocaleString()
                    : "Not available"
                }
              />
            )}

            <InfoCard
              title="Network Influence"
              value={
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
                selectedPageRank !== null &&
                  Number.isFinite(selectedPageRank)
                  ? selectedPageRank.toFixed(4)
                  : "Not available"
              }
            />

            {!isSourceNode && (
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
            )}

            <InfoCard
              title="Platform"
              value={
                selectedData.platform || "-"
              }
            />

            {!isSourceNode && (
              <>
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
              </>
            )}

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

          <div className="bg-slate-800/90 border border-slate-700/70 rounded-3xl p-6 shadow-lg">

            <div className="flex items-center gap-3 mb-6">

              <div className="w-1 h-8 bg-cyan-400 rounded-full" />

              <div>
                <h2 className="text-xl font-bold text-white">
                  Graph Analytics
                </h2>

                <p className="text-sm text-slate-500 mt-1">
                  Network structure and propagation metrics
                </p>
              </div>

            </div>


            <div className="grid grid-cols-2 md:grid-cols-3 gap-3">

              <div className="bg-slate-900/80 border border-slate-700 rounded-2xl p-4">
                <p className="text-xs text-slate-500">
                  Total Nodes
                </p>

                <p className="text-2xl font-bold text-blue-400 mt-2">
                  {analytics?.totalNodes ?? 0}
                </p>
              </div>


              <div className="bg-slate-900/80 border border-slate-700 rounded-2xl p-4">
                <p className="text-xs text-slate-500">
                  Total Edges
                </p>

                <p className="text-2xl font-bold text-cyan-400 mt-2">
                  {analytics?.totalEdges ?? 0}
                </p>
              </div>


              <div className="bg-slate-900/80 border border-slate-700 rounded-2xl p-4">
                <p className="text-xs text-slate-500">
                  Average Influence
                </p>

                <p className="text-2xl font-bold text-violet-400 mt-2">
                  {analytics?.averageInfluence ?? 0}
                </p>
              </div>


              <div className="bg-slate-900/80 border border-slate-700 rounded-2xl p-4">
                <p className="text-xs text-slate-500">
                  Graph Density
                </p>

                <p className="text-2xl font-bold text-amber-400 mt-2">
                  {analytics?.density ?? 0}
                </p>
              </div>


              <div className="bg-slate-900/80 border border-slate-700 rounded-2xl p-4">
                <p className="text-xs text-slate-500">
                  Spread Efficiency
                </p>

                <p className="text-2xl font-bold text-emerald-400 mt-2">
                  {analytics?.spreadEfficiency ?? 0}
                </p>
              </div>


              <div className="bg-slate-900/80 border border-slate-700 rounded-2xl p-4">
                <p className="text-xs text-slate-500">
                  Largest Community
                </p>

                <p className="text-2xl font-bold text-pink-400 mt-2">
                  {analytics?.largestCommunity ?? "-"}
                </p>
              </div>

            </div>

          </div>


          {/* Top Influencers */}

          <div className="bg-slate-800/90 border border-slate-700/70 rounded-3xl p-6 shadow-lg">

            <div className="flex items-center justify-between mb-5">

              <div>
                <h2 className="text-xl font-bold text-white">
                  Top Influencers
                </h2>

                <p className="text-sm text-slate-500 mt-1">
                  Accounts with the strongest network influence
                </p>
              </div>

              <div className="w-10 h-10 rounded-xl bg-violet-500/10 border border-violet-500/20 flex items-center justify-center">
                <span className="text-violet-400 font-bold">
                  ★
                </span>
              </div>

            </div>

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
                        className="flex justify-between items-start bg-slate-900/80 border border-slate-700/70 rounded-2xl p-4 hover:border-violet-500/30 transition"
                      >
                        <div className="min-w-0">
                          <div className="flex items-center gap-3">

                            <div className="w-9 h-9 rounded-xl bg-violet-500/10 border border-violet-500/20 flex items-center justify-center text-xs font-bold text-violet-400">
                              #{index + 1}
                            </div>

                            <div className="font-semibold text-white truncate">
                              {name}
                            </div>

                          </div>

                          <div className="text-xs text-slate-400">
                            {role}
                          </div>

                          <div className="text-xs text-slate-500 mt-1">
                            {followers > 0
                              ? `${followers.toLocaleString()} followers`
                              : "Followers not available"}
                          </div>
                        </div>

                        <div className="text-right ml-4">

                          <div className="font-bold text-violet-400">
                            {Math.min(
                              100,
                              Math.max(0, score)
                            ).toFixed(0)}%
                          </div>

                          <div className="text-[10px] uppercase tracking-wider text-slate-600 mt-1">
                            Influence
                          </div>

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
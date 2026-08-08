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


/*
 * Automatically centers the complete graph
 * after ReactFlow has finished initializing nodes.
 */
function GraphViewportController({ nodes, pdfMode }) {
  const { fitView } = useReactFlow();
  const nodesInitialized = useNodesInitialized();

  useEffect(() => {
    if (!nodes.length || !nodesInitialized) {
      return;
    }

    const timer = setTimeout(() => {
      fitView({
        padding: pdfMode ? 0.05 : 0.12,
        duration: 0,
        minZoom: pdfMode ? 0.02 : 0.05,
        maxZoom: 2,
      });
    }, pdfMode ? 500 : 200);

    return () => clearTimeout(timer);
  }, [
    nodes,
    nodesInitialized,
    fitView,
    pdfMode,
  ]);

  return null;
}


export default function GraphViewer({
  analysis,
  interactive = true,
  pdfMode = false,
  showControls = false,
  graphHeight = "760px",
}) {

  const [nodes, setNodes] = useState([]);
  const [edges, setEdges] = useState([]);

  const [analytics, setAnalytics] = useState(null);
  const [influencers, setInfluencers] = useState([]);
  const [blueprint, setBlueprint] = useState(null);

  const [selectedNode, setSelectedNode] = useState(null);


  /*
   * Generate graph whenever analysis changes.
   */
  useEffect(() => {

    if (!analysis) {
      return;
    }

    let cancelled = false;

    const loadGraph = async () => {

      try {

        const graph =
          await GraphGenerator.generate(
            analysis
          );

        if (cancelled) {
          return;
        }

        const reactNodes =
          graph.nodes.map(node => ({
            ...node,
            type: "custom",
          }));

        setNodes(reactNodes);
        setEdges(graph.edges);

        setAnalytics(
          graph.analytics
        );

        setInfluencers(
          graph.influencers
        );

        setBlueprint(
          graph.blueprint
        );

      } catch (error) {

        console.error(
          "GRAPH GENERATION ERROR:",
          error
        );

        if (!cancelled) {
          setNodes([]);
          setEdges([]);
        }
      }
    };

    loadGraph();

    return () => {
      cancelled = true;
    };

  }, [analysis]);


  const nodeTypes = useMemo(
    () => ({
      custom: GraphNode,
    }),
    []
  );


  const closeDetails = () => {
    setSelectedNode(null);
  };


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
          edges={edges}
          nodeTypes={nodeTypes}
          fitView
          minZoom={0.02}
          maxZoom={2}
          onNodeClick={
            interactive
              ? (_, node) => setSelectedNode(node.data)
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
              value={selectedNode.displayName}
            />

            <InfoCard
              title="Role"
              value={selectedNode.label}
            />

            <InfoCard
              title="Followers"
              value={selectedNode.formattedFollowers}
            />

            <InfoCard
              title="Network Influence"
              value={`${Math.round(
                selectedNode.networkInfluencePercent
              )}%`}
            />

            <InfoCard
              title="Reach"
              value={selectedNode.reach}
            />

            <InfoCard
              title="Community"
              value={selectedNode.community}
            />

            <InfoCard
              title="PageRank"
              value={
                selectedNode.pageRank?.toFixed(4)
              }
            />

            <InfoCard
              title="Share Probability"
              value={`${Math.round(
                selectedNode.shareProbability * 100
              )}%`}
            />

            <InfoCard
              title="Platform"
              value={selectedNode.platform}
            />

            <InfoCard
              title="Verified"
              value={
                selectedNode.verified
                  ? "Yes ✔"
                  : "No"
              }
            />

            <InfoCard
              title="Bot"
              value={
                selectedNode.isBot
                  ? "Yes 🤖"
                  : "No"
              }
            />

            <InfoCard
              title="Created"
              value={
                selectedNode.createdAt
                  ? new Date(
                    selectedNode.createdAt
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

              {influencers
                .slice(0, 5)
                .map(node => (

                  <div
                    key={node.id}
                    className="flex justify-between border-b border-slate-700 pb-2"
                  >

                    <div>

                      <div className="font-semibold text-white">
                        {node.data.displayName}
                      </div>

                      <div className="text-xs text-slate-400">
                        {node.data.label}
                      </div>

                      <div className="text-xs text-slate-500">
                        {node.data.formattedFollowers} followers
                      </div>

                    </div>

                    <div className="text-yellow-400 font-bold">
                      {Math.round(
                        node.data
                          .networkInfluencePercent
                      )}%
                    </div>

                  </div>

                ))}

            </div>

          </div>

        </div>

      )}

    </div>
  );
}
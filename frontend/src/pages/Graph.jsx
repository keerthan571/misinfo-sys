import { useEffect, useState } from "react";
import { useLocation, Navigate } from "react-router-dom";
import ReactFlow, {
  Background,
  Controls,
  MiniMap,
} from "reactflow";
import dagre from "dagre";
import "reactflow/dist/style.css";
import GraphNode from "../components/graph/GraphNode";

const dagreGraph = new dagre.graphlib.Graph();
dagreGraph.setDefaultEdgeLabel(() => ({}));

const nodeWidth = 170;
const nodeHeight = 70;

const getLayoutedElements = (nodes, edges) => {
  dagreGraph.setGraph({
    rankdir: "TB",
    ranksep: 120,
    nodesep: 80,
  });

  nodes.forEach((node) => {
    dagreGraph.setNode(node.id, {
      width: nodeWidth,
      height: nodeHeight,
    });
  });

  edges.forEach((edge) => {
    dagreGraph.setEdge(edge.source, edge.target);
  });

  dagre.layout(dagreGraph);

  const layoutedNodes = nodes.map((node) => {
    const position = dagreGraph.node(node.id);

    return {
      ...node,
      position: {
        x: position.x - nodeWidth / 2,
        y: position.y - nodeHeight / 2,
      },
    };
  });

  return {
    nodes: layoutedNodes,
    edges,
  };
};

export default function Graph() {
  const location = useLocation();

  const graph = location.state?.graph;
  const analysis = location.state?.analysis;

  const [nodes, setNodes] = useState([]);
  const [edges, setEdges] = useState([]);

  useEffect(() => {
    if (!graph) return;

    const flowNodes = graph.nodes.map((node) => ({
      id: node.id,

      type: "custom",

      data: {
        label: node.label,

        type: node.type,

        followers: node.followers,

        influenceScore: node.influenceScore,

        shareProbability: node.shareProbability,

        verified: node.verified,

        cluster: node.cluster,
      },

      position: { x: 0, y: 0 },
    }));
    const flowEdges = graph.edges.map((edge, index) => ({
      id: `edge-${index}`,
      source: edge.source,
      target: edge.target,
      animated: true,
      type: "smoothstep",
      style: {
        stroke: "#60a5fa",
        strokeWidth: 2,
      },
    }));

    const layouted = getLayoutedElements(flowNodes, flowEdges);

    setNodes(layouted.nodes);
    setEdges(layouted.edges);
  }, [graph]);

  const nodeTypes = {
    custom: GraphNode,
  };
  
  if (!graph) {
    return <Navigate to="/analyze" replace />;
  }

  return (
    <div className="space-y-6 p-6">

      <h1 className="text-4xl font-bold text-white">
        🌐 Propagation Analytics
      </h1>

      {/* Analysis Summary */}
      <div className="bg-slate-800 rounded-xl p-6 shadow-lg text-white">

        <h2 className="text-2xl font-bold mb-4">
          Analysis Summary
        </h2>

        <p>
          <strong>Prediction:</strong>{" "}
          {analysis?.final_result?.label}
        </p>

        <p className="mt-2">
          <strong>Confidence:</strong>{" "}
          {analysis?.final_result?.confidence}%
        </p>

        <p className="mt-2">
          <strong>Risk Level:</strong>{" "}
          {analysis?.final_result?.risk_level}
        </p>

        <p className="mt-2">
          <strong>Summary:</strong>{" "}
          {analysis?.final_result?.summary}
        </p>

      </div>

      {/* Graph */}
      <div
        className="bg-slate-800 rounded-xl shadow-lg"
        style={{ height: "700px" }}
      >
        <ReactFlow
          nodes={nodes}
          edges={edges}
          nodeTypes={nodeTypes}
          fitView
        >
          <MiniMap zoomable pannable />
          <Controls showInteractive />
          <Background gap={20} size={1} />
        </ReactFlow>
      </div>

      {/* Legend */}
      <div className="bg-slate-800 rounded-xl p-5 text-white">

        <h2 className="text-xl font-semibold mb-3">
          Graph Legend
        </h2>

        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">

          <div className="flex items-center gap-2">
            <span className="w-4 h-4 rounded-full bg-red-500"></span>
            Source Post
          </div>

          <div className="flex items-center gap-2">
            <span className="w-4 h-4 rounded-full bg-blue-500"></span>
            User
          </div>

          <div className="flex items-center gap-2">
            <span className="w-4 h-4 rounded-full bg-green-500"></span>
            Influencer
          </div>

          <div className="flex items-center gap-2">
            <span className="w-4 h-4 rounded-full bg-purple-500"></span>
            Community
          </div>

        </div>

      </div>

    </div>
  );
}
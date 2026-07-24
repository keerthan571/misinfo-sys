import { useState } from "react";
import ReactFlow, {
  Background,
  Controls,
  MiniMap,
} from "reactflow";
import dagre from "dagre";
import "reactflow/dist/style.css";

import apiClient from "../api/apiClient";

const dagreGraph = new dagre.graphlib.Graph();
dagreGraph.setDefaultEdgeLabel(() => ({}));

const nodeWidth = 170;
const nodeHeight = 70;

const getLayoutedElements = (nodes, edges) => {
  dagreGraph.setGraph({
    rankdir: "TB", // Top -> Bottom
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
  const [content, setContent] = useState("");
  const [reposts, setReposts] = useState("");
  const [nodes, setNodes] = useState([]);
  const [edges, setEdges] = useState([]);
  const [loading, setLoading] = useState(false);

  const generateGraph = async () => {
    if (!content || !reposts) {
      alert("Please enter content and repost count.");
      return;
    }

    try {
      setLoading(true);

      const response = await apiClient.post("/graph/", {
        content,
        reposts: Number(reposts),
      });

      const graph = response.data;

      const flowNodes = graph.nodes.map((node) => ({
        id: node.id,
        data: {
          label: node.label,
        },
        style: {
          background: node.color,
          color: "#fff",
          border: "2px solid white",
          borderRadius: "12px",
          width: 150,
          padding: "10px",
          textAlign: "center",
          fontWeight: "bold",
          fontSize: "14px",
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

    } catch (error) {
      console.error(error);
      alert("Failed to generate graph.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6 p-6">

      <h1 className="text-4xl font-bold text-white">
        🌐 Propagation Analytics
      </h1>

      <div className="bg-slate-800 rounded-xl p-6 space-y-4 shadow-lg">

        <textarea
          rows={5}
          value={content}
          onChange={(e) => setContent(e.target.value)}
          className="w-full p-4 rounded-lg bg-slate-900 text-white border border-slate-700"
          placeholder="Enter news article..."
        />

        <input
          type="number"
          value={reposts}
          onChange={(e) => setReposts(e.target.value)}
          className="w-full p-4 rounded-lg bg-slate-900 text-white border border-slate-700"
          placeholder="Number of reposts"
        />

        <button
          onClick={generateGraph}
          className="bg-blue-600 hover:bg-blue-700 transition-all px-8 py-3 rounded-lg font-semibold text-white"
        >
          {loading ? "Generating..." : "Generate Propagation Graph"}
        </button>

      </div>

      <div
        className="bg-slate-800 rounded-xl shadow-lg"
        style={{ height: "700px" }}
      >
        <ReactFlow
          nodes={nodes}
          edges={edges}
          fitView
        >
          <MiniMap zoomable pannable />
          <Controls showInteractive={true} />
          <Background gap={20} size={1} />
        </ReactFlow>
      </div>

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
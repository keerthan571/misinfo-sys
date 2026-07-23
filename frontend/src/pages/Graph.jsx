import { useState } from "react";
import ReactFlow, {
  Background,
  Controls,
  MiniMap,
} from "reactflow";
import "reactflow/dist/style.css";

import apiClient from "../api/apiClient";

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

      const response = await apiClient.post("/api/graph/", {
        content,
        reposts: Number(reposts),
      });

      const graph = response.data;

      // Create React Flow nodes
      const flowNodes = graph.nodes.map((node, index) => ({
        id: node,
        data: { label: node },
        position: {
          x: (index % 5) * 220,
          y: Math.floor(index / 5) * 150,
        },
      }));

      // Create React Flow edges
      const flowEdges = graph.edges.map((edge, index) => ({
        id: `edge-${index}`,
        source: edge.source,
        target: edge.target,
        animated: true,
      }));

      setNodes(flowNodes);
      setEdges(flowEdges);
    } catch (error) {
      console.error(error);
      alert("Failed to generate graph.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">

      <h1 className="text-3xl font-bold text-white">
        🌐 Propagation Graph
      </h1>

      <div className="bg-slate-800 rounded-xl p-6 space-y-4">

        <textarea
          rows={4}
          value={content}
          onChange={(e) => setContent(e.target.value)}
          className="w-full p-3 rounded bg-slate-900 text-white"
          placeholder="Enter news content..."
        />

        <input
          type="number"
          value={reposts}
          onChange={(e) => setReposts(e.target.value)}
          className="w-full p-3 rounded bg-slate-900 text-white"
          placeholder="Number of reposts"
        />

        <button
          onClick={generateGraph}
          className="bg-blue-600 hover:bg-blue-700 px-6 py-3 rounded-lg"
        >
          {loading ? "Generating..." : "Generate Graph"}
        </button>

      </div>

      <div className="bg-slate-800 rounded-xl h-[650px]">

        <ReactFlow
          nodes={nodes}
          edges={edges}
          fitView
        >
          <MiniMap />
          <Controls />
          <Background />
        </ReactFlow>

      </div>

    </div>
  );
}
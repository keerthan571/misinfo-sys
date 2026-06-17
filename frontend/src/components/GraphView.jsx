import React from "react";
import ForceGraph2D from "react-force-graph-2d";

const GraphView = ({ data }) => {
  if (!data || !data.nodes || !data.edges) {
    return (
      <div className="card">
        <h2>Propagation Graph</h2>
        <p>No graph data available</p>
      </div>
    );
  }

  // 🔥 Detect top influencer (from backend)
  const topInfluencer = data.top_influencer;

  // 🔥 Build node set
  const nodeSet = new Set(data.nodes);

  data.edges.forEach((edge) => {
    nodeSet.add(edge.source);
    nodeSet.add(edge.target);
  });

  // 🔥 Create nodes with styling info
  const nodes = Array.from(nodeSet).map((id) => {
    let color = "#3b82f6"; // blue (users)
    let size = 8;

    if (id.startsWith("Post")) {
      color = "#ef4444"; // red
      size = 12;
    }

    if (id === topInfluencer) {
      color = "#22c55e"; // green
      size = 16;
    }

    return { id, color, size };
  });

  // 🔥 Create links
  const links = data.edges.map((edge) => ({
    source: edge.source,
    target: edge.target
  }));

  const graphData = { nodes, links };

  return (
    <div className="card">
      <h2>Propagation Graph</h2>

      <p style={{ fontSize: "0.9rem", color: "#6b7280" }}>
        Nodes: {nodes.length} | Links: {links.length}
      </p>

      <div style={{ width: "100%", height: "500px" }}>
        <ForceGraph2D
          graphData={graphData}
          width={800}
          height={500}

          nodeLabel={(node) => `${node.id}`}

          // 🔥 Apply custom color + size
          nodeCanvasObject={(node, ctx, globalScale) => {
            const label = node.id;
            const fontSize = 12 / globalScale;

            ctx.beginPath();
            ctx.arc(node.x, node.y, node.size, 0, 2 * Math.PI, false);
            ctx.fillStyle = node.color;
            ctx.fill();

            ctx.font = `${fontSize}px Sans-Serif`;
            ctx.fillStyle = "#111";
            ctx.fillText(label, node.x + 8, node.y + 4);
          }}

          linkDirectionalArrowLength={6}
          linkDirectionalArrowRelPos={1}

          cooldownTicks={150}
          d3VelocityDecay={0.6}
          d3AlphaDecay={0.1}

          d3Force={(fg) => {
            fg.d3Force("charge").strength(-200);
            fg.d3Force("link").distance(120);
          }}

          enableNodeDrag={true}
        />
      </div>
    </div>
  );
};

export default GraphView;
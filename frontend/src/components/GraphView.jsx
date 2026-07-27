import React from "react";
import ForceGraph2D from "react-force-graph-2d";
import AnalyticsPanel from "./graph/AnalyticsPanel";

const GraphView = ({ data }) => {
  if (!data || !data.nodes || !data.edges) {
    return (
      <div className="card">
        <h2>Propagation Graph</h2>
        <p>No graph data available</p>
      </div>
    );
  }

  // ----------------------------
  // Backend already sends complete node objects
  // ----------------------------
  
  const TYPE_CONFIG = {
  origin: {
    color: "#ef4444",
    icon: "📢",
    size: 16,
  },
  influencer: {
    color: "#f59e0b",
    icon: "⭐",
    size: 14,
  },
  media: {
    color: "#10b981",
    icon: "📰",
    size: 13,
  },
  bot: {
    color: "#6b7280",
    icon: "🤖",
    size: 11,
  },
  user: {
    color: "#2563eb",
    icon: "👤",
    size: 10,
  },
};

const nodes = data.nodes.map((node) => {
  const config = TYPE_CONFIG[node.type] || TYPE_CONFIG.user;

  return {
    ...node,
    color: config.color,
    icon: config.icon,
    size: config.size,
  };
});
  // ----------------------------
  // Links
  // ----------------------------
  const links = data.edges.map((edge) => ({
    source: edge.source,
    target: edge.target
  }));

  const graphData = {
    nodes,
    links
  };
  const analytics = data.analytics || {};
  return (
    <div
      className="card"
      style={{
        padding: "20px",
        borderRadius: "12px",
        background: "#ffffff"
      }}
    >
      <h2 style={{ marginBottom: "10px" }}>
        Propagation Graph
      </h2>

      <p
        style={{
          color: "#6b7280",
          marginBottom: "15px"
        }}
      >
        Nodes : {nodes.length} | Links : {links.length}
      </p>

      <div
        style={{
          width: "100%",
          height: "600px",
          border: "1px solid #e5e7eb",
          borderRadius: "10px",
          overflow: "hidden"
        }}
      >
        <ForceGraph2D
          graphData={graphData}
          width={1000}
          height={600}

          backgroundColor="#ffffff"

          nodeLabel={(node) => `
          ${node.label}
          Type : ${node.type}
          Followers : ${node.followers ?? "-"}
          Engagement : ${node.engagement ?? "-"}
          Influence : ${node.influence ?? "-"}
          `}

          nodeCanvasObject={(node, ctx, globalScale) => {

            const label = node.label || node.id;

            const fontSize = 12 / globalScale;

            // Node Circle
            ctx.beginPath();
            ctx.arc(node.x, node.y, node.size, 0, 2 * Math.PI);
            ctx.fillStyle = node.color;
            ctx.fill();

            // Border
            ctx.strokeStyle = "#111827";
            ctx.lineWidth = 1.5;
            ctx.stroke();

            // Label
            ctx.font = `${fontSize}px Sans-Serif`;
            ctx.fillStyle = "#111827";
            ctx.fillText(
              label,
              node.x + node.size + 4,
              node.y + 4
            );
          }}

          // Links
          linkDirectionalArrowLength={6}
          linkDirectionalArrowRelPos={1}

          linkColor={() => "#9ca3af"}

          linkWidth={1.5}

          cooldownTicks={120}

          d3VelocityDecay={0.4}

          d3AlphaDecay={0.03}

          d3Force={(fg) => {
            fg.d3Force("charge").strength(-300);
            fg.d3Force("link").distance(120);
          }}

          enableNodeDrag={true}
          enablePanInteraction={true}
          enableZoomInteraction={true}
        />
      </div>

      {/* Legend */}

      <div
        style={{
          display: "flex",
          gap: "20px",
          marginTop: "20px",
          flexWrap: "wrap"
        }}
      >
        <span>🔴 Source</span>

        <span>🔵 User</span>

        <span>🟢 Influencer (Coming Next)</span>

        <span>🟣 Community (Coming Next)</span>
      </div>
    </div>
  );
};

export default GraphView;
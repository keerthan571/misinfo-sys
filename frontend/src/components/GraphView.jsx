import React, {
  useMemo,
  useRef,
  useState,
  useEffect,
} from "react";
import ForceGraph2D from "react-force-graph-2d";
import "./GraphView.css";

const TYPE_CONFIG = {
  source: {
    color: "#ef4444",
    size: 18,
    icon: "📢",
  },
  influencer: {
    color: "#f59e0b",
    size: 14,
    icon: "⭐",
  },
  user: {
    color: "#2563eb",
    size: 10,
    icon: "👤",
  },
};

const COMMUNITY_COLORS = [
  "#3b82f6",
  "#10b981",
  "#8b5cf6",
  "#f59e0b",
  "#ef4444",
  "#14b8a6",
  "#ec4899",
  "#6366f1",
];

const EDGE_COLORS = {
  publish: "#ef4444",
  share: "#3b82f6",
  cascade: "#9ca3af",
  bridge: "#8b5cf6",
  bot: "#f97316",
};

function GraphView({ data }) {
  const graphRef = useRef(null);
  const containerRef = useRef(null);

  const [selectedNode, setSelectedNode] =
    useState(null);

  const [graphSize, setGraphSize] =
    useState({
      width: 1200,
      height: 700,
    });

  useEffect(() => {
    function resize() {
      if (!containerRef.current) return;

      setGraphSize({
        width:
          containerRef.current.offsetWidth,
        height: 700,
      });
    }

    resize();

    window.addEventListener(
      "resize",
      resize
    );

    return () =>
      window.removeEventListener(
        "resize",
        resize
      );
  }, []);

  const graphData = useMemo(() => {
    if (!data?.nodes || !data?.edges) {
      return {
        nodes: [],
        links: [],
      };
    }

    const nodes = data.nodes.map((node) => {
      const config =
        TYPE_CONFIG[node.type] ??
        TYPE_CONFIG.user;

      const followers =
        node.followers || 0;

      const radius = Math.max(
        config.size,
        Math.min(
          28,
          Math.sqrt(followers) / 12
        )
      );

      return {
        ...node,
        radius,
        color: config.color,
        communityColor:
          COMMUNITY_COLORS[
            (node.community || 0) %
              COMMUNITY_COLORS.length
          ],
      };
    });

    const links = data.edges.map(
      (edge) => ({
        ...edge,
        color:
          EDGE_COLORS[
            edge.interaction
          ] || "#9ca3af",
      })
    );

    return {
      nodes,
      links,
    };
  }, [data]);

  const statistics =
    data?.statistics || {};

  if (graphData.nodes.length === 0) {
    return (
      <div className="graph-card">
        <h2>Propagation Graph</h2>

        <p>
          No graph data available.
        </p>
      </div>
    );
  }

  return (
    <div className="graph-card">

      <div className="graph-header">

        <div>

          <h2>
            AI Misinformation
            Propagation Graph
          </h2>

          <p>
            Nodes :
            {" "}
            {graphData.nodes.length}

            {" | "}

            Edges :
            {" "}
            {graphData.links.length}
          </p>

        </div>

        <div className="graph-summary">

          <span>
            👑 Leaders :
            {" "}
            {statistics.leaders || 0}
          </span>

          <span>
            🤖 Bots :
            {" "}
            {statistics.bots || 0}
          </span>

          <span>
            🔥 Viral :
            {" "}
            {statistics.viral_nodes || 0}
          </span>

        </div>

      </div>

      <div
        ref={containerRef}
        className="graph-container"
      >
      <ForceGraph2D
        ref={graphRef}
        width={graphSize.width}
        height={graphSize.height}
        graphData={graphData}
        backgroundColor="#ffffff"
        autoPauseRedraw={false}
        warmupTicks={100}
        cooldownTicks={200}
        cooldownTime={4000}
        enableNodeDrag
        enableZoomInteraction
        enablePanInteraction
        nodeRelSize={6}
        nodeLabel={(node) => `
      ${node.label}

      Type : ${node.type}
      Followers : ${node.followers}
      Leader : ${node.leader ? "Yes" : "No"}
      Bot : ${node.bot ? "Yes" : "No"}
      Viral : ${node.viral ? "Yes" : "No"}
      Community : ${node.community}
      `}
        onNodeClick={(node) => {
          setSelectedNode(node);
        }}
        onNodeHover={(node) => {
          document.body.style.cursor =
            node ? "pointer" : "default";
        }}
        nodeCanvasObject={(
          node,
          ctx,
          globalScale
        ) => {
          const fontSize = 12 / globalScale;

          if (node.viral) {
            ctx.beginPath();
            ctx.arc(
              node.x,
              node.y,
              node.radius + 5,
              0,
              2 * Math.PI
            );
            ctx.strokeStyle = "#ef4444";
            ctx.lineWidth = 2;
            ctx.stroke();
          }

          ctx.beginPath();
          ctx.arc(
            node.x,
            node.y,
            node.radius,
            0,
            2 * Math.PI
          );

          ctx.fillStyle = node.color;
          ctx.fill();

          ctx.lineWidth = 3;
          ctx.strokeStyle =
            node.communityColor;
          ctx.stroke();

          if (node.leader) {
            ctx.font = `${
              16 / globalScale
            }px Arial`;

            ctx.fillText(
              "👑",
              node.x - 8,
              node.y - node.radius - 5
            );
          }

          if (node.bot) {
            ctx.font = `${
              14 / globalScale
            }px Arial`;

            ctx.fillText(
              "🤖",
              node.x + node.radius,
              node.y - node.radius
            );
          }

          if (globalScale > 1.5) {
            ctx.font = `${fontSize}px Sans-Serif`;
            ctx.fillStyle = "#111827";

            ctx.fillText(
              node.label,
              node.x + node.radius + 5,
              node.y + 4
            );
          }
        }}
        linkColor={(link) =>
          link.color
        }
        linkWidth={(link) =>
          Math.max(
            1,
            (link.weight || 1) * 3
          )
        }
        linkDirectionalArrowLength={6}
        linkDirectionalArrowRelPos={1}
        d3VelocityDecay={0.4}
        d3AlphaDecay={0.03}
        d3Force={(fg) => {
          fg
            .d3Force("charge")
            .strength(-350);

          fg
            .d3Force("link")
            .distance(120);

          fg
            .d3Force("center")
            .strength(0.2);
        }}
      />
            </div>

      <div className="graph-bottom">

        <div className="graph-legend">

          <h3>Legend</h3>

          <div className="legend-grid">

            <div className="legend-item">
              <span
                className="legend-dot"
                style={{ background: "#ef4444" }}
              />
              Source
            </div>

            <div className="legend-item">
              <span
                className="legend-dot"
                style={{ background: "#f59e0b" }}
              />
              Influencer
            </div>

            <div className="legend-item">
              <span
                className="legend-dot"
                style={{ background: "#2563eb" }}
              />
              User
            </div>

            <div className="legend-item">
              👑 Leader
            </div>

            <div className="legend-item">
              🤖 Bot
            </div>

            <div className="legend-item">
              🔥 Viral
            </div>

          </div>

        </div>

        <div className="graph-stats">

          <h3>Statistics</h3>

          <div className="stats-grid">

            <div className="stat-card">
              <h4>Total Nodes</h4>
              <p>{statistics.node_count}</p>
            </div>

            <div className="stat-card">
              <h4>Total Edges</h4>
              <p>{statistics.edge_count}</p>
            </div>

            <div className="stat-card">
              <h4>Density</h4>
              <p>{statistics.density}</p>
            </div>

            <div className="stat-card">
              <h4>Communities</h4>
              <p>
                {data.communities?.communities?.length || 0}
              </p>
            </div>

          </div>

        </div>

      </div>

      {selectedNode && (

        <div className="node-panel">

          <div className="node-header">

            <h3>
              {selectedNode.label}
            </h3>

            <button
              onClick={() =>
                setSelectedNode(null)
              }
            >
              ✖
            </button>

          </div>

          <table>

            <tbody>

              <tr>
                <td>Type</td>
                <td>{selectedNode.type}</td>
              </tr>

              <tr>
                <td>Followers</td>
                <td>{selectedNode.followers}</td>
              </tr>

              <tr>
                <td>Community</td>
                <td>{selectedNode.community}</td>
              </tr>

              <tr>
                <td>Leader</td>
                <td>
                  {selectedNode.leader
                    ? "Yes"
                    : "No"}
                </td>
              </tr>

              <tr>
                <td>Bot</td>
                <td>
                  {selectedNode.bot
                    ? "Yes"
                    : "No"}
                </td>
              </tr>

              <tr>
                <td>Viral</td>
                <td>
                  {selectedNode.viral
                    ? "Yes"
                    : "No"}
                </td>
              </tr>

            </tbody>

          </table>

        </div>

      )}

    </div>
  );
}

export default GraphView;
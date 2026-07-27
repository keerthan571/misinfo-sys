import { Handle, Position } from "reactflow";
import "./GraphNode.css";

const TYPE_ICON = {
  origin: "📢",
  influencer: "⭐",
  media: "📰",
  user: "👤",
  bot: "🤖",
};

export default function GraphNode({ data }) {
  const {
    label,
    type,
    followers,
    influenceScore,
    shareProbability,
    verified,
    cluster,
  } = data;

  return (
    <>
      <Handle type="target" position={Position.Top} />

      <div className={`graph-node ${type}`}>
        <div className="graph-node-header">
          <span className="graph-node-icon">
            {TYPE_ICON[type] || "👤"}
          </span>

          <span className="graph-node-title">
            {label}
          </span>

          {verified && (
            <span className="verified">✔</span>
          )}
        </div>

        <div className="graph-node-body">
          <div>
            <strong>Followers</strong>
            <span>{followers}</span>
          </div>

          <div>
            <strong>Influence</strong>
            <span>{influenceScore}</span>
          </div>

          <div>
            <strong>Share %</strong>
            <span>
              {Math.round(
                shareProbability * 100
              )}
              %
            </span>
          </div>

          <div>
            <strong>Cluster</strong>
            <span>{cluster}</span>
          </div>
        </div>
      </div>

      <Handle
        type="source"
        position={Position.Bottom}
      />
    </>
  );
}
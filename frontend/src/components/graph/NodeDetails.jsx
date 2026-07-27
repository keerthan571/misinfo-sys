import React from "react";
import "./NodeDetails.css";

const NodeDetails = ({ node }) => {
  if (!node) {
    return (
      <div className="node-details">
        <div className="node-title">
          🖱 Select a Node
        </div>

        <div className="node-empty">
          Click any node in the graph to view its details.
        </div>
      </div>
    );
  }

  return (
    <div className="node-details">
      <div className="node-title">
        {node.icon} {node.label}
      </div>

      <div className="node-card">
        <span>Type</span>
        <strong>{node.type}</strong>
      </div>

      <div className="node-card">
        <span>Followers</span>
        <strong>{node.followers ?? "-"}</strong>
      </div>

      <div className="node-card">
        <span>Influence</span>
        <strong>{node.influenceScore ?? node.influence ?? "-"}</strong>
      </div>

      <div className="node-card">
        <span>Engagement</span>
        <strong>{node.engagement ?? "-"}</strong>
      </div>

      <div className="node-card">
        <span>Cluster</span>
        <strong>{node.cluster ?? "-"}</strong>
      </div>

      <div className="node-card">
        <span>Verified</span>
        <strong>{node.verified ? "✔ Yes" : "✖ No"}</strong>
      </div>

      <div className="node-card">
        <span>Share Probability</span>
        <strong>
          {node.shareProbability
            ? `${Math.round(node.shareProbability * 100)}%`
            : "-"}
        </strong>
      </div>

      <div className="node-card">
        <span>Parent</span>
        <strong>{node.parentId ?? "-"}</strong>
      </div>

      <div className="node-card">
        <span>Children</span>
        <strong>{node.children ?? "-"}</strong>
      </div>
    </div>
  );
};

export default NodeDetails;
import React from "react";
import "./AnalyticsPanel.css";

const AnalyticsPanel = ({ analytics = {}, nodes = [], edges = [] }) => {
  return (
    <div className="analytics-panel">
      <div className="analytics-title">
        📊 AI Analytics
      </div>

      <div className="analytics-card">
        <div className="analytics-label">
          Total Nodes
        </div>

        <div className="analytics-value">
          {nodes.length}
        </div>
      </div>

      <div className="analytics-card">
        <div className="analytics-label">
          Total Edges
        </div>

        <div className="analytics-value">
          {edges.length}
        </div>
      </div>

      <div className="analytics-card">
        <div className="analytics-label">
          Average Influence
        </div>

        <div className="analytics-value">
          {analytics.averageInfluence ?? "-"}
        </div>
      </div>

      <div className="analytics-card">
        <div className="analytics-label">
          Highest Influence
        </div>

        <div className="analytics-value">
          {analytics.highestInfluence ?? "-"}
        </div>
      </div>

      <div className="analytics-card">
        <div className="analytics-label">
          Average PageRank
        </div>

        <div className="analytics-value">
          {analytics.averagePageRank ?? "-"}
        </div>
      </div>

      <div className="analytics-card">
        <div className="analytics-label">
          Top Influencer
        </div>

        <div className="analytics-value">
          {analytics.topInfluencer ?? "-"}
        </div>
      </div>
    </div>
  );
};

export default AnalyticsPanel;
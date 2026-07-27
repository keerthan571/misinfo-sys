import React from "react";
import "./GraphLegend.css";

const legendItems = [
  {
    color: "#ef4444",
    label: "Source",
    icon: "📢",
  },
  {
    color: "#2563eb",
    label: "User",
    icon: "👤",
  },
  {
    color: "#10b981",
    label: "Media",
    icon: "📰",
  },
  {
    color: "#f59e0b",
    label: "Influencer",
    icon: "⭐",
  },
  {
    color: "#6b7280",
    label: "Bot",
    icon: "🤖",
  },
];

const GraphLegend = () => {
  return (
    <div className="graph-legend">

      <h3>Graph Legend</h3>

      {legendItems.map((item) => (
        <div
          key={item.label}
          className="legend-item"
        >
          <div
            className="legend-color"
            style={{
              background: item.color,
            }}
          />

          <span className="legend-icon">
            {item.icon}
          </span>

          <span className="legend-label">
            {item.label}
          </span>
        </div>
      ))}
    </div>
  );
};

export default GraphLegend;
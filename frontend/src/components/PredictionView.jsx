import React from "react";

const getRiskColor = (risk) => {
  switch (risk) {
    case "Critical":
      return "#dc2626";
    case "High":
      return "#ea580c";
    case "Moderate":
      return "#ca8a04";
    default:
      return "#16a34a";
  }
};

const PredictionView = ({ data }) => {
  if (!data) return null;

  return (
    <div className="prediction-card">
      <h2>Spread Prediction Analysis</h2>

      <div className="metric-box">
        <h3>Predicted Reach</h3>
        <p>{data.predicted_reach} users</p>
      </div>

      <div className="metric-box">
        <h3>Risk Level</h3>

        <span
          style={{
            backgroundColor: getRiskColor(data.risk_level),
            color: "white",
            padding: "6px 12px",
            borderRadius: "20px",
            fontWeight: "bold"
          }}
        >
          {data.risk_level}
        </span>
      </div>

      <div className="metric-box">
        <h3>Confidence Score</h3>
        <p>{data.confidence}%</p>

        <div className="progress-container">
          <div
            className="progress-bar"
            style={{
              width: `${data.confidence}%`
            }}
          />
        </div>
      </div>

      <div className="metric-box">
        <h3>Virality Score</h3>
        <p>{data.virality_score}%</p>
      </div>

      <div className="metric-box">
        <h3>Why This Prediction?</h3>

        <ul>
          {data.reasons.map((reason, index) => (
            <li key={index}>✓ {reason}</li>
          ))}
        </ul>
      </div>

      <div className="chart-placeholder">
        Recharts Virality Chart Here
      </div>
    </div>
  );
};

export default PredictionView;
import React from "react";

const AnalyticsSummary = ({
  prediction,
  influencers
}) => {

  if (!prediction) return null;

  const topInfluencer =
    influencers?.top_influencers?.[0]?.name || "N/A";

  return (
    <div className="analytics-grid">

      <div className="analytics-card">
        <h4>Predicted Reach</h4>
        <h2>
          {Math.round(
            prediction.predicted_reach
          ).toLocaleString()}
        </h2>
      </div>

      <div className="analytics-card">
        <h4>Risk Level</h4>
        <h2>
          {prediction.risk_level}
        </h2>
      </div>

      <div className="analytics-card">
        <h4>Confidence</h4>
        <h2>
          {prediction.confidence}%
        </h2>
      </div>

      <div className="analytics-card">
        <h4>Top Influencer</h4>
        <h2>
          {topInfluencer}
        </h2>
      </div>

    </div>
  );
};

export default AnalyticsSummary;
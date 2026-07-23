import React from "react";

const getCategoryColor = (category) => {
  switch (category) {
    case "Mega Influencer":
      return "#dc2626";

    case "Strong Influencer":
      return "#ea580c";

    case "Active User":
      return "#2563eb";

    default:
      return "#16a34a";
  }
};

const InfluencerCard = ({ influencer }) => {
  return (
    <div className="influencer-card">

      <h3>{influencer.name}</h3>

      <div className="metric-row">
        <span>Score</span>
        <strong>{influencer.influence_score}</strong>
      </div>

      <div className="metric-row">
        <span>Followers</span>
        <strong>{influencer.followers}</strong>
      </div>

      <div className="metric-row">
        <span>Connections</span>
        <strong>{influencer.connections}</strong>
      </div>

      <span
        style={{
          backgroundColor: getCategoryColor(
            influencer.category
          ),
          color: "white",
          padding: "5px 10px",
          borderRadius: "20px",
          fontSize: "0.8rem"
        }}
      >
        {influencer.category}
      </span>

    </div>
  );
};

export default InfluencerCard;
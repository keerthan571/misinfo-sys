import React from "react";
import InfluencerCard from "./InfluencerCard";

const InfluencerList = ({ data }) => {

  if (!data || !data.top_influencers) {
    return null;
  }

  return (
    <div>
      <h2>Top Influencers</h2>

      <div className="influencer-grid">
        {data.top_influencers.map((influencer) => (
          <InfluencerCard
            key={influencer.user_id}
            influencer={influencer}
          />
        ))}
      </div>
    </div>
  );
};

export default InfluencerList;
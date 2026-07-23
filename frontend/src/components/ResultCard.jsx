import React from "react";

const ResultCard = ({ title, children }) => {
  return (
    <div className="result-card">
      <div className="result-card-header">
        <h2>{title}</h2>
      </div>

      <div className="result-card-content">
        {children}
      </div>
    </div>
  );
};

export default ResultCard;
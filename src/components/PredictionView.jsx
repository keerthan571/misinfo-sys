import React from 'react';

const PredictionView = ({ data }) => {
  if (!data) return null;

  return (
    <div className="card">
      <h2>Spread Prediction</h2>
      <div className="result-item">
        <strong>Predicted Reach:</strong> {data.predicted_reach} users
      </div>
      <div className="result-item">
        <strong>Risk Level:</strong> 
        <span style={{ 
          color: data.risk_level === 'High' ? 'red' : 'green',
          fontWeight: 'bold',
          marginLeft: '5px'
        }}>
          {data.risk_level}
        </span>
      </div>
      
      {/* Placeholder for Chart.js or Recharts */}
      <div className="chart-placeholder">
        [ Bar Chart Placeholder ]<br/>
        Integrate Recharts here.
      </div>
    </div>
  );
};

export default PredictionView;

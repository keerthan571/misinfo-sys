import React from 'react';

const ResultCard = ({ title, data }) => {
  if (!data) return null;

  return (
    <div className="card">
      <h2>{title}</h2>
      {Object.entries(data).map(([key, value]) => {
        if (typeof value === 'object' && value !== null) {
          // Simplistic rendering for nested objects/arrays
          return (
            <div key={key} className="result-item">
              <strong>{key}:</strong> 
              <pre style={{ fontSize: '0.8rem', margin: '0.5rem 0 0' }}>
                {JSON.stringify(value, null, 2)}
              </pre>
            </div>
          );
        }
        return (
          <div key={key} className="result-item">
            <strong>{key}:</strong> {String(value)}
          </div>
        );
      })}
    </div>
  );
};

export default ResultCard;

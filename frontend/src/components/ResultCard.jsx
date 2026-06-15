import React from 'react';

const ResultCard = ({ title, data }) => {
  if (!data) return null;

  const renderValue = (value) => {
    // 🔥 Handle arrays
    if (Array.isArray(value)) {
      return (
        <ul>
          {value.map((item, index) => (
            <li key={index}>
              {typeof item === 'object'
                ? JSON.stringify(item, null, 2) // safe rendering
                : String(item)}
            </li>
          ))}
        </ul>
      );
    }

    // 🔥 Handle objects
    if (typeof value === 'object' && value !== null) {
      return (
        <pre style={{ fontSize: '0.8rem', marginTop: '5px' }}>
          {JSON.stringify(value, null, 2)}
        </pre>
      );
    }

    // 🔥 Handle string/number
    return <span>{String(value)}</span>;
  };

  return (
    <div className="card">
      <h2>{title}</h2>

      {Object.entries(data).map(([key, value]) => (
        <div key={key} className="result-item" style={{ marginBottom: '10px' }}>
          <strong>{key}:</strong>
          <div>{renderValue(value)}</div>
        </div>
      ))}
    </div>
  );
};

export default ResultCard;
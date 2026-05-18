import React from 'react';

const GraphView = ({ data }) => {
  if (!data) return null;

  return (
    <div className="card">
      <h2>Propagation Graph</h2>
      <p style={{ fontSize: '0.9rem', color: '#6b7280' }}>
        Nodes: {data.nodes?.length} | Links: {data.links?.length}
      </p>
      
      {/* Placeholder for D3.js, Vis.js or react-force-graph */}
      <div className="graph-placeholder">
        [ Graph Visualization Placeholder ]<br/>
        Integrate react-force-graph here.
      </div>
    </div>
  );
};

export default GraphView;

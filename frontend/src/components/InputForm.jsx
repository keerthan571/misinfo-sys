import React, { useState } from 'react';

const InputForm = ({ onSubmit }) => {
  const [content, setContent] = useState('');
  const [reposts, setReposts] = useState(5);

  const handleClick = () => {
    if (!content.trim()) return;

    onSubmit({
      content,
      reposts: Number(reposts)
    });
  };

  return (
    <div className="card">
      <h2>Analyze Content</h2>

      <textarea
        rows="5"
        placeholder="Enter news or social media content..."
        value={content}
        onChange={(e) => setContent(e.target.value)}
      />

      <div style={{ marginTop: '10px' }}>
        <label>Reposts (simulate spread): </label>
        <input
          type="number"
          value={reposts}
          onChange={(e) => setReposts(e.target.value)}
          style={{ marginLeft: '10px' }}
        />
      </div>

      <button onClick={handleClick} style={{ marginTop: '15px' }}>
        Run Analysis Pipeline
      </button>
    </div>
  );
};

export default InputForm;
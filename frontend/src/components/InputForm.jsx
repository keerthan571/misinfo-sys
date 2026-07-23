import React, { useState } from 'react';

const InputForm = ({ onSubmit }) => {

  const [content, setContent] = useState('');
  const [reposts, setReposts] = useState(5);

  const [likes, setLikes] = useState(500);
  const [shares, setShares] = useState(150);
  const [comments, setComments] = useState(100);
  const [followers, setFollowers] = useState(8000);
  const [accountAge, setAccountAge] = useState(365);

  const handleClick = () => {

    if (!content.trim()) return;

    onSubmit({
      content,
      reposts: Number(reposts),

      likes: Number(likes),
      shares: Number(shares),
      comments: Number(comments),
      followers: Number(followers),
      accountAge: Number(accountAge)
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

      <div className="input-group">
        <label>Reposts</label>
        <input
          type="number"
          value={reposts}
          onChange={(e) => setReposts(e.target.value)}
        />
      </div>

      <div className="input-group">
        <label>Likes</label>
        <input
          type="number"
          value={likes}
          onChange={(e) => setLikes(e.target.value)}
        />
      </div>

      <div className="input-group">
        <label>Shares</label>
        <input
          type="number"
          value={shares}
          onChange={(e) => setShares(e.target.value)}
        />
      </div>

      <div className="input-group">
        <label>Comments</label>
        <input
          type="number"
          value={comments}
          onChange={(e) => setComments(e.target.value)}
        />
      </div>

      <div className="input-group">
        <label>Follower Count</label>
        <input
          type="number"
          value={followers}
          onChange={(e) => setFollowers(e.target.value)}
        />
      </div>

      <div className="input-group">
        <label>Account Age (Days)</label>
        <input
          type="number"
          value={accountAge}
          onChange={(e) => setAccountAge(e.target.value)}
        />
      </div>

      <button
        onClick={handleClick}
        style={{ marginTop: '15px' }}
      >
        Run Analysis Pipeline
      </button>

    </div>
  );
};

export default InputForm;
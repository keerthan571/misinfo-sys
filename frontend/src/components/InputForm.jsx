import React, { useState } from 'react';
import apiClient from '../api/apiClient';

const InputForm = ({ setNlpResult, setGraphData, setInfluenceData, setPredictionData }) => {
  const [text, setText] = useState('');
  const [loading, setLoading] = useState(false);

  const handleAnalyze = async () => {
    if (!text.trim()) return;
    setLoading(true);
    
    try {
      // 1. Detect Misinformation
      const detectRes = await apiClient.post('/detect/', { text });
      setNlpResult(detectRes.data);

      // 2. Fetch Graph Data (dummy)
      const graphRes = await apiClient.post('/graph/', { post_id: 'sample_123' });
      setGraphData(graphRes.data);

      // 3. Fetch Influence Data
      const influenceRes = await apiClient.post('/influence/', { topic: 'General' });
      setInfluenceData(influenceRes.data);

      // 4. Fetch Prediction
      const predictRes = await apiClient.post('/predict/', { 
        initial_likes: 150, 
        account_age_days: 30 
      });
      setPredictionData(predictRes.data);

    } catch (error) {
      console.error("API Error", error);
      alert("Error analyzing text. Is the backend running?");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="card">
      <h2>Analyze Content</h2>
      <div className="form-group">
        <textarea 
          rows="5" 
          placeholder="Paste news text or social media post here..."
          value={text}
          onChange={(e) => setText(e.target.value)}
        />
      </div>
      <button onClick={handleAnalyze} disabled={loading}>
        {loading ? 'Analyzing...' : 'Run Analysis Pipeline'}
      </button>
    </div>
  );
};

export default InputForm;

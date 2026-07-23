import React, { useState } from 'react';
import apiClient from '../api/apiClient';

const InputForm = ({
  setNlpResult,
  setGraphData,
  setInfluenceData,
  setPredictionData,
  setFactVerification
}) => {
  const [text, setText] = useState('');
  const [loading, setLoading] = useState(false);

  const handleAnalyze = async () => {
    if (!text.trim()) return;

    setLoading(true);

    try {
      // 1. ML Detection
      const detectRes = await apiClient.post('/detect/', { text });
      setNlpResult(detectRes.data);

      // 2. AI Fact Verification
      const factRes = await apiClient.post('/fact-verify/', {
        claim: text
      });
      setFactVerification(factRes.data);

      // 3. Graph Data
      const graphRes = await apiClient.post('/graph/', {
        post_id: 'sample_123'
      });
      setGraphData(graphRes.data);

      // 4. Influence Detection
      const influenceRes = await apiClient.post('/influence/', {
        topic: 'General'
      });
      setInfluenceData(influenceRes.data);

      // 5. Spread Prediction
      const predictRes = await apiClient.post('/predict/', {
        initial_likes: 150,
        account_age_days: 30
      });
      setPredictionData(predictRes.data);

    } catch (error) {
      console.error(error);
      alert("Error analyzing text.");
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
        {loading ? "Analyzing..." : "Run Analysis Pipeline"}
      </button>
    </div>
  );
};

export default InputForm;
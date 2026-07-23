import React, { useState } from 'react';
import InputForm from './components/InputForm';
import ResultCard from './components/ResultCard';
import GraphView from './components/GraphView';
import PredictionView from './components/PredictionView';
import InfluencerList from "./components/InfluencerList";
import AnalyticsSummary from "./components/AnalyticsSummary";
import './App.css';

function App() {
  const [nlpResult, setNlpResult] = useState(null);
  const [graphData, setGraphData] = useState(null);
  const [influenceData, setInfluenceData] = useState(null);
  const [predictionData, setPredictionData] = useState(null);

  const handleSubmit = async (inputData) => {
    try {
      // DETECT
      const nlpRes = await fetch("http://127.0.0.1:8000/api/detect/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          text: inputData.content
        })
      });
      const nlpData = await nlpRes.json();
      setNlpResult(nlpData);

      // GRAPH
      const graphRes = await fetch("http://127.0.0.1:8000/api/graph/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          content: inputData.content,
          reposts: inputData.reposts
        })
      });
      const graphData = await graphRes.json();
      setGraphData(graphData);

      // INFLUENCE
      const influenceRes = await fetch("http://127.0.0.1:8000/api/influence/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          topic: inputData.content
        })
      });
      const influenceData = await influenceRes.json();
      setInfluenceData(influenceData);

      // PREDICT
      const predictionRes = await fetch("http://127.0.0.1:8000/api/predict/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
        initial_likes: inputData.likes,
        initial_shares: inputData.shares,
        comments: inputData.comments,
        follower_count: inputData.followers,
        account_age_days: inputData.accountAge
      })
      });
      const predictionData = await predictionRes.json();
      setPredictionData(predictionData);

    } catch (error) {
      console.error("Error:", error);
      alert("Backend not responding correctly");
    }
  };

  return (
    <div className="app-container">
      <header>
        <h1>AI Misinformation Analysis System</h1>
        
      </header>

      <div className="main-content">
        <div className="left-panel">
          <InputForm onSubmit={handleSubmit} />
        </div>

        <div className="right-panel">
          <AnalyticsSummary
          prediction={predictionData?.prediction}
          influencers={influenceData}
         />
          <ResultCard title="NLP Detection Result">

          {nlpResult && (
            <div>
              <pre>
                {JSON.stringify(nlpResult, null, 2)}
              </pre>
            </div>
          )}

          </ResultCard>
          <PredictionView data={predictionData?.prediction} />
          <InfluencerList data={influenceData}/>
          <GraphView data={graphData} />
        </div>
      </div>
    </div>
  );
}

export default App;
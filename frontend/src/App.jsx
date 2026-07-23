<<<<<<< HEAD
import { BrowserRouter, Routes, Route } from "react-router-dom";

import Layout from "./components/layout/Layout";

import Dashboard from "./pages/Dashboard";
import Analyze from "./pages/Analyze";
import OCR from "./pages/OCR";
import Graph from "./pages/Graph";
import Prediction from "./pages/Prediction";
import History from "./pages/History";
import Settings from "./pages/Settings";

function App() {
  return (
    <BrowserRouter>
      <Layout>
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/analyze" element={<Analyze />} />
          <Route path="/ocr" element={<OCR />} />
          <Route path="/graph" element={<Graph />} />
          <Route path="/prediction" element={<Prediction />} />
          <Route path="/history" element={<History />} />
          <Route path="/settings" element={<Settings />} />
        </Routes>
      </Layout>
    </BrowserRouter>
=======
import React, { useState } from 'react';
import InputForm from './components/InputForm';
import ResultCard from './components/ResultCard';
import GraphView from './components/GraphView';
import PredictionView from './components/PredictionView';
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
          initial_likes: 100,
          account_age_days: 30
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
        <p className="subtitle">VTU Final Year Project</p>
      </header>

      <div className="main-content">
        <div className="left-panel">
          <InputForm onSubmit={handleSubmit} />
        </div>

        <div className="right-panel">
          <ResultCard title="NLP Detection Result" data={nlpResult} />
          <PredictionView data={predictionData} />
          <ResultCard title="Key Influencers" data={influenceData} />
          <GraphView data={graphData} />
        </div>
      </div>
    </div>
>>>>>>> 8b44c954ba4e4703454da20488ed0a29cac18568
  );
}

export default App;
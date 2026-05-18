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

  return (
    <div className="app-container">
      <header>
        <h1>AI Misinformation Analysis System</h1>
        <p className="subtitle">VTU Final Year Project Boilerplate</p>
      </header>

      <div className="main-content">
        <div className="left-panel">
          <InputForm 
            setNlpResult={setNlpResult} 
            setGraphData={setGraphData}
            setInfluenceData={setInfluenceData}
            setPredictionData={setPredictionData}
          />
        </div>
        
        <div className="right-panel">
          <ResultCard title="NLP Detection Result" data={nlpResult} />
          <PredictionView data={predictionData} />
          <ResultCard title="Key Influencers" data={influenceData} />
          <GraphView data={graphData} />
        </div>
      </div>
    </div>
  );
}

export default App;

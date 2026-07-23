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
  );
}

export default App;
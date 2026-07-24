import { BrowserRouter, Routes, Route } from "react-router-dom";

import Layout from "./components/layout/Layout";

import Dashboard from "./pages/Dashboard";
import Analyze from "./pages/Analyze";
import OCR from "./pages/OCR";
import Graph from "./pages/Graph";
import Prediction from "./pages/Prediction";
import History from "./pages/History";
import Settings from "./pages/Settings";
import Login from "./pages/Login";
import Signup from "./pages/Signup";
import ForgotPassword from "./pages/ForgotPassword";

function App() {
  return (
    <BrowserRouter>
      <Routes>

        {/* Authentication Pages (No Sidebar/Navbar) */}
        <Route path="/login" element={<Login />} />
        <Route path="/signup" element={<Signup />} />
        <Route path="/forgot-password" element={<ForgotPassword />} />
        {/* Main Application */}
        <Route
          path="/"
          element={
            <Layout>
              <Dashboard />
            </Layout>
          }
        />

        <Route
          path="/analyze"
          element={
            <Layout>
              <Analyze />
            </Layout>
          }
        />

        <Route
          path="/ocr"
          element={
            <Layout>
              <OCR />
            </Layout>
          }
        />

        <Route
          path="/graph"
          element={
            <Layout>
              <Graph />
            </Layout>
          }
        />

        <Route
          path="/prediction"
          element={
            <Layout>
              <Prediction />
            </Layout>
          }
        />

        <Route
          path="/history"
          element={
            <Layout>
              <History />
            </Layout>
          }
        />

        <Route
          path="/settings"
          element={
            <Layout>
              <Settings />
            </Layout>
          }
        />

      </Routes>
    </BrowserRouter>
  );
}

export default App;
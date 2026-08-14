import { BrowserRouter, Routes, Route } from "react-router-dom";

import Layout from "./components/layout/Layout";
import ProtectedRoute from "./components/auth/ProtectedRoute";

import Dashboard from "./pages/Dashboard";
import Analyze from "./pages/Analyze";
import Graph from "./pages/Graph";
import Prediction from "./pages/Prediction";
import EngagementVerification from "./pages/EngagementVerification";
import History from "./pages/History";
import HistoryDetails from "./pages/HistoryDetails";
import Settings from "./pages/Settings";

import Login from "./pages/Login";
import Signup from "./pages/Signup";
import ForgotPassword from "./pages/ForgotPassword";
import ResetPassword from "./pages/ResetPassword";

function App() {

  return (

    <BrowserRouter>

      <Routes>


        <Route
          path="/login"
          element={<Login />}
        />


        <Route
          path="/signup"
          element={<Signup />}
        />


        <Route
          path="/forgot-password"
          element={<ForgotPassword />}
        />

        <Route
          path="/reset-password"
          element={<ResetPassword />}
        />

        <Route
          path="/"
          element={
            <ProtectedRoute>
              <Layout>
                <Dashboard />
              </Layout>
            </ProtectedRoute>
          }
        />


        <Route
          path="/analyze"
          element={
            <ProtectedRoute>
              <Layout>
                <Analyze />
              </Layout>
            </ProtectedRoute>
          }
        />


        <Route
          path="/graph"
          element={
            <ProtectedRoute>
              <Layout>
                <Graph />
              </Layout>
            </ProtectedRoute>
          }
        />


        <Route
          path="/engagement-verification"
          element={
            <ProtectedRoute>
              <Layout>
                <EngagementVerification />
              </Layout>
            </ProtectedRoute>
          }
        />


        <Route
          path="/prediction"
          element={
            <ProtectedRoute>
              <Layout>
                <Prediction />
              </Layout>
            </ProtectedRoute>
          }
        />


        <Route
          path="/history"
          element={
            <ProtectedRoute>
              <Layout>
                <History />
              </Layout>
            </ProtectedRoute>
          }
        />

        <Route
          path="/history/:id"
          element={
            <ProtectedRoute>
              <Layout>
                <HistoryDetails />
              </Layout>
            </ProtectedRoute>
          }
        />


        <Route
          path="/settings"
          element={
            <ProtectedRoute>
              <Layout>
                <Settings />
              </Layout>
            </ProtectedRoute>
          }
        />


      </Routes>

    </BrowserRouter>

  );

}


export default App;
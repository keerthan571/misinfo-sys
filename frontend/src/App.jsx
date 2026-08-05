import { BrowserRouter, Routes, Route } from "react-router-dom";

import Layout from "./components/layout/Layout";
import ProtectedRoute from "./components/auth/ProtectedRoute";

import Dashboard from "./pages/Dashboard";
import Analyze from "./pages/Analyze";
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


        {/* Authentication Pages */}

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



        {/* Protected Pages */}


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
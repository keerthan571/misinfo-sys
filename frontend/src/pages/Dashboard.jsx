import { useNavigate } from "react-router-dom";
import Charts from "../components/dashboard/Charts";

export default function Dashboard() {
  const navigate = useNavigate();

  return (
    <div className="space-y-8">
      {/* Header */}
      <div>
        <h1 className="text-4xl font-bold text-white">Dashboard</h1>

        <p className="text-gray-400 mt-2">
          Welcome back! Here's an overview of your AI-powered misinformation
          analysis platform.
        </p>
      </div>

      {/* Statistics Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-6">

        <div className="bg-slate-800 rounded-2xl p-6 shadow-lg hover:scale-105 transition duration-300">
          <p className="text-gray-400 text-lg">📊 Total Analyses</p>
          <h2 className="text-4xl font-bold text-white mt-4">1245</h2>
          <p className="text-green-400 mt-2">+12% Today</p>
        </div>

        <div className="bg-slate-800 rounded-2xl p-6 shadow-lg hover:scale-105 transition duration-300">
          <p className="text-gray-400 text-lg">🚨 Fake News</p>
          <h2 className="text-4xl font-bold text-red-500 mt-4">412</h2>
          <p className="text-red-400 mt-2">High Detection Rate</p>
        </div>

        <div className="bg-slate-800 rounded-2xl p-6 shadow-lg hover:scale-105 transition duration-300">
          <p className="text-gray-400 text-lg">⚠ High Risk</p>
          <h2 className="text-4xl font-bold text-yellow-400 mt-4">23</h2>
          <p className="text-yellow-400 mt-2">Critical Posts</p>
        </div>

        <div className="bg-slate-800 rounded-2xl p-6 shadow-lg hover:scale-105 transition duration-300">
          <p className="text-gray-400 text-lg">👥 Influencers</p>
          <h2 className="text-4xl font-bold text-green-400 mt-4">87</h2>
          <p className="text-green-400 mt-2">Active Accounts</p>
        </div>

      </div>

      {/* Charts */}
      <Charts />

      {/* Recent Activity */}
      <div className="bg-slate-800 rounded-2xl p-6 shadow-lg">

        <h2 className="text-2xl font-bold text-white mb-4">
          📰 Recent Activity
        </h2>

        <div className="space-y-3">

          <div className="bg-slate-900 p-4 rounded-lg">
            🚨 Fake news detected in uploaded article
          </div>

          <div className="bg-slate-900 p-4 rounded-lg">
            📷 OCR analysis completed
          </div>

          <div className="bg-slate-900 p-4 rounded-lg">
            🌐 Propagation graph generated
          </div>

          <div className="bg-slate-900 p-4 rounded-lg">
            📈 Spread prediction completed
          </div>

        </div>

      </div>

      {/* Quick Actions */}
      <div>

        <h2 className="text-2xl font-bold text-white mb-4">
          ⚡ Quick Actions
        </h2>

        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-4">

          <button
            onClick={() => navigate("/analyze")}
            className="bg-blue-600 hover:bg-blue-700 rounded-xl py-4 font-semibold transition"
          >
            📰 Analyze News
          </button>

          <button
            onClick={() => navigate("/ocr")}
            className="bg-purple-600 hover:bg-purple-700 rounded-xl py-4 font-semibold transition"
          >
            📷 OCR Scanner
          </button>

          <button
            onClick={() => navigate("/graph")}
            className="bg-green-600 hover:bg-green-700 rounded-xl py-4 font-semibold transition"
          >
            🌐 View Graph
          </button>

          <button
            onClick={() => navigate("/prediction")}
            className="bg-red-600 hover:bg-red-700 rounded-xl py-4 font-semibold transition"
          >
            📈 Prediction
          </button>

        </div>

      </div>

    </div>
  );
}
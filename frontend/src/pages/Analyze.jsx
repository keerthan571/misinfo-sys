import { useState } from "react";
import apiClient from "../api/apiClient";

export default function Analyze() {
  const [news, setNews] = useState("");
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleAnalyze = async () => {
    if (!news.trim()) {
      alert("Please enter some news text.");
      return;
    }

    setLoading(true);
    setError("");
    setResult(null);

    try {
      const response = await apiClient.post("/api/detect/", {
        text: news,
      });

      setResult(response.data);
    } catch (err) {
      console.error(err);
      setError("Unable to connect to backend.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-8">

      {/* Header */}
      <div>
        <h1 className="text-4xl font-bold text-white">
          Analyze News
        </h1>

        <p className="text-gray-400 mt-2">
          Enter a news article or upload an image to detect misinformation.
        </p>
      </div>

      {/* Input Section */}
      <div className="bg-slate-800 rounded-2xl p-6 shadow-lg">

        <label className="text-white font-semibold">
          News Text
        </label>

        <textarea
          rows="8"
          value={news}
          onChange={(e) => setNews(e.target.value)}
          placeholder="Paste your news article here..."
          className="w-full mt-4 bg-slate-900 rounded-xl p-4 text-white outline-none resize-none"
        />

        <div className="mt-6">

          <label className="text-white font-semibold">
            Upload Screenshot (OCR)
          </label>

          <input
            type="file"
            className="block mt-3 text-white"
          />

        </div>

        <button
          onClick={handleAnalyze}
          disabled={loading}
          className="mt-6 bg-blue-600 hover:bg-blue-700 px-8 py-3 rounded-xl font-bold disabled:opacity-50"
        >
          {loading ? "Analyzing..." : "Analyze"}
        </button>

      </div>

      {/* Error */}
      {error && (
        <div className="bg-red-500 text-white rounded-xl p-4">
          {error}
        </div>
      )}

      {/* Result */}
      {result && (
        <div className="bg-slate-800 rounded-2xl p-6 shadow-lg">

          <h2 className="text-3xl font-bold text-white mb-6">
            AI Analysis Result
          </h2>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">

            {/* Prediction */}
            <div className="bg-slate-900 rounded-xl p-6">

              <p className="text-gray-400">
                Prediction
              </p>

              <h2
                className={`text-4xl font-bold mt-4 ${
                  result.prediction.toLowerCase() === "fake"
                    ? "text-red-500"
                    : "text-green-500"
                }`}
              >
                {result.prediction}
              </h2>

            </div>

            {/* Confidence */}
            <div className="bg-slate-900 rounded-xl p-6">

              <p className="text-gray-400">
                Confidence
              </p>

              <h2 className="text-4xl font-bold text-blue-400 mt-4">
                {Number(result.confidence).toFixed(2)}%
              </h2>

            </div>

            {/* Risk */}
            <div className="bg-slate-900 rounded-xl p-6">

              <p className="text-gray-400">
                Risk Level
              </p>

              <h2
                className={`text-4xl font-bold mt-4 ${
                  result.prediction.toLowerCase() === "fake"
                    ? "text-red-500"
                    : "text-green-500"
                }`}
              >
                {result.prediction.toLowerCase() === "fake"
                  ? "HIGH"
                  : "LOW"}
              </h2>

            </div>

          </div>

          {/* Text Analyzed */}
          <div className="mt-8">

            <h3 className="text-xl font-semibold text-white mb-3">
              Text Analyzed
            </h3>

            <div className="bg-slate-900 rounded-xl p-4 text-gray-300 leading-7">
              {result.text_analyzed}
            </div>

          </div>

        </div>
      )}

    </div>
  );
}
import { useState } from "react";
import apiClient from "../api/apiClient";
import { useNavigate } from "react-router-dom";

import AnalyzeInput from "../components/analyze/AnalyzeInput";
import DetectionCard from "../components/analyze/DetectionCard";
import FactVerificationCard from "../components/analyze/FactVerificationCard";
import OCRCard from "../components/analyze/OCRCard";
import PlatformCard from "../components/analyze/PlatformCard";
import SpreadPredictionCard from "../components/analyze/SpreadPredictionCard";


export default function Analyze() {

  const [news, setNews] = useState("");
  const [image, setImage] = useState(null);

  const [result, setResult] = useState(null);

  const [loading, setLoading] = useState(false);

  const [error, setError] = useState("");
  const navigate = useNavigate();
  const handleAnalyze = async () => {
    if (!news.trim() && !image) {
      setError(
        "Please enter news text or upload an image."
      );
      return;
    }
    try {
      setLoading(true);
      setError("");
      setResult(null);
      const formData = new FormData();
      if (news.trim()) {
        formData.append(
          "text",
          news
        );
      }
      if (image) {
        formData.append(
          "image",
          image
        );
      }
      const response = await apiClient.post(
        "/api/analyze/",
        formData,
        {
          headers:{
            "Content-Type":"multipart/form-data"
          }
        }
      );
      setResult(response.data);
      console.log(response);
      if (
        response.data?.analysis?.ocr?.extracted_text
        &&
        !news.trim()
      ){
        setNews(
          response.data.analysis.ocr.extracted_text
        );
      }
    }
    catch(err){
      console.error(err);
      setError(
        err.response?.data?.detail ||
        err.response?.data?.message ||
        "Analysis failed."
      );
    }
    finally{
      setLoading(false);
    }
  };
  
  const handleViewGraph = () => {

    if (!result?.analysis) {
        alert("Analysis data is not available.");
        return;
    }

    localStorage.setItem(
        "latestAnalysis",
        JSON.stringify(result.analysis)
    );

    navigate("/graph", {
        state: {
            analysis: result.analysis
        }
    });
  };

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-4xl font-bold text-white">
          Analyze News
        </h1>
        <p className="text-gray-400 mt-2">
          Upload news images or enter text.
          OCR extraction, misinformation detection and verification happen automatically.
        </p>
      </div>
      <AnalyzeInput

        news={news}

        setNews={setNews}

        image={image}

        setImage={setImage}

        loading={loading}

        onAnalyze={handleAnalyze}

      />

      {
        error && (
          <div className="bg-red-500 p-4 rounded-xl text-white">
            {error}
          </div>
        )
      }
      {
        result?.analysis && (
          <div className="space-y-6">
            {/* FINAL RESULT */}
              <div className="bg-slate-800 rounded-2xl shadow-lg p-6 text-white">
                <h2 className="text-3xl font-bold mb-5">
                  🧠 Final Analysis Result
                </h2>

                <p className="text-xl">
                  Prediction:
                  <span className="ml-3 font-bold text-red-400">
                    {result.analysis.final_result?.label}
                  </span>
                </p>

                <p className="text-xl mt-3">
                  Confidence:
                  <span className="ml-3 font-bold text-green-400">
                    {result.analysis.final_result?.confidence}%
                  </span>
                </p>

                <p className="text-xl mt-3">
                  Risk Level:
                  <span className="ml-3 font-bold text-yellow-400">
                    {result.analysis.final_result?.risk_level}
                  </span>
                </p>

                <p className="text-gray-300 mt-5">
                  {result.analysis.final_result?.summary}
                </p>
              </div>

              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">

                <OCRCard
                  data={result.analysis.ocr}
                />

                <PlatformCard
                  data={result.analysis.platform}
                />

                <DetectionCard
                  data={result.analysis.detection}
                />

                <FactVerificationCard
                  data={result.analysis.fact_verification}
                />

                <SpreadPredictionCard
                  data={{
                    ...result.analysis.prediction?.data,
                    analysis_summary:
                      result.analysis.prediction?.analysis_summary,
                  }}
                />

                {/* ENGAGEMENT */}
                <div className="bg-slate-800 rounded-2xl shadow-lg p-6 text-white">
                  <h2 className="text-2xl font-bold mb-5 text-white">
                    📊 Social Engagement Signals
                  </h2>

                  <p>
                    ❤️ Likes: {result.analysis.engagement?.likes ?? 0}
                  </p>

                  <p>
                    🔁 Shares: {result.analysis.engagement?.shares ?? 0}
                  </p>

                  <p>
                    👀 Views: {result.analysis.engagement?.views ?? 0}
                  </p>

                  <p>
                    🔖 Bookmarks: {result.analysis.engagement?.bookmarks ?? 0}
                  </p>
                </div>

                {/* SPREAD ANALYSIS */}
                <div className="bg-slate-800 rounded-2xl shadow-lg p-6 text-white">
                  <h2 className="text-2xl font-bold mb-5 text-white">
                    📈 Spread Factor Analysis
                  </h2>

                  <p>
                    Spread Score:
                    <span className="ml-2 font-bold text-green-400">
                      {result.analysis.spread_analysis?.metrics?.spread_score ?? 0}
                    </span>
                  </p>

                  <p className="mt-4 text-gray-300">
                    {result.analysis.spread_analysis?.summary ||
                      "No spread analysis available."}
                  </p>
                </div>

              </div>

              {/* VIEW GRAPH BUTTON (Only for OCR/Image Analysis) */}
              {image && result?.analysis && (
                <div className="flex justify-center">
                  <button
                    onClick={handleViewGraph}
                    className="bg-indigo-600 hover:bg-indigo-700 transition-all duration-200 text-white font-semibold px-8 py-3 rounded-xl shadow-lg"
                  >
                    🌐 View Propagation Graph
                  </button>
                </div>
              )}

            </div>
          )
      }
    </div>
  );
}
import { useState } from "react";
import apiClient from "../api/apiClient";

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

  const handleAnalyze = async () => {
    if (!news.trim()) {
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

      // Send the OCR extracted (or edited) text
      formData.append("text", news.trim());

      // Also send the original image if available
      if (image) {
        formData.append("image", image);
      }

      const { data } = await apiClient.post(
        "/api/analyze/",
        formData,
        {
          headers: {
            "Content-Type":
              "multipart/form-data",
          },
        }
      );

      setResult(data);
    } catch (err) {
      console.error(err);

      setError(
        err.response?.data?.detail ||
          err.response?.data?.message ||
          "Analysis failed."
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-4xl font-bold text-white">
          Analyze News
        </h1>

        <p className="text-gray-400 mt-2">
          Upload a news screenshot or enter text.
          OCR extracts the content automatically,
          after which misinformation detection,
          fact verification, spread prediction,
          and graph generation are performed.
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

      {error && (
        <div className="bg-red-500 rounded-xl p-4 text-white">
          {error}
        </div>
      )}

      {result?.analysis && (
                <div className="space-y-6">
          {/* Final Result */}
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

            <p className="mt-5 text-gray-300">
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
              data={
                result.analysis.fact_verification
              }
            />

            <SpreadPredictionCard
              data={result.analysis.prediction}
            />

            {/* Engagement */}
            <div className="bg-slate-800 rounded-2xl shadow-lg p-6 text-white">
              <h2 className="text-2xl font-bold mb-5">
                📊 Engagement Analysis
              </h2>

              <div className="space-y-3">
                <p>
                  ❤️ Likes:
                  <span className="ml-2 font-semibold">
                    {result.analysis.engagement?.likes ?? 0}
                  </span>
                </p>

                <p>
                  🔁 Shares:
                  <span className="ml-2 font-semibold">
                    {result.analysis.engagement?.shares ?? 0}
                  </span>
                </p>

                <p>
                  👀 Views:
                  <span className="ml-2 font-semibold">
                    {result.analysis.engagement?.views ?? 0}
                  </span>
                </p>

                <p>
                  🔖 Bookmarks:
                  <span className="ml-2 font-semibold">
                    {result.analysis.engagement?.bookmarks ?? 0}
                  </span>
                </p>
              </div>
            </div>

            {/* Spread Analysis */}
            <div className="bg-slate-800 rounded-2xl shadow-lg p-6 text-white">
              <h2 className="text-2xl font-bold mb-5">
                🚀 Spread Analysis
              </h2>

              <p>
                Spread Score:
                <span className="ml-2 font-bold text-green-400">
                  {
                    result.analysis
                      .spread_analysis?.metrics
                      ?.spread_score ?? 0
                  }
                </span>
              </p>

              <p className="mt-4 text-gray-300">
                {result.analysis.spread_analysis?.summary ??
                  "No spread analysis available."}
              </p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
import { useState } from "react";
import { useNavigate } from "react-router-dom";
import apiClient from "../api/apiClient";
import { useAnalysis } from "../context/AnalysisContext";

import AnalyzeInput from "../components/analyze/AnalyzeInput";
import DetectionCard from "../components/analyze/DetectionCard";
import FactVerificationCard from "../components/analyze/FactVerificationCard";

export default function Analyze() {
  const { analysisData, setAnalysisData } = useAnalysis();

  const [news, setNews] = useState(analysisData?.news || "");
  const [image, setImage] = useState(null);
  const [platform, setPlatform] = useState("");
  const [imagePreview, setImagePreview] = useState(analysisData?.imagePreview || null);
  const [result, setResult] = useState(analysisData?.result || null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const navigate = useNavigate();

  const handleAnalyze = async () => {
    if (!news.trim() && !image) {
      setError("Please enter news text or upload an image.");
      return;
    }

    if (!platform) {
      setError("Please select the platform.");
      return;
    }

    try {
      setLoading(true);
      setError("");
      setResult(null);

      const formData = new FormData();

      formData.append("platform", platform);

      if (news.trim()) {
        formData.append("text", news);
      }

      if (image) {
        formData.append("image", image);
      }

      const response = await apiClient.post(
        "/api/analyze/",
        formData,
        {
          headers: {
            "Content-Type": "multipart/form-data",
          },
        }
      );

      setResult(response.data);

      let preview = null;

      const savedImage = response.data?.analysis?.image?.path;

      if (savedImage) {
        preview = `http://127.0.0.1:8000/${savedImage.replace("\\", "/")}`;
        setImagePreview(preview);
      }

      setAnalysisData({
        result: response.data,
        imagePreview: preview,
        news,
        platform,
      });

      if (
        response.data?.analysis?.ocr?.extracted_text &&
        !news.trim()
      ) {
        setNews(response.data.analysis.ocr.extracted_text);
      }

    } catch (err) {
      setError(
        err.response?.data?.detail ||
        err.response?.data?.message ||
        "Analysis failed."
      );
    } finally {
      setLoading(false);
    }
  };

  const prediction =
    result?.analysis?.final_result?.label || "";

  const predictionColor = () => {
    const label = prediction.toLowerCase();

    if (
      label.includes("verified") ||
      label.includes("reliable")
    ) {
      return "text-green-400";
    }

    if (
      label.includes("false") ||
      label.includes("misinformation")
    ) {
      return "text-red-400";
    }

    if (
      label.includes("verification") ||
      label.includes("misleading")
    ) {
      return "text-yellow-400";
    }

    return "text-blue-400";
  };

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-4xl font-bold text-white">
          Analyze News
        </h1>

        <p className="text-gray-400 mt-2">
          Upload news images or enter text. OCR extraction,
          misinformation detection and verification happen automatically.
        </p>
      </div>

      <AnalyzeInput
        news={news}
        setNews={setNews}
        image={image}
        setImage={setImage}
        loading={loading}
        onAnalyze={handleAnalyze}
        platform={platform}
        setPlatform={setPlatform}
      />

      {error && (
        <div className="bg-red-500 p-4 rounded-xl text-white">
          {error}
        </div>
      )}

      {imagePreview && (
        <div className="bg-slate-800 rounded-2xl p-6">
          <h2 className="text-2xl font-bold text-white mb-4">
            🖼 Uploaded Image
          </h2>

          <img
            src={imagePreview}
            alt="Uploaded"
            className="rounded-xl max-h-96 mx-auto"
          />
        </div>
      )}

      {result?.analysis && (
        <div className="space-y-6">

          <div className="bg-slate-800 rounded-2xl shadow-lg p-6">

            <h2 className="text-3xl font-bold text-white mb-6">
              🧠 Final Analysis Result
            </h2>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">

              <div className="bg-slate-900 rounded-xl p-5">
                <p className="text-gray-400 text-sm mb-2">
                  Prediction
                </p>

                <p className={`text-lg font-bold ${predictionColor()}`}>
                  {result.analysis.final_result?.label}
                </p>
              </div>

              <div className="bg-slate-900 rounded-xl p-5">
                <p className="text-gray-400 text-sm mb-2">
                  Confidence
                </p>

                <p className="text-lg font-bold text-green-400">
                  {result.analysis.final_result?.confidence}%
                </p>
              </div>

              <div className="bg-slate-900 rounded-xl p-5">
                <p className="text-gray-400 text-sm mb-2">
                  Risk Level
                </p>

                <p className="text-lg font-bold text-yellow-400">
                  {result.analysis.final_result?.risk_level}
                </p>
              </div>

            </div>

            <div className="border-t border-slate-700 pt-5">

              <h3 className="text-lg font-semibold text-white mb-2">
                Summary
              </h3>

              <p className="text-gray-300 leading-7">
                {result.analysis.final_result?.summary}
              </p>

            </div>

          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">

            <DetectionCard
              data={result.analysis.detection}
            />

            <FactVerificationCard
              data={result.analysis.fact_verification}
            />

          </div>

          <div className="flex justify-center">

            <button
              className="bg-blue-600 hover:bg-blue-700 text-white font-bold px-8 py-4 rounded-xl shadow-lg"
              onClick={() => {
                console.log("FULL RESPONSE", result.analysis);

                navigate("/prediction", {
                  state: {
                    prediction:
                      result.analysis.prediction,

                    spread:
                      result.analysis.spread_analysis,

                    engagement: {
                      ...result.analysis.engagement,
                      platform: platform,
                    },
                  },
                });
              }}
            >
              🚀 View Spread Prediction
            </button>

          </div>

        </div>
      )}

    </div>
  );
}
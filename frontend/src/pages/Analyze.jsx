import { useState } from "react";
import apiClient from "../api/apiClient";

import AnalyzeInput from "../components/analyze/AnalyzeInput";
import DetectionCard from "../components/analyze/DetectionCard";
import FactVerificationCard from "../components/analyze/FactVerificationCard";
import OCRCard from "../components/analyze/OCRCard";
import SpreadPredictionCard from "../components/analyze/SpreadPredictionCard";

export default function Analyze() {
  const [news, setNews] = useState("");
  const [image, setImage] = useState(null);
  const [result, setResult] = useState(null);

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  // Temporary Mock Response
  const mockResult = {
    status: "success",
    analysis: {
      analysis_id: "7b970220-4979-48e4-be43-b85f5f98a4cc",
      analysis_time: "2026-07-24T18:10:42.862709+00:00",

      detection: {
        status: "success",
        prediction: "Fake",
        confidence: 95,
        reason:
          "NASA has not officially announced any discovery of life on Mars, and such a significant finding would be widely reported by credible sources.",
      },

      fact_verification: {
        status: "success",
        claim: "NASA discovered life on Mars yesterday.",
        verdict: "False",
        confidence: 100,
        reason:
          "NASA discovered a potential biosignature, not confirmed life.",
        sources: [
          "https://www.nasa.gov",
          "https://www.cnn.com",
        ],
      },

      ocr: {
        used: false,
        extracted_text: "",
        confidence: 0,
      },

      prediction: {
        status: "success",
        predicted_reach: 0,
        risk_level: "Low",
        virality_score: 0,
      },

      graph: {
        nodes: [],
        edges: [],
      },
    },
  };

  const handleAnalyze = async () => {
    if (!news.trim() && !image) {
      setError("Please enter news text or upload an image.");
      return;
    }

    setLoading(true);
    setError("");

    try {
      // ----------------------------------
      // TEMPORARY MOCK
      // ----------------------------------
      setTimeout(() => {
        setResult(mockResult);
        setLoading(false);
      }, 1000);

      /*
      // ----------------------------------
      // REAL API (Enable after backend merge)
      // ----------------------------------

      const formData = new FormData();

      if (news.trim()) {
        formData.append("text", news);
      }

      if (image) {
        formData.append("image", image);
      }

      const response = await apiClient.post(
        "/analyze/",
        formData,
        {
          headers: {
            "Content-Type": "multipart/form-data",
          },
        }
      );

      setResult(response.data);
      setLoading(false);
      */

    } catch (err) {
      console.error(err);

      if (err.response) {
        setError(err.response.data?.detail || "Analysis failed.");
      } else {
        setError("Unable to connect to backend.");
      }

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
          Paste news text or upload a news screenshot to detect misinformation.
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
        <div className="bg-red-500 p-4 rounded-xl text-white">
          {error}
        </div>
      )}

      {result && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">

          <DetectionCard
            data={result.analysis.detection}
          />

          <FactVerificationCard
            data={result.analysis.fact_verification}
          />

          <OCRCard
            data={result.analysis.ocr}
          />

          <SpreadPredictionCard
            data={result.analysis.prediction}
          />

        </div>
      )}

    </div>
  );
}
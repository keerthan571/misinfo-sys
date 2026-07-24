import { useState } from "react";
import apiClient from "../api/apiClient";

export default function Analyze() {
  const [news, setNews] = useState("");
  const [image, setImage] = useState(null);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleAnalyze = async () => {
    if (!news.trim() && !image) {
      alert("Please enter text or upload an image.");
      return;
    }

    setLoading(true);
    setError("");
    setResult(null);

    try {
      const formData = new FormData();

      formData.append("text", news);

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

      setResult(response.data.analysis);

    } catch (err) {
      console.error(err);
      setError("Unable to connect to backend.");
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
          Detect misinformation using AI, fact verification and OCR.
        </p>
      </div>


      {/* INPUT */}

      <div className="bg-slate-800 rounded-2xl p-6 shadow-lg">

        <label className="text-white font-semibold">
          News Text
        </label>

        <textarea
          rows="8"
          value={news}
          onChange={(e)=>setNews(e.target.value)}
          placeholder="Paste news article..."
          className="w-full mt-4 bg-slate-900 rounded-xl p-4 text-white"
        />


        <label className="text-white font-semibold block mt-6">
          Upload Image (OCR)
        </label>


        <input
          type="file"
          onChange={(e)=>setImage(e.target.files[0])}
          className="mt-3 text-white"
        />


        <button
          onClick={handleAnalyze}
          disabled={loading}
          className="mt-6 bg-blue-600 hover:bg-blue-700 px-8 py-3 rounded-xl font-bold"
        >
          {loading ? "Analyzing..." : "Analyze"}
        </button>

      </div>



      {error && (
        <div className="bg-red-500 p-4 rounded-xl text-white">
          {error}
        </div>
      )}



      {result && (

        <div className="space-y-6">


          {/* DETECTION */}

          <div className="bg-slate-800 rounded-2xl p-6">

            <h2 className="text-2xl font-bold text-white">
              AI Detection
            </h2>


            <p className="text-gray-400 mt-4">
              Prediction
            </p>

            <h3
              className={`text-4xl font-bold ${
                result.detection.prediction === "Fake"
                ? "text-red-500"
                : "text-green-500"
              }`}
            >
              {result.detection.prediction}
            </h3>


            <p className="text-gray-400 mt-4">
              Confidence
            </p>

            <h3 className="text-3xl text-blue-400 font-bold">
              {result.detection.confidence}%
            </h3>


            <p className="text-gray-300 mt-4">
              {result.detection.reason}
            </p>


          </div>



          {/* FACT CHECK */}

          <div className="bg-slate-800 rounded-2xl p-6">

            <h2 className="text-2xl font-bold text-white">
              Fact Verification
            </h2>


            <p className="text-gray-300 mt-4">
              Claim:
            </p>

            <p className="text-white">
              {result.fact_verification.claim}
            </p>


            <p className="text-gray-300 mt-4">
              Verdict:
            </p>

            <p className="text-red-400 font-bold">
              {result.fact_verification.verdict}
            </p>


            <p className="text-gray-300 mt-4">
              {result.fact_verification.reason}
            </p>


          </div>




          {/* OCR */}

          <div className="bg-slate-800 rounded-2xl p-6">

            <h2 className="text-2xl font-bold text-white">
              OCR Result
            </h2>


            <p className="text-gray-300 mt-4">
              Used: {result.ocr.used ? "Yes" : "No"}
            </p>


            <p className="text-white mt-3">
              {result.ocr.extracted_text}
            </p>


          </div>




          {/* PREDICTION */}

          <div className="bg-slate-800 rounded-2xl p-6">

            <h2 className="text-2xl font-bold text-white">
              Spread Prediction
            </h2>


            <p className="text-white mt-4">
              Risk Level: {result.prediction.risk_level}
            </p>


            <p className="text-white">
              Virality Score: {result.prediction.virality_score}
            </p>


          </div>


        </div>

      )}

    </div>
  );
}
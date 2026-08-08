import { useState } from "react";
import { useNavigate } from "react-router-dom";
import apiClient from "../api/apiClient";
import { useAnalysis } from "../context/AnalysisContext";

import AnalyzeInput from "../components/analyze/AnalyzeInput";
import DetectionCard from "../components/analyze/DetectionCard";
import FactVerificationCard from "../components/analyze/FactVerificationCard";

export default function Analyze() {
  const { analysis, setAnalysis } = useAnalysis();

  const [news, setNews] = useState(analysis?.news || "");

  const [image, setImage] = useState(null);

  const [platform, setPlatform] = useState(
    analysis?.platform || ""
  );

  const [followers, setFollowers] = useState("");

  const [ocrEngagement, setOcrEngagement] = useState({});

  const [imagePreview, setImagePreview] = useState(
    analysis?.imagePreview || null
  );

  const [result, setResult] = useState(
    analysis?.result || null
  );

  const [loading, setLoading] = useState(false);

  const [error, setError] = useState("");

  const navigate = useNavigate();

  /*
   * TEXT / GENERAL MODE
   */
  const isTextMode = platform === "Text";

  /*
   * SOCIAL MEDIA MODE
   *
   * An image is required for propagation analysis.
   */
  const isImageMode = Boolean(image);

  /*
   * COMPLETE SOCIAL ANALYSIS IS AVAILABLE ONLY WHEN:
   *
   * 1. An image exists
   * 2. Platform is not Text
   * 3. Analysis result exists
   */
  const hasSocialAnalysis =
    Boolean(
      result?.analysis &&
      isImageMode &&
      !isTextMode
    );

  const handleAnalyze = async () => {

    /*
     * At least text or image is required.
     */
    if (!news.trim() && !image) {
      setError(
        "Please enter news text or upload a social media screenshot."
      );
      return;
    }

    /*
     * Platform is mandatory.
     */
    if (!platform) {
      setError(
        "Please select the platform."
      );
      return;
    }

    /*
     * Text mode requires text.
     */
    if (
      isTextMode &&
      !news.trim()
    ) {
      setError(
        "Please enter text for Text / General analysis."
      );
      return;
    }

    /*
     * Social media analysis requires screenshot.
     */
    if (
      !isTextMode &&
      !image
    ) {
      setError(
        "Please upload a social media screenshot for complete analysis."
      );
      return;
    }

    try {

      setLoading(true);

      setError("");

      setResult(null);

      const formData =
        new FormData();

      /*
       * Platform
       */
      formData.append(
        "platform",
        platform
      );

      /*
       * Instagram followers
       */
      if (
        platform === "Instagram" &&
        followers
      ) {
        formData.append(
          "followers",
          followers
        );
      }

      /*
       * Text
       */
      if (news.trim()) {
        formData.append(
          "text",
          news
        );
      }

      /*
       * Image
       */
      if (image) {
        formData.append(
          "image",
          image
        );
      }

      /*
       * OCR engagement
       *
       * Text mode gets empty engagement values.
       */
      formData.append(
        "ocr_engagement",
        JSON.stringify(
          isTextMode
            ? {}
            : ocrEngagement
        )
      );

      const response =
        await apiClient.post(
          "/api/analyze/",
          formData,
          {
            headers: {
              "Content-Type":
                "multipart/form-data",
            },
          }
        );

      console.log(
        "FULL RESPONSE:",
        response
      );

      console.log(
        "RESPONSE DATA:",
        response.data
      );

      setResult(
        response.data
      );

      /*
       * Image preview
       */
      let preview = null;

      const savedImage =
        response.data
          ?.analysis
          ?.image
          ?.path;

      if (savedImage) {

        preview =
          `http://127.0.0.1:8000/${savedImage.replace(
            "\\",
            "/"
          )}`;

        setImagePreview(
          preview
        );

      } else {

        setImagePreview(null);

      }

      /*
       * Save to global analysis context.
       */
      setAnalysis({
        result:
          response.data,

        imagePreview:
          preview,

        news,

        platform,

        followers,
      });

      /*
       * If OCR/Vision extracted text,
       * populate text box only when
       * user did not manually enter text.
       */
      if (
        response.data
          ?.analysis
          ?.vision
          ?.post_text &&
        !news.trim()
      ) {

        setNews(
          response.data
            .analysis
            .vision
            .post_text
        );

      }

    } catch (err) {

      console.error(
        "ANALYSIS ERROR:",
        err
      );

      setError(
        err.response?.data?.detail ||
        err.response?.data?.message ||
        "Analysis failed."
      );

    } finally {

      setLoading(false);

    }
  };

  /*
   * Prediction label
   */
  const prediction =
    result
      ?.analysis
      ?.final_result
      ?.label || "";

  const predictionColor =
    () => {

      const label =
        prediction.toLowerCase();

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
    <div className="space-y-6">

      {/* =====================================================
          PAGE HEADER
      ===================================================== */}

      <div>

        <h1 className="text-4xl font-bold text-white">
          Analyze News
        </h1>

        <p className="text-gray-400 mt-2">
          Analyze news text for misinformation and
          fact verification, or upload a social media
          screenshot for complete propagation analysis.
        </p>

      </div>


      {/* =====================================================
          INPUT
      ===================================================== */}

      <AnalyzeInput
        news={news}
        setNews={setNews}

        image={image}
        setImage={setImage}

        loading={loading}
        onAnalyze={handleAnalyze}

        platform={platform}
        setPlatform={setPlatform}

        followers={followers}
        setFollowers={setFollowers}

        setOcrEngagement={
          setOcrEngagement
        }
      />


      {/* =====================================================
          ERROR
      ===================================================== */}

      {error && (
        <div className="bg-red-500/10 border border-red-500 rounded-xl p-4 text-red-300">
          {error}
        </div>
      )}


      {/* =====================================================
          UPLOADED IMAGE
      ===================================================== */}

      {imagePreview &&
        isImageMode && (
          <div className="bg-slate-800 rounded-2xl p-6">

            <h2 className="text-2xl font-bold text-white mb-4">
              🖼 Uploaded Image
            </h2>

            <img
              src={imagePreview}
              alt="Uploaded social media screenshot"
              className="rounded-xl max-h-96 mx-auto"
            />

          </div>
        )}


      {/* =====================================================
          ANALYSIS RESULTS
      ===================================================== */}

      {result?.analysis && (

        <div className="space-y-6">


          {/* =================================================
              FINAL RESULT
          ================================================= */}

          <div className="bg-slate-800 rounded-2xl shadow-lg p-6">

            <h2 className="text-3xl font-bold text-white mb-6">
              🧠 Analysis Result
            </h2>


            <div
              className={`grid grid-cols-1 ${
                isTextMode
                  ? "md:grid-cols-2"
                  : "md:grid-cols-3"
              } gap-4 mb-6`}
            >

              {/* Prediction */}

              <div className="bg-slate-900 rounded-xl p-5">

                <p className="text-gray-400 text-sm">
                  Prediction
                </p>

                <p
                  className={`text-lg font-bold ${predictionColor()}`}
                >
                  {
                    result
                      .analysis
                      .final_result
                      ?.label
                  }
                </p>

              </div>


              {/* Confidence */}

              <div className="bg-slate-900 rounded-xl p-5">

                <p className="text-gray-400 text-sm">
                  Confidence
                </p>

                <p className="text-lg font-bold text-green-400">
                  {
                    result
                      .analysis
                      .final_result
                      ?.confidence
                  }%
                </p>

              </div>


              {/* Risk only for social analysis */}

              {!isTextMode && (

                <div className="bg-slate-900 rounded-xl p-5">

                  <p className="text-gray-400 text-sm">
                    Risk Level
                  </p>

                  <p className="text-lg font-bold text-yellow-400">
                    {
                      result
                        .analysis
                        .final_result
                        ?.risk_level
                    }
                  </p>

                </div>

              )}

            </div>


            {/* Summary */}

            <div className="border-t border-slate-700 pt-5">

              <h3 className="text-lg font-semibold text-white">
                Summary
              </h3>

              <p className="text-gray-300 leading-7 mt-2">
                {
                  result
                    .analysis
                    .final_result
                    ?.summary
                }
              </p>

            </div>

          </div>


          {/* =================================================
              DETECTION + FACT VERIFICATION
          ================================================= */}

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">

            <DetectionCard
              data={
                result.analysis.detection
              }
            />

            <FactVerificationCard
              data={
                result.analysis
                  .fact_verification
              }
            />

          </div>


          {/* =================================================
              SOCIAL MEDIA ACTIONS
          ================================================= */}

          {hasSocialAnalysis && (

            <div className="flex justify-center gap-4 flex-wrap">


              {/* Engagement */}

              <button
                className="bg-blue-600 hover:bg-blue-700 text-white font-bold px-8 py-4 rounded-xl transition"
                onClick={() => {

                  navigate(
                    "/engagement-verification",
                    {
                      state: {
                        analysis: {
                          ...result.analysis,

                          engagement: {
                            ...result.analysis
                              .engagement,

                            followers:
                              Number(
                                followers
                              ) || 0,
                          },
                        },
                      },
                    }
                  );

                }}
              >
                📊 Verify Engagement Values
              </button>


              {/* Prediction */}

              <button
                className="bg-purple-600 hover:bg-purple-700 text-white font-bold px-8 py-4 rounded-xl transition"
                onClick={() => {

                  navigate(
                    "/prediction",
                    {
                      state: {
                        analysis:
                          result.analysis,
                      },
                    }
                  );

                }}
              >
                📈 View Spread Prediction
              </button>


              {/* Graph */}

              <button
                className="bg-cyan-600 hover:bg-cyan-700 text-white font-bold px-8 py-4 rounded-xl transition"
                onClick={() => {

                  navigate(
                    "/graph",
                    {
                      state: {
                        analysis:
                          result.analysis,
                      },
                    }
                  );

                }}
              >
                🕸 View Propagation Graph
              </button>

            </div>

          )}


          {/* =================================================
              TEXT ONLY INFORMATION
          ================================================= */}

          {isTextMode && (

            <div className="bg-slate-800 border border-slate-700 rounded-2xl p-6">

              <h3 className="text-lg font-bold text-white mb-2">
                📝 Text Analysis
              </h3>

              <p className="text-gray-400 text-sm leading-6">
                This analysis is based on the submitted
                text. Social-media engagement, spread
                prediction and propagation graph analysis
                are not generated because no social-media
                evidence was provided.
              </p>

            </div>

          )}

        </div>

      )}

    </div>
  );
}
import { useLocation, useNavigate } from "react-router-dom";
import { useAnalysis } from "../context/AnalysisContext";

export default function Prediction() {
  const navigate = useNavigate();

  const { state } = useLocation();

  const { analysis: contextAnalysis } = useAnalysis();

  const analysis =
    state?.analysis ||
    contextAnalysis?.result?.analysis ||
    null;

  /*
   * Prediction is available only for social-media
   * screenshot analysis.
   *
   * Text / General analysis must NOT show
   * spread prediction.
   */
  const platform =
    analysis?.platform?.platform ||
    analysis?.platform ||
    "";

  const isTextAnalysis =
    String(platform).toLowerCase() === "text";

  const hasSocialEvidence =
    Boolean(
      analysis?.image?.path ||
      analysis?.vision?.used
    );

  const hasSocialAnalysis =
    Boolean(
      analysis &&
      !isTextAnalysis &&
      hasSocialEvidence
    );

  /*
   * No valid social-media analysis
   */
  if (!hasSocialAnalysis) {
    return (
      <div className="min-h-[70vh] flex items-center justify-center">

        <div className="bg-slate-800 border border-slate-700 rounded-2xl p-12 text-center text-white max-w-2xl w-full">

          <div className="text-6xl mb-6">
            📊
          </div>

          <h2 className="text-3xl font-bold">
            No Spread Prediction Available
          </h2>

          <p className="text-gray-400 mt-4 leading-7">
            Spread prediction is available only for
            social-media screenshot analysis.
          </p>

          <p className="text-gray-500 mt-2 text-sm">
            Analyze an Instagram, Facebook or Twitter/X
            screenshot first to generate propagation
            and spread prediction results.
          </p>

          <button
            onClick={() => navigate("/analyze")}
            className="mt-8 bg-blue-600 hover:bg-blue-700 px-7 py-3 rounded-xl text-white font-semibold transition"
          >
            🔍 Go to Analyze
          </button>

        </div>

      </div>
    );
  }

  /*
   * Existing prediction data
   */
  const prediction =
    analysis.prediction?.data ||
    analysis.prediction ||
    {};

  const spread =
    analysis.spread_analysis ||
    {};

  const engagement =
    analysis.verified_engagement ||
    analysis.engagement ||
    {};

  const platformName =
    analysis.platform?.platform ||
    "Not Selected";

  const analysisSummary =
    analysis.prediction?.analysis_summary ||
    "";

  /*
   * Engagement metrics
   */
  const engagementMetrics =
    Object.entries(engagement)

      .filter(
        ([key, value]) =>
          key !== "metrics" &&
          key !== "followers" &&
          typeof value === "number" &&
          value > 0
      )

      .map(
        ([key, value]) => ({
          label:
            key.charAt(0).toUpperCase() +
            key.slice(1),

          value,
        })
      );

  /*
   * Predicted reach
   */
  const reach =
    prediction.predicted_reach
      ? Math.round(
          prediction.predicted_reach
        ).toLocaleString()
      : "Not Available";

  /*
   * Spread probability
   */
  const probability =
    prediction.spread_probability !==
      undefined &&
    prediction.spread_probability !== null
      ? `${prediction.spread_probability}%`
      : "Not Available";

  /*
   * Virality score
   */
  const virality =
    prediction.virality_score !==
      undefined &&
    prediction.virality_score !== null
      ? `${prediction.virality_score}%`
      : "Not Available";

  return (
    <div className="space-y-8">

      {/* =====================================================
          PAGE HEADER
      ===================================================== */}

      <div className="bg-slate-800 rounded-2xl p-6 text-white">

        <h1 className="text-4xl font-bold">
          🚀 Spread Prediction Analysis
        </h1>

        <p className="text-gray-400 mt-2">
          Predict how misinformation may spread in
          the future.
        </p>

      </div>


      {/* =====================================================
          FUTURE SPREAD PREDICTION
      ===================================================== */}

      <div className="bg-slate-800 rounded-2xl p-8 text-white">

        <h2 className="text-3xl font-bold mb-6">
          🚀 Future Spread Prediction
        </h2>

        <div className="grid md:grid-cols-4 gap-6">

          {/* Predicted Reach */}

          <div className="bg-slate-900 rounded-xl p-6">

            <p className="text-gray-400">
              Predicted Reach
            </p>

            <h3 className="text-3xl font-bold text-blue-400 mt-3">
              {reach}
            </h3>

          </div>


          {/* Spread Probability */}

          <div className="bg-slate-900 rounded-xl p-6">

            <p className="text-gray-400">
              Spread Probability
            </p>

            <h3 className="text-3xl font-bold text-yellow-400 mt-3">
              {probability}
            </h3>

          </div>


          {/* Risk Level */}

          <div className="bg-slate-900 rounded-xl p-6">

            <p className="text-gray-400">
              Risk Level
            </p>

            <h3 className="text-3xl font-bold text-red-400 mt-3">
              {prediction.risk_level ||
                "Not Available"}
            </h3>

          </div>


          {/* Virality */}

          <div className="bg-slate-900 rounded-xl p-6">

            <p className="text-gray-400">
              Virality Score
            </p>

            <h3 className="text-3xl font-bold text-green-400 mt-3">
              {virality}
            </h3>

          </div>

        </div>

      </div>


      {/* =====================================================
          VERIFIED ENGAGEMENT
      ===================================================== */}

      <div className="bg-slate-800 rounded-2xl p-8 text-white">

        <div className="flex justify-between items-center mb-6">

          <h2 className="text-3xl font-bold">
            📊 Verified Engagement Signals
          </h2>

          <span className="bg-slate-900 px-4 py-2 rounded-xl">
            {platformName}
          </span>

        </div>


        <div className="grid md:grid-cols-4 sm:grid-cols-2 gap-6">

          {engagementMetrics.length > 0 ? (

            engagementMetrics.map(
              (metric, index) => (

                <div
                  key={index}
                  className="bg-slate-900 rounded-xl p-5"
                >

                  <p className="text-gray-400">
                    📊 {metric.label}
                  </p>

                  <h3 className="text-3xl font-bold text-blue-400 mt-3">
                    {metric.value.toLocaleString()}
                  </h3>

                </div>

              )
            )

          ) : (

            <p className="text-gray-300">
              No visible engagement data detected.
            </p>

          )}

        </div>

      </div>


      {/* =====================================================
          GRAPH BUTTON
      ===================================================== */}

      <div className="mt-8 flex justify-end">

        <button
          onClick={() =>
            navigate(
              "/graph",
              {
                state: {
                  analysis,
                },
              }
            )
          }
          className="bg-blue-600 hover:bg-blue-700 px-6 py-3 rounded-xl font-semibold text-white transition"
        >
          📈 View Propagation Graph
        </button>

      </div>


      {/* =====================================================
          SPREAD FACTOR ANALYSIS
      ===================================================== */}

      <div className="bg-slate-800 rounded-2xl p-8 text-white">

        <h2 className="text-3xl font-bold mb-6">
          📈 Spread Factor Analysis
        </h2>

        <p className="text-gray-300">

          Spread Score:

          <span className="ml-3 font-bold text-green-400">

            {spread.metrics?.spread_score ??
              "Not Available"}

          </span>

        </p>

        <p className="text-gray-300 mt-5">
          {spread.summary ||
            "No spread analysis available."}
        </p>

      </div>


      {/* =====================================================
          PREDICTION EXPLANATION
      ===================================================== */}

      {analysisSummary && (

        <div className="bg-slate-800 rounded-2xl p-8 text-white">

          <h2 className="text-3xl font-bold mb-4">
            🤖 Prediction Explanation
          </h2>

          <p className="text-gray-300">
            {analysisSummary}
          </p>

        </div>

      )}

    </div>
  );
}
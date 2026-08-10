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

  if (!hasSocialAnalysis) {
    return (
      <div className="min-h-[70vh] flex items-center justify-center px-4">
        <div className="max-w-xl w-full bg-slate-800/90 border border-slate-700 rounded-3xl p-10 text-white text-center shadow-2xl">
          <div className="w-16 h-16 mx-auto rounded-2xl bg-blue-500/10 border border-blue-500/30 flex items-center justify-center">
            <span className="text-3xl">⚠️</span>
          </div>
          <h1 className="text-3xl font-bold mt-6">
            No Spread Prediction Available
          </h1>
          <p className="text-slate-400 mt-4 leading-7">
            Spread prediction is available only for
            social-media screenshot analysis.
          </p>
          <p className="text-slate-500 mt-3 text-sm leading-6">
            Analyze an Instagram, Facebook or Twitter/X
            screenshot first to generate propagation
            and spread prediction results.
          </p>
          <button
            onClick={() => navigate("/analyze")}
            className="mt-8 bg-blue-600 hover:bg-blue-500 px-7 py-3 rounded-xl text-white font-semibold transition shadow-lg shadow-blue-900/20"
          >
            Go to Analyze
          </button>
        </div>
      </div>
    );
  }

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
    "Unknown";

  const analysisSummary =
    analysis.prediction?.analysis_summary ||
    "";

  const predictedReach =
    prediction.predicted_reach !== undefined &&
    prediction.predicted_reach !== null
      ? Math.round(Number(prediction.predicted_reach))
      : null;

  const spreadProbability =
    prediction.spread_probability !== undefined &&
    prediction.spread_probability !== null
      ? Number(prediction.spread_probability)
      : null;

  const viralityScore =
    prediction.virality_score !== undefined &&
    prediction.virality_score !== null
      ? Number(prediction.virality_score)
      : null;

  const riskLevel =
    prediction.risk_level ||
    "Unknown";

  const spreadScore =
    spread.metrics?.spread_score !== undefined &&
    spread.metrics?.spread_score !== null
      ? Number(spread.metrics.spread_score)
      : null;

  const normalizedRisk =
    String(riskLevel).toLowerCase();

  let riskClass =
    "bg-slate-700/50 text-slate-300 border-slate-600";

  let riskAccent = "text-slate-300";

  if (normalizedRisk === "low") {
    riskClass =
      "bg-emerald-500/10 text-emerald-400 border-emerald-500/30";
    riskAccent = "text-emerald-400";
  }

  if (normalizedRisk === "medium") {
    riskClass =
      "bg-amber-500/10 text-amber-400 border-amber-500/30";
    riskAccent = "text-amber-400";
  }

  if (normalizedRisk === "high") {
    riskClass =
      "bg-red-500/10 text-red-400 border-red-500/30";
    riskAccent = "text-red-400";
  }

  const engagementLabels = {
    likes: "Likes",
    comments: "Comments",
    replies: "Replies",
    reposts: "Reposts",
    shares: "Shares",
    bookmarks: "Bookmarks",
    views: "Views"
  };

  const engagementMetrics =
    Object.entries(engagement)
      .filter(
        ([key, value]) =>
          key !== "metrics" &&
          key !== "followers" &&
          typeof value === "number" &&
          value >= 0
      )
      .map(
        ([key, value]) => ({
          key,
          label:
            engagementLabels[key] ||
            key
              .replace(/_/g, " ")
              .replace(/\b\w/g, c =>
                c.toUpperCase()
              ),
          value
        })
      );

  const formatNumber = (value) => {
    if (
      value === null ||
      value === undefined
    ) {
      return "—";
    }

    return Number(value).toLocaleString();
  };

  const formatPercentage = (value) => {
    if (
      value === null ||
      value === undefined
    ) {
      return "—";
    }

    return `${value}%`;
  };

  let spreadInterpretation =
    "The available signals indicate limited immediate spreading potential.";

  if (
    spreadProbability !== null &&
    spreadProbability >= 70
  ) {
    spreadInterpretation =
      "The content shows strong potential for continued spread and wider network exposure.";
  } else if (
    spreadProbability !== null &&
    spreadProbability >= 40
  ) {
    spreadInterpretation =
      "The content shows moderate potential for continued spread if engagement remains active.";
  }

  const getProgressWidth = (value) =>
    `${Math.min(
      Math.max(Number(value) || 0, 0),
      100
    )}%`;

  return (
    <div className="space-y-6 pb-10">
      <section className="relative overflow-hidden bg-slate-800 border border-slate-700 rounded-3xl p-8 shadow-xl">
        <div className="absolute -right-24 -top-24 w-72 h-72 bg-blue-500/10 rounded-full blur-3xl pointer-events-none" />
        <div className="absolute -left-24 -bottom-32 w-64 h-64 bg-indigo-500/5 rounded-full blur-3xl pointer-events-none" />
        <div className="relative">
          <div className="flex flex-col md:flex-row md:items-start md:justify-between gap-6">
            <div>
              <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-blue-500/10 border border-blue-500/20">
                <span className="w-1.5 h-1.5 rounded-full bg-blue-400" />
                <p className="text-blue-400 text-xs font-semibold uppercase tracking-wider">
                  AI Network Assessment
                </p>
              </div>
              <h1 className="text-4xl font-bold text-white mt-4">
                Spread Prediction
              </h1>
              <p className="text-slate-400 mt-3 max-w-3xl leading-7">
                An estimate of how this social-media content
                may propagate through the network based on
                verified engagement signals and detected
                content characteristics.
              </p>
            </div>
            <div className="flex flex-col items-start md:items-end gap-2">
              <span className="text-xs text-slate-500 uppercase tracking-wider">
                Analysis Platform
              </span>
              <span className="px-4 py-2 rounded-xl bg-slate-900 border border-slate-700 text-white font-semibold shadow-sm">
                {platformName}
              </span>
            </div>
          </div>
        </div>
      </section>

      <section className="bg-slate-800 border border-slate-700 rounded-3xl p-7 shadow-lg">
        <div className="flex items-center gap-3 mb-5">
          <div className="w-1 h-8 bg-blue-500 rounded-full" />
          <div>
            <h2 className="text-xl font-bold text-white">
              Prediction Summary
            </h2>
            <p className="text-sm text-slate-500 mt-0.5">
              Overall interpretation of the prediction
            </p>
          </div>
        </div>

        <div className="grid lg:grid-cols-3 gap-5">
          <div className="lg:col-span-2 bg-slate-900/90 border border-slate-700 rounded-2xl p-6">
            <p className="text-slate-300 leading-8">
              {analysisSummary ||
                spreadInterpretation}
            </p>
          </div>

          <div className="bg-slate-900/90 border border-slate-700 rounded-2xl p-6">
            <p className="text-xs uppercase tracking-wider text-slate-500">
              Overall Risk
            </p>

            <div className="flex items-center justify-between gap-3 mt-4">
              <span
                className={`text-3xl font-bold ${riskAccent}`}
              >
                {riskLevel}
              </span>

              <span
                className={`px-3 py-1.5 rounded-lg border text-sm font-semibold ${riskClass}`}
              >
                {normalizedRisk === "low"
                  ? "Lower Risk"
                  : normalizedRisk === "medium"
                    ? "Moderate Risk"
                    : normalizedRisk === "high"
                      ? "High Risk"
                      : "Unclassified"}
              </span>
            </div>

            <p className="text-slate-500 text-sm mt-4 leading-6">
              Risk represents the estimated potential
              impact of continued content propagation.
            </p>
          </div>
        </div>
      </section>

      <section className="bg-slate-800 border border-slate-700 rounded-3xl p-7 shadow-lg">
        <div className="flex items-center gap-3 mb-2">
          <div className="w-1 h-8 bg-blue-500 rounded-full" />
          <h2 className="text-xl font-bold text-white">
            Key Prediction Metrics
          </h2>
        </div>

        <p className="text-slate-500 text-sm mb-6">
          The primary indicators produced by the spread
          prediction model.
        </p>

        <div className="grid sm:grid-cols-2 xl:grid-cols-4 gap-5">
          <div className="relative overflow-hidden bg-slate-900/90 border border-slate-700 rounded-2xl p-6">
            <div className="absolute right-5 top-5 w-2 h-2 rounded-full bg-blue-400" />
            <p className="text-slate-500 text-sm">
              Predicted Reach
            </p>
            <h3 className="text-4xl font-bold text-blue-400 mt-4">
              {formatNumber(predictedReach)}
            </h3>
            <div className="w-full h-px bg-slate-700 mt-5" />
            <p className="text-slate-500 text-xs mt-4 leading-5">
              Estimated number of users who may be
              exposed if the current spreading pattern
              continues.
            </p>
          </div>

          <div className="relative overflow-hidden bg-slate-900/90 border border-slate-700 rounded-2xl p-6">
            <div className="absolute right-5 top-5 w-2 h-2 rounded-full bg-amber-400" />
            <p className="text-slate-500 text-sm">
              Spread Probability
            </p>
            <h3 className="text-4xl font-bold text-amber-400 mt-4">
              {formatPercentage(spreadProbability)}
            </h3>
            <div className="mt-5 h-2 bg-slate-800 rounded-full overflow-hidden">
              <div
                className="h-full bg-amber-400 rounded-full transition-all duration-500"
                style={{
                  width: getProgressWidth(
                    spreadProbability
                  )
                }}
              />
            </div>
            <p className="text-slate-500 text-xs mt-3 leading-5">
              Likelihood that the content will continue
              spreading through the network.
            </p>
          </div>

          <div className="relative overflow-hidden bg-slate-900/90 border border-slate-700 rounded-2xl p-6">
            <div
              className={`absolute right-5 top-5 w-2 h-2 rounded-full ${
                normalizedRisk === "high"
                  ? "bg-red-400"
                  : normalizedRisk === "medium"
                    ? "bg-amber-400"
                    : "bg-emerald-400"
              }`}
            />
            <p className="text-slate-500 text-sm">
              Risk Level
            </p>
            <h3
              className={`text-4xl font-bold mt-4 ${riskAccent}`}
            >
              {riskLevel}
            </h3>
            <div className="w-full h-px bg-slate-700 mt-5" />
            <p className="text-slate-500 text-xs mt-4 leading-5">
              Overall assessment of the potential
              network-level impact of the content.
            </p>
          </div>

          <div className="relative overflow-hidden bg-slate-900/90 border border-slate-700 rounded-2xl p-6">
            <div className="absolute right-5 top-5 w-2 h-2 rounded-full bg-emerald-400" />
            <p className="text-slate-500 text-sm">
              Virality Score
            </p>
            <h3 className="text-4xl font-bold text-emerald-400 mt-4">
              {formatPercentage(viralityScore)}
            </h3>
            <div className="mt-5 h-2 bg-slate-800 rounded-full overflow-hidden">
              <div
                className="h-full bg-emerald-400 rounded-full transition-all duration-500"
                style={{
                  width: getProgressWidth(
                    viralityScore
                  )
                }}
              />
            </div>
            <p className="text-slate-500 text-xs mt-3 leading-5">
              Indicates the likelihood of attracting
              additional sharing and interaction.
            </p>
          </div>
        </div>
      </section>

      <section className="bg-slate-800 border border-slate-700 rounded-3xl p-7 shadow-lg">
        <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4 mb-2">
          <div className="flex items-center gap-3">
            <div className="w-1 h-8 bg-cyan-400 rounded-full" />
            <div>
              <h2 className="text-xl font-bold text-white">
                Verified Engagement Signals
              </h2>
              <p className="text-sm text-slate-500">
                Values used as inputs for prediction
              </p>
            </div>
          </div>

          <span className="px-4 py-2 rounded-xl bg-slate-900 border border-slate-700 text-sm text-slate-300">
            {platformName}
          </span>
        </div>

        <p className="text-slate-400 text-sm leading-6 mb-6">
          These values were detected from the uploaded
          social-media content and verified or corrected
          before generating the prediction.
        </p>

        {engagementMetrics.length > 0 ? (
          <div className="grid grid-cols-2 md:grid-cols-3 xl:grid-cols-4 gap-4">
            {engagementMetrics.map(
              (metric) => (
                <div
                  key={metric.key}
                  className="bg-slate-900/90 border border-slate-700 rounded-2xl p-5 hover:border-slate-600 transition"
                >
                  <p className="text-slate-500 text-sm">
                    {metric.label}
                  </p>

                  <p className="text-2xl font-bold text-white mt-2">
                    {formatNumber(metric.value)}
                  </p>

                  <div className="mt-4 flex items-center gap-2">
                    <span className="w-2 h-2 rounded-full bg-emerald-400" />
                    <span className="text-xs text-slate-500">
                      Verified input
                    </span>
                  </div>
                </div>
              )
            )}
          </div>
        ) : (
          <div className="bg-slate-900/90 border border-slate-700 rounded-2xl p-6">
            <p className="text-slate-400">
              No visible engagement data was detected.
            </p>
          </div>
        )}
      </section>

      <section className="bg-slate-800 border border-slate-700 rounded-3xl p-7 shadow-lg">
        <div className="flex items-center gap-3 mb-2">
          <div className="w-1 h-8 bg-violet-400 rounded-full" />
          <div>
            <h2 className="text-xl font-bold text-white">
              Spread Factor Analysis
            </h2>
            <p className="text-sm text-slate-500">
              Understanding the factors behind the result
            </p>
          </div>
        </div>

        <p className="text-slate-400 text-sm leading-6 mb-6">
          This analysis combines the available engagement
          and detection signals to estimate the potential
          for further propagation.
        </p>

        <div className="grid lg:grid-cols-3 gap-5">
          <div className="bg-slate-900/90 border border-slate-700 rounded-2xl p-6">
            <p className="text-slate-500 text-sm">
              Spread Score
            </p>

            <p className="text-4xl font-bold text-violet-400 mt-3">
              {spreadScore !== null
                ? spreadScore
                : "—"}
            </p>

            <div className="w-full h-px bg-slate-700 mt-5" />

            <p className="text-slate-500 text-xs mt-4 leading-5">
              Combined indicator representing the
              estimated potential for continued spread.
            </p>
          </div>

          <div className="lg:col-span-2 bg-slate-900/90 border border-slate-700 rounded-2xl p-6">
            <p className="text-slate-500 text-sm">
              Interpretation
            </p>

            <p className="text-slate-300 leading-7 mt-3">
              {spread.summary ||
                spreadInterpretation}
            </p>
          </div>
        </div>
      </section>

      <section className="bg-slate-800 border border-slate-700 rounded-3xl p-7 shadow-lg">
        <div className="flex items-center gap-3 mb-2">
          <div className="w-1 h-8 bg-emerald-400 rounded-full" />
          <div>
            <h2 className="text-xl font-bold text-white">
              Model Interpretation
            </h2>
            <p className="text-sm text-slate-500">
              Explanation of the prediction
            </p>
          </div>
        </div>

        <div className="mt-5 bg-slate-900/90 border border-slate-700 rounded-2xl p-6">
          <p className="text-slate-300 leading-8">
            {analysisSummary ||
              "The model did not provide an additional explanation for this prediction. The result is based on the verified engagement and available content signals."}
          </p>
        </div>
      </section>

      <section className="relative overflow-hidden bg-slate-800 border border-blue-500/30 rounded-3xl p-7 shadow-lg">
        <div className="absolute -right-20 -bottom-24 w-56 h-56 bg-blue-500/10 rounded-full blur-3xl pointer-events-none" />

        <div className="relative flex flex-col lg:flex-row lg:items-center lg:justify-between gap-6">
          <div className="min-w-0">
            <p className="text-blue-400 text-xs font-semibold uppercase tracking-wider">
              Network Analysis
            </p>

            <h2 className="text-2xl font-bold text-white mt-2">
              Explore Content Propagation
            </h2>

            <p className="text-slate-400 mt-2 leading-6 max-w-2xl">
              Visualize how this content can propagate through
              users, influencers, communities and automated
              accounts in the simulated social network.
            </p>
          </div>

          <div className="lg:shrink-0">
            <button
              type="button"
              onClick={() =>
                navigate(
                  "/graph",
                  {
                    state: {
                      analysis
                    }
                  }
                )
              }
              className="w-auto whitespace-nowrap bg-blue-600 hover:bg-blue-500 px-8 py-3.5 rounded-xl text-white font-semibold transition shadow-lg shadow-blue-900/20"
            >
              View Propagation
            </button>
          </div>
        </div>
      </section>
    </div>
  );
}
import {
  Rocket,
  Target,
  AlertTriangle,
  TrendingUp,
  Activity,
} from "lucide-react";

export default function SpreadPredictionCard({ data }) {
  if (!data) return null;

  const prediction = data?.prediction || data || {};

  const spreadProbability =
    Number(prediction.spread_probability ?? 0) || 0;

  const viralityScore =
    Number(prediction.virality_score ?? 0) || 0;

  const getRiskStyle = (risk) => {
    const value = String(risk || "").toLowerCase();

    if (value.includes("high")) {
      return {
        text: "text-red-400",
        bg: "bg-red-500/10",
        border: "border-red-500/20",
      };
    }

    if (value.includes("medium")) {
      return {
        text: "text-yellow-400",
        bg: "bg-yellow-500/10",
        border: "border-yellow-500/20",
      };
    }

    if (value.includes("low")) {
      return {
        text: "text-green-400",
        bg: "bg-green-500/10",
        border: "border-green-500/20",
      };
    }

    return {
      text: "text-slate-300",
      bg: "bg-slate-500/10",
      border: "border-slate-500/20",
    };
  };

  const riskStyle = getRiskStyle(
    prediction.risk_level
  );

  return (
    <div className="mt-8">
      <div className="flex items-center gap-3 mb-6">
        <div className="w-10 h-10 rounded-xl bg-orange-500/10 border border-orange-500/20 flex items-center justify-center">
          <Rocket
            size={21}
            className="text-orange-400"
          />
        </div>

        <div>
          <h2 className="text-2xl font-bold text-white">
            Future Spread Prediction
          </h2>

          <p className="text-slate-500 text-sm mt-0.5">
            AI prediction of how the content may propagate
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
        <div className="bg-[#0F172A] border border-slate-700/70 rounded-2xl p-5">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl bg-blue-500/10 border border-blue-500/20 flex items-center justify-center">
                <Target
                  size={19}
                  className="text-blue-400"
                />
              </div>

              <div>
                <p className="text-slate-500 text-xs uppercase tracking-wider font-semibold">
                  Estimated Reach
                </p>

                <p className="text-slate-400 text-xs mt-1">
                  Potential audience
                </p>
              </div>
            </div>

            <span className="text-2xl font-bold text-white">
              {prediction.predicted_reach
                ? Number(
                    prediction.predicted_reach
                  ).toLocaleString()
                : "N/A"}
            </span>
          </div>
        </div>

        <div className="bg-[#0F172A] border border-slate-700/70 rounded-2xl p-5">
          <div className="flex justify-between items-center mb-3">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl bg-blue-500/10 border border-blue-500/20 flex items-center justify-center">
                <Activity
                  size={19}
                  className="text-blue-400"
                />
              </div>

              <div>
                <p className="text-slate-500 text-xs uppercase tracking-wider font-semibold">
                  Spread Probability
                </p>

                <p className="text-slate-400 text-xs mt-1">
                  Likelihood of further spread
                </p>
              </div>
            </div>

            <span className="text-xl font-bold text-blue-400">
              {spreadProbability}%
            </span>
          </div>

          <div className="w-full bg-slate-800 rounded-full h-2.5 overflow-hidden">
            <div
              className="h-full rounded-full bg-gradient-to-r from-blue-600 to-blue-400 transition-all duration-500"
              style={{
                width: `${Math.min(
                  spreadProbability,
                  100
                )}%`,
              }}
            />
          </div>
        </div>

        <div className="bg-[#0F172A] border border-slate-700/70 rounded-2xl p-5">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div
                className={`w-10 h-10 rounded-xl ${riskStyle.bg} ${riskStyle.border} border flex items-center justify-center`}
              >
                <AlertTriangle
                  size={19}
                  className={riskStyle.text}
                />
              </div>

              <div>
                <p className="text-slate-500 text-xs uppercase tracking-wider font-semibold">
                  Risk Level
                </p>

                <p className="text-slate-400 text-xs mt-1">
                  Predicted propagation risk
                </p>
              </div>
            </div>

            <span
              className={`text-xl font-bold ${riskStyle.text}`}
            >
              {prediction.risk_level || "Unknown"}
            </span>
          </div>
        </div>

        <div className="bg-[#0F172A] border border-slate-700/70 rounded-2xl p-5">
          <div className="flex justify-between items-center mb-3">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl bg-green-500/10 border border-green-500/20 flex items-center justify-center">
                <TrendingUp
                  size={19}
                  className="text-green-400"
                />
              </div>

              <div>
                <p className="text-slate-500 text-xs uppercase tracking-wider font-semibold">
                  Virality Score
                </p>

                <p className="text-slate-400 text-xs mt-1">
                  Potential to become viral
                </p>
              </div>
            </div>

            <span className="text-xl font-bold text-green-400">
              {viralityScore}%
            </span>
          </div>

          <div className="w-full bg-slate-800 rounded-full h-2.5 overflow-hidden">
            <div
              className="h-full rounded-full bg-gradient-to-r from-green-600 to-emerald-400 transition-all duration-500"
              style={{
                width: `${Math.min(
                  viralityScore,
                  100
                )}%`,
              }}
            />
          </div>
        </div>
      </div>

      {prediction.features_used && (
        <div className="mt-5 bg-[#0F172A] border border-slate-700/70 rounded-2xl p-5">
          <div className="flex items-center gap-3 mb-4">
            <div className="w-9 h-9 rounded-lg bg-purple-500/10 border border-purple-500/20 flex items-center justify-center">
              <Activity
                size={17}
                className="text-purple-400"
              />
            </div>

            <div>
              <h3 className="text-sm font-semibold text-white">
                Prediction Factors
              </h3>

              <p className="text-slate-500 text-xs mt-0.5">
                Engagement signals used by the prediction model
              </p>
            </div>
          </div>

          <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
            <div className="bg-slate-950/70 border border-slate-800 rounded-xl p-4">
              <p className="text-slate-500 text-xs">
                Views
              </p>

              <p className="text-white font-semibold mt-1">
                {prediction.features_used.views ?? 0}
              </p>
            </div>

            <div className="bg-slate-950/70 border border-slate-800 rounded-xl p-4">
              <p className="text-slate-500 text-xs">
                Shares
              </p>

              <p className="text-white font-semibold mt-1">
                {prediction.features_used.shares ?? 0}
              </p>
            </div>

            <div className="bg-slate-950/70 border border-slate-800 rounded-xl p-4">
              <p className="text-slate-500 text-xs">
                Likes
              </p>

              <p className="text-white font-semibold mt-1">
                {prediction.features_used.likes ?? 0}
              </p>
            </div>

            <div className="bg-slate-950/70 border border-slate-800 rounded-xl p-4">
              <p className="text-slate-500 text-xs">
                Comments
              </p>

              <p className="text-white font-semibold mt-1">
                {prediction.features_used.comments ?? 0}
              </p>
            </div>
          </div>
        </div>
      )}

      {prediction.analysis_summary && (
        <div className="mt-5 bg-[#0F172A] border border-slate-700/70 rounded-2xl p-5">
          <div className="flex items-center gap-2 mb-3">
            <Rocket
              size={18}
              className="text-orange-400"
            />

            <h3 className="text-sm font-semibold text-white">
              AI Prediction Reason
            </h3>
          </div>

          <div className="bg-slate-950/70 border border-slate-800 rounded-xl p-4">
            <p className="text-slate-300 text-sm leading-7">
              {prediction.analysis_summary}
            </p>
          </div>
        </div>
      )}
    </div>
  );
}
export default function SpreadPredictionCard({ data }) {
  if (!data) return null;

  const prediction = data?.prediction || data || {};

  return (
    <div className="bg-slate-800 rounded-2xl shadow-lg p-6 text-white">
      <h2 className="text-2xl font-bold mb-6 text-white">
        🚀 Future Spread Prediction
      </h2>

      <div className="space-y-5">

        <div className="flex justify-between items-center">
          <span className="text-gray-400">
            Estimated Reach Potential
          </span>

          <span className="font-semibold text-white">
            {prediction.predicted_reach
              ? prediction.predicted_reach.toLocaleString()
              : "Not Available"}
          </span>
        </div>

        <div className="flex justify-between items-center">
          <span className="text-gray-400">
            Spread Probability
          </span>

          <span className="font-semibold text-blue-400">
            {prediction.spread_probability ?? 0}%
          </span>
        </div>

        <div className="flex justify-between items-center">
          <span className="text-gray-400">
            Risk Level
          </span>

          <span className="font-semibold text-yellow-400">
            {prediction.risk_level || "Unknown"}
          </span>
        </div>

        <div className="flex justify-between items-center">
          <span className="text-gray-400">
            Virality Score
          </span>

          <span className="font-semibold text-green-400">
            {prediction.virality_score ?? 0}%
          </span>
        </div>

      </div>

      {prediction.features_used && (
        <div className="mt-6 bg-slate-700 rounded-xl p-4">
          <h3 className="font-bold mb-3 text-white">
            Prediction Factors
          </h3>

          <p className="text-gray-300 text-sm">
            Views: {prediction.features_used.views}
          </p>

          <p className="text-gray-300 text-sm">
            Shares: {prediction.features_used.shares}
          </p>

          <p className="text-gray-300 text-sm">
            Likes: {prediction.features_used.likes}
          </p>

          <p className="text-gray-300 text-sm">
            Comments: {prediction.features_used.comments}
          </p>
        </div>
      )}

      {prediction.analysis_summary && (
        <div className="mt-6 bg-slate-700 rounded-xl p-4">
          <h3 className="font-bold mb-2 text-white">
            AI Prediction Reason
          </h3>

          <p className="text-gray-300 text-sm leading-6">
            {prediction.analysis_summary}
          </p>
        </div>
      )}

    </div>
  );
}
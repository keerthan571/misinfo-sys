export default function SpreadPredictionCard({ data }) {
  if (!data) return null;

  return (
    <div className="bg-slate-800 rounded-2xl shadow-lg p-6">
      <h2 className="text-2xl font-bold text-white mb-6">
        Spread Prediction
      </h2>

      <div className="space-y-5">

        <div className="flex justify-between">
          <span className="text-gray-400">
            Predicted Reach
          </span>

          <span className="text-white font-semibold">
            {data.predicted_reach}
          </span>
        </div>

        <div className="flex justify-between">
          <span className="text-gray-400">
            Risk Level
          </span>

          <span className="text-yellow-400 font-semibold">
            {data.risk_level}
          </span>
        </div>

        <div className="flex justify-between">
          <span className="text-gray-400">
            Virality Score
          </span>

          <span className="text-white font-semibold">
            {data.virality_score}
          </span>
        </div>

      </div>
    </div>
  );
}
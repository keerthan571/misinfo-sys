export default function DetectionCard({ data }) {
  if (!data) return null;

  const getBadgeColor = (prediction) => {
    switch (prediction?.toLowerCase()) {
      case "fake":
        return "bg-red-500";
      case "real":
        return "bg-green-500";
      default:
        return "bg-yellow-500";
    }
  };

  return (
    <div className="bg-slate-800 rounded-2xl shadow-lg p-6">
      <h2 className="text-2xl font-bold text-white mb-6">
        AI Detection
      </h2>

      <div className="space-y-5">
        {/* Prediction */}
        <div className="flex justify-between items-center">
          <span className="text-gray-400">Prediction</span>

          <span
            className={`px-3 py-1 rounded-full text-white font-semibold ${getBadgeColor(
              data.prediction
            )}`}
          >
            {data.prediction}
          </span>
        </div>

        {/* Confidence */}
        <div className="flex justify-between items-center">
          <span className="text-gray-400">Confidence</span>

          <span className="text-white font-semibold">
            {data.confidence}%
          </span>
        </div>

        {/* Reason */}
        <div>
          <p className="text-gray-400 mb-2">Reason</p>

          <div className="bg-slate-900 rounded-xl p-4 text-gray-300 leading-relaxed">
            {data.reason}
          </div>
        </div>
      </div>
    </div>
  );
}
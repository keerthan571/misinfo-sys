export default function AnalyzeResult({ result }) {
  if (!result) return null;

  return (
    <div className="bg-slate-800 rounded-2xl p-6 shadow-lg">

      <h2 className="text-3xl font-bold text-white mb-6">
        AI Analysis Result
      </h2>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">

        {/* Prediction */}
        <div className="bg-slate-900 rounded-xl p-6">

          <p className="text-gray-400">
            Prediction
          </p>

          <h2
            className={`text-4xl font-bold mt-4 ${
              result.prediction.toLowerCase() === "fake"
                ? "text-red-500"
                : "text-green-500"
            }`}
          >
            {result.prediction}
          </h2>

        </div>

        {/* Confidence */}
        <div className="bg-slate-900 rounded-xl p-6">

          <p className="text-gray-400">
            Confidence
          </p>

          <h2 className="text-4xl font-bold text-blue-400 mt-4">
            {Number(result.confidence).toFixed(2)}%
          </h2>

        </div>

        {/* Risk */}
        <div className="bg-slate-900 rounded-xl p-6">

          <p className="text-gray-400">
            Risk Level
          </p>

          <h2
            className={`text-4xl font-bold mt-4 ${
              result.prediction.toLowerCase() === "fake"
                ? "text-red-500"
                : "text-green-500"
            }`}
          >
            {result.prediction.toLowerCase() === "fake"
              ? "HIGH"
              : "LOW"}
          </h2>

        </div>

      </div>

      {/* Text */}
      <div className="mt-8">

        <h3 className="text-xl font-semibold text-white mb-3">
          Text Analyzed
        </h3>

        <div className="bg-slate-900 rounded-xl p-4 text-gray-300 leading-7">
          {result.text_analyzed}
        </div>

      </div>

    </div>
  );
}
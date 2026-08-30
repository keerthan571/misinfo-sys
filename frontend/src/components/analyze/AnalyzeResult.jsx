export default function DetectionCard({ data }) {
  if (!data) return null;

  const getBadgeColor = (prediction) => {
    switch (prediction?.toLowerCase()) {
      case "needs verification":
        return "bg-yellow-500";

      case "not a factual claim":
        return "bg-blue-500";

      default:
        return "bg-yellow-500";
    }
  };

  return (
    <div className="bg-slate-800 rounded-2xl shadow-lg p-5 h-full flex flex-col">
      <h2 className="text-2xl font-bold text-white mb-4">
        🧠 NLP Analysis
      </h2>

      <div className="space-y-4">
        <div className="flex justify-between items-center">
          <div>
            <span className="text-gray-400 block">
              NLP Assessment
            </span>

            <span className="text-gray-500 text-sm">
              Factual claim assessment
            </span>
          </div>

          <span
            className={`px-3 py-1 rounded-full text-sm text-white font-semibold ${getBadgeColor(
              data.prediction
            )}`}
          >
            {data.prediction || "Needs Verification"}
          </span>
        </div>

        <div className="bg-slate-900 rounded-xl p-3">
          <h3 className="text-white font-bold mb-2">
            📌 Detected Claim
          </h3>

          <p className="text-gray-300">
            {data.claim || "Unknown"}
          </p>
        </div>

        <div className="bg-slate-900 rounded-xl p-3 space-y-2">
          <div className="flex justify-between">
            <span className="text-gray-400">
              Claim Type
            </span>

            <span className="text-white font-semibold">
              {data.claim_type || "Unknown"}
            </span>
          </div>

          <div className="flex justify-between">
            <span className="text-gray-400">
              Language
            </span>

            <span className="text-white font-semibold">
              {data.language || "Unknown"}
            </span>
          </div>
        </div>

        {data.keywords?.length > 0 && (
          <div>
            <p className="text-gray-400 mb-2">
              🔑 Keywords
            </p>

            <div className="flex flex-wrap gap-2">
              {data.keywords.map((item, index) => (
                <span
                  key={index}
                  className="bg-slate-900 px-2.5 py-1 rounded-lg text-sm text-gray-300"
                >
                  {item}
                </span>
              ))}
            </div>
          </div>
        )}

        {data.manipulation_signals?.length > 0 && (
          <div>
            <p className="text-gray-400 mb-2">
              ⚠️ Manipulation Signals
            </p>

            <div className="space-y-2">
              {data.manipulation_signals.map((item, index) => (
                <div
                  key={index}
                  className="bg-slate-900 rounded-lg p-2.5 text-sm text-gray-300"
                >
                  ✓ {item}
                </div>
              ))}
            </div>
          </div>
        )}

        {data.entities?.length > 0 && (
          <div>
            <p className="text-gray-400 mb-2">
              🌐 Extracted Entities
            </p>

            <div className="space-y-2">
              {data.entities.map((entity, index) => (
                <div
                  key={index}
                  className="bg-slate-900 rounded-lg p-2.5 flex justify-between items-center"
                >
                  <span className="text-gray-300">
                    {entity.name}
                  </span>

                  <span className="text-blue-400">
                    {entity.type}
                  </span>
                </div>
              ))}
            </div>
          </div>
        )}

        <div className="flex justify-between">
          <span className="text-gray-400">
            Similar Claim
          </span>

          <span
            className={
              data.similar_claim
                ? "text-yellow-400 font-semibold"
                : "text-green-400 font-semibold"
            }
          >
            {data.similar_claim
              ? "Detected"
              : "Not Detected"}
          </span>
        </div>
      </div>
    </div>
  );
}
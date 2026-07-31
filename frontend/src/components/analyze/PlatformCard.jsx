export default function PlatformCard({ data }) {
  if (!data) return null;

  return (
    <div className="bg-slate-800 rounded-2xl shadow-lg p-5">
      <h2 className="text-2xl font-bold text-white mb-5">
        🌐 Platform Detection
      </h2>

      {/* Platform + Confidence */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4 mb-5">
        <div className="flex items-center gap-3">
          <span className="text-gray-400 font-medium">
            Platform:
          </span>

          <span className="bg-green-500/20 text-green-400 px-3 py-1 rounded-full font-semibold">
            {data.platform}
          </span>
        </div>

        <div className="flex items-center gap-3">
          <span className="text-gray-400 font-medium">
            Confidence:
          </span>

          <span className="bg-blue-500/20 text-blue-400 px-3 py-1 rounded-full font-semibold">
            {data.confidence}%
          </span>
        </div>
      </div>

      {/* Signals */}
      <div className="border-t border-slate-700 pt-4">
        <p className="text-gray-400 mb-3 font-medium">
          Matched Signals
        </p>

        <div className="flex flex-wrap gap-2">
          {data.matched_signals?.map((signal, index) => (
            <span
              key={index}
              className="bg-slate-900 border border-slate-700 text-blue-300 text-sm px-3 py-1 rounded-full"
            >
              {signal}
            </span>
          ))}
        </div>
      </div>
    </div>
  );
}
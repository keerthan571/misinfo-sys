export default function FactVerificationCard({ data }) {
  if (!data) return null;

  return (
    <div className="bg-slate-800 rounded-2xl shadow-lg p-6">
      <h2 className="text-2xl font-bold text-white mb-6">
        Fact Verification
      </h2>

      <div className="space-y-5">
        <div>
          <p className="text-gray-400 mb-1">Claim</p>
          <div className="bg-slate-900 rounded-xl p-4 text-gray-300">
            {data.claim}
          </div>
        </div>

        <div className="flex justify-between">
          <span className="text-gray-400">Verdict</span>
          <span className="font-semibold text-red-400">
            {data.verdict}
          </span>
        </div>

        <div className="flex justify-between">
          <span className="text-gray-400">Confidence</span>
          <span className="text-white font-semibold">
            {data.confidence}%
          </span>
        </div>

        <div>
          <p className="text-gray-400 mb-1">Reason</p>

          <div className="bg-slate-900 rounded-xl p-4 text-gray-300">
            {data.reason}
          </div>
        </div>

        <div>
          <p className="text-gray-400 mb-2">Sources</p>

          <div className="space-y-2">
            {data.sources?.map((source, index) => (
              <a
                key={index}
                href={source}
                target="_blank"
                rel="noreferrer"
                className="block text-blue-400 hover:underline break-all"
              >
                {source}
              </a>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
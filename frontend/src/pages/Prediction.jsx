export default function Prediction() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-4xl font-bold text-white">
          Spread Prediction
        </h1>

        <p className="text-gray-400 mt-2">
          Predict how misinformation may spread in the future.
        </p>
      </div>

      <div className="bg-slate-800 rounded-2xl p-8">
        <div className="grid md:grid-cols-3 gap-6">

          <div className="bg-slate-900 rounded-xl p-6">
            <p className="text-gray-400">Predicted Reach</p>
            <h2 className="text-3xl font-bold text-blue-400 mt-3">
              12,500
            </h2>
          </div>

          <div className="bg-slate-900 rounded-xl p-6">
            <p className="text-gray-400">Spread Probability</p>
            <h2 className="text-3xl font-bold text-yellow-400 mt-3">
              86%
            </h2>
          </div>

          <div className="bg-slate-900 rounded-xl p-6">
            <p className="text-gray-400">Risk Level</p>
            <h2 className="text-3xl font-bold text-red-500 mt-3">
              HIGH
            </h2>
          </div>

        </div>
      </div>
    </div>
  );
}
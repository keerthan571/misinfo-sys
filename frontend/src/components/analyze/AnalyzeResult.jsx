export default function AnalyzeResult({ result }) {

  if (!result) return null;

  const data=result.analysis?.final_result;

  if(!data) return null;

  const prediction=data.label || "Unknown";

  const predictionColor=()=>{

    const value=prediction.toLowerCase();

    if(value.includes("verified")){
      return "text-green-400";
    }

    if(value.includes("false") || value.includes("fake")){
      return "text-red-400";
    }

    if(value.includes("misleading")){
      return "text-yellow-400";
    }

    return "text-blue-400";
  };

  return (
    <div className="bg-slate-800 rounded-2xl p-6 shadow-lg">

      <h2 className="text-3xl font-bold text-white mb-6">
        AI Analysis Result
      </h2>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">

        <div className="bg-slate-900 rounded-xl p-6">
          <p className="text-gray-400">
            Prediction
          </p>

          <h2 className={`text-4xl font-bold mt-4 ${predictionColor()}`}>
            {prediction}
          </h2>
        </div>

        <div className="bg-slate-900 rounded-xl p-6">
          <p className="text-gray-400">
            Confidence
          </p>

          <h2 className="text-4xl font-bold text-blue-400 mt-4">
            {Number(data.confidence || 0).toFixed(2)}%
          </h2>
        </div>

        <div className="bg-slate-900 rounded-xl p-6">
          <p className="text-gray-400">
            Risk Level
          </p>

          <h2 className="text-4xl font-bold text-yellow-400 mt-4">
            {data.risk_level || "Unknown"}
          </h2>
        </div>

      </div>

      <div className="mt-8">

        <h3 className="text-xl font-semibold text-white mb-3">
          Summary
        </h3>

        <div className="bg-slate-900 rounded-xl p-4 text-gray-300 leading-7">
          {data.summary || "No summary available."}
        </div>

      </div>

    </div>
  );
}
export default function SpreadPredictionCard({ data }) {

  if (!data) return null;


  return (

    <div className="
      bg-slate-800
      rounded-2xl
      shadow-lg
      p-6
      text-white
    ">


      <h2 className="text-2xl font-bold mb-6">
        🚀 Future Spread Prediction
      </h2>



      <div className="space-y-5">


        {/* Estimated Reach */}

        <div className="flex justify-between items-center">

          <span className="text-gray-400">
            Estimated Reach Potential
          </span>

          <span className="font-semibold text-white">
            {data.predicted_reach
              ? data.predicted_reach.toLocaleString()
              : "0"}
          </span>

        </div>




        {/* Spread Probability */}

        <div className="flex justify-between items-center">

          <span className="text-gray-400">
            Spread Probability
          </span>

          <span className="font-semibold text-blue-400">
            {data.spread_probability || 0}%
          </span>

        </div>




        {/* Risk Level */}

        <div className="flex justify-between items-center">

          <span className="text-gray-400">
            Risk Level
          </span>

          <span className="
            font-semibold
            text-yellow-400
          ">
            {data.risk_level || "Unknown"}
          </span>

        </div>




        {/* Virality Score */}

        <div className="flex justify-between items-center">

          <span className="text-gray-400">
            Virality Score
          </span>

          <span className="font-semibold text-green-400">
            {data.virality_score || 0}%
          </span>

        </div>


      </div>




      {/* AI Explanation */}

      {
        data.analysis_summary && (

          <div className="
            mt-6
            bg-slate-700
            rounded-xl
            p-4
          ">


            <h3 className="font-bold mb-2">
              AI Prediction Reason
            </h3>


            <p className="text-gray-300 text-sm leading-6">
              {data.analysis_summary}
            </p>


          </div>

        )

      }



    </div>

  );

}
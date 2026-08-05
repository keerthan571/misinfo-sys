import { useLocation, useNavigate } from "react-router-dom";
import { useAnalysis } from "../context/AnalysisContext";

export default function Prediction(){

    const navigate = useNavigate();
    const { state } = useLocation();

    const { analysis: contextAnalysis } = useAnalysis();

    const analysis =
        state?.analysis ||
        contextAnalysis?.result?.analysis ||
        null;

    if(!analysis){

        return(
            <div className="bg-slate-800 rounded-2xl p-12 text-center">

                <h2 className="text-3xl font-bold text-white">
                    No Prediction Available
                </h2>

                <p className="text-gray-400 mt-4">
                    Analyze a post first.
                </p>

            </div>
        );
    }
  const prediction =
    analysis.prediction?.data ||
    analysis.prediction ||
    {};

  const analysisSummary =
    analysis.prediction?.analysis_summary ||
    "";

  const spread =
    analysis.spread_analysis || {};

  const engagement =
    analysis.verified_engagement ||
    analysis.engagement ||
    {};

  const platform =
    analysis.platform?.platform ||
    "Not Selected";

  const engagementMetrics =
    Object.entries(
      engagement
    )
      .filter(
        ([key, value]) =>
          key !== "metrics" &&
          typeof value === "number" &&
          value > 0
      )
      .map(
        ([key, value]) => ({

          label:
            key.charAt(0).toUpperCase() + key.slice(1),

          value: value

        })
      );

  const reach =
    prediction.predicted_reach
      ?
      Math.round(
        prediction.predicted_reach
      ).toLocaleString()
      :
      "Not Available";

  const probability =
    prediction.spread_probability !== undefined &&
      prediction.spread_probability !== null
      ?
      `${prediction.spread_probability}%`
      :
      "Not Available";

  const virality =
    prediction.virality_score !== undefined &&
      prediction.virality_score !== null
      ?
      `${prediction.virality_score}%`
      :
      "Not Available";

  return (

    <div className="space-y-8">

      <div>

        <h1 className="text-4xl font-bold text-white">
          Spread Prediction
        </h1>


        <p className="text-gray-400 mt-2">
          Predict how misinformation may spread in the future.
        </p>


      </div>




      <div className="bg-slate-800 rounded-2xl p-8 text-white">


        <h2 className="text-3xl font-bold mb-6">
          🚀 Future Spread Prediction
        </h2>



        <div className="grid md:grid-cols-4 gap-6">


          <div className="bg-slate-900 rounded-xl p-6">

            <p className="text-gray-400">
              Predicted Reach
            </p>

            <h3 className="text-3xl font-bold text-blue-400 mt-3">
              {reach}
            </h3>

          </div>



          <div className="bg-slate-900 rounded-xl p-6">

            <p className="text-gray-400">
              Spread Probability
            </p>

            <h3 className="text-3xl font-bold text-yellow-400 mt-3">
              {probability}
            </h3>

          </div>



          <div className="bg-slate-900 rounded-xl p-6">

            <p className="text-gray-400">
              Risk Level
            </p>

            <h3 className="text-3xl font-bold text-red-400 mt-3">
              {prediction.risk_level || "Not Available"}
            </h3>

          </div>



          <div className="bg-slate-900 rounded-xl p-6">

            <p className="text-gray-400">
              Virality Score
            </p>

            <h3 className="text-3xl font-bold text-green-400 mt-3">
              {virality}
            </h3>

          </div>


        </div>


      </div>





      <div className="bg-slate-800 rounded-2xl p-8 text-white">


        <div className="flex justify-between items-center mb-6">


          <h2 className="text-3xl font-bold">
            📊 Verified Engagement Signals
          </h2>


          <span className="bg-slate-900 px-4 py-2 rounded-xl text-gray-300">
            {platform}
          </span>


        </div>




        <div className="grid md:grid-cols-4 sm:grid-cols-2 gap-6">


          {
            engagementMetrics.length > 0

              ?

              engagementMetrics.map(
                (metric, index) => (

                  <div
                    key={index}
                    className="bg-slate-900 rounded-xl p-5"
                  >

                    <p className="text-gray-400">
                      📊 {metric.label}
                    </p>


                    <h3 className="text-3xl font-bold mt-3 text-blue-400">

                      {metric.value.toLocaleString()}

                    </h3>


                  </div>

                )
              )

              :

              <div className="col-span-full bg-slate-900 rounded-xl p-6">

                <p className="text-gray-300 text-lg">
                  No visible engagement data detected.
                </p>

              </div>

          }


        </div>


      </div>
      <div className="mt-8 flex justify-end">
         
        <button
        
          onClick={() =>
            navigate("/graph", {
                state:{
                    analysis
                }
            })
          }
          className="
      bg-blue-600
      hover:bg-blue-700
      px-6
      py-3
      rounded-xl
      font-semibold
      transition-all
      duration-200
      hover:scale-105
      shadow-lg
    "
        >
          📈 View Propagation Graph
        </button>

      </div>




      <div className="bg-slate-800 rounded-2xl p-8 text-white">


        <h2 className="text-3xl font-bold mb-6">
          📈 Spread Factor Analysis
        </h2>


        <p className="text-gray-300 text-lg">

          Spread Score:

          <span className="ml-3 font-bold text-green-400">

            {spread.metrics?.spread_score ?? "Not Available"}

          </span>

        </p>



        <p className="text-gray-300 mt-5">

          {spread.summary || "No spread analysis available."}

        </p>


      </div>





      {
        analysisSummary &&

        <div className="bg-slate-800 rounded-2xl p-8 text-white">

          <h2 className="text-3xl font-bold mb-4">
            🤖 Prediction Explanation
          </h2>


          <p className="text-gray-300">
            {analysisSummary}
          </p>


        </div>
      }


    </div>

  );

}
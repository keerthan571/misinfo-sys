import { useLocation } from "react-router-dom";


export default function Prediction() {


  const { state } = useLocation();


  const latestAnalysis = state || {};



  const prediction =

    latestAnalysis.prediction?.data ||

    latestAnalysis.prediction ||

    {};



  const spread =

    latestAnalysis.spread ||

    {};



  const engagement =

    latestAnalysis.engagement ||

    {};




  const reach =

    prediction.predicted_reach

      ? Math.round(
          prediction.predicted_reach
        ).toLocaleString()

      : "Not Available";




  const probability =

    prediction.spread_probability !== undefined &&

    prediction.spread_probability !== null

      ? `${prediction.spread_probability}%`

      : "Not Available";




  const virality =

    prediction.virality_score !== undefined &&

    prediction.virality_score !== null

      ? `${prediction.virality_score}%`

      : "Not Available";




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


        <h2 className="text-3xl font-bold mb-6">

          📊 Social Engagement Signals

        </h2>



        <div className="grid md:grid-cols-4 gap-6">


          <div className="bg-slate-900 rounded-xl p-5">

            ❤️ Likes

            <h3 className="text-2xl font-bold mt-2">

              {engagement.likes ?? "Not Available"}

            </h3>

          </div>



          <div className="bg-slate-900 rounded-xl p-5">

            🔁 Shares

            <h3 className="text-2xl font-bold mt-2">

              {engagement.shares ?? "Not Available"}

            </h3>

          </div>



          <div className="bg-slate-900 rounded-xl p-5">

            👀 Views

            <h3 className="text-2xl font-bold mt-2">

              {engagement.views ?? "Not Available"}

            </h3>

          </div>



          <div className="bg-slate-900 rounded-xl p-5">

            🔖 Bookmarks

            <h3 className="text-2xl font-bold mt-2">

              {engagement.bookmarks ?? "Not Available"}

            </h3>

          </div>


        </div>


      </div>





      <div className="bg-slate-800 rounded-2xl p-8 text-white">


        <h2 className="text-3xl font-bold mb-6">

          📈 Spread Factor Analysis

        </h2>



        <p className="text-gray-300 text-lg">

          Spread Score:

          <span className="ml-3 font-bold text-green-400">

            {
              spread.metrics?.spread_score ??

              spread.spread_score ??

              "Not Available"
            }

          </span>

        </p>




        <p className="text-gray-300 mt-5">

          {
            spread.summary ||

            "No spread analysis available."
          }

        </p>


      </div>





      {
        prediction.analysis_summary && (

          <div className="bg-slate-800 rounded-2xl p-8 text-white">


            <h2 className="text-3xl font-bold mb-4">

              🤖 Prediction Explanation

            </h2>


            <p className="text-gray-300">

              {prediction.analysis_summary}

            </p>


          </div>

        )
      }



    </div>

  );

}
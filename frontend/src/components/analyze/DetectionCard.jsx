export default function DetectionCard({ data }) {

  if (!data) return null;



  const getBadgeColor = (prediction) => {

    switch(prediction?.toLowerCase()) {

      case "high risk":
      case "suspicious":
        return "bg-red-500";

      case "normal":
        return "bg-green-500";

      case "uncertain":
        return "bg-yellow-500";

      default:
        return "bg-blue-500";

    }

  };





  const getRiskBadge = (risk) => {

    switch(risk?.toLowerCase()) {

      case "high":
        return "bg-red-500";

      case "medium":
        return "bg-yellow-500";

      case "low":
        return "bg-green-500";

      default:
        return "bg-gray-500";

    }

  };





  const confidenceValue = Number(
    String(data.confidence)
    .replace("%","")
  ) || 0;





  return (

    <div className="bg-slate-800 rounded-2xl shadow-lg p-6">


      <h2 className="text-2xl font-bold text-white mb-6">
        🧠 NLP Content Intelligence
      </h2>




      <div className="space-y-5">





        {/* Classification */}

        <div className="flex justify-between items-center">

          <span className="text-gray-400">
            Classification
          </span>


          <span
            className={`px-4 py-1 rounded-full text-white font-semibold ${getBadgeColor(
              data.prediction
            )}`}
          >

            {data.prediction || "Normal"}

          </span>

        </div>







        {/* Confidence */}

        <div>

          <div className="flex justify-between mb-2">

            <span className="text-gray-400">
              Confidence
            </span>


            <span className="text-white font-semibold">
              {confidenceValue}%
            </span>

          </div>



          <div className="w-full bg-slate-900 rounded-full h-2">

            <div

              className="bg-green-400 h-2 rounded-full"

              style={{
                width:`${confidenceValue}%`
              }}

            ></div>


          </div>


        </div>








        {/* Content Understanding */}

        <div className="bg-slate-900 rounded-xl p-4 space-y-3">


          <h3 className="text-white font-bold mb-3">
            📌 Content Understanding
          </h3>



          <div className="flex justify-between">

            <span className="text-gray-400">
              Content Type
            </span>

            <span className="text-white font-semibold">
              {data.content_type || "Unknown"}
            </span>

          </div>





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
              Temporal Context
            </span>

            <span className="text-white font-semibold">
              {data.temporal_context || "Unknown"}
            </span>

          </div>



        </div>









        {/* Risk Analysis */}

        <div className="bg-slate-900 rounded-xl p-4 space-y-3">


          <h3 className="text-white font-bold mb-3">
            ⚠️ Risk Analysis
          </h3>



          <div className="flex justify-between items-center">


            <span className="text-gray-400">
              Risk Level
            </span>



            <span

              className={`px-3 py-1 rounded-full text-white font-semibold ${getRiskBadge(
                data.risk_level
              )}`}

            >

              {data.risk_level || "Unknown"}

            </span>


          </div>






          <div className="flex justify-between">

            <span className="text-gray-400">
              Risk Score
            </span>


            <span className="text-white font-bold">

              {data.risk_score ?? 0}

              <span className="text-gray-400">
                /100
              </span>

            </span>


          </div>



        </div>









        {/* Indicators */}

        {
          data.indicators?.length > 0 && (

            <div>


              <p className="text-gray-400 mb-2">
                🔍 Detected Indicators
              </p>



              <div className="space-y-2">


                {
                  data.indicators.map(
                    (item,index)=>(

                      <div

                        key={index}

                        className="bg-slate-900 rounded-lg p-3 text-gray-300"

                      >

                        ✓ {item}

                      </div>


                    )
                  )

                }


              </div>


            </div>


          )

        }









        {/* Entities */}

        {
          data.entities?.length > 0 && (

            <div>


              <p className="text-gray-400 mb-2">
                🌐 Extracted Entities
              </p>



              <div className="space-y-2">


                {
                  data.entities.map(
                    (entity,index)=>(

                      <div

                        key={index}

                        className="bg-slate-900 rounded-lg p-3 text-gray-300 flex justify-between"

                      >

                        <span>
                          {entity.name}
                        </span>


                        <span className="text-blue-400">
                          {entity.type}
                        </span>


                      </div>


                    )
                  )

                }


              </div>


            </div>

          )

        }









        {/* Reason */}

        <div>


          <p className="text-gray-400 mb-2">
            🤖 AI Explanation
          </p>



          <div className="bg-slate-900 rounded-xl p-4 text-gray-300 leading-relaxed">

            {data.reason || "No explanation available."}

          </div>


        </div>





      </div>



    </div>


  );

}
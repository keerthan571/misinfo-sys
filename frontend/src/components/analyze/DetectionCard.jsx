export default function DetectionCard({ data }) {

  if (!data) return null;


  const getBadgeColor = (prediction) => {

    switch(prediction?.toLowerCase()) {

      case "potential misinformation":
        return "bg-red-500";

      case "needs verification":
        return "bg-yellow-500";

      case "likely reliable":
        return "bg-green-500";

      default:
        return "bg-blue-500";

    }

  };



  const confidenceValue = Number(
    String(data.confidence || "0")
    .replace("%","")
  ) || 0;



  return (

    <div className="bg-slate-800 rounded-2xl shadow-lg p-6">


      <h2 className="text-2xl font-bold text-white mb-6">
        🧠 NLP Analysis
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
            {data.prediction || "Unknown"}
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
            />

          </div>

        </div>





        {/* Claim */}

        <div className="bg-slate-900 rounded-xl p-4">

          <h3 className="text-white font-bold mb-3">
            📌 Detected Claim
          </h3>


          <p className="text-gray-300">
            {data.claim || "Unknown"}
          </p>


        </div>






        {/* Claim Type + Language + Time */}

        <div className="bg-slate-900 rounded-xl p-4 space-y-3">


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





          <div className="flex justify-between">

            <span className="text-gray-400">
              Time Context
            </span>


            <span className="text-white font-semibold">
              {data.temporal_context || "Unknown"}
            </span>

          </div>


        </div>







        {/* Keywords */}

        {
          data.keywords?.length > 0 && (

            <div>

              <p className="text-gray-400 mb-2">
                🔑 Keywords
              </p>


              <div className="flex flex-wrap gap-2">


                {
                  data.keywords.map(

                    (item,index)=>(

                      <span

                        key={index}

                        className="bg-slate-900 px-3 py-2 rounded-lg text-gray-300"

                      >

                        {item}

                      </span>

                    )

                  )
                }


              </div>


            </div>

          )

        }








        {/* Manipulation Signals */}

        {
          data.manipulation_signals?.length > 0 && (

            <div>


              <p className="text-gray-400 mb-2">
                ⚠️ Manipulation Signals
              </p>



              <div className="space-y-2">


                {
                  data.manipulation_signals.map(

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

                        className="bg-slate-900 rounded-lg p-3 flex justify-between"

                      >

                        <span className="text-gray-300">
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






        {/* Similar Claim */}

        <div className="flex justify-between">


          <span className="text-gray-400">
            Similar Claim
          </span>


          <span className="text-white font-semibold">

            {
              data.similar_claim
              ? "Detected"
              : "Not Detected"
            }

          </span>


        </div>



      </div>


    </div>


  );

}
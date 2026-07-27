export default function FactVerificationCard({ data }) {

  if (!data) return null;


  const verdict = data.verdict || "Not Available";


  return (

    <div className="bg-slate-800 rounded-2xl shadow-lg p-6">


      <h2 className="text-2xl font-bold text-white mb-6">
        ✅ Fact Verification
      </h2>



      <div className="space-y-5">



        <div>

          <p className="text-gray-400 mb-2">
            Claim
          </p>


          <div className="bg-slate-900 rounded-xl p-4 text-gray-300 min-h-[80px]">

            {
              data.claim ||
              "No claim extracted."
            }

          </div>


        </div>







        <div className="flex justify-between items-center">


          <span className="text-gray-400">
            Verdict
          </span>



          <span
          className={`px-3 py-1 rounded-full font-semibold ${
            verdict === "Verified Information"
            ? "bg-green-500/20 text-green-400"
            :
            verdict === "False Information"
            ? "bg-red-500/20 text-red-400"
            :
            verdict === "Misleading Information"
            ? "bg-orange-500/20 text-orange-400"
            :
            "bg-yellow-500/20 text-yellow-400"
            }`}
          >

            {verdict}

          </span>


        </div>








        <div className="flex justify-between">


          <span className="text-gray-400">
            Confidence
          </span>



          <span className="text-white font-semibold">

            {data.confidence ?? 0}%

          </span>



        </div>








        <div>


          <p className="text-gray-400 mb-2">
            Reason
          </p>



          <div className="bg-slate-900 rounded-xl p-4 text-gray-300 min-h-[80px]">


            {
              data.reason ||
              "No verification explanation available."
            }


          </div>



        </div>









        <div>


          <p className="text-gray-400 mb-2">
            Sources
          </p>



          {

            data.sources &&
            data.sources.length > 0

            ?

            <div className="space-y-2">


              {
                data.sources.map(

                  (source,index)=>(

                    <a

                      key={index}

                      href={source}

                      target="_blank"

                      rel="noreferrer"

                      className="
                      block 
                      text-blue-400 
                      hover:underline 
                      break-all
                      "

                    >

                      {source}

                    </a>


                  )

                )
              }


            </div>


            :

            <p className="text-gray-500">
              No sources available.
            </p>


          }



        </div>





      </div>


    </div>


  );

}
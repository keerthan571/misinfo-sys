export default function PlatformCard({ data }) {

  if (!data) return null;


  return (

    <div className="bg-slate-800 rounded-2xl shadow-lg p-6">


      <h2 className="text-2xl font-bold text-white mb-6">
        🌐 Platform Detection
      </h2>



      <div className="space-y-5">


        <div className="flex justify-between">

          <span className="text-gray-400">
            Detected Platform
          </span>


          <span className="text-green-400 font-bold">
            {data.platform}
          </span>


        </div>





        <div className="flex justify-between">

          <span className="text-gray-400">
            Confidence
          </span>


          <span className="text-white font-semibold">
            {data.confidence}%
          </span>


        </div>





        <div>


          <p className="text-gray-400 mb-2">
            Matched Signals
          </p>



          <div className="flex flex-wrap gap-2">


            {
              data.matched_signals?.map(
                (signal,index)=>(

                  <span
                    key={index}
                    className="bg-slate-900 px-3 py-1 rounded-full text-blue-300"
                  >
                    {signal}
                  </span>

                )
              )
            }


          </div>


        </div>



      </div>


    </div>

  );

}
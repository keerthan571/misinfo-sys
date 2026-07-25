export default function OCRCard({ data }) {

  if (!data) return null;


  return (

    <div className="bg-slate-800 rounded-2xl shadow-lg p-6">


      <h2 className="text-2xl font-bold text-white mb-6">
        Content Summary
      </h2>



      <div className="space-y-5">



        <div className="flex justify-between">

          <span className="text-gray-400">
            Input Type
          </span>


          <span className="text-white font-semibold">

            {data.used ? "Image + OCR" : "Direct Text"}

          </span>


        </div>





        <div className="flex justify-between">

          <span className="text-gray-400">
            OCR Processing
          </span>


          <span className="text-white font-semibold">

            {data.used ? "Completed" : "Not Required"}

          </span>


        </div>





        {data.used && (

          <div className="flex justify-between">

            <span className="text-gray-400">
              OCR Confidence
            </span>


            <span className="text-green-400 font-semibold">

              {data.confidence}%

            </span>


          </div>

        )}







        <div>


          <p className="text-gray-400 mb-2">

            Extracted Content

          </p>



          <div className="bg-slate-900 rounded-xl p-4 min-h-[120px] text-gray-300 leading-relaxed">


            {data.extracted_text
              ? data.extracted_text
              : "User provided text directly."
            }


          </div>



        </div>




      </div>


    </div>

  );

}
import { useState } from "react";
import apiClient from "../../api/apiClient";


export default function AnalyzeInput({
  news,
  setNews,
  image,
  setImage,
  loading,
  onAnalyze,
}) {


  const [ocrLoading, setOcrLoading] = useState(false);

  const [ocrConfidence, setOcrConfidence] = useState(null);

  const [ocrError, setOcrError] = useState("");




  const handleImageChange = async (e) => {


    const file = e.target.files[0];


    if (!file) return;



    setImage(file);

    setOcrError("");

    setOcrConfidence(null);




    try {


      setOcrLoading(true);



      const formData = new FormData();


      formData.append(
        "file",
        file
      );




      const response = await apiClient.post(

        "/api/ocr/",

        formData,

        {
          headers: {

            "Content-Type":
            "multipart/form-data"

          }

        }

      );




      const data = response.data;




      if(data.status === "success"){


        setNews(

          data.extracted_text || ""

        );


        setOcrConfidence(

          data.confidence || 0

        );


      }

      else{


        setOcrError(
          "OCR extraction failed."
        );


      }




    }

    catch(err){


      console.error(err);


      setOcrError(
        "OCR service unavailable."
      );


    }


    finally{


      setOcrLoading(false);


    }


  };







  return (

    <div className="bg-slate-800 rounded-2xl p-6 shadow-lg">


      <h2 className="text-2xl font-bold text-white mb-6">

        Analyze News

      </h2>






      {/* OCR Editable Text */}

      <div>


        <label className="text-white font-semibold">

          News Text / OCR Edited Text

        </label>



        <textarea

          rows={10}

          value={news}

          onChange={(e)=>setNews(e.target.value)}

          placeholder="OCR text will appear here. You can edit before analysis..."

          className="w-full mt-3 bg-slate-900 rounded-xl p-4 text-white outline-none resize-none"

        />



      </div>







      <div className="flex items-center my-6">


        <div className="flex-1 border-t border-slate-600"></div>


        <span className="px-4 text-gray-400 text-sm">

          OR

        </span>


        <div className="flex-1 border-t border-slate-600"></div>


      </div>








      {/* Image Upload */}


      <div>


        <label className="text-white font-semibold">

          Upload News Screenshot

        </label>



        <input

          type="file"

          accept="image/*"

          onChange={handleImageChange}

          className="block mt-3 text-gray-300"

        />





        {
          image && (

            <div className="mt-5">


              <p className="text-green-400 text-sm mb-3">

                Selected: {image.name}

              </p>



              <img

                src={URL.createObjectURL(image)}

                alt="Uploaded news"

                className="w-full max-h-80 object-contain rounded-xl border border-slate-600"

              />



            </div>

          )

        }







        {
          ocrLoading && (

            <p className="text-yellow-400 mt-4">

              Extracting text from image...

            </p>

          )

        }







        {
          ocrConfidence !== null && (

            <p className="text-green-400 mt-4">

              OCR Confidence: {ocrConfidence}%

            </p>

          )

        }







        {
          ocrError && (

            <p className="text-red-400 mt-4">

              {ocrError}

            </p>

          )

        }



      </div>








      <button

        onClick={onAnalyze}

        disabled={loading || ocrLoading}

        className="mt-8 w-full bg-blue-600 hover:bg-blue-700 py-3 rounded-xl font-bold text-white disabled:opacity-50"

      >

        {
          loading

          ? "Analyzing..."

          : "Analyze"

        }


      </button>



    </div>

  );

}
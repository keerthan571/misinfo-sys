import { useState } from "react";
import apiClient from "../api/apiClient";

import AnalyzeInput from "../components/analyze/AnalyzeInput";
import DetectionCard from "../components/analyze/DetectionCard";
import FactVerificationCard from "../components/analyze/FactVerificationCard";
import OCRCard from "../components/analyze/OCRCard";
import SpreadPredictionCard from "../components/analyze/SpreadPredictionCard";
import PlatformCard from "../components/analyze/PlatformCard";


export default function Analyze() {


  const [news, setNews] = useState("");

  const [image, setImage] = useState(null);

  const [result, setResult] = useState(null);

  const [loading, setLoading] = useState(false);

  const [error, setError] = useState("");





  const handleAnalyze = async () => {


    if (!news.trim() && !image) {


      setError(
        "Please enter news text or upload an image."
      );

      return;

    }




    try {


      setLoading(true);

      setError("");

      setResult(null);




      const formData = new FormData();




      /*
        Priority:
        1. User edited OCR text
        2. Manual text
        3. Backend OCR
      */


      if (news.trim()) {


        formData.append(
          "text",
          news
        );


      }




      if (image) {


        formData.append(
          "image",
          image
        );


      }





      const response = await apiClient.post(

        "/api/analyze/",

        formData,

        {
          headers: {

            "Content-Type":
            "multipart/form-data"

          }

        }

      );





      const data = response.data;



      setResult(data);





      /*
        Put OCR extracted text into editor
        so user can modify and re-analyze
      */


      if (

        data?.analysis?.ocr?.extracted_text

        &&

        !news.trim()

      ) {


        setNews(

          data.analysis.ocr.extracted_text

        );


      }




    }



    catch(err) {


      console.error(err);


      setError(

        err.response?.data?.detail ||

        "Analysis failed."

      );


    }



    finally {


      setLoading(false);


    }


  };







  return (

    <div className="space-y-8">





      <div>


        <h1 className="text-4xl font-bold text-white">

          Analyze News

        </h1>



        <p className="text-gray-400 mt-2">

          Upload news images or enter text.
          OCR extraction, misinformation detection and verification happen automatically.

        </p>



      </div>







      <AnalyzeInput


        news={news}

        setNews={setNews}


        image={image}

        setImage={setImage}


        loading={loading}


        onAnalyze={handleAnalyze}


      />








      {
        error && (


          <div className="bg-red-500 p-4 rounded-xl text-white">


            {error}


          </div>


        )
      }










      {
        result?.analysis && (



          <div className="space-y-6">








            {/* FINAL RESULT */}


            <div className="bg-slate-800 rounded-2xl shadow-lg p-6 text-white">



              <h2 className="text-3xl font-bold mb-5">

                🧠 Final Analysis Result

              </h2>




              <p className="text-xl">

                Prediction:

                <span className="ml-3 font-bold text-red-400">


                  {
                    result.analysis.final_result?.label
                  }


                </span>


              </p>





              <p className="text-xl mt-3">


                Confidence:


                <span className="ml-3 font-bold text-green-400">


                  {
                    result.analysis.final_result?.confidence
                  }%


                </span>


              </p>





              <p className="text-xl mt-3">


                Risk Level:


                <span className="ml-3 font-bold text-yellow-400">


                  {
                    result.analysis.final_result?.risk_level
                  }


                </span>


              </p>





              <p className="text-gray-300 mt-5">


                {
                  result.analysis.final_result?.summary
                }


              </p>



            </div>









            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">






              <OCRCard

                data={
                  result.analysis.ocr
                }

              />







              <PlatformCard

                data={
                  result.analysis.platform
                }

              />








              <DetectionCard

                data={
                  result.analysis.detection
                }

              />








              <FactVerificationCard

                data={
                  result.analysis.fact_verification
                }

              />









              <SpreadPredictionCard

                data={
                  result.analysis.prediction
                }

              />






            </div>



          </div>


        )
      }






    </div>

  );

}
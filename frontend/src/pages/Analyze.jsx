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
      setError("Please enter news text or upload an image.");
      return;

    }

    setLoading(true);
    setError("");
    setResult(null);

    try {
      const formData = new FormData();



      if(news.trim()){

        formData.append(
          "text",
          news
        );

      }



      if(image){

        formData.append(
          "image",
          image
        );

      }





      const response = await apiClient.post(
        "/api/analyze/",
        formData,

        {
          headers:{
            "Content-Type":
            "multipart/form-data"
          }
        }

      );

      console.log("Analysis Result:", response.data);
      setResult(response.data);
    } catch (err) {
      console.error(err);

      if (err.response) {
        setError(
          err.response.data?.detail ||
            err.response.data?.message ||
            "Analysis failed."
        );
      } else {
        setError("Unable to connect to backend.");
      }
    } finally {
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
          Enter text or upload content image.
          AI will extract, verify and analyze misinformation spread.
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






      {error && (

        <div className="bg-red-500 p-4 rounded-xl text-white">

          {error}

        </div>

      )}

      {result?.analysis && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <OCRCard data={result.analysis.ocr} />

          <PlatformCard data={result.analysis.platform} />

          <DetectionCard data={result.analysis.detection} />





          {/* Content Summary */}

          <div className="bg-slate-800 rounded-2xl shadow-lg p-6 text-white">
            <h2 className="text-2xl font-bold mb-5">
              📊 Engagement Analysis
            </h2>

            <p>
              ❤️ Likes:{" "}
              {result.analysis.engagement?.likes ??
                "Not detected"}
            </p>

            <p>
              🔁 Shares/Reposts:{" "}
              {result.analysis.engagement?.shares ??
                "Not detected"}
            </p>

            <p>
              👀 Views:{" "}
              {result.analysis.engagement?.views ??
                "Not detected"}
            </p>

            <p>
              🔖 Bookmarks:{" "}
              {result.analysis.engagement?.bookmarks ??
                "Not detected"}
            </p>
          </div>

          <div className="bg-slate-800 rounded-2xl shadow-lg p-6 text-white">
            <h2 className="text-2xl font-bold mb-5">
              🚀 Spread Analysis
            </h2>

            <p className="mb-3">
              Spread Score:
              <span className="ml-2 font-bold text-green-400">
                {result.analysis.spread_analysis?.metrics
                  ?.spread_score ?? 0}
              </span>
            </p>

            {result.analysis.spread_analysis?.factors?.map(
              (item, index) => (
                <p key={index} className="mb-2">
                  🔥 {item.factor} - {item.impact}
                </p>
              )
            )}

            <p className="mt-4 text-gray-300">
              {result.analysis.spread_analysis?.summary ??
                "No spread analysis available."}
            </p>
          </div>






          {/* Platform */}

          <PlatformCard

            data={
              result.analysis.platform
            }

          />








          {/* AI Detection */}

          <DetectionCard

            data={
              result.analysis.detection
            }

          />








          {/* Fact Verification */}

          <FactVerificationCard

            data={
              result.analysis.fact_verification
            }

          />









          {/* Engagement */}

          <div className="bg-slate-800 rounded-2xl shadow-lg p-6 text-white">


            <h2 className="text-2xl font-bold mb-5">

              📊 Engagement Analysis

            </h2>




            <p>
              ❤️ Likes:

              {
                result.analysis.engagement?.likes ??
                "Not detected"
              }

            </p>




            <p>
              🔁 Shares/Reposts:

              {
                result.analysis.engagement?.shares ??
                "Not detected"
              }

            </p>




            <p>
              👀 Views:

              {
                result.analysis.engagement?.views ??
                "Not detected"
              }

            </p>




            <p>
              🔖 Bookmarks:

              {
                result.analysis.engagement?.bookmarks ??
                "Not detected"
              }

            </p>



          </div>









          {/* Spread Analysis */}

          <div className="bg-slate-800 rounded-2xl shadow-lg p-6 text-white">


            <h2 className="text-2xl font-bold mb-5">

              🚀 Spread Analysis

            </h2>




            <p className="mb-3">

              Spread Score:

              <span className="ml-2 font-bold text-green-400">

                {
                  result.analysis.spread_analysis
                  ?.metrics
                  ?.spread_score
                  ??
                  0
                }

              </span>


            </p>






            {
              result.analysis.spread_analysis
              ?.factors
              ?.map(

                (item,index)=>(

                  <p
                    key={index}
                    className="mb-2"
                  >

                    🔥 {item.factor}

                    {" - "}

                    {item.impact}

                  </p>

                )

              )

            }







            <p className="mt-4 text-gray-300">

              {
                result.analysis.spread_analysis
                ?.summary
                ??
                "No spread analysis available."
              }

            </p>




          </div>









          {/* Prediction */}

          <SpreadPredictionCard

            data={
              result.analysis.prediction
            }

          />
        </div>
      )}
    </div>

  );

}
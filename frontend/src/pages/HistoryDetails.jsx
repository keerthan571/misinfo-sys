import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import apiClient from "../api/apiClient";


export default function HistoryDetails() {

  const { id } = useParams();

  const [analysis, setAnalysis] = useState(null);

  const [loading, setLoading] = useState(true);



  useEffect(() => {

    fetchAnalysis();

  }, []);



  const fetchAnalysis = async () => {

    try {

      const response = await apiClient.get(
        `/api/history/${id}`
      );


      setAnalysis(
        response.data.analysis
      );


    } catch(err){

      console.error(err);

    }
    finally{

      setLoading(false);

    }

  };



  if(loading)
    return <div className="text-white text-xl">
      Loading analysis...
    </div>



  if(!analysis)
    return <div className="text-white text-xl">
      Analysis not found.
    </div>




  const imageUrl = analysis.image?.path
    ?
    `http://127.0.0.1:8000/${analysis.image.path.replace("\\","/")}`
    :
    null;



  return (

    <div className="space-y-6 text-white">


      <h1 className="text-4xl font-bold">
        Analysis Details
      </h1>



      {/* Uploaded Image */}

      {
        imageUrl && (

          <div className="bg-slate-800 rounded-2xl p-6">

            <h2 className="text-2xl font-bold mb-4">
              🖼 Uploaded Image
            </h2>


            <img

              src={imageUrl}

              className="
              rounded-xl
              max-h-96
              mx-auto
              "

              alt="Uploaded"

            />


          </div>

        )
      }





      {/* Original Text */}

      <div className="bg-slate-800 rounded-2xl p-6">

        <h2 className="text-2xl font-bold mb-4">
          📝 Original Content
        </h2>


        <p>
          {analysis.text || "No text available"}
        </p>


      </div>






      {/* Final Result */}

      <div className="bg-slate-800 rounded-2xl p-6">

        <h2 className="text-2xl font-bold mb-4">
          🧠 Final Result
        </h2>


        <p>
          Result:
          <span className="ml-2 font-bold">
            {analysis.final_result?.label}
          </span>
        </p>


        <p>
          Confidence:
          <span className="ml-2 font-bold">
            {analysis.final_result?.confidence}%
          </span>
        </p>


        <p>
          Risk:
          <span className="ml-2 font-bold">
            {analysis.final_result?.risk_level}
          </span>
        </p>


      </div>






      {/* OCR */}

      <div className="bg-slate-800 rounded-2xl p-6">

        <h2 className="text-2xl font-bold mb-4">
          📄 OCR Analysis
        </h2>


        <p>
          {analysis.ocr?.extracted_text || "No OCR data"}
        </p>


      </div>






      {/* NLP */}

      <div className="bg-slate-800 rounded-2xl p-6">

        <h2 className="text-2xl font-bold mb-4">
          🧠 NLP Detection
        </h2>


        <p>
          Claim:
          {analysis.detection?.claim}
        </p>


        <p>
          Prediction:
          {analysis.detection?.prediction}
        </p>


        <p>
          Manipulation Signals:
          {
            analysis.detection?.manipulation_signals?.join(", ")
          }
        </p>


      </div>






      {/* Fact Verification */}

      <div className="bg-slate-800 rounded-2xl p-6">

        <h2 className="text-2xl font-bold mb-4">
          ✅ Fact Verification
        </h2>


        <p>
          Verdict:
          {analysis.fact_verification?.verdict}
        </p>


        <p>
          Reason:
          {analysis.fact_verification?.reason}
        </p>


      </div>







      {/* Platform */}

      <div className="bg-slate-800 rounded-2xl p-6">

        <h2 className="text-2xl font-bold mb-4">
          🌐 Platform Detection
        </h2>


        <p>
          Platform:
          {analysis.platform?.platform || "Unknown"}
        </p>


        <p>
          Confidence:
          {analysis.platform?.confidence ?? 0}%
        </p>


      </div>






      {/* Engagement */}

      <div className="bg-slate-800 rounded-2xl p-6">

        <h2 className="text-2xl font-bold mb-4">
          📊 Engagement
        </h2>


        <p>
          Likes: {analysis.engagement?.likes ?? 0}
        </p>


        <p>
          Shares: {analysis.engagement?.shares ?? 0}
        </p>


        <p>
          Views: {analysis.engagement?.views ?? 0}
        </p>


      </div>






      {/* Prediction */}

      <div className="bg-slate-800 rounded-2xl p-6">

        <h2 className="text-2xl font-bold mb-4">
          🚀 Spread Prediction
        </h2>


        <p>
          Reach:
          {analysis.prediction?.predicted_reach}
        </p>


        <p>
          Probability:
          {analysis.prediction?.spread_probability}%
        </p>


        <p>
          Virality:
          {analysis.prediction?.virality_score}%
        </p>


      </div>



    </div>

  );

}
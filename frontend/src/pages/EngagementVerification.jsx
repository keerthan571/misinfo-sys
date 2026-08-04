import { useLocation, useNavigate } from "react-router-dom";
import { useState } from "react";
import apiClient from "../api/apiClient";


export default function EngagementVerification() {


  const { state } = useLocation();
  const navigate = useNavigate();


  const analysis = state?.analysis || {};



  const originalEngagement =
    analysis.engagement || {

      likes:0,
      comments:0,
      reposts:0,
      shares:0,
      bookmarks:0

    };



  const [editMode,setEditMode] = useState(false);



  const [engagement,setEngagement] = useState({

    likes:originalEngagement.likes || 0,

    comments:originalEngagement.comments || 0,

    reposts:originalEngagement.reposts || 0,

    shares:originalEngagement.shares || 0,

    bookmarks:originalEngagement.bookmarks || 0

  });



  const continuePrediction = async()=>{


    const verifiedEngagement={

      likes:Number(engagement.likes),

      comments:Number(engagement.comments),

      reposts:Number(engagement.reposts),

      shares:Number(engagement.shares),

      bookmarks:Number(engagement.bookmarks),

      views:0

    };



    try{


      const response = await apiClient.post(
        "/api/predict/",
        {

          engagement:verifiedEngagement,

          detection:analysis.detection || {},

          platform:
          analysis.platform?.platform ||
          "Instagram"

        }
      );



      const updatedAnalysis={

        ...analysis,


        // OCR values
        engagement:originalEngagement,


        // User verified values
        verified_engagement:verifiedEngagement,


        // New prediction after verification
        prediction:
        response.data.prediction,


        spread_analysis:
        response.data.spread_analysis

      };



      navigate("/prediction",{

        state:{
          analysis:updatedAnalysis
        }

      });



    }
    catch(error){

      console.log(
        "Prediction Error:",
        error
      );

    }


  };




  const handleChange=(key,value)=>{

    setEngagement({

      ...engagement,

      [key]:Number(value)

    });

  };



  return (

    <div className="space-y-8">


      <div className="bg-slate-800 rounded-2xl p-8 text-white">


        <h1 className="text-4xl font-bold mb-6">
          📊 Engagement Verification
        </h1>


        <p className="text-gray-300 mb-6">
          OCR detected the following engagement values.
          Verify or edit before spread prediction.
        </p>



        <div className="grid md:grid-cols-5 gap-5">


          {
            Object.entries(engagement).map(([key,value])=>(

              <div
                key={key}
                className="bg-slate-900 rounded-xl p-5"
              >

                <p className="text-gray-400 capitalize">
                  {key}
                </p>



                {
                  editMode ?


                  <input

                    type="number"

                    value={value}

                    onChange={(e)=>
                      handleChange(
                        key,
                        e.target.value
                      )
                    }

                    className="mt-3 w-full bg-slate-700 p-3 rounded-lg text-white"

                  />


                  :


                  <h2 className="text-3xl font-bold text-blue-400 mt-3">

                    {value.toLocaleString()}

                  </h2>


                }


              </div>

            ))
          }


        </div>




        <div className="flex gap-5 mt-8">


          <button

            onClick={continuePrediction}

            className="bg-green-600 hover:bg-green-700 px-8 py-3 rounded-xl font-bold"

          >

            Continue

          </button>




          <button

            onClick={()=>setEditMode(!editMode)}

            className="bg-yellow-600 hover:bg-yellow-700 px-8 py-3 rounded-xl font-bold"

          >

            {
              editMode
              ?
              "Save Changes"
              :
              "Edit Values"
            }


          </button>



        </div>


      </div>


    </div>

  );

}
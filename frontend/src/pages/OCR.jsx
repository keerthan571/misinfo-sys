import { useState } from "react";
import apiClient from "../api/apiClient";


export default function OCR() {


  const [selectedFile, setSelectedFile] = useState(null);
  const [preview, setPreview] = useState(null);

  const [loading, setLoading] = useState(false);
  const [analyzing, setAnalyzing] = useState(false);

  const [text, setText] = useState("");
  const [result, setResult] = useState(null);



  const handleFileChange = (e)=>{

    const file = e.target.files[0];

    if(!file) return;


    setSelectedFile(file);

    setPreview(
      URL.createObjectURL(file)
    );

  };





  const handleUpload = async()=>{


    if(!selectedFile){

      alert("Please select an image");

      return;

    }



    const formData = new FormData();


    formData.append(
      "file",
      selectedFile
    );



    try{


      setLoading(true);



      const response = await apiClient.post(

        "/api/ocr/",

        formData,

        {

          headers:{
            "Content-Type":"multipart/form-data"
          }

        }

      );



      setText(

        response.data.extracted_text || ""

      );



    }

    catch(error){

      console.error(error);

      alert("OCR Failed");

    }


    finally{

      setLoading(false);

    }

  };








  const handleAnalyze = async()=>{


    if(!text.trim()){

      alert("No text available");

      return;

    }



    try{


      setAnalyzing(true);



      const formData = new FormData();


      formData.append(

        "text",

        text

      );




      const response = await apiClient.post(

        "/api/analyze/",

        formData,

        {

          headers:{
            "Content-Type":"multipart/form-data"
          }

        }

      );



      console.log(
        response.data
      );



      setResult(

        response.data.analysis

      );



    }


    catch(error){


      console.error(error);

      alert("Analysis failed");


    }


    finally{


      setAnalyzing(false);


    }


  };








return (

<div className="space-y-6">



<h1 className="text-3xl font-bold text-white">
OCR Analysis
</h1>





<div className="bg-slate-800 rounded-xl p-6">


<input

type="file"

accept="image/*"

onChange={handleFileChange}

/>



{
preview &&

<img

src={preview}

className="mt-5 w-80 rounded-lg"

/>

}




<button

onClick={handleUpload}

className="mt-5 bg-blue-600 px-6 py-3 rounded-lg"

>


{
loading
?
"Extracting..."
:
"Extract Text"
}


</button>


</div>








{
text &&


<div className="bg-slate-800 rounded-xl p-6">


<h2 className="text-xl text-white font-bold">

Extracted Text

</h2>



<textarea

rows="8"

value={text}

onChange={(e)=>setText(e.target.value)}

className="mt-4 w-full bg-slate-900 text-white p-4 rounded-lg"

/>



<button

onClick={handleAnalyze}

className="mt-5 bg-green-600 px-6 py-3 rounded-lg"

>


{
analyzing
?
"Analyzing..."
:
"Analyze This Text"
}


</button>



</div>


}









{
result &&


<div className="bg-slate-800 rounded-xl p-6 text-white">





<h2 className="text-xl font-bold mb-5">

Analysis Result

</h2>





<div className="space-y-2">


<p>
🌐 Platform:

{
result.platform?.platform
||
"Not detected"
}

</p>



<p>
Prediction:

{
result.detection?.prediction
||
"N/A"
}

</p>



<p>
Confidence:

{
result.detection?.confidence
||
0
}%

</p>



<p>
Fact Verdict:

{
result.fact_verification?.verdict
||
"N/A"
}

</p>



<p>
Risk Level:

{
result.prediction?.risk_level
||
"N/A"
}

</p>



<p>
Virality Score:

{
result.prediction?.virality_score
||
0
}

</p>



</div>









<div className="mt-6 bg-slate-900 rounded-lg p-5">


<h3 className="text-lg font-bold mb-4">

📊 Engagement Analysis

</h3>




<p>
❤️ Likes:

{
result.engagement?.likes ??
"Not detected"
}

</p>



<p>
🔁 Shares/Reposts:

{
result.engagement?.shares ??
"Not detected"
}

</p>



<p>
💬 Comments:

{
result.engagement?.comments ??
"Not detected"
}

</p>



<p>
👀 Views:

{
result.engagement?.views ??
"Not detected"
}

</p>



<p>
🔖 Bookmarks:

{
result.engagement?.bookmarks ??
"Not detected"
}

</p>



<p>
👥 Followers:

{
result.engagement?.followers ??
"Not detected"
}

</p>



</div>









<div className="mt-6 bg-slate-900 rounded-lg p-5">


<h3 className="text-lg font-bold">

🚀 Spread Analysis

</h3>



<p className="mt-3">

Engagement Rate:

{
result.spread_analysis?.metrics?.engagement_rate
??
"Not calculated"
}%

</p>



<p>

Share Ratio:

{
result.spread_analysis?.metrics?.share_ratio
??
"Not calculated"
}%

</p>






<h4 className="mt-5 font-bold">

Main Spread Factors

</h4>




{

result.spread_analysis?.factors?.length > 0


?


result.spread_analysis.factors.map(

(item,index)=>(


<p key={index}>

🔥 {item.factor}

-
{item.impact}

</p>


)

)


:


<p>
No strong spread signals detected
</p>


}




<p className="mt-4">

📝 Summary:

{
result.spread_analysis?.summary
||
"No analysis"
}


</p>




</div>






</div>


}



</div>


);


}
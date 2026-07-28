from fastapi import APIRouter, UploadFile, File, Form, Depends
from datetime import datetime, timezone
import uuid
from app.auth.dependencies import get_current_user

from ..services.nlp_service import nlp_service
from ..services.ocr_service import ocr_service
from ..services.prediction_service import prediction_service
from ..services.fact_verification_service import verify_claim

from ..services.engagement_service import engagement_service
from ..services.platform_detector import platform_detector
from ..services.spread_factor_service import spread_factor_service

from ..database.mongodb import analyses_collection


router = APIRouter()



def safe_confidence(value):

    try:
        return int(
            str(value).replace("%", "")
        )

    except:
        return 0




def generate_final_result(response):

    detection = response.get(
        "detection",
        {}
    )

    fact = response.get(
        "fact_verification",
        {}
    )

    prediction = response.get(
        "prediction",
        {}
    )


    detection_conf = safe_confidence(
        detection.get(
            "confidence",
            0
        )
    )


    fact_conf = safe_confidence(
        fact.get(
            "confidence",
            0
        )
    )


    virality_score = int(
        prediction.get(
            "virality_score",
            0
        )
    )


    final_confidence = int(
        (
            detection_conf * 0.5
            +
            fact_conf * 0.3
            +
            virality_score * 0.2
        )
    )


    verdict = str(
        fact.get(
            "verdict",
            ""
        )
    ).lower()



    if "false" in verdict or "fake" in verdict:

        label = "False Information"


    elif "verified" in verdict or "true" in verdict:

        label = "Verified Information"


    elif "misleading" in verdict:

        label = "Misleading Information"


    else:

        label = "Insufficient Evidence"



    if final_confidence >= 75:

        risk_level = "High"

    elif final_confidence >= 40:

        risk_level = "Medium"

    else:

        risk_level = "Low"



    return {

        "label": label,

        "confidence": final_confidence,

        "risk_level": risk_level,

        "summary":
        f"Final analysis result: {label} with {final_confidence}% confidence."

    }






@router.post("/")
async def analyze(
    text: str = Form(None),
    image: UploadFile = File(None),
    current_user=Depends(get_current_user)
):
    analysis_id = str(uuid.uuid4())


    analysis_time = datetime.now(
        timezone.utc
    ).isoformat()



    response = {

        "analysis_id": analysis_id,

        "analysis_time": analysis_time,
        

        "final_result": {},


        "platform": {},

        "detection": {},

        "fact_verification": {},


        "ocr": {

            "used": False,

            "extracted_text": "",

            "confidence": 0,

            "word_count": 0

        },


        "engagement": {},

        "spread_analysis": {},

        "prediction": {},


        "graph": {

            "nodes": [],

            "edges": [],

            "trend_data": {

                "spread_score": [],

                "risk_score": [],

                "virality_score": []

            }

        }

    }




    final_text = text or ""

    extracted_text = ""




    # =========================
    # OCR PROCESSING
    # =========================


    if image:


        image_bytes = await image.read()


        ocr_result = (
            ocr_service
            .extract_text_from_image(
                image_bytes
            )
        )



        if ocr_result.get("status") == "success":


            extracted_text = ocr_result.get(
                "extracted_text",
                ""
            )


            response["ocr"] = {

                "used": True,

                "extracted_text": extracted_text,

                "confidence":
                ocr_result.get(
                    "confidence",
                    0
                ),

                "word_count":
                len(
                    extracted_text.split()
                )

            }



            if not final_text.strip():

                final_text = extracted_text







    # =========================
    # PLATFORM DETECTION
    # =========================


    platform_text = final_text


    if extracted_text:

        platform_text += " " + extracted_text



    response["platform"] = (

        platform_detector
        .detect_platform(
            platform_text
        )

    )







    # =========================
    # NLP + FACT VERIFICATION
    # =========================


    if final_text.strip():


        detection_result = (

            nlp_service
            .analyze_text(
                final_text
            )

        )



        response["detection"] = {
            
            "language":
            detection_result.get(
                "language",
                "Unknown"
            ),

            "keywords":
            detection_result.get(
                "keywords",
                []
            ),

            "manipulation_signals":
            detection_result.get(
                "manipulation_signals",
                []
            ),

            "similar_claim":
            detection_result.get(
                "similar_claim",
                False
            ),


            "status":

            detection_result.get(
                "status",
                "success"
            ),

            "claim":
            detection_result.get(
                "claim",
                final_text
            ),


            "prediction":

            detection_result.get(
                "prediction",
                "Needs Verification"
            ),



            "confidence":

            safe_confidence(
                detection_result.get(
                    "confidence",
                    0
                )
            ),



            "reason":

            detection_result.get(
                "reason",
                ""
            ),



            "content_type":

            detection_result.get(
                "content_type",
                "Other"
            ),



            "claim_type":

            detection_result.get(
                "claim_type",
                "Other"
            ),



            "temporal_context":

            detection_result.get(
                "temporal_context",
                "Unknown"
            ),



            "risk_level":

            detection_result.get(
                "risk_level",
                "Low"
            ),



            "risk_score":

            detection_result.get(
                "risk_score",
                0
            ),



            "entities":

            detection_result.get(
                "entities",
                []
            ),



            "indicators":

            detection_result.get(
                "indicators",
                []
            )

        }





        fact_result = verify_claim(
            detection_result.get(
                "claim",
                final_text
            )
        )



        response["fact_verification"] = {


            "status":

            fact_result.get(
                "status",
                "failed"
            ),



            "claim":

            fact_result.get(
                "claim",
                ""
            ),



            "verdict":

            fact_result.get(
                "verdict",
                ""
            ),



            "reason":

            fact_result.get(
                "reason",
                ""
            ),



            "confidence":

            safe_confidence(
                fact_result.get(
                    "confidence",
                    0
                )
            ),



            "sources":

            fact_result.get(
                "sources",
                []
            )

        }








    # =========================
    # ENGAGEMENT
    # =========================


    engagement_data = (

        engagement_service
        .extract_engagement(
            final_text
        )

    )


    response["engagement"] = engagement_data







    # =========================
    # SPREAD ANALYSIS
    # =========================


    response["spread_analysis"] = (

        spread_factor_service
        .analyze(

            engagement_data,

            content_analysis=response["detection"],

            platform=response["platform"].get(
                "platform"
            )

        )

    )







    # =========================
    # PREDICTION
    # =========================


    prediction_result = (

        prediction_service
        .predict_spread(

            {

                **engagement_data,


                "spread_score":

                response["spread_analysis"]
                .get("metrics", {})
                .get("spread_score", 0),



                "risk_score":

                response["detection"]
                .get("risk_score", 0),



                "emotion_score":

                max(
                    response["detection"]
                    .get("emotion_analysis", {})
                    .get("scores", {})
                    .values(),
                    default=0
                ),



                "manipulation_score":

                len(
                    response["detection"]
                    .get(
                        "manipulation_signals",
                        []
                    )
                ) * 20

            }

        )

    )



    prediction_data = prediction_result.get(
        "data",
        {}
    )



    response["prediction"] = prediction_result








    # =========================
    # FINAL RESULT
    # =========================


    response["final_result"] = (

        generate_final_result(
            response
        )

    )







    # =========================
    # SAVE ANALYSIS
    # =========================
    analysis_document = {

        "analysis_id": analysis_id,

        "email": current_user["email"],

        "userId": current_user["email"],

        "text": final_text,

        "analysis_time": analysis_time,

        "platform": response["platform"],

        "final_result": response["final_result"],

        "detection": response["detection"],

        "fact_verification": response["fact_verification"],

        "ocr": response["ocr"],

        "engagement": response["engagement"],

        "spread_analysis": response["spread_analysis"],

        "prediction": response["prediction"],

        "graph": response["graph"]
    }
    
    try:


        result = (

            analyses_collection
            .insert_one(
                analysis_document
            )

        )


        print(
            "MongoDB Inserted:",
            result.inserted_id
        )



    except Exception as e:


        print(
            "MongoDB Error:",
            e
        )







    return {

        "status": "success",

        "analysis": {

            **response,

            "verification_status":
            response["fact_verification"].get(
                "verdict",
                "Insufficient Evidence"
            ),

            "spread_prediction":
            response["prediction"],

            "metadata": {

                "analysis_id": analysis_id,

                "timestamp": analysis_time,

                "processing_status": "completed"

        }

    }

}
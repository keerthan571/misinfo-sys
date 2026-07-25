from fastapi import APIRouter, UploadFile, File, Form
from datetime import datetime, timezone
import uuid


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
            str(value)
            .replace("%", "")
        )

    except:

        return 0






@router.post("/")
async def analyze(

    text: str = Form(None),

    image: UploadFile = File(None)

):


    analysis_id = str(uuid.uuid4())


    analysis_time = datetime.now(
        timezone.utc
    ).isoformat()



    response = {

        "analysis_id": analysis_id,

        "analysis_time": analysis_time,

        "platform": {},

        "detection": {},

        "fact_verification": {},

        "ocr": {
            "used": False,
            "extracted_text": "",
            "confidence": 0
        },

        "engagement": {},

        "spread_analysis": {},

        "prediction": {},

        "graph": {
            "nodes": [],
            "edges": []
        }

    }




    final_text = text or ""





    # =========================
    # OCR EXTRACTION
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

                "confidence": 98

            }



            if not final_text.strip():

                final_text = extracted_text







    # =========================
    # PLATFORM DETECTION
    # =========================


    response["platform"] = (

        platform_detector
        .detect_platform(
            final_text
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



        # COMPLETE NLP OUTPUT

        response["detection"] = {


            "status":

            detection_result.get(
                "status",
                "success"
            ),



            "prediction":

            detection_result.get(
                "prediction",
                "Normal"
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




            # CONTENT INTELLIGENCE

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




            # RISK ANALYSIS

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




            # ENTITY + INDICATORS

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







        # FACT VERIFICATION

        fact_result = verify_claim(

            final_text

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
    # ENGAGEMENT ANALYSIS
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


    platform_name = (

        response["platform"].get(
            "platform"
        )

    )




    response["spread_analysis"] = (

        spread_factor_service
        .analyze(

            engagement_data,

            content_analysis=response["detection"],

            platform=platform_name

        )

    )







    # =========================
    # SPREAD PREDICTION
    # =========================


    prediction_result = (

        prediction_service
        .predict_spread(
            engagement_data
        )

    )



    prediction_data = prediction_result.get(
        "data",
        {}
    )



    response["prediction"] = {


        "status":

        prediction_result.get(
            "status",
            "success"
        ),



        "predicted_reach":

        prediction_data.get(
            "predicted_reach",
            0
        ),



        "risk_level":

        prediction_data.get(
            "risk_level",
            ""
        ),



        "virality_score":

        prediction_data.get(
            "virality_score",
            0
        )

    }







    # =========================
    # SAVE TO MONGODB
    # =========================


    analysis_document = {


        "analysis_id":
        analysis_id,


        "userId":
        "test_user",


        "analysis_time":
        analysis_time,


        "platform":
        response["platform"],


        "detection":
        response["detection"],


        "fact_verification":
        response["fact_verification"],


        "ocr":
        response["ocr"],


        "engagement":
        response["engagement"],


        "spread_analysis":
        response["spread_analysis"],


        "prediction":
        response["prediction"],


        "graph":
        response["graph"]

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

        "status":"success",

        "analysis":response

    }
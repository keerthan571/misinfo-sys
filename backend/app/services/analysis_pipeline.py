import time
import uuid

from app.services.ocr_service import ocr_service
from app.services.nlp_service import nlp_service
from app.services.fact_verification_service import verify_claim
from app.services.engagement_service import engagement_service
from app.services.spread_factor_service import spread_factor_service
from app.services.prediction_service import prediction_service
from app.database.mongodb import analysis_collection


class AnalysisPipeline:

    async def run(self,text,image,platform,current_user):

        start=time.time()

        analysis_id=str(uuid.uuid4())

        extracted_text=""
        engagement_text=""
        raw_ocr_text=""

        if image:

            image_bytes=await image.read()

            ocr_result=ocr_service.extract_text_from_image(
                image_bytes
            )

            if ocr_result.get("status")=="success":

                extracted_text=ocr_result.get(
                    "extracted_text",
                    ""
                )

                engagement_text=ocr_result.get(
                    "raw_text",
                    ""
                )

                raw_ocr_text=ocr_result.get(
                    "raw_text",
                    ""
                )

        final_text=text.strip() if text else extracted_text

        if not final_text:
            final_text=extracted_text

        detection=nlp_service.analyze_text(
            final_text
        )

        claim=detection.get(
            "claim",
            final_text
        )

        fact_result=verify_claim(
            claim
        )

        print("========== ENGAGEMENT DEBUG ==========")
        print("PLATFORM:",platform)
        print("ENGAGEMENT TEXT:",engagement_text)
        print("======================================")

        engagement=engagement_service.extract_engagement(
            engagement_text,
            platform
        )

        print("========== FINAL ENGAGEMENT ==========")
        print(engagement)
        print("======================================")

        spread_analysis=spread_factor_service.analyze(
            engagement,
            detection,
            platform
        )

        prediction=prediction_service.predict_spread(
            {
                **engagement,
                "spread_score":spread_analysis["metrics"]["spread_score"],
                "risk_score":detection.get("risk_score",0),
                "emotion_score":0,
                "manipulation_score":0
            }
        )

        final_result={
            "label":fact_result.get(
                "verdict",
                "Insufficient Evidence"
            ),
            "confidence":self.convert_confidence(
                fact_result.get(
                    "confidence",
                    "0%"
                )
            ),
            "risk_level":prediction["data"]["risk_level"],
            "summary":spread_analysis["summary"]
        }

        response={
            "analysis_id":analysis_id,
            "platform":{
                "platform":platform
            },
            "ocr":{
                "used":bool(image),
                "extracted_text":extracted_text,
                "engagement_text":engagement_text
            },
            "detection":detection,
            "fact_verification":fact_result,
            "engagement":engagement,
            "spread_analysis":spread_analysis,
            "prediction":prediction["data"],
            "final_result":final_result,
            "metadata":{
                "analysis_id":analysis_id,
                "processing_status":"completed",
                "processing_time":round(
                    time.time()-start,
                    2
                )
            }
        }

        analysis_collection.insert_one(
            {
                **response,
                "user":current_user.get("email")
            }
        )

        return {
            "analysis":response
        }


    def convert_confidence(self,value):

        if isinstance(value,(int,float)):
            return value

        value=str(value).lower()

        if "high" in value:
            return 90

        if "medium" in value:
            return 70

        if "low" in value:
            return 40

        try:
            return float(
                value.replace("%","")
            )

        except:
            return 0


analysis_pipeline=AnalysisPipeline()
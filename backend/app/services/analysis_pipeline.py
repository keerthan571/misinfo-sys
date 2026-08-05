import time
import uuid
import io

from PIL import Image

from app.services.vision_engagement_detector import vision_engagement_detector
from app.services.nlp_service import nlp_service
from app.services.fact_verification_service import verify_claim
from app.services.spread_factor_service import spread_factor_service
from app.services.prediction_service import prediction_service
from app.database.mongodb import analysis_collection


class AnalysisPipeline:


    async def run(
        self,
        text,
        image,
        platform,
        current_user,
        followers=0,
        ocr_values={}
    ):

        start=time.time()

        analysis_id=str(uuid.uuid4())


        extracted_text=""
        engagement_values={}



        # IMAGE + GEMINI VISION

        if image:

            image_bytes=await image.read()


            img=Image.open(
                io.BytesIO(image_bytes)
            )

            img.load()



            vision_result=vision_engagement_detector.analyze(
                img,
                platform
            )



            extracted_text=vision_result.get(
                "post_text",
                ""
            )



            engagement_values=vision_result.get(
                "engagement",
                {}
            )



            if not isinstance(
                engagement_values,
                dict
            ):

                engagement_values={}





        # GEMINI FAILURE FALLBACK -> OCR VALUES

        if not engagement_values and ocr_values:


            print("USING OCR FALLBACK")


            for key,value in ocr_values.items():


                try:

                    clean=str(value).replace(
                        ",",
                        ""
                    )


                    clean=clean.lstrip("0")


                    if clean=="":

                        clean="0"



                    engagement_values[key]=int(clean)



                except:

                    continue




        # REMOVE OCR FALSE POSITIVES

        # 69 was coming from "69 ball century"
        if "bookmarks" in engagement_values:

            if engagement_values["bookmarks"] < 100:

                engagement_values["bookmarks"]=0




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




        print("========== VISION DEBUG ==========")

        print("PLATFORM:",platform)

        print("POST TEXT:",extracted_text)

        print("ENGAGEMENT:",engagement_values)

        print("==================================")




        engagement={

            **engagement_values,

            "metrics":[]

        }





        for key,value in engagement_values.items():


            if isinstance(value,(int,float)) and value>0:


                engagement["metrics"].append(
                    {
                        "label":key.title(),
                        "value":value
                    }
                )





        if platform.lower()=="instagram" and followers:


            engagement["followers"]=followers





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


                "spread_score":
                spread_analysis["metrics"]["spread_score"],


                "risk_score":
                detection.get(
                    "risk_score",
                    0
                ),


                "emotion_score":0,


                "manipulation_score":0

            }

        )







        final_result={


            "label":
            fact_result.get(
                "verdict",
                "Insufficient Evidence"
            ),



            "confidence":
            self.convert_confidence(
                fact_result.get(
                    "confidence",
                    "0%"
                )
            ),



            "risk_level":
            prediction["data"]["risk_level"],



            "summary":
            spread_analysis["summary"]

        }







        response={


            "analysis_id":analysis_id,


            "platform":{
                "platform":platform
            },



            "vision":{

                "used":bool(image),

                "post_text":extracted_text,

                "engagement_values":engagement_values

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

                "user":current_user.get(
                    "email"
                )

            }

        )



        return {

            "analysis":response

        }





    def convert_confidence(
        self,
        value
    ):


        if isinstance(
            value,
            (int,float)
        ):

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
                value.replace(
                    "%",
                    ""
                )
            )
        except:
            return 0
analysis_pipeline=AnalysisPipeline()
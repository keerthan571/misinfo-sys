import time
import uuid

from app.services.ocr_service import ocr_service
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
        followers=0
    ):


        start=time.time()

        analysis_id=str(uuid.uuid4())

        extracted_text=""
        engagement_values={}

        image_bytes=None



        # ================= OCR =================

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

                engagement_values=ocr_result.get(
                    "ordered_values",
                    {}
                )



        # ================= NLP =================


        final_text=text.strip() if text else extracted_text


        if not final_text:

            final_text=extracted_text



        detection=nlp_service.analyze_text(
            final_text
        )



        # ================= FACT =================


        claim=detection.get(
            "claim",
            final_text
        )


        fact_result=verify_claim(
            claim
        )



        # ================= ENGAGEMENT =================


        print("========== ENGAGEMENT DEBUG ==========")
        print("PLATFORM:",platform)
        print("OCR VALUES:",engagement_values)
        print("======================================")



        engagement={


            "likes":self.convert_number(
                engagement_values.get(
                    "likes",
                    0
                )
            ),


            "comments":self.convert_number(
                engagement_values.get(
                    "comments",
                    0
                )
            ),


            "reposts":self.convert_number(
                engagement_values.get(
                    "reposts",
                    0
                )
            ),


            "shares":self.convert_number(
                engagement_values.get(
                    "shares",
                    0
                )
            ),


            "bookmarks":self.convert_number(
                engagement_values.get(
                    "bookmarks",
                    0
                )
            ),


            "views":0,

            "metrics":[]

        }



        for key in [

            "likes",
            "comments",
            "reposts",
            "shares",
            "bookmarks"

        ]:


            if engagement[key] > 0:


                engagement["metrics"].append(

                    {
                        "label":key.title(),
                        "value":engagement[key]
                    }

                )




        if platform=="Instagram":

            engagement["platform"]="Instagram"

            engagement["followers"]=followers



        print("========== FINAL ENGAGEMENT ==========")
        print(engagement)
        print("======================================")




        # ================= SPREAD =================


        spread_analysis=spread_factor_service.analyze(

            engagement,

            detection,

            platform

        )





        # ================= PREDICTION =================


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





        # ================= FINAL =================


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


            "ocr":{

                "used":bool(image),

                "extracted_text":extracted_text,

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





    # ================= NUMBER CONVERTER =================


    def convert_number(self,value):


        if value is None:

            return 0



        value=str(value).replace(
            ",",
            ""
        ).strip()



        try:


            if value.lower().endswith("k"):

                return int(
                    float(value[:-1]) * 1000
                )



            if value.lower().endswith("m"):

                return int(
                    float(value[:-1]) * 1000000
                )



            return int(
                float(value)
            )



        except:


            return 0






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
                value.replace(
                    "%",
                    ""
                )
            )


        except:

            return 0




analysis_pipeline=AnalysisPipeline()
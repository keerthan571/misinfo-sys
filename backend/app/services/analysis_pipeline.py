import time
import uuid
import io

from PIL import Image

import cv2
import numpy as np


from app.services.vision_engagement_detector import vision_engagement_detector
from app.services.engagement_extractor import engagement_extractor

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
        ocr_values=None
    ):


        start = time.time()


        analysis_id = str(uuid.uuid4())



        if ocr_values is None:

            ocr_values = {}



        extracted_text = ""



        # ALWAYS KEEP ALL ENGAGEMENT FIELDS

        engagement_values = {

            "likes":0,

            "comments":0,

            "reposts":0,

            "shares":0,

            "bookmarks":0

        }




        # ============================
        # IMAGE PROCESSING
        # ============================


        if image:


            image_bytes = await image.read()



            pil_image = Image.open(
                io.BytesIO(image_bytes)
            )


            pil_image.load()



            img = np.array(
                pil_image
            )


            img = cv2.cvtColor(
                img,
                cv2.COLOR_RGB2BGR
            )




            # ============================
            # OPENCV ICON DETECTION
            # ============================


            opencv_engagement = engagement_extractor.analyze(
                img
            )


            engagement_values.update(
                opencv_engagement
            )



            print(
                "========== OPENCV ENGAGEMENT =========="
            )

            print(
                engagement_values
            )

            print(
                "========================================"
            )





            # ============================
            # GEMINI TEXT EXTRACTION ONLY
            # ============================


            try:


                vision_result = vision_engagement_detector.analyze(
                    pil_image,
                    platform
                )


                extracted_text = vision_result.get(
                    "post_text",
                    ""
                )



            except Exception as e:


                print(
                    "VISION TEXT ERROR:",
                    e
                )


                extracted_text = ""







        # ============================
        # OCR FALLBACK
        # ONLY UPDATE EXISTING VALUES
        # ============================


        if ocr_values:


            for key,value in ocr_values.items():


                if key not in engagement_values:

                    continue



                if engagement_values[key] == 0:


                    try:


                        clean = str(value).replace(
                            ",",
                            ""
                        )


                        clean = clean.lower()



                        if "k" in clean:


                            number=float(
                                clean.replace(
                                    "k",
                                    ""
                                )
                            ) * 1000



                        elif "m" in clean:


                            number=float(
                                clean.replace(
                                    "m",
                                    ""
                                )
                            ) * 1000000



                        else:


                            number=int(clean)



                        engagement_values[key]=int(number)



                    except:

                        pass







        final_text = text.strip() if text else extracted_text



        detection = nlp_service.analyze_text(
            final_text
        )



        claim = detection.get(
            "claim",
            final_text
        )



        fact_result = verify_claim(
            claim
        )





        print(
            "========== FINAL DEBUG =========="
        )


        print(
            "PLATFORM:",
            platform
        )


        print(
            "TEXT:",
            extracted_text
        )


        print(
            "ENGAGEMENT:",
            engagement_values
        )


        print(
            "================================="
        )






        engagement = {


            **engagement_values,


            "metrics":[]

        }




        for key,value in engagement_values.items():


            if value > 0:


                engagement["metrics"].append(

                    {

                        "label":key.title(),

                        "value":value

                    }

                )






        if platform.lower()=="instagram" and followers:


            engagement["followers"]=followers






        spread_analysis = spread_factor_service.analyze(

            engagement,

            detection,

            platform

        )







        prediction = prediction_service.predict_spread(

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








        final_result = {


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









        response = {


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





analysis_pipeline = AnalysisPipeline()
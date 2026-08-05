import time
import uuid
from ..database.mongodb import analyses_collection
from .engagement_service import engagement_service
from .fact_verification_service import verify_claim

from .nlp_service import nlp_service
from .ocr_service import ocr_service
from .platform_detector import platform_detector
from .prediction_service import prediction_service
from .spread_factor_service import spread_factor_service

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


        start=time.time()

        analysis_id=str(uuid.uuid4())
        analysis_time=datetime.now(timezone.utc).isoformat()
        return{
            "analysis_id":analysis_id,
            "analysis_time":analysis_time,
            "final_result":{},
            "platform":{},
            "detection":{},
            "fact_verification":{},
            "ocr":{
                "used":False,
                "extracted_text":"",
                "confidence":0,
                "word_count":0
            },
            "engagement":{},
            "spread_analysis":{},
            "prediction":{},
            "graph":{}
        },analysis_id,analysis_time
    async def _run_ocr(self, image, final_text, response):

        extracted_text = ""

        if image:

            image_bytes = await image.read()

            ocr_result = ocr_service.extract_text_from_image(image_bytes)

            if ocr_result.get("status") == "success":

                extracted_text = ocr_result.get(
                    "extracted_text",
                    ""
                )

                response["ocr"] = {
                    "used": True,
                    "extracted_text": extracted_text,
                    "confidence": ocr_result.get("confidence", 0),
                    "word_count": len(extracted_text.split())
                }

                if not final_text.strip():
                    final_text = extracted_text

        return final_text, extracted_text
    def _detect_platform(self,final_text,extracted_text,response):
        platform_text=final_text
        if extracted_text:
            platform_text+=" "+extracted_text
        response["platform"]=platform_detector.detect_platform(platform_text)
    def _run_nlp(self,final_text,response):
        if not final_text.strip():
            return
        detection_result=nlp_service.analyze_text(final_text)
        response["detection"]={
            "language":detection_result.get("language","Unknown"),
            "keywords":detection_result.get("keywords",[]),
            "manipulation_signals":detection_result.get("manipulation_signals",[]),
            "similar_claim":detection_result.get("similar_claim",False),
            "status":detection_result.get("status","success"),
            "claim":detection_result.get("claim",final_text),
            "prediction":detection_result.get("prediction","Needs Verification"),
            "confidence":self.safe_confidence(detection_result.get("confidence",0)),
            "reason":detection_result.get("reason",""),
            "content_type":detection_result.get("content_type","Other"),
            "claim_type":detection_result.get("claim_type","Other"),
            "temporal_context":detection_result.get("temporal_context","Unknown"),
            "risk_level":detection_result.get("risk_level","Low"),
            "risk_score":detection_result.get("risk_score",0),
            "entities":detection_result.get("entities",[]),
            "indicators":detection_result.get("indicators",[])
        }
    def _verify_fact(self,final_text,response):
        if not response["detection"]:
            return
        fact_result=verify_claim(response["detection"].get("claim",final_text))
        response["fact_verification"]={
            "status":fact_result.get("status","failed"),
            "claim":fact_result.get("claim",""),
            "verdict":fact_result.get("verdict",""),
            "reason":fact_result.get("reason",""),
            "confidence":self.safe_confidence(fact_result.get("confidence",0)),
            "sources":fact_result.get("sources",[])
        }
    async def run(self,text,image,current_user):
        start_time=time.time()
        response,analysis_id,analysis_time=self._initialize_response()
        final_text=text or ""
        final_text,extracted_text=await self._run_ocr(image,final_text,response)
        self._detect_platform(final_text,extracted_text,response)
        self._run_nlp(final_text,response)
        self._verify_fact(final_text,response)
        self._analyze_engagement(final_text,response)
        self._generate_graph(final_text,response)
        processing_time=round(time.time()-start_time,2)
        self._save_analysis(current_user,analysis_id,analysis_time,final_text,response,processing_time)
        
        return self._build_response(response,analysis_id,analysis_time,processing_time)
        
    def _analyze_engagement(self,final_text,response):
        engagement_data=engagement_service.extract_engagement(final_text)
        response["engagement"]=engagement_data
        response["spread_analysis"]=spread_factor_service.analyze(
            engagement_data,
            content_analysis=response["detection"],
            platform=response["platform"].get("platform")
        )
        prediction_result=prediction_service.predict_spread({
            **engagement_data,
            "spread_score":response["spread_analysis"].get("metrics",{}).get("spread_score",0),
            "risk_score":response["detection"].get("risk_score",0)
        })
        prediction_data=prediction_result.get("data",{})
        response["prediction"]={
            "status":prediction_result.get("status","success"),
            "predicted_reach":prediction_data.get("predicted_reach",0),
            "risk_level":prediction_data.get("risk_level",""),
            "virality_score":prediction_data.get("virality_score",0)
        }
        response["final_result"]=self.generate_final_result(response)
    
    def _generate_graph(self, final_text, response):
        ai_result = {
            "text": final_text,
            "platform": response["platform"],
            "detection": response["detection"],
            "fact_verification": response["fact_verification"],
            "engagement": response["engagement"],
            "spread_analysis": response["spread_analysis"],
            "prediction": response["prediction"],
            "final_result": response["final_result"],
        }

        
    def _save_analysis(self,current_user,analysis_id,analysis_time,final_text,response,processing_time):
        analysis_document={
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





analysis_pipeline = AnalysisPipeline()
from datetime import datetime, timezone
import time
import uuid
import os
import shutil
from ..database.mongodb import analyses_collection
from .engagement_service import engagement_service
from .fact_verification_service import verify_claim
from .graph_service import build_graph
from .nlp_service import nlp_service
from .ocr_service import ocr_service
from .platform_detector import platform_detector
from .prediction_service import prediction_service
from .spread_factor_service import spread_factor_service

class AnalysisPipeline:
    def __init__(self):
        pass
    async def _save_uploaded_image(self, image, analysis_id):

        if not image:
            return None

        upload_dir = "uploads"

        os.makedirs(
            upload_dir,
            exist_ok=True
        )

        extension = os.path.splitext(
            image.filename
        )[1]

        filename = f"{analysis_id}{extension}"

        file_path = os.path.join(
            upload_dir,
            filename
        )

        image.file.seek(0)

        with open(
            file_path,
            "wb"
        ) as buffer:

            shutil.copyfileobj(
                image.file,
                buffer
            )

        return file_path
    @staticmethod
    def safe_confidence(value):
        try:
            return int(str(value).replace("%",""))
        except Exception:
            return 0
    @staticmethod
    def generate_final_result(response):
        detection=response.get("detection",{})
        fact=response.get("fact_verification",{})
        prediction=response.get("prediction",{})
        detection_conf=AnalysisPipeline.safe_confidence(detection.get("confidence",0))
        fact_conf=AnalysisPipeline.safe_confidence(fact.get("confidence",0))
        virality_score=int(prediction.get("virality_score",0))
        final_confidence=int(detection_conf*0.5+fact_conf*0.3+virality_score*0.2)
        verdict=str(fact.get("verdict","")).lower()
        if "false" in verdict or "fake" in verdict:
            label="False Information"
        elif "verified" in verdict or "true" in verdict:
            label="Verified Information"
        elif "misleading" in verdict:
            label="Misleading Information"
        else:
            label="Insufficient Evidence"
        if final_confidence>=75:
            risk_level="High"
        elif final_confidence>=40:
            risk_level="Medium"
        else:
            risk_level="Low"
        return{
            "label":label,
            "confidence":final_confidence,
            "risk_level":risk_level,
            "summary":f"Final analysis result: {label} with {final_confidence}% confidence."
        }
    def _initialize_response(self):
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
    # Image uploaded -> OCR should run
        if image:
            image_bytes = await image.read()
            ocr_result = ocr_service.extract_text_from_image(
                image_bytes
            )
            if ocr_result.get("status") == "success":
                extracted_text = ocr_result.get(
                "extracted_text",
                ""
                )
                response["ocr"] = {
                    "used": True,
                    "input_type": "Image",
                    "status": "OCR Completed",
                    "extracted_text": extracted_text,
                    "confidence": ocr_result.get(
                        "confidence",
                        0
                    ),

                    "word_count": len(
                        extracted_text.split()
                    )
                }
                # OCR text becomes analysis text
                if extracted_text.strip():
                    final_text = extracted_text
                # Text only input
        elif final_text.strip():

            response["ocr"] = {

                "used": False,

                "input_type": "Direct Text",

                "status": "Not Required",

                "extracted_text":
                    "User entered text directly. OCR was not required.",
                "confidence": 0,

                "word_count": len(
                    final_text.split()
                )
            }


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
        image_path = await self._save_uploaded_image(
            image,
            analysis_id
        )
        response["image"] = {
            "uploaded": bool(image_path),
            "path": image_path
        }
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
            "spread_probability":prediction_data.get("spread_probability",None),
            "risk_level":prediction_data.get("risk_level",""),
            "virality_score":prediction_data.get("virality_score",0),
            "features_used":prediction_data.get("features_used",{}),
            "analysis_summary":prediction_result.get("analysis_summary","")
        }
        response["final_result"]=self.generate_final_result(response)
    def _generate_graph(self,final_text,response):
        graph_input={
            "text":final_text,
            "platform":response["platform"],
            "detection":response["detection"],
            "fact_verification":response["fact_verification"],
            "engagement":response["engagement"],
            "spread_analysis":response["spread_analysis"],
            "prediction":response["prediction"],
            "final_result":response["final_result"]
        }
        try:
            response["graph"]=build_graph(graph_input)
        except Exception as e:
            response["graph"]={
                "nodes":[],
                "edges":[],
                "error":str(e)
            }
    def _save_analysis(self,current_user,analysis_id,analysis_time,final_text,response,processing_time):
        analysis_document={
            "analysis_id":analysis_id,
            "email":current_user["email"],
            "userId":current_user["email"],
            "text":final_text,
            "analysis_time":analysis_time,
            "platform":response["platform"],
            "final_result":response["final_result"],
            "detection":response["detection"],
            "fact_verification":response["fact_verification"],
            "ocr":response["ocr"],
            "image":response.get("image",{}),
            "engagement":response["engagement"],
            "spread_analysis":response["spread_analysis"],
            "prediction":response["prediction"],
            "graph":response["graph"],
            "metadata":{
                "processing_time":processing_time,
                "text_length":len(final_text),
                "word_count":len(final_text.split()),
                "pipeline_version":"2.0",
                "created_at":analysis_time
            }
        }
        try:
            analyses_collection.insert_one(analysis_document)
        except Exception as e:
            print("MongoDB Error:",e)
    def _build_response(self,response,analysis_id,analysis_time,processing_time):
        return{
            "status":"success",
            "analysis_id":analysis_id,
            "processing_time":processing_time,
            "analysis":{
                **response,
                "verification_status":response["fact_verification"].get("verdict","Insufficient Evidence"),
                "spread_prediction":response["prediction"],
                "metadata":{
                    "analysis_id":analysis_id,
                    "timestamp":analysis_time,
                    "processing_time":processing_time,
                    "processing_status":"completed"
                }
            }
        }
        
analysis_pipeline = AnalysisPipeline()
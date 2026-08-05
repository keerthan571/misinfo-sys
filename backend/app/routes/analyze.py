from fastapi import APIRouter, Depends, File, Form, UploadFile
import json

from app.auth.dependencies import get_current_user
from app.services.analysis_pipeline import analysis_pipeline


router = APIRouter()



@router.post("/")
async def analyze(

    text: str = Form(None),

    platform: str = Form(None),

    followers: int = Form(0),

    ocr_engagement: str = Form("{}"),

    image: UploadFile = File(None),

    current_user = Depends(get_current_user),

):


    try:

        ocr_values = json.loads(
            ocr_engagement
        )

    except:

        ocr_values = {}



    return await analysis_pipeline.run(

        text=text,

        image=image,

        platform=platform,

        current_user=current_user,

        followers=followers,

        ocr_values=ocr_values

    )
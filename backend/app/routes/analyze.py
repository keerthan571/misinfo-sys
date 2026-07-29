from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    UploadFile,
)

from app.auth.dependencies import get_current_user

from app.services.analysis_pipeline import (
    analysis_pipeline,
)

router = APIRouter()


@router.post("/")
async def analyze(
    text: str = Form(None),
    image: UploadFile = File(None),
    current_user=Depends(get_current_user),
):
    """
    Complete AI Analysis Pipeline
    """

    return await analysis_pipeline.run(
        text=text,
        image=image,
        current_user=current_user,
    )
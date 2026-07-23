from fastapi import APIRouter
from pydantic import BaseModel
from ..services.nlp_service import nlp_service

router = APIRouter()

class TextRequest(BaseModel):
    text: str

@router.post("/")
def detect_misinformation(request: TextRequest):
    """
    Endpoint to classify text as true or fake using the NLP service.
    """
    result = nlp_service.analyze_text(request.text)
    return result

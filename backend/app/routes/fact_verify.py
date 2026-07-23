from fastapi import APIRouter
from pydantic import BaseModel

from app.services.fact_verification_service import verify_claim

router = APIRouter()


class FactRequest(BaseModel):
    claim: str


@router.post("/")
def fact_verify(request: FactRequest):
    return verify_claim(request.claim)
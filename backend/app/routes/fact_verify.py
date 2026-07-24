from fastapi import APIRouter
from pydantic import BaseModel

from app.services.fact_verification_service import verify_claim

router = APIRouter()


class FactRequest(BaseModel):
    claim: str


class FactResponse(BaseModel):
    status: str
    claim: str | None = None
    verdict: str | None = None
    reason: str | None = None
    confidence: str | None = None
    sources: list[str] | None = None
    message: str | None = None


@router.post("/", response_model=FactResponse)
def fact_verify(request: FactRequest):
    return verify_claim(request.claim)
from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()

class FactCheckRequest(BaseModel):
    claim: str

@router.post("/verify")
async def verify_facts(request: FactCheckRequest):
    return {
        "verified": True,
        "confidence": 0.95,
        "sources": []
    }
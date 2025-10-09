from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime
from .base import BaseSchema

class PIICheckRequest(BaseModel):
    text: str = Field(..., min_length=1)
    mask_detected: bool = True

class PIIToken(BaseSchema):
    token_id: str
    user_id: str
    data_type: str
    is_active: bool = True
    expires_at: Optional[datetime] = None

class PIICheckResponse(BaseSchema):
    has_pii: bool
    detected_types: List[str]
    risk_level: str
    masked_text: Optional[str]
    tokens: Optional[Dict[str, str]]
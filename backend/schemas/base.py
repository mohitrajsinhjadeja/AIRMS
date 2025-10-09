from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, Dict, Any

class BaseSchema(BaseModel):
    id: Optional[str] = Field(None, description="Unique identifier")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)

    class Config:
        validate_assignment = True
        arbitrary_types_allowed = True
        json_encoders = {
            datetime: lambda dt: dt.isoformat()
        }
        
    def update_timestamp(self):
        self.updated_at = datetime.utcnow()
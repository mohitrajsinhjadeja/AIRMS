from typing import Dict, Any
from datetime import datetime

class BaseService:
    def __init__(self):
        self.start_time = datetime.utcnow()
        
    def format_response(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Format service response with metadata"""
        return {
            **data,
            "processing_time_ms": int((datetime.utcnow() - self.start_time).total_seconds() * 1000),
            "timestamp": datetime.utcnow()
        }
from typing import Dict, Any
from datetime import datetime

class BaseDetector:
    def __init__(self):
        self.name = self.__class__.__name__

    async def detect(self, text: str) -> Dict[str, Any]:
        """Base detection method to be implemented by specific detectors"""
        raise NotImplementedError
    
    def format_response(self, detected: bool, score: float, details: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "detected": detected,
            "score": score,
            "detector": self.name,
            "timestamp": datetime.utcnow().isoformat(),
            "details": details
        }
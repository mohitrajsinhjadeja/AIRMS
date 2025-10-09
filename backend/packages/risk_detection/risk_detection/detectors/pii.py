import re
from .base import BaseDetector

class PIIDetector(BaseDetector):
    def __init__(self):
        super().__init__()
        self.patterns = {
            "email": r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            "phone": r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b',
            "ssn": r'\b\d{3}-\d{2}-\d{4}\b'
        }

    async def detect(self, text: str) -> dict:
        detected_items = {}
        for pii_type, pattern in self.patterns.items():
            matches = re.findall(pattern, text)
            if matches:
                detected_items[pii_type] = len(matches)
        
        score = min(len(detected_items) * 0.3, 1.0)
        return self.format_response(
            detected=bool(detected_items),
            score=score,
            details={"found_types": list(detected_items.keys())}
        )
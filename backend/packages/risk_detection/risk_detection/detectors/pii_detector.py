from .base import BaseDetector
import re

class PIIDetector(BaseDetector):
    def __init__(self):
        super().__init__()
        self.detector_type = "pii"
        
    def detect(self, input_text: str) -> dict:
        # Basic PII patterns
        patterns = {
            "email": r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            "phone": r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b',
            "ssn": r'\b\d{3}-\d{2}-\d{4}\b'
        }
        
        detected_items = {}
        for pii_type, pattern in patterns.items():
            matches = re.findall(pattern, input_text)
            if matches:
                detected_items[pii_type] = len(matches)
        
        detected = len(detected_items) > 0
        score = min(len(detected_items) * 0.3, 1.0)
        
        return self.format_response(
            detected=detected,
            score=score,
            details={
                "detected_types": list(detected_items.keys()),
                "item_counts": detected_items
            }
        )
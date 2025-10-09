from .base import BaseDetector

class AdversarialDetector(BaseDetector):
    def detect(self, input_text: str) -> dict:
        return {
            "is_adversarial": False,
            "confidence": 0.0,
            "attack_type": None
        }
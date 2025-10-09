from .base import BaseDetector

class BiasDetector(BaseDetector):
    def __init__(self):
        super().__init__()
        self.detector_type = "bias"
        
    def detect(self, input_text: str) -> dict:
        bias_categories = {
            "gender": ["he/she", "man/woman", "male/female"],
            "racial": ["race", "ethnic", "minority"],
            "political": ["liberal", "conservative", "republican", "democrat"],
            "cultural": ["western", "eastern", "traditional", "modern"]
        }
        
        detected_biases = {}
        for category, terms in bias_categories.items():
            matches = [term for term in terms if term.lower() in input_text.lower()]
            if matches:
                detected_biases[category] = matches
        
        score = min(len(detected_biases) * 0.25, 1.0)
        
        return self.format_response(
            detected=score > 0.2,
            score=score,
            details={
                "categories": list(detected_biases.keys()),
                "detected_terms": detected_biases,
                "severity": "high" if score > 0.7 else "medium" if score > 0.3 else "low"
            }
        )
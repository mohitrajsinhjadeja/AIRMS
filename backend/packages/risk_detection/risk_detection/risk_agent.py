from typing import Dict, Any
from .detectors import PIIDetector, BiasDetector, HallucinationDetector, AdversarialDetector

class RiskAgent:
    def __init__(self):
        self.detectors = {
            "pii": PIIDetector(),
            "bias": BiasDetector(),
            "hallucination": HallucinationDetector(),
            "adversarial": AdversarialDetector()
        }
    
    async def analyze(self, text: str) -> Dict[str, Any]:
        results = {}
        for name, detector in self.detectors.items():
            try:
                results[name] = await detector.detect(text)
            except Exception as e:
                results[name] = {
                    "error": str(e),
                    "detected": False,
                    "score": 0.0
                }
        
        return {
            "results": results,
            "risk_score": self._calculate_risk_score(results)
        }
    
    def _calculate_risk_score(self, results: Dict[str, Any]) -> float:
        weights = {
            "pii": 0.3,
            "bias": 0.2,
            "hallucination": 0.3,
            "adversarial": 0.2
        }
        
        total_score = 0.0
        for detector_name, result in results.items():
            if not isinstance(result, dict) or "score" not in result:
                continue
            total_score += result["score"] * weights.get(detector_name, 0.1)
        
        return min(total_score * 10, 10.0)
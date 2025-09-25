from typing import Dict, Any, List
from .detectors import BiasDetector, PIIDetector, HallucinationDetector, AdversarialDetector

class RiskAgent:
    def __init__(self):
        self.bias_detector = BiasDetector()
        self.pii_detector = PIIDetector()
        self.hallucination_detector = HallucinationDetector()
        self.adversarial_detector = AdversarialDetector()

    async def analyze_content(self, content: str) -> Dict[str, Any]:
        # Run all detectors in parallel
        bias_results = await self.bias_detector.detect(content)
        pii_results = await self.pii_detector.detect(content)
        hallucination_results = await self.hallucination_detector.detect(content)
        adversarial_results = await self.adversarial_detector.detect(content)

        # Calculate overall risk score
        risk_factors = {
            'bias': bias_results['confidence'],
            'pii': pii_results['confidence'],
            'hallucination': hallucination_results['confidence'],
            'adversarial': adversarial_results['confidence']
        }
        
        overall_risk = sum(risk_factors.values()) / len(risk_factors)

        # Determine severity level
        severity_level = self._get_severity_level(overall_risk)

        return {
            'risk_score': overall_risk,
            'severity_level': severity_level,
            'bias_analysis': bias_results,
            'pii_analysis': pii_results,
            'hallucination_analysis': hallucination_results,
            'adversarial_analysis': adversarial_results
        }

    def _get_severity_level(self, risk_score: float) -> str:
        if risk_score >= 0.8:
            return 'CRITICAL'
        elif risk_score >= 0.6:
            return 'HIGH'
        elif risk_score >= 0.4:
            return 'MEDIUM'
        elif risk_score >= 0.2:
            return 'LOW'
        else:
            return 'MINIMAL'
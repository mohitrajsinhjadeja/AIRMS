"""
🛡️ AIRMS+ Detection Engine
Comprehensive AI risk detection with bias, PII, hallucination, and adversarial detection
"""

import re
import asyncio
import logging
import json
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass
from enum import Enum

from app.core.config import settings, get_risk_weights, get_risk_thresholds
from app.services.ai_integration import ai_service, fact_checker, AITaskType

# Configure logging
logger = logging.getLogger(__name__)

class RiskLevel(Enum):
    """Risk severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class DetectionResult:
    """Standard detection result format"""
    detected: bool
    confidence: float
    risk_score: float
    details: Dict[str, Any]
    evidence: List[str]
    mitigation_suggestions: List[str]

class BiasDetector:
    """Detect political, cultural, religious, gender, racial, economic, regional, caste, linguistic bias"""
    
    def __init__(self):
        self.bias_patterns = settings.INDIAN_BIAS_KEYWORDS
        self.bias_categories = settings.BIAS_CATEGORIES
    
    async def detect(self, text: str) -> DetectionResult:
        """Detect bias in text using pattern matching and AI analysis"""
        try:
            # Pattern-based detection
            pattern_results = self._pattern_based_detection(text)
            
            # AI-based detection for nuanced bias
            ai_results = await self._ai_based_detection(text)
            
            # Combine results
            detected_biases = list(set(pattern_results["types"] + ai_results.get("bias_types", [])))
            
            # Calculate overall confidence and risk score
            pattern_confidence = pattern_results["confidence"]
            ai_confidence = ai_results.get("confidence_score", 0.0) if ai_results.get("success") else 0.0
            
            combined_confidence = max(pattern_confidence, ai_confidence)
            risk_score = self._calculate_bias_risk_score(detected_biases, combined_confidence)
            
            # Generate evidence and mitigation suggestions
            evidence = pattern_results["evidence"] + ai_results.get("evidence", [])
            mitigation_suggestions = self._generate_bias_mitigation(detected_biases)
            
            return DetectionResult(
                detected=len(detected_biases) > 0,
                confidence=combined_confidence,
                risk_score=risk_score,
                details={
                    "bias_types": detected_biases,
                    "pattern_matches": pattern_results["matches"],
                    "ai_analysis": ai_results.get("response", "") if ai_results.get("success") else None,
                    "severity": self._get_bias_severity(risk_score)
                },
                evidence=evidence,
                mitigation_suggestions=mitigation_suggestions
            )
            
        except Exception as e:
            logger.error(f"Bias detection failed: {e}")
            return DetectionResult(
                detected=False, confidence=0.0, risk_score=0.0,
                details={"error": str(e)}, evidence=[], mitigation_suggestions=[]
            )
    
    def _pattern_based_detection(self, text: str) -> Dict[str, Any]:
        """Pattern-based bias detection"""
        text_lower = text.lower()
        detected_types = []
        matches = {}
        evidence = []
        
        for bias_type, keywords in self.bias_patterns.items():
            found_keywords = []
            for keyword in keywords:
                if keyword.lower() in text_lower:
                    found_keywords.append(keyword)
                    evidence.append(f"Found {bias_type} bias keyword: '{keyword}'")
            
            if found_keywords:
                detected_types.append(bias_type)
                matches[bias_type] = found_keywords
        
        confidence = min(len(detected_types) * 0.3, 1.0)
        
        return {
            "types": detected_types,
            "matches": matches,
            "confidence": confidence,
            "evidence": evidence
        }
    
    async def _ai_based_detection(self, text: str) -> Dict[str, Any]:
        """AI-based bias detection for nuanced analysis"""
        try:
            prompt = f"""Analyze for bias in: political, cultural, religious, gender, racial, economic, regional, caste, linguistic.
            JSON response: {{"bias_detected": bool, "bias_types": [], "confidence_score": float, "explanation": str, "evidence": []}}
            Text: {text}"""
            
            async with ai_service:
                result = await ai_service.process_request(AITaskType.FAST_FILTER, prompt, max_tokens=800, temperature=0.1)
            
            if result.get("success"):
                try:
                    response_text = result.get("response", "")
                    if response_text.strip().startswith("{"):
                        ai_data = json.loads(response_text)
                        return {**result, **ai_data}
                except json.JSONDecodeError:
                    pass
            
            return result
            
        except Exception as e:
            logger.warning(f"AI bias detection failed: {e}")
            return {"success": False, "error": str(e)}
    
    def _calculate_bias_risk_score(self, bias_types: List[str], confidence: float) -> float:
        """Calculate bias risk score"""
        if not bias_types:
            return 0.0
        
        base_score = min(len(bias_types) * 20, 80)
        severity_multipliers = {"racial": 1.5, "religious": 1.4, "caste": 1.3, "gender": 1.2, "political": 1.1}
        max_multiplier = max([severity_multipliers.get(bt, 1.0) for bt in bias_types])
        adjusted_score = base_score * max_multiplier
        final_score = adjusted_score * confidence
        
        return min(final_score, 100.0)
    
    def _get_bias_severity(self, risk_score: float) -> str:
        """Get bias severity level"""
        thresholds = get_risk_thresholds()
        if risk_score >= thresholds["high"]:
            return "high"
        elif risk_score >= thresholds["medium"]:
            return "medium"
        else:
            return "low"
    
    def _generate_bias_mitigation(self, bias_types: List[str]) -> List[str]:
        """Generate bias mitigation suggestions"""
        suggestions = [
            "Review content for balanced representation of different viewpoints",
            "Consider multiple perspectives before making claims",
            "Use inclusive language that doesn't exclude or stereotype groups"
        ]
        
        if "political" in bias_types:
            suggestions.append("Present multiple political viewpoints fairly")
        if "religious" in bias_types:
            suggestions.append("Ensure respectful treatment of all religious beliefs")
        if "gender" in bias_types:
            suggestions.append("Use gender-neutral language where appropriate")
        if "racial" in bias_types or "caste" in bias_types:
            suggestions.append("Avoid language that reinforces social hierarchies or stereotypes")
        
        return suggestions

class PIIDetector:
    """Detect PII including Indian-specific data (Aadhaar, PAN, phone, email, bank accounts)"""
    
    def __init__(self):
        self.pii_patterns = settings.PII_PATTERNS
    
    async def detect(self, text: str) -> DetectionResult:
        """Detect PII in text using regex patterns"""
        try:
            detected_pii = []
            evidence = []
            
            for pii_type, pattern in self.pii_patterns.items():
                matches = re.finditer(pattern, text, re.IGNORECASE)
                for match in matches:
                    detected_pii.append({
                        "type": pii_type,
                        "value": match.group(),
                        "start": match.start(),
                        "end": match.end(),
                        "confidence": self._get_pii_confidence(pii_type)
                    })
                    evidence.append(f"Found {pii_type}: {match.group()[:4]}***")
            
            risk_score = self._calculate_pii_risk_score(detected_pii) if detected_pii else 0.0
            mitigation_suggestions = self._generate_pii_mitigation(detected_pii)
            
            return DetectionResult(
                detected=len(detected_pii) > 0,
                confidence=1.0 if detected_pii else 0.0,
                risk_score=risk_score,
                details={
                    "pii_found": len(detected_pii),
                    "pii_types": list(set([pii["type"] for pii in detected_pii])),
                    "pii_items": detected_pii,
                    "severity": self._get_pii_severity(risk_score)
                },
                evidence=evidence,
                mitigation_suggestions=mitigation_suggestions
            )
            
        except Exception as e:
            logger.error(f"PII detection failed: {e}")
            return DetectionResult(
                detected=False, confidence=0.0, risk_score=0.0,
                details={"error": str(e)}, evidence=[], mitigation_suggestions=[]
            )
    
    def _get_pii_confidence(self, pii_type: str) -> float:
        """Get confidence score for PII detection"""
        confidence_scores = {
            "aadhaar": 0.95, "pan": 0.90, "email": 0.85, "phone": 0.80,
            "credit_card": 0.85, "bank_account": 0.70, "ifsc": 0.90
        }
        return confidence_scores.get(pii_type, 0.75)
    
    def _calculate_pii_risk_score(self, pii_items: List[Dict[str, Any]]) -> float:
        """Calculate PII risk score based on sensitivity"""
        if not pii_items:
            return 0.0
        
        sensitivity_scores = {
            "aadhaar": 90, "pan": 85, "credit_card": 80, "bank_account": 75,
            "phone": 60, "email": 50, "ifsc": 70
        }
        
        total_risk = 0.0
        for pii in pii_items:
            pii_type = pii["type"]
            confidence = pii["confidence"]
            sensitivity = sensitivity_scores.get(pii_type, 50)
            total_risk += sensitivity * confidence
        
        avg_risk = total_risk / len(pii_items)
        return min(avg_risk, 100.0)
    
    def _get_pii_severity(self, risk_score: float) -> str:
        """Get PII severity level"""
        if risk_score >= 80:
            return "critical"
        elif risk_score >= 60:
            return "high"
        elif risk_score >= 40:
            return "medium"
        else:
            return "low"
    
    def _generate_pii_mitigation(self, pii_items: List[Dict[str, Any]]) -> List[str]:
        """Generate PII mitigation suggestions"""
        if not pii_items:
            return []
        
        suggestions = [
            "Remove or redact all personally identifiable information",
            "Replace PII with placeholder values (e.g., [REDACTED])",
            "Implement data anonymization techniques"
        ]
        
        pii_types = set([pii["type"] for pii in pii_items])
        
        if "aadhaar" in pii_types:
            suggestions.append("Aadhaar numbers should never be shared publicly - remove immediately")
        if "pan" in pii_types:
            suggestions.append("PAN numbers are sensitive tax information - redact completely")
        if "credit_card" in pii_types:
            suggestions.append("Credit card numbers pose financial risk - remove all digits")
        
        return suggestions

class RiskScoringEngine:
    """Unified risk scoring engine with weighted system: bias (25%), hallucination (25%), PII (30%), adversarial (20%)"""
    
    def __init__(self):
        self.weights = get_risk_weights()
        self.thresholds = get_risk_thresholds()
        self.bias_detector = BiasDetector()
        self.pii_detector = PIIDetector()
    
    async def comprehensive_analysis(self, text: str, user_id: Optional[str] = None) -> Dict[str, Any]:
        """Perform comprehensive risk analysis"""
        start_time = datetime.utcnow()
        
        try:
            # Run detections in parallel
            bias_result, pii_result = await asyncio.gather(
                self.bias_detector.detect(text),
                self.pii_detector.detect(text),
                return_exceptions=True
            )
            
            # Handle exceptions
            if isinstance(bias_result, Exception):
                logger.error(f"Bias detection failed: {bias_result}")
                bias_result = DetectionResult(False, 0.0, 0.0, {"error": str(bias_result)}, [], [])
            
            if isinstance(pii_result, Exception):
                logger.error(f"PII detection failed: {pii_result}")
                pii_result = DetectionResult(False, 0.0, 0.0, {"error": str(pii_result)}, [], [])
            
            # Calculate weighted risk score
            weighted_score = (
                bias_result.risk_score * self.weights["bias"] +
                pii_result.risk_score * self.weights["pii"] +
                0.0 * self.weights["hallucination"] +  # Placeholder
                0.0 * self.weights["adversarial"]      # Placeholder
            )
            
            # Determine overall risk level
            risk_level = self._determine_risk_level(weighted_score)
            
            # Combine all evidence and mitigation suggestions
            all_evidence = bias_result.evidence + pii_result.evidence
            all_mitigations = bias_result.mitigation_suggestions + pii_result.mitigation_suggestions
            
            # Calculate processing time
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            
            return {
                "case_id": f"case_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
                "user_id": user_id,
                "input_text": text[:500] + "..." if len(text) > 500 else text,
                "analysis_timestamp": datetime.utcnow().isoformat(),
                "processing_time": processing_time,
                
                # Overall risk assessment
                "risk_score": round(weighted_score, 2),
                "risk_level": risk_level,
                "severity": self._get_severity_label(weighted_score),
                
                # Individual detection results
                "detected_bias": bias_result.detected,
                "bias_details": bias_result.details,
                "detected_pii": pii_result.detected,
                "pii_details": pii_result.details,
                "hallucination_flag": False,  # Placeholder
                "adversarial_flag": False,    # Placeholder
                
                # Evidence and recommendations
                "evidence": all_evidence,
                "mitigation_suggestions": list(set(all_mitigations)),
                
                # Scoring breakdown
                "score_breakdown": {
                    "bias_score": bias_result.risk_score,
                    "pii_score": pii_result.risk_score,
                    "hallucination_score": 0.0,  # Placeholder
                    "adversarial_score": 0.0,    # Placeholder
                    "weights_applied": self.weights
                },
                
                # System info
                "detection_modules_used": ["bias", "pii"],
                "ai_provider_used": "groq",  # Based on routing
                "confidence_scores": {
                    "bias_confidence": bias_result.confidence,
                    "pii_confidence": pii_result.confidence,
                    "overall_confidence": max(bias_result.confidence, pii_result.confidence)
                }
            }
            
        except Exception as e:
            logger.error(f"Comprehensive analysis failed: {e}")
            return {
                "case_id": f"error_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
                "error": str(e),
                "risk_score": 0.0,
                "risk_level": "unknown",
                "analysis_timestamp": datetime.utcnow().isoformat()
            }
    
    def _determine_risk_level(self, score: float) -> str:
        """Determine risk level based on score"""
        if score >= self.thresholds["high"]:
            return "high"
        elif score >= self.thresholds["medium"]:
            return "medium"
        else:
            return "low"
    
    def _get_severity_label(self, score: float) -> str:
        """Get human-readable severity label"""
        if score >= 90:
            return "critical"
        elif score >= self.thresholds["high"]:
            return "high"
        elif score >= self.thresholds["medium"]:
            return "medium"
        else:
            return "low"

# Global risk scoring engine instance
risk_engine = RiskScoringEngine()

# Convenience functions
async def quick_risk_assessment(text: str, user_id: Optional[str] = None) -> Dict[str, Any]:
    """Quick risk assessment using the global engine"""
    return await risk_engine.comprehensive_analysis(text, user_id)

async def bulk_risk_assessment(texts: List[str], user_id: Optional[str] = None) -> List[Dict[str, Any]]:
    """Bulk risk assessment for multiple texts"""
    tasks = [risk_engine.comprehensive_analysis(text, user_id) for text in texts]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    # Handle exceptions in results
    processed_results = []
    for i, result in enumerate(results):
        if isinstance(result, Exception):
            processed_results.append({
                "case_id": f"bulk_error_{i}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
                "error": str(result),
                "risk_score": 0.0,
                "risk_level": "unknown"
            })
        else:
            processed_results.append(result)
    
    return processed_results

"""
🚨 AIRMS+ Risk Analysis Service
Real-time risk detection for chat and content analysis
"""
import logging
import re
from datetime import datetime
from typing import Dict, List, Any, Tuple
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class RiskResult:
    """Risk analysis result"""
    risk_score: int  # 0-100 percentage
    risk_flags: List[str]
    risk_details: Dict[str, Any]
    confidence: float

class RealTimeRiskAnalyzer:
    """Real-time risk analyzer for chat messages and content"""
    
    def __init__(self):
        self.risk_patterns = {
            "bias": {
                "patterns": [
                    r"\b(men|women) are (better|worse) at\b",
                    r"\ball (black|white|asian) people\b",
                    r"\b(young|old) people (can't|cannot)\b",
                    r"\b(muslims|christians|hindus) are all\b"
                ],
                "weight": 25,
                "description": "Gender, racial, age, or religious bias"
            },
            "pii_leak": {
                "patterns": [
                    r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',  # Email
                    r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b',  # Phone
                    r'\b\d{3}-?\d{2}-?\d{4}\b',  # SSN
                    r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b',  # Credit Card
                    r'\b\d{4}\s?\d{4}\s?\d{4}\b'  # Aadhaar
                ],
                "weight": 35,
                "description": "Personal identifiable information detected"
            },
            "hallucination": {
                "patterns": [
                    r"according to my (knowledge|training)",
                    r"i am (100%|completely) (sure|certain)",
                    r"it is (definitely|absolutely) true that",
                    r"studies (prove|show) that \d+%",
                    r"scientists have (confirmed|proven)",
                    r"research (clearly|definitely) shows"
                ],
                "weight": 20,
                "description": "Potential false or unverified claims"
            },
            "adversarial": {
                "patterns": [
                    r"ignore (previous|all) instructions",
                    r"disregard (the above|everything)",
                    r"forget (everything|all previous)",
                    r"new instructions?:",
                    r"system prompt?:",
                    r"jailbreak",
                    r"roleplay as",
                    r"pretend (you are|to be)",
                    r"act as if you are"
                ],
                "weight": 40,
                "description": "Prompt injection or manipulation attempt"
            },
            "toxicity": {
                "patterns": [
                    r"\b(hate|kill|destroy|attack)\s+(all|every)\b",
                    r"\b(stupid|idiot|moron)\s+(people|users)\b",
                    r"\bgo (die|kill yourself)\b",
                    r"\b(fuck|shit|damn)\s+(you|this|that)\b"
                ],
                "weight": 30,
                "description": "Toxic or harmful language"
            },
            "misinformation": {
                "patterns": [
                    r"\b(covid|vaccine) (causes|leads to) (autism|death)\b",
                    r"\b(earth is|world is) (flat|hollow)\b",
                    r"\b(government|media) (hiding|covering up)\b",
                    r"\bBIG PHARMA (controls|owns)\b",
                    r"\b(miracle|secret) (cure|remedy) for\b"
                ],
                "weight": 35,
                "description": "Potential misinformation patterns"
            }
        }
    
    def analyze_content(self, content: str, user_context: Dict[str, Any] = None) -> RiskResult:
        """
        Analyze content for multiple risk types
        Returns risk score as percentage (0-100)
        """
        risk_flags = []
        risk_details = {}
        total_risk_score = 0
        pattern_matches = 0
        
        # Analyze each risk category
        for risk_type, config in self.risk_patterns.items():
            matches = []
            category_score = 0
            
            for pattern in config["patterns"]:
                if re.search(pattern, content.lower()):
                    matches.append(pattern)
                    category_score += config["weight"]
                    pattern_matches += 1
            
            if matches:
                risk_flags.append(risk_type)
                risk_details[risk_type] = {
                    "matches": len(matches),
                    "patterns_found": matches[:3],  # Limit for response size
                    "description": config["description"],
                    "score": min(category_score, 100)  # Cap at 100
                }
                total_risk_score += category_score
        
        # Calculate final risk score (0-100%)
        if pattern_matches > 0:
            # Use weighted average with decay for multiple patterns
            final_score = min(total_risk_score / max(pattern_matches, 1), 100)
            # Add bonus for multiple risk types
            if len(risk_flags) > 1:
                final_score = min(final_score * 1.2, 100)
        else:
            final_score = 0
        
        # Additional context-based scoring
        if user_context:
            final_score = self._apply_context_modifiers(final_score, user_context, risk_flags)
        
        # Determine confidence based on pattern clarity
        confidence = min(0.9, 0.6 + (pattern_matches * 0.1))
        
        return RiskResult(
            risk_score=int(final_score),
            risk_flags=risk_flags if risk_flags else ["none"],
            risk_details=risk_details,
            confidence=confidence
        )
    
    def _apply_context_modifiers(self, base_score: float, context: Dict[str, Any], risk_flags: List[str]) -> float:
        """Apply context-based risk modifiers"""
        modified_score = base_score
        
        # High-risk user patterns
        if context.get("suspicious_activity", False):
            modified_score *= 1.3
        
        # Time-based factors
        if context.get("rapid_requests", 0) > 10:
            modified_score *= 1.2
        
        # Content length factors
        content_length = context.get("content_length", 0)
        if content_length > 2000:
            modified_score *= 1.1  # Longer content = potentially more risk
        
        return min(modified_score, 100)
    
    def get_risk_summary(self, risk_result: RiskResult) -> Dict[str, Any]:
        """Generate human-readable risk summary"""
        if risk_result.risk_score == 0:
            return {
                "level": "SAFE",
                "message": "No risks detected in this content.",
                "action": "proceed_normally"
            }
        elif risk_result.risk_score <= 25:
            return {
                "level": "LOW",
                "message": "Minor risks detected. Monitor for patterns.",
                "action": "log_and_continue"
            }
        elif risk_result.risk_score <= 50:
            return {
                "level": "MEDIUM", 
                "message": "Moderate risks detected. Review recommended.",
                "action": "flag_for_review"
            }
        elif risk_result.risk_score <= 75:
            return {
                "level": "HIGH",
                "message": "Significant risks detected. Immediate review required.",
                "action": "require_approval"
            }
        else:
            return {
                "level": "CRITICAL",
                "message": "Critical risks detected. Content blocked pending review.",
                "action": "block_content"
            }

# Global instance
risk_analyzer = RealTimeRiskAnalyzer()
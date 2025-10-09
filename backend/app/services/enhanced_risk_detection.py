"""
🛡️ Enhanced Risk Detection Service
Integrates hallucination and adversarial detectors for comprehensive AI safety
"""

import logging
import asyncio
from typing import Dict, List, Any, Optional, Union
from datetime import datetime
from dataclasses import dataclass
from enum import Enum
from risk_detection import RiskAgent

class HallucinationType(Enum):
    FACTUAL_ERROR = "FACTUAL_ERROR"
    LOGICAL_ERROR = "LOGICAL_ERROR"
    CONTEXT_ERROR = "CONTEXT_ERROR"

class AdversarialType(Enum):
    PROMPT_INJECTION = "PROMPT_INJECTION"
    JAILBREAK = "JAILBREAK"
    INSTRUCTION_MANIPULATION = "INSTRUCTION_MANIPULATION"

@dataclass
class AdversarialResult:
    is_adversarial: bool
    confidence_score: float
    attack_type: Optional[AdversarialType]
    risk_level: str
    evidence: Dict[str, Any]
    flagged_patterns: List[str]
    mitigation_suggestions: List[str]

@dataclass
class HallucinationResult:
    is_hallucination: bool
    confidence_score: float
    hallucination_type: Optional[HallucinationType]
    evidence: Dict[str, Any]
    flagged_segments: List[str]

@dataclass
class EnhancedRiskResult:
    overall_risk_score: float
    risk_severity: 'RiskSeverity'
    risk_categories: Dict[str, Any]
    hallucination_result: Optional[Any]
    adversarial_result: Optional[Any]
    mitigation_actions: List[str]
    processing_safe: bool
    requires_human_review: bool
    metadata: Dict[str, Any]

class RiskSeverity(Enum):
    MINIMAL = "MINIMAL"
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"

from app.core.config import settings
from app.core.database import get_database_operations

logger = logging.getLogger(__name__)

class EnhancedRiskDetectionService:
    """
    🛡️ Enhanced Risk Detection Service
    
    Combines multiple detection methods for comprehensive AI safety:
    - Hallucination detection with ground truth validation
    - Adversarial input detection (prompt injection, jailbreaks)
    - PII detection and tokenization
    - Bias detection with cultural context
    - Risk scoring and severity assessment
    """
    
    def __init__(self):
        try:
            self.risk_agent = RiskAgent()
            self.is_available = True
        except ImportError as e:
            logger.warning(f"⚠️ Risk detection not available: {str(e)}")
            self.is_available = False

        # Risk weights for overall scoring
        self.risk_weights = {
            'hallucination': 0.35,
            'adversarial': 0.30,
            'pii': 0.20,
            'bias': 0.15
        }
        
        # Severity thresholds
        self.severity_thresholds = {
            RiskSeverity.MINIMAL: 0.0,
            RiskSeverity.LOW: 0.2,
            RiskSeverity.MEDIUM: 0.4,
            RiskSeverity.HIGH: 0.7,
            RiskSeverity.CRITICAL: 0.9
        }
    
    async def comprehensive_risk_assessment(self, 
                                          content: str, 
                                          context: Optional[str] = None,
                                          user_id: Optional[str] = None,
                                          source_documents: Optional[List[str]] = None) -> EnhancedRiskResult:
        """
        Perform comprehensive risk assessment on content
        
        Args:
            content: Text content to analyze
            context: Additional context for analysis
            user_id: User ID for tracking and permissions
            source_documents: Reference documents for validation
            
        Returns:
            EnhancedRiskResult with comprehensive analysis
        """
        start_time = datetime.utcnow()
        
        logger.info(f"🔍 Starting comprehensive risk assessment for content: {content[:100]}...")
        
        # Initialize result
        result = EnhancedRiskResult(
            overall_risk_score=0.0,
            risk_severity=RiskSeverity.MINIMAL,
            risk_categories={},
            hallucination_result=None,
            adversarial_result=None,
            mitigation_actions=[],
            processing_safe=True,
            requires_human_review=False,
            metadata={}
        )
        
        # Run all detection methods in parallel
        detection_tasks = []
        
        # 1. Hallucination Detection
        if self.hallucination_detector:
            detection_tasks.append(
                self._detect_hallucination(content, context, source_documents)
            )
        else:
            detection_tasks.append(self._fallback_hallucination_detection(content))
        
        # 2. Adversarial Detection
        if self.adversarial_detector:
            detection_tasks.append(
                self._detect_adversarial_input(content, context)
            )
        else:
            detection_tasks.append(self._fallback_adversarial_detection(content))
        
        # 3. PII Detection (using existing service)
        detection_tasks.append(self._detect_pii_risk(content, user_id))
        
        # 4. Bias Detection (using existing service)
        detection_tasks.append(self._detect_bias_risk(content))
        
        # Execute all detections in parallel
        try:
            results = await asyncio.gather(*detection_tasks, return_exceptions=True)
            
            hallucination_result = results[0] if not isinstance(results[0], Exception) else None
            adversarial_result = results[1] if not isinstance(results[1], Exception) else None
            pii_result = results[2] if not isinstance(results[2], Exception) else None
            bias_result = results[3] if not isinstance(results[3], Exception) else None
            
        except Exception as e:
            logger.error(f"❌ Error during parallel detection: {e}")
            # Fallback to sequential execution
            hallucination_result = await self._detect_hallucination(content, context, source_documents)
            adversarial_result = await self._detect_adversarial_input(content, context)
            pii_result = await self._detect_pii_risk(content, user_id)
            bias_result = await self._detect_bias_risk(content)
        
        # Store individual results
        result.hallucination_result = hallucination_result
        result.adversarial_result = adversarial_result
        
        # Calculate risk scores for each category
        risk_scores = {
            'hallucination': self._extract_risk_score(hallucination_result),
            'adversarial': self._extract_risk_score(adversarial_result),
            'pii': self._extract_risk_score(pii_result),
            'bias': self._extract_risk_score(bias_result)
        }
        
        result.risk_categories = {
            'hallucination': {
                'score': risk_scores['hallucination'],
                'detected': risk_scores['hallucination'] > 0.3,
                'details': hallucination_result
            },
            'adversarial': {
                'score': risk_scores['adversarial'],
                'detected': risk_scores['adversarial'] > 0.3,
                'details': adversarial_result
            },
            'pii': {
                'score': risk_scores['pii'],
                'detected': risk_scores['pii'] > 0.3,
                'details': pii_result
            },
            'bias': {
                'score': risk_scores['bias'],
                'detected': risk_scores['bias'] > 0.3,
                'details': bias_result
            }
        }
        
        # Calculate overall risk score
        result.overall_risk_score = sum(
            score * self.risk_weights[category] 
            for category, score in risk_scores.items()
        )
        
        # Determine risk severity
        result.risk_severity = self._determine_risk_severity(result.overall_risk_score)
        
        # Determine processing safety
        result.processing_safe = (
            result.overall_risk_score < 0.7 and
            not (adversarial_result and getattr(adversarial_result, 'is_adversarial', False)) and
            not (pii_result and pii_result.get('requires_permission', False))
        )
        
        # Determine if human review is required
        result.requires_human_review = (
            result.risk_severity in [RiskSeverity.HIGH, RiskSeverity.CRITICAL] or
            result.overall_risk_score > 0.8
        )
        
        # Generate mitigation actions
        result.mitigation_actions = self._generate_mitigation_actions(result)
        
        # Add metadata
        processing_time = (datetime.utcnow() - start_time).total_seconds()
        result.metadata = {
            'assessment_timestamp': start_time.isoformat(),
            'processing_time_seconds': processing_time,
            'content_length': len(content),
            'detectors_used': {
                'hallucination': self.hallucination_detector is not None,
                'adversarial': self.adversarial_detector is not None,
                'pii': True,
                'bias': True
            },
            'risk_weights': self.risk_weights,
            'severity_thresholds': {k.value: v for k, v in self.severity_thresholds.items()}
        }
        
        # Save assessment to database
        await self._save_risk_assessment(result, content, user_id)
        
        logger.info(f"✅ Risk assessment completed. Overall score: {result.overall_risk_score:.3f}, Severity: {result.risk_severity.value}")
        
        return result
    
    async def _detect_hallucination(self, content: str, context: Optional[str], source_documents: Optional[List[str]]) -> Optional[HallucinationResult]:
        """Detect hallucinations using advanced detector"""
        try:
            if not self.hallucination_detector:
                return await self._fallback_hallucination_detection(content)
            
            result = await self.hallucination_detector.detect_hallucination(
                content=content,
                context=context or "",
                source_documents=source_documents or []
            )
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Hallucination detection error: {e}")
            return await self._fallback_hallucination_detection(content)
    
    async def _detect_adversarial_input(self, content: str, context: Optional[str]) -> Optional[AdversarialResult]:
        """Detect adversarial inputs using advanced detector"""
        try:
            if not self.adversarial_detector:
                return await self._fallback_adversarial_detection(content)
            
            result = self.adversarial_detector.detect_adversarial_input(
                text=content,
                context=context or ""
            )
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Adversarial detection error: {e}")
            return await self._fallback_adversarial_detection(content)
    
    async def _detect_pii_risk(self, content: str, user_id: Optional[str]) -> Dict[str, Any]:
        """Detect PII using existing tokenization service"""
        try:
            from app.services.pii_tokenization import pii_tokenizer
            
            result = await pii_tokenizer.tokenize_text(
                text=content,
                user_id=user_id,
                request_permission=True
            )
            
            return {
                'pii_detected': result['pii_count'] > 0,
                'pii_count': result['pii_count'],
                'risk_score': min(1.0, result['pii_count'] * 0.2),
                'requires_permission': result['requires_user_consent'],
                'detected_types': [pii['type'] for pii in result['detected_pii']],
                'processing_safe': result['processing_safe']
            }
            
        except Exception as e:
            logger.error(f"❌ PII detection error: {e}")
            return {'pii_detected': False, 'risk_score': 0.0, 'requires_permission': False}
    
    async def _detect_bias_risk(self, content: str) -> Dict[str, Any]:
        """Detect bias using existing detection patterns"""
        try:
            bias_patterns = settings.INDIAN_BIAS_KEYWORDS
            detected_biases = []
            total_matches = 0
            
            for category, keywords in bias_patterns.items():
                matches = sum(1 for keyword in keywords if keyword.lower() in content.lower())
                if matches > 0:
                    detected_biases.append({
                        'category': category,
                        'matches': matches,
                        'keywords_found': [kw for kw in keywords if kw.lower() in content.lower()]
                    })
                    total_matches += matches
            
            risk_score = min(1.0, total_matches * 0.1)
            
            return {
                'bias_detected': len(detected_biases) > 0,
                'risk_score': risk_score,
                'detected_categories': detected_biases,
                'total_matches': total_matches
            }
            
        except Exception as e:
            logger.error(f"❌ Bias detection error: {e}")
            return {'bias_detected': False, 'risk_score': 0.0}
    
    async def _fallback_hallucination_detection(self, content: str) -> HallucinationResult:
        """Fallback hallucination detection using simple patterns"""
        suspicious_patterns = [
            r'according to a study',
            r'research shows',
            r'experts say',
            r'it is widely known',
            r'studies have proven'
        ]
        
        matches = 0
        for pattern in suspicious_patterns:
            import re
            if re.search(pattern, content, re.IGNORECASE):
                matches += 1
        
        confidence = min(1.0, matches * 0.3)
        
        return HallucinationResult(
            is_hallucination=confidence > 0.4,
            confidence_score=confidence,
            hallucination_type=HallucinationType.FACTUAL_ERROR if confidence > 0.4 else None,
            evidence={'pattern_matches': matches},
            flagged_segments=[]
        )
    
    async def _fallback_adversarial_detection(self, content: str) -> AdversarialResult:
        """Fallback adversarial detection using simple patterns"""
        adversarial_patterns = [
            r'ignore.*instructions',
            r'forget.*previous',
            r'act as',
            r'pretend to be',
            r'jailbreak',
            r'developer mode'
        ]
        
        matches = 0
        detected_patterns = []
        
        for pattern in adversarial_patterns:
            import re
            if re.search(pattern, content, re.IGNORECASE):
                matches += 1
                detected_patterns.append(pattern)
        
        confidence = min(1.0, matches * 0.4)
        risk_level = "CRITICAL" if confidence > 0.8 else "HIGH" if confidence > 0.5 else "MEDIUM" if confidence > 0.3 else "LOW"
        
        return AdversarialResult(
            is_adversarial=confidence > 0.3,
            confidence_score=confidence,
            attack_type=AdversarialType.PROMPT_INJECTION if confidence > 0.3 else None,
            risk_level=risk_level,
            evidence={'pattern_matches': matches, 'patterns_found': detected_patterns},
            flagged_patterns=[],
            mitigation_suggestions=[]
        )
    
    def _extract_risk_score(self, result: Any) -> float:
        """Extract risk score from detection result"""
        if result is None:
            return 0.0
        
        if hasattr(result, 'confidence_score'):
            return result.confidence_score
        elif isinstance(result, dict):
            return result.get('risk_score', result.get('confidence_score', 0.0))
        
        return 0.0
    
    def _determine_risk_severity(self, overall_score: float) -> RiskSeverity:
        """Determine risk severity based on overall score"""
        if overall_score >= self.severity_thresholds[RiskSeverity.CRITICAL]:
            return RiskSeverity.CRITICAL
        elif overall_score >= self.severity_thresholds[RiskSeverity.HIGH]:
            return RiskSeverity.HIGH
        elif overall_score >= self.severity_thresholds[RiskSeverity.MEDIUM]:
            return RiskSeverity.MEDIUM
        elif overall_score >= self.severity_thresholds[RiskSeverity.LOW]:
            return RiskSeverity.LOW
        else:
            return RiskSeverity.MINIMAL
    
    def _generate_mitigation_actions(self, result: EnhancedRiskResult) -> List[str]:
        """Generate mitigation actions based on detected risks"""
        actions = []
        
        # Hallucination mitigation
        if result.risk_categories.get('hallucination', {}).get('detected'):
            actions.extend([
                "Verify factual claims against reliable sources",
                "Request citations for statistical claims",
                "Cross-reference information with authoritative databases"
            ])
        
        # Adversarial mitigation
        if result.risk_categories.get('adversarial', {}).get('detected'):
            actions.extend([
                "Apply input sanitization to remove instruction keywords",
                "Implement prompt isolation techniques",
                "Log and monitor for security analysis"
            ])
        
        # PII mitigation
        if result.risk_categories.get('pii', {}).get('detected'):
            actions.extend([
                "Tokenize PII before processing",
                "Request user permission for sensitive data",
                "Apply data minimization principles"
            ])
        
        # Bias mitigation
        if result.risk_categories.get('bias', {}).get('detected'):
            actions.extend([
                "Review content for cultural sensitivity",
                "Apply bias correction techniques",
                "Provide balanced perspectives"
            ])
        
        # High-risk general actions
        if result.risk_severity in [RiskSeverity.HIGH, RiskSeverity.CRITICAL]:
            actions.extend([
                "Require human review before processing",
                "Implement additional safety checks",
                "Consider blocking or quarantining content"
            ])
        
        return list(set(actions))  # Remove duplicates
    
    async def _save_risk_assessment(self, result: EnhancedRiskResult, content: str, user_id: Optional[str]):
        """Save risk assessment to database"""
        try:
            db_ops = await get_database_operations()
            
            assessment_data = {
                'user_id': user_id,
                'content_hash': hash(content),
                'content_length': len(content),
                'overall_risk_score': result.overall_risk_score,
                'risk_severity': result.risk_severity.value,
                'risk_categories': result.risk_categories,
                'processing_safe': result.processing_safe,
                'requires_human_review': result.requires_human_review,
                'mitigation_actions': result.mitigation_actions,
                'metadata': result.metadata,
                'created_at': datetime.utcnow()
            }
            
            await db_ops.db.enhanced_risk_assessments.insert_one(assessment_data)
            
        except Exception as e:
            logger.error(f"❌ Failed to save risk assessment: {e}")

# Global service instance
enhanced_risk_service = EnhancedRiskDetectionService()

# Convenience functions
async def assess_content_risk(content: str, 
                            context: Optional[str] = None,
                            user_id: Optional[str] = None,
                            source_documents: Optional[List[str]] = None) -> EnhancedRiskResult:
    """Quick risk assessment function"""
    return await enhanced_risk_service.comprehensive_risk_assessment(
        content=content,
        context=context,
        user_id=user_id,
        source_documents=source_documents
    )

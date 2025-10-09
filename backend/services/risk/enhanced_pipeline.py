"""
🚀 Enhanced Risk Analysis Pipeline
Comprehensive AI-powered risk detection and mitigation system
"""
import asyncio
import time
import hashlib
from typing import Dict, List, Any, Optional
from datetime import datetime
import logging

from detectors.pii.detector import PIIDetector
from detectors.misinformation.detector import MisinformationDetector
from detectors.bias import BiasDetector
from detectors.hallucination import HallucinationDetector
from detectors.adversarial import AdversarialDetector
from utils.sanitizers import InputSanitizer
from db.models import (
    RiskAnalysisRequest, RiskAnalysisResponse, PIIAnalysis, 
    MisinformationAnalysis, SanitizationResult, RiskSeverity,
    DetectionStatus, MitigationAction
)
from core.database import get_database

logger = logging.getLogger(__name__)

class EnhancedRiskPipeline:
    """
    Enhanced risk analysis pipeline with comprehensive security and AI safety features
    """
    
    def __init__(self):
        # Initialize all detectors
        self.pii_detector = PIIDetector()
        self.misinformation_detector = MisinformationDetector()
        self.input_sanitizer = InputSanitizer()
        
        # Initialize other detectors (placeholder implementations)
        try:
            self.bias_detector = BiasDetector()
        except:
            self.bias_detector = None
            logger.warning("BiasDetector not available")
            
        try:
            self.hallucination_detector = HallucinationDetector()
        except:
            self.hallucination_detector = None
            logger.warning("HallucinationDetector not available")
            
        try:
            self.adversarial_detector = AdversarialDetector()
        except:
            self.adversarial_detector = None
            logger.warning("AdversarialDetector not available")
        
        # Risk thresholds and weights
        self.risk_weights = {
            'pii': 0.25,
            'misinformation': 0.25,
            'sanitization': 0.20,
            'bias': 0.10,
            'hallucination': 0.10,
            'adversarial': 0.10
        }
        
        # Severity score mappings
        self.severity_scores = {
            RiskSeverity.MINIMAL: (0, 19),
            RiskSeverity.LOW: (20, 39),
            RiskSeverity.MEDIUM: (40, 69),
            RiskSeverity.HIGH: (70, 89),
            RiskSeverity.CRITICAL: (90, 100)
        }
        
        # Mitigation strategies
        self.mitigation_strategies = {
            RiskSeverity.CRITICAL: [MitigationAction.BLOCK, MitigationAction.REDACT],
            RiskSeverity.HIGH: [MitigationAction.FLAG, MitigationAction.SANITIZE],
            RiskSeverity.MEDIUM: [MitigationAction.WARN, MitigationAction.MONITOR],
            RiskSeverity.LOW: [MitigationAction.MONITOR],
            RiskSeverity.MINIMAL: []
        }
    
    async def process_comprehensive_analysis(self, 
                                           input_text: str,
                                           context: Dict[str, Any],
                                           config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Comprehensive risk analysis with all detection components
        """
        start_time = time.time()
        request_id = context.get('request_id', self._generate_request_id())
        user_id = context.get('user_id')
        
        logger.info(f"Starting comprehensive analysis for request {request_id}")
        
        # Store initial request
        await self._store_analysis_request(input_text, context, config)
        
        try:
            # Phase 1: Input Sanitization (Critical - must run first)
            sanitization_result = await self._run_input_sanitization(
                input_text, context, config
            )
            
            # Phase 2: Parallel Risk Detection
            detection_results = await self._run_parallel_detection(
                sanitization_result['sanitized_input'], context, config
            )
            
            # Phase 3: Risk Score Calculation and Severity Assessment
            risk_assessment = await self._calculate_comprehensive_risk_score(
                sanitization_result, detection_results
            )
            
            # Phase 4: Mitigation Strategy Application
            mitigation_results = await self._apply_mitigation_strategies(
                risk_assessment, sanitization_result, detection_results
            )
            
            # Phase 5: Generate Comprehensive Response
            final_response = await self._generate_comprehensive_response(
                request_id, user_id, input_text, sanitization_result,
                detection_results, risk_assessment, mitigation_results,
                start_time
            )
            
            # Phase 6: Store Results in Database
            await self._store_analysis_results(final_response, detection_results)
            
            logger.info(f"Analysis completed for request {request_id} in {time.time() - start_time:.3f}s")
            return final_response
            
        except Exception as e:
            logger.error(f"Analysis failed for request {request_id}: {e}", exc_info=True)
            return await self._generate_error_response(request_id, user_id, str(e), start_time)
    
    async def _run_input_sanitization(self, 
                                    input_text: str, 
                                    context: Dict[str, Any],
                                    config: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Run comprehensive input sanitization"""
        logger.debug("Running input sanitization")
        
        input_type = config.get('input_type', 'text') if config else 'text'
        
        sanitization_result = await self.input_sanitizer.sanitize(
            input_text, input_type, context
        )
        
        # Add processing metadata
        sanitization_result['component'] = 'input_sanitization'
        sanitization_result['processing_time'] = time.time()
        
        return sanitization_result
    
    async def _run_parallel_detection(self, 
                                    sanitized_input: str,
                                    context: Dict[str, Any],
                                    config: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Run all detection components in parallel"""
        logger.debug("Running parallel risk detection")
        
        # Prepare detection tasks
        detection_tasks = []
        
        # PII Detection
        detection_tasks.append(
            self._run_pii_detection(sanitized_input, context)
        )
        
        # Misinformation Detection
        urls = self._extract_urls(sanitized_input)
        detection_tasks.append(
            self._run_misinformation_detection(sanitized_input, context, urls)
        )
        
        # Additional detectors (if available)
        if self.bias_detector:
            detection_tasks.append(
                self._run_bias_detection(sanitized_input, context)
            )
        
        if self.hallucination_detector:
            detection_tasks.append(
                self._run_hallucination_detection(sanitized_input, context)
            )
        
        if self.adversarial_detector:
            detection_tasks.append(
                self._run_adversarial_detection(sanitized_input, context)
            )
        
        # Execute all detections in parallel
        detection_results = await asyncio.gather(*detection_tasks, return_exceptions=True)
        
        # Process results and handle exceptions
        processed_results = {}
        for i, result in enumerate(detection_results):
            if isinstance(result, Exception):
                logger.error(f"Detection task {i} failed: {result}")
                continue
            
            if isinstance(result, dict) and 'component' in result:
                component_name = result['component']
                processed_results[component_name] = result
        
        return processed_results
    
    async def _run_pii_detection(self, text: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Run PII detection"""
        start_time = time.time()
        
        try:
            result = await self.pii_detector.detect_pii(text, context)
            result['component'] = 'pii_detection'
            result['processing_time'] = time.time() - start_time
            return result
        except Exception as e:
            logger.error(f"PII detection failed: {e}")
            return {
                'component': 'pii_detection',
                'error': str(e),
                'risk_score': 0,
                'processing_time': time.time() - start_time
            }
    
    async def _run_misinformation_detection(self, 
                                          text: str, 
                                          context: Dict[str, Any],
                                          urls: List[str]) -> Dict[str, Any]:
        """Run misinformation detection"""
        start_time = time.time()
        
        try:
            result = await self.misinformation_detector.detect_misinformation(
                text, context, urls
            )
            result['component'] = 'misinformation_detection'
            result['processing_time'] = time.time() - start_time
            return result
        except Exception as e:
            logger.error(f"Misinformation detection failed: {e}")
            return {
                'component': 'misinformation_detection',
                'error': str(e),
                'risk_score': 0,
                'processing_time': time.time() - start_time
            }
    
    async def _run_bias_detection(self, text: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Run bias detection (placeholder)"""
        start_time = time.time()
        
        # Placeholder implementation
        return {
            'component': 'bias_detection',
            'risk_score': 0,
            'severity': 'minimal',
            'bias_indicators': [],
            'processing_time': time.time() - start_time
        }
    
    async def _run_hallucination_detection(self, text: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Run hallucination detection (placeholder)"""
        start_time = time.time()
        
        # Placeholder implementation
        return {
            'component': 'hallucination_detection',
            'risk_score': 0,
            'severity': 'minimal',
            'hallucination_indicators': [],
            'processing_time': time.time() - start_time
        }
    
    async def _run_adversarial_detection(self, text: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Run adversarial attack detection (placeholder)"""
        start_time = time.time()
        
        # Placeholder implementation
        return {
            'component': 'adversarial_detection',
            'risk_score': 0,
            'severity': 'minimal',
            'adversarial_indicators': [],
            'processing_time': time.time() - start_time
        }
    
    async def _calculate_comprehensive_risk_score(self, 
                                                sanitization_result: Dict[str, Any],
                                                detection_results: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate comprehensive risk score from all components"""
        
        component_scores = {}
        
        # Sanitization risk score
        component_scores['sanitization'] = sanitization_result.get('risk_score', 0)
        
        # Detection component scores
        for component_name, result in detection_results.items():
            if 'risk_score' in result:
                component_scores[component_name.replace('_detection', '')] = result['risk_score']
        
        # Calculate weighted overall score
        total_score = 0
        total_weight = 0
        
        for component, score in component_scores.items():
            weight = self.risk_weights.get(component, 0.05)  # Default small weight
            total_score += score * weight
            total_weight += weight
        
        # Normalize score
        overall_score = total_score / total_weight if total_weight > 0 else 0
        overall_score = min(100, max(0, overall_score))
        
        # Determine severity
        overall_severity = self._score_to_severity(overall_score)
        
        # Risk category breakdown
        risk_categories = {}
        detected_risks = []
        
        for component, score in component_scores.items():
            risk_categories[component] = score
            if score >= 40:  # Medium risk threshold
                detected_risks.append(component)
        
        return {
            'overall_risk_score': overall_score,
            'overall_severity': overall_severity,
            'component_scores': component_scores,
            'risk_categories': risk_categories,
            'detected_risks': detected_risks,
            'is_safe_for_processing': overall_score < 50
        }
    
    async def _apply_mitigation_strategies(self,
                                         risk_assessment: Dict[str, Any],
                                         sanitization_result: Dict[str, Any],
                                         detection_results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Apply appropriate mitigation strategies based on risk assessment"""
        
        applied_mitigations = []
        severity = risk_assessment['overall_severity']
        
        # Get mitigation actions for this severity level
        mitigation_actions = self.mitigation_strategies.get(severity, [])
        
        for action in mitigation_actions:
            mitigation = {
                'action_type': action,
                'reason': f'Risk severity: {severity}',
                'timestamp': datetime.utcnow(),
                'automated': True,
                'details': {
                    'risk_score': risk_assessment['overall_risk_score'],
                    'detected_risks': risk_assessment['detected_risks']
                }
            }
            applied_mitigations.append(mitigation)
        
        # Component-specific mitigations
        if 'pii_detection' in detection_results:
            pii_result = detection_results['pii_detection']
            if pii_result.get('risk_score', 0) >= 70:
                applied_mitigations.append({
                    'action_type': MitigationAction.REDACT,
                    'reason': 'High PII risk detected',
                    'timestamp': datetime.utcnow(),
                    'automated': True,
                    'details': {'pii_count': len(pii_result.get('pii_found', []))}
                })
        
        if 'misinformation_detection' in detection_results:
            misinfo_result = detection_results['misinformation_detection']
            if misinfo_result.get('risk_score', 0) >= 60:
                applied_mitigations.append({
                    'action_type': MitigationAction.FLAG,
                    'reason': 'Potential misinformation detected',
                    'timestamp': datetime.utcnow(),
                    'automated': True,
                    'details': {
                        'credibility_score': misinfo_result.get('credibility_score', 50)
                    }
                })
        
        return applied_mitigations
    
    async def _generate_comprehensive_response(self,
                                             request_id: str,
                                             user_id: Optional[str],
                                             original_input: str,
                                             sanitization_result: Dict[str, Any],
                                             detection_results: Dict[str, Any],
                                             risk_assessment: Dict[str, Any],
                                             mitigation_results: List[Dict[str, Any]],
                                             start_time: float) -> Dict[str, Any]:
        """Generate comprehensive analysis response"""
        
        processing_time = (time.time() - start_time) * 1000  # Convert to milliseconds
        
        # Generate recommendations
        recommendations = self._generate_recommendations(
            risk_assessment, detection_results, mitigation_results
        )
        
        # Compliance flags
        compliance_flags = self._generate_compliance_flags(
            detection_results, risk_assessment
        )
        
        # Audit trail
        audit_trail = [
            {
                'action': 'analysis_started',
                'timestamp': datetime.fromtimestamp(start_time).isoformat(),
                'details': {'request_id': request_id}
            },
            {
                'action': 'input_sanitized',
                'timestamp': datetime.utcnow().isoformat(),
                'details': {
                    'security_issues': len(sanitization_result.get('security_issues', [])),
                    'is_safe': sanitization_result.get('is_safe', True)
                }
            },
            {
                'action': 'risk_analysis_completed',
                'timestamp': datetime.utcnow().isoformat(),
                'details': {
                    'overall_score': risk_assessment['overall_risk_score'],
                    'components_analyzed': list(detection_results.keys())
                }
            }
        ]
        
        return {
            'request_id': request_id,
            'user_id': user_id,
            'overall_risk_score': risk_assessment['overall_risk_score'],
            'overall_severity': risk_assessment['overall_severity'],
            'is_safe_for_processing': risk_assessment['is_safe_for_processing'],
            'risk_categories': risk_assessment['risk_categories'],
            'detected_risks': risk_assessment['detected_risks'],
            'recommended_actions': recommendations,
            'applied_mitigations': mitigation_results,
            'processing_status': DetectionStatus.COMPLETED,
            'total_processing_time_ms': processing_time,
            'analysis_timestamp': datetime.utcnow(),
            'compliance_flags': compliance_flags,
            'audit_trail': audit_trail,
            'component_results': {
                'sanitization': sanitization_result,
                'detection': detection_results
            }
        }
    
    async def _generate_error_response(self,
                                     request_id: str,
                                     user_id: Optional[str],
                                     error_message: str,
                                     start_time: float) -> Dict[str, Any]:
        """Generate error response for failed analysis"""
        
        processing_time = (time.time() - start_time) * 1000
        
        return {
            'request_id': request_id,
            'user_id': user_id,
            'overall_risk_score': 100,  # Assume highest risk on error
            'overall_severity': RiskSeverity.CRITICAL,
            'is_safe_for_processing': False,
            'risk_categories': {'system_error': 100},
            'detected_risks': ['system_error'],
            'recommended_actions': ['Manual review required due to system error'],
            'applied_mitigations': [{
                'action_type': MitigationAction.BLOCK,
                'reason': f'System error: {error_message}',
                'timestamp': datetime.utcnow(),
                'automated': True
            }],
            'processing_status': DetectionStatus.FAILED,
            'total_processing_time_ms': processing_time,
            'analysis_timestamp': datetime.utcnow(),
            'error': error_message
        }
    
    def _generate_recommendations(self,
                                risk_assessment: Dict[str, Any],
                                detection_results: Dict[str, Any],
                                mitigation_results: List[Dict[str, Any]]) -> List[str]:
        """Generate actionable recommendations"""
        
        recommendations = []
        overall_score = risk_assessment['overall_risk_score']
        
        # Overall recommendations based on score
        if overall_score >= 90:
            recommendations.extend([
                "CRITICAL: Block content immediately",
                "Require manual security review",
                "Implement additional monitoring"
            ])
        elif overall_score >= 70:
            recommendations.extend([
                "HIGH RISK: Apply content warnings",
                "Increase monitoring frequency",
                "Consider user notification"
            ])
        elif overall_score >= 40:
            recommendations.extend([
                "MEDIUM RISK: Apply standard mitigations",
                "Monitor for patterns"
            ])
        
        # Component-specific recommendations
        for component, result in detection_results.items():
            if result.get('risk_score', 0) >= 60:
                if component == 'pii_detection':
                    recommendations.append("Implement PII redaction before storage")
                elif component == 'misinformation_detection':
                    recommendations.append("Add fact-checking warnings")
        
        return list(set(recommendations))  # Remove duplicates
    
    def _generate_compliance_flags(self,
                                 detection_results: Dict[str, Any],
                                 risk_assessment: Dict[str, Any]) -> List[str]:
        """Generate compliance-related flags"""
        
        flags = []
        
        # PII compliance
        if 'pii_detection' in detection_results:
            pii_result = detection_results['pii_detection']
            if pii_result.get('pii_found'):
                flags.extend(['GDPR_RELEVANT', 'CCPA_RELEVANT', 'PII_DETECTED'])
        
        # High risk content
        if risk_assessment['overall_risk_score'] >= 70:
            flags.append('HIGH_RISK_CONTENT')
        
        # Misinformation
        if 'misinformation_detection' in detection_results:
            misinfo_result = detection_results['misinformation_detection']
            if misinfo_result.get('risk_score', 0) >= 60:
                flags.append('MISINFORMATION_RISK')
        
        return flags
    
    def _score_to_severity(self, score: float) -> RiskSeverity:
        """Convert numeric score to severity level"""
        for severity, (min_score, max_score) in self.severity_scores.items():
            if min_score <= score <= max_score:
                return severity
        return RiskSeverity.MINIMAL
    
    def _extract_urls(self, text: str) -> List[str]:
        """Extract URLs from text for source analysis"""
        import re
        url_pattern = re.compile(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+')
        return url_pattern.findall(text)
    
    def _generate_request_id(self) -> str:
        """Generate unique request ID"""
        timestamp = str(int(time.time() * 1000))
        random_part = hashlib.md5(timestamp.encode()).hexdigest()[:8]
        return f"req_{timestamp}_{random_part}"
    
    async def _store_analysis_request(self,
                                    input_text: str,
                                    context: Dict[str, Any],
                                    config: Optional[Dict[str, Any]]):
        """Store analysis request in database"""
        try:
            db = await get_database()
            
            request_doc = RiskAnalysisRequest(
                request_id=context.get('request_id'),
                user_id=context.get('user_id'),
                input_text=input_text,
                input_type=config.get('input_type', 'text') if config else 'text',
                context=context,
                config=config or {},
                client_ip=context.get('client_ip'),
                user_agent=context.get('user_agent')
            )
            
            await db.risk_analysis_requests.insert_one(request_doc.dict(by_alias=True))
            
        except Exception as e:
            logger.error(f"Failed to store analysis request: {e}")
    
    async def _store_analysis_results(self,
                                    final_response: Dict[str, Any],
                                    detection_results: Dict[str, Any]):
        """Store analysis results in database"""
        try:
            db = await get_database()
            
            # Store main response
            response_doc = RiskAnalysisResponse(**final_response)
            await db.risk_analysis_responses.insert_one(response_doc.dict(by_alias=True))
            
            # Store component-specific results
            if 'pii_detection' in detection_results:
                pii_doc = PIIAnalysis(
                    request_id=final_response['request_id'],
                    user_id=final_response.get('user_id'),
                    **detection_results['pii_detection']
                )
                await db.pii_analyses.insert_one(pii_doc.dict(by_alias=True))
            
            if 'misinformation_detection' in detection_results:
                misinfo_doc = MisinformationAnalysis(
                    request_id=final_response['request_id'],
                    user_id=final_response.get('user_id'),
                    **detection_results['misinformation_detection']
                )
                await db.misinformation_analyses.insert_one(misinfo_doc.dict(by_alias=True))
            
        except Exception as e:
            logger.error(f"Failed to store analysis results: {e}")

# Factory function for dependency injection
def get_enhanced_risk_pipeline() -> EnhancedRiskPipeline:
    """Get enhanced risk pipeline instance"""
    return EnhancedRiskPipeline()

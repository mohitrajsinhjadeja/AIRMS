"""
Enterprise Risk Detection Service
Real-time AI-powered risk assessment with multiple detection methods
"""

import logging
import hashlib
import time
import re
import json
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any, Tuple
from bson import ObjectId

from app.core.database import mongodb
from app.models.risk_assessment import (
    RiskAssessmentCreate,
    RiskAssessmentInDB,
    RiskAssessmentResponse,
    RiskAssessmentStats,
    RiskAssessmentFilter,
    RiskTrend,
    RiskCategory,
    RiskSeverity,
    ContentType,
    DetectionMethod,
    RiskEvidence,
    MitigationAction
)

logger = logging.getLogger(__name__)


class RiskDetectionEngine:
    """Core risk detection engine with multiple AI methods"""
    
    def __init__(self):
        self.model_version = "1.0.0"
        self.confidence_threshold = 0.7
        
        # Risk patterns for different categories
        self.risk_patterns = {
            RiskCategory.MISINFORMATION: [
                r'\b(fake news|hoax|conspiracy|debunked|false claim)\b',
                r'\b(unverified|unconfirmed|alleged|rumored)\b',
                r'\b(they don\'t want you to know|hidden truth|cover[- ]?up)\b'
            ],
            RiskCategory.SECURITY_THREAT: [
                r'\b(hack|exploit|vulnerability|malware|phishing)\b',
                r'\b(password|credential|token|api[- ]?key)\b',
                r'\b(injection|xss|csrf|sql[- ]?injection)\b'
            ],
            RiskCategory.CONTENT_SAFETY: [
                r'\b(hate|violence|harassment|threat|abuse)\b',
                r'\b(suicide|self[- ]?harm|dangerous)\b',
                r'\b(explicit|inappropriate|nsfw)\b'
            ],
            RiskCategory.ADVERSARIAL_ATTACK: [
                r'\b(ignore previous|forget instructions|system prompt)\b',
                r'\b(jailbreak|bypass|override|disable)\b',
                r'\b(act as|pretend to be|roleplay)\b'
            ]
        }
        
        # Severity scoring thresholds
        self.severity_thresholds = {
            RiskSeverity.CRITICAL: 90,
            RiskSeverity.HIGH: 70,
            RiskSeverity.MEDIUM: 40,
            RiskSeverity.LOW: 20,
            RiskSeverity.MINIMAL: 0
        }
    
    def calculate_content_hash(self, content: str) -> str:
        """Calculate hash for content deduplication"""
        return hashlib.sha256(content.encode('utf-8')).hexdigest()
    
    def detect_misinformation(self, content: str) -> Tuple[float, List[RiskEvidence]]:
        """Detect misinformation patterns"""
        evidence = []
        score = 0.0
        
        # Pattern-based detection
        patterns = self.risk_patterns[RiskCategory.MISINFORMATION]
        matches = []
        
        for pattern in patterns:
            found = re.findall(pattern, content.lower())
            if found:
                matches.extend(found)
                score += len(found) * 15  # Each match adds 15 points
        
        if matches:
            evidence.append(RiskEvidence(
                type="pattern_match",
                confidence=min(0.8, len(matches) * 0.2),
                description=f"Found {len(matches)} misinformation indicators",
                data={"matches": matches[:5]},  # Limit to first 5
                source="pattern_detector"
            ))
        
        # Check for unverified claims
        unverified_indicators = ['allegedly', 'reportedly', 'sources say', 'it is believed']
        unverified_count = sum(1 for indicator in unverified_indicators if indicator in content.lower())
        
        if unverified_count > 0:
            score += unverified_count * 10
            evidence.append(RiskEvidence(
                type="unverified_claims",
                confidence=0.6,
                description=f"Contains {unverified_count} unverified claim indicators",
                data={"count": unverified_count},
                source="claim_detector"
            ))
        
        # Check for emotional manipulation
        emotional_words = ['shocking', 'unbelievable', 'must see', 'they hate this', 'doctors hate']
        emotional_count = sum(1 for word in emotional_words if word in content.lower())
        
        if emotional_count > 0:
            score += emotional_count * 8
            evidence.append(RiskEvidence(
                type="emotional_manipulation",
                confidence=0.5,
                description=f"Contains {emotional_count} emotional manipulation indicators",
                data={"count": emotional_count},
                source="emotion_detector"
            ))
        
        return min(score, 100.0), evidence
    
    def detect_security_threats(self, content: str) -> Tuple[float, List[RiskEvidence]]:
        """Detect security threats and vulnerabilities"""
        evidence = []
        score = 0.0
        
        # Pattern-based detection
        patterns = self.risk_patterns[RiskCategory.SECURITY_THREAT]
        matches = []
        
        for pattern in patterns:
            found = re.findall(pattern, content.lower())
            if found:
                matches.extend(found)
                score += len(found) * 20  # Security threats are high priority
        
        if matches:
            evidence.append(RiskEvidence(
                type="security_pattern",
                confidence=0.9,
                description=f"Found {len(matches)} security threat indicators",
                data={"matches": matches[:5]},
                source="security_detector"
            ))
        
        # Check for credential exposure
        credential_patterns = [
            r'password[:\s]*["\']?[\w!@#$%^&*()]+["\']?',
            r'api[_\s]*key[:\s]*["\']?[\w-]+["\']?',
            r'token[:\s]*["\']?[\w.-]+["\']?'
        ]
        
        for pattern in credential_patterns:
            if re.search(pattern, content.lower()):
                score += 30
                evidence.append(RiskEvidence(
                    type="credential_exposure",
                    confidence=0.8,
                    description="Potential credential exposure detected",
                    data={"pattern": pattern},
                    source="credential_detector"
                ))
        
        return min(score, 100.0), evidence
    
    def detect_adversarial_attacks(self, content: str) -> Tuple[float, List[RiskEvidence]]:
        """Detect adversarial attacks and prompt injection"""
        evidence = []
        score = 0.0
        
        # Pattern-based detection
        patterns = self.risk_patterns[RiskCategory.ADVERSARIAL_ATTACK]
        matches = []
        
        for pattern in patterns:
            found = re.findall(pattern, content.lower())
            if found:
                matches.extend(found)
                score += len(found) * 25  # High severity for adversarial attacks
        
        if matches:
            evidence.append(RiskEvidence(
                type="adversarial_pattern",
                confidence=0.85,
                description=f"Found {len(matches)} adversarial attack indicators",
                data={"matches": matches[:5]},
                source="adversarial_detector"
            ))
        
        # Check for instruction manipulation
        instruction_patterns = [
            r'ignore\s+(previous|all|above)',
            r'forget\s+(everything|instructions|context)',
            r'new\s+(instructions|rules|system)',
            r'override\s+(safety|security|rules)'
        ]
        
        for pattern in instruction_patterns:
            if re.search(pattern, content.lower()):
                score += 35
                evidence.append(RiskEvidence(
                    type="instruction_manipulation",
                    confidence=0.9,
                    description="Instruction manipulation attempt detected",
                    data={"pattern": pattern},
                    source="instruction_detector"
                ))
        
        return min(score, 100.0), evidence
    
    def detect_content_safety(self, content: str) -> Tuple[float, List[RiskEvidence]]:
        """Detect unsafe content"""
        evidence = []
        score = 0.0
        
        # Pattern-based detection
        patterns = self.risk_patterns[RiskCategory.CONTENT_SAFETY]
        matches = []
        
        for pattern in patterns:
            found = re.findall(pattern, content.lower())
            if found:
                matches.extend(found)
                score += len(found) * 18
        
        if matches:
            evidence.append(RiskEvidence(
                type="unsafe_content",
                confidence=0.75,
                description=f"Found {len(matches)} unsafe content indicators",
                data={"matches": matches[:5]},
                source="safety_detector"
            ))
        
        return min(score, 100.0), evidence
    
    def detect_anomalies(self, content: str, context: Dict[str, Any]) -> Tuple[float, List[RiskEvidence]]:
        """Detect anomalies based on content and context"""
        evidence = []
        score = 0.0
        
        # Length anomaly
        if len(content) > 10000:
            score += 15
            evidence.append(RiskEvidence(
                type="length_anomaly",
                confidence=0.6,
                description=f"Unusually long content ({len(content)} characters)",
                data={"length": len(content)},
                source="anomaly_detector"
            ))
        
        # Repetition anomaly
        words = content.lower().split()
        if len(words) > 10:
            word_freq = {}
            for word in words:
                word_freq[word] = word_freq.get(word, 0) + 1
            
            max_freq = max(word_freq.values())
            if max_freq > len(words) * 0.3:  # More than 30% repetition
                score += 20
                evidence.append(RiskEvidence(
                    type="repetition_anomaly",
                    confidence=0.7,
                    description=f"High word repetition detected (max: {max_freq})",
                    data={"max_frequency": max_freq, "total_words": len(words)},
                    source="anomaly_detector"
                ))
        
        # Special character anomaly
        special_chars = sum(1 for c in content if not c.isalnum() and not c.isspace())
        if special_chars > len(content) * 0.2:  # More than 20% special characters
            score += 12
            evidence.append(RiskEvidence(
                type="special_char_anomaly",
                confidence=0.5,
                description=f"High special character density ({special_chars} chars)",
                data={"special_chars": special_chars, "total_chars": len(content)},
                source="anomaly_detector"
            ))
        
        return min(score, 100.0), evidence
    
    def determine_severity(self, risk_score: float) -> RiskSeverity:
        """Determine risk severity based on score"""
        if risk_score >= self.severity_thresholds[RiskSeverity.CRITICAL]:
            return RiskSeverity.CRITICAL
        elif risk_score >= self.severity_thresholds[RiskSeverity.HIGH]:
            return RiskSeverity.HIGH
        elif risk_score >= self.severity_thresholds[RiskSeverity.MEDIUM]:
            return RiskSeverity.MEDIUM
        elif risk_score >= self.severity_thresholds[RiskSeverity.LOW]:
            return RiskSeverity.LOW
        else:
            return RiskSeverity.MINIMAL
    
    def generate_mitigation_actions(self, categories: List[RiskCategory], severity: RiskSeverity) -> List[MitigationAction]:
        """Generate mitigation actions based on detected risks"""
        actions = []
        
        if RiskCategory.MISINFORMATION in categories:
            actions.append(MitigationAction(
                action_type="content_flag",
                priority=2 if severity in [RiskSeverity.HIGH, RiskSeverity.CRITICAL] else 3,
                description="Flag content for fact-checking review",
                automated=True,
                estimated_effort="5 minutes"
            ))
        
        if RiskCategory.SECURITY_THREAT in categories:
            actions.append(MitigationAction(
                action_type="immediate_block",
                priority=1,
                description="Block content and alert security team",
                automated=True,
                estimated_effort="Immediate"
            ))
        
        if RiskCategory.ADVERSARIAL_ATTACK in categories:
            actions.append(MitigationAction(
                action_type="session_terminate",
                priority=1,
                description="Terminate session and log security event",
                automated=True,
                estimated_effort="Immediate"
            ))
        
        if RiskCategory.CONTENT_SAFETY in categories:
            actions.append(MitigationAction(
                action_type="content_moderate",
                priority=2,
                description="Remove content and notify user",
                automated=True,
                estimated_effort="2 minutes"
            ))
        
        if severity == RiskSeverity.CRITICAL:
            actions.append(MitigationAction(
                action_type="escalate_human",
                priority=1,
                description="Escalate to human reviewer immediately",
                automated=False,
                estimated_effort="15 minutes"
            ))
        
        return actions
    
    def assess_content(self, content: str, content_type: ContentType, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Main content assessment method"""
        start_time = time.time()
        
        if context is None:
            context = {}
        
        # Initialize results
        all_evidence = []
        category_scores = {}
        detected_categories = []
        detection_methods = []
        
        # Run all detection methods
        methods_and_detectors = [
            (DetectionMethod.PATTERN_MATCHING, self.detect_misinformation, RiskCategory.MISINFORMATION),
            (DetectionMethod.PATTERN_MATCHING, self.detect_security_threats, RiskCategory.SECURITY_THREAT),
            (DetectionMethod.PATTERN_MATCHING, self.detect_adversarial_attacks, RiskCategory.ADVERSARIAL_ATTACK),
            (DetectionMethod.PATTERN_MATCHING, self.detect_content_safety, RiskCategory.CONTENT_SAFETY),
            (DetectionMethod.ANOMALY_DETECTION, lambda c: self.detect_anomalies(c, context), RiskCategory.ANOMALY)
        ]
        
        for method, detector, category in methods_and_detectors:
            try:
                if category == RiskCategory.ANOMALY:
                    score, evidence = detector(content)
                else:
                    score, evidence = detector(content)
                
                if score > 0:
                    category_scores[category] = score
                    detected_categories.append(category)
                    all_evidence.extend(evidence)
                    if method not in detection_methods:
                        detection_methods.append(method)
                        
            except Exception as e:
                logger.error(f"Error in {method} detection: {e}")
        
        # Calculate overall risk score (weighted average)
        if category_scores:
            # Weight critical categories higher
            weights = {
                RiskCategory.SECURITY_THREAT: 1.5,
                RiskCategory.ADVERSARIAL_ATTACK: 1.4,
                RiskCategory.CONTENT_SAFETY: 1.2,
                RiskCategory.MISINFORMATION: 1.0,
                RiskCategory.ANOMALY: 0.8
            }
            
            weighted_sum = sum(score * weights.get(cat, 1.0) for cat, score in category_scores.items())
            total_weight = sum(weights.get(cat, 1.0) for cat in category_scores.keys())
            overall_score = min(weighted_sum / total_weight, 100.0)
        else:
            overall_score = 0.0
        
        # Determine severity
        severity = self.determine_severity(overall_score)
        
        # Calculate confidence
        confidence = min(len(all_evidence) * 0.2, 1.0) if all_evidence else 0.0
        
        # Generate mitigation actions
        mitigation_actions = self.generate_mitigation_actions(detected_categories, severity)
        
        # Calculate processing time
        processing_time = (time.time() - start_time) * 1000  # Convert to milliseconds
        
        return {
            "risk_score": round(overall_score, 2),
            "risk_severity": severity,
            "risk_categories": detected_categories,
            "detection_methods": detection_methods,
            "confidence": round(confidence, 3),
            "evidence": all_evidence,
            "mitigation_actions": mitigation_actions,
            "processing_time_ms": round(processing_time, 2),
            "model_version": self.model_version,
            "category_scores": {str(k): v for k, v in category_scores.items()}
        }


class RiskDetectionService:
    """Service for managing risk assessments"""
    
    def __init__(self):
        self.collection_name = "risk_assessments"
        self.engine = RiskDetectionEngine()
    
    @property
    def collection(self):
        """Get risk assessments collection"""
        if not mongodb.is_connected:
            raise RuntimeError("Database not connected")
        return mongodb.get_collection(self.collection_name)
    
    async def assess_content(self, content: str, content_type: ContentType, user_id: Optional[str] = None, context: Dict[str, Any] = None) -> RiskAssessmentResponse:
        """Assess content for risks"""
        try:
            if not mongodb.is_connected:
                logger.warning("⚠️ Database not connected, performing assessment only")
            
            # Generate content hash for deduplication
            content_hash = self.engine.calculate_content_hash(content)
            
            # Check for existing assessment
            if mongodb.is_connected:
                existing = await self.collection.find_one({"content_hash": content_hash})
                if existing:
                    logger.info(f"✅ Found existing assessment for content hash: {content_hash[:8]}...")
                    return self._convert_to_response(RiskAssessmentInDB(**existing))
            
            # Perform risk assessment
            assessment_result = self.engine.assess_content(content, content_type, context or {})
            
            # Create assessment record
            assessment_data = RiskAssessmentCreate(
                content_id=content_hash[:16],  # Use first 16 chars as content ID
                content_type=content_type,
                content_hash=content_hash,
                risk_score=assessment_result["risk_score"],
                risk_severity=assessment_result["risk_severity"],
                risk_categories=assessment_result["risk_categories"],
                detection_methods=assessment_result["detection_methods"],
                confidence=assessment_result["confidence"],
                evidence=assessment_result["evidence"],
                mitigation_actions=assessment_result["mitigation_actions"],
                processing_time_ms=assessment_result["processing_time_ms"],
                model_version=assessment_result["model_version"],
                metadata={"category_scores": assessment_result["category_scores"]},
                user_id=user_id,
                source_ip=context.get("source_ip") if context else None,
                user_agent=context.get("user_agent") if context else None,
                session_id=context.get("session_id") if context else None,
                organization_id=context.get("organization_id") if context else None
            )
            
            # Save to database if connected
            if mongodb.is_connected:
                assessment_doc = {
                    **assessment_data.dict(),
                    "user_id": ObjectId(user_id) if user_id else None,
                    "created_at": datetime.utcnow(),
                    "status": "completed"
                }
                
                result = await self.collection.insert_one(assessment_doc)
                assessment_doc["_id"] = result.inserted_id
                
                created_assessment = RiskAssessmentInDB(**assessment_doc)
                logger.info(f"✅ Risk assessment completed: Score {assessment_result['risk_score']}, Severity {assessment_result['risk_severity']}")
                
                return self._convert_to_response(created_assessment)
            else:
                # Return assessment without saving
                mock_assessment = RiskAssessmentInDB(
                    **assessment_data.dict(),
                    id=ObjectId(),
                    user_id=ObjectId(user_id) if user_id else None,
                    created_at=datetime.utcnow(),
                    status="completed"
                )
                return self._convert_to_response(mock_assessment)
                
        except Exception as e:
            logger.error(f"❌ Risk assessment failed: {e}")
            raise
    
    def _convert_to_response(self, assessment: RiskAssessmentInDB) -> RiskAssessmentResponse:
        """Convert database model to response model"""
        return RiskAssessmentResponse(
            id=str(assessment.id),
            content_id=assessment.content_id,
            content_type=assessment.content_type.value,
            content_hash=assessment.content_hash,
            risk_score=assessment.risk_score,
            risk_severity=assessment.risk_severity.value,
            risk_categories=[cat.value for cat in assessment.risk_categories],
            detection_methods=[method.value for method in assessment.detection_methods],
            confidence=assessment.confidence,
            evidence=assessment.evidence,
            source_ip=assessment.source_ip,
            user_agent=assessment.user_agent,
            session_id=assessment.session_id,
            organization_id=assessment.organization_id,
            mitigation_actions=assessment.mitigation_actions,
            auto_mitigated=assessment.auto_mitigated,
            created_at=assessment.created_at,
            updated_at=assessment.updated_at,
            status=assessment.status,
            escalated=assessment.escalated,
            processing_time_ms=assessment.processing_time_ms,
            model_version=assessment.model_version
        )
    
    async def get_assessments(self, filter_params: RiskAssessmentFilter) -> List[RiskAssessmentResponse]:
        """Get risk assessments with filtering"""
        try:
            if not mongodb.is_connected:
                return []
            
            # Build query
            query = {}
            
            if filter_params.start_date:
                query["created_at"] = {"$gte": filter_params.start_date}
            if filter_params.end_date:
                if "created_at" in query:
                    query["created_at"]["$lte"] = filter_params.end_date
                else:
                    query["created_at"] = {"$lte": filter_params.end_date}
            
            if filter_params.min_risk_score is not None:
                query["risk_score"] = {"$gte": filter_params.min_risk_score}
            if filter_params.max_risk_score is not None:
                if "risk_score" in query:
                    query["risk_score"]["$lte"] = filter_params.max_risk_score
                else:
                    query["risk_score"] = {"$lte": filter_params.max_risk_score}
            
            if filter_params.severities:
                query["risk_severity"] = {"$in": [s.value for s in filter_params.severities]}
            
            if filter_params.categories:
                query["risk_categories"] = {"$in": [c.value for c in filter_params.categories]}
            
            if filter_params.user_id:
                query["user_id"] = ObjectId(filter_params.user_id)
            
            if filter_params.escalated_only:
                query["escalated"] = True
            
            if filter_params.status:
                query["status"] = filter_params.status
            
            # Execute query
            cursor = self.collection.find(query).sort("created_at", -1).skip(filter_params.skip).limit(filter_params.limit)
            assessments = []
            
            async for doc in cursor:
                assessment = RiskAssessmentInDB(**doc)
                assessments.append(self._convert_to_response(assessment))
            
            return assessments
            
        except Exception as e:
            logger.error(f"❌ Failed to get assessments: {e}")
            return []
    
    async def get_stats(self, user_id: Optional[str] = None) -> RiskAssessmentStats:
        """Get risk assessment statistics"""
        try:
            if not mongodb.is_connected:
                return RiskAssessmentStats(
                    total_assessments=0,
                    by_severity={},
                    by_category={},
                    by_status={},
                    average_risk_score=0.0,
                    average_processing_time_ms=0.0,
                    escalation_rate=0.0,
                    auto_mitigation_rate=0.0
                )
            
            # Build base query
            base_query = {}
            if user_id:
                base_query["user_id"] = ObjectId(user_id)
            
            # Get total count
            total = await self.collection.count_documents(base_query)
            
            if total == 0:
                return RiskAssessmentStats(
                    total_assessments=0,
                    by_severity={},
                    by_category={},
                    by_status={},
                    average_risk_score=0.0,
                    average_processing_time_ms=0.0,
                    escalation_rate=0.0,
                    auto_mitigation_rate=0.0
                )
            
            # Aggregation pipeline for statistics
            pipeline = [
                {"$match": base_query},
                {"$group": {
                    "_id": None,
                    "total": {"$sum": 1},
                    "avg_score": {"$avg": "$risk_score"},
                    "avg_processing_time": {"$avg": "$processing_time_ms"},
                    "escalated_count": {"$sum": {"$cond": ["$escalated", 1, 0]}},
                    "auto_mitigated_count": {"$sum": {"$cond": ["$auto_mitigated", 1, 0]}},
                    "severities": {"$push": "$risk_severity"},
                    "categories": {"$push": "$risk_categories"},
                    "statuses": {"$push": "$status"}
                }}
            ]
            
            result = await self.collection.aggregate(pipeline).to_list(1)
            
            if not result:
                return RiskAssessmentStats(
                    total_assessments=0,
                    by_severity={},
                    by_category={},
                    by_status={},
                    average_risk_score=0.0,
                    average_processing_time_ms=0.0,
                    escalation_rate=0.0,
                    auto_mitigation_rate=0.0
                )
            
            data = result[0]
            
            # Count severities
            by_severity = {}
            for severity in data["severities"]:
                by_severity[severity] = by_severity.get(severity, 0) + 1
            
            # Count categories (flatten nested arrays)
            by_category = {}
            for category_list in data["categories"]:
                for category in category_list:
                    by_category[category] = by_category.get(category, 0) + 1
            
            # Count statuses
            by_status = {}
            for status in data["statuses"]:
                by_status[status] = by_status.get(status, 0) + 1
            
            return RiskAssessmentStats(
                total_assessments=data["total"],
                by_severity=by_severity,
                by_category=by_category,
                by_status=by_status,
                average_risk_score=round(data["avg_score"], 2),
                average_processing_time_ms=round(data["avg_processing_time"], 2),
                escalation_rate=round((data["escalated_count"] / data["total"]) * 100, 2),
                auto_mitigation_rate=round((data["auto_mitigated_count"] / data["total"]) * 100, 2)
            )
            
        except Exception as e:
            logger.error(f"❌ Failed to get risk assessment stats: {e}")
            return RiskAssessmentStats(
                total_assessments=0,
                by_severity={},
                by_category={},
                by_status={},
                average_risk_score=0.0,
                average_processing_time_ms=0.0,
                escalation_rate=0.0,
                auto_mitigation_rate=0.0
            )


# Global service instance
risk_detection_service = RiskDetectionService()

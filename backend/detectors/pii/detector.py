"""
🔒 Advanced PII Detection Engine
Detects and securely handles Personally Identifiable Information
"""
import re
import hashlib
import hmac
import secrets
from typing import Dict, List, Tuple, Any, Optional
from datetime import datetime
import spacy
from transformers import pipeline
import phonenumbers
from email_validator import validate_email, EmailNotValidError
import logging

logger = logging.getLogger(__name__)

class PIIDetector:
    """Advanced PII Detection with secure hashing and storage"""
    
    def __init__(self):
        self.confidence_threshold = 0.8
        self.salt = self._generate_salt()
        
        # Load NLP models
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except OSError:
            logger.warning("spaCy model not found. Install with: python -m spacy download en_core_web_sm")
            self.nlp = None
            
        # Initialize NER pipeline for additional PII detection
        try:
            self.ner_pipeline = pipeline("ner", 
                                       model="dbmdz/bert-large-cased-finetuned-conll03-english",
                                       aggregation_strategy="simple")
        except Exception as e:
            logger.warning(f"Could not load NER pipeline: {e}")
            self.ner_pipeline = None
        
        # PII patterns with enhanced regex
        self.pii_patterns = {
            'ssn': {
                'pattern': re.compile(r'\b(?:\d{3}-?\d{2}-?\d{4}|\d{9})\b'),
                'severity': 'critical',
                'description': 'Social Security Number'
            },
            'credit_card': {
                'pattern': re.compile(r'\b(?:4[0-9]{12}(?:[0-9]{3})?|5[1-5][0-9]{14}|3[47][0-9]{13}|3[0-9]{13}|6(?:011|5[0-9]{2})[0-9]{12})\b'),
                'severity': 'critical',
                'description': 'Credit Card Number'
            },
            'phone': {
                'pattern': re.compile(r'\b(?:\+?1[-.\s]?)?\(?[0-9]{3}\)?[-.\s]?[0-9]{3}[-.\s]?[0-9]{4}\b'),
                'severity': 'high',
                'description': 'Phone Number'
            },
            'email': {
                'pattern': re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'),
                'severity': 'medium',
                'description': 'Email Address'
            },
            'ip_address': {
                'pattern': re.compile(r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b'),
                'severity': 'medium',
                'description': 'IP Address'
            },
            'passport': {
                'pattern': re.compile(r'\b[A-Z]{1,2}[0-9]{6,9}\b'),
                'severity': 'critical',
                'description': 'Passport Number'
            },
            'driver_license': {
                'pattern': re.compile(r'\b[A-Z]{1,2}[0-9]{6,8}\b'),
                'severity': 'high',
                'description': 'Driver License'
            },
            'bank_account': {
                'pattern': re.compile(r'\b[0-9]{8,17}\b'),
                'severity': 'critical',
                'description': 'Bank Account Number'
            },
            'aadhaar': {
                'pattern': re.compile(r'\b[0-9]{4}\s?[0-9]{4}\s?[0-9]{4}\b'),
                'severity': 'critical',
                'description': 'Aadhaar Number (India)'
            },
            'pan': {
                'pattern': re.compile(r'\b[A-Z]{5}[0-9]{4}[A-Z]{1}\b'),
                'severity': 'high',
                'description': 'PAN Number (India)'
            }
        }
        
    def _generate_salt(self) -> bytes:
        """Generate cryptographic salt for hashing"""
        return secrets.token_bytes(32)
    
    def _hash_pii(self, pii_value: str, pii_type: str) -> str:
        """Securely hash PII data with salt and type-specific pepper"""
        pepper = f"AIRMS_PII_{pii_type.upper()}"
        combined = f"{pepper}{pii_value}{self.salt.hex()}"
        return hashlib.sha256(combined.encode()).hexdigest()
    
    def _validate_email(self, email: str) -> bool:
        """Validate email format"""
        try:
            validate_email(email)
            return True
        except EmailNotValidError:
            return False
    
    def _validate_phone(self, phone: str) -> bool:
        """Validate phone number format"""
        try:
            parsed = phonenumbers.parse(phone, None)
            return phonenumbers.is_valid_number(parsed)
        except:
            return False
    
    def _luhn_check(self, card_number: str) -> bool:
        """Validate credit card using Luhn algorithm"""
        def luhn_checksum(card_num):
            def digits_of(n):
                return [int(d) for d in str(n)]
            digits = digits_of(card_num)
            odd_digits = digits[-1::-2]
            even_digits = digits[-2::-2]
            checksum = sum(odd_digits)
            for d in even_digits:
                checksum += sum(digits_of(d*2))
            return checksum % 10
        return luhn_checksum(card_number.replace(' ', '').replace('-', '')) == 0
    
    async def detect_pii(self, text: str, context: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Comprehensive PII detection with multiple validation layers
        """
        results = {
            'pii_found': [],
            'risk_score': 0,
            'severity': 'low',
            'masked_text': text,
            'hashed_pii': {},
            'metadata': {
                'detection_timestamp': datetime.utcnow().isoformat(),
                'detection_methods': [],
                'context': context or {}
            }
        }
        
        # Pattern-based detection
        await self._pattern_based_detection(text, results)
        
        # NLP-based detection
        if self.nlp:
            await self._nlp_based_detection(text, results)
            
        # NER-based detection
        if self.ner_pipeline:
            await self._ner_based_detection(text, results)
        
        # Calculate overall risk score
        self._calculate_risk_score(results)
        
        # Generate masked text
        self._generate_masked_text(results)
        
        return results
    
    async def _pattern_based_detection(self, text: str, results: Dict):
        """Pattern-based PII detection with validation"""
        results['metadata']['detection_methods'].append('pattern_based')
        
        for pii_type, config in self.pii_patterns.items():
            matches = config['pattern'].findall(text)
            
            for match in matches:
                # Additional validation for specific PII types
                is_valid = True
                confidence = 0.8
                
                if pii_type == 'email':
                    is_valid = self._validate_email(match)
                    confidence = 0.95 if is_valid else 0.3
                elif pii_type == 'phone':
                    is_valid = self._validate_phone(match)
                    confidence = 0.9 if is_valid else 0.4
                elif pii_type == 'credit_card':
                    is_valid = self._luhn_check(match)
                    confidence = 0.95 if is_valid else 0.2
                
                if is_valid and confidence >= self.confidence_threshold:
                    # Hash the PII for secure storage
                    hashed_value = self._hash_pii(match, pii_type)
                    
                    pii_item = {
                        'type': pii_type,
                        'value': match,
                        'hashed_value': hashed_value,
                        'severity': config['severity'],
                        'confidence': confidence,
                        'description': config['description'],
                        'position': text.find(match),
                        'detection_method': 'pattern_regex'
                    }
                    
                    results['pii_found'].append(pii_item)
                    results['hashed_pii'][hashed_value] = {
                        'type': pii_type,
                        'severity': config['severity'],
                        'timestamp': datetime.utcnow().isoformat()
                    }
    
    async def _nlp_based_detection(self, text: str, results: Dict):
        """NLP-based PII detection using spaCy"""
        results['metadata']['detection_methods'].append('nlp_spacy')
        
        doc = self.nlp(text)
        
        for ent in doc.ents:
            if ent.label_ in ['PERSON', 'ORG', 'GPE', 'DATE', 'MONEY']:
                severity = 'medium' if ent.label_ == 'PERSON' else 'low'
                confidence = 0.7
                
                hashed_value = self._hash_pii(ent.text, ent.label_.lower())
                
                pii_item = {
                    'type': f'named_entity_{ent.label_.lower()}',
                    'value': ent.text,
                    'hashed_value': hashed_value,
                    'severity': severity,
                    'confidence': confidence,
                    'description': f'Named Entity: {ent.label_}',
                    'position': ent.start_char,
                    'detection_method': 'nlp_spacy'
                }
                
                results['pii_found'].append(pii_item)
                results['hashed_pii'][hashed_value] = {
                    'type': f'named_entity_{ent.label_.lower()}',
                    'severity': severity,
                    'timestamp': datetime.utcnow().isoformat()
                }
    
    async def _ner_based_detection(self, text: str, results: Dict):
        """NER-based PII detection using transformers"""
        results['metadata']['detection_methods'].append('ner_transformers')
        
        try:
            entities = self.ner_pipeline(text)
            
            for entity in entities:
                if entity['entity_group'] in ['PER', 'ORG', 'LOC']:
                    severity = 'medium' if entity['entity_group'] == 'PER' else 'low'
                    confidence = entity['score']
                    
                    if confidence >= self.confidence_threshold:
                        hashed_value = self._hash_pii(entity['word'], entity['entity_group'].lower())
                        
                        pii_item = {
                            'type': f'ner_{entity["entity_group"].lower()}',
                            'value': entity['word'],
                            'hashed_value': hashed_value,
                            'severity': severity,
                            'confidence': confidence,
                            'description': f'NER Entity: {entity["entity_group"]}',
                            'position': entity['start'],
                            'detection_method': 'ner_transformers'
                        }
                        
                        results['pii_found'].append(pii_item)
                        results['hashed_pii'][hashed_value] = {
                            'type': f'ner_{entity["entity_group"].lower()}',
                            'severity': severity,
                            'timestamp': datetime.utcnow().isoformat()
                        }
        except Exception as e:
            logger.error(f"NER detection failed: {e}")
    
    def _calculate_risk_score(self, results: Dict):
        """Calculate overall PII risk score"""
        if not results['pii_found']:
            results['risk_score'] = 0
            results['severity'] = 'minimal'
            return
        
        severity_weights = {
            'critical': 25,
            'high': 15,
            'medium': 10,
            'low': 5,
            'minimal': 1
        }
        
        total_score = 0
        max_severity = 'minimal'
        
        for pii in results['pii_found']:
            weight = severity_weights.get(pii['severity'], 1)
            confidence_factor = pii['confidence']
            total_score += weight * confidence_factor
            
            # Track highest severity
            if severity_weights[pii['severity']] > severity_weights[max_severity]:
                max_severity = pii['severity']
        
        results['risk_score'] = min(100, total_score)
        results['severity'] = max_severity
    
    def _generate_masked_text(self, results: Dict):
        """Generate masked version of text with PII replaced"""
        masked_text = results['masked_text']
        
        # Sort by position in reverse order to maintain positions
        pii_items = sorted(results['pii_found'], key=lambda x: x['position'], reverse=True)
        
        for pii in pii_items:
            start_pos = pii['position']
            end_pos = start_pos + len(pii['value'])
            
            # Create mask based on PII type
            if pii['severity'] == 'critical':
                mask = '[REDACTED]'
            elif pii['severity'] == 'high':
                mask = f'[{pii["type"].upper()}]'
            else:
                # Partial masking for lower severity
                value = pii['value']
                if len(value) > 4:
                    mask = value[:2] + '*' * (len(value) - 4) + value[-2:]
                else:
                    mask = '*' * len(value)
            
            masked_text = masked_text[:start_pos] + mask + masked_text[end_pos:]
        
        results['masked_text'] = masked_text

    def get_pii_statistics(self, results: Dict) -> Dict[str, Any]:
        """Generate PII detection statistics"""
        stats = {
            'total_pii_found': len(results['pii_found']),
            'by_severity': {},
            'by_type': {},
            'by_detection_method': {},
            'risk_assessment': {
                'score': results['risk_score'],
                'severity': results['severity'],
                'recommendation': self._get_risk_recommendation(results['risk_score'])
            }
        }
        
        for pii in results['pii_found']:
            # Count by severity
            severity = pii['severity']
            stats['by_severity'][severity] = stats['by_severity'].get(severity, 0) + 1
            
            # Count by type
            pii_type = pii['type']
            stats['by_type'][pii_type] = stats['by_type'].get(pii_type, 0) + 1
            
            # Count by detection method
            method = pii['detection_method']
            stats['by_detection_method'][method] = stats['by_detection_method'].get(method, 0) + 1
        
        return stats
    
    def _get_risk_recommendation(self, risk_score: float) -> str:
        """Get risk-based recommendation"""
        if risk_score >= 80:
            return "CRITICAL: Immediate action required. Block or heavily sanitize content."
        elif risk_score >= 60:
            return "HIGH: Review and sanitize before processing."
        elif risk_score >= 40:
            return "MEDIUM: Monitor and apply standard sanitization."
        elif risk_score >= 20:
            return "LOW: Log for audit purposes."
        else:
            return "MINIMAL: Standard processing acceptable."

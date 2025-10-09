"""
🛡️ Advanced Input Sanitization & Validation System
Multi-layer security for input processing
"""
import re
import html
import bleach
import hashlib
from typing import Dict, List, Any, Optional, Tuple
from urllib.parse import urlparse, quote
import logging
from datetime import datetime
import unicodedata

logger = logging.getLogger(__name__)

class InputSanitizer:
    """Advanced input sanitization with multiple security layers"""
    
    def __init__(self):
        # XSS prevention patterns
        self.xss_patterns = [
            re.compile(r'<script[^>]*>.*?</script>', re.IGNORECASE | re.DOTALL),
            re.compile(r'javascript:', re.IGNORECASE),
            re.compile(r'vbscript:', re.IGNORECASE),
            re.compile(r'onload\s*=', re.IGNORECASE),
            re.compile(r'onerror\s*=', re.IGNORECASE),
            re.compile(r'onclick\s*=', re.IGNORECASE),
            re.compile(r'onmouseover\s*=', re.IGNORECASE),
            re.compile(r'expression\s*\(', re.IGNORECASE),
            re.compile(r'<iframe[^>]*>', re.IGNORECASE),
            re.compile(r'<object[^>]*>', re.IGNORECASE),
            re.compile(r'<embed[^>]*>', re.IGNORECASE),
        ]
        
        # SQL injection patterns
        self.sql_patterns = [
            re.compile(r'(\b(SELECT|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER|EXEC)\b)', re.IGNORECASE),
            re.compile(r'(\b(UNION|JOIN)\b.*\b(SELECT)\b)', re.IGNORECASE),
            re.compile(r'(\b(OR|AND)\b\s+\d+\s*=\s*\d+)', re.IGNORECASE),
            re.compile(r'(\'\s*(OR|AND)\s*\')', re.IGNORECASE),
            re.compile(r'(--|\#|\/\*)', re.IGNORECASE),
            re.compile(r'(\bxp_cmdshell\b)', re.IGNORECASE),
        ]
        
        # NoSQL injection patterns
        self.nosql_patterns = [
            re.compile(r'\$where', re.IGNORECASE),
            re.compile(r'\$ne\s*:', re.IGNORECASE),
            re.compile(r'\$gt\s*:', re.IGNORECASE),
            re.compile(r'\$lt\s*:', re.IGNORECASE),
            re.compile(r'\$regex\s*:', re.IGNORECASE),
            re.compile(r'function\s*\(', re.IGNORECASE),
        ]
        
        # Command injection patterns
        self.command_patterns = [
            re.compile(r'[;&|`$(){}[\]<>]'),
            re.compile(r'\b(cat|ls|pwd|whoami|id|uname|ps|netstat|ifconfig|wget|curl)\b', re.IGNORECASE),
            re.compile(r'(\.\.\/|\.\.\\\\)', re.IGNORECASE),
            re.compile(r'\/etc\/passwd', re.IGNORECASE),
            re.compile(r'\/proc\/', re.IGNORECASE),
        ]
        
        # LDAP injection patterns
        self.ldap_patterns = [
            re.compile(r'[()&|!*]'),
            re.compile(r'\\[0-9a-fA-F]{2}'),
        ]
        
        # Allowed HTML tags and attributes for content sanitization
        self.allowed_tags = ['p', 'br', 'strong', 'em', 'u', 'ol', 'ul', 'li', 'blockquote']
        self.allowed_attributes = {
            '*': ['class'],
            'a': ['href', 'title'],
        }
        
        # Maximum input lengths by type
        self.max_lengths = {
            'text': 32768,      # 32KB
            'title': 200,
            'description': 1000,
            'url': 2048,
            'email': 254,
            'phone': 20,
            'name': 100,
        }
        
        # Dangerous file extensions
        self.dangerous_extensions = {
            'exe', 'bat', 'cmd', 'com', 'pif', 'scr', 'vbs', 'js', 'jar',
            'php', 'asp', 'aspx', 'jsp', 'sh', 'py', 'rb', 'pl'
        }
    
    async def sanitize(self, 
                      input_data: str, 
                      input_type: str = 'text',
                      context: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Comprehensive input sanitization with security validation
        """
        sanitization_result = {
            'original_input': input_data,
            'sanitized_input': input_data,
            'security_issues': [],
            'risk_score': 0,
            'is_safe': True,
            'metadata': {
                'sanitization_timestamp': datetime.utcnow().isoformat(),
                'input_type': input_type,
                'context': context or {},
                'applied_filters': []
            }
        }
        
        try:
            # Step 1: Basic validation
            await self._basic_validation(input_data, input_type, sanitization_result)
            
            # Step 2: Length validation
            await self._length_validation(input_data, input_type, sanitization_result)
            
            # Step 3: Encoding normalization
            sanitization_result['sanitized_input'] = await self._normalize_encoding(
                sanitization_result['sanitized_input'], sanitization_result
            )
            
            # Step 4: XSS prevention
            sanitization_result['sanitized_input'] = await self._prevent_xss(
                sanitization_result['sanitized_input'], sanitization_result
            )
            
            # Step 5: SQL injection prevention
            await self._detect_sql_injection(
                sanitization_result['sanitized_input'], sanitization_result
            )
            
            # Step 6: NoSQL injection prevention
            await self._detect_nosql_injection(
                sanitization_result['sanitized_input'], sanitization_result
            )
            
            # Step 7: Command injection prevention
            await self._detect_command_injection(
                sanitization_result['sanitized_input'], sanitization_result
            )
            
            # Step 8: LDAP injection prevention
            await self._detect_ldap_injection(
                sanitization_result['sanitized_input'], sanitization_result
            )
            
            # Step 9: URL validation (if applicable)
            if input_type == 'url':
                await self._validate_url(
                    sanitization_result['sanitized_input'], sanitization_result
                )
            
            # Step 10: File extension validation (if applicable)
            if input_type == 'filename':
                await self._validate_filename(
                    sanitization_result['sanitized_input'], sanitization_result
                )
            
            # Step 11: Calculate final risk score
            self._calculate_risk_score(sanitization_result)
            
            # Step 12: Apply final sanitization based on risk
            sanitization_result['sanitized_input'] = await self._apply_final_sanitization(
                sanitization_result['sanitized_input'], sanitization_result
            )
            
        except Exception as e:
            logger.error(f"Sanitization error: {e}")
            sanitization_result['security_issues'].append({
                'type': 'sanitization_error',
                'severity': 'high',
                'description': f'Error during sanitization: {str(e)}',
                'timestamp': datetime.utcnow().isoformat()
            })
            sanitization_result['is_safe'] = False
            sanitization_result['risk_score'] = 100
        
        return sanitization_result
    
    async def _basic_validation(self, input_data: str, input_type: str, result: Dict):
        """Basic input validation"""
        if not isinstance(input_data, str):
            result['security_issues'].append({
                'type': 'invalid_type',
                'severity': 'medium',
                'description': f'Expected string, got {type(input_data).__name__}',
                'timestamp': datetime.utcnow().isoformat()
            })
        
        if not input_data.strip():
            result['security_issues'].append({
                'type': 'empty_input',
                'severity': 'low',
                'description': 'Input is empty or contains only whitespace',
                'timestamp': datetime.utcnow().isoformat()
            })
    
    async def _length_validation(self, input_data: str, input_type: str, result: Dict):
        """Validate input length"""
        max_length = self.max_lengths.get(input_type, self.max_lengths['text'])
        
        if len(input_data) > max_length:
            result['security_issues'].append({
                'type': 'length_exceeded',
                'severity': 'medium',
                'description': f'Input length {len(input_data)} exceeds maximum {max_length}',
                'timestamp': datetime.utcnow().isoformat()
            })
            # Truncate input
            result['sanitized_input'] = input_data[:max_length]
            result['metadata']['applied_filters'].append('length_truncation')
    
    async def _normalize_encoding(self, input_data: str, result: Dict) -> str:
        """Normalize Unicode encoding to prevent bypass attempts"""
        try:
            # Normalize Unicode
            normalized = unicodedata.normalize('NFKC', input_data)
            
            # Remove null bytes and other control characters
            normalized = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', normalized)
            
            if normalized != input_data:
                result['metadata']['applied_filters'].append('encoding_normalization')
            
            return normalized
        except Exception as e:
            logger.error(f"Encoding normalization error: {e}")
            return input_data
    
    async def _prevent_xss(self, input_data: str, result: Dict) -> str:
        """Prevent XSS attacks"""
        original_input = input_data
        
        # HTML entity encoding
        sanitized = html.escape(input_data, quote=True)
        
        # Check for XSS patterns
        for pattern in self.xss_patterns:
            if pattern.search(input_data):
                result['security_issues'].append({
                    'type': 'xss_attempt',
                    'severity': 'high',
                    'description': f'Potential XSS pattern detected: {pattern.pattern}',
                    'timestamp': datetime.utcnow().isoformat()
                })
        
        # Use bleach for additional HTML sanitization
        sanitized = bleach.clean(
            sanitized,
            tags=self.allowed_tags,
            attributes=self.allowed_attributes,
            strip=True
        )
        
        if sanitized != original_input:
            result['metadata']['applied_filters'].append('xss_prevention')
        
        return sanitized
    
    async def _detect_sql_injection(self, input_data: str, result: Dict):
        """Detect SQL injection attempts"""
        for pattern in self.sql_patterns:
            matches = pattern.findall(input_data)
            if matches:
                result['security_issues'].append({
                    'type': 'sql_injection',
                    'severity': 'critical',
                    'description': f'Potential SQL injection detected: {matches}',
                    'timestamp': datetime.utcnow().isoformat()
                })
    
    async def _detect_nosql_injection(self, input_data: str, result: Dict):
        """Detect NoSQL injection attempts"""
        for pattern in self.nosql_patterns:
            if pattern.search(input_data):
                result['security_issues'].append({
                    'type': 'nosql_injection',
                    'severity': 'critical',
                    'description': f'Potential NoSQL injection detected: {pattern.pattern}',
                    'timestamp': datetime.utcnow().isoformat()
                })
    
    async def _detect_command_injection(self, input_data: str, result: Dict):
        """Detect command injection attempts"""
        for pattern in self.command_patterns:
            matches = pattern.findall(input_data)
            if matches:
                result['security_issues'].append({
                    'type': 'command_injection',
                    'severity': 'critical',
                    'description': f'Potential command injection detected: {matches}',
                    'timestamp': datetime.utcnow().isoformat()
                })
    
    async def _detect_ldap_injection(self, input_data: str, result: Dict):
        """Detect LDAP injection attempts"""
        for pattern in self.ldap_patterns:
            if pattern.search(input_data):
                result['security_issues'].append({
                    'type': 'ldap_injection',
                    'severity': 'high',
                    'description': f'Potential LDAP injection detected: {pattern.pattern}',
                    'timestamp': datetime.utcnow().isoformat()
                })
    
    async def _validate_url(self, input_data: str, result: Dict):
        """Validate URL format and security"""
        try:
            parsed = urlparse(input_data)
            
            # Check for valid scheme
            if parsed.scheme not in ['http', 'https']:
                result['security_issues'].append({
                    'type': 'invalid_url_scheme',
                    'severity': 'medium',
                    'description': f'Invalid URL scheme: {parsed.scheme}',
                    'timestamp': datetime.utcnow().isoformat()
                })
            
            # Check for localhost/internal IPs
            if parsed.hostname in ['localhost', '127.0.0.1', '0.0.0.0']:
                result['security_issues'].append({
                    'type': 'internal_url',
                    'severity': 'medium',
                    'description': 'URL points to internal/localhost address',
                    'timestamp': datetime.utcnow().isoformat()
                })
            
        except Exception as e:
            result['security_issues'].append({
                'type': 'url_parse_error',
                'severity': 'medium',
                'description': f'Failed to parse URL: {str(e)}',
                'timestamp': datetime.utcnow().isoformat()
            })
    
    async def _validate_filename(self, input_data: str, result: Dict):
        """Validate filename security"""
        # Check for path traversal
        if '..' in input_data or '/' in input_data or '\\' in input_data:
            result['security_issues'].append({
                'type': 'path_traversal',
                'severity': 'high',
                'description': 'Potential path traversal in filename',
                'timestamp': datetime.utcnow().isoformat()
            })
        
        # Check for dangerous extensions
        extension = input_data.split('.')[-1].lower() if '.' in input_data else ''
        if extension in self.dangerous_extensions:
            result['security_issues'].append({
                'type': 'dangerous_file_extension',
                'severity': 'high',
                'description': f'Dangerous file extension: {extension}',
                'timestamp': datetime.utcnow().isoformat()
            })
    
    def _calculate_risk_score(self, result: Dict):
        """Calculate overall risk score based on security issues"""
        severity_weights = {
            'critical': 30,
            'high': 20,
            'medium': 10,
            'low': 5
        }
        
        total_score = 0
        for issue in result['security_issues']:
            weight = severity_weights.get(issue['severity'], 5)
            total_score += weight
        
        result['risk_score'] = min(100, total_score)
        result['is_safe'] = result['risk_score'] < 50
    
    async def _apply_final_sanitization(self, input_data: str, result: Dict) -> str:
        """Apply final sanitization based on risk assessment"""
        if result['risk_score'] >= 80:
            # High risk: aggressive sanitization
            sanitized = re.sub(r'[^\w\s\-_.,!?]', '', input_data)
            result['metadata']['applied_filters'].append('aggressive_sanitization')
        elif result['risk_score'] >= 50:
            # Medium risk: moderate sanitization
            sanitized = re.sub(r'[<>"\']', '', input_data)
            result['metadata']['applied_filters'].append('moderate_sanitization')
        else:
            # Low risk: minimal sanitization
            sanitized = input_data.strip()
            result['metadata']['applied_filters'].append('minimal_sanitization')
        
        return sanitized
    
    def get_sanitization_report(self, result: Dict) -> Dict[str, Any]:
        """Generate comprehensive sanitization report"""
        return {
            'input_length': len(result['original_input']),
            'output_length': len(result['sanitized_input']),
            'risk_assessment': {
                'score': result['risk_score'],
                'is_safe': result['is_safe'],
                'recommendation': self._get_risk_recommendation(result['risk_score'])
            },
            'security_summary': {
                'total_issues': len(result['security_issues']),
                'by_severity': self._count_by_severity(result['security_issues']),
                'by_type': self._count_by_type(result['security_issues'])
            },
            'applied_filters': result['metadata']['applied_filters'],
            'processing_time': result['metadata']['sanitization_timestamp']
        }
    
    def _count_by_severity(self, issues: List[Dict]) -> Dict[str, int]:
        """Count security issues by severity"""
        counts = {}
        for issue in issues:
            severity = issue['severity']
            counts[severity] = counts.get(severity, 0) + 1
        return counts
    
    def _count_by_type(self, issues: List[Dict]) -> Dict[str, int]:
        """Count security issues by type"""
        counts = {}
        for issue in issues:
            issue_type = issue['type']
            counts[issue_type] = counts.get(issue_type, 0) + 1
        return counts
    
    def _get_risk_recommendation(self, risk_score: float) -> str:
        """Get risk-based recommendation"""
        if risk_score >= 80:
            return "CRITICAL: Block input immediately. Manual review required."
        elif risk_score >= 50:
            return "HIGH: Apply additional sanitization and monitoring."
        elif risk_score >= 20:
            return "MEDIUM: Standard processing with logging."
        else:
            return "LOW: Safe for processing."

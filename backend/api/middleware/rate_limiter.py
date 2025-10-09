"""
🚦 Advanced Rate Limiting & DDoS Protection Middleware
Multi-layer protection against abuse and attacks
"""
import asyncio
import time
import hashlib
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from collections import defaultdict, deque
import logging
from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
import redis
import ipaddress

logger = logging.getLogger(__name__)

class RateLimiter:
    """Advanced rate limiting with multiple strategies"""
    
    def __init__(self, redis_client: Optional[redis.Redis] = None):
        self.redis_client = redis_client
        self.memory_store = defaultdict(lambda: defaultdict(deque))
        
        # Rate limiting rules
        self.rate_limits = {
            'default': {
                'requests_per_minute': 60,
                'requests_per_hour': 1000,
                'requests_per_day': 10000,
                'burst_limit': 10,
                'window_size': 60
            },
            'authenticated': {
                'requests_per_minute': 120,
                'requests_per_hour': 5000,
                'requests_per_day': 50000,
                'burst_limit': 20,
                'window_size': 60
            },
            'premium': {
                'requests_per_minute': 300,
                'requests_per_hour': 15000,
                'requests_per_day': 150000,
                'burst_limit': 50,
                'window_size': 60
            },
            'analysis_endpoint': {
                'requests_per_minute': 30,
                'requests_per_hour': 500,
                'requests_per_day': 2000,
                'burst_limit': 5,
                'window_size': 60
            }
        }
        
        # DDoS protection settings
        self.ddos_protection = {
            'suspicious_threshold': 100,  # requests per minute
            'block_duration': 3600,       # 1 hour in seconds
            'progressive_delay': True,
            'max_delay': 30,              # seconds
            'whitelist_ips': set(),
            'blacklist_ips': set()
        }
        
        # Geolocation-based limits (mock data)
        self.geo_limits = {
            'high_risk_countries': ['XX', 'YY'],  # ISO country codes
            'restricted_multiplier': 0.5  # Reduce limits by 50%
        }
        
        # Suspicious pattern detection
        self.suspicious_patterns = {
            'rapid_user_agent_changes': 5,
            'no_user_agent': True,
            'suspicious_user_agents': [
                'bot', 'crawler', 'scraper', 'spider', 'curl', 'wget'
            ],
            'rapid_ip_changes': 10
        }
    
    async def check_rate_limit(self, 
                              request: Request, 
                              user_id: Optional[str] = None,
                              endpoint_type: str = 'default') -> Dict[str, any]:
        """
        Comprehensive rate limit checking with multiple factors
        """
        client_ip = self._get_client_ip(request)
        user_agent = request.headers.get('user-agent', '')
        
        # Create unique identifier
        identifier = self._create_identifier(client_ip, user_id, user_agent)
        
        # Check whitelist/blacklist
        if await self._is_blacklisted(client_ip):
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="IP address is blacklisted due to suspicious activity"
            )
        
        if await self._is_whitelisted(client_ip):
            return {'allowed': True, 'reason': 'whitelisted'}
        
        # Detect suspicious patterns
        suspicion_score = await self._detect_suspicious_patterns(request, identifier)
        
        # Get rate limit rules
        rules = self._get_rate_limit_rules(endpoint_type, user_id, suspicion_score)
        
        # Check multiple time windows
        rate_check_result = await self._check_multiple_windows(identifier, rules)
        
        if not rate_check_result['allowed']:
            # Apply progressive delay for repeated violations
            delay = await self._calculate_progressive_delay(identifier)
            if delay > 0:
                await asyncio.sleep(delay)
            
            # Log rate limit violation
            await self._log_rate_limit_violation(request, identifier, rate_check_result)
            
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=rate_check_result['message'],
                headers=rate_check_result.get('headers', {})
            )
        
        # Record successful request
        await self._record_request(identifier, rules)
        
        return rate_check_result
    
    def _get_client_ip(self, request: Request) -> str:
        """Extract real client IP considering proxies"""
        # Check for forwarded headers
        forwarded_for = request.headers.get('x-forwarded-for')
        if forwarded_for:
            # Take the first IP in the chain
            return forwarded_for.split(',')[0].strip()
        
        real_ip = request.headers.get('x-real-ip')
        if real_ip:
            return real_ip
        
        # Fallback to direct connection
        return request.client.host if request.client else 'unknown'
    
    def _create_identifier(self, ip: str, user_id: Optional[str], user_agent: str) -> str:
        """Create unique identifier for rate limiting"""
        if user_id:
            # Authenticated user: combine user_id and IP
            base_string = f"user:{user_id}:ip:{ip}"
        else:
            # Anonymous user: use IP and user agent hash
            ua_hash = hashlib.md5(user_agent.encode()).hexdigest()[:8]
            base_string = f"anon:ip:{ip}:ua:{ua_hash}"
        
        return hashlib.sha256(base_string.encode()).hexdigest()
    
    async def _is_blacklisted(self, ip: str) -> bool:
        """Check if IP is blacklisted"""
        if ip in self.ddos_protection['blacklist_ips']:
            return True
        
        # Check Redis blacklist if available
        if self.redis_client:
            try:
                return await self.redis_client.sismember('blacklisted_ips', ip)
            except Exception as e:
                logger.error(f"Redis blacklist check error: {e}")
        
        return False
    
    async def _is_whitelisted(self, ip: str) -> bool:
        """Check if IP is whitelisted"""
        if ip in self.ddos_protection['whitelist_ips']:
            return True
        
        # Check for private/internal IPs
        try:
            ip_obj = ipaddress.ip_address(ip)
            if ip_obj.is_private or ip_obj.is_loopback:
                return True
        except ValueError:
            pass
        
        # Check Redis whitelist if available
        if self.redis_client:
            try:
                return await self.redis_client.sismember('whitelisted_ips', ip)
            except Exception as e:
                logger.error(f"Redis whitelist check error: {e}")
        
        return False
    
    async def _detect_suspicious_patterns(self, request: Request, identifier: str) -> float:
        """Detect suspicious request patterns and return suspicion score (0-1)"""
        suspicion_score = 0.0
        user_agent = request.headers.get('user-agent', '').lower()
        
        # No User-Agent
        if not user_agent:
            suspicion_score += 0.3
        
        # Suspicious User-Agent patterns
        for suspicious_ua in self.suspicious_patterns['suspicious_user_agents']:
            if suspicious_ua in user_agent:
                suspicion_score += 0.2
                break
        
        # Rapid requests pattern (check recent request frequency)
        recent_requests = await self._get_recent_request_count(identifier, window=10)
        if recent_requests > 20:  # More than 20 requests in 10 seconds
            suspicion_score += 0.4
        
        # Missing common headers
        common_headers = ['accept', 'accept-language', 'accept-encoding']
        missing_headers = sum(1 for header in common_headers 
                            if header not in request.headers)
        suspicion_score += (missing_headers / len(common_headers)) * 0.2
        
        # Suspicious request patterns
        path = request.url.path.lower()
        if any(pattern in path for pattern in ['admin', 'config', '.env', 'backup']):
            suspicion_score += 0.3
        
        return min(1.0, suspicion_score)
    
    def _get_rate_limit_rules(self, 
                             endpoint_type: str, 
                             user_id: Optional[str], 
                             suspicion_score: float) -> Dict:
        """Get appropriate rate limit rules based on context"""
        # Base rules
        if user_id:
            if self._is_premium_user(user_id):
                rules = self.rate_limits['premium'].copy()
            else:
                rules = self.rate_limits['authenticated'].copy()
        else:
            rules = self.rate_limits['default'].copy()
        
        # Endpoint-specific adjustments
        if endpoint_type in self.rate_limits:
            endpoint_rules = self.rate_limits[endpoint_type]
            # Use more restrictive limits
            for key in ['requests_per_minute', 'requests_per_hour', 'requests_per_day']:
                rules[key] = min(rules[key], endpoint_rules[key])
        
        # Apply suspicion-based restrictions
        if suspicion_score > 0.5:
            multiplier = 1 - (suspicion_score * 0.8)  # Reduce by up to 80%
            for key in ['requests_per_minute', 'requests_per_hour', 'requests_per_day']:
                rules[key] = int(rules[key] * multiplier)
        
        return rules
    
    async def _check_multiple_windows(self, identifier: str, rules: Dict) -> Dict:
        """Check rate limits across multiple time windows"""
        current_time = time.time()
        
        # Check different time windows
        windows = [
            ('minute', 60, rules['requests_per_minute']),
            ('hour', 3600, rules['requests_per_hour']),
            ('day', 86400, rules['requests_per_day'])
        ]
        
        for window_name, window_seconds, limit in windows:
            count = await self._get_request_count(identifier, window_seconds)
            
            if count >= limit:
                reset_time = current_time + window_seconds
                return {
                    'allowed': False,
                    'message': f'Rate limit exceeded for {window_name}. Limit: {limit}',
                    'headers': {
                        'X-RateLimit-Limit': str(limit),
                        'X-RateLimit-Remaining': '0',
                        'X-RateLimit-Reset': str(int(reset_time)),
                        'Retry-After': str(window_seconds)
                    }
                }
        
        # Check burst limit
        burst_count = await self._get_request_count(identifier, rules['window_size'])
        if burst_count >= rules['burst_limit']:
            return {
                'allowed': False,
                'message': f'Burst limit exceeded. Limit: {rules["burst_limit"]}',
                'headers': {
                    'X-RateLimit-Limit': str(rules['burst_limit']),
                    'X-RateLimit-Remaining': '0',
                    'Retry-After': str(rules['window_size'])
                }
            }
        
        # Calculate remaining requests
        remaining = min(
            rules['requests_per_minute'] - await self._get_request_count(identifier, 60),
            rules['requests_per_hour'] - await self._get_request_count(identifier, 3600),
            rules['requests_per_day'] - await self._get_request_count(identifier, 86400)
        )
        
        return {
            'allowed': True,
            'headers': {
                'X-RateLimit-Limit': str(rules['requests_per_minute']),
                'X-RateLimit-Remaining': str(max(0, remaining)),
                'X-RateLimit-Reset': str(int(current_time + 60))
            }
        }
    
    async def _get_request_count(self, identifier: str, window_seconds: int) -> int:
        """Get request count for identifier within time window"""
        if self.redis_client:
            return await self._get_redis_count(identifier, window_seconds)
        else:
            return self._get_memory_count(identifier, window_seconds)
    
    async def _get_redis_count(self, identifier: str, window_seconds: int) -> int:
        """Get request count from Redis"""
        try:
            key = f"rate_limit:{identifier}:{window_seconds}"
            count = await self.redis_client.get(key)
            return int(count) if count else 0
        except Exception as e:
            logger.error(f"Redis count retrieval error: {e}")
            return 0
    
    def _get_memory_count(self, identifier: str, window_seconds: int) -> int:
        """Get request count from memory store"""
        current_time = time.time()
        cutoff_time = current_time - window_seconds
        
        # Clean old entries
        requests = self.memory_store[identifier][window_seconds]
        while requests and requests[0] < cutoff_time:
            requests.popleft()
        
        return len(requests)
    
    async def _get_recent_request_count(self, identifier: str, window: int) -> int:
        """Get recent request count for suspicious pattern detection"""
        return await self._get_request_count(identifier, window)
    
    async def _record_request(self, identifier: str, rules: Dict):
        """Record a successful request"""
        current_time = time.time()
        
        if self.redis_client:
            await self._record_redis_request(identifier, current_time)
        else:
            self._record_memory_request(identifier, current_time)
    
    async def _record_redis_request(self, identifier: str, timestamp: float):
        """Record request in Redis"""
        try:
            # Record for different time windows
            for window in [60, 3600, 86400]:
                key = f"rate_limit:{identifier}:{window}"
                await self.redis_client.incr(key)
                await self.redis_client.expire(key, window)
        except Exception as e:
            logger.error(f"Redis request recording error: {e}")
    
    def _record_memory_request(self, identifier: str, timestamp: float):
        """Record request in memory store"""
        # Record for different time windows
        for window in [60, 3600, 86400]:
            self.memory_store[identifier][window].append(timestamp)
            
            # Limit memory usage by keeping only recent entries
            cutoff_time = timestamp - window
            requests = self.memory_store[identifier][window]
            while requests and requests[0] < cutoff_time:
                requests.popleft()
    
    async def _calculate_progressive_delay(self, identifier: str) -> float:
        """Calculate progressive delay for repeated violations"""
        if not self.ddos_protection['progressive_delay']:
            return 0
        
        # Get violation count in the last hour
        violations = await self._get_violation_count(identifier, 3600)
        
        if violations <= 1:
            return 0
        
        # Exponential backoff: 2^(violations-1) seconds, capped at max_delay
        delay = min(2 ** (violations - 1), self.ddos_protection['max_delay'])
        return delay
    
    async def _get_violation_count(self, identifier: str, window: int) -> int:
        """Get rate limit violation count"""
        if self.redis_client:
            try:
                key = f"violations:{identifier}"
                count = await self.redis_client.get(key)
                return int(count) if count else 0
            except Exception as e:
                logger.error(f"Redis violation count error: {e}")
        
        return 0  # Fallback
    
    async def _log_rate_limit_violation(self, 
                                       request: Request, 
                                       identifier: str, 
                                       result: Dict):
        """Log rate limit violation for monitoring"""
        violation_data = {
            'timestamp': datetime.utcnow().isoformat(),
            'identifier': identifier,
            'ip': self._get_client_ip(request),
            'user_agent': request.headers.get('user-agent', ''),
            'path': request.url.path,
            'method': request.method,
            'reason': result['message']
        }
        
        logger.warning(f"Rate limit violation: {violation_data}")
        
        # Record violation in Redis for progressive delay calculation
        if self.redis_client:
            try:
                key = f"violations:{identifier}"
                await self.redis_client.incr(key)
                await self.redis_client.expire(key, 3600)  # 1 hour expiry
            except Exception as e:
                logger.error(f"Redis violation recording error: {e}")
    
    def _is_premium_user(self, user_id: str) -> bool:
        """Check if user has premium subscription (mock implementation)"""
        # In production, this would check your user database
        return user_id.startswith('premium_')
    
    async def add_to_blacklist(self, ip: str, duration: int = None):
        """Add IP to blacklist"""
        duration = duration or self.ddos_protection['block_duration']
        
        self.ddos_protection['blacklist_ips'].add(ip)
        
        if self.redis_client:
            try:
                await self.redis_client.sadd('blacklisted_ips', ip)
                await self.redis_client.expire('blacklisted_ips', duration)
            except Exception as e:
                logger.error(f"Redis blacklist addition error: {e}")
        
        logger.warning(f"IP {ip} added to blacklist for {duration} seconds")
    
    async def remove_from_blacklist(self, ip: str):
        """Remove IP from blacklist"""
        self.ddos_protection['blacklist_ips'].discard(ip)
        
        if self.redis_client:
            try:
                await self.redis_client.srem('blacklisted_ips', ip)
            except Exception as e:
                logger.error(f"Redis blacklist removal error: {e}")
        
        logger.info(f"IP {ip} removed from blacklist")
    
    async def get_rate_limit_stats(self, identifier: str) -> Dict:
        """Get current rate limit statistics for identifier"""
        stats = {}
        
        for window_name, window_seconds in [('minute', 60), ('hour', 3600), ('day', 86400)]:
            count = await self._get_request_count(identifier, window_seconds)
            stats[window_name] = {
                'requests': count,
                'window_seconds': window_seconds
            }
        
        return stats

# Middleware function for FastAPI
async def rate_limit_middleware(request: Request, call_next):
    """FastAPI middleware for rate limiting"""
    rate_limiter = RateLimiter()
    
    try:
        # Extract user info if available (from JWT token, session, etc.)
        user_id = None  # Extract from authentication
        
        # Determine endpoint type
        endpoint_type = 'default'
        if '/api/v1/risk/analyze' in request.url.path:
            endpoint_type = 'analysis_endpoint'
        
        # Check rate limit
        await rate_limiter.check_rate_limit(request, user_id, endpoint_type)
        
        # Process request
        response = await call_next(request)
        
        return response
        
    except HTTPException as e:
        return JSONResponse(
            status_code=e.status_code,
            content={"error": e.detail},
            headers=getattr(e, 'headers', {})
        )
    except Exception as e:
        logger.error(f"Rate limiting middleware error: {e}")
        return JSONResponse(
            status_code=500,
            content={"error": "Internal server error"}
        )

"""
📊 AIRMS Performance Monitoring System
Real-time performance tracking and optimization for Universal AI Risk API
"""

import time
import asyncio
import psutil
import logging
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from collections import defaultdict, deque
import json

from app.core.database import mongodb
from app.core.config import settings

logger = logging.getLogger(__name__)

@dataclass
class PerformanceMetrics:
    """Performance metrics data structure"""
    timestamp: datetime
    endpoint: str
    method: str
    response_time_ms: float
    status_code: int
    request_size_bytes: int
    response_size_bytes: int
    memory_usage_mb: float
    cpu_usage_percent: float
    cache_hit: bool
    ai_model_used: Optional[str] = None
    user_id: Optional[str] = None
    error_message: Optional[str] = None

@dataclass
class SystemMetrics:
    """System-wide performance metrics"""
    timestamp: datetime
    requests_per_minute: int
    avg_response_time_ms: float
    error_rate_percent: float
    memory_usage_percent: float
    cpu_usage_percent: float
    disk_usage_percent: float
    active_connections: int
    cache_hit_rate_percent: float
    throughput_requests_per_second: float

class PerformanceMonitor:
    """Real-time performance monitoring and analytics"""
    
    def __init__(self):
        self.metrics_buffer: deque = deque(maxlen=10000)  # Keep last 10k metrics
        self.system_metrics_buffer: deque = deque(maxlen=1000)  # Keep last 1k system metrics
        self.request_counts = defaultdict(int)
        self.response_times = defaultdict(list)
        self.error_counts = defaultdict(int)
        self.cache_stats = {"hits": 0, "misses": 0}
        self.start_time = time.time()
        
        # Performance thresholds
        self.thresholds = {
            "response_time_warning_ms": 1000,
            "response_time_critical_ms": 3000,
            "error_rate_warning_percent": 5.0,
            "error_rate_critical_percent": 10.0,
            "memory_warning_percent": 80.0,
            "memory_critical_percent": 90.0,
            "cpu_warning_percent": 70.0,
            "cpu_critical_percent": 85.0
        }
    
    async def record_request_metrics(self, 
                                   endpoint: str,
                                   method: str,
                                   response_time_ms: float,
                                   status_code: int,
                                   request_size: int = 0,
                                   response_size: int = 0,
                                   cache_hit: bool = False,
                                   ai_model_used: Optional[str] = None,
                                   user_id: Optional[str] = None,
                                   error_message: Optional[str] = None):
        """Record individual request performance metrics"""
        
        # Get system metrics
        memory_usage = psutil.virtual_memory().percent
        cpu_usage = psutil.cpu_percent()
        
        metrics = PerformanceMetrics(
            timestamp=datetime.utcnow(),
            endpoint=endpoint,
            method=method,
            response_time_ms=response_time_ms,
            status_code=status_code,
            request_size_bytes=request_size,
            response_size_bytes=response_size,
            memory_usage_mb=memory_usage,
            cpu_usage_percent=cpu_usage,
            cache_hit=cache_hit,
            ai_model_used=ai_model_used,
            user_id=user_id,
            error_message=error_message
        )
        
        # Add to buffer
        self.metrics_buffer.append(metrics)
        
        # Update counters
        self.request_counts[endpoint] += 1
        self.response_times[endpoint].append(response_time_ms)
        
        if status_code >= 400:
            self.error_counts[endpoint] += 1
        
        if cache_hit:
            self.cache_stats["hits"] += 1
        else:
            self.cache_stats["misses"] += 1
        
        # Check for performance alerts
        await self._check_performance_alerts(metrics)
        
        # Store in database (async)
        asyncio.create_task(self._store_metrics_async(metrics))
    
    async def get_real_time_metrics(self) -> Dict[str, Any]:
        """Get current real-time performance metrics"""
        
        now = datetime.utcnow()
        one_minute_ago = now - timedelta(minutes=1)
        
        # Filter recent metrics
        recent_metrics = [m for m in self.metrics_buffer if m.timestamp >= one_minute_ago]
        
        if not recent_metrics:
            return {
                "requests_per_minute": 0,
                "avg_response_time_ms": 0,
                "error_rate_percent": 0,
                "cache_hit_rate_percent": 0,
                "system_health": "unknown"
            }
        
        # Calculate metrics
        total_requests = len(recent_metrics)
        avg_response_time = sum(m.response_time_ms for m in recent_metrics) / total_requests
        error_count = sum(1 for m in recent_metrics if m.status_code >= 400)
        error_rate = (error_count / total_requests) * 100 if total_requests > 0 else 0
        
        # Cache hit rate
        total_cache_requests = self.cache_stats["hits"] + self.cache_stats["misses"]
        cache_hit_rate = (self.cache_stats["hits"] / total_cache_requests * 100) if total_cache_requests > 0 else 0
        
        # System health assessment
        system_health = self._assess_system_health(avg_response_time, error_rate)
        
        return {
            "requests_per_minute": total_requests,
            "avg_response_time_ms": round(avg_response_time, 2),
            "error_rate_percent": round(error_rate, 2),
            "cache_hit_rate_percent": round(cache_hit_rate, 2),
            "system_health": system_health,
            "active_connections": len(self.metrics_buffer),
            "uptime_seconds": int(time.time() - self.start_time),
            "memory_usage_percent": psutil.virtual_memory().percent,
            "cpu_usage_percent": psutil.cpu_percent(),
            "disk_usage_percent": psutil.disk_usage('/').percent
        }
    
    async def get_performance_statistics(self, hours: int = 24) -> Dict[str, Any]:
        """Get performance statistics for the specified time period"""
        
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        
        # Filter metrics by time period
        period_metrics = [m for m in self.metrics_buffer if m.timestamp >= cutoff_time]
        
        if not period_metrics:
            return {"message": "No data available for the specified period"}
        
        # Calculate statistics
        total_requests = len(period_metrics)
        successful_requests = sum(1 for m in period_metrics if m.status_code < 400)
        failed_requests = total_requests - successful_requests
        
        response_times = [m.response_time_ms for m in period_metrics]
        avg_response_time = sum(response_times) / len(response_times)
        min_response_time = min(response_times)
        max_response_time = max(response_times)
        
        # Percentiles
        sorted_times = sorted(response_times)
        p50_response_time = sorted_times[int(len(sorted_times) * 0.5)]
        p95_response_time = sorted_times[int(len(sorted_times) * 0.95)]
        p99_response_time = sorted_times[int(len(sorted_times) * 0.99)]
        
        # Endpoint statistics
        endpoint_stats = defaultdict(lambda: {"count": 0, "avg_time": 0, "errors": 0})
        for metric in period_metrics:
            endpoint_stats[metric.endpoint]["count"] += 1
            endpoint_stats[metric.endpoint]["avg_time"] += metric.response_time_ms
            if metric.status_code >= 400:
                endpoint_stats[metric.endpoint]["errors"] += 1
        
        # Calculate averages
        for endpoint, stats in endpoint_stats.items():
            stats["avg_time"] = stats["avg_time"] / stats["count"]
            stats["error_rate"] = (stats["errors"] / stats["count"]) * 100
        
        return {
            "period_hours": hours,
            "total_requests": total_requests,
            "successful_requests": successful_requests,
            "failed_requests": failed_requests,
            "success_rate_percent": (successful_requests / total_requests) * 100,
            "response_time_stats": {
                "avg_ms": round(avg_response_time, 2),
                "min_ms": round(min_response_time, 2),
                "max_ms": round(max_response_time, 2),
                "p50_ms": round(p50_response_time, 2),
                "p95_ms": round(p95_response_time, 2),
                "p99_ms": round(p99_response_time, 2)
            },
            "endpoint_statistics": dict(endpoint_stats),
            "cache_statistics": {
                "hit_rate_percent": round(
                    (self.cache_stats["hits"] / (self.cache_stats["hits"] + self.cache_stats["misses"])) * 100, 2
                ) if (self.cache_stats["hits"] + self.cache_stats["misses"]) > 0 else 0,
                "total_hits": self.cache_stats["hits"],
                "total_misses": self.cache_stats["misses"]
            }
        }
    
    async def get_performance_timeline(self, hours: int = 24, interval_minutes: int = 60) -> List[Dict[str, Any]]:
        """Get performance metrics timeline with specified intervals"""
        
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        current_time = datetime.utcnow()
        
        timeline = []
        
        # Create time buckets
        bucket_start = cutoff_time
        while bucket_start < current_time:
            bucket_end = bucket_start + timedelta(minutes=interval_minutes)
            
            # Filter metrics for this time bucket
            bucket_metrics = [
                m for m in self.metrics_buffer 
                if bucket_start <= m.timestamp < bucket_end
            ]
            
            if bucket_metrics:
                total_requests = len(bucket_metrics)
                avg_response_time = sum(m.response_time_ms for m in bucket_metrics) / total_requests
                error_count = sum(1 for m in bucket_metrics if m.status_code >= 400)
                error_rate = (error_count / total_requests) * 100
                
                timeline.append({
                    "timestamp": bucket_start.isoformat(),
                    "requests": total_requests,
                    "avg_response_time_ms": round(avg_response_time, 2),
                    "error_rate_percent": round(error_rate, 2),
                    "errors": error_count
                })
            else:
                timeline.append({
                    "timestamp": bucket_start.isoformat(),
                    "requests": 0,
                    "avg_response_time_ms": 0,
                    "error_rate_percent": 0,
                    "errors": 0
                })
            
            bucket_start = bucket_end
        
        return timeline
    
    def _assess_system_health(self, avg_response_time: float, error_rate: float) -> str:
        """Assess overall system health based on metrics"""
        
        if (avg_response_time > self.thresholds["response_time_critical_ms"] or 
            error_rate > self.thresholds["error_rate_critical_percent"]):
            return "critical"
        elif (avg_response_time > self.thresholds["response_time_warning_ms"] or 
              error_rate > self.thresholds["error_rate_warning_percent"]):
            return "warning"
        else:
            return "healthy"
    
    async def _check_performance_alerts(self, metrics: PerformanceMetrics):
        """Check for performance alerts and log warnings"""
        
        alerts = []
        
        # Response time alerts
        if metrics.response_time_ms > self.thresholds["response_time_critical_ms"]:
            alerts.append(f"CRITICAL: Response time {metrics.response_time_ms}ms exceeds critical threshold")
        elif metrics.response_time_ms > self.thresholds["response_time_warning_ms"]:
            alerts.append(f"WARNING: Response time {metrics.response_time_ms}ms exceeds warning threshold")
        
        # Memory alerts
        if metrics.memory_usage_mb > self.thresholds["memory_critical_percent"]:
            alerts.append(f"CRITICAL: Memory usage {metrics.memory_usage_mb}% exceeds critical threshold")
        elif metrics.memory_usage_mb > self.thresholds["memory_warning_percent"]:
            alerts.append(f"WARNING: Memory usage {metrics.memory_usage_mb}% exceeds warning threshold")
        
        # CPU alerts
        if metrics.cpu_usage_percent > self.thresholds["cpu_critical_percent"]:
            alerts.append(f"CRITICAL: CPU usage {metrics.cpu_usage_percent}% exceeds critical threshold")
        elif metrics.cpu_usage_percent > self.thresholds["cpu_warning_percent"]:
            alerts.append(f"WARNING: CPU usage {metrics.cpu_usage_percent}% exceeds warning threshold")
        
        # Log alerts
        for alert in alerts:
            if "CRITICAL" in alert:
                logger.critical(alert)
            else:
                logger.warning(alert)
    
    async def _store_metrics_async(self, metrics: PerformanceMetrics):
        """Store metrics in database asynchronously"""
        try:
            if mongodb.database:
                await mongodb.database.performance_metrics.insert_one(asdict(metrics))
        except Exception as e:
            logger.error(f"Failed to store performance metrics: {e}")
    
    async def cleanup_old_metrics(self, days_to_keep: int = 30):
        """Clean up old performance metrics from database"""
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days_to_keep)
            
            if mongodb.database:
                result = await mongodb.database.performance_metrics.delete_many({
                    "timestamp": {"$lt": cutoff_date}
                })
                logger.info(f"Cleaned up {result.deleted_count} old performance metrics")
        except Exception as e:
            logger.error(f"Failed to cleanup old metrics: {e}")

# Global performance monitor instance
performance_monitor = PerformanceMonitor()

# Middleware for automatic performance tracking
async def performance_tracking_middleware(request, call_next):
    """FastAPI middleware for automatic performance tracking"""
    
    start_time = time.time()
    
    # Get request size
    request_size = 0
    if hasattr(request, 'body'):
        try:
            body = await request.body()
            request_size = len(body)
        except:
            pass
    
    # Process request
    response = await call_next(request)
    
    # Calculate metrics
    end_time = time.time()
    response_time_ms = (end_time - start_time) * 1000
    
    # Get response size
    response_size = 0
    if hasattr(response, 'body'):
        try:
            response_size = len(response.body)
        except:
            pass
    
    # Extract user info if available
    user_id = None
    if hasattr(request.state, 'user'):
        user_id = getattr(request.state.user, 'id', None)
    
    # Record metrics
    await performance_monitor.record_request_metrics(
        endpoint=str(request.url.path),
        method=request.method,
        response_time_ms=response_time_ms,
        status_code=response.status_code,
        request_size=request_size,
        response_size=response_size,
        user_id=user_id
    )
    
    return response

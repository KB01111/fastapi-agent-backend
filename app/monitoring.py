"""Monitoring and observability with Prometheus metrics and structured logging."""

import time
from typing import Dict, Any, Optional
from functools import wraps
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
import structlog
from fastapi import Response

from app.config import settings

# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()

# Prometheus metrics
http_requests_total = Counter(
    'http_requests_total',
    'Total number of HTTP requests',
    ['method', 'endpoint', 'status_code']
)

http_request_duration_seconds = Histogram(
    'http_request_duration_seconds',
    'HTTP request duration in seconds',
    ['method', 'endpoint']
)

agent_executions_total = Counter(
    'agent_executions_total',
    'Total number of agent executions',
    ['agent_type', 'status']
)

agent_execution_duration_seconds = Histogram(
    'agent_execution_duration_seconds',
    'Agent execution duration in seconds',
    ['agent_type']
)

agent_token_usage_total = Counter(
    'agent_token_usage_total',
    'Total token usage by agents',
    ['agent_type', 'token_type']
)

active_sessions = Gauge(
    'active_sessions_total',
    'Number of active agent sessions'
)

database_connections = Gauge(
    'database_connections_total',
    'Number of active database connections'
)

system_memory_usage = Gauge(
    'system_memory_usage_bytes',
    'System memory usage in bytes'
)


class MetricsCollector:
    """Collector for application metrics."""
    
    def __init__(self):
        self.logger = logger.bind(component="metrics")
    
    def record_http_request(self, method: str, endpoint: str, status_code: int, duration: float):
        """Record HTTP request metrics."""
        http_requests_total.labels(
            method=method,
            endpoint=endpoint,
            status_code=str(status_code)
        ).inc()
        
        http_request_duration_seconds.labels(
            method=method,
            endpoint=endpoint
        ).observe(duration)
        
        self.logger.debug("HTTP request recorded", 
                         method=method, endpoint=endpoint, 
                         status_code=status_code, duration=duration)
    
    def record_agent_execution(
        self, 
        agent_type: str, 
        status: str, 
        duration: Optional[float] = None,
        token_usage: Optional[Dict[str, int]] = None
    ):
        """Record agent execution metrics."""
        agent_executions_total.labels(
            agent_type=agent_type,
            status=status
        ).inc()
        
        if duration is not None:
            agent_execution_duration_seconds.labels(
                agent_type=agent_type
            ).observe(duration)
        
        if token_usage:
            for token_type, count in token_usage.items():
                agent_token_usage_total.labels(
                    agent_type=agent_type,
                    token_type=token_type
                ).inc(count)
        
        self.logger.info("Agent execution recorded", 
                        agent_type=agent_type, status=status, 
                        duration=duration, token_usage=token_usage)
    
    def update_active_sessions(self, count: int):
        """Update active sessions gauge."""
        active_sessions.set(count)
        self.logger.debug("Active sessions updated", count=count)
    
    def update_database_connections(self, count: int):
        """Update database connections gauge."""
        database_connections.set(count)
        self.logger.debug("Database connections updated", count=count)
    
    def update_memory_usage(self, bytes_used: int):
        """Update memory usage gauge."""
        system_memory_usage.set(bytes_used)
        self.logger.debug("Memory usage updated", bytes_used=bytes_used)


def monitor_execution_time(metric_name: Optional[str] = None):
    """
    Decorator to monitor function execution time.
    
    Args:
        metric_name: Optional custom metric name
    """
    def decorator(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            start_time = time.time()
            func_name = metric_name or f"{func.__module__}.{func.__name__}"
            
            try:
                result = await func(*args, **kwargs)
                duration = time.time() - start_time
                
                logger.info("Function executed successfully", 
                          function=func_name, duration=duration)
                
                return result
                
            except Exception as e:
                duration = time.time() - start_time
                
                logger.error("Function execution failed", 
                           function=func_name, duration=duration, error=str(e))
                
                raise
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            start_time = time.time()
            func_name = metric_name or f"{func.__module__}.{func.__name__}"
            
            try:
                result = func(*args, **kwargs)
                duration = time.time() - start_time
                
                logger.info("Function executed successfully", 
                          function=func_name, duration=duration)
                
                return result
                
            except Exception as e:
                duration = time.time() - start_time
                
                logger.error("Function execution failed", 
                           function=func_name, duration=duration, error=str(e))
                
                raise
        
        # Return the appropriate wrapper based on whether the function is async
        import asyncio
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator


from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response as StarletteResponse


class RequestMetricsMiddleware(BaseHTTPMiddleware):
    """Middleware to collect HTTP request metrics."""
    
    def __init__(self, app):
        super().__init__(app)
        self.metrics = MetricsCollector()
    
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        method = request.method
        path = request.url.path
        
        # Extract endpoint pattern (remove path parameters)
        endpoint = self._extract_endpoint_pattern(path)
        
        try:
            response = await call_next(request)
            duration = time.time() - start_time
            
            # Record metrics
            self.metrics.record_http_request(
                method=method,
                endpoint=endpoint,
                status_code=response.status_code,
                duration=duration
            )
            
            return response
            
        except Exception as e:
            duration = time.time() - start_time
            
            # Record error metrics
            self.metrics.record_http_request(
                method=method,
                endpoint=endpoint,
                status_code=500,
                duration=duration
            )
            
            raise
    
    def _extract_endpoint_pattern(self, path: str) -> str:
        """Extract endpoint pattern from path."""
        # Simple pattern extraction - in production, you might want
        # to use the actual FastAPI route pattern
        parts = path.split('/')
        if len(parts) > 1 and parts[1] == 'v1':
            return f"/{parts[1]}/{parts[2] if len(parts) > 2 else ''}"
        return path


async def get_metrics() -> Response:
    """
    Get Prometheus metrics endpoint.
    
    Returns:
        Response: Prometheus metrics in text format
    """
    metrics_data = generate_latest()
    return Response(
        content=metrics_data,
        media_type=CONTENT_TYPE_LATEST
    )


def log_request_info(request_id: str, user_id: Optional[str] = None, **kwargs):
    """
    Log request information with structured data.
    
    Args:
        request_id: Unique request identifier
        user_id: Optional user identifier
        **kwargs: Additional structured data
    """
    logger.info("Request processed", 
               request_id=request_id, 
               user_id=user_id, 
               **kwargs)


def log_error(error: Exception, context: Optional[Dict[str, Any]] = None, **kwargs):
    """
    Log error with structured context.
    
    Args:
        error: Exception that occurred
        context: Optional context dictionary
        **kwargs: Additional structured data
    """
    logger.error("Error occurred", 
                error_type=type(error).__name__,
                error_message=str(error),
                context=context or {},
                **kwargs)


def log_performance_metrics(
    operation: str,
    duration_ms: int,
    success: bool = True,
    **kwargs
):
    """
    Log performance metrics for operations.
    
    Args:
        operation: Operation name
        duration_ms: Operation duration in milliseconds
        success: Whether operation was successful
        **kwargs: Additional metrics
    """
    logger.info("Performance metrics", 
               operation=operation,
               duration_ms=duration_ms,
               success=success,
               **kwargs)


# Global metrics collector instance
metrics_collector = MetricsCollector() 
import os
import time
import re
import logging
from typing import Dict, List
from fastapi import Request, Response, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger("rate_limiter")

# In-memory store for rate limiting: IP -> list of timestamps
ip_request_history: Dict[str, List[float]] = {}

class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    IP-based sliding window rate-limiter middleware.
    Caps public requests to 60 requests per minute per IP.
    """
    async def dispatch(self, request: Request, call_next) -> Response:
        # Exclude docs, static pages, and health checks
        path = request.url.path
        if os.getenv("TESTING") == "true" or path.startswith("/health") or path.startswith("/ready") or path.startswith("/metrics") or "/docs" in path or "/openapi.json" in path:
            return await call_next(request)
            
        client_ip = request.client.host if request.client else "unknown"
        now = time.time()
        
        if client_ip not in ip_request_history:
            ip_request_history[client_ip] = []
            
        # Keep only timestamps in the last 60 seconds
        ip_request_history[client_ip] = [t for t in ip_request_history[client_ip] if now - t < 60]
        
        # Max 60 requests per minute
        if len(ip_request_history[client_ip]) >= 60:
            logger.warning(f"Rate limit exceeded for IP: {client_ip} on endpoint {path}")
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={"detail": "Too many requests. Limit is 60 requests per minute."}
            )
            
        ip_request_history[client_ip].append(now)
        return await call_next(request)

def sanitize_string(val: str) -> str:
    """
    Strips dangerous HTML/script tags from inputs to prevent prompt injection and XSS.
    """
    if not isinstance(val, str):
        return val
    # Remove HTML tags
    clean = re.compile('<.*?>')
    return re.sub(clean, '', val)

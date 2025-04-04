from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
import time
from typing import Dict, Tuple
import logging
from .config import settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, limit: int = settings.RATE_LIMIT_PER_MINUTE):
        super().__init__(app)
        self.limit = limit
        self.requests: Dict[str, Tuple[int, float]] = {}

    async def dispatch(self, request: Request, call_next):
        client_ip = request.client.host
        current_time = time.time()
        
        # Clean up old entries
        self.requests = {
            ip: (count, timestamp)
            for ip, (count, timestamp) in self.requests.items()
            if current_time - timestamp < 60
        }
        
        # Check rate limit
        if client_ip in self.requests:
            count, timestamp = self.requests[client_ip]
            if count >= self.limit:
                raise HTTPException(
                    status_code=429,
                    detail="Too many requests. Please try again later."
                )
            self.requests[client_ip] = (count + 1, timestamp)
        else:
            self.requests[client_ip] = (1, current_time)
        
        # Log request
        logger.info(f"Request: {request.method} {request.url.path} from {client_ip}")
        
        response = await call_next(request)
        return response

class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        response = await call_next(request)
        process_time = time.time() - start_time
        
        logger.info(
            f"Request completed: {request.method} {request.url.path} "
            f"Status: {response.status_code} "
            f"Time: {process_time:.2f}s"
        )
        
        return response 
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import time
from .gateway.config import settings
from .gateway.middleware import RateLimitMiddleware, LoggingMiddleware
from src.services.auth.router import router as auth_router
from src.services.products.router import router as products_router
from src.services.orders.router import router as orders_router
from src.metrics import (
    metrics_endpoint,
    record_request_metrics,
)

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="A microservices-based e-commerce platform with API Gateway",
    version=settings.VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
)

# Add middleware
app.add_middleware(RateLimitMiddleware)
app.add_middleware(LoggingMiddleware)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Import and include routers from different services
from src.services.products.router import router as products_router
from src.services.orders.router import router as orders_router
from src.services.auth.router import router as auth_router

# Include service routers with proper prefixes
app.include_router(
    auth_router,
    prefix=f"{settings.API_V1_STR}/auth",
    tags=["auth"]
)
app.include_router(
    products_router,
    prefix=f"{settings.API_V1_STR}/products",
    tags=["products"]
)
app.include_router(
    orders_router,
    prefix=f"{settings.API_V1_STR}/orders",
    tags=["orders"]
)

@app.middleware("http")
async def metrics_middleware(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    duration = time.time() - start_time
    
    # Record metrics
    record_request_metrics(
        method=request.method,
        endpoint=request.url.path,
        status_code=response.status_code,
        duration=duration
    )
    
    return response

@app.get("/")
async def root():
    return {
        "message": "Welcome to the E-Commerce API Gateway",
        "version": settings.VERSION,
        "health": "/health",
        "metrics": "/metrics"
    }

@app.get("/metrics")
async def prometheus_metrics():
    """Prometheus metrics endpoint"""
    return await metrics_endpoint()

@app.get("/health", tags=["health"])
async def health_check():
    """Simple health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": settings.VERSION
    } 
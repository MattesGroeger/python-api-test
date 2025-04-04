from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .gateway.config import settings
from .gateway.middleware import RateLimitMiddleware, LoggingMiddleware

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="A microservices-based e-commerce platform with API Gateway",
    version=settings.VERSION
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

# Include service routers with proper prefixes
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

@app.get("/")
async def root():
    return {
        "message": "Welcome to the E-Commerce API Gateway",
        "version": settings.VERSION,
        "docs_url": "/docs",
        "redoc_url": "/redoc"
    } 
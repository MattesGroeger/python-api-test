from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "E-Commerce API Gateway"
    VERSION: str = "1.0.0"
    
    # CORS settings
    BACKEND_CORS_ORIGINS: List[str] = ["*"]
    
    # Rate limiting
    RATE_LIMIT_PER_MINUTE: int = 60
    
    # Service URLs (in a real setup, these would be service discovery URLs)
    PRODUCT_SERVICE_URL: str = "http://localhost:8001"
    ORDER_SERVICE_URL: str = "http://localhost:8002"
    
    class Config:
        case_sensitive = True

settings = Settings() 
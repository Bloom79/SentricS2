"""
Configuration management for Kronos EAM
Multi-tenant aware configuration with environment variable support
"""

from typing import List, Optional, Dict, Any
from pydantic_settings import BaseSettings
from pydantic import field_validator, model_validator, RedisDsn
import secrets
import logging
import os
from functools import lru_cache

logger = logging.getLogger(__name__)


class Settings(BaseSettings):
    # Application
    APP_NAME: str = "Kronos EAM"
    APP_VERSION: str = "2.0.0"
    API_V1_STR: str = "/api/v1"
    DEBUG: bool = False
    ENVIRONMENT: str = "development"

    # Security
    SECRET_KEY: str = secrets.token_urlsafe(32)

    @model_validator(mode="before")
    @classmethod
    def set_secret_key_from_jwt_env(cls, data: Dict[str, Any]) -> Dict[str, Any]:
        """Map JWT_SECRET_KEY env var to SECRET_KEY for Cloud Run compatibility"""
        if isinstance(data, dict):
            # If JWT_SECRET_KEY is in env but not in data, use it
            jwt_secret = os.getenv("JWT_SECRET_KEY")
            if jwt_secret and "SECRET_KEY" not in data:
                data["SECRET_KEY"] = jwt_secret
        return data

    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    ALGORITHM: str = "HS256"
    BCRYPT_ROUNDS: int = 12

    # Multi-tenant Configuration
    ENABLE_MULTI_TENANT: bool = True
    DEFAULT_TENANT_ID: str = "demo"
    MAX_USERS_PER_TENANT: int = 100
    TENANT_ISOLATION_MODE: str = "strict"  # strict, shared, hybrid

    # Database
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/kronos_eam"
    REDIS_URL: RedisDsn = "redis://localhost:6379/0"
    DB_POOL_SIZE: int = 20
    DB_MAX_OVERFLOW: int = 0
    DB_POOL_PRE_PING: bool = True

    # Service Toggles
    DISABLE_REDIS: bool = False
    DISABLE_QDRANT: bool = False
    DISABLE_RATE_LIMIT: bool = False

    # CORS
    BACKEND_CORS_ORIGINS: List[str] = []
    CORS_ORIGINS: str = ""  # Comma-separated list for easy GCP Secret Manager
    ALLOWED_HOSTS: str = "*"  # Comma-separated list

    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: str | List[str] | None) -> List[str]:
        if v is None or v == "":
            return []
        if isinstance(v, list):
            return v
        if isinstance(v, str):
            # Handle JSON array format
            if v.startswith("[") and v.endswith("]"):
                try:
                    import json

                    return json.loads(v)
                except (json.JSONDecodeError, ValueError):
                    pass
            # Handle comma-separated string
            if "," in v:
                return [i.strip() for i in v.split(",") if i.strip()]
            # Single value
            return [v.strip()] if v.strip() else []
        return []

    # GCP Specific
    GCP_PROJECT_ID: Optional[str] = None
    GCP_REGION: str = "us-central1"
    GCP_SERVICE_NAME: Optional[str] = None
    FRONTEND_URL: Optional[str] = None

    # Rate Limiting
    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_PER_MINUTE: int = 200

    # API Configuration
    API_V1_PREFIX: str = "/api/v1"
    PROJECT_NAME: str = "Kronos EAM"

    # File Upload
    MAX_UPLOAD_SIZE: int = 10 * 1024 * 1024  # 10MB
    UPLOAD_DIR: str = "./uploads"

    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"  # json or text

    # Geographic
    DEFAULT_SRID: int = 4326  # WGS84

    class Config:
        case_sensitive = True
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()


settings = get_settings()

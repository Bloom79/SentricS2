"""
Configuration management for Kronos EAM
Multi-tenant aware configuration with environment variable support
"""

from typing import List, Optional, Dict, Any
from pydantic_settings import BaseSettings
from pydantic import AnyHttpUrl, field_validator, model_validator, PostgresDsn, RedisDsn, AnyUrl
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
    # SECRET_KEY is required and must be set via environment variable
    # In production, this MUST be a strong, randomly generated secret
    SECRET_KEY: str = None

    @model_validator(mode='before')
    @classmethod
    def set_secret_key_from_jwt_env(cls, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Map JWT_SECRET_KEY env var to SECRET_KEY for Cloud Run compatibility.
        Requires SECRET_KEY or JWT_SECRET_KEY to be set.
        In development, generates a random key if not provided.
        """
        if isinstance(data, dict):
            # If JWT_SECRET_KEY is in env but not in data, use it
            jwt_secret = os.getenv("JWT_SECRET_KEY")
            secret_key = data.get("SECRET_KEY") or os.getenv("SECRET_KEY")

            if jwt_secret:
                data["SECRET_KEY"] = jwt_secret
            elif secret_key:
                data["SECRET_KEY"] = secret_key
            elif data.get("ENVIRONMENT", "development") == "development":
                # Only in development: generate a random key with warning
                generated_key = secrets.token_urlsafe(32)
                data["SECRET_KEY"] = generated_key
                logger.warning(
                    "SECRET_KEY not set! Generated random key for development. "
                    "WARNING: This will invalidate tokens on restart. "
                    "Set SECRET_KEY or JWT_SECRET_KEY environment variable."
                )
            else:
                # In production, SECRET_KEY is mandatory
                raise ValueError(
                    "SECRET_KEY or JWT_SECRET_KEY must be set in production! "
                    "Generate a secure key with: python -c 'import secrets; print(secrets.token_urlsafe(32))'"
                )
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

    # Security Options
    STRICT_CSP: bool = False  # Enable strict Content Security Policy (no unsafe-inline/unsafe-eval)
    PASSWORD_MIN_LENGTH: int = 8
    PASSWORD_REQUIRE_UPPERCASE: bool = True
    PASSWORD_REQUIRE_LOWERCASE: bool = True
    PASSWORD_REQUIRE_DIGITS: bool = True
    PASSWORD_REQUIRE_SPECIAL: bool = True
    
    # CORS
    BACKEND_CORS_ORIGINS: List[str] = []
    
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
                except:
                    pass
            # Handle comma-separated string
            if "," in v:
                return [i.strip() for i in v.split(",") if i.strip()]
            # Single value
            return [v.strip()] if v.strip() else []
        return []
    
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


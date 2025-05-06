import os
from functools import lru_cache
from typing import Literal

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings with environment variable loading"""

    # App settings
    APP_NAME: str = "Merchant Lead Form"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = False

    # Database settings
    DATABASE_URL: str = "postgresql://postgres:password@postgres:5432/merchant_leads"

    # Redis settings - for session management
    REDIS_URL: str = "redis://redis:6379/0"
    SESSION_TTL: int = 86400  # 24 hours in seconds

    # Enrichment API settings
    ENRICHMENT_API_URL: str = "https://api.example.com/tib-verification"
    ENRICHMENT_API_TIMEOUT: int = 5  # seconds
    ENRICHMENT_SIMULATE_DELAY: tuple = (
        0.5, 2.0)  # min and max delay in seconds
    ENRICHMENT_SIMULATE_FAILURE_RATE: float = 0.1  # 10% chance of failure

    # Logging settings
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: Literal["text", "json"] = "json"
    LOG_TO_CONSOLE: bool = True
    LOG_TO_FILE: bool = True
    LOG_ROTATION_TYPE: Literal["size", "time"] = "time"
    LOG_ROTATION_SIZE: int = 10 * 1024 * 1024  # 10 MB
    LOG_ROTATION_WHEN: str = "midnight"  # Can be S, M, H, D, W0-W6, midnight
    LOG_ROTATION_INTERVAL: int = 1  # Number of units between rotations
    LOG_ROTATION_BACKUPS: int = 30  # Number of backups to keep
    LOG_SQL: bool = False  # Whether to log SQL queries

    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """
    Get singleton instance of settings

    Using lru_cache creates a singleton to prevent reloading settings
    for each request
    """
    environment = os.getenv("ENVIRONMENT", "dev")
    return Settings(
        _env_file=f".env.{environment}" if environment != "prod" else ".env"
    )

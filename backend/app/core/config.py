from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )

    # API Keys
    anthropic_api_key: str
    clearbit_api_key: Optional[str] = None
    hunter_api_key: Optional[str] = None

    # Database
    database_url: str
    redis_url: str

    # Application Settings
    scraping_delay: int = 2
    cache_ttl: int = 604800  # 7 days
    max_companies_per_search: int = 50

    # Environment
    environment: str = "development"
    debug: bool = True

    # API Settings
    api_v1_prefix: str = "/api/v1"
    project_name: str = "Sales Intelligence Agent"

    # CORS
    cors_origins: list[str] = ["http://localhost:3000", "http://localhost:5173", "http://localhost:5177", "http://localhost:5178"]


settings = Settings()

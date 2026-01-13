"""
Configuration management for the API.
"""

from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Database settings
    db_host: str
    db_port: int = 5432
    db_name: str
    db_user: str
    db_password: str
    
    # API settings
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_reload: bool = True
    
    # Pagination settings
    default_page_size: int = 50
    max_page_size: int = 100
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False
    )
    
    @property
    def database_url(self) -> str:
        """Construct database URL from settings."""
        return f"postgresql+pg8000://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}"


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()

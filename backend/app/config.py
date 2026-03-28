import os
from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import model_validator


class Settings(BaseSettings):
    SECRET_KEY: str = os.environ.get("SECRET_KEY", "your-secret-key-change-in-production")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7
    
    # Backward-compat: allow explicit URL; otherwise build from type/envs
    DATABASE_URL: Optional[str] = None
    DATABASE_TYPE: str = "sqlite"
    # Postgres config (used when DATABASE_TYPE=postgresql)
    POSTGRES_USER: Optional[str] = None
    POSTGRES_PASSWORD: Optional[str] = None
    POSTGRES_HOST: Optional[str] = None
    POSTGRES_PORT: Optional[str] = None
    POSTGRES_DB: Optional[str] = None

    model_config = {"env_file": ".env"}

    # Build DATABASE_URL if not provided, based on DATABASE_TYPE and related env vars
    @model_validator(mode='after')
    def build_database_url(self) -> 'Settings':
        # If explicit URL provided, keep it (backward compatibility)
        if self.DATABASE_URL and self.DATABASE_URL.strip():
            return self
        
        db_type = (self.DATABASE_TYPE or "sqlite").lower()
        if db_type == "sqlite":
            self.DATABASE_URL = "sqlite:///./data/home_assets.db"
        elif db_type == "postgresql":
            user = self.POSTGRES_USER or "postgres"
            password = self.POSTGRES_PASSWORD or "postgres"
            host = self.POSTGRES_HOST or "localhost"
            port = self.POSTGRES_PORT or "5432"
            dbname = self.POSTGRES_DB or "home_assets"
            self.DATABASE_URL = f"postgresql://{user}:{password}@{host}:{port}/{dbname}"
        else:
            self.DATABASE_URL = "sqlite:///./data/home_assets.db"
        
        return self


settings = Settings()

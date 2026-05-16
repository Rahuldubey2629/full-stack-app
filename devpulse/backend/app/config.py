# /devpulse/backend/app/config.py
from __future__ import annotations

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", case_sensitive=False)

    app_env: str = Field(default="local", validation_alias="APP_ENV")

    database_url: str = Field(validation_alias="DATABASE_URL")

    jwt_secret: str = Field(validation_alias="JWT_SECRET")
    jwt_algorithm: str = Field(default="HS256", validation_alias="JWT_ALGORITHM")
    jwt_access_minutes: int = Field(default=30, validation_alias="JWT_ACCESS_MINUTES")
    jwt_refresh_minutes: int = Field(default=1440, validation_alias="JWT_REFRESH_MINUTES")

    gemini_api_key: str = Field(validation_alias="GEMINI_API_KEY")

    redis_url: str = Field(default="redis://redis:6379/0", validation_alias="REDIS_URL")

    cors_origins_raw: str = Field(default="*", validation_alias="CORS_ORIGINS")

    @property
    def cors_origins(self) -> list[str]:
        value = (self.cors_origins_raw or "*").strip()
        if value in ("", "*"):
            return ["*"]
        return [v.strip() for v in value.split(",") if v.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()

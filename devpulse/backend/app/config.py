# /devpulse/backend/app/config.py
from __future__ import annotations

from functools import lru_cache

from pydantic import AliasChoices, Field
from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", case_sensitive=False)

    app_env: str = Field(default="local", validation_alias="APP_ENV")

    database_url: str = Field(validation_alias="DATABASE_URL")

    jwt_secret: str = Field(validation_alias="JWT_SECRET")
    jwt_algorithm: str = Field(default="HS256", validation_alias="JWT_ALGORITHM")
    jwt_access_minutes: int = Field(default=30, validation_alias="JWT_ACCESS_MINUTES")
    jwt_refresh_minutes: int = Field(default=1440, validation_alias="JWT_REFRESH_MINUTES")

    llm_provider: str = Field(default="gemini", validation_alias="LLM_PROVIDER")

    gemini_api_key: str = Field(
        default="",
        validation_alias=AliasChoices("GEMINI_API_KEY", "GOOGLE_API_KEY"),
    )
    gemini_model: str = Field(default="gemini-1.5-flash", validation_alias="GEMINI_MODEL")

    groq_api_key: str = Field(default="", validation_alias="GROQ_API_KEY")
    groq_model: str = Field(default="llama-3.1-8b-instant", validation_alias="GROQ_MODEL")
    groq_base_url: str = Field(
        default="https://api.groq.com/openai/v1/chat/completions",
        validation_alias="GROQ_BASE_URL",
    )

    # Azure AI Foundry / Azure AI Inference (services.ai.azure.com)
    azure_ai_endpoint: str = Field(default="", validation_alias="AZURE_AI_ENDPOINT")
    azure_ai_api_key: str = Field(default="", validation_alias="AZURE_AI_API_KEY")
    azure_ai_model: str = Field(default="gpt-4o-mini", validation_alias="AZURE_AI_MODEL")
    azure_ai_api_version: str = Field(default="2024-05-01-preview", validation_alias="AZURE_AI_API_VERSION")
    azure_ai_chat_path: str = Field(default="/models/chat/completions", validation_alias="AZURE_AI_CHAT_PATH")

    # Azure OpenAI (deployment-based)
    azure_openai_endpoint: str = Field(default="", validation_alias="AZURE_OPENAI_ENDPOINT")
    azure_openai_api_key: str = Field(default="", validation_alias="AZURE_OPENAI_API_KEY")
    azure_openai_deployment: str = Field(default="", validation_alias="AZURE_OPENAI_DEPLOYMENT")
    azure_openai_api_version: str = Field(default="2024-05-01-preview", validation_alias="AZURE_OPENAI_API_VERSION")

    redis_url: str = Field(default="redis://redis:6379/0", validation_alias="REDIS_URL")

    cors_origins_raw: str = Field(default="*", validation_alias="CORS_ORIGINS")

    @property
    def cors_origins(self) -> list[str]:
        value = (self.cors_origins_raw or "*").strip()
        if value in ("", "*"):
            return ["*"]
        return [v.strip() for v in value.split(",") if v.strip()]

    @model_validator(mode="after")
    def _validate_llm(self) -> "Settings":
        provider = (self.llm_provider or "gemini").strip().lower()
        aliases = {
            "azure": "azure_ai",
            "azureai": "azure_ai",
            "azure-openai": "azure_openai",
            "foundry": "azure_ai",
            "ai_foundry": "azure_ai",
            "ai-foundry": "azure_ai",
        }
        provider = aliases.get(provider, provider)
        if provider not in {"gemini", "groq", "azure_ai", "azure_openai"}:
            raise ValueError("LLM_PROVIDER must be 'gemini', 'groq', 'azure_ai', or 'azure_openai'")
        self.llm_provider = provider
        return self


@lru_cache
def get_settings() -> Settings:
    return Settings()

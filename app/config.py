from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "RAG Agent"
    database_host: str = "localhost"
    database_port: int = 5433
    database_user: str = "postgres"
    database_password: str = "postgres"
    database_name: str = "rag_agent"
    openai_api_key: str | None = None


@lru_cache
def get_settings() -> Settings:
    return Settings()

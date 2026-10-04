from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    app_name: str = "CaixaLivre API"
    environment: str = "development"

    database_url: str = "postgresql+psycopg://caixalivre:caixalivre@localhost:5432/caixalivre"
    secret_key: str = "development-only-change-me"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60

    cors_origins: str = "http://localhost:3000,http://localhost:5173"

    openai_api_key: str | None = None
    openai_model: str = "gpt-6-astra"
    openai_timeout_seconds: float = 20.0

    @property
    def allowed_origins(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()

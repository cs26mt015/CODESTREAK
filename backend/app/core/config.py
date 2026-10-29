from functools import lru_cache

from pydantic import Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "CodeStreak API"
    app_env: str = "development"
    database_url: str = "mysql+pymysql://asdl:asdl@localhost:3306/asdl"
    jwt_secret_key: str = "local-development-signing-key-change-before-deploy"
    access_token_expire_minutes: int = Field(default=60, ge=1, le=10080)
    hint_provider: str = "disabled"

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore", case_sensitive=False
    )

    @model_validator(mode="after")
    def require_production_secret(self):
        if self.app_env.lower() in {"prod", "production"} and self.jwt_secret_key in {
            "local-development-signing-key-change-before-deploy",
            "replace-this-with-a-random-secret-at-least-32-characters",
        }:
            raise ValueError("Set JWT_SECRET_KEY to a private random value in production")
        return self


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()

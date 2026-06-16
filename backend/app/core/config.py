from functools import lru_cache
from typing import Annotated

from pydantic import AnyHttpUrl, Field, field_validator
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file="../.env", env_file_encoding="utf-8", extra="ignore")

    project_name: str = "SteamNStats"
    environment: str = "development"
    backend_cors_origins: Annotated[list[str], NoDecode] = Field(
        default_factory=lambda: ["http://localhost:5173"],
    )
    frontend_url: AnyHttpUrl = "http://localhost:5173"  # type: ignore[assignment]
    api_base_url: AnyHttpUrl = "http://localhost:8000"  # type: ignore[assignment]

    database_url: str = "postgresql+psycopg://steamnstats:steamnstats@localhost:5432/steamnstats"
    redis_url: str = "redis://localhost:6379/0"

    steam_web_api_key: str = ""
    steam_openid_realm: str = "http://localhost:8000"
    steam_openid_return_url: str = "http://localhost:8000/auth/steam/callback"
    steam_openid_verify: bool = True

    jwt_secret_key: str = "change-me"
    jwt_refresh_secret_key: str = "change-me-too"
    access_token_expire_minutes: int = 15
    refresh_token_expire_days: int = 30
    game_metadata_ttl_hours: int = 24

    @field_validator("backend_cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, value: str | list[str]) -> list[str]:
        if isinstance(value, str):
            return [origin.strip() for origin in value.split(",") if origin.strip()]
        return value


@lru_cache
def get_settings() -> Settings:
    return Settings()

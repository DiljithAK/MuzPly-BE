from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Muzply YouTube Audio API"
    app_version: str = "1.0.0"
    api_prefix: str = "/api/v1"
    download_timeout_seconds: int = 300
    max_audio_duration_seconds: int = 900
    mp3_audio_quality_kbps: int = 320

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()

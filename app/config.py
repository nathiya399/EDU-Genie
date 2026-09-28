from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application configuration.

    Values can be supplied through environment variables
    or a local .env file.
    """

    app_name: str = "EduGenie"
    app_version: str = "1.0.0"

    gemini_api_key: str | None = None
    gemini_model: str = "gemini-3.8-flash"

    # Set true when you want to run the application without Gemini.
    mock_ai: bool = False

    cors_origins: str = (
        "http://127.0.0.1:8000,"
        "http://localhost:8000"
    )

    max_input_chars: int = 20000

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @property
    def cors_origin_list(self) -> list[str]:
        return [
            origin.strip()
            for origin in self.cors_origins.split(",")
            if origin.strip()
        ]


@lru_cache
def get_settings() -> Settings:
    return Settings()
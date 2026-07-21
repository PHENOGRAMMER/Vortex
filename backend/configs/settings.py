from pathlib import Path
import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import AliasChoices, Field

BACKEND_DIR = Path(__file__).resolve().parents[1]
# backend/configs/settings.py
# parents[0] -> configs
# parents[1] -> backend


class Settings(BaseSettings):

    # Accept both names used by this repository.  The application-level
    # settings and deployment template use OLLAMA_BASE_URL.
    OLLAMA_URL: str = Field(
        default="http://localhost:11434",
        validation_alias=AliasChoices("OLLAMA_URL", "OLLAMA_BASE_URL"),
    )
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    DEFAULT_PROVIDER: str = "ollama"
    DEFAULT_MODEL: str = "qwen2.5-coder:7b"
    DEFAULT_EMBEDDING_MODEL: str = "bge-m3-b1024"
    EMBEDDING_DIMENSION: int = 1024
    EMBEDDING_PROVIDER: str = "ollama"
    EMBEDDING_BATCH_SIZE: int = 16
    EMBEDDING_TIMEOUT_SECONDS: float = 60.0

    model_config = SettingsConfigDict(
        env_file=BACKEND_DIR / ".env",
        extra="ignore",
    )


settings = Settings()

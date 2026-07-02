from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

BACKEND_DIR = Path(__file__).resolve().parents[1]
# backend/configs/settings.py
# parents[0] -> configs
# parents[1] -> backend


class Settings(BaseSettings):

    OLLAMA_URL: str = "http://localhost:11434"
    GEMINI_API_KEY: str = ""
    DEFAULT_PROVIDER: str = "ollama"
    DEFAULT_MODEL: str = "qwen2.5-coder:7b"

    model_config = SettingsConfigDict(
        env_file=BACKEND_DIR / ".env",
        extra="ignore",
    )


settings = Settings()
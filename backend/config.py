from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

BACKEND_DIR = Path(__file__).resolve().parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=BACKEND_DIR / ".env")

    # --- Groq (free tier: generous rate limits, very fast inference) ---
    groq_api_key: str = ""
    groq_text_model: str = "llama-3.1-8b-instant"
    groq_strong_model: str = "llama-3.3-70b-versatile"

    # --- Ollama (self-hosted, zero API cost, runs on your own server/GPU) ---
    ollama_base_url: str = "http://localhost:11434"
    ollama_text_model: str = "llama3.1"
    ollama_code_model: str = "deepseek-coder-v2"

    # --- Model routing defaults ---
    default_provider: str = "ollama"
    default_model: str = "qwen2.5:7b"

    # --- HuggingFace Inference API (free tier, used for image generation) ---
    hf_api_key: str = ""
    hf_image_model: str = "black-forest-labs/FLUX.1-Krea-dev"

    # --- Local GPU image generation (ComfyUI) ---
    comfyui_base_url: str = "http://127.0.0.1:8188"
    comfyui_checkpoint: str = "v1-5-pruned-emaonly-fp16.safetensors"

    # --- Gemini (Google AI Studio free tier, multimodal fallback) ---
    gemini_api_key: str = ""
    gemini_model: str = "gemini-2.0-flash"

    # --- App ---
    app_name: str = "OmniGen"
    environment: str = "development"
    cors_origins: list[str] = ["*"]
    data_dir: Path = BACKEND_DIR / "storage"
    enable_local_image_generation: bool = True
    enable_remote_image_generation: bool = True

    # --- DB / Auth (wired up in later phases, centralized here now) ---
    database_url: str = "sqlite:///./omnigen.db"
    jwt_secret: str = "change-me"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60
    frontend_url: str = "http://localhost:5173"
    session_token_limit: int = 24000

    # --- OAuth login ---
    google_client_id: str = ""
    google_client_secret: str = ""
    google_redirect_uri: str = "http://127.0.0.1:8000/auth/oauth/google/callback"
    github_client_id: str = ""
    github_client_secret: str = ""
    github_redirect_uri: str = "http://127.0.0.1:8000/auth/oauth/github/callback"


@lru_cache
def get_settings() -> Settings:
    return Settings()

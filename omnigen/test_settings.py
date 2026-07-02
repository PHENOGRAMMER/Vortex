from backend.configs.settings import settings

from pathlib import Path

print("settings.py location:", Path(__file__).resolve())
print("Current working directory:", Path.cwd())
print("Looking for .env at:", Path(".env").resolve())

print("OLLAMA_URL:", settings.OLLAMA_URL)
print("DEFAULT_PROVIDER:", settings.DEFAULT_PROVIDER)
print("DEFAULT_MODEL:", settings.DEFAULT_MODEL)
print("GEMINI_API_KEY:", "Loaded" if settings.GEMINI_API_KEY else "Not Set")
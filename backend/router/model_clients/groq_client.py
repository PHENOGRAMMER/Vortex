import time

import httpx

from backend.config import get_settings
from .base import BaseClient, ModelResponse, ModelUnavailableError

settings = get_settings()


class GroqClient(BaseClient):
    provider_name = "groq"
    BASE_URL = "https://api.groq.com/openai/v1/chat/completions"

    async def chat(self, messages, model=None, **kwargs) -> ModelResponse:
        model = model or settings.groq_text_model
        start = time.perf_counter()
        try:
            async with httpx.AsyncClient(timeout=30) as client:
                resp = await client.post(
                    self.BASE_URL,
                    headers={"Authorization": f"Bearer {settings.groq_api_key}"},
                    json={
                        "model": model,
                        "messages": messages,
                        "temperature": kwargs.pop("temperature", 0.55),
                        "max_tokens": kwargs.pop("max_tokens", 1600),
                        **kwargs,
                    },
                )
            if resp.status_code == 429:
                raise ModelUnavailableError("groq rate-limited")
            resp.raise_for_status()
            data = resp.json()
            text = data["choices"][0]["message"]["content"]
            return ModelResponse(
                content=text,
                provider=self.provider_name,
                model=model,
                latency_ms=(time.perf_counter() - start) * 1000,
                raw=data,
            )
        except httpx.HTTPError as e:
            raise ModelUnavailableError(f"groq error: {e}") from e


groq_client = GroqClient()

import time

import httpx

from backend.config import get_settings
from .base import BaseClient, ModelResponse, ModelUnavailableError

settings = get_settings()


class OllamaClient(BaseClient):
    provider_name = "ollama"

    async def chat(self, messages, model=None, **kwargs) -> ModelResponse:
        model = model or settings.ollama_text_model
        start = time.perf_counter()
        try:
            async with httpx.AsyncClient(timeout=60) as client:
                resp = await client.post(
                    f"{settings.ollama_base_url}/api/chat",
                    json={
                        "model": model,
                        "messages": messages,
                        "stream": False,
                        "options": {
                            "temperature": kwargs.pop("temperature", 0.55),
                            "num_predict": kwargs.pop("max_tokens", 1600),
                        },
                        **kwargs,
                    },
                )
            resp.raise_for_status()
            data = resp.json()
            text = data["message"]["content"]
            return ModelResponse(
                content=text,
                provider=self.provider_name,
                model=model,
                latency_ms=(time.perf_counter() - start) * 1000,
                raw=data,
            )
        except httpx.HTTPError as e:
            # e.g. ollama not running, model not pulled, server unreachable
            raise ModelUnavailableError(f"ollama error: {e}") from e


ollama_client = OllamaClient()

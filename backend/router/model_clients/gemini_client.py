import time

import httpx

from backend.config import get_settings
from .base import BaseClient, ModelResponse, ModelUnavailableError

settings = get_settings()


class GeminiClient(BaseClient):
    provider_name = "gemini"

    async def chat(self, messages, model=None, **kwargs) -> ModelResponse:
        model = model or settings.gemini_model
        start = time.perf_counter()
        url = (
            f"https://generativelanguage.googleapis.com/v1beta/models/"
            f"{model}:generateContent?key={settings.gemini_api_key}"
        )
        system_instruction = None
        contents = []
        for m in messages:
            if m["role"] == "system":
                system_instruction = {"parts": [{"text": m["content"]}]}
            else:
                contents.append({
                    "role": "model" if m["role"] == "assistant" else "user",
                    "parts": [{"text": m["content"]}],
                })
        try:
            json_payload = {
                "contents": contents,
                "generationConfig": {
                    "temperature": kwargs.pop("temperature", 0.55),
                    "maxOutputTokens": kwargs.pop("max_tokens", 1600),
                },
            }
            if system_instruction:
                json_payload["systemInstruction"] = system_instruction

            async with httpx.AsyncClient(timeout=30) as client:
                resp = await client.post(
                    url,
                    json=json_payload,
                )
            if resp.status_code == 429:
                raise ModelUnavailableError("gemini rate-limited")
            resp.raise_for_status()
            data = resp.json()
            text = data["candidates"][0]["content"]["parts"][0]["text"]
            return ModelResponse(
                content=text,
                provider=self.provider_name,
                model=model,
                latency_ms=(time.perf_counter() - start) * 1000,
                raw=data,
            )
        except httpx.HTTPError as e:
            raise ModelUnavailableError(f"gemini error: {e}") from e


gemini_client = GeminiClient()

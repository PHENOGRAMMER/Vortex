import base64
import time
from typing import Optional

import httpx

from backend.config import get_settings
from .base import BaseClient, ModelResponse, ModelUnavailableError

settings = get_settings()


class HFClient(BaseClient):
    provider_name = "huggingface"

    async def generate_image(self, prompt: str, model: Optional[str] = None) -> ModelResponse:
        model = model or settings.hf_image_model
        start = time.perf_counter()
        url = f"https://router.huggingface.co/hf-inference/models/{model}"
        try:
            async with httpx.AsyncClient(timeout=60) as client:
                resp = await client.post(
                    url,
                    headers={"Authorization": f"Bearer {settings.hf_api_key}"},
                    json={"inputs": prompt},
                )
            if resp.status_code == 503:
                # Free-tier models unload when idle; first call "wakes" them up.
                raise ModelUnavailableError("hf model is cold-starting, retry shortly")
            if resp.status_code == 429:
                raise ModelUnavailableError("hf rate-limited")
            try:
                resp.raise_for_status()
            except httpx.HTTPStatusError as e:
                detail = resp.text[:500] if resp.text else str(e)
                raise ModelUnavailableError(f"huggingface error: {detail}") from e
            image_b64 = base64.b64encode(resp.content).decode()
            return ModelResponse(
                content=image_b64,
                provider=self.provider_name,
                model=model,
                latency_ms=(time.perf_counter() - start) * 1000,
            )
        except httpx.HTTPError as e:
            raise ModelUnavailableError(f"huggingface error: {e}") from e

    async def chat(self, messages, model=None, **kwargs) -> ModelResponse:
        raise NotImplementedError("HFClient currently handles image generation only")


hf_client = HFClient()

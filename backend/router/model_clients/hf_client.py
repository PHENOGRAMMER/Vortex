import base64
import asyncio
from io import BytesIO
import time
from typing import Optional

from huggingface_hub import InferenceClient

from backend.config import get_settings
from .base import BaseClient, ModelResponse, ModelUnavailableError

settings = get_settings()


class HFClient(BaseClient):
    provider_name = "huggingface"

    async def generate_image(self, prompt: str, model: Optional[str] = None) -> ModelResponse:
        model = model or settings.hf_image_model
        if not settings.hf_api_key:
            raise ModelUnavailableError("Hugging Face image generation requires an HF token with Inference Providers permission.")
        start = time.perf_counter()
        try:
            image_bytes = await asyncio.to_thread(self._generate_image, prompt, model)
            image_b64 = base64.b64encode(image_bytes).decode()
            return ModelResponse(
                content=image_b64,
                provider=self.provider_name,
                model=model,
                latency_ms=(time.perf_counter() - start) * 1000,
            )
        except ModelUnavailableError:
            raise
        except Exception as e:
            raise ModelUnavailableError(f"Hugging Face image generation failed: {e}") from e

    @staticmethod
    def _generate_image(prompt: str, model: str) -> bytes:
        """Use Hugging Face Inference Providers' supported image API."""
        client = InferenceClient(api_key=settings.hf_api_key, provider="auto", timeout=120)
        image = client.text_to_image(prompt=prompt, model=model)
        if isinstance(image, bytes):
            return image
        buffer = BytesIO()
        image.save(buffer, format="PNG")
        return buffer.getvalue()

    async def chat(self, messages, model=None, **kwargs) -> ModelResponse:
        raise NotImplementedError("HFClient currently handles image generation only")


hf_client = HFClient()

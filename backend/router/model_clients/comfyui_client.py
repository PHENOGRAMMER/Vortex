import asyncio
import base64
import random
import time

import httpx

from backend.config import get_settings
from .base import BaseClient, ModelResponse, ModelUnavailableError

settings = get_settings()


class ComfyUIClient(BaseClient):
    """Generate real images through a locally running ComfyUI instance."""

    provider_name = "local-comfyui"

    async def generate_image(self, prompt: str) -> ModelResponse:
        started = time.perf_counter()
        workflow = self._workflow(prompt)
        try:
            async with httpx.AsyncClient(timeout=20) as client:
                response = await client.post(f"{settings.comfyui_base_url}/prompt", json={"prompt": workflow})
                response.raise_for_status()
                prompt_id = response.json().get("prompt_id")
                if not prompt_id:
                    raise ModelUnavailableError("ComfyUI did not return a prompt ID.")

                history = await self._wait_for_result(client, prompt_id)
                image = self._first_output_image(history, prompt_id)
                image_response = await client.get(
                    f"{settings.comfyui_base_url}/view",
                    params={"filename": image["filename"], "subfolder": image.get("subfolder", ""), "type": image.get("type", "output")},
                )
                image_response.raise_for_status()
        except httpx.ConnectError as exc:
            raise ModelUnavailableError(
                "Local image generator is not running. Start ComfyUI at http://127.0.0.1:8188 and install the configured checkpoint."
            ) from exc
        except httpx.HTTPError as exc:
            raise ModelUnavailableError(f"Local ComfyUI image generation failed: {exc}") from exc

        return ModelResponse(
            content=base64.b64encode(image_response.content).decode(),
            provider=self.provider_name,
            model=settings.comfyui_checkpoint,
            latency_ms=(time.perf_counter() - started) * 1000,
        )

    @staticmethod
    def _workflow(prompt: str) -> dict:
        positive_prompt = (
            "high-quality detailed digital artwork, cinematic lighting, sharp focus, "
            "well-composed subject, rich color and texture, "
            f"{prompt}"
        )
        negative_prompt = (
            "lowres, blurry, low quality, jpeg artifacts, distorted, malformed anatomy, "
            "extra fingers, extra limbs, cropped, watermark, text, signature, logo"
        )
        return {
            "4": {"class_type": "CheckpointLoaderSimple", "inputs": {"ckpt_name": settings.comfyui_checkpoint}},
            "5": {"class_type": "EmptyLatentImage", "inputs": {"width": 512, "height": 512, "batch_size": 1}},
            "6": {"class_type": "CLIPTextEncode", "inputs": {"text": positive_prompt, "clip": ["4", 1]}},
            "7": {"class_type": "CLIPTextEncode", "inputs": {"text": negative_prompt, "clip": ["4", 1]}},
            "3": {"class_type": "KSampler", "inputs": {"seed": random.randint(0, 2**63 - 1), "steps": 28, "cfg": 7.5, "sampler_name": "dpmpp_2m", "scheduler": "karras", "denoise": 1.0, "model": ["4", 0], "positive": ["6", 0], "negative": ["7", 0], "latent_image": ["5", 0]}},
            "8": {"class_type": "VAEDecode", "inputs": {"samples": ["3", 0], "vae": ["4", 2]}},
            "9": {"class_type": "SaveImage", "inputs": {"filename_prefix": "omnigen", "images": ["8", 0]}},
        }

    @staticmethod
    async def _wait_for_result(client: httpx.AsyncClient, prompt_id: str) -> dict:
        for _ in range(60):
            await asyncio.sleep(2)
            response = await client.get(f"{settings.comfyui_base_url}/history/{prompt_id}")
            response.raise_for_status()
            history = response.json()
            if prompt_id in history:
                return history[prompt_id]
        raise ModelUnavailableError("Local image generation timed out after two minutes.")

    @staticmethod
    def _first_output_image(history: dict, prompt_id: str) -> dict:
        outputs = history.get("outputs", {})
        for output in outputs.values():
            images = output.get("images", [])
            if images:
                return images[0]
        raise ModelUnavailableError(f"ComfyUI completed {prompt_id} without an image output.")

    async def chat(self, messages, model=None, **kwargs) -> ModelResponse:
        raise NotImplementedError("ComfyUIClient only supports image generation.")


comfyui_client = ComfyUIClient()

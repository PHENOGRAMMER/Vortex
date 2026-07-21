import httpx

from backend.configs.settings import settings
import os

class GeminiClient:

    def __init__(self):

        self.api_key = settings.GEMINI_API_KEY

        self.base_url = (
            "https://generativelanguage.googleapis.com/v1beta"
        )

    @property
    def headers(self):

        return {
            "Content-Type": "application/json",
        }

    async def stream_chat(
        self,
        payload: dict,
        model: str,
    ):

        url = (
            f"{self.base_url}/models/"
            f"{model}:streamGenerateContent"
        )

        params = {
            "key": self.api_key,
            "alt": "sse",
        }

        async with httpx.AsyncClient(
            timeout=None,
        ) as client:

            async with client.stream(
                "POST",
                url,
                headers=self.headers,
                params=params,
                json=payload,
            ) as response:

                response.raise_for_status()

                async for line in response.aiter_lines():

                    if not line:
                        continue

                    if not line.startswith("data:"):
                        continue

                    yield line.removeprefix("data:").strip()

    async def generate_content(
        self,
        payload: dict,
        model: str,
    ):

        url = (
            f"{self.base_url}/models/"
            f"{model}:generateContent"
        )

        params = {
            "key": self.api_key,
        }

        async with httpx.AsyncClient() as client:

            response = await client.post(
                url,
                headers=self.headers,
                params=params,
                json=payload,
            )

            response.raise_for_status()

            return response.json()

    async def embeddings(
        self,
        text: str | list[str],
        model: str = "text-embedding-004",
    ):

        # Gemini embedContent accepts one input at a time
        if isinstance(text, list):
            text = text[0]

        url = (
            f"{self.base_url}/models/"
            f"{model}:embedContent"
        )

        params = {
            "key": self.api_key,
        }

        payload = {
            "model": f"models/{model}",
            "content": {
                "parts": [
                    {
                        "text": text,
                    }
                ]
            },
        }

        async with httpx.AsyncClient() as client:

            response = await client.post(
                url,
                headers=self.headers,
                params=params,
                json=payload,
            )

            # Temporary debugging
            print("=" * 70)
            print("GEMINI EMBEDDINGS")
            print(response.status_code)
            print(response.text)
            print("=" * 70)

            response.raise_for_status()

            return response.json()
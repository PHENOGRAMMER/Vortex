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

            if response.is_error:
                print("="* 70)
                print("Gemini Embedding Error")
                print("Status Code: ", response.status_code)
                print("Body: ", response.text)
                print("="* 70)

            response.raise_for_status()

            return response.json()

    async def embeddings(
        self,
        text: str | list[str],
        model: str = "text-embedding-004",
    ):

        params = {
            "key": self.api_key,
        }

        async with httpx.AsyncClient(timeout=60.0) as client:

            # Single input
            if isinstance(text, str):

                url = (
                    f"{self.base_url}/models/"
                    f"{model}:embedContent"
                )

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

                response = await client.post(
                    url,
                    headers=self.headers,
                    params=params,
                    json=payload,
                )

                response.raise_for_status()

                return response.json()

            # Multiple inputs
            url = (
                f"{self.base_url}/models/"
                f"{model}:batchEmbedContents"
            )

            payload = {
                "requests": [
                    {
                        "model": f"models/{model}",
                        "content": {
                            "parts": [
                                {
                                    "text": item,
                                }
                            ]
                        },
                    }
                    for item in text
                ]
            }

            response = await client.post(
                url,
                headers=self.headers,
                params=params,
                json=payload,
            )

            response.raise_for_status()

            return response.json()
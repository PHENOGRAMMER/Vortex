import json

import httpx

from backend.configs.settings import settings


class OllamaClient:

    def __init__(self):

        self.base_url = settings.OLLAMA_URL

    async def stream_chat(self, payload):

        async with httpx.AsyncClient(timeout=None) as client:

            async with client.stream(

                "POST",

                f"{self.base_url}/api/chat",

                json=payload,

            ) as response:

                response.raise_for_status()

                async for line in response.aiter_lines():

                    if line:

                        yield json.loads(line)

    async def list_models(self):

        async with httpx.AsyncClient() as client:

            response = await client.get(

                f"{self.base_url}/api/tags"

            )

            response.raise_for_status()

            return response.json()


    async def health(self):

        try:

            async with httpx.AsyncClient() as client:

                response = await client.get(

                    self.base_url

                )

                return response.status_code == 200

        except Exception:

            return False
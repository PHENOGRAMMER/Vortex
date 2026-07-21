from asyncio import sleep

from backend.providers.base import BaseProvider
from backend.models.chat_request import ChatRequest
from backend.core.stream_context import StreamContext


class MockProvider(BaseProvider):

    id = "mock"

    name = "Mock Provider"

    capabilities = {
        "streaming": True,
        "vision": False,
        "embeddings": False,
        "tool_calling": False,
        "images": False,
        "local": True,
    }

    async def stream_chat(self, request: ChatRequest):

        stream = StreamContext()

        yield stream.status("Using Mock Provider")

        words = [
            "Hello",
            ",",
            " this",
            " is",
            " the",
            " mock",
            " provider."
        ]

        for word in words:

            await sleep(0.15)

            yield stream.token(word)

        yield stream.done()

    async def complete(self, request):

        raise NotImplementedError()

    async def list_models(self):

        return [
            {
                "id": "mock",
                "name": "Mock Model"
            }
        ]

    async def health(self):

        return True
    
    async def embeddings(
        self,
        input: str | list[str],
        model: str | None = None,
    ) -> list[list[float]]:

        if isinstance(input, str):
            input = [input]

        return [[0.0] * 768 for _ in input]
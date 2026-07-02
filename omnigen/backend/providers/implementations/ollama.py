from backend.providers.base import BaseProvider
from backend.providers.clients.ollama_client import OllamaClient
from backend.configs.settings import settings

from backend.models.chat_request import ChatRequest
from backend.core.stream_context import StreamContext
from backend.models.model_info import ModelInfo


class OllamaProvider(BaseProvider):

    id = "ollama"

    name = "Ollama"

    capabilities = {

        "streaming": True,
        "vision": False,
        "embeddings": True,
        "tool_calling": False,
        "images": False,
        "local": True,
    }

    def __init__(self):

        self.client = OllamaClient()

    async def stream_chat(
        self,
        request: ChatRequest,
    ):

        stream = StreamContext()

        model = request.model or settings.DEFAULT_MODEL

        yield stream.status(
            f"Using Ollama ({model})"
        )

        payload = {

            "model": model,

            "messages": [
                message.dict()
                for message in request.messages
            ],
            "stream": True,
        }

        async for chunk in self.client.stream_chat(payload):

            if "message" in chunk:

                content = chunk["message"].get(
                    "content",
                    "",
                )

                if content:

                    yield stream.token(content)

            if chunk.get("done"):

                break

        yield stream.done()

    async def complete(
            self,
            request: ChatRequest,
            ):
        raise NotImplementedError("Ollama provider currently supports streaming only.") 

    async def list_models(self) -> list[ModelInfo]:
        response = await self.client.list_models()
        models = []

        for item in response.get("models", []):
            name = item["name"]
            capabilities = ["chat"]
            if "coder" in name.lower():
                capabilities = ["code", "chat", "reasoning"]
            elif "embed" in name.lower():
                capabilities = ["embedding"]
            elif "vision" in name.lower():
                capabilities = ["vision"]

            context = 32768
            details = item.get("details", {})

            model = ModelInfo(
                id=name,
                name=name,
                provider=self.id,
                capabilities=capabilities,
                context_length=context,
                vision="vision" in capabilities,
                tool_calling=True,
                embeddings="embedding" in capabilities,
                local=True,
                speed="fast",
                priority=100 if "code" in capabilities else 50,
                cost=0,
            )
            models.append(model)

        return models

    async def health(self):

        return await self.client.health()
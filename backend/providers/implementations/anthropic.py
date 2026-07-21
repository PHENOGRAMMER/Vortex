from backend.providers.base import BaseProvider


class AnthropicProvider(BaseProvider):

    id = "anthropic"

    name = "Anthropic Claude"

    capabilities = {
        "streaming": True,
        "vision": True,
        "embeddings": False,
        "tool_calling": True,
        "images": False,
        "local": False,
    }

    async def stream_chat(self, request):
        raise NotImplementedError("Anthropic integration not enabled.")

    async def complete(self, request):
        raise NotImplementedError
from backend.providers.base import BaseProvider
from backend.models.chat_request import ChatRequest
from backend.core.stream_context import StreamContext
from backend.models.model_info import ModelInfo


class GeminiProvider(BaseProvider):

    id = "gemini"

    name = "Google Gemini"

    capabilities = {

        "streaming": True,
        "vision": True,
        "embeddings": True,
        "tool_calling": True,
        "images": False,
        "local": False,

    }

    async def stream_chat(self, request: ChatRequest):

        stream = StreamContext()

        yield stream.status("Gemini Provider")

        yield stream.token(
            "Gemini implementation coming next."
        )

        yield stream.done()

    async def complete(self, request):

        raise NotImplementedError()

    async def list_models(self) -> list[ModelInfo]:

        return [

        ModelInfo(

            id="gemini-2.5-flash",

            name="Gemini 2.5 Flash",

            provider=self.id,

            capabilities=[
                "chat",
                "reasoning",
                "code",
                "vision",
            ],

            context_length=1_048_576,

            vision=True,

            tool_calling=True,

            embeddings=False,

            local=False,

            speed="fast",

            priority=90,

            cost=1,
        ),

        ModelInfo(

            id="gemini-2.5-pro",

            name="Gemini 2.5 Pro",

            provider=self.id,

            capabilities=[
                "chat",
                "reasoning",
                "code",
                "vision",
            ],

            context_length=2_097_152,

            vision=True,

            tool_calling=True,

            embeddings=False,

            local=False,

            speed="medium",

            priority=95,

            cost=1,
        ),
    ]

    async def health(self):

        return True
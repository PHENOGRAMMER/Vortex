import json

from backend.providers.base import BaseProvider
from backend.providers.clients.gemini_client import GeminiClient

from backend.models.chat_request import ChatRequest
from backend.models.model_info import ModelInfo

from backend.core.stream_context import StreamContext


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

    def __init__(self):
        self.client = GeminiClient()

    async def stream_chat(
        self,
        request: ChatRequest,
    ):

        stream = StreamContext(
            request.metadata.get("stream_id")
        )

        contents = []

        for message in request.messages:

            role = (
                "model"
                if message.role == "assistant"
                else "user"
            )

            contents.append(
                {
                    "role": role,
                    "parts": [
                        {
                            "text": message.content
                        }
                    ],
                }
            )

        payload = {
            "contents": contents,
            "generationConfig": {
                "temperature": request.temperature,
                "maxOutputTokens": request.max_tokens,
            },
        }

        async for chunk in self.client.stream_chat(
            payload,
            request.model,
        ):

            if not chunk:
                continue

            try:
                data = json.loads(chunk)
            except json.JSONDecodeError:
                continue

            candidates = data.get("candidates", [])

            if not candidates:
                continue

            parts = (
                candidates[0]
                .get("content", {})
                .get("parts", [])
            )

            if not parts:
                continue

            text = parts[0].get("text", "")

            if text:
                yield stream.token(text)

        yield stream.done()

    async def complete(
        self,
        request,
    ):
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
                embeddings=True,
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
                embeddings=True,
                local=False,
                speed="medium",
                priority=95,
                cost=1,
            ),
        ]

    async def health(self):
        return True

    async def embeddings(
        self,
        input: str | list[str],
        model: str | None = None,
    ) -> list[list[float]]:

        model = model or "text-embedding-004"

        response = await self.client.embeddings(
            text=input,
            model=model,
        )

        # Response from batchEmbedContents
        if "embeddings" in response:
            return [
                item.get("values", [])
                for item in response["embeddings"]
            ]

        # Response from embedContent
        if "embedding" in response:
            return [
                response["embedding"].get("values", [])
            ]

        raise RuntimeError(
            f"Unexpected Gemini embedding response: {response}"
        )
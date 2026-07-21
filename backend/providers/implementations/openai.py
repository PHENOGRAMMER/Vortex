from backend.providers.base import BaseProvider
from backend.models.model_info import ModelInfo


class OpenAIProvider(BaseProvider):

    id = "openai"

    name = "OpenAI"

    capabilities = {
        "streaming": True,
        "vision": True,
        "embeddings": True,
        "tool_calling": True,
        "images": True,
        "local": False,
    }

    async def stream_chat(self, request):
        raise NotImplementedError("OpenAI integration not enabled.")

    async def complete(self, request):
        raise NotImplementedError

    async def list_models(self) -> list[ModelInfo]:

        return [
            ModelInfo(
                id="gpt-4.1",
                name="GPT-4.1",
                provider=self.id,
                capabilities=[
                    "chat",
                    "reasoning",
                    "code",
                    "vision",
                ],
                context_length=1_047_576,
                vision=True,
                tool_calling=True,
                embeddings=False,
                local=False,
                speed="medium",
                priority=100,
                cost=3,
            ),
            ModelInfo(
                id="gpt-4.1-mini",
                name="GPT-4.1 Mini",
                provider=self.id,
                capabilities=[
                    "chat",
                    "reasoning",
                    "code",
                    "vision",
                ],
                context_length=1_047_576,
                vision=True,
                tool_calling=True,
                embeddings=False,
                local=False,
                speed="fast",
                priority=95,
                cost=2,
            ),
            ModelInfo(
                id="gpt-4.1-nano",
                name="GPT-4.1 Nano",
                provider=self.id,
                capabilities=[
                    "chat",
                    "reasoning",
                    "code",
                ],
                context_length=1_047_576,
                vision=False,
                tool_calling=True,
                embeddings=False,
                local=False,
                speed="very_fast",
                priority=90,
                cost=1,
            ),
            ModelInfo(
                id="gpt-5",
                name="GPT-5",
                provider=self.id,
                capabilities=[
                    "chat",
                    "reasoning",
                    "code",
                    "vision",
                ],
                context_length=400_000,
                vision=True,
                tool_calling=True,
                embeddings=False,
                local=False,
                speed="medium",
                priority=110,
                cost=4,
            ),
            ModelInfo(
                id="gpt-5-mini",
                name="GPT-5 Mini",
                provider=self.id,
                capabilities=[
                    "chat",
                    "reasoning",
                    "code",
                    "vision",
                ],
                context_length=400_000,
                vision=True,
                tool_calling=True,
                embeddings=False,
                local=False,
                speed="fast",
                priority=105,
                cost=3,
            ),
            ModelInfo(
                id="gpt-5-nano",
                name="GPT-5 Nano",
                provider=self.id,
                capabilities=[
                    "chat",
                    "reasoning",
                    "code",
                ],
                context_length=400_000,
                vision=False,
                tool_calling=True,
                embeddings=False,
                local=False,
                speed="very_fast",
                priority=95,
                cost=2,
            ),
        ]

    async def health(self):

        return True
    
    async def embeddings(
            self,
            input: str | list[str],
            model: str | None = None,
    ) -> list[list[float]]:
        
        raise NotImplementedError("Gemini provider currently does not support embeddings.")    
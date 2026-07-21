from backend.models.chat_request import ChatRequest
from backend.services.chat_service import ChatService
from backend.services.prompt_assembler import PromptAssembler


class GenerationService:
    def __init__(self):
        self.chat_service = ChatService()

    async def generate(
        self,
        question: str,
        chunks,
        history: list[dict] | None = None,
        temperature: float = 0.2,
        max_tokens: int | None = 1200,
    ) -> tuple[str, str]:
        messages = PromptAssembler.assemble(
            question=question,
            chunks=chunks,
            history=history,
        )
        request = ChatRequest(
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            metadata={"rag": True},
        )
        return await self.chat_service.chat(request)

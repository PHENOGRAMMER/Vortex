from backend.services.generation_service import GenerationService
from backend.services.prompt_assembler import PromptAssembler
from backend.services.response_formatter import ResponseFormatter
from backend.services.retrieval_service import RetrievalService


class RAGService:

    def __init__(self):

        self.retriever = RetrievalService()
        self.generator = GenerationService()

    async def build_prompt(
        self,
        question: str,
        top_k: int = 5,
    ) -> str:

        retrieved_chunks = await self.retriever.retrieve(

            query=question,

            top_k=20,

        )

        prompt = PromptAssembler.assemble(
            question=question,
            chunks=retrieved_chunks[:top_k],
        )[-1]["content"]

        return prompt

    async def retrieve(
        self,
        question: str,
        top_k: int = 5,
        document_ids: list[str] | None = None,
        filenames: list[str] | None = None,
        user_id: int | None = None,
        session_id: int | None = None,
    ) -> dict:
        chunks = await self.retriever.retrieve(
            query=question,
            top_k=top_k,
            document_ids=document_ids,
            filenames=filenames,
            user_id=user_id,
            session_id=session_id,
        )
        return ResponseFormatter.format_retrieval(question, chunks)

    async def answer(
        self,
        question: str,
        top_k: int = 5,
        history: list[dict] | None = None,
        document_ids: list[str] | None = None,
        filenames: list[str] | None = None,
        user_id: int | None = None,
        session_id: int | None = None,
    ) -> dict:
        chunks = await self.retriever.retrieve(
            query=question,
            top_k=top_k,
            document_ids=document_ids,
            filenames=filenames,
            user_id=user_id,
            session_id=session_id,
        )
        if not chunks:
            return ResponseFormatter.format_answer(
                question=question,
                answer="I couldn't find that information in the uploaded documents.",
                chunks=[],
                model="none",
            )

        answer, model = await self.generator.generate(
            question=question,
            chunks=chunks,
            history=history,
        )
        return ResponseFormatter.format_answer(
            question=question,
            answer=answer,
            chunks=chunks,
            model=model,
        )

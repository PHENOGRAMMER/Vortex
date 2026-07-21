from backend.models.retrieved_chunk import RetrievedChunk


class PromptAssembler:
    SYSTEM_PROMPT = (
        "You are OmniGen, a careful document-grounded assistant. "
        "Answer only from the relevant context; never add tools, components, "
        "or facts that are not stated there. Preserve important named lists and "
        "architecture layers. If the context does not contain the answer, say that "
        "you could not find it in the uploaded documents."
    )

    @staticmethod
    def assemble(
        question: str,
        chunks: list[RetrievedChunk],
        history: list[dict] | None = None,
    ) -> list[dict]:
        context = PromptAssembler.context_text(chunks)
        history_messages = [
            item
            for item in (history or [])[-8:]
            if item.get("role") in {"user", "assistant"} and item.get("content")
        ]

        return [
            {"role": "system", "content": PromptAssembler.SYSTEM_PROMPT},
            *history_messages,
            {
                "role": "user",
                "content": (
                    f"Question:\n{question}\n\n"
                    f"Relevant Context:\n{context}\n\n"
                    "Give a direct, structured answer. For methodology or architecture "
                    "questions, use a short overview followed by the explicitly named "
                    "layers/components as bullets. Cite only the exact filename(s) shown "
                    "in the context; do not invent or substitute filenames."
                ),
            },
        ]

    @staticmethod
    def context_text(chunks: list[RetrievedChunk]) -> str:
        if not chunks:
            return "No relevant context was retrieved."

        sections = []
        for index, chunk in enumerate(chunks, start=1):
            start_chunk = chunk.source_start_chunk
            if start_chunk is None:
                start_chunk = chunk.chunk_index
            end_chunk = chunk.source_end_chunk
            if end_chunk is None:
                end_chunk = chunk.chunk_index
            section = f"\nSection: {chunk.section}" if chunk.section else ""
            sections.append(
                (
                    f"Source {index}\n"
                    f"File: {chunk.filename}\n"
                    f"Document ID: {chunk.document_id}\n"
                    f"Chunks: {start_chunk}-{end_chunk}"
                    f"{section}\n\n"
                    f"{chunk.text}"
                )
            )
        return "\n\n---\n\n".join(sections)

from backend.models.retrieved_chunk import RetrievedChunk


class PromptBuilder:

    SYSTEM_PROMPT = """You are OmniGen, an AI assistant.

Answer the user's question ONLY using the provided context.

Instructions:

- Use only information found in the retrieved context.
- Never invent facts.
- If the answer cannot be found in the context, reply exactly:
  "I couldn't find that information in the provided documents."
- If multiple sources contain relevant information, combine them into one answer.
- Do not mention internal chunk numbers unless explicitly asked.
- Keep answers concise and accurate.
"""

    @staticmethod
    def build(
        question: str,
        chunks: list[RetrievedChunk],
    ) -> str:

        context_sections = []

        for i, chunk in enumerate(chunks, start=1):
            filename = getattr(chunk, "filename", "unknown")
            chunk_index = getattr(chunk, "chunk_index", getattr(chunk, "index", i - 1))
            score = getattr(chunk, "score", 0.0)

            context_sections.append(
                f"""Source {i}

File: {filename}
Chunk: {chunk_index}
Similarity: {score:.4f}

{chunk.text}
"""
            )

        context = "\n" + ("-" * 80) + "\n\n"

        context += ("\n" + ("-" * 80) + "\n\n").join(
            context_sections
        )

        prompt = f"""{PromptBuilder.SYSTEM_PROMPT}

==================== CONTEXT ====================

{context}

=================================================

Question:

{question}

Answer:
"""

        return prompt

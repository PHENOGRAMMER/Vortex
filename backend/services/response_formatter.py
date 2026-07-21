from backend.models.retrieved_chunk import RetrievedChunk


class ResponseFormatter:
    @staticmethod
    def sources(chunks: list[RetrievedChunk]) -> list[dict]:
        return [
            {
                "document_id": chunk.document_id,
                "filename": chunk.filename,
                "chunk_id": chunk.chunk_id,
                "chunk_index": chunk.chunk_index,
                "chunk_start": chunk.source_start_chunk
                if chunk.source_start_chunk is not None
                else chunk.chunk_index,
                "chunk_end": chunk.source_end_chunk
                if chunk.source_end_chunk is not None
                else chunk.chunk_index,
                "section": chunk.section,
                "score": round(float(chunk.score), 4),
            }
            for chunk in chunks
        ]

    @staticmethod
    def confidence(chunks: list[RetrievedChunk]) -> float:
        if not chunks:
            return 0.0
        scores = [max(0.0, float(chunk.score)) for chunk in chunks]
        average = sum(scores) / len(scores)
        return round(min(1.0, average), 3)

    @staticmethod
    def format_retrieval(
        question: str,
        chunks: list[RetrievedChunk],
    ) -> dict:
        return {
            "question": question,
            "relevant_context": [
                {
                    "text": chunk.text,
                    "source": source,
                }
                for chunk, source in zip(chunks, ResponseFormatter.sources(chunks))
            ],
            "sources": ResponseFormatter.sources(chunks),
            "confidence": ResponseFormatter.confidence(chunks),
        }

    @staticmethod
    def format_answer(
        question: str,
        answer: str,
        chunks: list[RetrievedChunk],
        model: str,
    ) -> dict:
        payload = ResponseFormatter.format_retrieval(question, chunks)
        payload.update(
            {
                "answer": answer,
                "model": model,
            }
        )
        return payload

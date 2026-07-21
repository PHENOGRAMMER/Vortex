from backend.models.retrieved_chunk import RetrievedChunk


class Reranker:

    def __init__(self):
        self.model = None
        self._load_error = None

    def _get_model(self):
        if self.model is not None:
            return self.model
        if self._load_error is not None:
            return None
        try:
            from sentence_transformers import CrossEncoder

            self.model = CrossEncoder(
                "BAAI/bge-reranker-base"
            )
        except Exception as ex:
            self._load_error = ex
            print(f"Cross encoder reranker unavailable: {ex}")
            return None
        return self.model

    def rerank(
        self,
        query: str,
        chunks: list[RetrievedChunk],
        top_k: int = 5,
    ) -> list[RetrievedChunk]:

        if not chunks:
            return []

        model = self._get_model()
        if model is None:
            return sorted(
                chunks,
                key=lambda chunk: chunk.score,
                reverse=True,
            )[:top_k]

        pairs = [

            (
                query,
                chunk.text,
            )

            for chunk in chunks

        ]

        scores = model.predict(
            pairs,
            show_progress_bar=False,
        )

        ranked = list(

            zip(
                chunks,
                scores,
            )

        )

        ranked.sort(

            key=lambda x: x[1],

            reverse=True,

        )

        reranked = []

        for chunk, score in ranked[:top_k]:

            chunk.score = float(score)

            reranked.append(chunk)

        return reranked

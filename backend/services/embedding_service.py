from backend.providers.factory import ProviderFactory
from backend.configs.settings import settings
import asyncio


class EmbeddingService:

    def __init__(self):
        self.provider = (
            ProviderFactory.get("ollama")
            if settings.EMBEDDING_PROVIDER == "ollama"
            else None
        )
        self._local_model = None

    async def embed(
        self,
        texts: list[str],
    ) -> list[list[float]]:

        if not texts:
            return []

        if settings.EMBEDDING_PROVIDER == "sentence-transformers":
            return await asyncio.to_thread(self._embed_with_sentence_transformers, texts)

        if self.provider is None:
            raise RuntimeError(f"Unsupported embedding provider: {settings.EMBEDDING_PROVIDER}")

        print("EMBEDDING SERVICE Start")
        result = []
        # Large documents can contain dozens of chunks.  Sending bounded
        # batches prevents one slow Ollama request from making the upload look
        # permanently stuck and works with models that enforce input limits.
        for start in range(0, len(texts), settings.EMBEDDING_BATCH_SIZE):
            batch = texts[start:start + settings.EMBEDDING_BATCH_SIZE]
            result.extend(await self.provider.embeddings(
                input=batch,
                model=settings.DEFAULT_EMBEDDING_MODEL,
            ))

        print("Embedding Service End.")

        return result

    def _embed_with_sentence_transformers(self, texts: list[str]) -> list[list[float]]:
        """CPU-friendly hosted fallback that does not require Ollama."""
        if self._local_model is None:
            from sentence_transformers import SentenceTransformer
            self._local_model = SentenceTransformer(settings.DEFAULT_EMBEDDING_MODEL)
        vectors = self._local_model.encode(texts, normalize_embeddings=True)
        return vectors.tolist()

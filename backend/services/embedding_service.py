from backend.providers.factory import ProviderFactory
from backend.configs.settings import settings


class EmbeddingService:
    """
    Provider-agnostic embedding service.

    The configured provider is responsible for generating embeddings.
    Supported providers currently include:
        - ollama
        - gemini
    """

    def __init__(self):
        self.provider = ProviderFactory.get(
            settings.EMBEDDING_PROVIDER
        )

    async def embed(
        self,
        texts: list[str],
    ) -> list[list[float]]:

        if not texts:
            return []

        print("=" * 70)
        print("EMBEDDING SERVICE")
        print("=" * 70)
        print(f"Provider : {settings.EMBEDDING_PROVIDER}")
        print(f"Model    : {settings.DEFAULT_EMBEDDING_MODEL}")
        print(f"Texts    : {len(texts)}")
        print("=" * 70)

        vectors = []

        for start in range(
            0,
            len(texts),
            settings.EMBEDDING_BATCH_SIZE,
        ):

            batch = texts[
                start:start + settings.EMBEDDING_BATCH_SIZE
            ]

            batch_vectors = await self.provider.embeddings(
                input=batch,
                model=settings.DEFAULT_EMBEDDING_MODEL,
            )

            vectors.extend(batch_vectors)

        print(f"Generated {len(vectors)} embeddings.")

        return vectors
import asyncio
import numpy as np

from backend.services.embedding_service import EmbeddingService


def cosine(a, b):
    a = np.array(a)
    b = np.array(b)
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))


async def main():

    texts = [
        "Hello world",
        "Artificial Intelligence",
        "Machine Learning",
    ]

    service = EmbeddingService()

    vectors = await service.embed(texts)

    print()

    print("Hello vs AI")
    print(cosine(vectors[0], vectors[1]))

    print()

    print("Hello vs ML")
    print(cosine(vectors[0], vectors[2]))

    print()

    print("AI vs ML")
    print(cosine(vectors[1], vectors[2]))

    print()

    print("Vector equality")

    print(vectors[0] == vectors[1])
    print(vectors[0] == vectors[2])
    print(vectors[1] == vectors[2])


asyncio.run(main())
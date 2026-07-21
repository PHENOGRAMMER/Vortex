import asyncio

from backend.services.retrieval_service import RetrievalService


async def main():

    service = RetrievalService()

    results = await service.retrieve(
        "What programming languages does Aryan know?"
    )

    print()

    print("=" * 70)
    print("RESULTS")
    print("=" * 70)

    for i, chunk in enumerate(results):

        print("=" * 70)
        print(f"Rank {i + 1}")

        print("Chunk Index:", chunk.index)
        print("Start:", chunk.start)
        print("End:", chunk.end)
        print()
        print(chunk.text)


asyncio.run(main())
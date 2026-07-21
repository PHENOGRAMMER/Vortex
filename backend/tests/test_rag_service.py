import asyncio

from backend.services.rag_service import RAGService


async def main():

    service = RAGService()

    prompt = await service.build_prompt(

        "What programming languages does Aryan know?"

    )

    print()

    print("=" * 80)

    print(prompt)

    print("=" * 80)


asyncio.run(main())
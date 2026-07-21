import asyncio

from backend.models.document import Document
from backend.services.indexing_service import IndexingService


async def main():

    service = IndexingService()

    document = Document(

        id="1",

        filename="resume.pdf",

        content="""
Python
FastAPI
Machine Learning
LangChain
Vector Databases
Large Language Models
""" * 200,

        metadata={},
    )

    store = await service.index_document(
        document
    )

    print()

    print("=" * 70)

    print("SUMMARY")

    print("=" * 70)

    print("Total Vectors:", store.size)


asyncio.run(main())
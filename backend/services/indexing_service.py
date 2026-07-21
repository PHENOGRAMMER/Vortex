from backend.services.embedding_service import EmbeddingService
from backend.services.storage import storage
from backend.services.heading_detector import HeadingDetector


class IndexingService:

    def __init__(self):

        print("Creating Embedding Service")

        self.embedder = EmbeddingService()

        print("Creating Storage Manager")

        self.storage = storage

        print("Indexing Service Ready.")

    async def index_document(
        self,
        document,
    ):

        print()
        print("=" * 70)
        print("INDEXING DOCUMENT")
        print(document.filename)
        print("=" * 70)

        ####################################################################
        # Use chunks produced during upload
        ####################################################################
        print("B")
        print("Before chunk()")
        chunks = document.metadata["chunk_objects"]
        print("After chunk()")
        print(f"Chunks : {len(chunks)}")

        print("Before Texts")
        texts = [
            chunk.text
            for chunk in chunks
        ]
        print("After Texts")

        print("Generating embeddings...")

        print("Before embeddings")
        embeddings = await self.embedder.embed(texts)
        print("After embeddings")

        print(f"Embeddings Returned : {len(embeddings)}")

        ####################################################################
        # Prepare metadata
        ####################################################################

        ids = []

        metadata = []

        for chunk in chunks:

            chunk_id = f"{document.id}_{chunk.index}"

            ids.append(chunk_id)

            metadata.append(
                {
                    "document_id": document.id,
                    "filename": document.filename,

                    "chunk_id": chunk_id,
                    "chunk_index": chunk.index,

                    "text": chunk.text,
                    "section": self._section_title(chunk.text),

                    "start": chunk.start,
                    "end": chunk.end,
                    "length": len(chunk.text),

                    "extension": document.metadata.get("extension"),
                    "path": document.metadata.get("path"),
                    "user_id": document.metadata.get("user_id"),
                    "session_id": document.metadata.get("session_id"),
                }
            )

        print("Adding vectors to StorageManager...")

        print("Before storage.add()")
        self.storage.add(
            ids=ids,
            vectors=embeddings,
            metadata=metadata,
        )
        print("After storage.add()")

        print("Storage complete.")
        print(f"Total vectors stored: {self.storage.size}")
        print("FAISS file:", self.storage.vector_store.index_file)
        print("Metadata file:", self.storage.vector_store.metadata_file)

        print("=" * 70)

        return self.storage

    async def reindex_documents(
        self,
        documents,
    ):
        ids = []
        metadata = []
        texts = []

        for document in documents:
            chunks = document.metadata.get("chunk_objects", [])
            for chunk in chunks:
                chunk_id = f"{document.id}_{chunk.index}"
                ids.append(chunk_id)
                texts.append(chunk.text)
                metadata.append(
                    {
                        "document_id": document.id,
                        "filename": document.filename,
                        "chunk_id": chunk_id,
                        "chunk_index": chunk.index,
                        "text": chunk.text,
                        "section": self._section_title(chunk.text),
                        "start": chunk.start,
                        "end": chunk.end,
                        "length": len(chunk.text),
                        "extension": document.metadata.get("extension"),
                        "path": document.metadata.get("path"),
                        "user_id": document.metadata.get("user_id"),
                        "session_id": document.metadata.get("session_id"),
                    }
                )

        embeddings = await self.embedder.embed(texts) if texts else []
        self.storage.replace_all(
            ids=ids,
            vectors=embeddings,
            metadata=metadata,
        )
        return self.storage

    @staticmethod
    def _section_title(text: str) -> str | None:
        first_line = (text or "").strip().splitlines()[0] if (text or "").strip() else ""
        if first_line and HeadingDetector.is_heading(first_line):
            return first_line
        return None

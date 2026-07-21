from backend.models.retrieved_chunk import RetrievedChunk
from backend.services.embedding_service import EmbeddingService
from backend.services.reranker import Reranker
from backend.services.storage import storage


shared_reranker = Reranker()


class RetrievalService:

    def __init__(self):

        self.embedder = EmbeddingService()
        self.reranker = shared_reranker
        self.storage = storage

        print("=" * 70)
        print("Storage Status")
        print("-" * 70)
        print("Vector Count  :", self.storage.size)
        print("Metadata Count:", len(self.storage.vector_store.metadata))
        print("FAISS File:", self.storage.vector_store.index_file)
        print("Metadata File:", self.storage.vector_store.metadata_file)
        print("=" * 70)

    ####################################################################
    # Context Expansion
    ####################################################################

    def expand_context(
        self,
        chunks: list[RetrievedChunk],
        window: int = 1,
    ) -> list[RetrievedChunk]:

        expanded = []
        seen = set()

        for chunk in chunks:

            neighbors = self.storage.get_neighbor_chunks(
                document_id=chunk.document_id,
                chunk_index=chunk.chunk_index,
                window=window,
            )

            for item in neighbors:

                key = (
                    item["document_id"],
                    item["chunk_index"],
                )

                if key in seen:
                    continue

                seen.add(key)

                expanded.append(
                    RetrievedChunk(
                        score=chunk.score,
                        document_id=item["document_id"],
                        filename=item["filename"],
                        chunk_id=item["chunk_id"],
                        chunk_index=item["chunk_index"],
                        text=item["text"],
                        start=item["start"],
                        end=item["end"],
                        length=item["length"],
                        section=item.get("section"),
                        source_start_chunk=item["chunk_index"],
                        source_end_chunk=item["chunk_index"],
                    )
                )

        expanded.sort(
            key=lambda x: (
                x.document_id,
                x.chunk_index,
            )
        )

        return expanded
    

    def merge_chunks(
        self,
        chunks: list[RetrievedChunk],
    ) -> list[RetrievedChunk]:
        
        if not chunks:
            return []
        
        merged = []

        current = chunks[0]
        current.source_start_chunk = current.chunk_index
        current.source_end_chunk = current.chunk_index
        
        for chunk in chunks[1:]:
            if (
                chunk.document_id ==current.document_id
                and chunk.chunk_index == (current.source_end_chunk or current.chunk_index) + 1
            ):
                current.text += "\n\n" + chunk.text
                current.end = chunk.end
                current.length = len(current.text)
                current.source_end_chunk = chunk.chunk_index

                current.score = max(
                    current.score,
                    chunk.score,
                )

            else:
                merged.append(current)
                current = chunk

        merged.append(current)

        return merged


    def select_chunks_for_expansion(
        self,
        chunks: list[RetrievedChunk],
        max_chunks: int = 2,
        relative_threshold: float = 0.90,
    ) -> list[RetrievedChunk]:

        if not chunks:
            return []

        best_score = chunks[0].score

        selected = []

        for chunk in chunks:

            if chunk.score >= best_score * relative_threshold:
                selected.append(chunk)

            if len(selected) >= max_chunks:
                break

        return selected


    ####################################################################
    # Retrieval
    ####################################################################

    async def retrieve(
        self,
        query: str,
        top_k: int = 20,
        document_ids: list[str] | None = None,
        filenames: list[str] | None = None,
        user_id: int | None = None,
        session_id: int | None = None,
    ) -> list[RetrievedChunk]:

        print()
        print("=" * 70)
        print("RETRIEVAL")
        print("=" * 70)
        print("Query:", query)
        print("=" * 70)

        ####################################################################
        # Embed Query
        ####################################################################

        embedding = await self.embedder.embed([query])

        if isinstance(embedding, list):
            embedding = embedding[0]

        ####################################################################
        # Hybrid Search
        ####################################################################

        candidate_count = (
            self.storage.size
            if document_ids or filenames or session_id is not None
            else max(top_k * 4, 20)
        )
        results = self.storage.search_hybrid(
            query=query,
            query_vector=embedding,
            # Retrieve a wider candidate set before applying ownership and document
            # filters, otherwise another user's high-scoring chunks could crowd out
            # the current user's documents.
            top_k=candidate_count,
        )

        if document_ids:
            allowed = set(document_ids)
            results = [
                item
                for item in results
                if item.get("document_id") in allowed
            ]

        if filenames:
            allowed_names = {name.lower() for name in filenames}
            results = [
                item
                for item in results
                if item.get("filename", "").lower() in allowed_names
            ]

        if user_id is not None:
            results = [item for item in results if item.get("user_id") == user_id]

        if session_id is not None:
            results = [item for item in results if item.get("session_id") == session_id]

        ####################################################################
        # Convert
        ####################################################################

        retrieved = []
        seen = set()

        for item in results:

            key = (
                item["document_id"],
                item["chunk_index"],
            )

            if key in seen:
                continue

            seen.add(key)

            retrieved.append(

                RetrievedChunk(

                    score=item["score"],

                    document_id=item["document_id"],

                    filename=item["filename"],

                    chunk_id=item["chunk_id"],

                    chunk_index=item["chunk_index"],

                    text=item["text"],

                    start=item["start"],

                    end=item["end"],

                    length=item["length"],

                    section=item.get("section"),

                )

            )

        print()
        print("=" * 70)
        print("HYBRID RESULTS")
        print("=" * 70)

        for chunk in retrieved:
            print(
                f"{chunk.score:.5f} | "
                f"{chunk.filename} | "
                f"Chunk {chunk.chunk_index}"
            )

        ####################################################################
        # Rerank
        ####################################################################

        reranked = self.reranker.rerank(
            query=query,
            chunks=retrieved,
            top_k=min(5, top_k),
        )

        print()
        print("=" * 70)
        print("RERANKED")
        print("=" * 70)

        for chunk in reranked:

            print(
                f"{chunk.score:.5f} | "
                f"{chunk.filename} | "
                f"Chunk {chunk.chunk_index}"
            )

        ####################################################################
        # Score Filter
        ####################################################################

        threshold = 0.05

        filtered = [

            chunk

            for chunk in reranked

            if chunk.score >= threshold

        ]
        if not filtered and reranked and (document_ids or filenames or session_id is not None):
            filtered = reranked[:1]

        print()
        print("=" * 70)
        print("AFTER SCORE FILTER")
        print("=" * 70)
        print(f"Threshold : {threshold}")
        print(f"Chunks     : {len(filtered)}")

        for chunk in filtered:

            print(
                f"{chunk.score:.5f} | "
                f"{chunk.filename} | "
                f"Chunk {chunk.chunk_index}"
            )

        ####################################################################
        # Select Best Chunks
        ####################################################################

        selected = self.select_chunks_for_expansion(
            filtered,
            max_chunks=3,
            relative_threshold=0.75,
        )

        print()
        print("=" * 70)
        print("SELECTED FOR EXPANSION")
        print("=" * 70)

        for chunk in selected:

            print(
                f"{chunk.score:.5f} | "
                f"{chunk.filename} | "
                f"Chunk {chunk.chunk_index}"
            )

        ####################################################################
        # Context Expansion
        ####################################################################

        expanded = self.expand_context(
            selected,
            window=2,
        )

        print()
        print("=" * 70)
        print("CONTEXT EXPANSION")
        print("=" * 70)
        print(f"Expanded to {len(expanded)} chunks")

        ####################################################################
        # Merge Adjacent Chunks
        ####################################################################

        merged = self.merge_chunks(expanded)

        print()
        print("=" * 70)
        print("MERGED CONTEXT")
        print("=" * 70)
        print(f"Merged into {len(merged)} chunks")

        for chunk in merged:

            print(
                f"{chunk.filename} | "
                f"Chunk {chunk.chunk_index} | "
                f"{len(chunk.text)} chars"
            )

        print("=" * 70)

        return merged

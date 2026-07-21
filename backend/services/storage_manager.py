from collections import defaultdict

from backend.configs.settings import settings
from backend.services.bm25_store import BM25Store
from backend.services.vector_store import VectorStore


class StorageManager:

    def __init__(self):

        self.vector_store = VectorStore(
            dimension=settings.EMBEDDING_DIMENSION,
        )

        self.bm25_store = BM25Store()

        # Build the BM25 index from any metadata already stored by FAISS
        self._rebuild_bm25()

    ####################################################################
    # Internal
    ####################################################################

    def _rebuild_bm25(self):

        self.bm25_store.build(
            self.vector_store.metadata
        )

    ####################################################################
    # Add
    ####################################################################

    def add(
        self,
        ids,
        vectors,
        metadata,
    ):

        self.vector_store.add(
            ids=ids,
            vectors=vectors,
            metadata=metadata,
        )

        self._rebuild_bm25()

    def replace_all(
        self,
        ids,
        vectors,
        metadata,
    ):
        self.vector_store.replace_all(
            ids=ids,
            vectors=vectors,
            metadata=metadata,
        )
        self._rebuild_bm25()

    ####################################################################
    # Dense Search (FAISS)
    ####################################################################

    def search_dense(
        self,
        query_vector,
        top_k=20,
    ):

        return self.vector_store.search(
            query_vector=query_vector,
            top_k=top_k,
        )

    ####################################################################
    # Keyword Search (BM25)
    ####################################################################

    def search_bm25(
        self,
        query,
        top_k=20,
    ):

        return self.bm25_store.search(
            query=query,
            top_k=top_k,
        )


    def search_hybrid(
            self,
            query: str,
            query_vector,
            top_k: int = 20,
            rrf_k: int = 60,
    ):
        dense_results = self.search_dense(
            query_vector = query_vector,
            top_k = top_k,
        )

        bm25_results = self.search_bm25(
            query=query,
            top_k=top_k,
        )

        fused_scores = defaultdict(float)

        fused_items = {}

        for rank, item in enumerate(dense_results):

            chunk_id = item["chunk_id"]
            
            fused_scores[chunk_id] +=1 / (rrf_k + rank + 1)

            fused_items[chunk_id] = item


        for rank, item in enumerate(bm25_results):

            chunk_id = item["chunk_id"]

            fused_scores[chunk_id] +=1 / (rrf_k + rank + 1)

            fused_items[chunk_id] = item

        ranked = sorted(
            fused_scores.items(),
            key = lambda x: x[1],
            reverse=True,
        )

        results = []

        for chunk_id, score in ranked[:top_k]:

            item = fused_items[chunk_id].copy()

            item["score"] = score

            results.append(item)

        return results
    ####################################################################
    # Statistics
    ####################################################################

    def get_neighbor_chunks(
            self,
            document_id: str,
            chunk_index: int,
            window: int = 1,
    ):
        return self.vector_store.get_neighbor_chunks(
            document_id=document_id,
            chunk_index=chunk_index,
            window=window,
        )

    @property
    def size(self):

        return self.vector_store.size

    ####################################################################
    # Reset
    ####################################################################

    def reset(self):

        self.vector_store.reset()

        self.bm25_store.reset()

import os
import numpy as np
from typing import List, Dict, Any

try:
    import faiss
except ImportError:
    faiss = None


def _missing_faiss_error():
    return ImportError(
        "FAISS is required for the RAG vector store. Install with 'pip install faiss-cpu' (or faiss-gpu)."
    )

class VectorStore:
    """Simple wrapper around a FAISS IndexFlatL2 for embedding storage.

    Embeddings are assumed to be 1‑D numpy arrays of dtype float32.
    Metadata is stored in a parallel list of dicts (in‑memory).
    The index is persisted to disk under `index_path`.
    """

    def __init__(self, dim: int, index_path: str = "omnigen/backend/rag/faiss_index"):
        if faiss is None:
            raise _missing_faiss_error()
        self.dim = dim
        self.index_path = index_path
        self.metadata: List[Dict[str, Any]] = []
        if os.path.exists(index_path + ".faiss"):
            self.index = faiss.read_index(index_path + ".faiss")
            # Load metadata if exists
            meta_path = index_path + "_meta.npy"
            if os.path.exists(meta_path):
                self.metadata = np.load(meta_path, allow_pickle=True).tolist()
        else:
            self.index = faiss.IndexFlatL2(dim)

    def add_vectors(self, ids: List[str], vectors: np.ndarray, metadata: List[Dict[str, Any]]):
        """Add a batch of vectors.

        - `ids` – list of document‑chunk identifiers (stored only in metadata).
        - `vectors` – np.ndarray of shape (n, dim).
        - `metadata` – list of dicts with keys like `doc_id`, `source`, `page`.
        """
        assert vectors.shape[0] == len(ids) == len(metadata)
        self.index.add(vectors.astype(np.float32))
        for i, meta in zip(ids, metadata):
            entry = {"id": i, **meta}
            self.metadata.append(entry)
        self._persist()

    def search(self, query_vec: np.ndarray, k: int = 5) -> List[Dict[str, Any]]:
        """Return top‑k nearest neighbours with their metadata.
        Result format: [{"id": ..., "score": ..., **metadata}, ...]
        """
        query_vec = np.asarray(query_vec, dtype=np.float32).reshape(1, -1)
        distances, indices = self.index.search(query_vec, k)
        results = []
        for dist, idx in zip(distances[0], indices[0]):
            if idx == -1:
                continue
            meta = self.metadata[idx]
            results.append({"id": meta["id"], "score": float(dist), **meta})
        return results

    def _persist(self):
        if faiss is None:
            raise _missing_faiss_error()
        os.makedirs(os.path.dirname(self.index_path), exist_ok=True)
        faiss.write_index(self.index, self.index_path + ".faiss")
        # Save metadata as numpy object array for simplicity
        np.save(self.index_path + "_meta.npy", np.array(self.metadata, dtype=object))

    def reset(self):
        """Clear the index and metadata (useful for tests)."""
        self.index = faiss.IndexFlatL2(self.dim)
        self.metadata = []
        self._persist()

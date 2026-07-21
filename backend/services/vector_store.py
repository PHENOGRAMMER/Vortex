from pathlib import Path
from typing import Any, Dict, List
import os

from backend.config import get_settings

import numpy as np

try:
    import faiss
except ImportError:
    faiss = None


class _NumpyIndex:
    def __init__(self, dimension: int):
        self.dimension = dimension
        self.vectors = np.empty((0, dimension), dtype=np.float32)

    @property
    def ntotal(self):
        return len(self.vectors)

    def add(self, vectors):
        self.vectors = np.vstack([self.vectors, vectors])

    def search(self, query, top_k):
        if self.ntotal == 0:
            return np.array([[]]), np.array([[]], dtype=int)
        scores = np.dot(self.vectors, query[0])
        order = np.argsort(scores)[::-1][:top_k]
        return np.array([scores[order]]), np.array([order])


def _new_index(dimension: int):
    if faiss is not None:
        return faiss.IndexFlatIP(dimension)
    return _NumpyIndex(dimension)


def _normalize(vectors):
    if faiss is not None:
        faiss.normalize_L2(vectors)
        return
    norms = np.linalg.norm(vectors, axis=1, keepdims=True)
    norms[norms == 0] = 1
    vectors /= norms


class VectorStore:
    """
    FAISS-backed vector store.

    Responsibilities
    ----------------
    • Store embeddings
    • Persist index to disk
    • Store metadata
    • Retrieve nearest neighbours
    """

    def __init__(
        self,
        dimension: int,
        index_path: str | None = None,
    ):

        self.dimension = dimension

        if index_path is None:
            index_path = str(get_settings().data_dir / "vector_store")

        self.index_path = Path(index_path).resolve()

        self.index_file = self.index_path.with_suffix(".faiss")

        self.metadata_file = (
            self.index_path.parent
            / f"{self.index_path.name}_metadata.npy"
        )

        self.index_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        self.metadata: List[Dict[str, Any]] = []

        print()
        print("=" * 70)
        print("VECTOR STORE INITIALIZED")
        print("=" * 70)
        print("cwd            :", os.getcwd())
        print("index path     :", self.index_path)
        print("faiss file     :", self.index_file)
        print("metadata file  :", self.metadata_file)
        print("faiss exists   :", self.index_file.exists())
        print("metadata exists:", self.metadata_file.exists())
        print("=" * 70)

        self._load()

    ####################################################################
    # Load
    ####################################################################

    def _load(self):

        print("Loading Vector Store...")

        if self.index_file.exists() and faiss is not None:

            print("Loading existing FAISS index...")

            self.index = faiss.read_index(
                str(self.index_file)
            )

            if self.metadata_file.exists():

                self.metadata = np.load(
                    self.metadata_file,
                    allow_pickle=True,
                ).tolist()

            print()
            print("=" * 70)
            print("VECTOR STORE LOADED")
            print("=" * 70)
            print("Vectors :", self.index.ntotal)
            print("Metadata:", len(self.metadata))
            print("=" * 70)

        else:

            print("Creating new Vector Index...")

            self.index = _new_index(self.dimension)

            if self.metadata_file.exists():
                self.metadata = np.load(
                    self.metadata_file,
                    allow_pickle=True,
                ).tolist()

    ####################################################################
    # Save
    ####################################################################

    def _save(self):

        print()
        print("=" * 70)
        print("SAVING VECTOR STORE")
        print("=" * 70)
        print("Vectors :", self.index.ntotal)
        print("Metadata:", len(self.metadata))

        if faiss is not None:
            faiss.write_index(
                self.index,
                str(self.index_file),
            )
            print("FAISS index written.")
        else:
            print("FAISS unavailable; vectors kept in memory only.")

        np.save(
            self.metadata_file,
            np.array(
                self.metadata,
                dtype=object,
            ),
        )

        print("Metadata written.")

        print("FAISS exists   :", self.index_file.exists())
        print("Metadata exists:", self.metadata_file.exists())

        print("=" * 70)

    ####################################################################
    # Add
    ####################################################################

    def add(
        self,
        ids: List[str],
        vectors: List[List[float]],
        metadata: List[Dict[str, Any]],
    ):

        print()
        print("=" * 70)
        print("ADDING VECTORS")
        print("=" * 70)

        vectors = np.asarray(
            vectors,
            dtype=np.float32,
        )

        _normalize(vectors)

        print("Before add :", self.index.ntotal)

        self.index.add(vectors)

        print("After add  :", self.index.ntotal)

        for vector_id, meta in zip(ids, metadata):

            self.metadata.append(
                {
                    "id": vector_id,
                    **meta,
                }
            )

        print("Metadata size:", len(self.metadata))

        self._save()

        print("Vector Store Save Complete.")

    def replace_all(
        self,
        ids: List[str],
        vectors: List[List[float]],
        metadata: List[Dict[str, Any]],
    ):
        self.index = _new_index(self.dimension)
        self.metadata.clear()
        if vectors:
            self.add(ids=ids, vectors=vectors, metadata=metadata)
        else:
            self._save()

    ####################################################################
    # Search
    ####################################################################

    def search(
        self,
        query_vector: List[float],
        top_k: int = 5,
    ) -> List[Dict[str, Any]]:

        print()
        print("=" * 70)
        print("FAISS SEARCH")
        print("=" * 70)
        print("Vectors in index:", self.index.ntotal)
        print("Metadata count  :", len(self.metadata))
        print("=" * 70)

        if self.index.ntotal == 0:
            print("Vector store is empty.")
            return []

        query = np.asarray(
            query_vector,
            dtype=np.float32,
        ).reshape(1, -1)

        _normalize(query)

        scores, indices = self.index.search(
            query,
            top_k,
        )

        results = []

        for score, index in zip(
            scores[0],
            indices[0],
        ):

            if index == -1:
                continue

            results.append(
                {
                    "score": float(score),
                    **self.metadata[index],
                }
            )

        print(f"Returned {len(results)} results.")

        return results

    ####################################################################
    # Neighbor chunks
    ####################################################################

    def get_neighbor_chunks(
        self,
        document_id: str,
        chunk_index: int,
        window: int = 1,
    ):

        neighbors = []

        start = chunk_index - window
        end = chunk_index + window

        for item in self.metadata:

            if item["document_id"] != document_id:
                continue

            idx = item["chunk_index"]

            if start <= idx <= end:
                neighbors.append(item)

        neighbors.sort(
            key=lambda x: x["chunk_index"]
        )

        return neighbors

    ####################################################################
    # Reset
    ####################################################################

    def reset(self):

        print("Resetting Vector Store...")

        self.index = _new_index(self.dimension)

        self.metadata.clear()

        self._save()

    ####################################################################
    # Helpers
    ####################################################################

    @property
    def size(self):

        return self.index.ntotal

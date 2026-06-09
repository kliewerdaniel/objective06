"""FAISS adapter — vector database for semantic retrieval."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np

try:
    import faiss
except ImportError:
    faiss = None  # type: ignore[assignment]


class FAISSAdapter:
    def __init__(self, index_path: str, dimension: int = 768) -> None:
        self._index_path = index_path
        self._dimension = dimension
        self._index: Any = None
        Path(index_path).parent.mkdir(parents=True, exist_ok=True)
        self._load_or_create()

    def _load_or_create(self) -> None:
        if faiss is None:
            return
        path = Path(self._index_path)
        if path.exists():
            self._index = faiss.read_index(str(path))
        else:
            self._index = faiss.IndexFlatL2(self._dimension)

    def insert(self, vector: list[float], id: str) -> None:
        if faiss is None or self._index is None:
            return
        arr = np.array([vector], dtype=np.float32)
        self._index.add(arr)

    def search(self, vector: list[float], k: int = 10) -> list[dict[str, Any]]:
        if faiss is None or self._index is None:
            return []
        arr = np.array([vector], dtype=np.float32)
        distances, indices = self._index.search(arr, k)
        results = []
        for dist, idx in zip(distances[0], indices[0]):
            if idx >= 0:
                score = 1.0 / (1.0 + float(dist))
                results.append({"index": int(idx), "distance": float(dist), "score": score})
        return results

    def save(self) -> None:
        if faiss is None or self._index is None:
            return
        faiss.write_index(self._index, str(self._index_path))

    @property
    def size(self) -> int:
        return self._index.ntotal if self._index is not None else 0

    def close(self) -> None:
        self.save()

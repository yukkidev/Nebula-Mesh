from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable


def _ensure_vector_dim(vector: list[float]) -> None:
    if not vector:
        raise ValueError("vector must not be empty")


@dataclass(frozen=True)
class VectorMemoryConfig:
    persist_directory: str
    collection_name: str = "processed_memories"


class VectorMemoryRepository:
    """Chroma-backed vector repository for VPS.

    Note: Chroma is synchronous; we wrap it in async-compatible methods.
    """

    def __init__(self, *, config: VectorMemoryConfig) -> None:
        import chromadb

        self._client = chromadb.PersistentClient(path=config.persist_directory)
        self._collection = self._client.get_or_create_collection(config.collection_name)

    async def save_vector(
        self, id: str, vector: list[float], metadata: dict[str, Any]
    ) -> None:
        _ensure_vector_dim(vector)

        self._collection.upsert(
            ids=[id],
            embeddings=[vector],
            metadatas=[metadata],
        )

    async def retrieve_vectors(
        self, ids: list[str]
    ) -> tuple[list[list[float]], list[dict[str, Any]]]:
        res = self._collection.get(ids=ids)
        embeddings = [list(e) for e in (res.get("embeddings") or [])]
        metadatas = list(res.get("metadatas") or [])
        return embeddings, metadatas

    async def delete_vector(self, id: str) -> bool:
        try:
            self._collection.delete(ids=[id])
            return True
        except Exception:
            return False

    async def search_similar(
        self, query_vector: list[float], *, limit: int = 5
    ) -> list[dict[str, Any]]:
        _ensure_vector_dim(query_vector)
        res = self._collection.query(
            query_embeddings=[query_vector],
            n_results=limit,
        )
        return list(res.get("metadatas") or [])

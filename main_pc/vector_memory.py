from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any


def _ensure_vector_dim(vector: list[float]) -> None:
    if vector is None or len(vector) == 0:
        raise ValueError("vector must not be empty")


def _serialize_metadata(metadata: dict[str, Any]) -> dict[str, str]:
    """Serialize metadata for ChromaDB - all values must be str, int, float, or bool."""
    result = {}
    for k, v in metadata.items():
        if isinstance(v, (str, int, float, bool)):
            result[k] = v
        else:
            result[k] = json.dumps(v)
    return result


@dataclass(frozen=True)
class VectorMemoryConfig:
    persist_directory: str
    collection_name: str = "processed_memories"


class VectorMemoryRepository:
    """Chroma-backed vector repository for Main PC.

    This is the canonical storage location for processed thoughts.
    VPS acts as temporary buffer only.
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
            metadatas=[_serialize_metadata(metadata)],
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
        metadatas = res.get("metadatas") or []
        if metadatas and isinstance(metadatas[0], list):
            return metadatas[0]
        return metadatas

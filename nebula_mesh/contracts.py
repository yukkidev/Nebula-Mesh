from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Protocol, TypedDict


@dataclass(frozen=True)
class ClassificationResult:
    categories: list[dict[str, Any]]
    todos: list[dict[str, Any]]
    importance: int


class ClassificationStrategy(Protocol):
    async def classify(self, text: str) -> list[dict[str, Any]]: ...
    async def extract_todos(self, text: str) -> list[dict[str, Any]]: ...
    async def rate_importance(self, text: str) -> int: ...

    def __call__(self, text: str) -> ClassificationResult: ...


class ClassificationEngine:
    def __init__(self, strategy: ClassificationStrategy):
        self._strategy = strategy

    async def process(self, text: str) -> ClassificationResult:
        categories = await self._strategy.classify(text)
        todos = await self._strategy.extract_todos(text)
        importance = await self._strategy.rate_importance(text)
        return ClassificationResult(
            categories=categories, todos=todos, importance=importance
        )


class SyncManager(Protocol):
    async def poll_pending(self) -> list["PendingItem"]: ...
    async def push_processed(self, items: list["ProcessedItem"]) -> None: ...
    async def clear_buffer(self) -> bool: ...


class StorageBackend(Protocol):
    async def save_vector(
        self, id: str, vector: list[float], metadata: dict[str, Any]
    ) -> None: ...


class PendingItem(TypedDict):
    id: str
    text: str
    timestamp: str


class ProcessedItem(TypedDict):
    id: str
    categories: list[dict[str, Any]]
    todos: list[dict[str, Any]]
    importance: int

from __future__ import annotations

import asyncio
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Optional
import uuid

from nebula_mesh.contracts import (
    ClassificationEngine,
    ProcessedItem,
    PendingItem,
    SyncManager,
    StorageBackend,
)


@dataclass(frozen=True)
class SyncConfig:
    vps_target: str = "vps"
    poll_interval_seconds: float = 5.0
    max_items_per_poll: int = 20


class SyncDaemon:
    """Process items fetched from a SyncManager.

    MVP simplification:
    - SyncManager provides pending items as dicts, not just IDs.
    - StorageBackend stores vectors as float lists (no numpy requirement).
    """

    def __init__(
        self,
        *,
        sync_manager: SyncManager,
        engine: ClassificationEngine,
        storage: StorageBackend,
        config: SyncConfig = SyncConfig(),
    ) -> None:
        self._sync_manager = sync_manager
        self._engine = engine
        self._storage = storage
        self._config = config
        self._running = False
        self._task: Optional[asyncio.Task[None]] = None

    async def start(self) -> None:
        if self._running:
            return
        self._running = True
        self._task = asyncio.create_task(self._run_loop())

    async def stop(self) -> None:
        self._running = False
        if self._task is not None:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass

    async def run_once(self) -> int:
        """Process one batch of pending items."""
        pending = await self._sync_manager.poll_pending()
        if not pending:
            return 0

        processed_count = 0
        for item in pending[: self._config.max_items_per_poll]:
            await self._process_item(item)
            processed_count += 1

        return processed_count

    async def _run_loop(self) -> None:
        while self._running:
            try:
                await self.run_once()
            finally:
                await asyncio.sleep(self._config.poll_interval_seconds)

    async def _process_item(self, item: PendingItem) -> None:
        item_id = str(item["id"])
        text = str(item["text"])

        result = await self._engine.process(text)

        # MVP embedding: deterministic pseudo-vector based on content length.
        # This keeps the architecture intact without pulling in embedding deps.
        dim = 32
        seed = (len(text) % 997) + result.importance
        vector = [(seed * (i + 1)) % 1000 / 1000.0 for i in range(dim)]

        metadata: dict[str, Any] = {
            "id": item_id,
            "timestamp": datetime.utcnow().isoformat(),
            "categories": result.categories,
            "todos": result.todos,
            "importance": result.importance,
        }
        await self._storage.save_vector(item_id, vector, metadata)
        processed: ProcessedItem = {
            "id": item_id,
            "categories": result.categories,
            "todos": result.todos,
            "importance": result.importance,
        }
        await self._sync_manager.push_processed([processed])
        await self._sync_manager.clear_buffer()


class HTTPPollingSyncManager(SyncManager):
    """SyncManager that polls a VPS over HTTP.

    MVP expectations on VPS:
    - GET /get_pending returns list of PendingItem dicts
    - POST /vectors/upsert is handled by the caller (StorageBackend)
    - clear_buffer is a no-op (VPS dequeue_all already clears)
    """

    def __init__(self, *, vps_base_url: str, timeout_seconds: float = 5.0) -> None:
        self._vps_base_url = vps_base_url.rstrip("/")
        self._timeout_seconds = timeout_seconds

    async def poll_pending(self) -> list[PendingItem]:
        import asyncio
        import requests

        def _get() -> list[PendingItem]:
            r = requests.get(
                f"{self._vps_base_url}/get_pending", timeout=self._timeout_seconds
            )
            r.raise_for_status()
            return r.json()

        return await asyncio.to_thread(_get)

    async def push_processed(self, items: list[ProcessedItem]) -> None:
        # MVP: VPS doesn't store processed items; SyncDaemon already cleared buffer.
        return None

    async def clear_buffer(self) -> bool:
        return True

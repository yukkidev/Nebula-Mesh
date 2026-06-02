from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any

from fastapi import FastAPI
from pydantic import BaseModel

from nebula_mesh.contracts import SyncManager
from vps.pending_queue import PendingSyncQueue
from vps.pii_firewall import PIFirewall
from vps.vector_memory import VectorMemoryConfig, VectorMemoryRepository


class IngestRequest(BaseModel):
    text: str


class VectorUpsertRequest(BaseModel):
    id: str
    vector: list[float]
    metadata: dict[str, Any]


@dataclass(frozen=True)
class QueueItem:
    id: str
    text: str
    timestamp: str


class SQLiteSyncManager(SyncManager):
    def __init__(self, queue: PendingSyncQueue) -> None:
        self._queue = queue

    async def poll_pending(self) -> list[dict[str, Any]]:
        # Kept as dict for FastAPI/Pydantic compatibility; contract is enforced by SyncDaemon tests.
        items = self._queue.dequeue_all()
        return [{"id": i.id, "text": i.text, "timestamp": i.timestamp} for i in items]

    async def push_processed(self, items: list[dict[str, Any]]) -> None:
        # For MVP, processed items are not stored on VPS.
        # The queue is cleared by dequeue_all + clear_buffer in SyncDaemon.
        return None

    async def clear_buffer(self) -> bool:
        # Since we dequeue_all() we are already cleared; keep contract.
        return True

    def enqueue_text(self, text: str) -> str:
        return self._queue.enqueue(text)

    def pending_count(self) -> int:
        return self._queue.size()


def build_app(
    *,
    queue_db_path: str = "./vps_data/pending_sync.db",
    vector_persist_dir: str | None = None,
) -> FastAPI:
    queue = PendingSyncQueue(queue_db_path)
    sync_manager = SQLiteSyncManager(queue)
    pii = PIFirewall()

    vector_persist_dir = vector_persist_dir or "./vps_data/chroma_db"
    vector_repo = VectorMemoryRepository(
        config=VectorMemoryConfig(
            persist_directory=vector_persist_dir, collection_name="processed_memories"
        )
    )

    app = FastAPI(title="Nebula Mesh - VPS")

    @app.get("/get_pending")
    async def get_pending() -> list[dict[str, Any]]:
        return await sync_manager.poll_pending()

    @app.post("/ingest")
    async def ingest(req: IngestRequest) -> dict[str, Any]:
        clean = pii.strip_pii(req.text)
        item_id = sync_manager.enqueue_text(clean)
        return {"status": "queued", "id": item_id}

    @app.get("/status")
    async def status() -> dict[str, Any]:
        return {
            "vps_online": True,
            "pending_count": sync_manager.pending_count(),
            "last_sync": datetime.utcnow().isoformat(),
        }

    @app.post("/vectors/upsert")
    async def upsert_vector(req: VectorUpsertRequest) -> dict[str, Any]:
        await vector_repo.save_vector(req.id, req.vector, req.metadata)
        return {"status": "ok", "id": req.id}

    return app

from __future__ import annotations

import asyncio
import tempfile
from dataclasses import dataclass


@dataclass
class MockSyncManager:
    pending: list
    cleared: bool = False

    async def poll_pending(self):
        items = self.pending
        self.pending = []
        return items

    async def push_processed(self, items):
        pass

    async def clear_buffer(self):
        self.cleared = True
        return True


@dataclass
class MockStorage:
    saved: list

    async def save_vector(self, id, vector, metadata):
        self.saved.append((id, vector, metadata))


def test_sync_daemon_processes_pending_items():
    from main_pc.sync_daemon import SyncDaemon, SyncConfig
    from nebula_mesh.contracts import ClassificationEngine, PendingItem

    class DummyStrategy:
        async def classify(self, text):
            return [{"category": "test"}]

        async def extract_todos(self, text):
            return []

        async def rate_importance(self, text):
            return 5

    manager = MockSyncManager(
        pending=[{"id": "item-1", "text": "hello", "timestamp": "2024-01-01"}]
    )
    engine = ClassificationEngine(strategy=DummyStrategy())
    storage = MockStorage(saved=[])

    config = SyncConfig(poll_interval_seconds=0.1)
    daemon = SyncDaemon(
        sync_manager=manager, engine=engine, storage=storage, config=config
    )

    count = asyncio.run(daemon.run_once())

    assert count == 1
    assert len(storage.saved) == 1
    assert storage.saved[0][0] == "item-1"


def test_sync_daemon_empty_queue_returns_zero():
    from main_pc.sync_daemon import SyncDaemon, SyncConfig
    from nebula_mesh.contracts import ClassificationEngine

    class DummyStrategy:
        async def classify(self, text):
            return []

        async def extract_todos(self, text):
            return []

        async def rate_importance(self, text):
            return 5

    manager = MockSyncManager(pending=[])
    engine = ClassificationEngine(strategy=DummyStrategy())
    storage = MockStorage(saved=[])

    config = SyncConfig()
    daemon = SyncDaemon(
        sync_manager=manager, engine=engine, storage=storage, config=config
    )

    count = asyncio.run(daemon.run_once())

    assert count == 0


def test_sync_daemon_respects_max_per_poll():
    from main_pc.sync_daemon import SyncDaemon, SyncConfig
    from nebula_mesh.contracts import ClassificationEngine

    class DummyStrategy:
        async def classify(self, text):
            return []

        async def extract_todos(self, text):
            return []

        async def rate_importance(self, text):
            return 5

    manager = MockSyncManager(
        pending=[
            {"id": f"item-{i}", "text": f"text{i}", "timestamp": "2024-01-01"}
            for i in range(10)
        ]
    )
    engine = ClassificationEngine(strategy=DummyStrategy())
    storage = MockStorage(saved=[])

    config = SyncConfig(max_items_per_poll=3)
    daemon = SyncDaemon(
        sync_manager=manager, engine=engine, storage=storage, config=config
    )

    count = asyncio.run(daemon.run_once())

    assert count == 3
    assert len(storage.saved) == 3


def test_sync_daemon_start_stop():
    from main_pc.sync_daemon import SyncDaemon, SyncConfig
    from nebula_mesh.contracts import ClassificationEngine

    class DummyStrategy:
        async def classify(self, text):
            return []

        async def extract_todos(self, text):
            return []

        async def rate_importance(self, text):
            return 5

    manager = MockSyncManager(pending=[])
    engine = ClassificationEngine(strategy=DummyStrategy())
    storage = MockStorage(saved=[])

    config = SyncConfig(poll_interval_seconds=0.05)
    daemon = SyncDaemon(
        sync_manager=manager, engine=engine, storage=storage, config=config
    )

    asyncio.run(daemon.start())
    asyncio.run(asyncio.sleep(0.15))
    asyncio.run(daemon.stop())

    assert daemon._running is False

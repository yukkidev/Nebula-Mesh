import asyncio


class FakeStorage:
    def __init__(self) -> None:
        self.saved: list[tuple[str, list[float], dict]] = []

    async def save_vector(self, id: str, vector: list[float], metadata: dict):
        self.saved.append((id, vector, metadata))


class FakeSyncManager:
    def __init__(self) -> None:
        self.pending = [
            {"id": "1", "text": "urgent note\n- buy milk"},
            {"id": "2", "text": "a task\n* call mom"},
        ]
        self.pushed: list[list[dict]] = []
        self.cleared = 0

    async def poll_pending(self):
        return list(self.pending)

    async def push_processed(self, items):
        self.pushed.append(items)

    async def clear_buffer(self) -> bool:
        self.cleared += 1
        return True


def test_sync_daemon_run_once_processes_all():
    from main_pc.sync_daemon import SyncDaemon
    from main_pc.strategy import BasicHeuristicStrategy
    from nebula_mesh.contracts import ClassificationEngine

    engine = ClassificationEngine(strategy=BasicHeuristicStrategy())
    sync = FakeSyncManager()
    storage = FakeStorage()

    daemon = SyncDaemon(sync_manager=sync, engine=engine, storage=storage)

    processed = asyncio.run(daemon.run_once())
    assert processed == 2
    assert len(storage.saved) == 2
    assert len(sync.pushed) == 2
    assert sync.cleared == 2

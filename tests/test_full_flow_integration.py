from __future__ import annotations

import asyncio
import tempfile


def test_full_flow_mobile_to_vps_to_main_pc():
    """Test complete flow: mobile -> VPS buffer -> Main PC -> ChromaDB"""
    from fastapi.testclient import TestClient

    with tempfile.TemporaryDirectory() as td:
        vps_db = f"{td}/vps_pending.db"
        vps_app_dir = f"{td}/vps_chroma"
        pc_chroma_dir = f"{td}/pc_chroma"

        from vps.api import build_app as build_vps_app

        vps_app = build_vps_app(queue_db_path=vps_db, vector_persist_dir=vps_app_dir)
        vps_client = TestClient(vps_app)

        resp = vps_client.post(
            "/ingest", json={"text": "call john@example.com about the project"}
        )
        assert resp.status_code == 200
        assert resp.json()["status"] == "queued"
        item_id = resp.json()["id"]

        pending = vps_client.get("/get_pending")
        assert len(pending.json()) == 1
        assert "[EMAIL]" in pending.json()[0]["text"]

        from main_pc.app import build_app as build_pc_app
        from main_pc.vector_memory import VectorMemoryConfig, VectorMemoryRepository
        from main_pc.strategy import BasicHeuristicStrategy
        from nebula_mesh.contracts import ClassificationEngine

        pc_app = build_pc_app()
        engine = ClassificationEngine(strategy=BasicHeuristicStrategy())

        result = asyncio.run(engine.process("call john about the project"))
        assert result.categories[0]["category"] == "notes"

        vec_repo = VectorMemoryRepository(
            config=VectorMemoryConfig(persist_directory=pc_chroma_dir)
        )
        vector = [0.1] * 32
        metadata = {
            "text": "call john about the project",
            "importance": result.importance,
        }
        asyncio.run(vec_repo.save_vector(item_id, vector, metadata))

        results = asyncio.run(vec_repo.search_similar(vector, limit=5))
        assert len(results) == 1
        assert results[0]["importance"] == 5


def test_vps_pending_queue_thread_safety():
    """Test that pending queue handles concurrent access."""
    import threading
    from vps.pending_queue import PendingSyncQueue

    with tempfile.TemporaryDirectory() as td:
        db_path = f"{td}/queue.db"
        queue = PendingSyncQueue(db_path=db_path)

        def add_items(start, count):
            for i in range(start, start + count):
                queue.enqueue(f"item-{i}")

        threads = [
            threading.Thread(target=add_items, args=(0, 10)),
            threading.Thread(target=add_items, args=(10, 10)),
            threading.Thread(target=add_items, args=(20, 10)),
        ]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert queue.size() == 30


def test_mobile_client_routes_to_pc_when_online(monkeypatch):
    """Test mobile client routes directly to PC when available."""
    from mobile_client import server as s
    from mobile_client.config import MobileConfig

    health_called = False
    pc_called = False

    def fake_get(url, timeout):
        nonlocal health_called
        if "health" in url:
            health_called = True

            class R:
                status_code = 200

            return R()

        class R:
            status_code = 200

            def json(self):
                return {
                    "status": "ingested",
                    "categories": [],
                    "todos": [],
                    "importance": 5,
                }

        return R()

    def fake_post(url, json, timeout):
        nonlocal pc_called
        pc_called = True

        class R:
            ok = True

            def json(self):
                return {
                    "status": "ingested",
                    "categories": [],
                    "todos": [],
                    "importance": 5,
                }

        return R()

    monkeypatch.setattr("requests.get", fake_get)
    monkeypatch.setattr("requests.post", fake_post)

    app = s.MobileInputServer(config=MobileConfig())._app

    from flask import testing

    client = app.test_client()
    resp = client.post("/api/submit", json={"text": "test thought"})

    assert resp.status_code == 200
    body = resp.get_json()
    assert body["target"] == "pc"
    assert health_called
    assert pc_called


def test_mobile_client_fallback_to_vps_when_pc_offline(monkeypatch):
    """Test mobile client falls back to VPS when PC unreachable."""
    from mobile_client import server as s
    from mobile_client.config import MobileConfig

    vps_called = False

    def fake_get(url, timeout):
        class R:
            status_code = 500

        return R()

    def fake_post(url, json, timeout):
        nonlocal vps_called
        if "vps" in url:
            vps_called = True

        class R:
            ok = True

            def json(self):
                return {"status": "queued", "id": "x"}

        return R()

    monkeypatch.setattr("requests.get", fake_get)
    monkeypatch.setattr("requests.post", fake_post)

    app = s.MobileInputServer(config=MobileConfig())._app

    client = app.test_client()
    resp = client.post("/api/submit", json={"text": "test thought"})

    assert resp.status_code == 200
    body = resp.get_json()
    assert body["target"] == "vps"
    assert vps_called

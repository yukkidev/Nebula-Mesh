import tempfile


def test_vps_api_ingest_get_pending_status():
    import asyncio
    from fastapi.testclient import TestClient

    from vps.api import build_app

    with tempfile.TemporaryDirectory() as td:
        db_path = f"{td}/pending.db"
        app = build_app(queue_db_path=db_path)
        client = TestClient(app)

        resp = client.post("/ingest", json={"text": "contact a@b.com\n- todo"})
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "queued"
        assert data["id"]

        status = client.get("/status")
        assert status.status_code == 200
        assert status.json()["pending_count"] == 1

        pending = client.get("/get_pending")
        assert pending.status_code == 200
        items = pending.json()
        assert len(items) == 1
        assert "[EMAIL]" in items[0]["text"]

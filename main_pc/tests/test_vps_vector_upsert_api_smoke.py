def test_vps_vector_upsert_endpoint():
    import tempfile

    from fastapi.testclient import TestClient

    from vps.api import build_app

    with tempfile.TemporaryDirectory() as td:
        app = build_app(
            queue_db_path=f"{td}/pending.db", vector_persist_dir=f"{td}/chroma"
        )
        client = TestClient(app)

        resp = client.post(
            "/vectors/upsert",
            json={
                "id": "v1",
                "vector": [0.1] * 32,
                "metadata": {"importance": 5, "title": "x"},
            },
        )
        assert resp.status_code == 200
        assert resp.json()["status"] == "ok"

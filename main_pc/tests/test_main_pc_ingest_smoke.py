def test_main_pc_ingest_returns_classification(monkeypatch):
    import asyncio

    from main_pc.app import build_app
    from main_pc.strategy import BasicHeuristicStrategy
    from nebula_mesh.contracts import ClassificationEngine

    # Monkeypatch engine used in build_app by replacing build_default_engine.
    import main_pc.app as appmod

    def fake_build_default_engine():
        return ClassificationEngine(strategy=BasicHeuristicStrategy())

    monkeypatch.setattr(appmod, "build_default_engine", fake_build_default_engine)

    app = build_app()
    client = app.test_client()
    resp = client.post("/ingest", json={"text": "urgent thing\n- buy milk"})
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["status"] == "ingested"
    assert data["importance"] == 10
    assert data["todos"][0]["task"] == "buy milk"

def test_mobile_uses_vps_ingest_when_pc_health_fails(monkeypatch):
    from mobile_client.server import MobileInputServer, MobileConfig

    calls = {"vps": 0, "pc": 0, "health": 0}

    def fake_get(url, timeout):
        calls["health"] += 1

        class R:
            status_code = 503

        return R()

    def fake_post(url, json, timeout):
        if "vps" in url:
            calls["vps"] += 1
        else:
            calls["pc"] += 1

        class R:
            ok = True

            def json(self):
                return {"status": "queued", "id": "id1"}

        return R()

    import mobile_client.server as s

    monkeypatch.setattr(s.requests, "get", fake_get)
    monkeypatch.setattr(s.requests, "post", fake_post)

    app = MobileInputServer(
        config=MobileConfig(
            pc_url="http://pc", vps_url="http://vps", timeout_seconds=5.0, port=8002
        )
    )._app
    client = app.test_client()
    resp = client.post("/api/submit", json={"text": "hello"})
    assert resp.status_code == 200
    assert resp.get_json()["target"] == "vps"
    assert calls["vps"] == 1
    assert calls["pc"] == 0

import json


def test_input_routes_to_vps_when_pc_offline(monkeypatch):
    from input_client import server as s

    calls = {"vps": 0, "pc": 0, "health": 0}

    def fake_get(url, timeout):
        calls["health"] += 1

        # PC offline
        class R:
            status_code = 500

        return R()

    def fake_post(url, json, timeout):
        if "vps" in url:
            calls["vps"] += 1
        else:
            calls["pc"] += 1

        class R:
            ok = True

            def json(self):
                return {"status": "queued", "id": "x"}

        return R()

    monkeypatch.setattr(s.requests, "get", fake_get)
    monkeypatch.setattr(s.requests, "post", fake_post)

    app = s.InputServer(
        config=s.InputConfig(pc_url="http://pc", vps_url="http://vps")
    )._app

    client = app.test_client()
    resp = client.post(
        "/api/submit",
        data=json.dumps({"text": "hello"}),
        content_type="application/json",
    )
    assert resp.status_code == 200
    body = resp.get_json()
    assert body["target"] == "vps"
    assert calls["vps"] == 1
    assert calls["pc"] == 0

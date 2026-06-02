def test_dashboard_status_offline_mock(monkeypatch):
    import rpi3_dashboard.dashboard as d

    class Boom(Exception):
        pass

    def fake_get(*args, **kwargs):
        raise Boom("nope")

    monkeypatch.setattr(d.requests, "get", fake_get)

    srv = d.DashboardServer(
        config=d.DashboardConfig(vps_url="http://example.invalid", port=0)
    )
    out = srv._get_status()
    assert out["vps_online"] is False

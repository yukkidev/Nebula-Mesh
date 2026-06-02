import asyncio
import sys


def test_http_polling_sync_manager_calls_vps_get_pending(monkeypatch):
    from main_pc.sync_daemon import HTTPPollingSyncManager

    class FakeResponse:
        def raise_for_status(self):
            return None

        def json(self):
            return [{"id": "1", "text": "hi", "timestamp": "t"}]

    def fake_get(url, timeout):
        assert url.endswith("/get_pending")
        return FakeResponse()

    monkeypatch.setattr("requests.get", fake_get)

    mgr = HTTPPollingSyncManager(vps_base_url="http://vps")
    pending = asyncio.run(mgr.poll_pending())
    assert pending[0]["id"] == "1"

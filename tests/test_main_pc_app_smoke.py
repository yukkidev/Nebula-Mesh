import main_pc.app as app


def test_health_contract():
    assert app.health() == {"ok": True}

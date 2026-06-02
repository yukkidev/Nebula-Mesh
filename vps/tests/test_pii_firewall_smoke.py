def test_pii_firewall_redacts():
    from vps.pii_firewall import PIFirewall

    text = "email me test@example.com or call 415-555-2671"
    out = PIFirewall.strip_pii(text)
    assert "test@example.com" not in out
    assert "415-555-2671" not in out
    assert "[EMAIL]" in out
    assert "[PHONE]" in out

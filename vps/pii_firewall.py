from __future__ import annotations

import re


class PIFirewall:
    """PII redaction before forwarding to cloud/other services."""

    _EMAIL_RE = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b")
    _PHONE_RE = re.compile(
        r"\+?1?\s*[-.]?\s*\(?[0-9]{3}\)?\s*[-.]?[0-9]{3}\s*[-.]?[0-9]{4}"
    )

    @classmethod
    def strip_pii(cls, text: str) -> str:
        text = cls._EMAIL_RE.sub("[EMAIL]", text)
        text = cls._PHONE_RE.sub("[PHONE]", text)
        return text

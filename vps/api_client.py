from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import requests


@dataclass(frozen=True)
class VPSClient:
    base_url: str
    timeout_seconds: float = 5.0

    def post_vector_upsert(
        self, *, id: str, vector: list[float], metadata: dict[str, Any]
    ) -> dict[str, Any]:
        r = requests.post(
            f"{self.base_url}/vectors/upsert",
            json={"id": id, "vector": vector, "metadata": metadata},
            timeout=self.timeout_seconds,
        )
        r.raise_for_status()
        return r.json()

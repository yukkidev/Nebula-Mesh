from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class InputConfig:
    pc_url: str = "http://main-pc.local:8001"
    vps_url: str = "http://vps.local:8000"
    timeout_seconds: float = 5.0
    port: int = 8002


def load_config() -> InputConfig:
    return InputConfig(
        pc_url=os.environ.get("PIM_PC_URL", "http://main-pc.local:8001"),
        vps_url=os.environ.get("PIM_VPS_URL", "http://vps.local:8000"),
        timeout_seconds=float(os.environ.get("PIM_HTTP_TIMEOUT", "5")),
        port=int(os.environ.get("PIM_INPUT_PORT", "8002")),
    )

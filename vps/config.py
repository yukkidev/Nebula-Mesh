from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class VPSConfig:
    queue_db_path: str
    vector_persist_dir: str
    port: int


def load_config() -> VPSConfig:
    return VPSConfig(
        queue_db_path=os.environ.get("PIM_VPS_QUEUE_DB", "./vps_data/pending_sync.db"),
        vector_persist_dir=os.environ.get("PIM_VPS_CHROMA_DIR", "./vps_data/chroma_db"),
        port=int(os.environ.get("VPS_PORT", "8000")),
    )

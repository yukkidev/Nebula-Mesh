from __future__ import annotations

import uvicorn

from vps.api import build_app
from vps.config import load_config


def main() -> None:
    cfg = load_config()
    uvicorn.run(
        build_app(
            queue_db_path=cfg.queue_db_path, vector_persist_dir=cfg.vector_persist_dir
        ),
        host="0.0.0.0",
        port=cfg.port,
    )


if __name__ == "__main__":
    main()

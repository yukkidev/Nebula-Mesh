from __future__ import annotations

import asyncio
import os

from main_pc.app import build_app, build_default_engine
from main_pc.sync_daemon import SyncConfig, SyncDaemon


async def main_async() -> None:
    # Start Flask app in a background thread by using the built-in dev server.
    # MVP: we run SyncDaemon in-process; Flask runs in a separate thread via Werkzeug.
    app = build_app()
    port = int(os.environ.get("PIM_PC_PORT", "8001"))

    import threading

    def _run_flask() -> None:
        app.run(host="0.0.0.0", port=port, debug=False, use_reloader=False)

    t = threading.Thread(target=_run_flask, daemon=True)
    t.start()

    # Wire SyncDaemon -> VPS over HTTP (no shared mount).
    from main_pc.sync_daemon import HTTPPollingSyncManager
    from main_pc.vector_memory import VectorMemoryConfig, VectorMemoryRepository

    vps_url = os.environ.get("PIM_VPS_URL")
    if not vps_url:
        await asyncio.Event().wait()
        return

    sync_manager = HTTPPollingSyncManager(vps_base_url=vps_url)

    # Vector storage: ChromaDB on Main PC
    chroma_dir = os.environ.get("PIM_CHROMA_PERSIST_DIR", "./chroma_db")
    engine = build_default_engine()
    storage = VectorMemoryRepository(
        config=VectorMemoryConfig(
            persist_directory=chroma_dir, collection_name="processed_memories"
        )
    )

    daemon = SyncDaemon(
        sync_manager=sync_manager,
        engine=engine,
        storage=storage,
        config=SyncConfig(
            poll_interval_seconds=float(os.environ.get("PIM_SYNC_INTERVAL", "5"))
        ),
    )
    await daemon.start()
    await asyncio.Event().wait()


def main() -> None:
    asyncio.run(main_async())


if __name__ == "__main__":
    main()

"""Migrate processed Chroma DB from Main PC to VPS.

MVP implementation: copy Chroma persistent directory contents.

Chroma stores a SQLite DB + index files inside the persistent directory.
We keep this intentionally simple and local-file based.
"""

from __future__ import annotations

import os
from pathlib import Path
import shutil


def main() -> None:
    src = Path(
        os.environ.get(
            "PIM_CHROMA_SRC",
            "/home/aspen/Documents/ai_companion_memory/memory_db/chroma_db",
        )
    )
    dest = Path(os.environ.get("PIM_CHROMA_DEST", "./vps_data/chroma_db"))

    if not src.exists():
        raise SystemExit(f"Source chroma directory not found: {src}")

    dest.mkdir(parents=True, exist_ok=True)

    # Copy all files (sqlite + index) into destination.
    for p in src.iterdir():
        if p.is_file():
            shutil.copy2(p, dest / p.name)

    print(f"Copied chroma files from {src} -> {dest}")


if __name__ == "__main__":
    main()

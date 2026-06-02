from __future__ import annotations

import sqlite3
import threading
from dataclasses import dataclass
from datetime import datetime
from typing import Any
import uuid


@dataclass(frozen=True)
class PendingItem:
    id: str
    text: str
    timestamp: str


class PendingSyncQueue:
    """Thread-safe SQLite-backed queue."""

    def __init__(self, db_path: str) -> None:
        self._db_path = db_path
        self._lock = threading.Lock()
        self._create_tables()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self._db_path, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        return conn

    def _create_tables(self) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS pending_sync (
                    id TEXT PRIMARY KEY,
                    text TEXT NOT NULL,
                    timestamp TEXT NOT NULL
                )
                """
            )
            conn.commit()

    def enqueue(self, text: str, *, item_id: str | None = None) -> str:
        item_id = item_id or str(uuid.uuid4())
        now = datetime.utcnow().isoformat()
        with self._lock:
            with self._connect() as conn:
                conn.execute(
                    "INSERT OR REPLACE INTO pending_sync (id, text, timestamp) VALUES (?, ?, ?)",
                    (item_id, text, now),
                )
                conn.commit()
        return item_id

    def dequeue_all(self) -> list[PendingItem]:
        with self._lock:
            with self._connect() as conn:
                conn.execute("BEGIN IMMEDIATE")
                cur = conn.execute(
                    "SELECT id, text, timestamp FROM pending_sync ORDER BY timestamp"
                )
                rows = cur.fetchall()
                if rows:
                    conn.execute("DELETE FROM pending_sync")
                    conn.commit()

        return [
            PendingItem(id=r["id"], text=r["text"], timestamp=r["timestamp"])
            for r in rows
        ]

    def size(self) -> int:
        with self._lock:
            with self._connect() as conn:
                row = conn.execute("SELECT COUNT(*) AS c FROM pending_sync").fetchone()
                return int(row["c"])

from __future__ import annotations

import tempfile


def test_pending_queue_enqueue_dequeue_all():
    from vps.pending_queue import PendingSyncQueue

    with tempfile.TemporaryDirectory() as td:
        db_path = f"{td}/queue.db"
        q = PendingSyncQueue(db_path=db_path)

        id1 = q.enqueue("hello")
        id2 = q.enqueue("world", item_id="fixed")
        assert q.size() == 2

        items = q.dequeue_all()
        assert {i.id for i in items} == {id1, "fixed"}
        assert q.size() == 0

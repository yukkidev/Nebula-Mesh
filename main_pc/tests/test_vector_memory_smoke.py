from __future__ import annotations

import asyncio
import tempfile


def test_vector_memory_save_and_search():
    """Test that we can save and search for vectors."""
    from main_pc.vector_memory import VectorMemoryConfig, VectorMemoryRepository

    with tempfile.TemporaryDirectory() as td:
        config = VectorMemoryConfig(persist_directory=td, collection_name="test")
        repo = VectorMemoryRepository(config=config)

        v1 = [0.0] * 32
        v2 = [0.1] * 32

        asyncio.run(repo.save_vector("note-1", v1, {"text": "first note", "cat": "a"}))
        asyncio.run(repo.save_vector("note-2", v2, {"text": "second note", "cat": "b"}))

        results = asyncio.run(repo.search_similar([0.05] * 32, limit=2))

        assert len(results) == 2
        assert results[0]["cat"] in {"a", "b"}


def test_vector_memory_delete():
    """Test that delete removes vector and it won't be found in search."""
    from main_pc.vector_memory import VectorMemoryConfig, VectorMemoryRepository

    with tempfile.TemporaryDirectory() as td:
        config = VectorMemoryConfig(persist_directory=td, collection_name="test")
        repo = VectorMemoryRepository(config=config)

        vector = [0.1] * 32
        asyncio.run(repo.save_vector("note-1", vector, {"text": "test"}))

        result = asyncio.run(repo.delete_vector("note-1"))
        assert result is True

        results = asyncio.run(repo.search_similar(vector, limit=5))
        assert len(results) == 0


def test_vector_memory_empty_vector_rejected():
    """Test that empty vectors are rejected."""
    from main_pc.vector_memory import VectorMemoryConfig, VectorMemoryRepository

    with tempfile.TemporaryDirectory() as td:
        config = VectorMemoryConfig(persist_directory=td, collection_name="test")
        repo = VectorMemoryRepository(config=config)

        try:
            asyncio.run(repo.save_vector("note-1", [], {}))
            assert False, "Should have raised"
        except ValueError:
            pass


def test_vector_memory_none_rejected():
    """Test that None vectors are rejected."""
    from main_pc.vector_memory import VectorMemoryConfig, VectorMemoryRepository

    with tempfile.TemporaryDirectory() as td:
        config = VectorMemoryConfig(persist_directory=td, collection_name="test")
        repo = VectorMemoryRepository(config=config)

        try:
            asyncio.run(repo.save_vector("note-1", None, {}))
            assert False, "Should have raised"
        except ValueError:
            pass

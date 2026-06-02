from __future__ import annotations

from typing import Any

from nebula_mesh.contracts import ClassificationStrategy


class BasicHeuristicStrategy(ClassificationStrategy):
    """Simplest possible strategy to enable testing without external LLMs."""

    async def classify(self, text: str) -> list[dict[str, Any]]:
        # Very lightweight categorization.
        lower = text.lower()
        if "todo" in lower or "task" in lower:
            return [{"category": "tasks", "description": "User indicated tasks"}]
        return [{"category": "notes", "description": "Default note category"}]

    async def extract_todos(self, text: str) -> list[dict[str, Any]]:
        # MVP: treat lines starting with "-" or "*" as todo-like.
        todos: list[dict[str, Any]] = []
        for line in text.splitlines():
            s = line.strip()
            if s.startswith(("-", "*")) and len(s) > 2:
                todos.append({"task": s[1:].strip()})
        return todos

    async def rate_importance(self, text: str) -> int:
        lower = text.lower()
        if "urgent" in lower or "asap" in lower:
            return 10
        if "important" in lower:
            return 8
        return 5

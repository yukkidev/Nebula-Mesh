from __future__ import annotations

import os
from typing import Any

from nebula_mesh.contracts import ClassificationEngine

from flask import Flask, jsonify, request


def build_app() -> Flask:
    app = Flask(__name__)

    engine = build_default_engine()

    @app.get("/health")
    def health_route():
        return jsonify(health())

    @app.post("/ingest")
    def ingest_route():
        payload = request.get_json(force=True) or {}
        text = str(payload.get("text") or "")
        if not text.strip():
            return jsonify({"status": "error", "error": "empty text"}), 400

        # MVP: run classification directly and return the result.
        # Future phase will route into SyncDaemon/storage pipeline.
        import asyncio

        result = asyncio.run(engine.process(text))
        return jsonify(
            {
                "status": "ingested",
                "categories": result.categories,
                "todos": result.todos,
                "importance": result.importance,
            }
        )

    return app


def build_default_engine() -> ClassificationEngine:
    """Build a default ClassificationEngine.

    This project runs in multiple environments; for now we provide a minimal
    strategy that does not require external services.
    """

    from main_pc.strategy import BasicHeuristicStrategy

    return ClassificationEngine(strategy=BasicHeuristicStrategy())


def health() -> dict[str, Any]:
    return {"ok": True}


def main() -> None:
    # Main PC Flask server for MVP.
    app = build_app()
    port = int(os.environ.get("PIM_PC_PORT", "8001"))
    app.run(host="0.0.0.0", port=port, debug=False)


if __name__ == "__main__":
    main()

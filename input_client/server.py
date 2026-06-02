from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any

import requests
from flask import Flask, jsonify, request


from input_client.config import InputConfig


class InputServer:
    def __init__(self, *, config: MobileConfig) -> None:
        self._config = config
        self._app = Flask(__name__)

        @self._app.get("/health")
        def health():
            return jsonify({"ok": True})

        @self._app.post("/api/submit")
        def submit():
            payload = request.get_json(force=True) or {}
            text = str(payload.get("text") or "")
            if not text.strip():
                return jsonify({"status": "error", "error": "empty text"}), 400

            # Routing strategy: if PC is reachable, send to PC; else buffer on VPS.
            if self._is_pc_online():
                # Future phase: PC will accept /ingest. For MVP, we return status.
                r = requests.post(
                    f"{self._config.pc_url}/ingest",
                    json={"text": text},
                    timeout=self._config.timeout_seconds,
                )
                return jsonify(
                    {
                        "status": "submitted",
                        "target": "pc",
                        "pc_response": r.json() if r.ok else None,
                    }
                )

            r = requests.post(
                f"{self._config.vps_url}/ingest",
                json={"text": text},
                timeout=self._config.timeout_seconds,
            )
            return jsonify(
                {
                    "status": "submitted",
                    "target": "vps",
                    "vps_response": r.json() if r.ok else None,
                }
            )

    def _is_pc_online(self) -> bool:
        try:
            r = requests.get(
                f"{self._config.pc_url}/health", timeout=self._config.timeout_seconds
            )
            return r.status_code == 200
        except Exception:
            return False

    def start(self) -> None:
        self._app.run(
            host="0.0.0.0",
            port=int(os.environ.get("PIM_INPUT_PORT", "8002")),
            debug=False,
        )


def build_app() -> Flask:
    cfg = MobileConfig(
        pc_url=os.environ.get("PIM_PC_URL", "http://main-pc.local:8001"),
        vps_url=os.environ.get("PIM_VPS_URL", "http://vps.local:8000"),
    )
    return InputServer(config=cfg)._app

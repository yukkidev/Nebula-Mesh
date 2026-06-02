from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any

import requests
from flask import Flask, jsonify, render_template_string


DASHBOARD_TEMPLATE = """<!DOCTYPE html>
<html>
<head>
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <style>
    body { font-family: monospace; background: #0a0a0a; color: #0f0; padding: 20px; }
    .status-online { color: #0f0; }
    .status-offline { color: #f33; }
    h1 { font-size: 18px; border-bottom: 1px solid #0f0; padding-bottom: 5px; }
    .metric { margin: 10px 0; }
    label { display: inline-block; width: 120px; }
  </style>
</head>
<body>
  <h1>PIM Status</h1>
  <div class="metric">
    <label>VPS Online:</label>
    <span id="vps-status" class="status-offline">Checking...</span>
  </div>
  <div class="metric">
    <label>Pending Items:</label>
    <span id="pending-count">0</span>
  </div>
  <div class="metric">
    <label>Last Sync:</label>
    <span id="last-sync">--:--:--</span>
  </div>
  <script>
    async function updateStatus() {
      try {
        const r = await fetch('/status');
        const data = await r.json();
        document.getElementById('vps-status').className =
          data.vps_online ? 'status-online' : 'status-offline';
        document.getElementById('vps-status').textContent =
          data.vps_online ? 'ONLINE' : 'OFFLINE';
        document.getElementById('pending-count').textContent =
          data.pending_count ?? 0;
        document.getElementById('last-sync').textContent =
          data.last_sync ? new Date(data.last_sync).toLocaleTimeString() : '--:--:--';
      } catch (e) {
        document.getElementById('vps-status').className = 'status-offline';
        document.getElementById('vps-status').textContent = 'OFFLINE';
      }
    }
    setInterval(updateStatus, 5000);
    updateStatus();
  </script>
</body>
</html>"""


@dataclass(frozen=True)
class DashboardConfig:
    vps_url: str
    port: int = 5000


class DashboardServer:
    def __init__(self, *, config: DashboardConfig) -> None:
        self._config = config
        self._app = Flask(__name__)

        @self._app.route("/")
        def dashboard():
            return render_template_string(DASHBOARD_TEMPLATE)

        @self._app.route("/status")
        def status():
            return jsonify(self._get_status())

    def _get_status(self) -> dict[str, Any]:
        try:
            r = requests.get(f"{self._config.vps_url}/status", timeout=5)
            r.raise_for_status()
            data = r.json()
            return {
                "vps_online": True,
                "pending_count": data.get("pending_count", 0),
                "last_sync": data.get("last_sync") or datetime.utcnow().isoformat(),
            }
        except Exception:
            return {"vps_online": False}

    def start(self) -> None:
        self._app.run(host="0.0.0.0", port=self._config.port, debug=False)

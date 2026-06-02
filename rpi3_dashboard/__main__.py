from __future__ import annotations

import os

from rpi3_dashboard.dashboard import DashboardConfig, DashboardServer


def main() -> None:
    vps_url = os.environ.get("PIM_VPS_URL", "http://vps.local:8000")
    port = int(os.environ.get("PIM_RPI_PORT", "5000"))
    DashboardServer(config=DashboardConfig(vps_url=vps_url, port=port)).start()


if __name__ == "__main__":
    main()

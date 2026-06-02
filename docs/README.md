# Nebula Mesh Setup (Per Device)

This repo is structured by device type:
- `main_pc/` (Brain / classification + processing)
- `vps/` (Buffer/Proxy + shared persistence)
- `rpi3_dashboard/` (Status display)
- `input_client/` (Input router for laptops/Python-capable machines)

The implementation is intentionally MVP-first: each component has a small surface area and is testable.

## Prerequisites

- Python 3.11+
- `git`
- Linux host for each Python component (Windows/macOS are possible but untested)
- Network connectivity over Tailscale (recommended)

## Environment Variables

Each device reads the following common environment variables:

- `PIM_VPS_URL` (VPS base URL, e.g. `http://vps.local:8000`)
- `PIM_PC_URL` (PC base URL, e.g. `http://main-pc.local:8001`)

See each device section for component-specific variables.

## Local Development

From repo root:

1. Create virtualenv (if not already):
   - `.venv/` is expected
2. Install dev deps:
   - `pip install -e ".[dev]"`
3. Run tests:
   - `pytest`

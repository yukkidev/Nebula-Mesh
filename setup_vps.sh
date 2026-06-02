#!/usr/bin/env bash
set -euo pipefail

python3 -m venv .venv
source .venv/bin/activate

pip install -U pip setuptools wheel
pip install -e "."
pip install fastapi uvicorn pydantic-settings flask requests chromadb

echo "VPS setup complete. Run: (see docs/vps.md)"

#!/usr/bin/env bash
set -euo pipefail

python3 -m venv .venv
source .venv/bin/activate

pip install -U pip setuptools wheel
pip install -e "."
pip install flask requests

echo "RPi dashboard setup complete. Run: .venv/bin/python -m rpi3_dashboard"

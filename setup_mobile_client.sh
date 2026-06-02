#!/usr/bin/env bash
set -euo pipefail

python3 -m venv .venv
source .venv/bin/activate

pip install -U pip setuptools wheel
pip install -e "."
pip install flask requests

echo "Mobile client setup complete. Run: .venv/bin/python -m mobile_client"

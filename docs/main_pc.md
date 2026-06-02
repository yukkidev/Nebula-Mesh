# Main PC Setup (Brain)

## 1) Install

From the `main_pc` repo checkout directory (or repo root):

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e "../" 
pip install flask requests
```

## 2) Configure

```bash
export PIM_PC_PORT=8001
export PIM_VPS_URL=http://vps.local:8000
```

## 3) Run

```bash
.venv/bin/python -m main_pc
```

Endpoints (MVP):
- `GET /health`
- `POST /ingest`

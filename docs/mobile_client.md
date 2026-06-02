# Mobile/Input Client Setup

## 1) Install

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e "../"
pip install flask requests
```

## 2) Configure

```bash
export PIM_PC_URL=http://main-pc.local:8001
export PIM_VPS_URL=http://vps.local:8000
export PIM_MOBILE_PORT=8002
```

## 3) Run

```bash
.venv/bin/python -m mobile_client
```

Endpoints:
- `POST /api/submit`
- `GET /health`

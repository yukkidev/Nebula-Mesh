# Input Client Setup

The input client is a gateway for laptops and other Python-capable machines. It routes submissions to the Main PC when online, or falls back to the VPS buffer.

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
export PIM_INPUT_PORT=8002
```

## 3) Run

```bash
.venv/bin/python -m input_client
```

Endpoints:
- `POST /api/submit`
- `GET /health`

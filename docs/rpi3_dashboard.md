# RPi 3 Dashboard Setup

## 1) Install

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e "../"
pip install flask requests
```

## 2) Configure

```bash
export PIM_VPS_URL=http://vps.local:8000
export PIM_RPI_PORT=5000
```

## 3) Run

```bash
.venv/bin/python -m rpi3_dashboard
```

Endpoints:
- `GET /` dashboard HTML
- `GET /status` (proxy to VPS)

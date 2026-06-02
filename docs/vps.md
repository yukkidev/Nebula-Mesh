# VPS Setup (Buffer & Proxy)

## 1) Install

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e "../"
pip install fastapi uvicorn pydantic-settings flask chromadb
```

## 2) Configure

```bash
export VPS_PORT=8000
```

## 3) Run

Start the server (MVP):

```bash
.venv/bin/python -c "from vps.api import build_app; import uvicorn; uvicorn.run(build_app(), host='0.0.0.0', port=int(__import__('os').environ.get('VPS_PORT','8000')) )"
```

Endpoints:
- `POST /ingest`
- `GET /get_pending`
- `GET /status`
- `POST /vectors/upsert` (processed-memory vector ingestion)

# Personal Intelligence Mesh - Architecture Design

**MVP-first**: Simple, functional, minimal dependencies.

## System Flow

```
Phone/Laptop → Mobile Client → VPS (buffer) → Main PC (process) → ChromaDB (storage)
                                              ↑
                                          RPi Dashboard (display)
```

## Components

| Component | Location | Framework | Purpose |
|-----------|----------|-----------|---------|
| InputClient | input_client/ | Flask | Routes input to PC (if online) or VPS (fallback) |
| VPS | vps/ | FastAPI | Temporary buffer, PII stripping, SQLite queue |
| MainPC | main_pc/ | Flask + asyncio | Classification, ChromaDB storage |
| Dashboard | rpi3_dashboard/ | Flask | Status display (polls VPS) |

## Data Flow Details

1. User submits thought via input_client
2. input_client checks if PC is reachable (health check)
3. If PC online → POST to PC `/ingest`
4. If PC offline → POST to VPS `/ingest` (queued in SQLite)
5. SyncDaemon polls VPS `/get_pending` every 5 seconds
6. For each pending item: classify → embed → store in ChromaDB
7. VPS queue cleared after processing

## Configuration

All components read from environment variables:

- `PIM_VPS_URL` - VPS base URL (default: `http://vps.local:8000`)
- `PIM_PC_URL` - Main PC base URL (default: `http://main-pc.local:8001`)
- `PIM_CHROMA_PERSIST_DIR` - ChromaDB directory (default: `./chroma_db`)
- `PIM_SYNC_INTERVAL` - Sync polling interval (default: `5` seconds)

## Ports

- VPS: 8000
- Main PC: 8001
- Mobile Client: 8002
- RPi Dashboard: 5000
# Nebula Mesh

A distributed thought-capture and classification system with a cloud VPS acting as a durable buffer between any number of local clients and a central processing PC.

## Overview

Nebula Mesh solves a simple problem: capture thoughts from any device, at any time, and reliably sync them to a single machine for classification, embedding, and long-term vector storage. A cloud VPS sits in the middle as a temporary buffer so submissions never fail, even when your main PC is offline.

```
Phone/Laptop → Mobile Client → VPS (buffer) → Main PC (process) → ChromaDB (storage)
                                              ↑
                                          RPi Dashboard (display)
```

## Architecture

| Component | Framework | Port | Purpose |
|-----------|-----------|------|---------|
| **Main PC** | Flask + ChromaDB | 8001 | Classification, vector embedding, long-term storage |
| **VPS** | FastAPI + SQLite | 8000 | Temporary queue buffer, PII stripping, vector backup |
| **Mobile Client** | Flask | 8002 | Input gateway with smart routing (PC-first, VPS-fallback) |
| **RPi Dashboard** | Flask | 5000 | Live status display (polls VPS) |

## Data Flow

1. User submits text via the Mobile Client (`/api/submit`).
2. The client checks if the Main PC is reachable (`/health`).
3. If the PC is online, the text is sent directly to the PC's `/ingest` endpoint.
4. If the PC is offline, the text is buffered on the VPS (`/ingest`), which strips PII and queues it in SQLite.
5. A `SyncDaemon` on the Main PC polls the VPS (`/get_pending`) every few seconds.
6. For each pending item: classify, embed, and store in ChromaDB.
7. The VPS queue is cleared after processing.

## Core Functions

### Classification Engine (`main_pc/`)
- **`ClassificationEngine.process(text)`** — Runs a configurable strategy to categorize input, extract todos, and rate importance.
- **`BasicHeuristicStrategy`** — Lightweight default strategy (no external LLM required). Categorizes by keywords, extracts dash/asterisk-bulleted lines as todos, and rates importance by keyword presence.
- Strategies implement the `ClassificationStrategy` protocol, so they can be swapped at runtime (e.g., to call an LLM).

### Vector Memory (`main_pc/vector_memory.py`, `vps/vector_memory.py`)
- **`VectorMemoryRepository.save_vector(id, vector, metadata)`** — Upsert a vector with metadata into ChromaDB.
- **`VectorMemoryRepository.retrieve_vectors(ids)`** — Fetch vectors and metadata by ID.
- **`VectorMemoryRepository.search_similar(query_vector, limit)`** — Find the closest vectors in embedding space.
- **`VectorMemoryRepository.delete_vector(id)`** — Remove a vector by ID.

### VPS Buffer (`vps/`)
- **`PendingSyncQueue`** — Thread-safe SQLite queue. Items are enqueued on submission and dequeued in bulk by the SyncDaemon.
- **`PIFirewall.strip_pii(text)`** — Regex-based redaction of email addresses and phone numbers before data leaves the VPS.
- **`SQLiteSyncManager`** — Bridges the queue to the `SyncManager` protocol.

### Mobile Client (`mobile_client/`)
- **`MobileInputServer`** — Flask app that routes submissions to the Main PC when it is reachable, otherwise falls back to the VPS buffer.

### Sync Daemon (`main_pc/sync_daemon.py`)
- **`SyncDaemon`** — Async loop that polls the VPS for pending items, processes each through the classification engine, generates a deterministic pseudo-vector, and stores results in ChromaDB.
- **`HTTPPollingSyncManager`** — HTTP implementation of the `SyncManager` protocol for the Main PC.

### RPi Dashboard (`rpi3_dashboard/`)
- **`DashboardServer`** — Serves a minimal status page showing VPS reachability, pending item count, and last sync time. Polls the VPS `/status` endpoint every 5 seconds.

## Configuration

All components read configuration from environment variables:

| Variable | Default | Description |
|----------|---------|-------------|
| `PIM_VPS_URL` | `http://vps.local:8000` | VPS base URL |
| `PIM_PC_URL` | `http://main-pc.local:8001` | Main PC base URL |
| `PIM_PC_PORT` | `8001` | Main PC listen port |
| `PIM_MOBILE_PORT` | `8002` | Mobile client listen port |
| `PIM_RPI_PORT` | `5000` | RPi dashboard listen port |
| `VPS_PORT` | `8000` | VPS listen port |
| `PIM_VPS_QUEUE_DB` | `./vps_data/pending_sync.db` | SQLite queue path |
| `PIM_VPS_CHROMA_DIR` | `./vps_data/chroma_db` | VPS ChromaDB directory |
| `PIM_CHROMA_PERSIST_DIR` | `./chroma_db` | Main PC ChromaDB directory |
| `PIM_SYNC_INTERVAL` | `5` | Seconds between sync polls |
| `PIM_HTTP_TIMEOUT` | `5` | HTTP request timeout |

## Setup

Each component has a setup script:

```bash
bash setup_main_pc.sh
bash setup_vps.sh
bash setup_mobile_client.sh
bash setup_rpi3_dashboard.sh
```

Each script creates a virtualenv, installs the package in editable mode, and installs component-specific dependencies.

## Running

```bash
# Main PC
python -m main_pc

# VPS
python -m vps

# Mobile Client
python -m mobile_client

# RPi Dashboard
python -m rpi3_dashboard
```

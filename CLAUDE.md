# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This repository contains the design and (eventually) implementation for **Nebula Mesh** (Personal Intelligence Mesh) - a distributed thought-capture and classification system with git-based deployment across multiple devices.

## Architecture Summary

The system consists of 4 device types, each with distinct responsibilities:

| Device | Role | Tech Stack |
|--------|------|------------|
| **Main PC** | The Brain | Python + Ollama + ChromaDB |
| **VPS** | Buffer & Proxy | Python + FastAPI + SQLite |
| **RPi 3** | Display | Python + Flask |
| **Laptop/Phone** | Input | React/Vue + Tailscale |

## Key Design Patterns

- **Strategy Pattern** - `ClassificationEngine` swaps classification strategies at runtime
- **Repository Pattern** - `VectorMemoryRepository` abstracts ChromaDB operations
- **Observer Pattern** - `HealthMonitor` interfaces for cross-device status callbacks
- **Factory Pattern** - `StrategyFactory` creates classification strategies

## Core Components

- `ClassificationEngine` - Processes thoughts, extracts todos, rates importance
- `VectorMemoryRepository` - Vector storage/retrieval with ChromaDB
- `SyncDaemon` - Polls VPS for pending items, processes them, pushes backup
- `FastAPIServer` - VPS REST API (`/get_pending`, `/ingest`, `/status`)
- `PendingSyncQueue` - Thread-safe SQLite queue for sync items
- `PIFirewall` - Strips PII before forwarding to cloud services
- `DashboardServer` - RPi status display
- `MobileClient` - Input client with routing logic (PC if online, VPS otherwise)
- `TailscaleManager` - Device discovery and connectivity management
- `UpdateManager` - Git-based deployment orchestrator

## Repository Structure (Planned)

```
main_pc/           # Classification engine, vector memory, sync daemon
vps/               # FastAPI server, pending sync queue, PII firewall
rpi3_dashboard/    # Flask status dashboard
mobile_client/     # React/Vue PWA input client
update_manager.py  # Deployment orchestration
```

## Development Notes

- All components designed for git-based deployment (`git clone --depth 1`)
- Tailscale used for mesh networking between devices
- See `design_document.md` for full class diagrams and implementation details

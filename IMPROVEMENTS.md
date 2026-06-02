# Known Limitations & Improvements

This document tracks what Nebula Mesh **is not** and what would need real work to make it production-ready.

## What It Is

A baseline system demonstrating the architecture for a distributed thought-capture pipeline with a cloud buffer and local processing. It is not a polished application.

## Current Limitations

### Input

- **Single note only.** Every endpoint accepts one `{"text": "..."}` at a time. No batch submission.
- **No rich input.** Plain text only. No markdown, tags, categories, or attachments.
- **No web UI.** Users must construct raw HTTP requests or build their own frontends.
- **No authentication.** Anyone who can reach the endpoints can submit or query data.
- **No rate limiting.** Nothing prevents abuse or accidental flooding of the queue.

### Processing

- **Heuristic-only classification.** The `BasicHeuristicStrategy` uses keyword matching. There is no LLM integration. Real classification would require swapping in an LLM-backed strategy.
- **Fake embeddings.** The `SyncDaemon` generates deterministic pseudo-vectors based on text length, not actual semantic embeddings. Real embeddings require an embedding model (e.g., `sentence-transformers`, OpenAI embeddings).
- **No deduplication.** The same thought submitted twice creates two entries.
- **No tagging or user-assigned metadata.** All metadata is auto-generated.

### Storage

- **ChromaDB only.** No support for other vector databases or storage backends.
- **No export.** No way to dump or migrate data out of ChromaDB.
- **No backup.** The VPS holds a temporary buffer only. If the Main PC dies before processing, data is lost after buffer clear.

### Sync

- **Polling only.** The `SyncDaemon` polls every N seconds. No webhooks, websockets, or push notifications.
- **No conflict resolution.** If two clients submit conflicting versions of the same thought, there is no merge strategy.
- **No delta sync.** Every poll fetches the full pending queue. No incremental sync.
- **No encryption in transit.** Assumes Tailscale or similar VPN handles transport security. No built-in TLS.

### Security

- **No auth on any endpoint.** `/ingest`, `/get_pending`, `/status` are all open.
- **Minimal PII stripping.** The `PIFirewall` only catches email addresses and US phone numbers via regex. No NER, no configurable rules.
- **No secrets management.** Environment variables are the only config mechanism.

### Frontend / UX

- **No web application.** The RPi dashboard is a status page only (VPS online, pending count, last sync). No thought browsing, search, or input form.
- **No mobile app.** The "input client" is a Flask server for laptops/Python-capable machines. Not a phone app.
- **No CLI tool.** No `nebula submit "my thought"` command-line interface.

### Operations

- **No logging.** Components print nothing to stdout beyond default Flask/uvicorn access logs.
- **No metrics.** No Prometheus, StatsD, or similar.
- **No alerting.** If the VPS goes down or the sync daemon stalls, nobody is notified.
- **No deployment automation.** Setup scripts create virtualenvs and install deps. No systemd units, Docker, or process management.
- **No configuration validation.** Missing environment variables silently use defaults or fail at runtime.

### Code Quality

- **`asyncio.run()` in request handlers.** `main_pc/app.py` calls `asyncio.run()` per request, creating a new event loop each time. Not suitable for production.
- **No retry logic.** If the VPS is temporarily unreachable, the sync daemon just skips that cycle. No exponential backoff.
- **No circuit breakers.** Repeated failures to the VPS or PC are not throttled.
- **No proper error responses.** Most errors return generic 500s or are swallowed.
- **MVP type hints.** Some `dict[str, Any]` where typed dataclasses or Pydantic models would be safer.

## What Would Make It Useful

1. **Batch ingestion endpoint** — `POST /ingest` should accept a list of notes.
2. **Web UI** — A simple frontend for submitting thoughts, browsing stored entries, and viewing status.
3. **CLI tool** — `nebula submit`, `nebula search`, `nebula status` commands.
4. **Real embeddings** — Integrate `sentence-transformers` or an embedding API.
5. **LLM classification** — Swap `BasicHeuristicStrategy` for an LLM-backed strategy.
6. **Authentication** — API keys or OAuth for all endpoints.
7. **TLS** — Built-in HTTPS or clear documentation for reverse proxy setup.
8. **Proper logging and metrics** — Structured logs, request tracing, Prometheus metrics.
9. **Systemd / Docker deployment** — One-command deployment per device.
10. **Data export** — Dump ChromaDB contents to JSON/CSV for backup or migration.

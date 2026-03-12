# Pulse Ingestor MVP

`pulse-ingestor-mvp` is a minimal product prototype that passively receives scheduled ChatGPT Personal Pro emails, converts them into structured pulse events, stores them locally, and exposes them to downstream LLMs through API and MCP tools.

## What It Does

- Reads unread emails from a dedicated mailbox
- Parses them into normalized pulse events
- Preserves raw content and summary
- Computes rule-based `entropy_score` and `decision_signal_score`
- Exposes query APIs and MCP tools for downstream agents

## What It Does Not Do

- No private ChatGPT webhook integration
- No browser automation against ChatGPT UI
- No Enterprise Compliance API integration
- No built-in orchestration-heavy agent layer

## Runtime

- API: FastAPI
- Storage: SQLite
- Ingestion: IMAP polling
- MCP transport: stdio

## Docker Quick Start

1. Copy `.env.example` to `.env`
2. Start services:

```bash
docker compose up --build -d
```

3. Check health:

```bash
curl http://127.0.0.1:8000/healthz
```

## Main API

- `GET /healthz`
- `GET /pulses`
- `GET /pulses/{id}`
- `GET /decision/context`
- `GET /scheduler/status`
- `POST /ingest/email`
- `POST /ingest/poll`
- `POST /admin/ingest/backfill`
- `DELETE /admin/pulses/non-target`
- `POST /admin/pulses/rehydrate`

## Mail Handling

- Matching pulse emails are ingested from `PULSE_IMAP_MAILBOX`
- Successfully processed emails are moved to `AI新聞脈動PLUS` by default
- Historical emails can be backfilled later from `AI新聞脈動PLUS`
- Backfill is an explicit tool call, not an automatic startup task

## MCP Tools

- `pulse_list`
- `pulse_get`
- `pulse_decision_context`
- `pulse_poll_now`
- `pulse_backfill_history`
- `pulse_scheduler_status`

## MCP Installation

Docker-based stdio startup:

```bash
docker compose run --rm -T mcp python -m app.mcp_server
```

Validation:

```bash
docker compose run --rm -T mcp python -c "import app.mcp_server; print('mcp-import-ok')"
```

## Sponsorship

This repository is public and supports two revenue paths:

- Sponsorship for open-source maintenance
- Paid implementation and advisory services

Suggested services:

- ChatGPT/email pulse ingestion integration
- MCP server packaging
- LLM decision workflow design
- FastAPI deployment and operations
- Internal knowledge and notification pipelines


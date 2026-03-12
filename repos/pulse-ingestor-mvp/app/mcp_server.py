from __future__ import annotations

from typing import Any

from fastmcp import FastMCP

from app.db import init_db
from app.services.decision_context import decision_context_payload, row_to_item
from app.services.ingestor import backfill_mailbox_history, poll_mailbox
from app.services.scheduler import get_scheduler_snapshot
from app.services.storage import get_pulse_event_by_id, list_pulse_events


mcp = FastMCP("pulse-ingestor-mvp")


@mcp.tool(name="pulse_list")
def pulse_list(
    limit: int = 20,
    status: str | None = None,
    source_type: str | None = None,
    min_entropy: float | None = None,
    min_decision_signal: float | None = None,
) -> dict[str, Any]:
    """List normalized pulse events with optional filters."""
    init_db()
    rows = list_pulse_events(
        limit=limit,
        status=status,
        source_type=source_type,
        min_entropy=min_entropy,
        min_decision_signal=min_decision_signal,
    )
    return {"count": len(rows), "items": [row_to_item(row) for row in rows]}


@mcp.tool(name="pulse_get")
def pulse_get(pulse_id: int) -> dict[str, Any]:
    """Get a single pulse event by ID."""
    init_db()
    row = get_pulse_event_by_id(pulse_id)
    if row is None:
        return {"found": False, "id": pulse_id}
    return {"found": True, "item": row_to_item(row)}


@mcp.tool(name="pulse_decision_context")
def pulse_decision_context(limit: int = 5, min_decision_signal: float = 0.45) -> dict[str, Any]:
    """Return high-signal pulse items for downstream LLM decision use."""
    init_db()
    return decision_context_payload(limit=limit, min_decision_signal=min_decision_signal)


@mcp.tool(name="pulse_poll_now")
def pulse_poll_now() -> dict[str, int]:
    """Poll the mailbox immediately and ingest matching pulse emails."""
    init_db()
    inserted, skipped = poll_mailbox()
    return {"inserted": inserted, "skipped": skipped}


@mcp.tool(name="pulse_backfill_history")
def pulse_backfill_history(mailbox: str | None = None, limit: int | None = None) -> dict[str, Any]:
    """Backfill historical pulse emails from the processed mailbox into local storage."""
    init_db()
    inserted, skipped = backfill_mailbox_history(mailbox_name=mailbox, limit=limit)
    return {"mailbox": mailbox, "inserted": inserted, "skipped": skipped}


@mcp.tool(name="pulse_scheduler_status")
def pulse_scheduler_status() -> dict[str, Any]:
    """Read the current background scheduler state."""
    return get_scheduler_snapshot()


if __name__ == "__main__":
    init_db()
    mcp.run()

from __future__ import annotations

import json
import time
from typing import Any

from app.services.storage import list_pulse_events


def row_to_item(row: object) -> dict[str, Any]:
    signals = json.loads(row["signals_json"])
    return {
        "id": row["id"],
        "source_type": row["source_type"],
        "source_message_id": row["source_message_id"],
        "raw_from": row["raw_from"],
        "normalized_from": row["normalized_from"],
        "received_at": row["received_at"],
        "task_title": row["task_title"],
        "raw_subject": row["raw_subject"],
        "decoded_subject": row["decoded_subject"],
        "raw_body": row["raw_body"],
        "summary": row["summary"],
        "source_url": row["source_url"],
        "signals": signals,
        "entropy_score": row["entropy_score"],
        "status": row["status"],
    }


def decision_context_payload(limit: int = 5, min_decision_signal: float = 0.45) -> dict[str, Any]:
    rows = list_pulse_events(limit=limit, min_decision_signal=min_decision_signal)
    items = []
    for row in rows:
        item = row_to_item(row)
        items.append(
            {
                "id": item["id"],
                "task_title": item["task_title"],
                "summary": item["summary"],
                "source_url": item["source_url"],
                "received_at": item["received_at"],
                "entropy_score": item["entropy_score"],
                "decision_signal_score": item["signals"].get("decision_signal_score", 0.0),
                "tags": item["signals"].get("tags", []),
            }
        )
    return {"generated_at": time.time(), "count": len(items), "items": items}

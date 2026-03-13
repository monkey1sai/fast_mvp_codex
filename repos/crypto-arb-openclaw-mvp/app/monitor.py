from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any, Callable


def load_recent_jsonl(path: str | Path, limit: int = 50) -> list[dict[str, Any]]:
    target = Path(path)
    if not target.exists():
        return []
    with target.open("r", encoding="utf-8") as handle:
        lines = [line.strip() for line in handle if line.strip()]
    if limit > 0:
        lines = lines[-limit:]
    return [json.loads(line) for line in lines]


def _extract_quote(record: dict[str, Any]) -> dict[str, Any]:
    return dict(record.get("result", {}).get("quote", {}) or {})


def _extract_order_state(record: dict[str, Any]) -> str:
    data = (
        record.get("result", {})
        .get("events", [{}])
    )
    for event in data:
        if event.get("stage") != "get_order_result":
            continue
        order_rows = event.get("result", {}).get("data", [])
        if order_rows:
            return str(order_rows[0].get("state", "unknown"))
    return "unknown"


def _extract_order_id(record: dict[str, Any]) -> str:
    place_result = record.get("result", {}).get("result", {}).get("data", [])
    if place_result:
        return str(place_result[0].get("ordId", ""))
    return ""


def build_monitor_snapshot(
    telemetry_path: str | Path,
    event_log_path: str | Path,
    recent_event_limit: int = 12,
) -> dict[str, Any]:
    telemetry_records = load_recent_jsonl(telemetry_path, limit=50)
    event_records = load_recent_jsonl(event_log_path, limit=recent_event_limit)
    latest = telemetry_records[-1] if telemetry_records else {}
    quote = _extract_quote(latest)
    latest_cycle = {
        "ts": latest.get("ts", ""),
        "cycle": latest.get("cycle", 0),
        "symbol": latest.get("symbol", ""),
        "price_source": latest.get("price_source", ""),
        "latency_ms": latest.get("latency_ms", 0.0),
        "kill_switch_mode": latest.get("kill_switch", {}).get("mode", "unknown"),
        "side": quote.get("side", ""),
        "price": quote.get("price", 0.0),
        "size_usd": quote.get("size_usd", 0.0),
        "placed_orders": latest.get("result", {}).get("placed_orders", 0),
        "cancelled_orders": latest.get("result", {}).get("cancelled_orders", 0),
        "order_state": _extract_order_state(latest),
        "order_id": _extract_order_id(latest),
    }
    recent_events = []
    for event in event_records:
        recent_events.append(
            {
                "ts": event.get("ts", ""),
                "cycle": event.get("cycle", 0),
                "stage": event.get("stage", ""),
                "side": event.get("side", ""),
                "price": event.get("price", 0.0),
                "size_usd": event.get("size_usd", 0.0),
                "approved": event.get("approved"),
                "order_id": event.get("order_id", ""),
            }
        )
    return {
        "telemetry_path": str(Path(telemetry_path)),
        "event_log_path": str(Path(event_log_path)),
        "telemetry_records_seen": len(telemetry_records),
        "latest_cycle": latest_cycle,
        "recent_events": recent_events,
    }


def render_monitor_snapshot(snapshot: dict[str, Any]) -> str:
    latest = snapshot.get("latest_cycle", {})
    recent_events = snapshot.get("recent_events", [])
    header = (
        f"[MONITOR] ts={latest.get('ts', '')} cycle={latest.get('cycle', 0)} "
        f"symbol={latest.get('symbol', '')} source={latest.get('price_source', '')} "
        f"kill={latest.get('kill_switch_mode', 'unknown')} latency_ms={latest.get('latency_ms', 0.0)}"
    )
    latest_line = (
        f"[LATEST] side={latest.get('side', '')} price={latest.get('price', 0.0)} "
        f"size_usd={latest.get('size_usd', 0.0)} placed={latest.get('placed_orders', 0)} "
        f"cancelled={latest.get('cancelled_orders', 0)} state={latest.get('order_state', 'unknown')} "
        f"order_id={latest.get('order_id', '')}"
    )
    lines = [header, latest_line, "[EVENTS]"]
    for event in recent_events:
        parts = [
            f"ts={event.get('ts', '')}",
            f"cycle={event.get('cycle', 0)}",
            f"stage={event.get('stage', '')}",
        ]
        if event.get("side"):
            parts.append(f"side={event['side']}")
        if event.get("price"):
            parts.append(f"price={event['price']}")
        if event.get("size_usd"):
            parts.append(f"size_usd={event['size_usd']}")
        if event.get("approved") is not None:
            parts.append(f"approved={event['approved']}")
        if event.get("order_id"):
            parts.append(f"order_id={event['order_id']}")
        lines.append(" - " + " ".join(parts))
    if len(lines) == 3:
        lines.append(" - no events")
    return "\n".join(lines)


def watch_monitor(
    telemetry_path: str | Path,
    event_log_path: str | Path,
    refresh_seconds: float = 2.0,
    recent_event_limit: int = 12,
    iterations: int = 1,
    clear_fn: Callable[[], None] | None = None,
    sleep_fn: Callable[[float], None] = time.sleep,
    print_fn: Callable[[str], None] = print,
) -> int:
    remaining = iterations
    while True:
        snapshot = build_monitor_snapshot(
            telemetry_path=telemetry_path,
            event_log_path=event_log_path,
            recent_event_limit=recent_event_limit,
        )
        if clear_fn is not None:
            clear_fn()
        print_fn(render_monitor_snapshot(snapshot))
        if iterations > 0:
            remaining -= 1
            if remaining <= 0:
                return 0
        sleep_fn(refresh_seconds)

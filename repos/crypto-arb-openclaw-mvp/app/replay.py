from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def load_telemetry_records(path: str | Path) -> list[dict[str, Any]]:
    target = Path(path)
    if not target.exists():
        return []
    records: list[dict[str, Any]] = []
    with target.open("r", encoding="utf-8") as handle:
        for raw_line in handle:
            line = raw_line.strip()
            if not line:
                continue
            records.append(json.loads(line))
    return records


def summarize_telemetry(records: list[dict[str, Any]]) -> dict[str, Any]:
    if not records:
        return {
            "cycles": 0,
            "placed_orders": 0,
            "cancelled_orders": 0,
            "halt_cycles": 0,
            "guard_reject_cycles": 0,
            "avg_latency_ms": 0.0,
            "max_latency_ms": 0.0,
            "price_sources": [],
            "symbols": [],
        }

    latencies = [float(record.get("latency_ms", 0.0)) for record in records]
    placed_orders = sum(int(record.get("result", {}).get("placed_orders", 0)) for record in records)
    cancelled_orders = sum(int(record.get("result", {}).get("cancelled_orders", 0)) for record in records)
    halt_cycles = sum(1 for record in records if record.get("kill_switch", {}).get("mode") == "halt")
    guard_reject_cycles = sum(
        1
        for record in records
        if record.get("result", {}).get("placed_orders", 0) == 0
        and record.get("result", {}).get("reason") == "no quote passed live guard"
    )
    return {
        "cycles": len(records),
        "placed_orders": placed_orders,
        "cancelled_orders": cancelled_orders,
        "halt_cycles": halt_cycles,
        "guard_reject_cycles": guard_reject_cycles,
        "avg_latency_ms": round(sum(latencies) / len(latencies), 3),
        "max_latency_ms": round(max(latencies), 3),
        "price_sources": sorted({str(record.get("price_source", "")) for record in records if record.get("price_source")}),
        "symbols": sorted({str(record.get("symbol", "")) for record in records if record.get("symbol")}),
    }


def load_and_summarize(path: str | Path) -> dict[str, Any]:
    records = load_telemetry_records(path)
    summary = summarize_telemetry(records)
    summary["telemetry_path"] = str(Path(path))
    return summary

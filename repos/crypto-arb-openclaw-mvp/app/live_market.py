from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from app.config import load_live_market_config
from app.integrations.coingecko_mcp import snapshot_from_websocket_event


def build_coingecko_subscribe_message(api_key: str, channel: str, coin_ids: list[str]) -> dict[str, Any]:
    del api_key
    del coin_ids
    return {
        "command": "subscribe",
        "identifier": json.dumps({"channel": channel}),
    }


def parse_live_event(event: dict[str, Any]) -> list[dict[str, Any]]:
    timestamp = datetime.now(timezone.utc).isoformat()
    snapshots = snapshot_from_websocket_event(event, timestamp=timestamp)
    return [
        {
            "symbol": snapshot.symbol,
            "reference_price": snapshot.reference_price,
            "venue_bid": snapshot.venue_bid,
            "venue_ask": snapshot.venue_ask,
            "spread_bps": round(((snapshot.venue_ask - snapshot.venue_bid) / snapshot.reference_price) * 10_000, 4),
            "timestamp": snapshot.timestamp,
        }
        for snapshot in snapshots
    ]


def write_live_event(path: Path, records: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        for record in records:
            handle.write(json.dumps(record, ensure_ascii=False) + "\n")


def live_monitor_plan() -> dict[str, Any]:
    config = load_live_market_config()
    return {
        "mode": "live_market_monitor_only",
        "provider": "CoinGecko WebSocket",
        "channel": config["coingecko_ws_channel"],
        "coin_ids": str(config["coingecko_ws_coin_ids"]).split(","),
        "duration_seconds": config["coingecko_ws_duration_seconds"],
        "instruction": "Connect to live market data, record observations, do not place orders.",
    }

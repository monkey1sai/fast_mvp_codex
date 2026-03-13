from __future__ import annotations

import argparse
import asyncio
import json
import logging
import os
from pathlib import Path
from typing import Any
from urllib.parse import urlencode

from app.config import load_live_market_config
from app.live_market import build_coingecko_subscribe_message, parse_live_event, write_live_event

LOGGER = logging.getLogger("coingecko_live_monitor")


def _normalize_message(payload: dict[str, Any]) -> dict[str, Any] | None:
    if "type" in payload:
        return None
    if "message" in payload and isinstance(payload["message"], dict):
        return payload["message"]
    if "message" in payload and isinstance(payload["message"], str):
        try:
            return json.loads(payload["message"])
        except json.JSONDecodeError:
            return None
    return payload


def format_live_record(record: dict[str, Any], event_index: int) -> str:
    return (
        f"event={event_index} symbol={record['symbol']} "
        f"price={record['reference_price']} spread_bps={record['spread_bps']} "
        f"timestamp={record['timestamp']}"
    )


async def monitor_coingecko_live_market(
    api_key: str,
    duration_seconds: int,
    output_path: Path,
    ws_url: str,
    channel: str,
    coin_ids: list[str],
) -> dict[str, Any]:
    try:
        import websockets
    except ImportError as exc:
        raise RuntimeError("websockets package is required") from exc

    connection_url = f"{ws_url}?{urlencode({'x_cg_pro_api_key': api_key})}"
    subscribe_message = build_coingecko_subscribe_message(api_key=api_key, channel=channel, coin_ids=coin_ids)
    set_tokens_message = {
        "command": "message",
        "identifier": json.dumps({"channel": channel}),
        "data": json.dumps({"coin_id": coin_ids, "action": "set_tokens"}),
    }

    collected = 0
    symbols: set[str] = set()
    async with websockets.connect(connection_url, ping_interval=20, ping_timeout=20) as websocket:
        await websocket.send(json.dumps(subscribe_message))
        await asyncio.sleep(1)
        await websocket.send(json.dumps(set_tokens_message))

        loop = asyncio.get_running_loop()
        deadline = loop.time() + duration_seconds
        while loop.time() < deadline:
            timeout = max(0.1, min(10.0, deadline - loop.time()))
            try:
                raw = await asyncio.wait_for(websocket.recv(), timeout=timeout)
            except TimeoutError:
                continue
            payload = json.loads(raw)
            normalized = _normalize_message(payload)
            if not normalized:
                continue
            records = parse_live_event(normalized)
            if not records:
                continue
            write_live_event(output_path, records)
            collected += len(records)
            for record in records:
                symbols.add(str(record["symbol"]))
                LOGGER.info(format_live_record(record, event_index=collected))

    return {
        "output_path": str(output_path),
        "events_collected": collected,
        "symbols": sorted(symbols),
        "duration_seconds": duration_seconds,
        "channel": channel,
    }


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    config = load_live_market_config()
    parser = argparse.ArgumentParser(description="Run CoinGecko live market monitor without placing orders.")
    parser.add_argument("--duration", type=int, default=int(config["coingecko_ws_duration_seconds"]))
    parser.add_argument("--output", default="runtime/coingecko-live.jsonl")
    args = parser.parse_args()

    api_key = os.getenv("COINGECKO_PRO_API_KEY", "")
    if not api_key:
        raise SystemExit("COINGECKO_PRO_API_KEY is required")

    result = asyncio.run(
        monitor_coingecko_live_market(
            api_key=api_key,
            duration_seconds=args.duration,
            output_path=Path(args.output),
            ws_url=str(config["coingecko_ws_url"]),
            channel=str(config["coingecko_ws_channel"]),
            coin_ids=[coin_id.strip() for coin_id in str(config["coingecko_ws_coin_ids"]).split(",") if coin_id.strip()],
        )
    )
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()

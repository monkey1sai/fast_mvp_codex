from __future__ import annotations

from app.models import MarketSnapshot


def snapshot_from_market_tool(payload: dict) -> list[MarketSnapshot]:
    generated_at = payload.get("generated_at", "")
    snapshots: list[MarketSnapshot] = []
    for asset in payload.get("assets", []):
        price = float(asset["current_price"])
        high_24h = float(asset.get("high_24h", price))
        low_24h = float(asset.get("low_24h", price))
        spread_proxy = max((high_24h - low_24h) * 0.015, price * 0.006)
        snapshots.append(
            MarketSnapshot(
                symbol=str(asset["symbol"]).upper(),
                venue_bid=round(price + (spread_proxy / 2), 8),
                venue_ask=round(price - (spread_proxy / 2), 8),
                reference_price=price,
                volatility_24h_pct=abs(float(asset.get("price_change_percentage_24h", 0.0))),
                liquidity_score=min(1.0, float(asset.get("total_volume", 0.0)) / 1_000_000_000),
                timestamp=generated_at,
            )
        )
    return snapshots


def snapshot_from_websocket_event(event: dict, timestamp: str) -> list[MarketSnapshot]:
    snapshots: list[MarketSnapshot] = []
    data = event.get("data", event)
    items = data if isinstance(data, list) else [data]
    for item in items:
        if not isinstance(item, dict):
            continue
        coin_id = str(item.get("coin_id", item.get("id", item.get("i", "unknown"))))
        price = float(item.get("price", item.get("usd_price", item.get("p", 0.0))))
        if price <= 0:
            continue
        spread_proxy = max(price * 0.001, 0.01)
        snapshots.append(
            MarketSnapshot(
                symbol=coin_id.upper(),
                venue_bid=round(price - (spread_proxy / 2), 8),
                venue_ask=round(price + (spread_proxy / 2), 8),
                reference_price=price,
                volatility_24h_pct=abs(float(item.get("h24_price_change_percentage", item.get("price_change_percentage_24h", item.get("pp", 0.0))))),
                liquidity_score=1.0,
                timestamp=str(item.get("t", timestamp)),
            )
        )
    return snapshots

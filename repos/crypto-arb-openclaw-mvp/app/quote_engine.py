from __future__ import annotations

from app.models import KillSwitchState, OrderBookTop, PositionState, QuoteIntent


def build_quote_intents(
    book: OrderBookTop,
    position: PositionState,
    kill_switch: KillSwitchState,
    max_notional_usd: float,
    quote_refresh_ms: int,
) -> list[QuoteIntent]:
    if kill_switch.triggered or kill_switch.mode == "halt":
        return []

    widen_factor = 1.5 if kill_switch.mode == "caution" else 1.0
    half_spread = ((book.ask - book.bid) / 2) * widen_factor
    buy_price = round(book.mid_price - half_spread, 8)
    sell_price = round(book.mid_price + half_spread, 8)

    if position.net_exposure_usd >= max_notional_usd * 1.5:
        return [
            QuoteIntent(
                symbol=book.symbol,
                side="sell",
                price=sell_price,
                size_usd=max_notional_usd,
                ttl_ms=quote_refresh_ms,
                rationale=f"{kill_switch.mode} regime with inventory reduction",
            )
        ]

    return [
        QuoteIntent(
            symbol=book.symbol,
            side="buy",
            price=buy_price,
            size_usd=max_notional_usd,
            ttl_ms=quote_refresh_ms,
            rationale=f"{kill_switch.mode} regime maker quote",
        ),
        QuoteIntent(
            symbol=book.symbol,
            side="sell",
            price=sell_price,
            size_usd=max_notional_usd,
            ttl_ms=quote_refresh_ms,
            rationale=f"{kill_switch.mode} regime maker quote",
        ),
    ]

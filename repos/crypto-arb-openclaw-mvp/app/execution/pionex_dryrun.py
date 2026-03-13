from __future__ import annotations

from app.execution.base import ExecutionAdapter
from app.models import OrderBookTop, PositionState, QuoteIntent


class PionexDryRunExecution(ExecutionAdapter):
    def __init__(self) -> None:
        self._positions: dict[str, PositionState] = {}
        self._order_seq = 0

    def place_order(self, quote: QuoteIntent, book: OrderBookTop) -> dict:
        self._order_seq += 1
        order_id = f"dryrun-{self._order_seq}"
        filled = (quote.side == "buy" and quote.price >= book.ask) or (quote.side == "sell" and quote.price <= book.bid)
        status = "filled" if filled else "resting"
        position = self._positions.get(
            quote.symbol,
            PositionState(symbol=quote.symbol, base_qty=0.0, quote_value_usd=0.0, open_orders=0),
        )

        if filled:
            direction = 1 if quote.side == "buy" else -1
            next_base = position.base_qty + (direction * (quote.size_usd / max(quote.price, 1e-9)))
            next_quote = max(0.0, position.quote_value_usd + quote.size_usd)
            next_open_orders = position.open_orders
        else:
            next_base = position.base_qty
            next_quote = position.quote_value_usd
            next_open_orders = position.open_orders + 1

        self._positions[quote.symbol] = PositionState(
            symbol=quote.symbol,
            base_qty=next_base,
            quote_value_usd=next_quote,
            open_orders=next_open_orders,
        )
        return {"accepted": True, "status": status, "order_id": order_id}

    def cancel_order(self, symbol: str, order_id: str) -> dict:
        return {"cancelled": True, "symbol": symbol, "order_id": order_id}

    def get_position(self, symbol: str) -> PositionState:
        return self._positions.get(symbol, PositionState(symbol=symbol, base_qty=0.0, quote_value_usd=0.0, open_orders=0))

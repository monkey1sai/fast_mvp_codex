from __future__ import annotations

from abc import ABC, abstractmethod

from app.models import OrderBookTop, PositionState, QuoteIntent


class ExecutionAdapter(ABC):
    @abstractmethod
    def place_order(self, quote: QuoteIntent, book: OrderBookTop) -> dict:
        raise NotImplementedError

    @abstractmethod
    def cancel_order(self, symbol: str, order_id: str) -> dict:
        raise NotImplementedError

    @abstractmethod
    def get_position(self, symbol: str) -> PositionState:
        raise NotImplementedError

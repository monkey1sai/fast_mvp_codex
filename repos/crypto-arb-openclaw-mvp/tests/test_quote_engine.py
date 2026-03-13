import unittest

from app.models import KillSwitchState, OrderBookTop, PositionState
from app.quote_engine import build_quote_intents


class QuoteEngineTests(unittest.TestCase):
    def test_generates_two_sided_quotes_in_normal_mode(self) -> None:
        book = OrderBookTop(symbol="BTC_USDT", bid=100.0, ask=100.2, timestamp="2026-03-13T00:00:00Z")
        position = PositionState(symbol="BTC_USDT", base_qty=0.0, quote_value_usd=0.0, open_orders=0)
        kill = KillSwitchState(mode="normal", triggered=False, reason="")

        intents = build_quote_intents(book, position, kill, max_notional_usd=5.0, quote_refresh_ms=1200)
        self.assertEqual(len(intents), 2)
        self.assertEqual({intent.side for intent in intents}, {"buy", "sell"})

    def test_halt_mode_blocks_quotes(self) -> None:
        book = OrderBookTop(symbol="BTC_USDT", bid=100.0, ask=100.2, timestamp="2026-03-13T00:00:00Z")
        position = PositionState(symbol="BTC_USDT", base_qty=0.0, quote_value_usd=0.0, open_orders=0)
        kill = KillSwitchState(mode="halt", triggered=True, reason="pulse risk")

        intents = build_quote_intents(book, position, kill, max_notional_usd=5.0, quote_refresh_ms=1200)
        self.assertEqual(intents, [])


if __name__ == "__main__":
    unittest.main()

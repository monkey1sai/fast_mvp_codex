import unittest

from app.execution.pionex_dryrun import PionexDryRunExecution
from app.models import OrderBookTop, PositionState, QuoteIntent


class PionexDryRunTests(unittest.TestCase):
    def test_buy_order_is_filled_when_crossing_ask(self) -> None:
        adapter = PionexDryRunExecution()
        book = OrderBookTop(symbol="BTC_USDT", bid=99.8, ask=100.0, timestamp="2026-03-13T00:00:00Z")
        quote = QuoteIntent(symbol="BTC_USDT", side="buy", price=100.0, size_usd=5.0, ttl_ms=1000, rationale="demo")

        result = adapter.place_order(quote, book)
        position = adapter.get_position("BTC_USDT")

        self.assertTrue(result["accepted"])
        self.assertEqual(result["status"], "filled")
        self.assertIsInstance(position, PositionState)
        self.assertGreater(position.quote_value_usd, 0.0)


if __name__ == "__main__":
    unittest.main()

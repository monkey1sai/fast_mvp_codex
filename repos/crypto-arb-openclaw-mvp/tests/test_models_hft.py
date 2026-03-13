import unittest

from app.models import CycleDecision, KillSwitchState, OrderBookTop, PositionState, QuoteIntent


class HftModelTests(unittest.TestCase):
    def test_order_book_mid_and_spread(self) -> None:
        book = OrderBookTop(symbol="BTC_USDT", bid=100.0, ask=100.5, timestamp="2026-03-13T00:00:00Z")
        self.assertAlmostEqual(book.mid_price, 100.25)
        self.assertGreater(book.spread_bps, 0.0)

    def test_quote_intent_notional(self) -> None:
        quote = QuoteIntent(symbol="BTC_USDT", side="buy", price=100.0, size_usd=5.0, ttl_ms=1200, rationale="demo")
        self.assertEqual(quote.notional_usd, 5.0)

    def test_kill_switch_triggered(self) -> None:
        kill = KillSwitchState(mode="halt", triggered=True, reason="exchange incident")
        self.assertTrue(kill.triggered)

    def test_position_state_inventory_skew(self) -> None:
        position = PositionState(symbol="BTC_USDT", base_qty=0.001, quote_value_usd=8.0, open_orders=1)
        self.assertGreaterEqual(position.net_exposure_usd, 8.0)

    def test_cycle_decision_trade_flag(self) -> None:
        decision = CycleDecision(
            action="trade",
            estimated_net_profit_bps=32.0,
            cooldown_seconds=0,
            reason="net edge above threshold",
        )
        self.assertEqual(decision.action, "trade")
        self.assertGreater(decision.estimated_net_profit_bps, 0.0)


if __name__ == "__main__":
    unittest.main()

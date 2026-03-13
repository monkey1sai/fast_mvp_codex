import unittest

from app.live_guard import evaluate_live_order
from app.models import LiveTradingConfig, QuoteIntent


class LiveGuardTests(unittest.TestCase):
    def test_rejects_when_live_disabled(self) -> None:
        config = LiveTradingConfig(
            enabled=False,
            exchange="pionex",
            api_base_url="https://api.pionex.com",
            symbol_allowlist=["BTC_USDT"],
            max_notional_per_order_usd=5.0,
            max_daily_loss_usd=1.0,
            auto_cancel_after_ms=3000,
            require_explicit_confirmation=True,
        )
        quote = QuoteIntent(symbol="BTC_USDT", side="buy", price=100.0, size_usd=5.0, ttl_ms=1000, rationale="demo")

        decision = evaluate_live_order(quote, config, daily_loss_usd=0.0, explicit_confirmation=True)
        self.assertFalse(decision.approved)
        self.assertIn("live trading disabled", decision.reasons)

    def test_rejects_disallowed_symbol(self) -> None:
        config = LiveTradingConfig(
            enabled=True,
            exchange="pionex",
            api_base_url="https://api.pionex.com",
            symbol_allowlist=["BTC_USDT"],
            max_notional_per_order_usd=5.0,
            max_daily_loss_usd=1.0,
            auto_cancel_after_ms=3000,
            require_explicit_confirmation=True,
        )
        quote = QuoteIntent(symbol="ETH_USDT", side="buy", price=100.0, size_usd=5.0, ttl_ms=1000, rationale="demo")

        decision = evaluate_live_order(quote, config, daily_loss_usd=0.0, explicit_confirmation=True)
        self.assertFalse(decision.approved)
        self.assertIn("symbol not allowlisted", decision.reasons)

    def test_approves_small_order_when_all_guards_pass(self) -> None:
        config = LiveTradingConfig(
            enabled=True,
            exchange="pionex",
            api_base_url="https://api.pionex.com",
            symbol_allowlist=["BTC_USDT"],
            max_notional_per_order_usd=5.0,
            max_daily_loss_usd=1.0,
            auto_cancel_after_ms=3000,
            require_explicit_confirmation=True,
        )
        quote = QuoteIntent(symbol="BTC_USDT", side="buy", price=100.0, size_usd=5.0, ttl_ms=1000, rationale="demo")

        decision = evaluate_live_order(quote, config, daily_loss_usd=0.0, explicit_confirmation=True)
        self.assertTrue(decision.approved)
        self.assertEqual(decision.capped_notional_usd, 5.0)

    def test_rejects_below_exchange_minimum(self) -> None:
        config = LiveTradingConfig(
            enabled=True,
            exchange="pionex",
            api_base_url="https://api.pionex.com",
            symbol_allowlist=["BTC_USDT"],
            max_notional_per_order_usd=15.0,
            max_daily_loss_usd=1.0,
            auto_cancel_after_ms=3000,
            require_explicit_confirmation=True,
        )
        quote = QuoteIntent(symbol="BTC_USDT", side="buy", price=100.0, size_usd=5.0, ttl_ms=1000, rationale="demo")

        decision = evaluate_live_order(
            quote,
            config,
            daily_loss_usd=0.0,
            explicit_confirmation=True,
            min_notional_usd=10.0,
        )
        self.assertFalse(decision.approved)
        self.assertIn("order notional below exchange minimum", decision.reasons)


if __name__ == "__main__":
    unittest.main()

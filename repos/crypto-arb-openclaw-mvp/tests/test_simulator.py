import unittest

from app.config import load_strategy_config
from app.models import MarketSnapshot
from app.simulator import run_simulation
from app.strategy import evaluate_cycle_decision


class SimulatorTests(unittest.TestCase):
    def test_cycle_decision_waits_when_net_edge_below_threshold(self) -> None:
        config = load_strategy_config()
        snapshots = [
            MarketSnapshot(
                symbol="BTC",
                venue_bid=100.1,
                venue_ask=99.9,
                reference_price=100.0,
                volatility_24h_pct=2.5,
                liquidity_score=0.8,
                timestamp="2026-03-13T00:00:00Z",
            ),
            MarketSnapshot(
                symbol="BTC",
                venue_bid=100.2,
                venue_ask=100.0,
                reference_price=100.1,
                volatility_24h_pct=2.4,
                liquidity_score=0.8,
                timestamp="2026-03-13T00:01:00Z",
            ),
        ]

        decision = evaluate_cycle_decision(snapshots, config)
        self.assertEqual(decision.action, "wait")
        self.assertEqual(decision.cooldown_seconds, config.cooldown_seconds)

    def test_simulation_grows_capital_on_positive_edges(self) -> None:
        config = load_strategy_config()
        snapshots = [
            MarketSnapshot(
                symbol="BTC",
                venue_bid=101.0,
                venue_ask=99.0,
                reference_price=100.0,
                volatility_24h_pct=2.5,
                liquidity_score=0.8,
                timestamp="2026-03-13T00:00:00Z",
            ),
            MarketSnapshot(
                symbol="ETH",
                venue_bid=102.0,
                venue_ask=100.0,
                reference_price=101.0,
                volatility_24h_pct=3.1,
                liquidity_score=0.7,
                timestamp="2026-03-13T00:01:00Z",
            ),
        ]

        trades = run_simulation(snapshots, [], config, initial_capital_usd=30.0)
        self.assertTrue(trades)
        self.assertGreater(trades[-1].capital_after_usd, 30.0)

    def test_simulation_respects_cooldown_after_failed_backtest(self) -> None:
        config = load_strategy_config()
        snapshots = [
            MarketSnapshot(
                symbol="BTC",
                venue_bid=100.1,
                venue_ask=99.9,
                reference_price=100.0,
                volatility_24h_pct=2.5,
                liquidity_score=0.8,
                timestamp="2026-03-13T00:00:00Z",
            ),
            MarketSnapshot(
                symbol="BTC",
                venue_bid=102.0,
                venue_ask=100.0,
                reference_price=101.0,
                volatility_24h_pct=3.1,
                liquidity_score=0.8,
                timestamp="2026-03-13T00:01:00Z",
            ),
            MarketSnapshot(
                symbol="BTC",
                venue_bid=103.0,
                venue_ask=101.0,
                reference_price=102.0,
                volatility_24h_pct=3.1,
                liquidity_score=0.8,
                timestamp="2026-03-13T00:02:00Z",
            ),
            MarketSnapshot(
                symbol="BTC",
                venue_bid=104.5,
                venue_ask=102.0,
                reference_price=103.0,
                volatility_24h_pct=3.2,
                liquidity_score=0.8,
                timestamp="2026-03-13T00:03:00Z",
            ),
        ]

        trades = run_simulation(snapshots, [], config, initial_capital_usd=30.0)
        self.assertEqual(len(trades), 1)
        self.assertEqual(trades[0].opportunity.symbol, "BTC")


if __name__ == "__main__":
    unittest.main()

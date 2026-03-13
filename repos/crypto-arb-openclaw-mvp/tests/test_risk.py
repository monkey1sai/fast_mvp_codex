import unittest

from app.models import Opportunity, PulseSignal
from app.config import load_strategy_config
from app.risk import evaluate_risk


class RiskTests(unittest.TestCase):
    def test_blocks_high_entropy_signal(self) -> None:
        config = load_strategy_config()
        opportunity = Opportunity(
            symbol="BTC",
            gross_edge_bps=40,
            net_edge_bps=30,
            size_usd=20,
            expected_pnl_usd=0.06,
            rationale="demo",
        )
        signals = [
            PulseSignal(
                task_title="Exchange incident",
                summary="withdrawal halted",
                entropy_score=0.9,
                decision_signal_score=0.8,
                tags=["exchange"],
            )
        ]

        decision = evaluate_risk(opportunity, signals, config, capital_usd=30, daily_drawdown_pct=0.0)
        self.assertFalse(decision.approved)
        self.assertIn("high-entropy pulse active", decision.reasons)


if __name__ == "__main__":
    unittest.main()

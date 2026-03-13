import unittest

from app.models import PulseSignal
from app.risk import derive_kill_switch


class KillSwitchTests(unittest.TestCase):
    def test_high_entropy_halts_trading(self) -> None:
        signals = [
            PulseSignal(
                task_title="Exchange exploit",
                summary="withdraw halted",
                entropy_score=0.91,
                decision_signal_score=0.8,
                tags=["exchange", "exploit"],
            )
        ]
        state = derive_kill_switch(signals, daily_drawdown_pct=0.0, entropy_threshold=0.75)
        self.assertTrue(state.triggered)
        self.assertEqual(state.mode, "halt")

    def test_medium_entropy_enters_caution(self) -> None:
        signals = [
            PulseSignal(
                task_title="Macro stress",
                summary="volatility rising",
                entropy_score=0.61,
                decision_signal_score=0.7,
                tags=["macro"],
            )
        ]
        state = derive_kill_switch(signals, daily_drawdown_pct=0.0, entropy_threshold=0.75)
        self.assertFalse(state.triggered)
        self.assertEqual(state.mode, "caution")


if __name__ == "__main__":
    unittest.main()

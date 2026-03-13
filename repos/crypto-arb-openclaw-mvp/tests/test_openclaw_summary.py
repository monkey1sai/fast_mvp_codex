import json
import unittest

from app.integrations.openclaw import build_openclaw_message


class OpenClawSummaryTests(unittest.TestCase):
    def test_message_contains_regime_fields(self) -> None:
        message = build_openclaw_message(
            {
                "risk_mode": "caution",
                "approved_count": 1,
                "blocked_count": 2,
                "kill_switch_reason": "",
                "human_review_note": "widen quotes",
            }
        )
        payload = json.loads(message)
        self.assertEqual(payload["summary"]["risk_mode"], "caution")
        self.assertEqual(payload["summary"]["human_review_note"], "widen quotes")


if __name__ == "__main__":
    unittest.main()

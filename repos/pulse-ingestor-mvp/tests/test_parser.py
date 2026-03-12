from __future__ import annotations

import json
import unittest

from app.services.parser import parse_email_to_pulse
from app.services.scorer import score_pulse_text


class ParserTests(unittest.TestCase):
    def test_parse_email_to_pulse_builds_summary_and_signals(self) -> None:
        event = parse_email_to_pulse(
            source_message_id="msg-1",
            raw_from="notifications@openai.com",
            subject="[任務更新] Crypto 指數",
            body="指數 18（Extreme Fear）。\n從 ChatGPT 更新任務\nCrypto 指數：極度恐懼 (18)\nhttps://chatgpt.com/c/test",
            received_at="Thu, 12 Mar 2026 10:00:00 +0800",
        )
        self.assertEqual(event.task_title, "Crypto 指數")
        self.assertEqual(event.decoded_subject, "[任務更新] Crypto 指數")
        self.assertEqual(event.source_url, "https://chatgpt.com/c/test")
        self.assertGreater(event.entropy_score, 0.0)
        signals = json.loads(event.signals_json)
        self.assertIn("crypto", signals["tags"])
        self.assertIn("decision_signal_score", signals)

    def test_score_pulse_text_returns_all_scores(self) -> None:
        scores = score_pulse_text(
            subject="urgent task",
            body="maybe this risk needs action today",
            summary="warning",
        )
        self.assertIn("entropy_score", scores)
        self.assertGreater(scores["priority_score"], 0.0)


if __name__ == "__main__":
    unittest.main()

import unittest

from app.live_market_runner import _normalize_message


class LiveMarketRunnerTests(unittest.TestCase):
    def test_normalize_message_passthrough(self) -> None:
        payload = {"i": "bitcoin", "p": 70000}
        self.assertEqual(_normalize_message(payload), payload)

    def test_normalize_message_nested(self) -> None:
        payload = {"message": {"i": "bitcoin", "p": 70000}}
        self.assertEqual(_normalize_message(payload), {"i": "bitcoin", "p": 70000})

    def test_normalize_message_skips_control_frames(self) -> None:
        payload = {"type": "welcome"}
        self.assertIsNone(_normalize_message(payload))


if __name__ == "__main__":
    unittest.main()

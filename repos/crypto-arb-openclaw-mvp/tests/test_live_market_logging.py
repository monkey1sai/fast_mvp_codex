import unittest

from app.live_market_runner import format_live_record


class LiveMarketLoggingTests(unittest.TestCase):
    def test_format_live_record(self) -> None:
        record = {
            "symbol": "BITCOIN",
            "reference_price": 71234.5,
            "spread_bps": 10.0,
            "timestamp": "2026-03-13T00:00:00Z",
        }
        message = format_live_record(record, event_index=3)
        self.assertIn("event=3", message)
        self.assertIn("BITCOIN", message)
        self.assertIn("71234.5", message)


if __name__ == "__main__":
    unittest.main()

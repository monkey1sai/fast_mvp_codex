import tempfile
import unittest
from pathlib import Path

from app.live_market import build_coingecko_subscribe_message, live_monitor_plan, parse_live_event, write_live_event


class LiveMarketTests(unittest.TestCase):
    def test_build_subscribe_message(self) -> None:
        payload = build_coingecko_subscribe_message("demo-key", "CGSimplePrice", ["bitcoin", "ethereum"])
        self.assertEqual(payload["command"], "subscribe")
        self.assertEqual(payload["identifier"], "{\"channel\": \"CGSimplePrice\"}")

    def test_parse_live_event(self) -> None:
        event = {"data": {"i": "bitcoin", "p": 71234.5, "pp": 3.2, "t": 1747808150}}
        records = parse_live_event(event)
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0]["symbol"], "BITCOIN")
        self.assertGreater(records[0]["spread_bps"], 0.0)

    def test_write_live_event(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "runtime" / "live.jsonl"
            write_live_event(path, [{"symbol": "BTC", "reference_price": 70000}])
            self.assertTrue(path.exists())
            self.assertIn("BTC", path.read_text(encoding="utf-8"))

    def test_live_monitor_plan(self) -> None:
        plan = live_monitor_plan()
        self.assertEqual(plan["mode"], "live_market_monitor_only")


if __name__ == "__main__":
    unittest.main()

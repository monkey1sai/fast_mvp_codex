from __future__ import annotations

import json
import tempfile
import unittest

from app.replay import load_and_summarize, load_telemetry_records, summarize_telemetry
from app.telemetry import append_jsonl


class ReplayTests(unittest.TestCase):
    def test_load_telemetry_records_returns_empty_for_missing_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            records = load_telemetry_records(f"{tmpdir}/missing.jsonl")
        self.assertEqual(records, [])

    def test_summarize_telemetry_aggregates_runner_metrics(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            target = f"{tmpdir}/runner.jsonl"
            append_jsonl(
                target,
                {
                    "cycle": 1,
                    "latency_ms": 12.5,
                    "price_source": "okx",
                    "symbol": "BTC_USDT",
                    "kill_switch": {"mode": "normal"},
                    "result": {"placed_orders": 1, "cancelled_orders": 0},
                },
            )
            append_jsonl(
                target,
                {
                    "cycle": 2,
                    "latency_ms": 25.0,
                    "price_source": "coingecko",
                    "symbol": "BTC_USDT",
                    "kill_switch": {"mode": "halt"},
                    "result": {
                        "placed_orders": 0,
                        "cancelled_orders": 1,
                        "reason": "no quote passed live guard",
                    },
                },
            )
            records = load_telemetry_records(target)
            summary = summarize_telemetry(records)
            enriched = load_and_summarize(target)

        self.assertEqual(summary["cycles"], 2)
        self.assertEqual(summary["placed_orders"], 1)
        self.assertEqual(summary["cancelled_orders"], 1)
        self.assertEqual(summary["halt_cycles"], 1)
        self.assertEqual(summary["guard_reject_cycles"], 1)
        self.assertEqual(summary["avg_latency_ms"], 18.75)
        self.assertEqual(summary["max_latency_ms"], 25.0)
        self.assertEqual(summary["price_sources"], ["coingecko", "okx"])
        self.assertEqual(summary["symbols"], ["BTC_USDT"])
        self.assertTrue(enriched["telemetry_path"].endswith("runner.jsonl"))


if __name__ == "__main__":
    unittest.main()

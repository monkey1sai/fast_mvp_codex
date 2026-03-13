from __future__ import annotations

import tempfile
import unittest

from app.monitor import build_monitor_snapshot, render_monitor_snapshot, watch_monitor
from app.telemetry import append_jsonl


class MonitorTests(unittest.TestCase):
    def test_build_monitor_snapshot_handles_missing_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            snapshot = build_monitor_snapshot(
                telemetry_path=f"{tmpdir}/missing-runner.jsonl",
                event_log_path=f"{tmpdir}/missing-events.jsonl",
            )
        self.assertEqual(snapshot["telemetry_records_seen"], 0)
        self.assertEqual(snapshot["latest_cycle"]["order_state"], "unknown")
        self.assertEqual(snapshot["recent_events"], [])

    def test_build_monitor_snapshot_extracts_latest_state(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            telemetry_path = f"{tmpdir}/runner.jsonl"
            event_path = f"{tmpdir}/events.jsonl"
            append_jsonl(
                telemetry_path,
                {
                    "ts": "2026-03-13T12:00:00+00:00",
                    "cycle": 7,
                    "price_source": "okx",
                    "symbol": "BTC_USDT",
                    "latency_ms": 3210.5,
                    "kill_switch": {"mode": "normal"},
                    "result": {
                        "placed_orders": 1,
                        "cancelled_orders": 1,
                        "quote": {"side": "buy", "price": 72000.1, "size_usd": 5.0},
                        "result": {"data": [{"ordId": "123"}]},
                        "events": [
                            {
                                "stage": "get_order_result",
                                "result": {"data": [{"state": "live"}]},
                            }
                        ],
                    },
                },
            )
            append_jsonl(
                event_path,
                {
                    "ts": "2026-03-13T12:00:01+00:00",
                    "cycle": 7,
                    "stage": "place_order_request",
                    "side": "buy",
                    "price": 72000.1,
                    "size_usd": 5.0,
                },
            )
            snapshot = build_monitor_snapshot(telemetry_path, event_path, recent_event_limit=5)
            rendered = render_monitor_snapshot(snapshot)

        self.assertEqual(snapshot["latest_cycle"]["order_id"], "123")
        self.assertEqual(snapshot["latest_cycle"]["order_state"], "live")
        self.assertIn("side=buy", rendered)
        self.assertIn("order_id=123", rendered)
        self.assertIn("stage=place_order_request", rendered)

    def test_watch_monitor_prints_once(self) -> None:
        outputs: list[str] = []
        with tempfile.TemporaryDirectory() as tmpdir:
            telemetry_path = f"{tmpdir}/runner.jsonl"
            event_path = f"{tmpdir}/events.jsonl"
            append_jsonl(
                telemetry_path,
                {
                    "ts": "2026-03-13T12:00:00+00:00",
                    "cycle": 1,
                    "price_source": "okx",
                    "symbol": "BTC_USDT",
                    "latency_ms": 100.0,
                    "kill_switch": {"mode": "normal"},
                    "result": {"placed_orders": 0, "cancelled_orders": 0, "events": []},
                },
            )
            code = watch_monitor(
                telemetry_path=telemetry_path,
                event_log_path=event_path,
                iterations=1,
                refresh_seconds=0,
                print_fn=outputs.append,
            )
        self.assertEqual(code, 0)
        self.assertEqual(len(outputs), 1)
        self.assertIn("[MONITOR]", outputs[0])

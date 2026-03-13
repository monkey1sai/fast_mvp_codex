from __future__ import annotations

import json
import tempfile
import unittest

from app.telemetry import append_jsonl


class TelemetryTests(unittest.TestCase):
    def test_append_jsonl_writes_single_line_json(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            path = f"{tmpdir}/events.jsonl"
            append_jsonl(path, {"cycle": 1, "result": {"placed_orders": 1}})
            with open(path, "r", encoding="utf-8") as handle:
                lines = handle.read().splitlines()
        self.assertEqual(len(lines), 1)
        payload = json.loads(lines[0])
        self.assertEqual(payload["cycle"], 1)
        self.assertEqual(payload["result"]["placed_orders"], 1)


if __name__ == "__main__":
    unittest.main()

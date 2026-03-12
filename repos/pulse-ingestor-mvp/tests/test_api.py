from __future__ import annotations

import os
import tempfile
import unittest
from pathlib import Path

from fastapi.testclient import TestClient
from app.services.decision_context import decision_context_payload


class ApiTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = Path(self.temp_dir.name) / "test.db"
        os.environ["PULSE_DB_PATH"] = str(self.db_path)

        from app.main import app

        self.client_manager = TestClient(app)
        self.client = self.client_manager.__enter__()

    def tearDown(self) -> None:
        self.client_manager.__exit__(None, None, None)
        os.environ.pop("PULSE_DB_PATH", None)
        self.temp_dir.cleanup()

    def test_healthz(self) -> None:
        response = self.client.get("/healthz")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "ok"})

    def test_ingest_email_is_idempotent(self) -> None:
        payload = {
            "source_message_id": "msg-42",
            "raw_from": "notifications@openai.com",
            "subject": "Daily pulse summary",
            "body": "From ChatGPT task update\nImportant action today\nRisk is still unclear\nReview the market changes",
            "received_at": "Thu, 12 Mar 2026 10:00:00 +0800",
        }

        first = self.client.post("/ingest/email", json=payload)
        second = self.client.post("/ingest/email", json=payload)

        self.assertEqual(first.status_code, 200)
        self.assertEqual(second.status_code, 200)
        self.assertTrue(first.json()["created"])
        self.assertFalse(second.json()["created"])
        self.assertEqual(first.json()["id"], second.json()["id"])
        self.assertEqual(first.json()["normalized_from"], "notifications@openai.com")

    def test_pulses_support_entropy_filter(self) -> None:
        low_payload = {
            "source_message_id": "msg-low",
            "raw_from": "notifications@openai.com",
            "subject": "[Task update] Daily summary",
            "body": "From ChatGPT task update\nsimple update",
            "received_at": "Thu, 12 Mar 2026 10:00:00 +0800",
        }
        high_payload = {
            "source_message_id": "msg-high",
            "raw_from": "notifications@openai.com",
            "subject": "[Task update] Urgent task warning",
            "body": "From ChatGPT task update\nImportant action today\nRisk is still unclear\nMaybe unknown deadline warning urgent action today",
            "received_at": "Thu, 12 Mar 2026 11:00:00 +0800",
        }

        self.client.post("/ingest/email", json=low_payload)
        self.client.post("/ingest/email", json=high_payload)

        response = self.client.get("/pulses?min_entropy=0.4")
        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(len(body), 1)
        self.assertEqual(body[0]["source_message_id"], "msg-high")
        self.assertGreater(body[0]["signals"]["decision_signal_score"], 0.0)

    def test_reject_non_target_email(self) -> None:
        payload = {
            "source_message_id": "msg-spam",
            "raw_from": "newsletter@example.com",
            "subject": "Weekend newsletter",
            "body": "simple update",
            "received_at": "Thu, 12 Mar 2026 12:00:00 +0800",
        }

        response = self.client.post("/ingest/email", json=payload)
        self.assertEqual(response.status_code, 400)

    def test_decision_context_returns_high_signal_items(self) -> None:
        payload = {
            "source_message_id": "msg-decision",
            "raw_from": "OpenAI <noreply@tm.openai.com>",
            "subject": "[Task update] Crypto 指數：極度恐懼 (18)",
            "body": "從 ChatGPT 更新任務\nCrypto 指數：極度恐懼 (18)\n指數 18（Extreme Fear）。首次讀取，暫無前次數據可比較。\nhttps://chatgpt.com/c/test",
            "received_at": "Thu, 12 Mar 2026 12:00:00 +0800",
        }
        self.client.post("/ingest/email", json=payload)
        response = self.client.get("/decision/context?limit=5&min_decision_signal=0.45")
        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(body["count"], 1)
        self.assertEqual(body["items"][0]["task_title"], "Crypto 指數：極度恐懼 (18)")

    def test_scheduler_status_endpoint(self) -> None:
        response = self.client.get("/scheduler/status")
        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertIn("enabled", body)
        self.assertIn("interval_seconds", body)

    def test_backfill_endpoint_returns_counts(self) -> None:
        from unittest.mock import patch

        with patch("app.main.backfill_mailbox_history", return_value=(2, 3)):
            response = self.client.post("/admin/ingest/backfill", json={"mailbox": "AI新聞脈動PLUS", "limit": 50})

        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(body["mailbox"], "AI新聞脈動PLUS")
        self.assertEqual(body["inserted"], 2)
        self.assertEqual(body["skipped"], 3)

    def test_mcp_decision_payload_helper(self) -> None:
        payload = {
            "source_message_id": "msg-mcp",
            "raw_from": "OpenAI <noreply@tm.openai.com>",
            "subject": "[Task update] AI SaaS opportunity",
            "body": "From ChatGPT task update\nFound five small AI SaaS opportunities with pricing ideas\nhttps://chatgpt.com/c/test-mcp",
            "received_at": "Thu, 12 Mar 2026 12:00:00 +0800",
        }
        self.client.post("/ingest/email", json=payload)
        context = decision_context_payload(limit=5, min_decision_signal=0.3)
        self.assertEqual(context["count"], 1)
        self.assertEqual(context["items"][0]["task_title"], "AI SaaS opportunity")


if __name__ == "__main__":
    unittest.main()

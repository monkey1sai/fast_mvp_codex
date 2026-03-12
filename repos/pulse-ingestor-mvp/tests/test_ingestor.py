from __future__ import annotations

import os
import unittest
from email.message import EmailMessage
from types import SimpleNamespace
from unittest.mock import patch

from app.services.ingestor import _encode_imap_mailbox_name, backfill_mailbox_history, poll_mailbox


class FakeMailbox:
    def __init__(self, raw_message: bytes) -> None:
        self.raw_message = raw_message
        self.copied: list[tuple[bytes, str]] = []
        self.stored: list[tuple[bytes, str, str]] = []
        self.expunge_calls = 0

    def login(self, username: str, password: str) -> tuple[str, list[bytes]]:
        return "OK", [b"logged-in"]

    def select(self, mailbox: str) -> tuple[str, list[bytes]]:
        return "OK", [b"1"]

    def search(self, charset: str | None, criteria: str) -> tuple[str, list[bytes]]:
        return "OK", [b"1"]

    def fetch(self, message_id: bytes, flags: str) -> tuple[str, list[tuple[bytes, bytes]]]:
        return "OK", [(b"1", self.raw_message)]

    def copy(self, message_id: bytes, target_mailbox: str) -> tuple[str, list[bytes]]:
        self.copied.append((message_id, target_mailbox))
        return "OK", [b"copied"]

    def store(self, message_id: bytes, operation: str, flags: str) -> tuple[str, list[bytes]]:
        self.stored.append((message_id, operation, flags))
        return "OK", [b"stored"]

    def expunge(self) -> tuple[str, list[bytes]]:
        self.expunge_calls += 1
        return "OK", [b"expunged"]

    def close(self) -> tuple[str, list[bytes]]:
        return "OK", [b"closed"]

    def logout(self) -> tuple[str, list[bytes]]:
        return "BYE", [b"logout"]


class IngestorTests(unittest.TestCase):
    def test_encode_imap_mailbox_name_supports_unicode(self) -> None:
        encoded = _encode_imap_mailbox_name("AI新聞脈動PLUS")
        self.assertIsInstance(encoded, bytes)
        self.assertTrue(encoded.startswith(b"AI&"))

    def setUp(self) -> None:
        self.original_env = os.environ.copy()
        os.environ["PULSE_IMAP_HOST"] = "imap.gmail.com"
        os.environ["PULSE_IMAP_PORT"] = "993"
        os.environ["PULSE_IMAP_USERNAME"] = "pulse@example.com"
        os.environ["PULSE_IMAP_PASSWORD"] = "secret"
        os.environ["PULSE_IMAP_MAILBOX"] = "INBOX"
        os.environ["PULSE_IMAP_PROCESSED_MAILBOX"] = "AI新聞脈動PLUS"
        os.environ["PULSE_IMAP_MOVE_ON_SUCCESS"] = "true"

    def tearDown(self) -> None:
        os.environ.clear()
        os.environ.update(self.original_env)

    def _build_email(self, subject: str, body: str) -> bytes:
        message = EmailMessage()
        message["From"] = "OpenAI <noreply@tm.openai.com>"
        message["Subject"] = subject
        message["Date"] = "Thu, 12 Mar 2026 12:00:00 +0800"
        message["Message-ID"] = "<msg-1@example.com>"
        message.set_content(body)
        return message.as_bytes()

    def test_poll_mailbox_moves_processed_email_to_ai_news_folder(self) -> None:
        fake_mailbox = FakeMailbox(
            self._build_email(
                "[Task update] Crypto 指數：極度恐懼 (18)",
                "從 ChatGPT 更新任務\nCrypto 指數：極度恐懼 (18)\nhttps://chatgpt.com/c/test",
            )
        )

        with (
            patch("app.services.ingestor.imaplib.IMAP4_SSL", return_value=fake_mailbox),
            patch("app.services.ingestor.insert_pulse_event", return_value=SimpleNamespace(created=True)),
        ):
            inserted, skipped = poll_mailbox()

        self.assertEqual((inserted, skipped), (1, 0))
        self.assertEqual(fake_mailbox.copied, [(b"1", _encode_imap_mailbox_name("AI新聞脈動PLUS"))])
        self.assertEqual(fake_mailbox.stored, [(b"1", "+FLAGS", "\\Seen \\Deleted")])
        self.assertEqual(fake_mailbox.expunge_calls, 1)

    def test_poll_mailbox_does_not_move_non_target_email(self) -> None:
        fake_mailbox = FakeMailbox(
            self._build_email(
                "Weekend newsletter",
                "simple update without task markers",
            )
        )

        with patch("app.services.ingestor.imaplib.IMAP4_SSL", return_value=fake_mailbox):
            inserted, skipped = poll_mailbox()

        self.assertEqual((inserted, skipped), (0, 1))
        self.assertEqual(fake_mailbox.copied, [])
        self.assertEqual(fake_mailbox.stored, [])
        self.assertEqual(fake_mailbox.expunge_calls, 0)

    def test_backfill_history_reads_processed_mailbox_without_moving_messages(self) -> None:
        fake_mailbox = FakeMailbox(
            self._build_email(
                "[Task update] AI SaaS opportunity",
                "From ChatGPT task update\nFound five small AI SaaS opportunities\nhttps://chatgpt.com/c/backfill",
            )
        )

        with (
            patch("app.services.ingestor.imaplib.IMAP4_SSL", return_value=fake_mailbox),
            patch("app.services.ingestor.insert_pulse_event", return_value=SimpleNamespace(created=True)),
        ):
            inserted, skipped = backfill_mailbox_history()

        self.assertEqual((inserted, skipped), (1, 0))
        self.assertEqual(fake_mailbox.copied, [])
        self.assertEqual(fake_mailbox.stored, [])
        self.assertEqual(fake_mailbox.expunge_calls, 0)


if __name__ == "__main__":
    unittest.main()

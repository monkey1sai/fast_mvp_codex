from __future__ import annotations

import email
import imaplib
from email.message import Message

from app.config import get_settings
from app.services.filters import is_target_pulse_email
from app.services.parser import parse_email_to_pulse
from app.services.storage import insert_pulse_event


def _extract_text_part(message: Message) -> str:
    if message.is_multipart():
        parts: list[str] = []
        for part in message.walk():
            content_type = part.get_content_type()
            if content_type != "text/plain":
                continue
            payload = part.get_payload(decode=True) or b""
            charset = part.get_content_charset() or "utf-8"
            parts.append(payload.decode(charset, errors="replace"))
        return "\n".join(parts).strip()

    payload = message.get_payload(decode=True) or b""
    charset = message.get_content_charset() or "utf-8"
    return payload.decode(charset, errors="replace").strip()


def poll_mailbox() -> tuple[int, int]:
    settings = get_settings()
    if not settings.imap_enabled:
        return 0, 0

    inserted = 0
    skipped = 0

    mailbox = imaplib.IMAP4_SSL(settings.imap_host, settings.imap_port)
    try:
        mailbox.login(settings.imap_username, settings.imap_password)
        mailbox.select(settings.imap_mailbox)
        status, data = mailbox.search(None, "UNSEEN")
        if status != "OK":
            return inserted, skipped

        ids = [item for item in data[0].split() if item][-settings.poll_max_messages :]
        for message_id in ids:
            status, payload = mailbox.fetch(message_id, "(RFC822)")
            if status != "OK" or not payload or not payload[0]:
                skipped += 1
                continue

            raw_bytes = payload[0][1]
            message = email.message_from_bytes(raw_bytes)
            source_message_id = message.get("Message-ID", message_id.decode("utf-8", errors="replace"))
            raw_from = message.get("From", "").strip()
            subject = message.get("Subject", "").strip()
            received_at = message.get("Date", "")
            body = _extract_text_part(message)
            if not is_target_pulse_email(raw_from=raw_from, subject=subject, body=body):
                skipped += 1
                continue

            event = parse_email_to_pulse(
                source_message_id=source_message_id,
                raw_from=raw_from,
                subject=subject,
                body=body,
                received_at=received_at,
            )
            result = insert_pulse_event(event)
            if result.created:
                inserted += 1
            else:
                skipped += 1
    finally:
        try:
            mailbox.close()
        except imaplib.IMAP4.error:
            pass
        mailbox.logout()

    return inserted, skipped

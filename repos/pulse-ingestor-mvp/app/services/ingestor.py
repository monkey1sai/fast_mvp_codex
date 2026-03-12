from __future__ import annotations

import email
import imaplib
import base64
from email.message import Message
from typing import Iterable

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


def _encode_imap_mailbox_name(mailbox_name: str) -> bytes | str:
    if mailbox_name.isascii():
        return mailbox_name

    chunks: list[str] = []
    buffer: list[str] = []

    def _flush_buffer() -> None:
        if not buffer:
            return
        encoded = "".join(buffer).encode("utf-16-be")
        token = base64.b64encode(encoded).decode("ascii").rstrip("=").replace("/", ",")
        chunks.append(f"&{token}-")
        buffer.clear()

    for char in mailbox_name:
        if ord(char) < 0x20 or ord(char) > 0x7E:
            buffer.append(char)
            continue
        _flush_buffer()
        chunks.append("&-" if char == "&" else char)

    _flush_buffer()
    return "".join(chunks).encode("ascii")


def _move_message_to_processed_mailbox(
    mailbox: imaplib.IMAP4_SSL,
    message_id: bytes,
    target_mailbox: str,
) -> bool:
    if not target_mailbox:
        return False

    copy_status, _ = mailbox.copy(message_id, _encode_imap_mailbox_name(target_mailbox))
    if copy_status != "OK":
        return False

    store_status, _ = mailbox.store(message_id, "+FLAGS", "\\Seen \\Deleted")
    if store_status != "OK":
        return False

    expunge_status, _ = mailbox.expunge()
    return expunge_status == "OK"


def _ingest_message_ids(
    mailbox: imaplib.IMAP4_SSL,
    *,
    message_ids: Iterable[bytes],
    move_on_success: bool,
    processed_mailbox: str,
) -> tuple[int, int]:
    inserted = 0
    skipped = 0

    for message_id in message_ids:
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

        if move_on_success:
            _move_message_to_processed_mailbox(
                mailbox=mailbox,
                message_id=message_id,
                target_mailbox=processed_mailbox,
            )

    return inserted, skipped


def _mailbox_search(
    mailbox: imaplib.IMAP4_SSL,
    *,
    mailbox_name: str,
    criteria: str,
    limit: int,
) -> list[bytes]:
    select_status, _ = mailbox.select(_encode_imap_mailbox_name(mailbox_name))
    if select_status != "OK":
        return []

    search_status, data = mailbox.search(None, criteria)
    if search_status != "OK":
        return []

    return [item for item in data[0].split() if item][-limit:]


def poll_mailbox() -> tuple[int, int]:
    settings = get_settings()
    if not settings.imap_enabled:
        return 0, 0

    mailbox = imaplib.IMAP4_SSL(settings.imap_host, settings.imap_port)
    try:
        mailbox.login(settings.imap_username, settings.imap_password)
        ids = _mailbox_search(
            mailbox,
            mailbox_name=settings.imap_mailbox,
            criteria="UNSEEN",
            limit=settings.poll_max_messages,
        )
        if not ids:
            return 0, 0

        return _ingest_message_ids(
            mailbox,
            message_ids=ids,
            move_on_success=settings.imap_move_on_success,
            processed_mailbox=settings.imap_processed_mailbox,
        )
    finally:
        try:
            mailbox.close()
        except imaplib.IMAP4.error:
            pass
        mailbox.logout()


def backfill_mailbox_history(
    *,
    mailbox_name: str | None = None,
    limit: int | None = None,
) -> tuple[int, int]:
    settings = get_settings()
    if not settings.imap_enabled:
        return 0, 0

    target_mailbox = mailbox_name or settings.imap_processed_mailbox
    target_limit = limit or settings.poll_max_messages

    mailbox = imaplib.IMAP4_SSL(settings.imap_host, settings.imap_port)
    try:
        mailbox.login(settings.imap_username, settings.imap_password)
        ids = _mailbox_search(
            mailbox,
            mailbox_name=target_mailbox,
            criteria="ALL",
            limit=target_limit,
        )
        if not ids:
            return 0, 0

        return _ingest_message_ids(
            mailbox,
            message_ids=ids,
            move_on_success=False,
            processed_mailbox=target_mailbox,
        )
    finally:
        try:
            mailbox.close()
        except imaplib.IMAP4.error:
            pass
        mailbox.logout()

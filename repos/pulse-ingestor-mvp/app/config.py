from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    db_path: str
    imap_host: str
    imap_port: int
    imap_username: str
    imap_password: str
    imap_mailbox: str
    poll_max_messages: int
    allowed_from_patterns: tuple[str, ...]
    allowed_subject_keywords: tuple[str, ...]
    allowed_body_keywords: tuple[str, ...]
    auto_poll_enabled: bool
    auto_poll_interval_seconds: int

    @property
    def imap_enabled(self) -> bool:
        return all([self.imap_host, self.imap_username, self.imap_password])


def get_settings() -> Settings:
    def _split_env(name: str, default: str) -> tuple[str, ...]:
        raw = os.getenv(name, default)
        return tuple(item.strip().lower() for item in raw.split(",") if item.strip())

    return Settings(
        db_path=os.getenv("PULSE_DB_PATH", "runtime/pulse.db"),
        imap_host=os.getenv("PULSE_IMAP_HOST", ""),
        imap_port=int(os.getenv("PULSE_IMAP_PORT", "993")),
        imap_username=os.getenv("PULSE_IMAP_USERNAME", ""),
        imap_password=os.getenv("PULSE_IMAP_PASSWORD", ""),
        imap_mailbox=os.getenv("PULSE_IMAP_MAILBOX", "INBOX"),
        poll_max_messages=int(os.getenv("PULSE_POLL_MAX_MESSAGES", "10")),
        allowed_from_patterns=_split_env(
            "PULSE_ALLOWED_FROM_PATTERNS",
            "openai,chatgpt",
        ),
        allowed_subject_keywords=_split_env(
            "PULSE_ALLOWED_SUBJECT_KEYWORDS",
            "[任務更新],[task update],task update",
        ),
        allowed_body_keywords=_split_env(
            "PULSE_ALLOWED_BODY_KEYWORDS",
            "從 chatgpt 更新任務,from chatgpt task update,chatgpt.com/c/,取消訂閱任務郵件,unsubscribe from task emails",
        ),
        auto_poll_enabled=os.getenv("PULSE_AUTO_POLL_ENABLED", "false").lower() in {"1", "true", "yes", "on"},
        auto_poll_interval_seconds=int(os.getenv("PULSE_AUTO_POLL_INTERVAL_SECONDS", "300")),
    )

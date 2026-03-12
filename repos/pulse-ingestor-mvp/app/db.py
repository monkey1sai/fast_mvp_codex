from __future__ import annotations

import sqlite3
from contextlib import closing
from typing import ContextManager
from pathlib import Path

from app.config import get_settings


SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS pulse_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_type TEXT NOT NULL,
    source_message_id TEXT NOT NULL UNIQUE,
    raw_from TEXT NOT NULL DEFAULT '',
    normalized_from TEXT NOT NULL DEFAULT '',
    received_at TEXT NOT NULL,
    task_title TEXT NOT NULL,
    raw_subject TEXT NOT NULL,
    decoded_subject TEXT NOT NULL DEFAULT '',
    raw_body TEXT NOT NULL,
    summary TEXT NOT NULL,
    source_url TEXT NOT NULL DEFAULT '',
    signals_json TEXT NOT NULL,
    entropy_score REAL NOT NULL,
    status TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_pulse_events_received_at ON pulse_events(received_at DESC);
CREATE INDEX IF NOT EXISTS idx_pulse_events_entropy_score ON pulse_events(entropy_score DESC);
CREATE INDEX IF NOT EXISTS idx_pulse_events_status ON pulse_events(status);
"""


def get_connection() -> ContextManager[sqlite3.Connection]:
    db_path = Path(get_settings().db_path)
    db_path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(db_path)
    connection.row_factory = sqlite3.Row
    return closing(connection)


def init_db() -> None:
    with get_connection() as connection:
        connection.executescript(SCHEMA_SQL)
        existing_columns = {
            row["name"]
            for row in connection.execute("PRAGMA table_info(pulse_events)").fetchall()
        }
        if "raw_from" not in existing_columns:
            connection.execute("ALTER TABLE pulse_events ADD COLUMN raw_from TEXT NOT NULL DEFAULT ''")
        if "normalized_from" not in existing_columns:
            connection.execute("ALTER TABLE pulse_events ADD COLUMN normalized_from TEXT NOT NULL DEFAULT ''")
        if "decoded_subject" not in existing_columns:
            connection.execute("ALTER TABLE pulse_events ADD COLUMN decoded_subject TEXT NOT NULL DEFAULT ''")
        if "source_url" not in existing_columns:
            connection.execute("ALTER TABLE pulse_events ADD COLUMN source_url TEXT NOT NULL DEFAULT ''")
        connection.commit()

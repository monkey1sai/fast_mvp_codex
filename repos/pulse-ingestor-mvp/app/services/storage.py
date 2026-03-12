from __future__ import annotations

import sqlite3
from dataclasses import dataclass

from app.db import get_connection
from app.models import PulseEvent


@dataclass(frozen=True)
class UpsertResult:
    row_id: int
    created: bool


def insert_pulse_event(event: PulseEvent) -> UpsertResult:
    with get_connection() as connection:
        cursor = connection.execute(
            """
            INSERT OR IGNORE INTO pulse_events (
                source_type,
                source_message_id,
                raw_from,
                normalized_from,
                received_at,
                task_title,
                raw_subject,
                decoded_subject,
                raw_body,
                summary,
                source_url,
                signals_json,
                entropy_score,
                status
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                event.source_type,
                event.source_message_id,
                event.raw_from,
                event.normalized_from,
                event.received_at,
                event.task_title,
                event.raw_subject,
                event.decoded_subject,
                event.raw_body,
                event.summary,
                event.source_url,
                event.signals_json,
                event.entropy_score,
                event.status,
            ),
        )
        connection.commit()
        if cursor.lastrowid:
            return UpsertResult(row_id=int(cursor.lastrowid), created=True)

    existing = get_pulse_event_by_source_message_id(event.source_message_id)
    return UpsertResult(row_id=int(existing["id"]) if existing else 0, created=False)


def get_pulse_event_by_id(pulse_id: int) -> sqlite3.Row | None:
    with get_connection() as connection:
        cursor = connection.execute(
            """
            SELECT id, source_type, source_message_id, raw_from, normalized_from, received_at, task_title, raw_subject,
                   decoded_subject, raw_body, summary, source_url, signals_json, entropy_score, status
            FROM pulse_events
            WHERE id = ?
            """,
            (pulse_id,),
        )
        return cursor.fetchone()


def get_pulse_event_by_source_message_id(source_message_id: str) -> sqlite3.Row | None:
    with get_connection() as connection:
        cursor = connection.execute(
            """
            SELECT id, source_type, source_message_id, raw_from, normalized_from, received_at, task_title, raw_subject,
                   decoded_subject, raw_body, summary, source_url, signals_json, entropy_score, status
            FROM pulse_events
            WHERE source_message_id = ?
            """,
            (source_message_id,),
        )
        return cursor.fetchone()


def list_pulse_events(
    *,
    limit: int = 20,
    source_message_id: str | None = None,
    status: str | None = None,
    source_type: str | None = None,
    min_entropy: float | None = None,
    min_decision_signal: float | None = None,
) -> list[sqlite3.Row]:
    query = """
        SELECT id, source_type, source_message_id, raw_from, normalized_from, received_at, task_title, raw_subject,
               decoded_subject, raw_body, summary, source_url, signals_json, entropy_score, status
        FROM pulse_events
    """
    where_clauses: list[str] = []
    params: list[object] = []
    if source_message_id:
        where_clauses.append("source_message_id = ?")
        params.append(source_message_id)
    if status:
        where_clauses.append("status = ?")
        params.append(status)
    if source_type:
        where_clauses.append("source_type = ?")
        params.append(source_type)
    if min_entropy is not None:
        where_clauses.append("entropy_score >= ?")
        params.append(min_entropy)
    if min_decision_signal is not None:
        where_clauses.append("CAST(json_extract(signals_json, '$.decision_signal_score') AS REAL) >= ?")
        params.append(min_decision_signal)
    if where_clauses:
        query += " WHERE " + " AND ".join(where_clauses)
    query += " ORDER BY id DESC LIMIT ?"
    params.append(limit)

    with get_connection() as connection:
        cursor = connection.execute(query, params)
        return list(cursor.fetchall())


def delete_non_target_pulse_events() -> int:
    with get_connection() as connection:
        cursor = connection.execute(
            """
            DELETE FROM pulse_events
            WHERE NOT (
                lower(raw_from) LIKE '%openai%'
                OR lower(raw_from) LIKE '%chatgpt%'
            )
            OR NOT (
                lower(raw_subject) LIKE '%task update%'
                OR lower(raw_subject) LIKE '%[任務更新]%'
                OR lower(raw_body) LIKE '%從 chatgpt 更新任務%'
                OR lower(raw_body) LIKE '%from chatgpt task update%'
                OR lower(raw_body) LIKE '%unsubscribe from task emails%'
                OR lower(raw_body) LIKE '%取消訂閱任務郵件%'
            )
            """
        )
        connection.commit()
        return int(cursor.rowcount)


def update_pulse_event(pulse_id: int, event: PulseEvent) -> None:
    with get_connection() as connection:
        connection.execute(
            """
            UPDATE pulse_events
            SET source_type = ?,
                source_message_id = ?,
                raw_from = ?,
                normalized_from = ?,
                received_at = ?,
                task_title = ?,
                raw_subject = ?,
                decoded_subject = ?,
                raw_body = ?,
                summary = ?,
                source_url = ?,
                signals_json = ?,
                entropy_score = ?,
                status = ?
            WHERE id = ?
            """,
            (
                event.source_type,
                event.source_message_id,
                event.raw_from,
                event.normalized_from,
                event.received_at,
                event.task_title,
                event.raw_subject,
                event.decoded_subject,
                event.raw_body,
                event.summary,
                event.source_url,
                event.signals_json,
                event.entropy_score,
                event.status,
                pulse_id,
            ),
        )
        connection.commit()

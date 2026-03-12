from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class PulseEvent:
    source_type: str
    source_message_id: str
    raw_from: str
    normalized_from: str
    received_at: str
    task_title: str
    raw_subject: str
    decoded_subject: str
    raw_body: str
    summary: str
    source_url: str
    signals_json: str
    entropy_score: float
    status: str = "new"

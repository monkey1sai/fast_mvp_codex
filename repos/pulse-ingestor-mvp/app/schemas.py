from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class EmailIngestRequest(BaseModel):
    source_message_id: str = Field(..., min_length=1)
    raw_from: str = ""
    subject: str = Field(..., min_length=1)
    body: str = Field(..., min_length=1)
    received_at: str = Field(..., min_length=1)


class PulseEventResponse(BaseModel):
    id: int
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
    signals: dict[str, Any]
    entropy_score: float
    status: str


class EmailIngestResponse(PulseEventResponse):
    created: bool


class PollResponse(BaseModel):
    inserted: int
    skipped: int


class BackfillRequest(BaseModel):
    mailbox: str | None = None
    limit: int | None = Field(default=None, ge=1, le=1000)


class BackfillResponse(BaseModel):
    mailbox: str
    inserted: int
    skipped: int


class CleanupResponse(BaseModel):
    deleted: int


class RehydrateResponse(BaseModel):
    updated: int


class DecisionContextResponse(BaseModel):
    generated_at: float
    count: int
    items: list[dict[str, Any]]


class SchedulerStatusResponse(BaseModel):
    enabled: bool
    interval_seconds: int
    started: bool
    runs: int
    last_started_at: float | None
    last_finished_at: float | None
    last_inserted: int
    last_skipped: int
    last_error: str

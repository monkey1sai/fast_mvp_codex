from __future__ import annotations

import json
import time
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException

from app.config import get_settings
from app.db import init_db
from app.schemas import (
    CleanupResponse,
    DecisionContextResponse,
    EmailIngestRequest,
    EmailIngestResponse,
    PollResponse,
    PulseEventResponse,
    RehydrateResponse,
    SchedulerStatusResponse,
)
from app.services.filters import is_target_pulse_email
from app.services.ingestor import poll_mailbox
from app.services.parser import parse_email_to_pulse
from app.services.scheduler import get_scheduler_snapshot, start_scheduler, stop_scheduler
from app.services.storage import (
    delete_non_target_pulse_events,
    get_pulse_event_by_id,
    get_pulse_event_by_source_message_id,
    insert_pulse_event,
    list_pulse_events,
    update_pulse_event,
)


@asynccontextmanager
async def lifespan(_: FastAPI):
    init_db()
    start_scheduler()
    yield
    stop_scheduler()


def _to_response(row: object) -> PulseEventResponse:
    return PulseEventResponse(
        id=row["id"],
        source_type=row["source_type"],
        source_message_id=row["source_message_id"],
        raw_from=row["raw_from"],
        normalized_from=row["normalized_from"],
        received_at=row["received_at"],
        task_title=row["task_title"],
        raw_subject=row["raw_subject"],
        decoded_subject=row["decoded_subject"],
        raw_body=row["raw_body"],
        summary=row["summary"],
        source_url=row["source_url"],
        signals=json.loads(row["signals_json"]),
        entropy_score=row["entropy_score"],
        status=row["status"],
    )


app = FastAPI(title="Pulse Ingestor MVP", version="0.1.0", lifespan=lifespan)


@app.get("/healthz")
def healthz() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/pulses", response_model=list[PulseEventResponse])
def get_pulses(
    limit: int = 20,
    status: str | None = None,
    source_type: str | None = None,
    min_entropy: float | None = None,
    min_decision_signal: float | None = None,
) -> list[PulseEventResponse]:
    rows = list_pulse_events(
        limit=limit,
        status=status,
        source_type=source_type,
        min_entropy=min_entropy,
        min_decision_signal=min_decision_signal,
    )
    return [_to_response(row) for row in rows]


@app.get("/pulses/{pulse_id}", response_model=PulseEventResponse)
def get_pulse(pulse_id: int) -> PulseEventResponse:
    row = get_pulse_event_by_id(pulse_id)
    if row is None:
        raise HTTPException(status_code=404, detail="pulse not found")
    return _to_response(row)


@app.post("/ingest/email", response_model=EmailIngestResponse)
def ingest_email(payload: EmailIngestRequest) -> EmailIngestResponse:
    if not is_target_pulse_email(raw_from=payload.raw_from, subject=payload.subject, body=payload.body):
        raise HTTPException(status_code=400, detail="email does not match ChatGPT pulse filters")
    event = parse_email_to_pulse(
        source_message_id=payload.source_message_id,
        raw_from=payload.raw_from,
        subject=payload.subject,
        body=payload.body,
        received_at=payload.received_at,
    )
    result = insert_pulse_event(event)
    row = get_pulse_event_by_source_message_id(payload.source_message_id)
    if row is None:
        raise HTTPException(status_code=500, detail="insert failed")
    return EmailIngestResponse(created=result.created, **_to_response(row).model_dump())


@app.post("/ingest/poll", response_model=PollResponse)
def ingest_from_mailbox() -> PollResponse:
    inserted, skipped = poll_mailbox()
    return PollResponse(inserted=inserted, skipped=skipped)


@app.delete("/admin/pulses/non-target", response_model=CleanupResponse)
def cleanup_non_target_pulses() -> CleanupResponse:
    deleted = delete_non_target_pulse_events()
    return CleanupResponse(deleted=deleted)


@app.post("/admin/pulses/rehydrate", response_model=RehydrateResponse)
def rehydrate_pulses() -> RehydrateResponse:
    rows = list_pulse_events(limit=1000)
    updated = 0
    for row in rows:
        event = parse_email_to_pulse(
            source_message_id=row["source_message_id"],
            raw_from=row["raw_from"],
            subject=row["raw_subject"],
            body=row["raw_body"],
            received_at=row["received_at"],
        )
        update_pulse_event(int(row["id"]), event)
        updated += 1
    return RehydrateResponse(updated=updated)


@app.get("/decision/context", response_model=DecisionContextResponse)
def get_decision_context(limit: int = 5, min_decision_signal: float = 0.5) -> DecisionContextResponse:
    rows = list_pulse_events(limit=limit, min_decision_signal=min_decision_signal)
    items = []
    for row in rows:
        response = _to_response(row)
        items.append(
            {
                "id": response.id,
                "task_title": response.task_title,
                "summary": response.summary,
                "source_url": response.source_url,
                "received_at": response.received_at,
                "entropy_score": response.entropy_score,
                "decision_signal_score": response.signals.get("decision_signal_score", 0.0),
                "tags": response.signals.get("tags", []),
            }
        )
    return DecisionContextResponse(generated_at=time.time(), count=len(items), items=items)


@app.get("/scheduler/status", response_model=SchedulerStatusResponse)
def scheduler_status() -> SchedulerStatusResponse:
    return SchedulerStatusResponse(**get_scheduler_snapshot())

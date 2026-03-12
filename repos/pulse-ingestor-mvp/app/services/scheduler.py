from __future__ import annotations

import threading
import time
from dataclasses import dataclass, field

from app.config import get_settings
from app.services.ingestor import poll_mailbox


@dataclass
class SchedulerState:
    thread: threading.Thread | None = None
    stop_event: threading.Event = field(default_factory=threading.Event)
    started: bool = False
    last_started_at: float | None = None
    last_finished_at: float | None = None
    last_inserted: int = 0
    last_skipped: int = 0
    runs: int = 0
    last_error: str = ""


STATE = SchedulerState()


def get_scheduler_snapshot() -> dict[str, object]:
    settings = get_settings()
    return {
        "enabled": settings.auto_poll_enabled,
        "interval_seconds": settings.auto_poll_interval_seconds,
        "started": STATE.started,
        "runs": STATE.runs,
        "last_started_at": STATE.last_started_at,
        "last_finished_at": STATE.last_finished_at,
        "last_inserted": STATE.last_inserted,
        "last_skipped": STATE.last_skipped,
        "last_error": STATE.last_error,
    }


def _run_loop() -> None:
    settings = get_settings()
    while not STATE.stop_event.is_set():
        STATE.last_started_at = time.time()
        try:
            inserted, skipped = poll_mailbox()
            STATE.last_inserted = inserted
            STATE.last_skipped = skipped
            STATE.last_error = ""
        except Exception as exc:  # pragma: no cover - defensive runtime guard
            STATE.last_error = str(exc)
        finally:
            STATE.runs += 1
            STATE.last_finished_at = time.time()
        if STATE.stop_event.wait(settings.auto_poll_interval_seconds):
            break


def start_scheduler() -> None:
    settings = get_settings()
    if not settings.auto_poll_enabled or STATE.started:
        return
    STATE.stop_event.clear()
    STATE.thread = threading.Thread(target=_run_loop, name="pulse-auto-poll", daemon=True)
    STATE.thread.start()
    STATE.started = True


def stop_scheduler() -> None:
    if not STATE.started:
        return
    STATE.stop_event.set()
    if STATE.thread is not None:
        STATE.thread.join(timeout=1.0)
    STATE.thread = None
    STATE.started = False

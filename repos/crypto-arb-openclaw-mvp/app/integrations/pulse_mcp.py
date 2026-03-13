from __future__ import annotations

from app.models import PulseSignal


def pulse_signals_from_context(payload: dict) -> list[PulseSignal]:
    items = payload.get("items", payload.get("pulses", []))
    signals: list[PulseSignal] = []
    for item in items:
        signals.append(
            PulseSignal(
                task_title=item.get("task_title", ""),
                summary=item.get("summary", ""),
                entropy_score=float(item.get("entropy_score", 0.0)),
                decision_signal_score=float(item.get("decision_signal_score", 0.0)),
                tags=list(item.get("tags", [])),
            )
        )
    return signals

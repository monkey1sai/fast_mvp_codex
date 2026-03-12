from __future__ import annotations

import json

from app.models import PulseEvent
from app.services.normalizer import clean_task_title, decode_mime_header, extract_first_url, extract_task_body, normalize_from_header
from app.services.scorer import score_pulse_text


def _extract_summary(body: str) -> str:
    lines = [line.strip() for line in body.splitlines() if line.strip()]
    if not lines:
        return ""
    return " ".join(lines[:3])[:500]


def _extract_tags(subject: str, body: str) -> list[str]:
    tags: list[str] = []
    haystack = f"{subject}\n{body}".lower()
    for keyword in ("daily", "weekly", "alert", "summary", "market", "task", "decision", "crypto", "saas", "lead", "trend", "fear", "任務", "更新", "機會"):
        if keyword in haystack:
            tags.append(keyword)
    return sorted(set(tags))


def parse_email_to_pulse(
    *,
    source_message_id: str,
    raw_from: str,
    subject: str,
    body: str,
    received_at: str,
) -> PulseEvent:
    normalized_from, _ = normalize_from_header(raw_from)
    decoded_subject = decode_mime_header(subject)
    normalized_body = extract_task_body(body) or body
    summary = _extract_summary(normalized_body)
    scores = score_pulse_text(subject=decoded_subject, body=normalized_body, summary=summary)
    signals = {
        "tags": _extract_tags(decoded_subject, normalized_body),
        "novelty_score": scores["novelty_score"],
        "uncertainty_score": scores["uncertainty_score"],
        "priority_score": scores["priority_score"],
        "market_signal_score": scores["market_signal_score"],
        "change_signal_score": scores["change_signal_score"],
        "decision_signal_score": scores["decision_signal_score"],
    }
    return PulseEvent(
        source_type="chatgpt_task_email",
        source_message_id=source_message_id,
        raw_from=raw_from,
        normalized_from=normalized_from,
        received_at=received_at,
        task_title=clean_task_title(decoded_subject, normalized_body),
        raw_subject=subject,
        decoded_subject=decoded_subject,
        raw_body=normalized_body,
        summary=summary,
        source_url=extract_first_url(body) or "",
        signals_json=json.dumps(signals, ensure_ascii=False),
        entropy_score=scores["entropy_score"],
    )

from __future__ import annotations

import re


def _clamp(value: float) -> float:
    return max(0.0, min(1.0, round(value, 3)))


def score_pulse_text(*, subject: str, body: str, summary: str) -> dict[str, float]:
    text = f"{subject}\n{body}\n{summary}".lower()
    words = [word for word in re.findall(r"[a-z0-9\u4e00-\u9fff\-]{2,}", text) if len(word) > 1]
    unique_words = set(words)
    unique_ratio = len(unique_words) / max(len(words), 1)
    novelty_score = _clamp(min((len(unique_words) / 40.0) * 0.6 + unique_ratio * 0.4, 1.0))

    uncertainty_hits = sum(text.count(token) for token in ("maybe", "unclear", "unknown", "risk", "warning", "恐懼", "風險"))
    uncertainty_score = _clamp(uncertainty_hits / 4.0)

    priority_hits = sum(text.count(token) for token in ("urgent", "important", "action", "today", "deadline", "立即", "今日"))
    priority_score = _clamp(priority_hits / 4.0)

    market_hits = sum(text.count(token) for token in ("market", "crypto", "saas", "lead", "pricing", "trend", "指數", "機會"))
    market_signal_score = _clamp(market_hits / 4.0)

    change_hits = sum(text.count(token) for token in ("new", "update", "found", "change", "首次", "發現", "更新"))
    change_signal_score = _clamp(change_hits / 4.0)

    decision_signal_score = _clamp(
        novelty_score * 0.30
        + priority_score * 0.25
        + uncertainty_score * 0.20
        + market_signal_score * 0.15
        + change_signal_score * 0.10
    )
    entropy_score = _clamp(
        novelty_score * 0.35
        + uncertainty_score * 0.25
        + priority_score * 0.15
        + market_signal_score * 0.10
        + change_signal_score * 0.15
    )
    return {
        "novelty_score": novelty_score,
        "uncertainty_score": uncertainty_score,
        "priority_score": priority_score,
        "market_signal_score": market_signal_score,
        "change_signal_score": change_signal_score,
        "decision_signal_score": decision_signal_score,
        "entropy_score": entropy_score,
    }

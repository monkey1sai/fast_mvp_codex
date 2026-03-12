from __future__ import annotations

from app.config import get_settings
from app.services.normalizer import decode_mime_header


def is_target_pulse_email(*, raw_from: str, subject: str, body: str) -> bool:
    settings = get_settings()
    from_text = raw_from.lower()
    subject_text = decode_mime_header(subject).lower()
    body_text = body.lower()

    from_match = any(pattern in from_text for pattern in settings.allowed_from_patterns)
    subject_match = any(pattern in subject_text for pattern in settings.allowed_subject_keywords)
    body_match = any(pattern in body_text for pattern in settings.allowed_body_keywords)

    # Require OpenAI/ChatGPT sender signal plus either subject/body task marker.
    return from_match and (subject_match or body_match)

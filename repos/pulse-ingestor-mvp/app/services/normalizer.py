from __future__ import annotations

import re
from email.header import decode_header
from email.utils import parseaddr


def decode_mime_header(value: str) -> str:
    if not value:
        return ""
    parts: list[str] = []
    for chunk, encoding in decode_header(value):
        if isinstance(chunk, bytes):
            codec = encoding or "utf-8"
            parts.append(chunk.decode(codec, errors="replace"))
        else:
            parts.append(chunk)
    return "".join(parts).strip()


def normalize_from_header(value: str) -> tuple[str, str]:
    display_name, address = parseaddr(decode_mime_header(value))
    normalized = display_name.strip() or address.strip()
    return normalized, address.strip().lower()


def extract_first_url(text: str) -> str | None:
    match = re.search(r"https?://[^\s>]+", text)
    return match.group(0) if match else None


def clean_task_title(subject: str, body: str) -> str:
    cleaned_subject = decode_mime_header(subject)
    cleaned_subject = re.sub(r"^\[(?:任務更新|task update)\]\s*", "", cleaned_subject, flags=re.IGNORECASE).strip()
    if cleaned_subject:
        return cleaned_subject[:160]

    lines = [line.strip() for line in body.splitlines() if line.strip()]
    for line in lines:
        if "從 chatgpt 更新任務" in line.lower():
            continue
        return re.sub(r"\s+", " ", line)[:160]
    return "untitled-pulse"


def extract_task_body(body: str) -> str:
    lines = [line.strip() for line in body.splitlines() if line.strip()]
    if not lines:
        return ""

    filtered: list[str] = []
    for line in lines:
        lower = line.lower()
        if "從 chatgpt 更新任務" in lower:
            continue
        if "unsubscribe from task emails" in lower or "取消訂閱任務郵件" in lower:
            continue
        if "help center" in lower or "服務條款" in lower or "privacy" in lower:
            continue
        if line.startswith("http://") or line.startswith("https://"):
            continue
        filtered.append(line)
    return "\n".join(filtered).strip()

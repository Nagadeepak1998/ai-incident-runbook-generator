from __future__ import annotations

import re

SECRET_PATTERNS = [
    re.compile(r"(?i)\b(bearer\s+)[a-z0-9._\-=/+]{12,}"),
    re.compile(r"(?i)\b(api[_-]?key|token|password|secret)\s*[:=]\s*['\"]?[^'\"\s,;]+"),
    re.compile(r"\b[A-Za-z0-9_]{20,}\.[A-Za-z0-9_]{10,}\.[A-Za-z0-9_\-]{10,}\b"),
]


def redact_text(value: str) -> tuple[str, int]:
    redacted = value
    count = 0
    for pattern in SECRET_PATTERNS:
        redacted, replacements = pattern.subn(lambda match: _replacement(match.group(0)), redacted)
        count += replacements
    return redacted, count


def redact_many(values: list[str]) -> tuple[list[str], int]:
    output: list[str] = []
    total = 0
    for value in values:
        redacted, count = redact_text(value)
        output.append(redacted)
        total += count
    return output, total


def _replacement(raw: str) -> str:
    if raw.lower().startswith("bearer "):
        return "Bearer [REDACTED]"
    if "=" in raw:
        return f"{raw.split('=', 1)[0]}=[REDACTED]"
    if ":" in raw:
        return f"{raw.split(':', 1)[0]}: [REDACTED]"
    return "[REDACTED]"

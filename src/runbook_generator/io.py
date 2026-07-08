from __future__ import annotations

import json
from pathlib import Path

from runbook_generator.models import GeneratedRunbook, Incident, RunbookReview, RunbookSection


def load_incident(path: Path) -> Incident:
    return Incident.model_validate_json(path.read_text())


def load_runbooks(path: Path) -> list[RunbookSection]:
    raw = json.loads(path.read_text())
    return [RunbookSection.model_validate(item) for item in raw["sections"]]


def load_generated_runbook(path: Path) -> GeneratedRunbook:
    return GeneratedRunbook.model_validate_json(path.read_text())


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")


def render_markdown(draft: GeneratedRunbook) -> str:
    lines = [
        f"# Incident Runbook: {draft.service}",
        "",
        f"- Title: {draft.title}",
        f"- Severity: `{draft.severity}`",
        f"- Confidence: `{draft.confidence}`",
        f"- Status: `{draft.status}`",
        f"- Redactions: `{draft.redaction_count}`",
        "",
        "## Summary",
        "",
        draft.summary,
        "",
        "## Likely Cause",
        "",
        draft.likely_cause,
        "",
        "## Immediate Checks",
        "",
    ]
    lines.extend(f"1. {item}" for item in draft.immediate_checks)
    lines.extend(["", "## Recommended Actions", ""])
    lines.extend(f"1. {item}" for item in draft.recommended_actions)
    lines.extend(["", "## Evidence", ""])
    lines.extend(f"- {item}" for item in draft.evidence)
    lines.extend(["", "## Matched Runbooks", ""])
    lines.extend(
        f"- `{match.id}`: {match.title} (score={match.score})" for match in draft.matched_sections
    )
    lines.extend(["", "## Escalation", "", draft.escalation, ""])
    return "\n".join(lines)


def render_review_markdown(review: RunbookReview) -> str:
    lines = [
        f"# Runbook Readiness Review: {review.service}",
        "",
        f"- Title: {review.title}",
        f"- Severity: `{review.severity}`",
        f"- Decision: `{review.decision}`",
        f"- Readiness score: `{review.readiness_score}/100`",
        f"- Human approval required: `{str(review.required_human_approval).lower()}`",
        "",
        "## Summary",
        "",
        review.summary,
        "",
        "## Findings",
        "",
    ]
    lines.extend(
        (
            f"- `{finding.severity}` `{finding.code}`: {finding.message} "
            f"Recommendation: {finding.recommendation}"
        )
        for finding in review.findings
    )
    lines.append("")
    return "\n".join(lines)


def write_text(path: Path, body: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body + "\n", encoding="utf-8")

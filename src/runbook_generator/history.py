from __future__ import annotations

import json
from pathlib import Path

from runbook_generator.generator import generate_runbook
from runbook_generator.io import load_incident, load_runbooks
from runbook_generator.models import (
    ReviewedRunbookWindow,
    RunbookHistoryReview,
    RunbookHistoryWindow,
)
from runbook_generator.review import review_runbook


def load_history_manifest(path: Path) -> list[RunbookHistoryWindow]:
    raw = json.loads(path.read_text())
    windows: list[RunbookHistoryWindow] = []
    for item in raw["windows"]:
        incident = load_incident(path.parent / item["incident_path"])
        sections = load_runbooks(path.parent / item["runbooks_path"])
        draft = generate_runbook(
            incident,
            sections,
            min_confidence=float(item.get("min_confidence", 0.2)),
        )
        windows.append(
            RunbookHistoryWindow(
                run_id=item["run_id"],
                generated_at=item["generated_at"],
                runbook=draft,
            )
        )
    return windows


def review_history(
    windows: list[RunbookHistoryWindow],
    min_confidence: float = 0.35,
) -> RunbookHistoryReview:
    reviewed: list[ReviewedRunbookWindow] = []
    recommendations: list[str] = []

    for window in windows:
        report = review_runbook(window.runbook, min_confidence=min_confidence)
        reviewed.append(
            ReviewedRunbookWindow(
                run_id=window.run_id,
                generated_at=window.generated_at,
                service=window.runbook.service,
                severity=window.runbook.severity,
                confidence=window.runbook.confidence,
                decision=report.decision,
                readiness_score=report.readiness_score,
                redaction_count=window.runbook.redaction_count,
                finding_codes=[finding.code for finding in report.findings],
            )
        )

    blocked = sum(1 for window in reviewed if window.decision == "block")
    needs_review = sum(1 for window in reviewed if window.decision == "review")
    approvals = sum(
        1 for window in reviewed if "approval_required" in set(window.finding_codes)
    )
    redactions = sum(window.redaction_count for window in reviewed)
    status = _status(blocked, needs_review)

    if blocked:
        recommendations.append("Route blocked drafts to an incident commander before handoff.")
    if approvals:
        recommendations.append("Keep human approval explicit for SEV1 and SEV2 drafts.")
    if redactions:
        recommendations.append("Attach sanitized artifacts instead of raw alert or log evidence.")
    if needs_review and not blocked:
        recommendations.append("Resolve review findings before treating the draft as on-call ready.")
    if not recommendations:
        recommendations.append("Continue sampling generated runbooks for quality drift.")

    latest = reviewed[-1] if reviewed else None
    return RunbookHistoryReview(
        status=status,
        reviewed_windows=len(reviewed),
        blocked_windows=blocked,
        review_windows=needs_review,
        approval_required_windows=approvals,
        total_redactions=redactions,
        latest_decision=latest.decision if latest else "none",
        latest_service=latest.service if latest else "none",
        summary=_summary(status, blocked, needs_review, len(reviewed), redactions),
        windows=reviewed,
        recommendations=recommendations,
    )


def _status(blocked: int, needs_review: int) -> str:
    if blocked:
        return "block"
    if needs_review:
        return "review"
    return "pass"


def _summary(
    status: str,
    blocked: int,
    needs_review: int,
    reviewed: int,
    redactions: int,
) -> str:
    return (
        f"Runbook quality history is {status}: {reviewed} window(s), "
        f"{blocked} blocked, {needs_review} needing review, {redactions} redaction(s)."
    )

from __future__ import annotations

from runbook_generator.models import GeneratedRunbook, ReviewFinding, RunbookReview


def review_runbook(draft: GeneratedRunbook, min_confidence: float = 0.35) -> RunbookReview:
    findings: list[ReviewFinding] = []

    if draft.status != "ready" or draft.confidence < min_confidence:
        findings.append(
            ReviewFinding(
                code="low_confidence",
                severity="blocker",
                message=f"Runbook confidence is {draft.confidence:.3f}.",
                recommendation="Add stronger service-specific evidence or route to human review.",
            )
        )
    if not draft.matched_sections:
        findings.append(
            ReviewFinding(
                code="no_matched_runbook",
                severity="blocker",
                message="No approved runbook section was matched.",
                recommendation="Attach an approved procedure before using this draft during an incident.",
            )
        )
    if len(draft.evidence) < 3:
        findings.append(
            ReviewFinding(
                code="thin_evidence",
                severity="warn",
                message="The draft has fewer than three evidence lines.",
                recommendation="Add alert, log, metric, or recent-change evidence before handoff.",
            )
        )
    if len(draft.immediate_checks) < 3:
        findings.append(
            ReviewFinding(
                code="thin_checks",
                severity="warn",
                message="The draft has fewer than three immediate checks.",
                recommendation="Add concrete checks for health, dependency status, and recent changes.",
            )
        )
    if len(draft.recommended_actions) < 3:
        findings.append(
            ReviewFinding(
                code="thin_actions",
                severity="warn",
                message="The draft has fewer than three recommended actions.",
                recommendation="Add owner assignment, containment, and rollback or mitigation guidance.",
            )
        )
    if not draft.escalation.strip():
        findings.append(
            ReviewFinding(
                code="missing_escalation",
                severity="blocker",
                message="The draft does not include an escalation path.",
                recommendation="Add a named team or role for escalation.",
            )
        )
    if draft.severity in {"sev1", "sev2"}:
        findings.append(
            ReviewFinding(
                code="approval_required",
                severity="warn",
                message=f"{draft.severity.upper()} incident drafts require human approval.",
                recommendation="Have the incident commander approve rollback, customer messaging, and closure.",
            )
        )
    if draft.redaction_count:
        findings.append(
            ReviewFinding(
                code="redactions_applied",
                severity="info",
                message=f"{draft.redaction_count} sensitive value(s) were redacted.",
                recommendation="Keep the sanitized artifact attached to the incident record.",
            )
        )

    decision = _decision(findings)
    score = _score(findings)
    return RunbookReview(
        service=draft.service,
        title=draft.title,
        severity=draft.severity,
        decision=decision,
        readiness_score=score,
        summary=_summary(decision, score, draft),
        findings=findings,
        required_human_approval=any(finding.code == "approval_required" for finding in findings),
    )


def _decision(findings: list[ReviewFinding]) -> str:
    if any(finding.severity == "blocker" for finding in findings):
        return "block"
    if any(finding.severity == "warn" for finding in findings):
        return "review"
    return "approve"


def _score(findings: list[ReviewFinding]) -> int:
    score = 100
    for finding in findings:
        if finding.severity == "blocker":
            score -= 30
        elif finding.severity == "warn":
            score -= 10
        else:
            score -= 2
    return max(0, score)


def _summary(decision: str, score: int, draft: GeneratedRunbook) -> str:
    return (
        f"{draft.service} {draft.severity} runbook readiness is {decision} "
        f"with score {score}/100."
    )

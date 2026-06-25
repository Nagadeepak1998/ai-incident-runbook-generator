from __future__ import annotations

from runbook_generator.models import GeneratedRunbook, Incident, RunbookSection
from runbook_generator.redaction import redact_many
from runbook_generator.retriever import rank_sections


def generate_runbook(
    incident: Incident,
    sections: list[RunbookSection],
    min_confidence: float = 0.2,
) -> GeneratedRunbook:
    sanitized_alerts, alert_redactions = redact_many(incident.alerts)
    sanitized_logs, log_redactions = redact_many(incident.logs)
    sanitized_changes, change_redactions = redact_many(incident.recent_changes)
    sanitized_incident = incident.model_copy(
        update={
            "alerts": sanitized_alerts,
            "logs": sanitized_logs,
            "recent_changes": sanitized_changes,
        }
    )

    matches = rank_sections(sanitized_incident, sections)
    top_section = _lookup_section(matches[0].id, sections) if matches else None
    confidence = _confidence(matches)
    status = "ready" if confidence >= min_confidence else "needs_human_review"

    checks = top_section.checks if top_section else ["Confirm alert source and impacted service."]
    actions = top_section.actions if top_section else ["Open an incident channel and assign an owner."]
    likely_cause = _likely_cause(sanitized_incident, top_section)
    risk_flags = _risk_flags(sanitized_incident, confidence)

    return GeneratedRunbook(
        service=sanitized_incident.service,
        title=sanitized_incident.title,
        severity=sanitized_incident.severity,
        confidence=confidence,
        summary=_summary(sanitized_incident, status),
        likely_cause=likely_cause,
        immediate_checks=checks[:5],
        recommended_actions=actions[:5],
        escalation=top_section.escalation if top_section else "Escalate to the on-call platform lead.",
        evidence=[*sanitized_alerts[:3], *sanitized_logs[:3], *sanitized_changes[:2]],
        matched_sections=matches,
        risk_flags=risk_flags,
        redaction_count=alert_redactions + log_redactions + change_redactions,
        status=status,
    )


def _lookup_section(section_id: str, sections: list[RunbookSection]) -> RunbookSection | None:
    return next((section for section in sections if section.id == section_id), None)


def _confidence(matches: list) -> float:
    if not matches:
        return 0.0
    top_score = matches[0].score
    total = sum(match.score for match in matches) or top_score
    return round(min(0.98, top_score / total + min(top_score / 50, 0.35)), 3)


def _summary(incident: Incident, status: str) -> str:
    return (
        f"{incident.severity.upper()} incident for {incident.service}: {incident.title}. "
        f"Runbook status is {status} based on sanitized alerts and matched procedures."
    )


def _likely_cause(incident: Incident, section: RunbookSection | None) -> str:
    if section:
        return f"Likely aligned with runbook '{section.title}'."
    if incident.recent_changes:
        return "No strong runbook match; recent changes should be reviewed first."
    return "No strong runbook match; start with service health, dependencies, and recent deploys."


def _risk_flags(incident: Incident, confidence: float) -> list[str]:
    flags: list[str] = []
    if incident.severity in {"sev1", "sev2"}:
        flags.append("high_severity_requires_human_approval")
    if confidence < 0.35:
        flags.append("low_retrieval_confidence")
    if any("rollback" in change.lower() for change in incident.recent_changes):
        flags.append("rollback_already_attempted")
    if not incident.logs:
        flags.append("missing_log_evidence")
    return flags


from __future__ import annotations

from datetime import datetime

from runbook_generator.models import ExecutionFinding, ExecutionManifest, ExecutionReview


def review_execution(manifest: ExecutionManifest) -> ExecutionReview:
    reference_time = _timestamp(manifest.reference_time)
    findings: list[ExecutionFinding] = []
    expired_steps = 0

    for step in manifest.steps:
        expired = _timestamp(step.expires_at) < reference_time
        if expired:
            expired_steps += 1
        if not step.owner.strip():
            findings.append(
                ExecutionFinding(
                    code="missing_owner",
                    step_id=step.step_id,
                    severity="blocker",
                    message="Execution step has no accountable owner.",
                )
            )
        if expired and step.status != "completed":
            findings.append(
                ExecutionFinding(
                    code="expired_open_step",
                    step_id=step.step_id,
                    severity="blocker",
                    message=f"Open step expired at {step.expires_at}.",
                )
            )
        if step.status == "completed" and not step.evidence:
            findings.append(
                ExecutionFinding(
                    code="missing_completion_evidence",
                    step_id=step.step_id,
                    severity="blocker",
                    message="Completed step has no command, dashboard, ticket, or log evidence.",
                )
            )
        if step.status == "skipped" and not step.evidence:
            findings.append(
                ExecutionFinding(
                    code="undocumented_skip",
                    step_id=step.step_id,
                    severity="warn",
                    message="Skipped step has no recorded rationale.",
                )
            )

    completed_steps = sum(step.status == "completed" for step in manifest.steps)
    open_steps = sum(step.status != "completed" for step in manifest.steps)
    status = "blocked" if findings else "verified"
    return ExecutionReview(
        incident_id=manifest.incident_id,
        service=manifest.service,
        runbook_id=manifest.runbook_id,
        status=status,
        reviewed_steps=len(manifest.steps),
        completed_steps=completed_steps,
        open_steps=open_steps,
        expired_steps=expired_steps,
        findings=findings,
        summary=(
            f"Runbook execution is {status}: {completed_steps}/{len(manifest.steps)} steps "
            f"completed with {len(findings)} governance finding(s)."
        ),
    )


def _timestamp(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))

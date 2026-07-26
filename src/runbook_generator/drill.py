from __future__ import annotations

import hashlib
import json
from datetime import datetime, timedelta

from runbook_generator.models import DrillFinding, DrillManifest, DrillReview


def review_drill(manifest: DrillManifest) -> DrillReview:
    reference_time = _timestamp(manifest.reference_time)
    freshness_cutoff = reference_time - timedelta(days=manifest.max_age_days)
    findings: list[DrillFinding] = []
    exercises_by_scenario = {exercise.scenario: exercise for exercise in manifest.exercises}

    for scenario in manifest.required_scenarios:
        exercise = exercises_by_scenario.get(scenario)
        if exercise is None:
            findings.append(
                DrillFinding(
                    code="missing_scenario",
                    scenario=scenario,
                    severity="blocker",
                    message="Required failure scenario has not been rehearsed.",
                )
            )
            continue
        if not exercise.owner.strip():
            findings.append(
                DrillFinding(
                    code="missing_owner",
                    scenario=scenario,
                    severity="blocker",
                    message="Drill exercise has no accountable owner.",
                )
            )
        if _timestamp(exercise.executed_at) < freshness_cutoff:
            findings.append(
                DrillFinding(
                    code="stale_exercise",
                    scenario=scenario,
                    severity="blocker",
                    message=(
                        f"Drill predates the {manifest.max_age_days}-day freshness window."
                    ),
                )
            )
        if exercise.outcome == "failed":
            findings.append(
                DrillFinding(
                    code="failed_exercise",
                    scenario=scenario,
                    severity="blocker",
                    message="Drill did not complete the expected recovery procedure.",
                )
            )
        if not exercise.evidence:
            findings.append(
                DrillFinding(
                    code="missing_evidence",
                    scenario=scenario,
                    severity="blocker",
                    message="Drill has no ticket, log, dashboard, or artifact evidence.",
                )
            )

    required_exercises = [
        exercises_by_scenario[scenario]
        for scenario in manifest.required_scenarios
        if scenario in exercises_by_scenario
    ]
    fresh_exercises = sum(
        _timestamp(exercise.executed_at) >= freshness_cutoff for exercise in required_exercises
    )
    passed_exercises = sum(exercise.outcome == "passed" for exercise in required_exercises)
    status = "blocked" if findings else "ready"
    fingerprint = hashlib.sha256(
        json.dumps(manifest.model_dump(), sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()
    return DrillReview(
        service=manifest.service,
        runbook_id=manifest.runbook_id,
        status=status,
        required_scenarios=len(manifest.required_scenarios),
        exercised_scenarios=len(required_exercises),
        fresh_exercises=fresh_exercises,
        passed_exercises=passed_exercises,
        findings=findings,
        evidence_fingerprint=fingerprint,
        summary=(
            f"Runbook drill readiness is {status}: {len(required_exercises)}/"
            f"{len(manifest.required_scenarios)} required scenarios exercised with "
            f"{len(findings)} finding(s)."
        ),
    )


def _timestamp(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))

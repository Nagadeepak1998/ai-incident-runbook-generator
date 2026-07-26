import json
from pathlib import Path

from fastapi.testclient import TestClient

from app.main import app
from runbook_generator.drill import review_drill
from runbook_generator.io import load_drill_manifest, render_drill_markdown
from runbook_generator.models import DrillManifest


def test_drill_review_accepts_fresh_passing_scenarios() -> None:
    report = review_drill(load_drill_manifest(Path("samples/payment_drill_manifest.json")))

    assert report.status == "ready"
    assert report.exercised_scenarios == 2
    assert report.fresh_exercises == 2
    assert report.passed_exercises == 2
    assert len(report.evidence_fingerprint) == 64
    assert report.findings == []


def test_drill_review_blocks_stale_and_missing_scenarios() -> None:
    report = review_drill(load_drill_manifest(Path("samples/stale_drill_manifest.json")))

    assert report.status == "blocked"
    assert [finding.code for finding in report.findings] == [
        "stale_exercise",
        "missing_scenario",
    ]


def test_drill_review_blocks_failed_unowned_exercise_without_evidence() -> None:
    payload = json.loads(Path("samples/payment_drill_manifest.json").read_text())
    payload["exercises"][0].update(
        {"owner": "", "outcome": "failed", "evidence": []}
    )

    report = review_drill(DrillManifest.model_validate(payload))

    assert report.status == "blocked"
    assert [finding.code for finding in report.findings] == [
        "missing_owner",
        "failed_exercise",
        "missing_evidence",
    ]


def test_drill_markdown_is_recruiter_readable() -> None:
    report = review_drill(load_drill_manifest(Path("samples/payment_drill_manifest.json")))

    markdown = render_drill_markdown(report)

    assert "# Runbook Drill Readiness Review" in markdown
    assert "Evidence fingerprint" in markdown
    assert "2/2" in markdown


def test_api_reviews_drill_and_records_metric() -> None:
    client = TestClient(app)
    payload = json.loads(Path("samples/payment_drill_manifest.json").read_text())

    response = client.post("/drills/review", json=payload)

    assert response.status_code == 200
    assert response.json()["status"] == "ready"
    assert "runbook_drill_reviews_total" in client.get("/metrics").text

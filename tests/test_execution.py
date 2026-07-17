import json
from pathlib import Path

from runbook_generator.execution import review_execution
from runbook_generator.io import load_execution_manifest, render_execution_markdown
from runbook_generator.models import ExecutionManifest


def test_execution_review_blocks_governance_gaps() -> None:
    report = review_execution(
        load_execution_manifest(Path("samples/payment_execution_manifest.json"))
    )

    assert report.status == "blocked"
    assert report.reviewed_steps == 3
    assert report.completed_steps == 2
    assert report.expired_steps == 2
    assert [finding.code for finding in report.findings] == [
        "missing_owner",
        "expired_open_step",
        "missing_completion_evidence",
    ]


def test_execution_review_verifies_owned_evidenced_steps() -> None:
    payload = json.loads(Path("samples/payment_execution_manifest.json").read_text())
    payload["steps"] = [payload["steps"][0]]

    report = review_execution(ExecutionManifest.model_validate(payload))

    assert report.status == "verified"
    assert report.findings == []


def test_execution_markdown_is_recruiter_readable() -> None:
    report = review_execution(
        load_execution_manifest(Path("samples/payment_execution_manifest.json"))
    )

    markdown = render_execution_markdown(report)

    assert "# Runbook Execution Review: INC-2026-0717-042" in markdown
    assert "`expired_open_step`" in markdown
    assert "`2/3`" in markdown

from pathlib import Path

from runbook_generator.generator import generate_runbook
from runbook_generator.io import load_incident, load_runbooks, render_review_markdown
from runbook_generator.review import review_runbook


def test_review_runbook_requires_human_approval_for_sev2() -> None:
    incident = load_incident(Path("samples/payment_latency_incident.json"))
    runbooks = load_runbooks(Path("samples/runbook_corpus.json"))
    draft = generate_runbook(incident, runbooks)

    report = review_runbook(draft)

    assert report.decision == "review"
    assert report.readiness_score == 88
    assert report.required_human_approval is True
    assert [finding.code for finding in report.findings] == [
        "approval_required",
        "redactions_applied",
    ]


def test_review_blocks_low_confidence_draft() -> None:
    incident = load_incident(Path("samples/payment_latency_incident.json"))
    runbooks = load_runbooks(Path("samples/runbook_corpus.json"))
    draft = generate_runbook(incident, runbooks, min_confidence=0.99)

    report = review_runbook(draft)

    assert report.decision == "block"
    assert any(finding.code == "low_confidence" for finding in report.findings)


def test_review_markdown_contains_findings() -> None:
    incident = load_incident(Path("samples/payment_latency_incident.json"))
    runbooks = load_runbooks(Path("samples/runbook_corpus.json"))
    draft = generate_runbook(incident, runbooks)
    report = review_runbook(draft)

    markdown = render_review_markdown(report)

    assert "# Runbook Readiness Review: payments-api" in markdown
    assert "`review`" in markdown
    assert "`approval_required`" in markdown

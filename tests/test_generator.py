from pathlib import Path

from runbook_generator.generator import generate_runbook
from runbook_generator.io import load_incident, load_runbooks


def test_generate_runbook_matches_payment_section() -> None:
    incident = load_incident(Path("samples/payment_latency_incident.json"))
    runbooks = load_runbooks(Path("samples/runbook_corpus.json"))

    draft = generate_runbook(incident, runbooks)

    assert draft.status == "ready"
    assert draft.service == "payments-api"
    assert draft.matched_sections[0].id == "payments-latency-sev2"
    assert draft.redaction_count == 2
    assert "high_severity_requires_human_approval" in draft.risk_flags
    assert all("prod_live" not in item for item in draft.evidence)


def test_low_confidence_requires_review() -> None:
    incident = load_incident(Path("samples/payment_latency_incident.json"))
    runbooks = load_runbooks(Path("samples/runbook_corpus.json"))

    draft = generate_runbook(incident, runbooks, min_confidence=0.99)

    assert draft.status == "needs_human_review"

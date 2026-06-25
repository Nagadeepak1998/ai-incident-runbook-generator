from pathlib import Path

from runbook_generator.generator import generate_runbook
from runbook_generator.io import load_incident, load_runbooks, render_markdown


def test_markdown_contains_operator_sections() -> None:
    incident = load_incident(Path("samples/payment_latency_incident.json"))
    runbooks = load_runbooks(Path("samples/runbook_corpus.json"))
    draft = generate_runbook(incident, runbooks)

    markdown = render_markdown(draft)

    assert "# Incident Runbook: payments-api" in markdown
    assert "## Immediate Checks" in markdown
    assert "## Escalation" in markdown
    assert "prod_live" not in markdown

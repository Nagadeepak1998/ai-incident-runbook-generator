# Case Study: AI Incident Runbook Generator

## Situation

Incident responders often lose time gathering context, finding the right runbook, and
sanitizing sensitive evidence before asking an AI assistant for help. The risky version of
this workflow sends raw logs into an LLM and returns generic advice with no source grounding.

## Approach

This project implements the safer platform pattern first:

- sanitize incident evidence before ranking or returning it
- retrieve from approved runbook sections
- show matched evidence and confidence
- make the same engine available through CLI and API
- expose metrics so platform teams can track quality and usage

## Production Shape

- `runbook_generator.redaction` removes common secrets from alert and log text
- `runbook_generator.retriever` ranks known runbook sections with explainable terms
- `runbook_generator.generator` creates a deterministic runbook draft
- `app.main` exposes `/health`, `/generate`, and `/metrics`
- tests cover redaction, retrieval, CLI output, and API behavior
- Docker, Kubernetes, Terraform, and CI templates are included for deployment review

## Operational Value

The service gives responders a useful first draft while keeping the decision boundary clear:
it suggests actions based on approved procedures, but humans still own incident changes,
rollbacks, customer communication, and escalation decisions.

## Evidence To Show Recruiters

- CLI and API parity for the same incident workflow
- safety controls around prompt inputs and log evidence
- deployment manifests with health checks, metrics, and container hardening
- tests that prove secrets are redacted and the highest-signal runbook wins


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
- review generated drafts for handoff readiness before an engineer acts on them
- replay dated incident windows to catch runbook quality drift and redaction trends
- verify step ownership, expiry, and completion evidence after responders start execution
- make the same engine available through CLI and API
- expose metrics so platform teams can track quality and usage

## Production Shape

- `runbook_generator.redaction` removes common secrets from alert and log text
- `runbook_generator.retriever` ranks known runbook sections with explainable terms
- `runbook_generator.generator` creates a deterministic runbook draft
- `runbook_generator.review` applies readiness checks for evidence, escalation, approval,
  and confidence
- `runbook_generator.history` reviews multi-window readiness and redaction quality
- `runbook_generator.execution` audits runbook step accountability with a reproducible clock
- `app.main` exposes `/health`, `/generate`, `/review`, `/history`, `/execution/review`, and
  `/metrics`
- tests cover redaction, retrieval, CLI output, and API behavior
- Docker, Kubernetes, Terraform, and CI templates are included for deployment review

## Operational Value

The service gives responders a useful first draft while keeping the decision boundary clear:
it suggests actions based on approved procedures, but humans still own incident changes,
rollbacks, customer communication, and escalation decisions.

The readiness review turns that boundary into a concrete gate. A draft can be approved,
sent for manual review, or blocked based on deterministic findings. The sample payment
incident returns `review` because a SEV2 incident still requires incident-commander
approval even when the generated runbook is grounded and redacted.

The history review turns one-off quality checks into a release-readiness signal. The
tracked sample report reviews three dated incident windows and blocks handoff because the
latest billing incident does not have enough approved runbook confidence.

The execution review prevents a well-written draft from being mistaken for completed work.
The tracked payment example blocks handoff because one expired step has no owner and another
step is marked complete without supporting command, dashboard, ticket, or log evidence.

## Evidence To Show Recruiters

- CLI and API parity for the same incident workflow
- CLI and API parity for readiness review through `runbook-generator review` and `/review`
- CLI and API parity for quality history through `runbook-generator history` and `/history`
- CLI and API parity for execution governance through `runbook-generator execution` and
  `/execution/review`
- safety controls around prompt inputs and log evidence
- deterministic Markdown artifacts in `reports/`
- deployment manifests with health checks, metrics, and container hardening
- tests that prove secrets are redacted and the highest-signal runbook wins

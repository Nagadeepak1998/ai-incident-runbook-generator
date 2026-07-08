# Incident Runbook: payments-api

- Title: Checkout payment authorization latency is above SLO
- Severity: `sev2`
- Confidence: `0.98`
- Status: `ready`
- Redactions: `2`

## Summary

SEV2 incident for payments-api: Checkout payment authorization latency is above SLO. Runbook status is ready based on sanitized alerts and matched procedures.

## Likely Cause

Likely aligned with runbook 'Payment authorization latency or timeout spike'.

## Immediate Checks

1. Confirm p95 latency, error rate, and retry budget from the last 15 minutes.
1. Compare processor timeout and retry settings against the previous release.
1. Check downstream processor status page and integration error codes.
1. Verify whether checkout traffic shifted by region or payment method.
1. Review recent deploy notes for payment gateway or timeout changes.

## Recommended Actions

1. Page payments on-call and assign one incident commander.
1. Freeze additional payments-api deploys until the incident is stable.
1. If processor timeout changed in the latest release, prepare rollback for human approval.
1. Route customer support updates through the incident commander.
1. Capture sanitized evidence and timeline before closing the incident.

## Evidence

- p95 latency for payments-api is 1850ms for 12 minutes
- checkout authorization errors increased to 7.2 percent
- Bearer [REDACTED] was seen in one debug line
- gateway timeout while calling payment processor from payments-api
- retry budget exhausted for processor-authorize after deploy pay-2026.06.25
- api_key=[REDACTED]
- deployed pay-2026.06.25 with new processor timeout
- rollback not yet attempted

## Matched Runbooks

- `payments-latency-sev2`: Payment authorization latency or timeout spike (score=52.5)
- `search-error-sev3`: Search API elevated 5xx errors (score=10.5)
- `auth-login-sev2`: Authentication login failures (score=6.0)

## Escalation

Escalate to payments platform owner and vendor integration contact if error rate stays above 5 percent for 15 minutes.


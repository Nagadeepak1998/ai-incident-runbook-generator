# Runbook Quality History Review

- Status: `block`
- Reviewed windows: `3`
- Blocked windows: `1`
- Review windows: `1`
- Approval required windows: `2`
- Total redactions: `2`
- Latest decision: `block`

## Summary

Runbook quality history is block: 3 window(s), 1 blocked, 1 needing review, 2 redaction(s).

## Windows

- `2026-07-01-payment-latency` `review` payments-api sev2 score=88/100 redactions=2 findings=approval_required, redactions_applied
- `2026-07-02-search-errors` `approve` search-api sev3 score=100/100 redactions=0 findings=none
- `2026-07-03-billing-unknown` `block` billing-worker sev2 score=60/100 redactions=0 findings=low_confidence, approval_required

## Recommendations

- Route blocked drafts to an incident commander before handoff.
- Keep human approval explicit for SEV1 and SEV2 drafts.
- Attach sanitized artifacts instead of raw alert or log evidence.

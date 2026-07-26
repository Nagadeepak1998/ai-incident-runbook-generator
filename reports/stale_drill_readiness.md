# Runbook Drill Readiness Review: payments-latency-sev2

- Service: `payments-api`
- Status: `blocked`
- Exercised scenarios: `1/2`
- Fresh exercises: `0`
- Passed exercises: `1`
- Evidence fingerprint: `1fae334e3e461b4f91367208d29de763e973078467ea58053ade8defc323ff64`

## Summary

Runbook drill readiness is blocked: 1/2 required scenarios exercised with 2 finding(s).

## Findings

- `blocker` `stale_exercise` `database-connection-saturation`: Drill predates the 90-day freshness window.
- `blocker` `missing_scenario` `upstream-timeout`: Required failure scenario has not been rehearsed.

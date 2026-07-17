from __future__ import annotations

from prometheus_client import Counter, Gauge, Histogram

GENERATIONS = Counter("runbook_generations_total", "Runbook generations", ["status"])
CONFIDENCE = Gauge("runbook_generation_confidence", "Latest runbook generation confidence")
LATENCY = Histogram("runbook_generation_seconds", "Runbook generation latency")
REVIEWS = Counter("runbook_reviews_total", "Runbook readiness reviews", ["decision"])
READINESS = Gauge("runbook_readiness_score", "Latest runbook readiness score")
HISTORY_REVIEWS = Counter(
    "runbook_history_reviews_total", "Runbook quality history reviews", ["status"]
)
EXECUTION_REVIEWS = Counter(
    "runbook_execution_reviews_total", "Runbook execution verification reviews", ["status"]
)

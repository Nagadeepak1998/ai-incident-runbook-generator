from __future__ import annotations

from prometheus_client import Counter, Gauge, Histogram

GENERATIONS = Counter("runbook_generations_total", "Runbook generations", ["status"])
CONFIDENCE = Gauge("runbook_generation_confidence", "Latest runbook generation confidence")
LATENCY = Histogram("runbook_generation_seconds", "Runbook generation latency")


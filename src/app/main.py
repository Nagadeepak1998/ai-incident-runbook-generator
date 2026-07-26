from __future__ import annotations

from fastapi import FastAPI, Response
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest

from app.metrics import (
    CONFIDENCE,
    DRILL_REVIEWS,
    EXECUTION_REVIEWS,
    GENERATIONS,
    HISTORY_REVIEWS,
    LATENCY,
    READINESS,
    REVIEWS,
)
from runbook_generator.drill import review_drill
from runbook_generator.execution import review_execution
from runbook_generator.generator import generate_runbook
from runbook_generator.history import review_history
from runbook_generator.models import (
    GeneratedRunbook,
    DrillManifest,
    DrillReview,
    ExecutionManifest,
    ExecutionReview,
    Incident,
    RunbookHistoryReview,
    RunbookHistoryWindow,
    RunbookReview,
    RunbookSection,
)
from runbook_generator.review import review_runbook

app = FastAPI(
    title="AI Incident Runbook Generator",
    version="0.3.0",
    description="Sanitized retrieval-backed runbook drafts for incident response.",
)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/generate", response_model=GeneratedRunbook)
def generate(payload: dict) -> GeneratedRunbook:
    incident = Incident.model_validate(payload["incident"])
    sections = [RunbookSection.model_validate(item) for item in payload["sections"]]
    min_confidence = float(payload.get("min_confidence", 0.2))

    with LATENCY.time():
        draft = generate_runbook(incident, sections, min_confidence=min_confidence)

    GENERATIONS.labels(status=draft.status).inc()
    CONFIDENCE.set(draft.confidence)
    return draft


@app.post("/review", response_model=RunbookReview)
def review(payload: dict) -> RunbookReview:
    draft = GeneratedRunbook.model_validate(payload["runbook"])
    min_confidence = float(payload.get("min_confidence", 0.35))
    report = review_runbook(draft, min_confidence=min_confidence)
    REVIEWS.labels(decision=report.decision).inc()
    READINESS.set(report.readiness_score)
    return report


@app.post("/history", response_model=RunbookHistoryReview)
def history(payload: dict) -> RunbookHistoryReview:
    windows = [RunbookHistoryWindow.model_validate(item) for item in payload["windows"]]
    min_confidence = float(payload.get("min_confidence", 0.35))
    report = review_history(windows, min_confidence=min_confidence)
    HISTORY_REVIEWS.labels(status=report.status).inc()
    return report


@app.post("/execution/review", response_model=ExecutionReview)
def execution_review(payload: ExecutionManifest) -> ExecutionReview:
    report = review_execution(payload)
    EXECUTION_REVIEWS.labels(status=report.status).inc()
    return report


@app.post("/drills/review", response_model=DrillReview)
def drill_review(payload: DrillManifest) -> DrillReview:
    report = review_drill(payload)
    DRILL_REVIEWS.labels(status=report.status).inc()
    return report


@app.get("/metrics")
def metrics() -> Response:
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)

from __future__ import annotations

from fastapi import FastAPI, Response
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest

from app.metrics import CONFIDENCE, GENERATIONS, LATENCY, READINESS, REVIEWS
from runbook_generator.generator import generate_runbook
from runbook_generator.models import GeneratedRunbook, Incident, RunbookReview, RunbookSection
from runbook_generator.review import review_runbook

app = FastAPI(
    title="AI Incident Runbook Generator",
    version="0.1.0",
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


@app.get("/metrics")
def metrics() -> Response:
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)

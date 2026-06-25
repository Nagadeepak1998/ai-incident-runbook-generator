import json
from pathlib import Path

from fastapi.testclient import TestClient

from app.main import app


def test_api_generate_returns_runbook() -> None:
    client = TestClient(app)
    payload = json.loads(Path("samples/api_request.json").read_text())

    response = client.post("/generate", json=payload)

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ready"
    assert body["matched_sections"][0]["id"] == "payments-latency-sev2"


def test_metrics_endpoint() -> None:
    client = TestClient(app)

    response = client.get("/metrics")

    assert response.status_code == 200
    assert "runbook_generations_total" in response.text


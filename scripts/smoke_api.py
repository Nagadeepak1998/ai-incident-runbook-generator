from __future__ import annotations

import json
from pathlib import Path

from fastapi.testclient import TestClient

from app.main import app


def main() -> int:
    client = TestClient(app)
    payload = json.loads(Path("samples/api_request.json").read_text())
    health = client.get("/health")
    response = client.post("/generate", json=payload)
    review = client.post("/review", json={"runbook": response.json()})
    metrics = client.get("/metrics")
    if (
        health.status_code != 200
        or response.status_code != 200
        or review.status_code != 200
        or metrics.status_code != 200
    ):
        print("API smoke failed")
        return 1
    body = response.json()
    review_body = review.json()
    print(
        f"{body['status']}: confidence={body['confidence']} "
        f"matches={len(body['matched_sections'])} review={review_body['decision']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

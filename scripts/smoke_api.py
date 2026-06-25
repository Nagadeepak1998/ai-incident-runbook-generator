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
    metrics = client.get("/metrics")
    if health.status_code != 200 or response.status_code != 200 or metrics.status_code != 200:
        print("API smoke failed")
        return 1
    body = response.json()
    print(f"{body['status']}: confidence={body['confidence']} matches={len(body['matched_sections'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


import os
import subprocess
import sys
from pathlib import Path

from fastapi.testclient import TestClient

from app.main import app
from runbook_generator.history import load_history_manifest, review_history
from runbook_generator.io import render_history_markdown


def test_history_review_blocks_unknown_runbook_window() -> None:
    windows = load_history_manifest(Path("samples/history_manifest.json"))

    report = review_history(windows)

    assert report.status == "block"
    assert report.reviewed_windows == 3
    assert report.blocked_windows == 1
    assert report.review_windows == 1
    assert report.total_redactions == 2
    assert report.windows[-1].run_id == "2026-07-03-billing-unknown"
    assert "low_confidence" in report.windows[-1].finding_codes


def test_history_markdown_contains_window_summary() -> None:
    report = review_history(load_history_manifest(Path("samples/history_manifest.json")))

    markdown = render_history_markdown(report)

    assert "# Runbook Quality History Review" in markdown
    assert "`2026-07-02-search-errors` `approve` search-api" in markdown
    assert "Route blocked drafts to an incident commander" in markdown


def test_cli_history_writes_markdown_and_returns_two(tmp_path: Path) -> None:
    output = tmp_path / "history.md"

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "runbook_generator.cli",
            "history",
            "--manifest",
            "samples/history_manifest.json",
            "--format",
            "markdown",
            "--output",
            str(output),
        ],
        check=False,
        text=True,
        capture_output=True,
        env={**os.environ, "PYTHONPATH": "src:."},
    )

    assert result.returncode == 2
    assert "block: windows=3 blocked=1 review=1 redactions=2" in result.stdout
    assert "`2026-07-03-billing-unknown` `block`" in output.read_text()


def test_api_history_returns_review() -> None:
    client = TestClient(app)
    windows = [window.model_dump() for window in load_history_manifest(Path("samples/history_manifest.json"))]

    response = client.post("/history", json={"windows": windows})

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "block"
    assert body["blocked_windows"] == 1
    assert body["latest_service"] == "billing-worker"


def test_history_metrics_are_exposed() -> None:
    client = TestClient(app)
    windows = [window.model_dump() for window in load_history_manifest(Path("samples/history_manifest.json"))]

    client.post("/history", json={"windows": windows})
    response = client.get("/metrics")

    assert response.status_code == 200
    assert "runbook_history_reviews_total" in response.text

import subprocess
import sys
import os
import json
from pathlib import Path


def test_cli_writes_report(tmp_path: Path) -> None:
    output = tmp_path / "report.json"

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "runbook_generator.cli",
            "generate",
            "--incident",
            "samples/payment_latency_incident.json",
            "--runbooks",
            "samples/runbook_corpus.json",
            "--output",
            str(output),
        ],
        check=False,
        text=True,
        capture_output=True,
        env={**os.environ, "PYTHONPATH": "src:."},
    )

    assert result.returncode == 0
    assert "ready: payments-api sev2" in result.stdout
    assert output.exists()


def test_cli_writes_readiness_review(tmp_path: Path) -> None:
    runbook = tmp_path / "runbook.json"
    output = tmp_path / "review.md"
    runbook.write_text(Path("reports/payment_latency_runbook.json").read_text())

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "runbook_generator.cli",
            "review",
            "--runbook",
            str(runbook),
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

    assert result.returncode == 0
    assert "review: payments-api sev2" in result.stdout
    assert "`approval_required`" in output.read_text()


def test_cli_review_fail_on_review_returns_one(tmp_path: Path) -> None:
    runbook = tmp_path / "runbook.json"
    output = tmp_path / "review.json"
    runbook.write_text(Path("reports/payment_latency_runbook.json").read_text())

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "runbook_generator.cli",
            "review",
            "--runbook",
            str(runbook),
            "--output",
            str(output),
            "--fail-on-review",
        ],
        check=False,
        text=True,
        capture_output=True,
        env={**os.environ, "PYTHONPATH": "src:."},
    )

    assert result.returncode == 1
    assert json.loads(output.read_text())["decision"] == "review"


def test_cli_execution_returns_blocking_gate_code(tmp_path: Path) -> None:
    output = tmp_path / "execution.md"

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "runbook_generator.cli",
            "execution",
            "--manifest",
            "samples/payment_execution_manifest.json",
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
    assert "blocked: steps=3 completed=2 open=1 expired=2 findings=3" in result.stdout
    assert "`missing_owner`" in output.read_text()

import subprocess
import sys
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
    )

    assert result.returncode == 0
    assert "ready: payments-api sev2" in result.stdout
    assert output.exists()

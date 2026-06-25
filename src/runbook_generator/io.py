from __future__ import annotations

import json
from pathlib import Path

from runbook_generator.models import Incident, RunbookSection


def load_incident(path: Path) -> Incident:
    return Incident.model_validate_json(path.read_text())


def load_runbooks(path: Path) -> list[RunbookSection]:
    raw = json.loads(path.read_text())
    return [RunbookSection.model_validate(item) for item in raw["sections"]]


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")


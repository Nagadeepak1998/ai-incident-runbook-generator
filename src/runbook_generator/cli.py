from __future__ import annotations

import argparse
from pathlib import Path

from runbook_generator.generator import generate_runbook
from runbook_generator.io import load_incident, load_runbooks, write_json


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate a sanitized incident runbook draft.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    generate = subparsers.add_parser("generate")
    generate.add_argument("--incident", required=True, type=Path)
    generate.add_argument("--runbooks", required=True, type=Path)
    generate.add_argument("--output", required=True, type=Path)
    generate.add_argument("--min-confidence", type=float, default=0.2)

    args = parser.parse_args()
    if args.command == "generate":
        incident = load_incident(args.incident)
        runbooks = load_runbooks(args.runbooks)
        draft = generate_runbook(incident, runbooks, min_confidence=args.min_confidence)
        write_json(args.output, draft.model_dump())
        print(
            f"{draft.status}: {draft.service} {draft.severity} "
            f"confidence={draft.confidence:.3f} redactions={draft.redaction_count}"
        )
        return 0 if draft.status == "ready" else 2
    return 1


if __name__ == "__main__":
    raise SystemExit(main())


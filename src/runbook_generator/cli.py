from __future__ import annotations

import argparse
from pathlib import Path

from runbook_generator.drill import review_drill
from runbook_generator.execution import review_execution
from runbook_generator.generator import generate_runbook
from runbook_generator.history import load_history_manifest, review_history
from runbook_generator.io import (
    load_generated_runbook,
    load_drill_manifest,
    load_execution_manifest,
    load_incident,
    load_runbooks,
    render_history_markdown,
    render_drill_markdown,
    render_execution_markdown,
    render_markdown,
    render_review_markdown,
    write_json,
    write_text,
)
from runbook_generator.review import review_runbook


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate a sanitized incident runbook draft.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    generate = subparsers.add_parser("generate")
    generate.add_argument("--incident", required=True, type=Path)
    generate.add_argument("--runbooks", required=True, type=Path)
    generate.add_argument("--output", required=True, type=Path)
    generate.add_argument("--format", choices=["json", "markdown"], default="json")
    generate.add_argument("--min-confidence", type=float, default=0.2)

    review = subparsers.add_parser("review")
    review.add_argument("--runbook", required=True, type=Path)
    review.add_argument("--output", required=True, type=Path)
    review.add_argument("--format", choices=["json", "markdown"], default="json")
    review.add_argument("--min-confidence", type=float, default=0.35)
    review.add_argument("--fail-on-review", action="store_true")

    history = subparsers.add_parser("history")
    history.add_argument("--manifest", required=True, type=Path)
    history.add_argument("--output", required=True, type=Path)
    history.add_argument("--format", choices=["json", "markdown"], default="json")
    history.add_argument("--min-confidence", type=float, default=0.35)

    execution = subparsers.add_parser("execution")
    execution.add_argument("--manifest", required=True, type=Path)
    execution.add_argument("--output", required=True, type=Path)
    execution.add_argument("--format", choices=["json", "markdown"], default="json")

    drill = subparsers.add_parser("drill")
    drill.add_argument("--manifest", required=True, type=Path)
    drill.add_argument("--output", required=True, type=Path)
    drill.add_argument("--format", choices=["json", "markdown"], default="json")

    args = parser.parse_args()
    if args.command == "generate":
        incident = load_incident(args.incident)
        runbooks = load_runbooks(args.runbooks)
        draft = generate_runbook(incident, runbooks, min_confidence=args.min_confidence)
        if args.format == "markdown":
            write_text(args.output, render_markdown(draft))
        else:
            write_json(args.output, draft.model_dump())
        print(
            f"{draft.status}: {draft.service} {draft.severity} "
            f"confidence={draft.confidence:.3f} redactions={draft.redaction_count}"
        )
        return 0 if draft.status == "ready" else 2
    if args.command == "review":
        draft = load_generated_runbook(args.runbook)
        report = review_runbook(draft, min_confidence=args.min_confidence)
        if args.format == "markdown":
            write_text(args.output, render_review_markdown(report))
        else:
            write_json(args.output, report.model_dump())
        print(
            f"{report.decision}: {report.service} {report.severity} "
            f"score={report.readiness_score}/100 findings={len(report.findings)}"
        )
        if report.decision == "block":
            return 2
        if report.decision == "review" and args.fail_on_review:
            return 1
        return 0
    if args.command == "history":
        windows = load_history_manifest(args.manifest)
        report = review_history(windows, min_confidence=args.min_confidence)
        if args.format == "markdown":
            write_text(args.output, render_history_markdown(report))
        else:
            write_json(args.output, report.model_dump())
        print(
            f"{report.status}: windows={report.reviewed_windows} "
            f"blocked={report.blocked_windows} review={report.review_windows} "
            f"redactions={report.total_redactions}"
        )
        return 2 if report.status == "block" else 0
    if args.command == "execution":
        report = review_execution(load_execution_manifest(args.manifest))
        if args.format == "markdown":
            write_text(args.output, render_execution_markdown(report))
        else:
            write_json(args.output, report.model_dump())
        print(
            f"{report.status}: steps={report.reviewed_steps} completed={report.completed_steps} "
            f"open={report.open_steps} expired={report.expired_steps} "
            f"findings={len(report.findings)}"
        )
        return 2 if report.status == "blocked" else 0
    if args.command == "drill":
        report = review_drill(load_drill_manifest(args.manifest))
        if args.format == "markdown":
            write_text(args.output, render_drill_markdown(report))
        else:
            write_json(args.output, report.model_dump())
        print(
            f"{report.status}: scenarios={report.exercised_scenarios}/"
            f"{report.required_scenarios} fresh={report.fresh_exercises} "
            f"passed={report.passed_exercises} findings={len(report.findings)}"
        )
        return 2 if report.status == "blocked" else 0
    return 1


if __name__ == "__main__":
    raise SystemExit(main())

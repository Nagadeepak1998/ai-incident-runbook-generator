.PHONY: setup test lint sample sample-markdown sample-review history-report execution-report drill-report drill-blocked run smoke docker-build docker-run clean

setup:
	python3 -m venv .venv
	.venv/bin/python -m pip install --upgrade pip
	.venv/bin/pip install -e '.[dev]'

test:
	.venv/bin/pytest

lint:
	.venv/bin/ruff check src tests

sample:
	PYTHONPATH=src:. .venv/bin/python -m runbook_generator.cli generate \
		--incident samples/payment_latency_incident.json \
		--runbooks samples/runbook_corpus.json \
		--output reports/payment_latency_runbook.json

sample-markdown:
	PYTHONPATH=src:. .venv/bin/python -m runbook_generator.cli generate \
		--incident samples/payment_latency_incident.json \
		--runbooks samples/runbook_corpus.json \
		--format markdown \
		--output reports/payment_latency_runbook.md

sample-review: sample
	PYTHONPATH=src:. .venv/bin/python -m runbook_generator.cli review \
		--runbook reports/payment_latency_runbook.json \
		--format markdown \
		--output reports/payment_latency_readiness_review.md

history-report:
	PYTHONPATH=src:. .venv/bin/python -m runbook_generator.cli history \
		--manifest samples/history_manifest.json \
		--format markdown \
		--output reports/runbook_quality_history.md || test $$? -eq 2

execution-report:
	PYTHONPATH=src:. .venv/bin/python -m runbook_generator.cli execution \
		--manifest samples/payment_execution_manifest.json \
		--format markdown \
		--output reports/payment_execution_review.md || test $$? -eq 2

drill-report:
	PYTHONPATH=src:. .venv/bin/python -m runbook_generator.cli drill \
		--manifest samples/payment_drill_manifest.json \
		--format markdown \
		--output reports/payment_drill_readiness.md

drill-blocked:
	PYTHONPATH=src:. .venv/bin/python -m runbook_generator.cli drill \
		--manifest samples/stale_drill_manifest.json \
		--format markdown \
		--output reports/stale_drill_readiness.md || test $$? -eq 2

run:
	.venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8080

smoke:
	PYTHONPATH=src:. .venv/bin/python scripts/smoke_api.py

docker-build:
	docker build -f infra/docker/Dockerfile -t ai-incident-runbook-generator:local .

docker-run:
	docker run --rm -p 8080:8080 ai-incident-runbook-generator:local

clean:
	rm -rf .venv .pytest_cache .ruff_cache *.egg-info src/*.egg-info

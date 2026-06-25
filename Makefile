.PHONY: setup test lint sample run smoke docker-build docker-run clean

setup:
	python3 -m venv .venv
	.venv/bin/python -m pip install --upgrade pip
	.venv/bin/pip install -e '.[dev]'

test:
	.venv/bin/pytest

lint:
	.venv/bin/ruff check app src tests

sample:
	.venv/bin/runbook-generator generate \
		--incident samples/payment_latency_incident.json \
		--runbooks samples/runbook_corpus.json \
		--output reports/payment_latency_runbook.json

run:
	.venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8080

smoke:
	.venv/bin/python scripts/smoke_api.py

docker-build:
	docker build -f infra/docker/Dockerfile -t ai-incident-runbook-generator:local .

docker-run:
	docker run --rm -p 8080:8080 ai-incident-runbook-generator:local

clean:
	rm -rf .venv .pytest_cache .ruff_cache *.egg-info src/*.egg-info

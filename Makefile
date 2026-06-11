.PHONY: install dev test lint format clean build run api worker docker-build docker-up docker-down docker-logs

PYTHON ?= python
PIP ?= pip
PYTEST ?= python -m pytest

install:
	$(PIP) install -e ".[dev]"

dev: install
	$(PIP) install -e ".[all]"

test:
	$(PYTEST) tests/ -v --tb=short -m "not slow"

test-all:
	$(PYTEST) tests/ -v --tb=short

test-cov:
	$(PYTEST) tests/ -v --cov=ai_multicolony --cov-report=term-missing --cov-report=html

lint:
	ruff check ai_multicolony/ tests/
	mypy ai_multicolony/ --ignore-missing-imports

format:
	ruff format ai_multicolony/ tests/
	ruff check --fix ai_multicolony/ tests/

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	rm -rf .pytest_cache .mypy_cache .ruff_cache htmlcov .coverage
	rm -rf data/chroma

build:
	$(PYTHON) -m build

run:
	$(PYTHON) -m ai_multicolony.cli run

api:
	uvicorn ai_multicolony.api.app:create_app --factory --host 0.0.0.0 --port 8000 --reload

worker:
	celery -A ai_multicolony.worker worker --loglevel=info

mcp:
	uvicorn ai_multicolony.mcp.server:MCPServer --factory --host 0.0.0.0 --port 5000

docker-build:
	docker compose build

docker-up:
	docker compose up -d

docker-down:
	docker compose down

docker-logs:
	docker compose logs -f

docker-restart:
	docker compose down && docker compose up -d

setup:
	bash scripts/setup_dev.sh

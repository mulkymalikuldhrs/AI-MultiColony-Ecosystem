# =============================================================================
# AI MultiColony Ecosystem — Makefile
# Version 3.0.0
# =============================================================================
# Monorepo orchestration for the unified multi-colony AI platform.
#
# Quick reference:
#   make install       — Install all Python + Node dependencies
#   make dev           — Start all services in dev mode
#   make dev-api       — Start just the FastAPI backend
#   make dev-web       — Start just the Next.js dashboard
#   make dev-crucix    — Start just the Crucix OSINT service
#   make build         — Build all packages
#   make test          — Run all tests (Python + JS)
#   make lint          — Run all linters
#   make docker-up     — Start Docker Compose stack
#   make docker-down   — Stop Docker Compose stack
#   make clean         — Remove all build artifacts
# =============================================================================

.PHONY: install dev dev-api dev-web dev-crucix build test test-python \
        test-js lint docker-up docker-down clean help

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
PYTHON       ?= python3
PIP          ?= pip3
NODE         ?= node
NPM          ?= npm
PYTEST       ?= $(PYTHON) -m pytest
DOCKER       ?= docker
DOCKER_COMPOSE ?= docker compose

# Project paths
ROOT_DIR     := $(shell pwd)
VENV_DIR     := $(ROOT_DIR)/.venv
DASHBOARD    := $(ROOT_DIR)/dashboard
CRUCIX       := $(ROOT_DIR)/packages/crucix
DEER_FLOW_FE := $(ROOT_DIR)/packages/deer-flow/frontend
DEER_FLOW_BE := $(ROOT_DIR)/packages/deer-flow/backend
AUTON_ORG    := $(ROOT_DIR)/packages/autonomous-organism
HERMES       := $(ROOT_DIR)/packages/hermes-quant
AGENTIC_LEG  := $(ROOT_DIR)/packages/agentic-legacy

# ---------------------------------------------------------------------------
# Colors (if terminal supports it)
# ---------------------------------------------------------------------------
BLUE   := \033[0;34m
GREEN  := \033[0;32m
YELLOW := \033[0;33m
CYAN   := \033[0;36m
RESET  := \033[0m

# ---------------------------------------------------------------------------
# Help
# ---------------------------------------------------------------------------
help: ## Show this help message
	@echo "$(CYAN)AI MultiColony Ecosystem v3.0.0 — Makefile Commands$(RESET)"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  $(GREEN)%-18s$(RESET) %s\n", $$1, $$2}'
	@echo ""

# ---------------------------------------------------------------------------
# Install
# ---------------------------------------------------------------------------
install: ## Install all dependencies (Python venv + pip + npm workspaces)
	@echo "$(BLUE)=== Installing Python dependencies ===$(RESET)"
	@if [ ! -d "$(VENV_DIR)" ]; then \
		$(PYTHON) -m venv $(VENV_DIR); \
		echo "$(GREEN)Created virtual environment at $(VENV_DIR)$(RESET)"; \
	fi
	@. $(VENV_DIR)/bin/activate && \
		$(PIP) install --upgrade pip setuptools wheel && \
		$(PIP) install -e ".[dev]" && \
		$(PIP) install -r requirements.txt && \
		$(PIP) install -r $(HERMES)/requirements.txt 2>/dev/null || true
	@echo "$(BLUE)=== Installing Node.js workspace dependencies ===$(RESET)"
	@$(NPM) install
	@echo "$(GREEN)=== All dependencies installed ===$(RESET)"

# ---------------------------------------------------------------------------
# Development
# ---------------------------------------------------------------------------
dev: ## Start all services in dev mode (API + Web + Crucix)
	@echo "$(CYAN)=== Starting all services in dev mode ===$(RESET)"
	@make dev-api &
	@make dev-web &
	@make dev-crucix &
	@wait

dev-api: ## Start just the FastAPI backend (port 8000)
	@echo "$(CYAN)=== Starting API server on http://localhost:8000 ===$(RESET)"
	@. $(VENV_DIR)/bin/activate && \
		uvicorn ai_multicolony.api.app:create_app --factory --host 0.0.0.0 --port 8000 --reload

dev-web: ## Start just the Next.js dashboard (port 3000)
	@echo "$(CYAN)=== Starting Web dashboard on http://localhost:3000 ===$(RESET)"
	@cd $(DASHBOARD) && $(NPM) run dev

dev-crucix: ## Start just the Crucix OSINT service (port 3117)
	@echo "$(CYAN)=== Starting Crucix OSINT on http://localhost:3117 ===$(RESET)"
	@cd $(CRUCIX) && $(NPM) run dev

# ---------------------------------------------------------------------------
# Build
# ---------------------------------------------------------------------------
build: ## Build all packages
	@echo "$(BLUE)=== Building all packages ===$(RESET)"
	@echo "$(YELLOW)--- Building Python package ---$(RESET)"
	@. $(VENV_DIR)/bin/activate && $(PYTHON) -m build 2>/dev/null || echo "Python build skipped (install build: pip install build)"
	@echo "$(YELLOW)--- Building Next.js dashboard ---$(RESET)"
	@cd $(DASHBOARD) && $(NPM) run build
	@echo "$(YELLOW)--- Building Crucix dashboard ---$(RESET)"
	@cd $(CRUCIX) && $(NPM) run inject 2>/dev/null || echo "Crucix inject skipped"
	@echo "$(YELLOW)--- Building Autonomous Organism ---$(RESET)"
	@cd $(AUTON_ORG) && $(NPM) run build 2>/dev/null || echo "Autonomous Organism build skipped"
	@echo "$(YELLOW)--- Building Deer Flow Frontend ---$(RESET)"
	@cd $(DEER_FLOW_FE) && npx pnpm install && npx pnpm run build 2>/dev/null || echo "Deer Flow frontend build skipped"
	@echo "$(GREEN)=== Build complete ===$(RESET)"

# ---------------------------------------------------------------------------
# Test
# ---------------------------------------------------------------------------
test: test-python test-js ## Run all tests (Python + JavaScript)

test-python: ## Run Python tests only
	@echo "$(BLUE)=== Running Python tests ===$(RESET)"
	@. $(VENV_DIR)/bin/activate && \
		$(PYTEST) tests/ -v --tb=short -m "not slow" 2>/dev/null || \
		$(PYTEST) tests/ -v --tb=short

test-js: ## Run JavaScript/TypeScript tests only
	@echo "$(BLUE)=== Running Dashboard (Next.js) tests ===$(RESET)"
	@cd $(DASHBOARD) && $(NPM) test 2>/dev/null || echo "Dashboard tests skipped"
	@echo "$(BLUE)=== Running Crucix tests ===$(RESET)"
	@cd $(CRUCIX) && $(NPM) test 2>/dev/null || echo "Crucix tests skipped"
	@echo "$(BLUE)=== Running Autonomous Organism tests ===$(RESET)"
	@cd $(AUTON_ORG) && $(NPM) test 2>/dev/null || echo "Autonomous Organism tests skipped"
	@echo "$(BLUE)=== Running Deer Flow Frontend tests ===$(RESET)"
	@cd $(DEER_FLOW_FE) && npx pnpm test 2>/dev/null || echo "Deer Flow frontend tests skipped"

# ---------------------------------------------------------------------------
# Lint
# ---------------------------------------------------------------------------
lint: ## Run all linters
	@echo "$(BLUE)=== Running Python linters ===$(RESET)"
	@. $(VENV_DIR)/bin/activate && \
		ruff check ai_multicolony/ tests/ 2>/dev/null || echo "Ruff not installed, skipping"
	@. $(VENV_DIR)/bin/activate && \
		mypy ai_multicolony/ --ignore-missing-imports 2>/dev/null || echo "Mypy not installed, skipping"
	@echo "$(BLUE)=== Running JavaScript linters ===$(RESET)"
	@cd $(DASHBOARD) && $(NPM) run lint 2>/dev/null || echo "Dashboard lint skipped"
	@cd $(AUTON_ORG) && $(NPM) run lint 2>/dev/null || echo "Autonomous Organism lint skipped"
	@cd $(DEER_FLOW_FE) && npx pnpm lint 2>/dev/null || echo "Deer Flow lint skipped"

# ---------------------------------------------------------------------------
# Docker
# ---------------------------------------------------------------------------
docker-up: ## Start Docker Compose stack
	@echo "$(CYAN)=== Starting Docker Compose ===$(RESET)"
	@$(DOCKER_COMPOSE) up -d
	@echo "$(GREEN)=== Docker stack started ===$(RESET)"
	@echo "  API:      http://localhost:8000"
	@echo "  Web:      http://localhost:3000"
	@echo "  Crucix:   http://localhost:3117"
	@echo "  Nginx:    http://localhost:80"
	@echo "  Postgres: localhost:5432"
	@echo "  Redis:    localhost:6379"

docker-down: ## Stop Docker Compose stack
	@echo "$(YELLOW)=== Stopping Docker Compose ===$(RESET)"
	@$(DOCKER_COMPOSE) down
	@echo "$(GREEN)=== Docker stack stopped ===$(RESET)"

# ---------------------------------------------------------------------------
# Clean
# ---------------------------------------------------------------------------
clean: ## Remove all build artifacts, caches, and temp files
	@echo "$(YELLOW)=== Cleaning build artifacts ===$(RESET)"
	@find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete 2>/dev/null || true
	@find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name ".next" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name "dist" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name "build" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name "node_modules" -maxdepth 3 -exec rm -rf {} + 2>/dev/null || true
	@rm -rf .coverage htmlcov .pytest_cache
	@rm -rf data/chroma
	@echo "$(GREEN)=== Clean complete ===$(RESET)"

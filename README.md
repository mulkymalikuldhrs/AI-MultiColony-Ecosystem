<p align="center">
  <img width="100%" src="https://capsule-render.vercel.app/api?type=waving&color=0:0d1b2a,50:1b263b,100:415a77&height=220&section=header&text=AI%20MultiColony%20Ecosystem&fontSize=42&fontColor=e0e1dd&animation=fadeIn&fontAlignY=30&desc=Unified%20Multi-Colony%20AI%20Platform%20v3.0&descSize=16&descColor=778da9&descAlignY=50" />
</p>

<div align="center">

[![Version](https://img.shields.io/badge/Version-3.0.0-brightgreen?style=for-the-badge&logo=semanticrelease&logoColor=white)](https://github.com/mulkymalikuldhrs/AI-MultiColony-Ecosystem/releases)
[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Node.js](https://img.shields.io/badge/Node.js-22+-339933?style=for-the-badge&logo=node.js&logoColor=white)](https://nodejs.org/)
[![Next.js](https://img.shields.io/badge/Next.js-16-000000?style=for-the-badge&logo=next.js&logoColor=white)](https://nextjs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![MIT License](https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge&logo=opensourceinitiative&logoColor=white)](LICENSE)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?style=for-the-badge&logo=docker&logoColor=white)](https://www.docker.com/)

[![CI](https://img.shields.io/badge/CI-GitHub_Actions-2088FF?style=for-the-badge&logo=githubactions&logoColor=white)](https://github.com/mulkymalikuldhrs/AI-MultiColony-Ecosystem/actions)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-4169E1?style=for-the-badge&logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![Redis](https://img.shields.io/badge/Redis-7-DC382D?style=for-the-badge&logo=redis&logoColor=white)](https://redis.io/)
[![Express](https://img.shields.io/badge/Express-5-000000?style=for-the-badge&logo=express&logoColor=white)](https://expressjs.com/)
[![Supabase](https://img.shields.io/badge/Supabase-Ready-3ECF8E?style=for-the-badge&logo=supabase&logoColor=white)](https://supabase.com/)

</div>

---

## Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Integrated Packages](#integrated-packages)
- [Quickstart](#quickstart)
- [API Endpoints](#api-endpoints)
- [Environment Variables](#environment-variables)
- [Development](#development)
- [Docker Deployment](#docker-deployment)
- [Testing](#testing)
- [Contributing](#contributing)
- [License](#license)

---

## Overview

**AI MultiColony Ecosystem v3.0** is a unified monorepo that consolidates **5 independent AI platforms** into a single, cohesive multi-colony intelligence system. Each "colony" specializes in a different domain — OSINT intelligence, agent orchestration, autonomous organisms, quantitative trading, and legacy AI — and they all communicate through shared infrastructure (PostgreSQL, Redis, event bus).

### What's New in v3.0

| Feature | Description |
|---------|-------------|
| **Monorepo Unification** | 5 previously separate repos merged into one codebase with npm workspaces |
| **Unified Docker Compose** | Single `docker-compose.yml` orchestrates all 7 services |
| **Consolidated Environment** | One `.env` file replaces 5 separate configurations |
| **Shared Makefile** | `make dev`, `make test`, `make lint` work across all packages |
| **Central Dashboard** | Next.js 16 dashboard monitors all colonies |
| **PostgreSQL 16** | Production-grade database replaces SQLite for multi-service coordination |

---

## Architecture

```
                            ┌─────────────────────────────────┐
                            │         Nginx (port 80)         │
                            │      Reverse Proxy + TLS        │
                            └────────────┬────────────────────┘
                                         │
              ┌──────────────────────────┼──────────────────────────┐
              │                          │                          │
    ┌─────────▼──────────┐   ┌──────────▼──────────┐   ┌──────────▼──────────┐
    │  Web Dashboard     │   │    Crucix OSINT     │   │  Deer Flow Frontend │
    │  (Next.js 16)      │   │  (Express 5)        │   │  (Next.js 16)       │
    │  port 3000         │   │  port 3117          │   │                     │
    └─────────┬──────────┘   └──────────┬──────────┘   └──────────┬──────────┘
              │                         │                          │
              └─────────────────────────┼──────────────────────────┘
                                        │
                              ┌─────────▼─────────┐
                              │   FastAPI Gateway  │
                              │   (port 8000)      │
                              │                    │
                              │  ┌──────────────┐  │
                              │  │  Colony       │  │
                              │  │  Coordinator  │  │
                              │  └──────┬───────┘  │
                              │         │          │
                              │  ┌──────▼───────┐  │
                              │  │  Agent        │  │
                              │  │  Registry     │  │
                              │  └──────┬───────┘  │
                              │         │          │
                              │  ┌──────▼───────┐  │
                              │  │  LLM Gateway  │  │
                              │  │  (9 providers)│  │
                              │  └──────────────┘  │
                              └─────────┬──────────┘
                                        │
         ┌──────────────────────────────┼──────────────────────────────┐
         │                              │                              │
  ┌──────▼──────┐              ┌────────▼────────┐           ┌────────▼────────┐
  │ PostgreSQL  │              │     Redis 7     │           │  Hermes Quant   │
  │    16       │              │   Cache + Bus   │           │  Trading Bot    │
  │  port 5432  │              │   port 6379     │           │  (Python, no    │
  └─────────────┘              └─────────────────┘           │   HTTP port)    │
                                                             └─────────────────┘
         │                              │
  ┌──────▼──────┐              ┌────────▼────────┐
  │ Autonomous  │              │   Qdrant /      │
  │  Organism   │              │   ChromaDB      │
  │ (React 18 + │              │  Vector Store   │
  │  Supabase)  │              │                 │
  └─────────────┘              └─────────────────┘
```

### Communication Flow

```
User Request → Nginx → API Gateway → Colony Coordinator → Agent Registry
                                                    ↓
                                              Selected Agent
                                                    ↓
                                          LLM Gateway (failover)
                                                    ↓
                                          Tool Execution
                                                    ↓
                                    Memory Store (PostgreSQL + Redis + Vectors)
                                                    ↓
                                          Response → User
```

---

## Integrated Packages

### 📦 `packages/crucix/` — OSINT Intelligence Platform

| Detail | Value |
|--------|-------|
| **Runtime** | Node.js 22+ / Express 5 |
| **Port** | 3117 |
| **Sources** | 29 OSINT data sources |
| **LLM Providers** | 9 (OpenAI, Anthropic, Mistral, Grok, Gemini, OpenRouter, Minimax, Ollama, Codex) |
| **Features** | Real-time intelligence dashboard, LLM-powered briefing synthesis, auto-refresh, multilingual alerts |

Key sources: ACLED, ADS-B, BLS, CISA KEV, Cloudflare Radar, Comtrade, EIA, EPA, FRED, FIRMS, GDELT, KiwiSDR, NOAA, OFAC, OpenSanctions, OpenSky, Patents, Reddit, ReliefWeb, Safecast, Ships, Space Track, Treasury, WHO, yfinance, and more.

### 📦 `packages/deer-flow/` — AI Agent Platform

| Detail | Value |
|--------|-------|
| **Frontend** | Next.js 16 + React 19 + pnpm |
| **Backend** | Python FastAPI + LangGraph + Uvicorn |
| **Port** | 8001 (backend) |
| **Maturity** | 2,251 commits (most mature package) |
| **Features** | Multi-agent orchestration, LangGraph workflows, MCP protocol, channel integrations (Telegram, Discord, Slack, WeChat, DingTalk, WeCom, Feishu), sandbox execution, memory management |

### 📦 `packages/autonomous-organism/` — Autonomous Organism Engine

| Detail | Value |
|--------|-------|
| **Runtime** | React 18 + Vite + TypeScript |
| **Backend** | Supabase (PostgreSQL + Edge Functions) |
| **Features** | Self-evolving organism simulation, sense/decision/factory/growth/immune/memory subsystems, real-time organism visualization, neural background effects |

### 📦 `packages/hermes-quant/` — Quantitative Trading Bot

| Detail | Value |
|--------|-------|
| **Runtime** | Python 3.11+ |
| **LLM** | NVIDIA Nemotron 70B (primary) + Groq (fallback) |
| **Agent Tools** | 21 (technical analysis, risk officer, kill switch, portfolio, market data, chart vision, news sentinel, backtest engine, etc.) |
| **Interface** | Telegram bot |
| **Features** | Strategy lifecycle management, autoswitch engine, pressure engine, audit logging, SMC agent, mathematical computation engine |

### 📦 `packages/agentic-legacy/` — Legacy AI System

| Detail | Value |
|--------|-------|
| **Runtime** | Python Flask |
| **Status** | Reference only (not actively developed) |
| **Purpose** | Preserved for historical reference and pattern extraction |

### 🖥️ `dashboard/` — Unified Dashboard

| Detail | Value |
|--------|-------|
| **Runtime** | Next.js 16 + React 19 + Tailwind CSS 4 + Zustand |
| **Port** | 3000 |
| **Features** | Colony management, agent monitoring, memory inspection, channel status, security overview, settings panel |

### 🧠 `ai_multicolony/` — Core Python Package

| Detail | Value |
|--------|-------|
| **Runtime** | Python 3.11+ / FastAPI |
| **Port** | 8000 |
| **Features** | Colony coordinator, agent loop, tool registry, event bus, LLM provider, memory manager, MCP server/client, multi-channel support, security analyzer, sandbox execution |

---

## Quickstart

### Prerequisites

| Requirement | Minimum Version |
|------------|-----------------|
| Python | 3.11+ |
| Node.js | 22+ |
| npm | 10+ |
| Git | 2.x |
| Docker (optional) | 24+ |
| Docker Compose (optional) | 2.x |

### One-Command Setup

```bash
git clone https://github.com/mulkymalikuldhrs/AI-MultiColony-Ecosystem.git
cd AI-MultiColony-Ecosystem
bash scripts/setup.sh
```

This will:
1. Check Python 3.11+ and Node 22+ are installed
2. Create a Python virtual environment
3. Install all Python and Node.js dependencies
4. Copy `.env.example` to `.env`

### Manual Setup

```bash
# 1. Install dependencies
make install

# 2. Configure environment
cp .env.example .env
# Edit .env with your API keys

# 3. Start services
make dev          # All services
make dev-api      # Just the API (port 8000)
make dev-web      # Just the dashboard (port 3000)
make dev-crucix   # Just Crucix OSINT (port 3117)
```

### Docker Setup

```bash
# Start the full stack
make docker-up

# Stop
make docker-down
```

---

## API Endpoints

### FastAPI Gateway (port 8000)

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/health` | Health check |
| `GET` | `/api/agents` | List all agents |
| `GET` | `/api/agents/{id}` | Get agent details |
| `POST` | `/api/agents/{id}/execute` | Execute agent task |
| `GET` | `/api/colony/status` | Colony status overview |
| `POST` | `/api/colony/dispatch` | Dispatch task to colony |
| `GET` | `/api/memory` | Query memory store |
| `POST` | `/api/memory/store` | Store memory entry |
| `GET` | `/api/tools` | List registered tools |
| `POST` | `/api/tools/{name}/execute` | Execute tool |
| `GET` | `/api/llm/providers` | List LLM providers |
| `POST` | `/api/llm/query` | Query LLM with failover |
| `GET` | `/api/credentials` | List credential keys |
| `POST` | `/api/credentials` | Store encrypted credential |
| `GET` | `/api/credentials/{name}` | Retrieve credential |
| `DELETE` | `/api/credentials/{name}` | Delete credential |
| `POST` | `/api/code/execute` | Execute code in sandbox |
| `WS` | `/ws/events` | WebSocket event stream |

### Crucix OSINT (port 3117)

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | Intelligence dashboard |
| `GET` | `/api/sources` | List OSINT sources |
| `GET` | `/api/briefing` | Generate LLM briefing |
| `GET` | `/api/alerts` | Active alerts |
| `POST` | `/api/sweep` | Run intelligence sweep |

### Deer Flow Backend (port 8001)

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/threads` | Create conversation thread |
| `POST` | `/api/threads/{id}/runs` | Start agent run |
| `GET` | `/api/threads/{id}/runs` | List runs |
| `GET` | `/api/models` | List available models |
| `POST` | `/api/auth/login` | Authenticate |
| `GET` | `/api/skills` | List agent skills |
| `GET` | `/api/mcp/tools` | List MCP tools |

---

## Environment Variables

All configuration is managed through a single `.env` file. See [`.env.example`](.env.example) for the complete list with documentation. Key sections:

| Section | Variables | Description |
|---------|-----------|-------------|
| **Core** | `APP_ENV`, `SECRET_KEY`, `LOG_LEVEL` | System-wide settings |
| **Database** | `DATABASE_URL`, `REDIS_URL`, `QDRANT_URL` | PostgreSQL, Redis, Qdrant connections |
| **LLM Providers** | `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, `GROQ_API_KEY`, ... | Shared across all packages |
| **Crucix** | `CRUCIX_PORT`, `CRUCIX_TELEGRAM_BOT_TOKEN`, ... | OSINT service config |
| **Deer Flow** | `DEER_FLOW_API_PORT`, `LANGCHAIN_API_KEY`, ... | Agent platform config |
| **Hermes Quant** | `NVIDIA_API_KEY`, `TELEGRAM_BOT_TOKEN`, ... | Trading bot config |
| **Autonomous Organism** | `SUPABASE_URL`, `SUPABASE_ANON_KEY`, ... | Organism engine config |
| **Security** | `CREDENTIAL_MASTER_PASSWORD`, `CORS_ALLOWED_ORIGINS` | Encryption & access control |

> **Important**: Set `SECRET_KEY` and `CREDENTIAL_MASTER_PASSWORD` to strong, unique values before deploying.

---

## Development

### Makefile Commands

```bash
make help          # Show all available commands
make install       # Install all dependencies
make dev           # Start all services in dev mode
make dev-api       # Start FastAPI backend (port 8000)
make dev-web       # Start Next.js dashboard (port 3000)
make dev-crucix    # Start Crucix OSINT (port 3117)
make build         # Build all packages
make test          # Run all tests
make test-python   # Run Python tests only
make test-js       # Run JavaScript tests only
make lint          # Run all linters
make docker-up     # Start Docker Compose stack
make docker-down   # Stop Docker Compose stack
make clean         # Clean all build artifacts
```

### Project Structure

```
AI-MultiColony-Ecosystem/
├── ai_multicolony/              # Core Python package (FastAPI backend)
│   ├── agents/                  # Agent implementations (Manus, Coder, Planner...)
│   ├── api/                     # FastAPI routes and schemas
│   ├── browser/                 # Stealth browser automation
│   ├── channels/                # Multi-channel (Telegram, Discord, Slack, WhatsApp)
│   ├── colony/                  # Colony coordination & scheduling
│   ├── config/                  # Logging and settings
│   ├── core/                    # BaseAgent, EventBus, ToolRegistry, LLMProvider
│   ├── mcp/                     # Model Context Protocol server/client
│   ├── memory/                  # Vector store, paging, session, knowledge
│   ├── sandbox/                 # Docker & WASM sandbox execution
│   ├── security/                # Analyzer, audit, permissions
│   └── tools/                   # Shell, file, browser, search, code, voice tools
├── dashboard/                   # Next.js 16 unified dashboard
├── packages/
│   ├── crucix/                  # OSINT intelligence (Express 5, 29 sources)
│   ├── deer-flow/               # AI agent platform (Next.js + FastAPI + LangGraph)
│   │   ├── frontend/            # Next.js 16 frontend
│   │   └── backend/             # FastAPI + LangGraph backend
│   ├── autonomous-organism/     # Autonomous organism engine (React + Supabase)
│   ├── hermes-quant/            # Quantitative trading bot (Python, 21 tools)
│   └── agentic-legacy/          # Legacy Flask system (reference only)
├── scripts/
│   ├── setup.sh                 # Full environment setup
│   ├── test-all.sh              # Cross-package test runner
│   └── entrypoint.sh            # Docker entrypoint
├── docs/                        # Architecture and design documents
├── docker-compose.yml           # Full stack orchestration
├── Makefile                     # Unified build & dev commands
├── package.json                 # npm workspaces root
├── .env.example                 # Consolidated env vars
└── pyproject.toml               # Python package config
```

---

## Docker Deployment

### Full Stack

```bash
# Start all services (API, Web, Crucix, Hermes, Postgres, Redis, Nginx)
docker compose up -d

# View logs
docker compose logs -f

# Stop
docker compose down
```

### Service Ports

| Service | Port | Description |
|---------|------|-------------|
| Nginx | 80, 443 | Reverse proxy (entry point) |
| Web Dashboard | 3000 | Next.js dashboard |
| FastAPI | 8000 | Main API gateway |
| Deer Flow | 8001 | Agent platform API |
| Crucix | 3117 | OSINT intelligence |
| PostgreSQL | 5432 | Primary database |
| Redis | 6379 | Cache + message broker |

---

## Testing

### Run All Tests

```bash
make test
# or
bash scripts/test-all.sh
```

### Run Specific Test Suites

```bash
# Python only
make test-python

# JavaScript only
make test-js

# Only Python core
python -m pytest tests/ -v

# Only Dashboard
cd dashboard && npm test

# Only Crucix
cd packages/crucix && npm test

# With coverage
python -m pytest tests/ --cov=ai_multicolony --cov-report=html
```

---

## Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

1. **Fork** the repository
2. Create a **feature branch** (`git checkout -b feature/amazing-feature`)
3. **Commit** your changes (`git commit -m 'Add amazing feature'`)
4. **Push** to the branch (`git push origin feature/amazing-feature`)
5. Open a **Pull Request**

---

## License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.

---

<p align="center">
  <img width="100%" src="https://capsule-render.vercel.app/api?type=waving&color=100:415a77,50:1b263b,0:0d1b2a&height=100&section=footer" />
</p>

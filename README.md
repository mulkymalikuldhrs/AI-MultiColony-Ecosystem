<a href="https://github.com/mulkymalikuldhrs/AI-MultiColony-Ecosystem">
  <img width="100%" src="https://capsule-render.vercel.app/api?type=waving&color=0:1a0a00,50:3d1f00,100:5c3000&height=220&section=header&text=AI%20MultiColony%20Ecosystem&fontSize=42&fontColor=f59e0b&animation=fadeIn&fontAlignY=30&desc=Multi-Agent%20Colony%20Coordination%20Platform&descSize=16&descColor=ef4444&descAlignY=50" />
</a>

<div align="center">

[![Typing SVG](https://readme-typing-svg.demolab.com?font=Fira+Code&size=20&duration=3000&pause=1000&color=f59e0b&center=true&vCenter=true&width=700&lines=25+Implemented+AI+Agents;Multi-LLM+Gateway+%2B+Automatic+Failover;AES-256+Encrypted+Credential+Vault;PWA+%2B+Docker+%2B+Kubernetes+Ready)](https://git.io/typing-svg)

<br/>

[![Python](https://img.shields.io/badge/Python-3.8+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-3-000000?style=for-the-badge&logo=flask&logoColor=white)](https://flask.palletsprojects.com/)
[![SQLite](https://img.shields.io/badge/SQLite-DB-003B57?style=for-the-badge&logo=sqlite&logoColor=white)](https://www.sqlite.org/)
[![AES-256](https://img.shields.io/badge/AES-256-Encryption-e74c3c?style=for-the-badge&logo=lock&logoColor=white)](https://cryptography.io/)
[![PWA](https://img.shields.io/badge/PWA-Ready-5A0FC8?style=for-the-badge&logo=pwa&logoColor=white)](https://web.dev/progressive-web-apps/)
[![Version](https://img.shields.io/badge/Version-0.3.0-orange?style=for-the-badge&logo=semanticrelease&logoColor=white)](https://github.com/mulkymalikuldhrs/AI-MultiColony-Ecosystem/releases)
[![MIT License](https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge&logo=opensourceinitiative&logoColor=white)](LICENSE)

<br/>

[![GitHub Stars](https://img.shields.io/github/stars/mulkymalikuldhrs/AI-MultiColony-Ecosystem?style=for-the-badge&logo=github&color=gold)](https://github.com/mulkymalikuldhrs/AI-MultiColony-Ecosystem/stargazers)
[![GitHub Forks](https://img.shields.io/github/forks/mulkymalikuldhrs/AI-MultiColony-Ecosystem?style=for-the-badge&logo=github&color=blue)](https://github.com/mulkymalikuldhrs/AI-MultiColony-Ecosystem/fork)
[![GitHub Issues](https://img.shields.io/github/issues/mulkymalikuldhrs/AI-MultiColony-Ecosystem?style=for-the-badge&logo=github&color=red)](https://github.com/mulkymalikuldhrs/AI-MultiColony-Ecosystem/issues)
[![GitHub Last Commit](https://img.shields.io/github/last-commit/mulkymalikuldhrs/AI-MultiColony-Ecosystem?style=for-the-badge&logo=github&color=orange)](https://github.com/mulkymalikuldhrs/AI-MultiColony-Ecosystem/commits/main)

</div>

---

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Agent Ecosystem](#agent-ecosystem)
- [Core Libraries](#core-libraries)
- [Architecture](#architecture)
- [Known Limitations](#known-limitations)
- [Honest Notes](#honest-notes)
- [Quick Start](#quick-start)
- [Configuration](#configuration)
- [API Documentation](#api-documentation)
- [Deployment](#deployment)
- [Security](#security)
- [Contributing](#contributing)
- [Disclaimer](#disclaimer)
- [License](#license)
- [Author](#author)

---

## Overview

AI MultiColony Ecosystem is a **multi-agent AI platform** built with Python and Flask that orchestrates 25 implemented AI agents across a unified web interface. It features a multi-LLM gateway with automatic failover (5 providers), AES-256 encrypted credential management, and Progressive Web App support.

The platform organizes agents into colony-style categories and includes substantial core libraries for quantitative trading (HermesQuantOS), autonomous organism systems, intelligence briefing (Crucix), and 8 IM channel integrations.

> **Transparency Notice**: This is a **v0.3.0 early-stage project** under active development. Some agent modules contain `TODO` placeholders and are not fully implemented. The "Money Making Agent" provides workflow scaffolding for revenue-generating tasks but does **not** autonomously generate income. No built-in user authentication in the Flask web app — a reverse proxy is required for production deployments. See [Known Limitations](#known-limitations) and [Honest Notes](#honest-notes) for full details.

---

## Features

### Implemented Features

- **25 Implemented AI Agents** — CyberShell, Agent Maker, Dev Engine, UI Designer, FullStack Dev, Bug Hunter, and more. See [Agent Ecosystem](#agent-ecosystem) for the complete list.
- **Multi-LLM Gateway with Failover** — 5 providers: LLM7 (free tier), OpenRouter, CAMEL, OpenAI, and Local models. Automatic failover when a provider is unavailable.
- **AES-256 Encrypted Credential Vault** — All stored credentials encrypted at rest using AES-256 via Fernet, with keys derived through PBKDF2HMAC at 100,000 iterations.
- **HermesQuantOS** — Full quantitative trading engine with 23 tool modules: math engine, risk officer, kill switch, decision engine, portfolio tool, and more.
- **Autonomous Organism System** — Self-organizing agent scheduler with sense, immune, decision, factory, and memory subsystems.
- **Crucix Intelligence Engine** — Python port with 27+ data sources, delta computation, briefing generator, and localization (i18n).
- **8 IM Channel Integrations** — Slack, Telegram, Discord, Feishu, WeChat, WeCom, DingTalk, plus a message bus.
- **API Gateway Framework** — Routing, middleware (18 modules), JWT auth, CSRF protection, localization, and pagination.
- **Progressive Web App** — Installable as a native-like app on desktop and mobile with offline caching.
- **Code Execution** — Multi-language code execution agent with optional Docker sandboxing.
- **Container-Ready** — Full Docker, Docker Compose, and Kubernetes deployment support.

### Not Yet Implemented

The following features are documented for planning purposes but do **not** have implementations yet:
- Built-in user authentication in the Flask web app (JWT auth library exists in `src/gateway/auth/` but is not wired into the Flask app)
- REST API endpoints for credential CRUD, code execution, and LLM queries
- Enterprise SSO, Global CDN, Auto-scaling
- SSL/TLS termination (relies on external reverse proxy)

---

## Agent Ecosystem

### Implemented Agents

The following agents have actual implementation files in the codebase:

#### Core Agents
| Agent | File | Description |
|-------|------|-------------|
| **CyberShell** | `agents/cybershell.py` | Shell execution, process management, and system monitoring |
| **Agent Maker** | `agents/agent_maker.py` | Dynamically creates and configures new agents |
| **Dev Engine** | `agents/dev_engine.py` | Project scaffolding, boilerplate generation, and CI/CD setup |
| **Meta Agent Creator** | `agents/meta_agent_creator.py` | Creates specialized agents dynamically based on requirements |
| **Commander AGI** | `agents/commander_agi.py` | Security monitoring and robotics coordination |

#### Development Agents
| Agent | File | Description |
|-------|------|-------------|
| **UI Designer** | `agents/ui_designer.py` | Generates React/NextJS components and responsive layouts |
| **FullStack Dev** | `agents/fullstack_dev.py` | End-to-end web application development (frontend + backend) |
| **Code Executor** | `agents/code_executor.py` | Multi-language code execution with Docker sandboxing |
| **Prompt Generator** | `agents/prompt_generator.py` | AI prompt engineering and optimization |

#### Infrastructure Agents
| Agent | File | Description |
|-------|------|-------------|
| **Deploy Manager** | `agents/deploy_manager.py` | Multi-platform deployment automation |
| **LLM Provider Manager** | `agents/llm_provider_manager.py` | Multi-LLM gateway with automatic failover |
| **System Optimizer** | `agents/system_optimizer.py` | System performance monitoring and optimization |
| **Data Sync** | `agents/data_sync.py` | Database and storage synchronization |
| **Backup Colony System** | `agents/backup_colony_system.py` | Distributed backup and redundancy management |

#### Security Agents
| Agent | File | Description |
|-------|------|-------------|
| **Bug Hunter Bot** | `agents/bug_hunter_bot.py` | Vulnerability discovery and ethical hacking |
| **Credential Manager** | `agents/credential_manager.py` | Secure credential storage with AES-256/Fernet encryption |
| **Authentication Agent** | `agents/authentication_agent.py` | Auto-login and registration (Selenium-based) |

#### Business & Research Agents
| Agent | File | Description |
|-------|------|-------------|
| **Marketing Agent** | `agents/marketing_agent.py` | Marketing automation and outreach |
| **Money Making Agent** | `agents/money_making_agent.py` | Workflow scaffolding for revenue tasks — **not** autonomous income generation |
| **AI Research** | `agents/ai_research_agent.py` | AI research monitoring and development |
| **Knowledge Management** | `agents/knowledge_management_agent.py` | Knowledge curation and retrieval |
| **Quality Control Specialist** | `agents/quality_control_specialist.py` | Visual and analytical quality assessment |
| **Deployment Specialist** | `agents/deployment_specialist.py` | Colony deployment automation |
| **AGIColony Connector** | `agents/agi_colony_connector.py` | Inter-colony communication |

#### Deer-Flow Agents (`src/agents/`)
| Agent | File | Description |
|-------|------|-------------|
| **Lead Agent** | `src/agents/lead_agent/agent.py` | LangGraph-based lead agent with tracing callbacks |
| **Web Automation** | `src/agents/web_automation_agent.py` | Web automation using Selenium |
| **Deployment Agent** | `src/agents/deployment_agent.py` | Platform deployment (Netlify, Supabase) |
| **Dynamic Agent Factory** | `src/agents/dynamic_agent_factory.py` | Runtime agent creation and management |
| **Agent 02-06** | `src/agents/agent_0[2-6]_*.py` | Specialized pipeline agents (meta spawner, planner, executor, designer, specialist) |

#### Thin Stub Agents
| Agent | File | Notes |
|-------|------|-------|
| **Data Scientist** | `agents/data_scientist.py` | Auto-generated stub (94 lines) — needs implementation |
| **Test Agent** | `agents/test_agent.py` | Auto-generated stub (94 lines) — needs implementation |

### Planned Agents (Not Yet Implemented)

The following agents are listed for future development. They do **not** have implementation files:

| Category | Planned Agents |
|----------|---------------|
| **Core** | Colony Coordinator, System Monitor |
| **Security** | Security Scanner, Vulnerability Analyzer, Auth Guardian |
| **Infrastructure** | Infrastructure Monitor, Network Manager, Resource Optimizer |
| **Development** | Code Generator, Code Reviewer, Test Runner, Documentation Generator, Refactoring Agent, Version Control Agent |
| **Data & Knowledge** | Data Pipeline Agent, Search Agent |
| **Business & Marketing** | SEO Agent, Content Writer, Social Media Agent, Analytics Agent |
| **Quality** | Compliance Checker, Performance Tester, Integration Tester |

> If you'd like to implement one of these planned agents, see [Contributing](#contributing) for how to get started.

---

## Core Libraries

Beyond the agents listed above, the project contains substantial Python libraries that form the backbone of the system:

### HermesQuantOS (`src/quant/`)
A full quantitative trading engine with 23 tool modules:
- **MathEngine** — Numerical computation for trading indicators
- **RiskOfficer** — Risk assessment and position sizing
- **KillSwitch** — Emergency circuit breaker for trading
- **DecisionEngine** — Trade decision logic with multi-factor analysis
- **PortfolioTool** — Portfolio management and rebalancing
- **MarketState** — Market regime detection
- **AutoSwitch** — Automatic strategy switching based on conditions
- **PressureEngine** — Market pressure analysis
- **NewsSentinel** — News monitoring and sentiment analysis
- **SMCAgent** — Smart money concept analysis
- **TechnicalAnalysis** — Technical indicator computation
- **MacroSentiment** — Macroeconomic sentiment tracking
- **StrategyLifecycle** — Strategy creation, backtesting, and lifecycle management
- **AuditLogger** — Comprehensive audit trail logging
- **Watchdog** — System health monitoring for the quant subsystem
- Plus: BacktestEngine, ChartVisionTool, ExecutionTool, JournalTool, MarketDataTool, AuditorResearchTool, StrategyTool, SharedState

### Autonomous Organism (`src/organism/`)
A self-organizing system inspired by biological organisms:
- **Scheduler** — Agent scheduling with configurable intervals
- **Sense** — Environmental perception and data ingestion
- **Immune** — Threat detection and system defense
- **Decision** — Autonomous decision-making based on sensory input
- **Factory** — Dynamic agent creation and configuration
- **Memory** — Persistent state management across cycles

### Crucix Intelligence Engine (`src/crucix/`)
A Python port of the Crucix intelligence briefing system:
- **Config** — Configuration management for data sources and alerts
- **Localization** — Multi-language support (i18n)
- **Briefing** — Intelligence briefing generation from multiple data sources
- **DataSources** — 27+ data source integrations (NOAA, FRED, BLS, WHO, ACLED, GDELT, etc.)
- **Gateway** — API gateway for the Crucix subsystem

### IM Channels (`src/channels/`)
Eight instant messaging channel integrations:
- **Slack** — Slack workspace integration
- **Telegram** — Telegram bot integration
- **Discord** — Discord bot integration
- **Feishu** — Feishu/Lark integration
- **WeChat** — WeChat integration
- **WeCom** — WeCom (enterprise WeChat) integration
- **DingTalk** — DingTalk integration
- **MessageBus** — Internal message routing between channels
- **Base** — Abstract base class for channel implementations
- **Manager** — Channel lifecycle and configuration management
- **Service** — Service layer for channel operations
- **Commands** — Command routing across channels
- **Store** — Channel state persistence

### API Gateway (`src/gateway/`)
A comprehensive API gateway framework:
- **Router** — Request routing and dispatch
- **Auth** — JWT authentication, providers, password hashing, SQLite repository
- **Middleware** — 18 middleware modules for request processing
- **CSRF** — Cross-site request forgery protection
- **Localization** — Request/response localization
- **Pagination** — API response pagination
- **Routers** — Sub-routers for agents, channels, skills, memory, MCP, models, feedback, threads, uploads, runs, auth, and more

### Additional Libraries

| Module | Path | Description |
|--------|------|-------------|
| **MCP** | `src/mcp/` | Model Context Protocol client, tools, session pooling, OAuth, caching |
| **Guardrails** | `src/guardrails/` | Pre-tool-call authorization middleware and providers |
| **Skills** | `src/skills/` | Dynamic skill system with installer, parser, validation, security scanner, permissions |
| **Persistence** | `src/persistence/` | SQLAlchemy 2.0 async ORM for runs, threads, users, feedback; Alembic migrations |
| **Runtime** | `src/runtime/` | Agent runtime: checkpointer, events, runs, serialization, stream bridge |
| **Middlewares** | `src/middlewares/` | 18 middleware modules (safety, summarization, loop detection, tool error handling, etc.) |
| **LLM Models** | `src/llm_models/` | LLM provider abstractions (OpenAI, Claude, vLLM, DeepSeek, MindIE, etc.) |
| **Community** | `src/community/` | Community integrations (DuckDuckGo search, Exa, Firecrawl, Tavily, Jina AI, etc.) |
| **Sandbox** | `src/sandbox/` | Local sandbox for code execution with security constraints |
| **Subagents** | `src/subagents/` | Sub-agent orchestration (bash agent, general-purpose agent) |
| **DF Tools** | `src/df_tools/` | Deer-flow built-in tools (clarification, task, tool search, etc.) |
| **Config** | `src/config/` | 25+ configuration modules (model, memory, skills, guardrails, etc.) |
| **Memory** | `src/memory/` | Conversation memory with LLM summarization, storage, and queue management |
| **Tracing** | `src/tracing/` | OpenTelemetry tracing factory and metadata |

---

## Architecture

```
+---------------------------------------------------------------------+
|                     AI MultiColony Ecosystem                         |
+---------------------------------------------------------------------+
|                                                                     |
|  +----------------------+    +----------------------------------+  |
|  |   PWA Frontend       |    |   Web Dashboard (Flask/Jinja2)   |  |
|  |  +----------------+  |    |  +--------+ +--------+ +------+ |  |
|  |  | Service Worker |  |    |  | Agents | | Creds  | | LLM  | |  |
|  |  | Web Manifest   |  |    |  | Panel  | | Vault  | | Config| |  |
|  |  +----------------+  |    |  +--------+ +--------+ +------+ |  |
|  +----------+-----------+    +--------------+-------------------+  |
|             |                              |                       |
|             +---------------+--------------+                       |
|                             |                                      |
|                  +----------v----------+                           |
|                  |  Flask App          |                           |
|                  |  (app.py)           |                           |
|                  +----------+----------+                           |
|                             |                                      |
|          +------------------+------------------+                   |
|          |                  |                  |                   |
|  +-------v------+  +-------v------+  +--------v------+           |
|  | Agent System |  | Core Libs    |  | LLM Gateway   |           |
|  | +----------+ |  | +----------+ |  | (Failover)    |           |
|  | |CyberShell| |  | |Quant     | |  +---+--+---+---+           |
|  | |AgentMaker| |  | |Organism  | |  |   |  |   |               |
|  | |DevEngine | |  | |Crucix    | |  +---+--+---+---+           |
|  | |...25 more| |  | |Channels  | |  |   |  |   |               |
|  | +----------+ |  | |Gateway   | |  LLM7 Open    CAMEL         |
|  +------+-------+  | |MCP       | |  OpenRouter  Local          |
|         |          | |...       | |                              |
|         |          | +----------+ |                              |
|         |          +------+-------+                              |
|         |                 |                                      |
|         +--------+--------+                                      |
|                  |                                                 |
|       +----------v-----------+                                    |
|       |  Credential Vault    |    +---------------------------+   |
|       |  AES-256 / Fernet   |    |   SQLite Database         |   |
|       |  PBKDF2HMAC 100k    |    |   (Agents, Config, Logs)  |   |
|       +----------------------+    +---------------------------+   |
|                                                                     |
+---------------------------------------------------------------------+
```

---

## Known Limitations

> These are important constraints. Please review before deploying.

| Limitation | Impact | Workaround |
|-----------|--------|------------|
| **No built-in authentication in Flask app** | Anyone with network access can use the platform | Use a reverse proxy (Nginx/Apache) with HTTP Basic Auth or OAuth |
| **Auth library exists but not wired in** | `src/gateway/auth/` has JWT auth but it's not connected to the Flask app | Wire it in or use proxy-level auth |
| **Many API endpoints documented but not implemented** | `/api/agents/{id}/execute`, `/api/llm/query`, `/api/credentials` CRUD, `/api/code/execute` don't exist | Use the existing endpoints; see [API Documentation](#api-documentation) |
| **Duplicate credential managers** | Two implementations exist — potential confusion | Use the `src/core/` version which is the more secure implementation |
| **Incomplete agent implementations** | Some agents contain `TODO` placeholders; 2 agents are auto-generated stubs | Check agent source before relying on functionality |
| **Integrations are standalone adapters** | AutoGen, CrewAI, LangGraph integrations exist but are not wired into main entry points | Must be manually instantiated; see deprecation notices in source |
| **"Money Making Agent" is scaffolding only** | Does not autonomously generate income | Use it as a template for building custom revenue workflows |
| **SQLite for production** | Not ideal for high-concurrency workloads | Consider PostgreSQL for production deployments |
| **Single-process Flask** | Not suitable for high-traffic production | Use Gunicorn/uWSGI with multiple workers |
| **Missing imports in requirements.txt** | Some third-party imports are not listed | Agents fail gracefully; install missing packages as needed |

---

## Honest Notes

> We believe in radical transparency. Here are important clarifications about this project.

1. **Early-stage project (v0.3.0)** — Some agents contain `TODO` placeholders and are not fully implemented. The agent list in this README reflects only agents that have actual implementation files. See [Planned Agents](#planned-agents-not-yet-implemented) for aspirational ones.

2. **No built-in user authentication in the Flask web app** — While `src/gateway/auth/` contains a JWT auth system, it is NOT wired into the Flask web app. For production deployments, use a reverse proxy (e.g., Nginx with `auth_basic`, Traefik with forward auth, or Cloudflare Access).

3. **LLM providers** — The gateway supports 5 providers: LLM7, OpenRouter, CAMEL, OpenAI, and Local models. DeepSeek, Anthropic, Google AI, and Hugging Face are **not** in the gateway code (though `src/llm_models/` has provider abstractions for Claude and DeepSeek).

4. **API documentation accuracy** — Only the endpoints listed in the [API Documentation](#api-documentation) section below actually exist. Previously documented endpoints like `/api/agents/{id}/execute`, `/api/llm/query`, credentials CRUD, and `/api/code/execute` do NOT exist.

5. **"Money Making Agent" is workflow scaffolding** — This agent provides templates and workflow structures for revenue-related tasks. It does **not** autonomously generate income, trade assets, or make financial decisions.

6. **Duplicate credential managers** — Two credential manager implementations exist in the codebase. The version in `src/core/` uses the more secure AES-256/Fernet implementation with PBKDF2HMAC key derivation. Prefer this version for production use.

7. **Integrations (AutoGen, CrewAI, LangGraph)** — These are standalone adapter files that are never imported by any main entry point. They require manual instantiation and are marked with deprecation notices. See source files for details.

---

## Quick Start

### Prerequisites

- Python 3.8 or higher
- pip package manager
- (Optional) Docker for containerized deployment

### Installation

```bash
# Clone the repository
git clone https://github.com/mulkymalikuldhrs/AI-MultiColony-Ecosystem.git
cd AI-MultiColony-Ecosystem

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env — set CREDENTIAL_MASTER_PASSWORD and SECRET_KEY (see Configuration below)

# Launch the platform
python web_interface/app.py
```

The dashboard will be available at **http://localhost:5000**.

### Verify Installation

```bash
# Check that the Flask app starts correctly
python -c "from web_interface.app import app; print('OK')"

# Verify credential encryption is working
python -c "from src.core.credential_manager import CredentialManager; print('Vault OK')"
```

---

## Configuration

All configuration is managed through environment variables and the `.env` file.

### `.env` Template

```env
# ============================================
# AI MultiColony Ecosystem Configuration
# ============================================

# --- Core Settings ---
SECRET_KEY=your-super-secret-flask-key-change-this
CREDENTIAL_MASTER_PASSWORD=your-master-password-for-aes256-encryption
FLASK_ENV=development
FLASK_DEBUG=1
PORT=5000
HOST=0.0.0.0

# --- Database ---
DATABASE_PATH=data/multicolony.db

# --- LLM Provider API Keys ---
# Only configure the providers you intend to use.
# The gateway will skip unconfigured providers and failover to the next.
# Supported providers: LLM7, OpenRouter, CAMEL, OpenAI, Local

LLM7_API_KEY=                    # Free tier — no key required
OPENROUTER_API_KEY=              # https://openrouter.ai/
CAMEL_API_KEY=                   # https://camel-ai.org/
OPENAI_API_KEY=                  # https://platform.openai.com/
# Local models run on localhost:11434 (Ollama)

# --- Default LLM Settings ---
DEFAULT_LLM_PROVIDER=llm7
DEFAULT_LLM_MODEL=default
LLM_TEMPERATURE=0.7
LLM_MAX_TOKENS=2048

# --- Code Execution ---
ENABLE_CODE_EXECUTION=true
DOCKER_SANDBOX_ENABLED=false
DOCKER_SANDBOX_IMAGE=python:3.11-slim

# --- PWA Settings ---
PWA_CACHE_NAME=multicolony-v2
PWA_OFFLINE_PAGE=/offline.html

# --- Security ---
CREDENTIAL_ENCRYPTION_ITERATIONS=100000
SESSION_TIMEOUT=3600
```

### Key Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `SECRET_KEY` | Yes | Flask session signing key — use a strong random string |
| `CREDENTIAL_MASTER_PASSWORD` | Yes | Master password for AES-256 credential encryption |
| `LLM7_API_KEY` | No | Free-tier LLM provider (no key required for basic use) |
| `OPENAI_API_KEY` | No | OpenAI GPT models |
| `OPENROUTER_API_KEY` | No | OpenRouter multi-model hub |
| `CAMEL_API_KEY` | No | CAMEL AI provider |
| `DOCKER_SANDBOX_ENABLED` | No | Enable Docker isolation for code execution (default: `false`) |

---

## API Documentation

> **Note**: Only the endpoints listed below actually exist in the Flask application. Endpoints previously documented (such as `/api/agents/{id}/execute`, `/api/llm/query`, `/api/credentials` CRUD, and `/api/code/execute`) do **not** exist.

### Base URL

```
http://localhost:5000/api
```

### System Status

#### Get System Status

```http
GET /api/system/status
```

**Response:**
```json
{
  "success": true,
  "data": {
    "system_status": "running",
    "agents_active": 10,
    "total_agents": 14,
    "loaded_agents": ["cybershell", "agent_maker", "..."],
    "version": "0.3.0",
    "components": {
      "memory_bus": true,
      "llm_gateway": true
    }
  }
}
```

### Agent Management

#### List All Agents

```http
GET /api/agents/list
```

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "id": "cybershell",
      "name": "CyberShell",
      "status": "ready",
      "capabilities": ["shell_execution", "process_management"]
    }
  ]
}
```

#### Get Agent Status

```http
GET /api/agents/<agent_id>/status
```

**Response:**
```json
{
  "success": true,
  "data": {
    "agent_id": "cybershell",
    "name": "CyberShell",
    "status": "ready",
    "capabilities": ["shell_execution", "process_management"]
  }
}
```

### Task Execution

#### Submit Task to Agent

```http
POST /api/task/submit
Content-Type: application/json

{
  "agent_id": "cybershell",
  "task": "List all running processes"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "success": true,
    "output": "..."
  }
}
```

### Prompt Processing

#### Process a Prompt

```http
POST /api/prompt/process
Content-Type: application/json

{
  "prompt": "Create a web application for task management",
  "input_type": "text"
}
```

### LLM Gateway

#### Get LLM Provider Status

```http
GET /api/llm/providers
```

**Response:**
```json
{
  "success": true,
  "data": {
    "providers": {
      "llm7": {"status": "active", "priority": 1, "models": ["gpt-3.5-turbo", "gpt-4", "claude-3-sonnet"]},
      "openrouter": {"status": "available", "priority": 2},
      "camel": {"status": "available", "priority": 3},
      "openai": {"status": "fallback", "priority": 4},
      "local": {"status": "optional", "priority": 5}
    }
  }
}
```

#### Test All LLM Providers

```http
POST /api/llm/test
```

### Memory & Performance

#### Get Memory Stats

```http
GET /api/memory/stats
```

#### Get Performance Metrics

```http
GET /api/performance/metrics
```

### Workflows

#### Execute a Workflow

```http
POST /api/workflows/execute
Content-Type: application/json

{
  "workflow_id": "custom",
  "steps": [
    {"agent_id": "cybershell", "task": {"description": "Check system status"}},
    {"agent_id": "bug_hunter", "task": {"description": "Scan for vulnerabilities"}}
  ]
}
```

### WebSocket Events

The system supports real-time updates via SocketIO:

- `connect` — Client connection
- `subscribe_updates` — Subscribe to system status updates
- `request_status_update` — Request current status
- `system_update` — Periodic system status broadcasts

---

## Deployment

### Docker

```bash
# Build the image
docker build -t multicolony-ecosystem .

# Run the container
docker run -d \
  --name multicolony \
  -p 5000:5000 \
  -e SECRET_KEY=your-secret-key \
  -e CREDENTIAL_MASTER_PASSWORD=your-master-password \
  -v multicolony-data:/app/data \
  multicolony-ecosystem
```

### Docker Compose

```yaml
version: '3.8'

services:
  multicolony:
    build: .
    container_name: multicolony-ecosystem
    ports:
      - "5000:5000"
    environment:
      - SECRET_KEY=${SECRET_KEY}
      - CREDENTIAL_MASTER_PASSWORD=${CREDENTIAL_MASTER_PASSWORD}
      - FLASK_ENV=production
      - DOCKER_SANDBOX_ENABLED=true
    volumes:
      - multicolony-data:/app/data
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:5000/"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

volumes:
  multicolony-data:
    driver: local
```

```bash
# Start the stack
docker compose up -d

# View logs
docker compose logs -f multicolony

# Stop
docker compose down
```

### Kubernetes

```yaml
# deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: multicolony-ecosystem
  labels:
    app: multicolony
spec:
  replicas: 2
  selector:
    matchLabels:
      app: multicolony
  template:
    metadata:
      labels:
        app: multicolony
    spec:
      containers:
        - name: multicolony
          image: multicolony-ecosystem:latest
          ports:
            - containerPort: 5000
          env:
            - name: SECRET_KEY
              valueFrom:
                secretKeyRef:
                  name: multicolony-secrets
                  key: secret-key
            - name: CREDENTIAL_MASTER_PASSWORD
              valueFrom:
                secretKeyRef:
                  name: multicolony-secrets
                  key: master-password
            - name: FLASK_ENV
              value: "production"
          resources:
            requests:
              memory: "256Mi"
              cpu: "250m"
            limits:
              memory: "512Mi"
              cpu: "500m"
          livenessProbe:
            httpGet:
              path: /
              port: 5000
            initialDelaySeconds: 30
            periodSeconds: 30
          readinessProbe:
            httpGet:
              path: /
              port: 5000
            initialDelaySeconds: 10
            periodSeconds: 10
          volumeMounts:
            - name: data
              mountPath: /app/data
      volumes:
        - name: data
          persistentVolumeClaim:
            claimName: multicolony-pvc
---
apiVersion: v1
kind: Service
metadata:
  name: multicolony-service
spec:
  selector:
    app: multicolony
  ports:
    - protocol: TCP
      port: 80
      targetPort: 5000
  type: ClusterIP
---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: multicolony-pvc
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 1Gi
```

```bash
# Create secrets
kubectl create secret generic multicolony-secrets \
  --from-literal=secret-key='your-secret-key' \
  --from-literal=master-password='your-master-password'

# Deploy
kubectl apply -f deployment.yaml

# Check status
kubectl get pods -l app=multicolony
```

### Production Checklist

- [ ] Set strong `SECRET_KEY` and `CREDENTIAL_MASTER_PASSWORD`
- [ ] Use a reverse proxy (Nginx/Traefik) with TLS termination
- [ ] Enable HTTP Basic Auth or OAuth at the proxy level
- [ ] Set `FLASK_ENV=production` and `FLASK_DEBUG=0`
- [ ] Use Gunicorn with multiple workers: `gunicorn -w 4 -b 0.0.0.0:5000 web_interface.app:app`
- [ ] Enable Docker sandboxing for code execution
- [ ] Configure regular database backups
- [ ] Set up monitoring and alerting
- [ ] Wire `src/gateway/auth/` into the Flask app for built-in authentication

---

## Security

### Credential Encryption

All credentials stored in the vault are encrypted at rest using **AES-256** via the Fernet symmetric encryption scheme:

- **Key Derivation**: PBKDF2HMAC with SHA-256
- **Iterations**: 100,000 (configurable via `CREDENTIAL_ENCRYPTION_ITERATIONS`)
- **Salt**: Randomly generated per encryption key
- **Master Password**: Never stored — derived into an encryption key at runtime

```python
# Encryption flow (simplified)
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.fernet import Fernet
import base64

kdf = PBKDF2HMAC(
    algorithm=hashes.SHA256(),
    length=32,
    salt=salt,
    iterations=100000,
)
key = base64.urlsafe_b64encode(kdf.derive(master_password.encode()))
fernet = Fernet(key)
encrypted = fernet.encrypt(credential_value.encode())
```

### Security Considerations

| Area | Status | Recommendation |
|------|--------|---------------|
| Encryption at rest | AES-256 via Fernet | Ensure `CREDENTIAL_MASTER_PASSWORD` is strong |
| TLS/HTTPS | Not built-in | Use reverse proxy with TLS termination |
| Authentication | JWT library exists but not wired into Flask app | Use reverse proxy auth OR wire `src/gateway/auth/` into Flask |
| Code execution sandboxing | Optional | Enable `DOCKER_SANDBOX_ENABLED=true` in production |
| Rate limiting | Not built-in | Add Flask-Limiter or proxy-level rate limiting |
| Input validation | Partial | Review agent inputs before production use |
| CORS | Default open | Restrict `CORS_ORIGINS` in production |
| Audit logging | Quant-only | General audit logging not yet implemented |

---

## Contributing

Contributions are welcome! This project has specific areas where help is most needed.

### Priority Areas

| Priority | Area | Description |
|----------|------|-------------|
| High | **Planned agent implementations** | Implement agents from the [Planned Agents](#planned-agents-not-yet-implemented) list |
| High | **Wire auth into Flask** | Connect `src/gateway/auth/` JWT system to the Flask web app |
| High | **Missing API endpoints** | Implement `/api/credentials` CRUD, `/api/code/execute`, `/api/llm/query` |
| High | **Missing requirements.txt entries** | Identify and add missing third-party dependencies |
| Medium | **Deduplicate credential managers** | Consolidate into a single, well-tested implementation |
| Medium | **Test coverage** | Add tests for untested modules (channels, mcp, guardrails, skills, etc.) |
| Medium | **Integration wiring** | Wire AutoGen/CrewAI/LangGraph into main entry points |
| Low | **Documentation** | Improve agent documentation and usage examples |
| Low | **PostgreSQL support** | Add database backend option beyond SQLite |

### How to Contribute

1. **Fork** the repository
2. Create a **feature branch** (`git checkout -b feature/amazing-feature`)
3. **Commit** your changes (`git commit -m 'Add amazing feature'`)
4. **Push** to the branch (`git push origin feature/amazing-feature`)
5. Open a **Pull Request**

### Development Setup

```bash
# Clone and install in development mode
git clone https://github.com/mulkymalikuldhrs/AI-MultiColony-Ecosystem.git
cd AI-MultiColony-Ecosystem
pip install -r requirements.txt
pip install -r requirements-dev.txt  # If available

# Run in debug mode
FLASK_ENV=development FLASK_DEBUG=1 python web_interface/app.py

# Run existing tests
python -m pytest tests/
```

### Code Style

- Follow PEP 8 for Python code
- Use descriptive variable and function names
- Add docstrings to public functions and classes
- Handle `ImportError` gracefully for optional dependencies

---

## Disclaimer

**For Education and Research Purpose Only**

This project is provided strictly for educational and research purposes. The authors and contributors assume **no responsibility or liability** for any damages, losses, or risks arising from the use of this software.

**Important:**
- **We do not guarantee** that any agent will function as described, especially those marked with `TODO` placeholders or listed as auto-generated stubs.
- **We do not bear any responsibility or risk** for how this software is used.
- **The "Money Making Agent"** is workflow scaffolding only — it does not generate income autonomously and should not be relied upon for financial decisions.
- **No warranty** is provided, express or implied. Use at your own risk.

---



## License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.

```
MIT License

Copyright (c) 2024-2026 Mulky Malikul Dhaher

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

---

## Author

**Mulky Malikul Dhaher**

[![GitHub](https://img.shields.io/badge/GitHub-mulkymalikuldhrs-181717?style=for-the-badge&logo=github&logoColor=white)](https://github.com/mulkymalikuldhrs)
[![Email](https://img.shields.io/badge/Email-mulkymalikudhr%40mail.com-D14836?style=for-the-badge&logo=gmail&logoColor=white)](mailto:mulkymalikudhr@mail.com)

---

<a href="https://github.com/mulkymalikuldhrs/AI-MultiColony-Ecosystem">
  <img width="100%" src="https://capsule-render.vercel.app/api?type=waving&color=100:5c3000,50:3d1f00,0:1a0a00&height=100&section=footer" />
</a>

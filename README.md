<img src="docs/banner.png" width="100%">

<a href="https://github.com/mulkymalikuldhrs/AI-MultiColony-Ecosystem">
  <img width="100%" src="https://capsule-render.vercel.app/api?type=waving&color=0:0a0a1a,50:1a1a3e,100:2d1b69&height=220&section=header&text=AI%20MultiColony%20Ecosystem&fontSize=42&fontColor=7c3aed&animation=fadeIn&fontAlignY=30&desc=5-Package%20Monorepo%20%7C%20Multi-LLM%20%7C%20OSINT%20%2B%20Trading%20%2B%20Autonomous%20Agents&descSize=16&descColor=a78bfa&descAlignY=50" />
</a>

<div align="center">

[![Typing SVG](https://readme-typing-svg.demolab.com?font=Fira+Code&size=22&duration=3000&pause=1000&color=7C3AED&center=true&vCenter=true&width=720&lines=5-Package+Integrated+Monorepo;Multi-LLM+9-Provider+Router;Crucix+OSINT+%2B+deer-flow+Agents;HermesQuantOS+Trading+Engine;Autonomous+Organism+Engine)](https://git.io/typing-svg)

<br/>

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Next.js](https://img.shields.io/badge/Next.js-16-000000?style=for-the-badge&logo=nextdotjs&logoColor=white)](https://nextjs.org)
[![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?style=for-the-badge&logo=docker&logoColor=white)](https://docker.com)
[![Multi-LLM](https://img.shields.io/badge/Multi--LLM-9_Providers-7c3aed?style=for-the-badge&logo=ai&logoColor=white)](#)
[![License](https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge&logo=opensourceinitiative&logoColor=white)](LICENSE)

<br/>

[![GitHub Stars](https://img.shields.io/github/stars/mulkymalikuldhrs/AI-MultiColony-Ecosystem?style=for-the-badge&logo=github&color=gold)](https://github.com/mulkymalikuldhrs/AI-MultiColony-Ecosystem/stargazers)
[![GitHub Forks](https://img.shields.io/github/forks/mulkymalikuldhrs/AI-MultiColony-Ecosystem?style=for-the-badge&logo=github&color=blue)](https://github.com/mulkymalikuldhrs/AI-MultiColony-Ecosystem/fork)
[![GitHub Issues](https://img.shields.io/github/issues/mulkymalikuldhrs/AI-MultiColony-Ecosystem?style=for-the-badge&logo=github&color=red)](https://github.com/mulkymalikuldhrs/AI-MultiColony-Ecosystem/issues)

<br/>

**Language / Bahasa / 语言**

[![EN](https://img.shields.io/badge/EN-English-blue?style=flat-square)](README.md)
[![ID](https://img.shields.io/badge/ID-Bahasa%20Indonesia-red?style=flat-square)](README_id.md)
[![CN](https://img.shields.io/badge/CN-中文-green?style=flat-square)](README_zh.md)

</div>

---

## Overview

**AI MultiColony Ecosystem** is a monorepo containing 5 integrated packages that together form a multi-agent AI platform spanning OSINT intelligence, autonomous agent orchestration, quantitative trading, and self-evolving organisms. The core Python backend (`ai_multicolony/`) exposes a FastAPI API, while a Next.js 16 dashboard provides real-time monitoring and control.

> **Honest Note**: This is a **research platform and scaffold**. Many modules are in active development. The 5 packages vary in maturity — some have substantial test suites, others are early prototypes. See the [Maturity Assessment](#maturity-assessment) below for details.

### The 5 Packages

| Package | Purpose | Language | Status |
|---------|---------|----------|--------|
| **Crucix** | OSINT intelligence platform — 25+ data sources, multi-LLM briefing engine, real-time alerts | Node.js / JavaScript | Active development |
| **deer-flow** | AI Agent Platform — skill-based workflow engine, multi-modal generation, LangGraph/CrewAI adapters | Python + Next.js | Active development |
| **autonomous-organism** | Autonomous Engine — sense/decide/act loop, self-evolving, Supabase-backed | TypeScript + Python | Early prototype |
| **HermesQuantOS** | Trading Engine — 5-layer decision stack, risk guardian, exchange adapters | Python | Active development |
| **Agentic-AI-System_OLD** | Legacy reference — original multi-agent system, Flask + WebSocket | Python | Archived (read-only) |

---

## Visual Architecture

### 1. Ecosystem Architecture — All 5 Packages as Equal Peers

```mermaid
graph TB
    subgraph Frontend["Frontend Layer"]
        Dashboard["Next.js 16 Dashboard<br/>Real-time Monitoring"]
        CrucixUI["Crucix Dashboard<br/>OSINT Visualization"]
        DeerUI["deer-flow Frontend<br/>Agent Chat and Skills"]
        OrganismUI["Organism UI<br/>Live Evolution View"]
    end

    subgraph Gateway["API Gateway"]
        Nginx["Nginx Reverse Proxy<br/>:80 / :443"]
        FastAPI["FastAPI Backend<br/>ai_multicolony/"]
    end

    subgraph Packages["Core Packages — Equal Peers"]
        Crucix["Crucix<br/>OSINT Engine<br/>25+ Data Sources"]
        DeerFlow["deer-flow<br/>AI Agent Platform<br/>Skill Orchestration"]
        Organism["autonomous-organism<br/>Self-Evolving Engine<br/>Sense/Decide/Act"]
        Hermes["HermesQuantOS<br/>Trading Engine<br/>5-Layer Decision Stack"]
        Legacy["Agentic-AI-System_OLD<br/>Legacy Reference<br/>Archived"]
    end

    subgraph Infra["Infrastructure"]
        Docker["Docker Compose<br/>Orchestration"]
        DB["PostgreSQL + Redis<br/>State and Cache"]
        Monitoring["Prometheus + Grafana<br/>Observability"]
    end

    Dashboard --> Nginx
    CrucixUI --> Nginx
    DeerUI --> Nginx
    OrganismUI --> Nginx

    Nginx --> FastAPI

    FastAPI --> Crucix
    FastAPI --> DeerFlow
    FastAPI --> Organism
    FastAPI --> Hermes

    Crucix -.->|"Intel Feed"| DeerFlow
    DeerFlow -.->|"Agent Delegation"| Organism
    Hermes -.->|"Market Data"| Crucix
    Organism -.->|"Self-Optimize"| Hermes

    Legacy -.->|"Historical Reference"| FastAPI

    FastAPI --> DB
    FastAPI --> Monitoring
    Docker --> FastAPI

    style Crucix fill:#1e40af,stroke:#3b82f6,color:#fff
    style DeerFlow fill:#065f46,stroke:#10b981,color:#fff
    style Organism fill:#7c2d12,stroke:#f97316,color:#fff
    style Hermes fill:#581c87,stroke:#a855f7,color:#fff
    style Legacy fill:#374151,stroke:#6b7280,color:#9ca3af
    style FastAPI fill:#134e4a,stroke:#14b8a6,color:#fff
    style Nginx fill:#1e293b,stroke:#475569,color:#fff
```

### 2. Agent Communication Flow — Sequence Diagram

```mermaid
sequenceDiagram
    participant User
    participant Dashboard as Next.js Dashboard
    participant API as FastAPI Gateway
    participant Crucix as Crucix OSINT
    participant DeerFlow as deer-flow Agents
    participant Organism as Autonomous Organism
    participant Hermes as HermesQuantOS

    User->>Dashboard: Submit Task
    Dashboard->>API: POST /api/tasks
    API->>DeerFlow: Route to Skill Engine

    alt OSINT Required
        DeerFlow->>Crucix: Request Intelligence Briefing
        Crucix->>Crucix: Aggregate 25+ Sources
        Crucix-->>DeerFlow: Structured Intel Feed
    end

    DeerFlow->>Organism: Delegate to Autonomous Agent
    Organism->>Organism: Sense - Decide - Act Loop

    alt Trading Decision Needed
        Organism->>Hermes: Market Analysis Request
        Hermes->>Hermes: 5-Layer Decision Stack
        Hermes-->>Organism: Pressure Vector + Risk Assessment
    end

    Organism-->>DeerFlow: Action Result
    DeerFlow-->>API: Task Completion
    API-->>Dashboard: WebSocket Update
    Dashboard-->>User: Real-time Notification
```

### 3. Data Pipeline — From Ingestion to Decision

```mermaid
flowchart LR
    subgraph Ingestion["Ingestion"]
        OSINT["OSINT Sources<br/>25+ APIs"]
        Market["Market Feeds<br/>Binance/Alpaca/IBKR"]
        Social["Social Signals<br/>Telegram/Discord/Reddit"]
        News["News and Research<br/>GDELT/FRED/SEC"]
    end

    subgraph Processing["Processing"]
        Normalize["Normalization<br/>Canonical Schema"]
        Enrich["Enrichment<br/>LLM Classification"]
        Validate["Validation<br/>Schema Checks"]
    end

    subgraph Storage["Storage"]
        PgDB[("PostgreSQL<br/>Persistent State")]
        Redis[("Redis<br/>Cache and Queues")]
        Vector[("Vector Store<br/>Embeddings")]
    end

    subgraph Agents["Agent Analysis"]
        Tech["Technical<br/>Sensor"]
        Sent["Sentiment<br/>Sensor"]
        Macro["Macro<br/>Sensor"]
        Liquidity["Liquidity<br/>Sensor"]
        OnChain["On-Chain<br/>Sensor"]
    end

    subgraph Decision["Decision"]
        Pressure["Pressure<br/>Normalization"]
        Guardian["Risk<br/>Guardian"]
        Output["Decision<br/>Artifact"]
    end

    OSINT --> Normalize
    Market --> Normalize
    Social --> Normalize
    News --> Normalize

    Normalize --> Enrich --> Validate

    Validate --> PgDB
    Validate --> Redis
    Validate --> Vector

    PgDB --> Tech
    PgDB --> Sent
    PgDB --> Macro
    PgDB --> Liquidity
    PgDB --> OnChain

    Vector --> Tech
    Vector --> Sent

    Tech --> Pressure
    Sent --> Pressure
    Macro --> Pressure
    Liquidity --> Pressure
    OnChain --> Pressure

    Pressure --> Guardian --> Output

    style Output fill:#15803d,stroke:#22c55e,color:#fff
    style Guardian fill:#b91c1c,stroke:#ef4444,color:#fff
    style Normalize fill:#1e40af,stroke:#3b82f6,color:#fff
```

### 4. Tech Stack — Full Layered Diagram

```mermaid
graph TB
    subgraph Client["Client Layer"]
        Browser["Browser<br/>React 19 / Next.js 16"]
        PWA["PWA<br/>Offline Support"]
        Mobile["Mobile<br/>Responsive"]
    end

    subgraph WebServer["Web Server"]
        Nginx["Nginx<br/>Reverse Proxy + SSL"]
        Static["Static Assets<br/>CSS/JS/Icons"]
    end

    subgraph AppLayer["Application Layer"]
        FastAPI["FastAPI<br/>Python 3.11+"]
        WS["WebSocket<br/>Real-time Events"]
        Workers["Background Workers<br/>Task Queue"]
    end

    subgraph AgentFW["Agent Framework"]
        Colony["Colony Manager<br/>Agent Orchestration"]
        Registry["Agent Registry<br/>Capability Discovery"]
        Memory["Memory Manager<br/>Context and Recall"]
        MCP["MCP Server<br/>Tool Protocol"]
        Skills["Skill Engine<br/>Plugin Architecture"]
    end

    subgraph LLMRouter["LLM Router"]
        Gateway["LLM Gateway<br/>Priority Fallback"]
        LLM7["LLM7<br/>Primary"]
        OpenRouter["OpenRouter<br/>Secondary"]
        OpenAI["OpenAI<br/>Tertiary"]
        Anthropic["Anthropic<br/>Quaternary"]
        CAMEL["CAMEL<br/>Quinary"]
        Local["Local Models<br/>Ollama"]
    end

    subgraph DataLayer["Data Layer"]
        Postgres[("PostgreSQL<br/>Alembic Migrations")]
        Redis[("Redis<br/>Cache and Pub/Sub")]
        Vector[("Vector DB<br/>Embeddings")]
    end

    subgraph InfraStack["Infrastructure"]
        Docker["Docker Compose<br/>Multi-Container"]
        Prometheus["Prometheus<br/>Metrics"]
        Grafana["Grafana<br/>Dashboards"]
        K8s["Kubernetes<br/>Production Orchestration"]
    end

    Browser --> Nginx
    PWA --> Nginx
    Mobile --> Nginx
    Nginx --> FastAPI
    Nginx --> Static
    FastAPI --> WS
    FastAPI --> Workers

    FastAPI --> Colony
    Colony --> Registry
    Colony --> Memory
    Colony --> MCP
    Colony --> Skills

    Skills --> Gateway
    Gateway --> LLM7
    Gateway --> OpenRouter
    Gateway --> OpenAI
    Gateway --> Anthropic
    Gateway --> CAMEL
    Gateway --> Local

    FastAPI --> Postgres
    FastAPI --> Redis
    FastAPI --> Vector

    Docker --> FastAPI
    Prometheus --> FastAPI
    Grafana --> Prometheus
    K8s --> Docker

    style Gateway fill:#7c3aed,stroke:#a855f7,color:#fff
    style Colony fill:#065f46,stroke:#10b981,color:#fff
    style FastAPI fill:#134e4a,stroke:#14b8a6,color:#fff
```

### 5. Multi-LLM Router — Provider Fallback Decision Flow

```mermaid
flowchart TD
    Request["Incoming LLM Request"] --> Router["LLM Gateway Router"]

    Router --> Check1{"LLM7<br/>Available?"}
    Check1 -->|"Yes + Free Tier"| LLM7["LLM7<br/>Priority 1<br/>GPT-3.5/4, Claude"]
    Check1 -->|"No / Rate Limited"| Check2

    Check2{"OpenRouter<br/>Available?"}
    Check2 -->|"Yes"| OpenRouter["OpenRouter<br/>Priority 2<br/>Claude, Llama-3-70B"]
    Check2 -->|"No / Rate Limited"| Check3

    Check3{"CAMEL<br/>Available?"}
    Check3 -->|"Yes"| CAMEL["CAMEL<br/>Priority 3<br/>camel-chat, camel-agent"]
    Check3 -->|"No / Rate Limited"| Check4

    Check4{"OpenAI<br/>Available?"}
    Check4 -->|"Yes"| OpenAI["OpenAI<br/>Priority 4<br/>GPT-4, GPT-4o"]
    Check4 -->|"No / Rate Limited"| Check5

    Check5{"Anthropic<br/>Available?"}
    Check5 -->|"Yes"| Anthropic["Anthropic<br/>Priority 5<br/>Claude 3.5 Sonnet"]
    Check5 -->|"No / Rate Limited"| Check6

    Check6{"Ollama Local<br/>Available?"}
    Check6 -->|"Yes"| Local["Ollama Local<br/>Priority 6<br/>Llama 3, Mistral"]
    Check6 -->|"No"| Fallback["Return Cached<br/>Response or Error"]

    LLM7 --> Response["Unified Response<br/>+ Provider Metadata"]
    OpenRouter --> Response
    CAMEL --> Response
    OpenAI --> Response
    Anthropic --> Response
    Local --> Response

    Response --> Audit["Audit Trail<br/>Provider, Latency, Tokens"]

    style Router fill:#7c3aed,stroke:#a855f7,color:#fff
    style LLM7 fill:#15803d,stroke:#22c55e,color:#fff
    style Fallback fill:#b91c1c,stroke:#ef4444,color:#fff
    style Audit fill:#1e40af,stroke:#3b82f6,color:#fff
```

---

## Maturity Assessment

> Radical transparency about what works and what doesn't.

| Component | Maturity | Test Coverage | Notes |
|-----------|----------|---------------|-------|
| FastAPI Backend (`ai_multicolony/`) | **Alpha** | Partial | Core routes exist; integration between packages is scaffolded |
| Crucix OSINT | **Beta** | Moderate | 25+ API sources working; LLM briefing engine functional |
| deer-flow | **Beta** | Moderate | Skill system works; LangGraph/CrewAI adapters present |
| autonomous-organism | **Prototype** | Minimal | Sense/Decide/Act loop scaffolded; self-evolution is aspirational |
| HermesQuantOS | **Alpha** | Moderate | 5-layer stack designed; paper trading not yet validated |
| Multi-LLM Gateway | **Beta** | Moderate | 9 providers defined; fallback chain tested for top 3 |
| Next.js Dashboard | **Alpha** | Minimal | UI shell and pages exist; real data integration in progress |
| Docker Orchestration | **Alpha** | Minimal | Compose files present; not production-hardened |

---

## Features

- **5-Package Monorepo** — Crucix (OSINT), deer-flow (Agent Platform), autonomous-organism (Self-Evolving), HermesQuantOS (Trading), Agentic-AI-System_OLD (Legacy)
- **Multi-LLM 9-Provider Router** — LLM7, OpenRouter, CAMEL, OpenAI, Anthropic, Ollama, Grok, Gemini, MiniMax with priority-based fallback
- **Colony-Based Agent Architecture** — Agents form colonies with shared memory, specialized roles, and inter-colony communication
- **FastAPI + Next.js 16** — Python backend with async WebSocket support and modern React dashboard
- **Docker Compose Orchestration** — Multi-container setup with Nginx reverse proxy
- **Skill Plugin System** — Extensible skill registry for adding new agent capabilities
- **MCP (Model Context Protocol)** — Standardized tool interface for agent-tool interaction
- **Monitoring Stack** — Prometheus metrics + Grafana dashboards

---

## Quick Start

### Prerequisites

- **Docker** and **Docker Compose**
- **Python** 3.11+
- **Node.js** 18+ (for dashboard)
- API keys for LLM providers (at least one)

### Installation

```bash
# Clone the repository

<!-- AUTO-PACKAGE-BADGES:START -->
<!-- Auto-generated package badges -->

![npm version](https://img.shields.io/npm/v/crucix?style=flat-square&logo=npm&color=blue) ![npm downloads](https://img.shields.io/npm/dw/crucix?style=flat-square&color=brightgreen) ![npm license](https://img.shields.io/npm/l/crucix?style=flat-square) [![Deployed](https://img.shields.io/badge/deployed-2.1.0-blue?style=flat-square)](https://www.npmjs.com/package/crucix)
![PyPI version](https://img.shields.io/pypi/v/quant-nanggroe-ai?style=flat-square&logo=pypi&color=green) ![PyPI downloads](https://img.shields.io/pypi/dm/quant-nanggroe-ai?style=flat-square&color=brightgreen) ![PyPI license](https://img.shields.io/pypi/l/quant-nanggroe-ai?style=flat-square) [![Deployed](https://img.shields.io/badge/deployed-0.2.0-blue?style=flat-square)](https://pypi.org/project/quant-nanggroe-ai)

<!-- AUTO-PACKAGE-BADGES:END -->
git clone https://github.com/mulkymalikuldhrs/AI-MultiColony-Ecosystem.git
cd AI-MultiColony-Ecosystem

# Copy environment template
cp .env.example .env
# Edit .env with your API keys

# Option 1: Docker Compose (recommended)
docker-compose up --build

# Option 2: Manual start
pip install -r requirements.txt
python main.py  # FastAPI backend on :8000
cd dashboard && npm install && npm run dev  # Next.js on :3000
```

### Environment Variables

```env
# LLM Providers (at least one required)
LLM7_API_KEY=           # Primary (free tier available)
OPENROUTER_API_KEY=     # Secondary
OPENAI_API_KEY=         # Tertiary
ANTHROPIC_API_KEY=      # Quaternary
CAMEL_API_KEY=          # Quinary

# Optional: Data Sources
BINANCE_API_KEY=
BINANCE_API_SECRET=

# Database
DATABASE_URL=postgresql://user:pass@localhost:5432/multicolony
REDIS_URL=redis://localhost:6379

# Infrastructure
LOG_LEVEL=info
DEBUG=false
```

---

## Project Structure

```
AI-MultiColony-Ecosystem/
├── ai_multicolony/              # Core Python backend
│   ├── api/                     # FastAPI routes (agents, colonies, tasks, tools, memory)
│   ├── browser/                 # Browser automation (stealth, human-like behavior)
│   ├── channels/                # Messaging integrations (Telegram, Discord, Slack, WhatsApp)
│   ├── integrations/            # Cross-package bridges (Crucix, Organism, Hermes)
│   ├── sources/                 # Data source managers (OSINT, market, economic)
│   └── types/                   # Shared type definitions
├── packages/
│   ├── crucix/                  # OSINT intelligence platform
│   ├── deer-flow/               # AI agent platform with skill system
│   ├── autonomous-organism/     # Self-evolving autonomous engine
│   ├── hermes-quant/            # Quantitative trading engine
│   └── agentic-legacy/          # Legacy archived system
├── connectors/                  # LLM gateway and external service connectors
├── dashboard/                   # Next.js 16 dashboard
├── database/                    # SQLAlchemy models and migrations
├── docker/                      # Docker Compose configurations
├── monitoring/                  # Prometheus + Grafana configs
├── skills/                      # Skill plugin registry
├── tests/                       # Test suites
├── docs/                        # Architecture and design docs
└── web_interface/               # Legacy Flask web interface
```

---

## Honest Notes

> We believe in radical transparency. Here are the limitations you should know.

| Claim | Reality |
|-------|---------|
| "5-Package Ecosystem" | 5 packages exist in the monorepo, but **inter-package communication is partially scaffolded**. Some bridges work; others are aspirational. |
| "Multi-LLM 9-Provider" | 9 providers are defined in the gateway. **Fallback has been tested for the top 3**; lower-priority providers may need API key validation. |
| "Autonomous Organism" | The sense/decide/act loop is **scaffolded, not production-ready**. Self-evolution is a design goal, not a current capability. |
| "Colony-Based Agents" | Colony management works for **basic task delegation**. Advanced features (inter-colony negotiation, shared learning) are in development. |
| "Docker Orchestration" | Docker Compose files exist but are **not production-hardened**. Use for development only. |
| "Next.js 16 Dashboard" | UI shell and pages exist with **mock data**. Real backend integration is ongoing. |

---

## Contributing

Contributions are welcome! We especially value contributions that improve transparency, testing, and cross-package integration.

### How to Contribute

1. **Fork** the repository
2. Create a **feature branch** (`git checkout -b feature/amazing-feature`)
3. **Commit** your changes (`git commit -m 'Add amazing feature'`)
4. **Push** to the branch (`git push origin feature/amazing-feature`)
5. Open a **Pull Request**

### Development Setup

```bash
# Install Python dependencies
pip install -r requirements.txt

# Install dashboard dependencies
cd dashboard && npm install

# Run tests
pytest tests/

# Run linting
ruff check .

# Start development environment
docker-compose -f docker-compose.dev.yml up
```

---

## Disclaimer

**FOR EDUCATION AND RESEARCH PURPOSE ONLY**

This project is provided strictly for educational and research purposes. The authors and contributors assume **no responsibility or liability** for any damages, losses, or risks arising from the use of this software.

- Trading modules are for **research only** — not financial advice
- OSINT modules must be used **responsibly and legally**
- The autonomous agent system is **not production-ready**
- Always use **test environments** before connecting to live systems

---

## Related Projects

| Project | Description |
|---------|-------------|
| [Quant-Nanggroe-AI](https://github.com/mulkymalikuldhrs/Quant-Nanggroe-AI) | Multi-Agent Decision Intelligence OS for Quantitative Trading |
| [HermesQuantOS](https://github.com/mulkymalikuldhrs/HermesQuantOS) | Unified Trading Intelligence Platform |
| [ProxyGateLLM](https://github.com/mulkymalikuldhrs/ProxyGateLLM) | Multi-LLM Gateway with Priority Fallback |
| [Agentic-AI-System_OLD](https://github.com/mulkymalikuldhrs/Agentic-AI-System_OLD) | Legacy Multi-Agent System (Archived) |

## License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.

---

## Author

**Mulky Malikul Dhaher**

[![GitHub](https://img.shields.io/badge/GitHub-mulkymalikuldhrs-181717?style=for-the-badge&logo=github)](https://github.com/mulkymalikuldhrs)
[![Email](https://img.shields.io/badge/Email-mulkymalikudhr%40mail.com-EA4335?style=for-the-badge&logo=gmail&logoColor=white)](mailto:mulkymalikudhr@mail.com)

---

<a href="https://github.com/mulkymalikuldhrs/AI-MultiColony-Ecosystem">
  <img width="100%" src="https://capsule-render.vercel.app/api?type=waving&color=0:2d1b69,50:1a1a3e,100:0a0a1a&height=100&section=footer" />
</a>

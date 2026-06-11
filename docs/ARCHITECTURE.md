# AI MultiColony Ecosystem — Architecture Document

> Unified Multi-Colony AI Platform v3.0.0
> Author: Mulky Malikul Dhaher | Indonesia

---

## Table of Contents

1. [Monorepo Structure](#1-monorepo-structure)
2. [Package Communication](#2-package-communication)
3. [Data Flow Between Services](#3-data-flow-between-services)
4. [Database Schema Overview](#4-database-schema-overview)
5. [API Gateway Design](#5-api-gateway-design)
6. [Technology Stack](#6-technology-stack)

---

## 1. Monorepo Structure

The AI MultiColony Ecosystem is organized as a monorepo with npm workspaces, bringing together 5 previously independent repositories under a single codebase. This enables shared dependencies, unified builds, and cross-package coordination.

### Directory Layout

```
AI-MultiColony-Ecosystem/                  # Root monorepo
│
├── package.json                            # npm workspaces orchestrator (v3.0.0)
├── docker-compose.yml                      # 7-service Docker orchestration
├── Makefile                                # Unified build/dev/test commands
├── .env.example                            # Consolidated environment variables
├── pyproject.toml                          # Python package configuration
├── requirements.txt                        # Python production dependencies
│
├── ai_multicolony/                         # Core Python package (FastAPI backend)
│   ├── agents/                             # 9 specialized agent types
│   │   ├── coder/                          # Code generation & review
│   │   ├── manus/                          # General-purpose assistant
│   │   ├── planner/                        # Task decomposition
│   │   ├── executor/                       # Action execution
│   │   ├── browser/                        # Web automation
│   │   ├── voice/                          # Speech I/O
│   │   ├── security/                       # Security analysis
│   │   ├── researcher/                     # Information gathering
│   │   └── colony/                         # Colony-level orchestration
│   ├── api/                                # FastAPI routes + WebSocket
│   ├── browser/                            # Stealth browser (Playwright)
│   ├── channels/                           # 5 channel integrations
│   │   ├── telegram.py                     # Telegram Bot API
│   │   ├── discord.py                      # Discord.js bridge
│   │   ├── slack.py                        # Slack Bolt
│   │   ├── whatsapp.py                     # WhatsApp Web
│   │   └── base.py                         # Channel abstraction
│   ├── colony/                             # Colony coordination
│   │   ├── coordinator.py                  # Task routing
│   │   ├── scheduler.py                    # Cron + event scheduling
│   │   ├── manager.py                      # Colony lifecycle
│   │   └── hands.py                        # Agent handoff protocol
│   ├── core/                               # Core framework
│   │   ├── base_agent.py                   # Agent base class
│   │   ├── agent_loop.py                   # Agent execution loop
│   │   ├── event_bus.py                    # Pub/sub event system
│   │   ├── tool_registry.py                # Tool discovery & execution
│   │   ├── llm_provider.py                 # Multi-LLM gateway
│   │   ├── memory_manager.py               # Memory orchestration
│   │   ├── tool_base.py                    # Tool abstract class
│   │   └── channel.py                      # Channel base class
│   ├── mcp/                                # Model Context Protocol
│   ├── memory/                             # Multi-layer memory
│   │   ├── vector.py                       # Vector store (Chroma/Qdrant)
│   │   ├── session.py                      # Session memory
│   │   ├── paging.py                       # Context window management
│   │   ├── condenser.py                    # Memory summarization
│   │   └── knowledge.py                    # Knowledge base
│   ├── sandbox/                            # Code execution
│   ├── security/                           # Security analysis
│   ├── tools/                              # 10 tool implementations
│   └── types/                              # Pydantic type definitions
│
├── dashboard/                              # Unified Next.js 16 Dashboard
│   ├── src/
│   │   ├── app/                            # App Router pages
│   │   │   ├── page.tsx                    # Home / overview
│   │   │   ├── agents/page.tsx             # Agent management
│   │   │   ├── colony/page.tsx             # Colony status
│   │   │   ├── memory/page.tsx             # Memory inspector
│   │   │   ├── channels/page.tsx           # Channel status
│   │   │   ├── tools/page.tsx              # Tool registry
│   │   │   ├── security/page.tsx           # Security dashboard
│   │   │   └── settings/page.tsx           # Configuration
│   │   ├── components/                     # Shared UI components
│   │   └── lib/                            # API client + utilities
│   └── package.json                        # Next.js 16 + Zustand
│
├── packages/
│   ├── crucix/                             # OSINT Intelligence Platform
│   │   ├── server.mjs                      # Express 5 server
│   │   ├── apis/sources/                   # 29 OSINT source modules
│   │   ├── apis/briefing.mjs               # LLM-powered briefing engine
│   │   ├── lib/llm/                        # 9 LLM provider adapters
│   │   ├── lib/alerts/                     # Telegram + Discord alerts
│   │   ├── lib/delta/                      # Change detection engine
│   │   ├── dashboard/                      # Static intelligence dashboard
│   │   ├── Dockerfile                      # Container build
│   │   └── package.json                    # Express 5 + Node 22
│   │
│   ├── deer-flow/                          # AI Agent Platform
│   │   ├── frontend/                       # Next.js 16 + React 19
│   │   │   ├── src/app/                    # App Router pages
│   │   │   ├── src/components/             # Agent UI, chat, workflow editor
│   │   │   └── package.json                # pnpm workspace
│   │   └── backend/                        # Python FastAPI
│   │       ├── app/gateway/                # API gateway + auth
│   │       ├── app/channels/               # 8 channel integrations
│   │       ├── packages/harness/           # LangGraph + agent harness
│   │       ├── Dockerfile                  # Multi-stage build
│   │       └── langgraph.json              # LangGraph configuration
│   │
│   ├── autonomous-organism/                # Autonomous Organism Engine
│   │   ├── src/                            # React 18 + Vite
│   │   │   ├── components/                 # Organism UI components
│   │   │   ├── hooks/                      # Real-time organism hooks
│   │   │   ├── pages/                      # Login, Index, NotFound
│   │   │   └── integrations/               # Supabase client
│   │   ├── supabase/                       # Edge functions + migrations
│   │   │   ├── functions/                  # ingest-sense, run-decision,
│   │   │   │                               # run-factory, run-growth, bootstrap
│   │   │   └── migrations/                 # Database migrations
│   │   ├── sense/                          # Sensory input processing
│   │   ├── decision/                       # Decision engine
│   │   ├── factory/                        # Organism factory
│   │   ├── memory/                         # Memory subsystem
│   │   ├── scheduler/                      # Task scheduling
│   │   ├── immune/                         # Immune system
│   │   └── package.json                    # React 18 + Vite
│   │
│   ├── hermes-quant/                       # Quantitative Trading Bot
│   │   ├── src/
│   │   │   ├── hermes_quant.py             # Main entry point
│   │   │   ├── watchdog.py                 # Process watchdog
│   │   │   └── tools/                      # 21 agent tools
│   │   │       ├── technical_analysis_tool.py
│   │   │       ├── risk_officer_tool.py
│   │   │       ├── kill_switch_tool.py
│   │   │       ├── portfolio_tool.py
│   │   │       ├── market_data_tool.py
│   │   │       ├── chart_vision_tool.py
│   │   │       ├── news_sentinel.py
│   │   │       ├── backtest_engine.py
│   │   │       ├── smc_agent_enhanced.py
│   │   │       ├── strategy_lifecycle.py
│   │   │       ├── decision_engine.py
│   │   │       ├── execution_tool.py
│   │   │       ├── autoswitch_engine.py
│   │   │       ├── pressure_engine.py
│   │   │       ├── market_state_engine.py
│   │   │       ├── math_engine.py
│   │   │       ├── macro_sentiment_tool.py
│   │   │       ├── auditor_research_tool.py
│   │   │       ├── audit_logger.py
│   │   │       ├── strategy_tool.py
│   │   │       └── journal_tool.py
│   │   ├── config/                         # System prompt + YAML config
│   │   ├── schemas/                        # Trading journal SQL
│   │   └── requirements.txt                # Python dependencies
│   │
│   └── agentic-legacy/                     # Legacy AI System (reference only)
│       ├── src/                            # Original agent framework
│       ├── web_interface/                  # Flask templates
│       └── requirements.txt                # Python dependencies
│
├── scripts/
│   ├── setup.sh                            # Full environment setup
│   ├── test-all.sh                         # Cross-package test runner
│   ├── setup_dev.sh                        # Legacy dev setup
│   └── entrypoint.sh                       # Docker entrypoint
│
├── docs/                                   # Documentation
│   ├── ARCHITECTURE.md                     # This document
│   ├── AGENT_ARCHITECTURE.md               # Agent system details
│   ├── MEMORY_ARCHITECTURE.md              # Memory system details
│   ├── TOOL_REGISTRY.md                    # Tool documentation
│   ├── SKILL_REGISTRY.md                   # Skill documentation
│   ├── ROADMAP.md                          # Development roadmap
│   └── DECISION_LOG.md                     # Architecture decisions
│
├── config/                                 # Shared configuration
│   ├── system_config.yaml                  # System configuration
│   └── prompts.yaml                        # Prompt templates
│
├── monitoring/                             # Observability stack
│   ├── prometheus.yml                      # Prometheus config
│   └── grafana/                            # Grafana dashboards
│
├── nginx/                                  # Reverse proxy config
│   └── nginx.conf                          # Production nginx config
│
├── database/                               # Database management
│   ├── models.py                           # SQLAlchemy models
│   ├── migrations.py                       # Migration runner
│   ├── init_db.py                          # Database initialization
│   └── init.sql                            # SQL initialization
│
└── tests/                                  # Python test suite
    ├── test_core/                          # Core system tests
    ├── test_agents/                        # Agent tests
    ├── test_mcp/                           # MCP protocol tests
    ├── test_memory/                        # Memory system tests
    ├── test_channels/                      # Channel integration tests
    ├── test_browser/                       # Browser automation tests
    ├── test_sandbox/                       # Sandbox execution tests
    ├── test_security/                      # Security tests
    ├── test_tools/                         # Tool tests
    └── test_api/                           # API endpoint tests
```

### npm Workspaces Configuration

The root `package.json` defines npm workspaces that manage JavaScript/TypeScript dependencies across packages:

```json
{
  "workspaces": [
    "dashboard",
    "packages/crucix",
    "packages/deer-flow/frontend",
    "packages/autonomous-organism"
  ]
}
```

- **Deer Flow Frontend** uses `pnpm` with its own `pnpm-workspace.yaml` — it is included in the npm workspaces for discovery but installs separately.
- **Hermes Quant** and **Agentic Legacy** are Python-only packages — not included in npm workspaces.
- **Crucix** uses Express 5 with native ES modules (`"type": "module"`).

---

## 2. Package Communication

### Communication Topology

```
                    ┌─────────────────────────────────────┐
                    │          Nginx (port 80)             │
                    │     TLS termination + routing        │
                    └──────┬──────────┬──────────┬────────┘
                           │          │          │
              ┌────────────▼──┐  ┌────▼──────┐  ┌▼──────────────┐
              │  Dashboard    │  │  Crucix   │  │  Deer Flow FE  │
              │  :3000        │  │  :3117    │  │  (standalone)  │
              └──────┬────────┘  └────┬──────┘  └──────┬─────────┘
                     │                │                 │
                     │   HTTP/REST    │  HTTP/REST      │ HTTP/REST
                     │                │                 │
              ┌──────▼────────────────▼─────────────────▼─────────┐
              │              FastAPI Gateway (:8000)               │
              │                                                    │
              │  ┌──────────────┐  ┌──────────────┐               │
              │  │ Colony       │  │ Agent        │               │
              │  │ Coordinator  │──│ Registry     │               │
              │  └──────┬───────┘  └──────┬───────┘               │
              │         │                 │                        │
              │  ┌──────▼───────┐  ┌──────▼───────┐               │
              │  │ LLM Gateway  │  │ Tool Registry │               │
              │  │ (9 providers)│  │ (10 tools)    │               │
              │  └──────────────┘  └──────────────┘               │
              └──────────┬──────────────────────────────────────────┘
                         │
           ┌─────────────┼─────────────┐
           │             │             │
    ┌──────▼──────┐ ┌────▼──────┐ ┌───▼────────────┐
    │ PostgreSQL  │ │  Redis 7  │ │ Hermes Quant   │
    │ :5432       │ │  :6379    │ │ (no HTTP port) │
    │             │ │           │ │                 │
    │ - agents    │ │ - cache   │ │ Python process  │
    │ - tasks     │ │ - pub/sub │ │ Telegram bot    │
    │ - memory    │ │ - sessions│ │ 21 agent tools  │
    │ - colonies  │ │ - queues  │ │                 │
    └─────────────┘ └───────────┘ └─────────────────┘
           │
    ┌──────▼──────────────┐
    │ Autonomous Organism │
    │ Supabase (managed)  │
    │                     │
    │ - organisms table   │
    │ - sense_data        │
    │ - decisions         │
    │ - edge functions    │
    └─────────────────────┘
```

### Communication Protocols

| From | To | Protocol | Purpose |
|------|----|----------|---------|
| Dashboard | FastAPI | HTTP/REST | Agent management, task dispatch |
| Dashboard | FastAPI | WebSocket | Real-time event streaming |
| Dashboard | Crucix | HTTP/REST | OSINT data, briefings |
| Crucix | FastAPI | HTTP/REST (optional) | Shared LLM gateway |
| Deer Flow FE | Deer Flow BE | HTTP/REST | Agent runs, threads, skills |
| Deer Flow BE | FastAPI | HTTP/REST (internal) | Colony coordination |
| Hermes Quant | Redis | Redis Protocol | Cache, state sharing |
| Hermes Quant | Telegram | HTTPS | User interaction |
| FastAPI | PostgreSQL | PostgreSQL Wire | Persistent data |
| FastAPI | Redis | Redis Protocol | Caching, sessions, pub/sub |
| FastAPI | Qdrant/Chroma | HTTP/gRPC | Vector similarity search |
| Nginx | All services | HTTP proxy | Routing + TLS |

### Inter-Service Event Bus

The Redis pub/sub system serves as the cross-service event bus:

```
Channel: colony:events       → Colony lifecycle events (agent spawn, task complete)
Channel: crucix:alerts       → OSINT alerts forwarded to colony coordinator
Channel: hermes:trades       → Trade execution events for audit/monitoring
Channel: organism:evolution  → Organism state changes for dashboard display
Channel: system:health       → Health check broadcasts from all services
```

---

## 3. Data Flow Between Services

### Request Flow: User Task Dispatch

```
 1. User submits task via Dashboard (Next.js)
    │
 2. Dashboard → POST /api/colony/dispatch → FastAPI Gateway
    │
 3. Colony Coordinator receives task
    │
 4. AI Selector scores agents based on:
    │   - Capability match (50%)
    │   - Specialization (40%)
    │   - Performance history (30%)
    │   - Load balance (20%)
    │   - Base priority (10%)
    │
 5. Selected Agent executes via AgentLoop
    │
 6. Agent calls LLM Gateway (with failover chain):
    │   LLM7 → OpenRouter → DeepSeek → OpenAI → Anthropic → Google AI
    │
 7. Agent invokes Tools via ToolRegistry
    │   - Shell execution (sandboxed)
    │   - File operations
    │   - Browser automation
    │   - Code execution
    │   - Memory storage/retrieval
    │
 8. Results stored in:
    │   - PostgreSQL (persistent task results, agent state)
    │   - Redis (session cache, real-time data)
    │   - Vector Store (embeddings for semantic search)
    │
 9. Event published to Redis pub/sub
    │
10. Dashboard receives event via WebSocket
    │
11. User sees result in real-time
```

### Data Flow: Crucix OSINT Intelligence

```
 1. Cron triggers intelligence sweep
    │
 2. Crucix fetches from 29 OSINT sources:
    │   - Geopolitical: ACLED, GDELT, ReliefWeb, OpenSanctions, OFAC
    │   - Economic: BLS, FRED, Treasury, Comtrade, EIA
    │   - Environmental: FIRMS, NOAA, Safecast, EPA
    │   - Cyber: CISA KEV
    │   - Infrastructure: Ships, ADS-B, OpenSky, Space Track
    │   - Social: Reddit, Bluesky, Telegram
    │   - Health: WHO
    │   - Innovation: Patents
    │   - Financial: yfinance, GSCPI
    │
 3. Delta Engine detects changes from previous sweep
    │
 4. Data pushed to Dashboard (static HTML injection)
    │
 5. (Optional) LLM synthesizes briefing from collected data
    │
 6. Alerts dispatched via Telegram / Discord
    │
 7. Briefing saved for historical reference
```

### Data Flow: Hermes Quant Trading

```
 1. Hermes main loop starts (Python process)
    │
 2. Market Data Tool fetches real-time data (yfinance)
    │
 3. Technical Analysis Tool computes indicators
    │
 4. Market State Engine classifies market regime
    │
 5. Decision Engine evaluates entry/exit signals
    │
 6. Risk Officer Tool validates trade parameters
    │
 7. Kill Switch Tool monitors for emergency stops
    │
 8. Execution Tool places order (if enabled)
    │
 9. Audit Logger records all decisions
    │
10. Journal Tool maintains trading diary
    │
11. Telegram bot sends trade notifications
    │
12. Strategy Lifecycle manages strategy rotation
    │
13. Autoswitch Engine adapts to market conditions
```

### Data Flow: Autonomous Organism

```
 1. Sense subsystem ingests environmental data
    │
 2. Supabase Edge Function: ingest-sense
    │
 3. Memory subsystem stores sensory input
    │
 4. Decision subsystem evaluates actions
    │
 5. Supabase Edge Function: run-decision
    │
 6. Factory subsystem creates new components
    │
 7. Supabase Edge Function: run-factory
    │
 8. Growth subsystem evolves organism
    │
 9. Supabase Edge Function: run-growth
    │
10. Immune subsystem defends against threats
    │
11. Bootstrap initializes new organisms
    │
12. Supabase Edge Function: bootstrap
    │
13. React frontend displays organism state in real-time
```

---

## 4. Database Schema Overview

### PostgreSQL (Primary Database)

The PostgreSQL database serves as the shared persistent store for the FastAPI gateway, colony coordination, and agent state.

```sql
-- === Core Tables ===

-- Agents registered in the colony
CREATE TABLE agents (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name            VARCHAR(100) NOT NULL UNIQUE,
    type            VARCHAR(50) NOT NULL,          -- manus, coder, planner, executor, etc.
    status          VARCHAR(20) DEFAULT 'idle',     -- idle, running, error, stopped
    capabilities    JSONB DEFAULT '[]',
    config          JSONB DEFAULT '{}',
    priority        INTEGER DEFAULT 5,
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    updated_at      TIMESTAMPTZ DEFAULT NOW(),
    last_heartbeat  TIMESTAMPTZ
);

-- Colonies (groups of agents)
CREATE TABLE colonies (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name            VARCHAR(100) NOT NULL UNIQUE,
    description     TEXT,
    strategy        VARCHAR(50) DEFAULT 'round-robin',  -- round-robin, least-loaded, capability
    agent_ids       UUID[] DEFAULT '{}',
    status          VARCHAR(20) DEFAULT 'active',
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

-- Tasks dispatched to agents
CREATE TABLE tasks (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    agent_id        UUID REFERENCES agents(id),
    colony_id       UUID REFERENCES colonies(id),
    parent_task_id  UUID REFERENCES tasks(id),
    type            VARCHAR(50) NOT NULL,
    input           JSONB DEFAULT '{}',
    output          JSONB,
    status          VARCHAR(20) DEFAULT 'pending',  -- pending, running, completed, failed
    priority        INTEGER DEFAULT 5,
    error           TEXT,
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    started_at      TIMESTAMPTZ,
    completed_at    TIMESTAMPTZ,
    tokens_used     INTEGER DEFAULT 0,
    llm_provider    VARCHAR(50),
    llm_model       VARCHAR(100)
);

-- === Memory System ===

-- Session memory (short-term, per conversation)
CREATE TABLE memory_sessions (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_key     VARCHAR(255) NOT NULL UNIQUE,
    agent_id        UUID REFERENCES agents(id),
    context         JSONB DEFAULT '{}',
    summary         TEXT,
    token_count     INTEGER DEFAULT 0,
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    expires_at      TIMESTAMPTZ,
    updated_at      TIMESTAMPTZ DEFAULT NOW()
);

-- Episodic memory (task history)
CREATE TABLE memory_episodes (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    agent_id        UUID REFERENCES agents(id),
    task_id         UUID REFERENCES tasks(id),
    event_type      VARCHAR(50) NOT NULL,
    content         JSONB NOT NULL,
    embedding_id    VARCHAR(255),               -- Reference to vector store
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

-- Knowledge base (semantic memory)
CREATE TABLE knowledge_entries (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    domain          VARCHAR(100) NOT NULL,
    topic           VARCHAR(255) NOT NULL,
    content         TEXT NOT NULL,
    source          VARCHAR(100),                -- agent, user, external
    confidence      FLOAT DEFAULT 1.0,
    embedding_id    VARCHAR(255),
    tags            VARCHAR(100)[],
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    updated_at      TIMESTAMPTZ DEFAULT NOW()
);

-- === Security ===

-- Encrypted credentials vault
CREATE TABLE credentials (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name            VARCHAR(255) NOT NULL UNIQUE,
    encrypted_value BYTEA NOT NULL,               -- AES-256 encrypted
    category        VARCHAR(50),                   -- api_key, token, password, secret
    salt            BYTEA NOT NULL,
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    updated_at      TIMESTAMPTZ DEFAULT NOW(),
    accessed_at     TIMESTAMPTZ
);

-- Audit log
CREATE TABLE audit_log (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    actor           VARCHAR(100) NOT NULL,         -- agent_id or user_id
    action          VARCHAR(100) NOT NULL,
    resource_type   VARCHAR(50),
    resource_id     VARCHAR(255),
    details         JSONB DEFAULT '{}',
    ip_address      INET,
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

-- === Channels ===

-- Channel configurations
CREATE TABLE channels (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    type            VARCHAR(50) NOT NULL,          -- telegram, discord, slack, whatsapp
    name            VARCHAR(100) NOT NULL,
    config          JSONB DEFAULT '{}',             -- Channel-specific config (encrypted)
    status          VARCHAR(20) DEFAULT 'disconnected',
    last_message_at TIMESTAMPTZ,
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

-- === Tools ===

-- Registered tools
CREATE TABLE tools (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name            VARCHAR(100) NOT NULL UNIQUE,
    description     TEXT,
    input_schema    JSONB DEFAULT '{}',
    output_schema   JSONB DEFAULT '{}',
    capabilities    JSONB DEFAULT '[]',
    is_active       BOOLEAN DEFAULT TRUE,
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

-- === Indexes ===
CREATE INDEX idx_tasks_agent_id ON tasks(agent_id);
CREATE INDEX idx_tasks_status ON tasks(status);
CREATE INDEX idx_tasks_created_at ON tasks(created_at);
CREATE INDEX idx_memory_sessions_key ON memory_sessions(session_key);
CREATE INDEX idx_memory_episodes_agent ON memory_episodes(agent_id);
CREATE INDEX idx_knowledge_domain ON knowledge_entries(domain);
CREATE INDEX idx_audit_log_actor ON audit_log(actor);
CREATE INDEX idx_audit_log_created ON audit_log(created_at);
```

### Redis Key Schema

```
# Sessions
session:{session_id}               → JSON (agent context, conversation state)
                                    TTL: 3600s

# Agent State
agent:{agent_id}:state             → JSON (status, current task, metrics)
agent:{agent_id}:heartbeat         → TIMESTAMP
                                    TTL: 60s (auto-expire on failure)

# Colony State
colony:{colony_id}:agents          → SET of agent_ids
colony:{colony_id}:queue           → LIST of pending task_ids

# LLM Cache
llm:cache:{hash(prompt)}           → JSON (cached LLM response)
                                    TTL: 3600s

# Rate Limiting
ratelimit:{ip_address}             → COUNTER
                                    TTL: 60s

# Event Bus (pub/sub channels)
colony:events                      → PUBSUB
crucix:alerts                      → PUBSUB
hermes:trades                      → PUBSUB
organism:evolution                 → PUBSUB
system:health                      → PUBSUB

# Hermes Quant State
hermes:portfolio                   → JSON (current positions)
hermes:strategy                    → STRING (active strategy name)
hermes:pressure                    → FLOAT (market pressure score)
```

### Vector Store (Qdrant/ChromaDB)

```json
{
  "collection": "ai_multicolony_embeddings",
  "vectors": {
    "size": 1536,
    "distance": "cosine"
  },
  "payload_schema": {
    "agent_id": "keyword",
    "memory_type": "keyword",      // episodic, knowledge, session
    "domain": "keyword",
    "timestamp": "datetime",
    "content_summary": "text"
  }
}
```

---

## 5. API Gateway Design

### FastAPI Gateway Architecture

The FastAPI gateway at port 8000 is the central API entry point for the entire ecosystem. It provides unified access to agent management, colony coordination, memory, tools, LLM providers, and credentials.

```
                    ┌──────────────────────────────────────┐
                    │         FastAPI Gateway (:8000)       │
                    │                                       │
  Incoming  ──────► │  ┌─────────────────────────────┐     │
  Requests          │  │      Middleware Stack         │     │
                    │  │  ┌────────┐ ┌────────────┐  │     │
                    │  │  │  CORS  │ │ Rate Limit  │  │     │
                    │  │  └────────┘ └────────────┘  │     │
                    │  │  ┌────────┐ ┌────────────┐  │     │
                    │  │  │  Auth  │ │  Logging   │  │     │
                    │  │  └────────┘ └────────────┘  │     │
                    │  │  ┌────────┐ ┌────────────┐  │     │
                    │  │  │ Error  │ │  Request   │  │     │
                    │  │  │ Handler│ │  Tracing    │  │     │
                    │  │  └────────┘ └────────────┘  │     │
                    │  └──────────────┬──────────────┘     │
                    │                 │                     │
                    │  ┌──────────────▼──────────────┐     │
                    │  │        Router Layer           │     │
                    │  │                               │     │
                    │  │  /api/agents/*    Agents      │     │
                    │  │  /api/colony/*    Colony      │     │
                    │  │  /api/memory/*    Memory      │     │
                    │  │  /api/tools/*     Tools       │     │
                    │  │  /api/llm/*       LLM         │     │
                    │  │  /api/credentials Security    │     │
                    │  │  /api/code/*      Sandbox     │     │
                    │  │  /ws/events       WebSocket   │     │
                    │  └──────────────┬──────────────┘     │
                    │                 │                     │
                    │  ┌──────────────▼──────────────┐     │
                    │  │       Service Layer           │     │
                    │  │                               │     │
                    │  │  ColonyCoordinator            │     │
                    │  │  AgentRegistry                │     │
                    │  │  ToolRegistry                 │     │
                    │  │  LLMProvider (failover)       │     │
                    │  │  MemoryManager                │     │
                    │  │  CredentialManager            │     │
                    │  └──────────────┬──────────────┘     │
                    │                 │                     │
                    │  ┌──────────────▼──────────────┐     │
                    │  │       Data Layer              │     │
                    │  │                               │     │
                    │  │  PostgreSQL   Redis   Qdrant  │     │
                    │  └──────────────────────────────┘     │
                    └──────────────────────────────────────┘
```

### LLM Gateway Failover Chain

```
Request → LLM7 (free tier)
           ↓ (if failed)
         OpenRouter
           ↓ (if failed)
         DeepSeek
           ↓ (if failed)
         OpenAI
           ↓ (if failed)
         Anthropic
           ↓ (if failed)
         Google AI
           ↓ (if failed)
         Groq
           ↓ (if failed)
         Hugging Face
           ↓ (if failed)
         Ollama (local fallback)
           ↓ (if all failed)
         Return error with provider status report
```

### Deer Flow Gateway (port 8001)

The Deer Flow backend has its own FastAPI gateway with a focus on LangGraph-based agent orchestration:

```
/api/threads          → Conversation thread management
/api/threads/{id}/runs → Agent execution within threads
/api/models           → Available model listing
/api/auth/*           → JWT-based authentication
/api/skills           → Skill registry
/api/mcp/*            → Model Context Protocol tools
/api/channels/*       → Multi-channel message routing
/api/artifacts/*      → Generated artifact management
/api/feedback/*       → User feedback collection
```

### Nginx Routing Rules

```
/              → Web Dashboard (port 3000)
/api/*         → FastAPI Gateway (port 8000)
/osint/*       → Crucix OSINT (port 3117)
/deer-flow/*   → Deer Flow Frontend (served by its own Next.js)
/socket.io/*   → WebSocket upgrade → FastAPI
/health        → API health check
/metrics       → Prometheus metrics (internal only)
```

---

## 6. Technology Stack

### Full Stack Overview

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **Reverse Proxy** | Nginx 1.27 | TLS, routing, rate limiting, static caching |
| **Frontend (Dashboard)** | Next.js 16 + React 19 + Tailwind CSS 4 | Unified management UI |
| **Frontend (Deer Flow)** | Next.js 16 + React 19 + pnpm | Agent chat interface |
| **Frontend (Organism)** | React 18 + Vite + Supabase | Organism visualization |
| **API Gateway** | FastAPI + Uvicorn | Central API entry point |
| **Agent Backend** | Python 3.11+ + LangGraph | Multi-agent orchestration |
| **OSINT Service** | Node.js 22 + Express 5 | Intelligence gathering |
| **Trading Bot** | Python 3.11+ | Quantitative trading |
| **Primary Database** | PostgreSQL 16 | Persistent storage |
| **Cache / Message Bus** | Redis 7 | Caching, sessions, pub/sub |
| **Vector Store** | Qdrant / ChromaDB | Semantic search |
| **Edge Functions** | Supabase | Organism computation |
| **Containerization** | Docker + Docker Compose | Service orchestration |
| **Monitoring** | Prometheus + Grafana | Observability |
| **CI/CD** | GitHub Actions | Automated testing + deployment |

### Language Distribution

| Language | Percentage | Primary Use |
|----------|-----------|-------------|
| Python | ~55% | Backend, agents, trading, ML |
| TypeScript/JavaScript | ~35% | Frontend, OSINT service |
| SQL | ~5% | Database schemas |
| YAML/Config | ~5% | Docker, CI/CD, Nginx |

### Key Dependencies

**Python (Backend)**:
- `fastapi` — API framework
- `uvicorn` — ASGI server
- `litellm` — Multi-LLM abstraction
- `pydantic` — Data validation
- `redis` — Cache + pub/sub
- `qdrant-client` / `chromadb` — Vector search
- `playwright` — Browser automation
- `sqlalchemy` — ORM
- `celery` — Async task queue

**Node.js (Frontend + OSINT)**:
- `next` 16 — React framework
- `express` 5 — OSINT API server
- `react` 18/19 — UI rendering
- `tailwindcss` 4 — Styling
- `@langchain/langgraph-sdk` — Agent client
- `@radix-ui/*` — UI primitives
- `zustand` — State management
- `recharts` — Data visualization

---

*This architecture document is maintained as part of the AI-MultiColony-Ecosystem project. Last updated: 2026-03-05.*

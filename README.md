<a href="https://github.com/mulkymalikuldhrs/Quant-Nanggroe-AI">
  <img width="100%" src="https://capsule-render.vercel.app/api?type=waving&color=0:001a0a,50:003d1a,100:005c2a&height=220&section=header&text=Quant%20Nanggroe%20AI&fontSize=42&fontColor=00D4AA&animation=fadeIn&fontAlignY=30&desc=Multi-Agent%20Decision%20Intelligence%20OS%20for%20Quantitative%20Trading&descSize=16&descColor=fbbf24&descAlignY=50" />
</a>

<div align="center">

[![Typing SVG](https://readme-typing-svg.demolab.com?font=Fira+Code&size=22&duration=3000&pause=1000&color=00D4AA&center=true&vCenter=true&width=720&lines=Multi-Agent+Decision+Intelligence+OS;5-Layer+Deterministic+Execution+Stack;Darwinian+Strategy+Lifecycle;Risk+Guardian+Constitution;Decision-Support+%E2%80%94+Not+Guaranteed+Profit)](https://git.io/typing-svg)

<br/>

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://github.com/mulkymalikuldhrs/Quant-Nanggroe-AI)
[![LangGraph](https://img.shields.io/badge/LangGraph-0.2+-00D4AA?style=for-the-badge&logo=ai&logoColor=white)](https://github.com/mulkymalikuldhrs/Quant-Nanggroe-AI)
[![Binance](https://img.shields.io/badge/Binance-API-F0B90B?style=for-the-badge&logo=binance&logoColor=white)](https://github.com/mulkymalikuldhrs/Quant-Nanggroe-AI)
[![Multi-Agent](https://img.shields.io/badge/Multi-Agent-5_Layers-00D4AA?style=for-the-badge&logo=ai&logoColor=white)](https://github.com/mulkymalikuldhrs/Quant-Nanggroe-AI)
[![Version](https://img.shields.io/badge/Version-v0.2.0-005c2a?style=for-the-badge&logo=semanticrelease&logoColor=white)](https://github.com/mulkymalikuldhrs/AI-MultiColony-Ecosystem)
[![License](https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge&logo=opensourceinitiative&logoColor=white)](LICENSE)

<br/>

[![GitHub Stars](https://img.shields.io/github/stars/mulkymalikuldhrs/Quant-Nanggroe-AI?style=for-the-badge&logo=github&color=gold)](https://github.com/mulkymalikuldhrs/Quant-Nanggroe-AI/stargazers)
[![GitHub Forks](https://img.shields.io/github/forks/mulkymalikuldhrs/Quant-Nanggroe-AI?style=for-the-badge&logo=github&color=blue)](https://github.com/mulkymalikuldhrs/Quant-Nanggroe-AI/fork)
[![GitHub Issues](https://img.shields.io/github/issues/mulkymalikuldhrs/Quant-Nanggroe-AI?style=for-the-badge&logo=github&color=red)](https://github.com/mulkymalikuldhrs/Quant-Nanggroe-AI/issues)

<br/>

**Language / Bahasa / 语言**

[![EN](https://img.shields.io/badge/EN-English-blue?style=flat-square)](README.md)
[![ID](https://img.shields.io/badge/ID-Bahasa%20Indonesia-red?style=flat-square)](README_id.md)
[![CN](https://img.shields.io/badge/CN-中文-green?style=flat-square)](README_zh.md)

</div>

---

<a href="https://www.producthunt.com/products/quant-nanggroe-ai?embed=true&amp;utm_source=badge-featured&amp;utm_medium=badge&amp;utm_campaign=badge-quant-nanggroe-ai" target="_blank" rel="noopener noreferrer"><img alt="Quant Nanggroe AI - trading, quantitative, stocks, ai, ai agent, swarm | Product Hunt" width="250" height="54" src="https://api.producthunt.com/widgets/embed-image/v1/featured.svg?post_id=1169196&amp;theme=dark&amp;t=1781170069213"></a>

## Overview

Quant Nanggroe AI is a **Multi-Agent Decision Intelligence Operating System** for quantitative research and systematic trading in financial markets. It is part of the [HermesQuantOS](https://github.com/mulkymalikuldhrs/HermesQuantOS) unified project ecosystem.

Built on the principle of **Deterministic Decision Intelligence**, the platform treats LLMs as Logical Reasoning Engines operating under strict contracts that forbid subjective opinions, mandate data grounding, and require pressure-based numerical outputs rather than direct trade signals.

The system implements a **5-Layer Execution Stack** that processes market data from raw L1/L2 feeds through regime detection, multi-agent sensor analysis, pressure normalization, and decision synthesis with risk enforcement. It features a **Darwinian Strategy Lifecycle** that automatically retires underperforming strategies and a **Risk Guardian Constitution** as an independent layer of hard-coded safety rules.

> **Honest Note**: This is a **decision-support and research tool**, not an autonomous trading system that guarantees profits. "Deterministic Decision Intelligence" means the data flow pipeline is deterministic — **not** that its outputs are guaranteed correct. All trading involves risk of loss. The Risk Guardian reduces but cannot eliminate risk.

---

## 5-Layer Execution Stack

The core of Quant Nanggroe AI is its layered execution architecture. Each layer has a single responsibility and strict data contracts with the layers above and below it. This is what makes the pipeline **deterministic** — the same inputs always follow the same processing path, producing auditable, traceable decision artifacts.

```
┌─────────────────────────────────────────────────────────┐
│                    LAYER 4 — DECISION                   │
│              Decision Synthesis & Risk Enforcement       │
│         Final pressure vector → action recommendation    │
├─────────────────────────────────────────────────────────┤
│                  LAYER 3 — NORMALIZATION                 │
│            Pressure Normalization & Conflict Resolution   │
│       Multi-agent outputs → unified pressure vector      │
├─────────────────────────────────────────────────────────┤
│                   LAYER 2 — SENSORS                      │
│          Multi-Agent Sensor Analysis & Interpretation    │
│       Regime context → specialized agent analysis        │
├─────────────────────────────────────────────────────────┤
│                    LAYER 1 — REGIME                      │
│            Market Regime Detection & Classification      │
│       Raw market data → regime labels & transitions      │
├─────────────────────────────────────────────────────────┤
│                     LAYER 0 — DATA                       │
│          Data Foundation & Market Feeds (L1/L2)          │
│       External feeds → normalized internal data model    │
└─────────────────────────────────────────────────────────┘
```

### Layer 0 — Data Foundation

The bedrock layer ingests raw market data from multiple providers and normalizes it into a unified internal data model.

- **L1/L2 Feed Ingestion** — Real-time order book snapshots, trade prints, and ticker updates from Binance and fallback providers
- **AutoSwitch Data Engine** — Automatic failover between data providers (Binance → CoinCap → AlphaVantage → Polygon → Finnhub) with latency tracking
- **Normalization Pipeline** — All incoming data is mapped to a canonical schema regardless of source, ensuring upstream layers never need provider-specific logic
- **Historical Replay** — Cached tick data enables deterministic replay for backtesting and audit trails

### Layer 1 — Regime Detection

Processes normalized data to identify the current market regime, which governs how all downstream agents interpret signals.

- **Regime Classification** — Labels market state (trending, mean-reverting, volatile, quiet, transitional) using statistical and structural indicators
- **Transition Detection** — Identifies regime shifts in real-time, triggering agent reconfiguration
- **Context Propagation** — Broadcasts regime labels to all Layer 2 sensors, ensuring every agent operates within the correct market context
- **Confidence Scoring** — Each regime label carries a confidence score; low-confidence regimes trigger conservative agent behavior

### Layer 2 — Multi-Agent Sensors

Specialized agents analyze the market within the context provided by Layer 1. Each agent is a narrow expert, not a generalist.

- **Technical Sensor** — Pattern recognition, momentum, mean-reversion, and volatility analysis
- **Sentiment Sensor** — NLP-based sentiment extraction from news, social, and on-chain data
- **Macro Sensor** — Interest rates, funding rates, correlation shifts, and cross-asset analysis
- **Liquidity Sensor** — Order book depth analysis, slippage estimation, and flow detection
- **Volatility Sensor** — Realized vs. implied volatility, regime-adjusted volatility forecasting
- **On-Chain Sensor** — Whale movements, exchange flows, and smart money tracking (crypto markets)

Each sensor produces a **pressure vector** (directional bias + magnitude) rather than a binary signal, enabling nuanced downstream synthesis.

### Layer 3 — Pressure Normalization

Receives pressure vectors from all active sensors and resolves conflicts into a unified assessment.

- **Weighted Aggregation** — Sensor pressures are weighted by historical accuracy in the current regime
- **Conflict Resolution** — When sensors disagree, the system reduces overall confidence rather than picking a winner
- **Temporal Smoothing** — Prevents whipsaw by requiring sustained pressure before adjusting the aggregate
- **Darwinian Weighting** — Sensors with consistently poor performance in a given regime have their weights automatically reduced (linked to the Strategy Lifecycle)

### Layer 4 — Decision Synthesis & Risk Enforcement

The final layer combines the normalized pressure vector with portfolio state and risk constraints to produce an action recommendation.

- **Position Sizing** — Kelly-derived sizing modulated by current portfolio heat and regime confidence
- **Risk Guardian Gate** — Every recommendation passes through the Risk Guardian Constitution before reaching the execution layer. The Guardian can **block, reduce, or modify** any action
- **Audit Trail** — Every decision is logged with full provenance: which sensors contributed, their weights, regime context, and Guardian rulings
- **Action Output** — The system outputs a structured decision artifact (not a direct trade order), which a human operator or downstream execution system can act upon

---

## Features

- **5-Layer Execution Stack** — Deterministic data flow from raw feeds to decision artifacts, with strict layer contracts and full audit trails
- **Deterministic Pipeline** — Every decision is traceable, auditable, and defensible. The same inputs follow the same processing path every time
- **Darwinian Strategy Lifecycle** — Strategies and sensors are continuously evaluated; underperformers are automatically retired and replaced with evolved variants
- **Risk Guardian Constitution** — Independent hard-coded safety rules immune to AI reasoning that can block, reduce, or modify any action regardless of agent confidence
- **Desktop-OS UI** — Dashboard interface with real-time visualization of agent states and pressure vectors
- **AutoSwitch Data Engine** — Automatic failover between data providers (Binance, CoinCap, AlphaVantage, Polygon, Finnhub) with latency-aware routing
- **Pressure-Based Outputs** — Agents produce continuous pressure vectors (direction + magnitude), not binary signals, enabling nuanced decision-making
- **Regime-Aware Analysis** — All agents operate within detected market regime context, reducing false signals from regime-inappropriate strategies
- **Full Provenance Audit** — Every decision artifact includes which sensors contributed, their weights, regime context, and Guardian rulings

---

## Architecture

```
                          ┌──────────────────────┐
                          │   Dashboard UI       │
                          │   (FastAPI + REST)    │
                          │   ┌──────────────┐   │
                          │   │  CLI (qnai)  │   │
                          │   │  REST API    │   │
                          │   │  WebSocket   │   │
                          │   └──────┬───────┘   │
                          └─────────┼────────────┘
                                    │
                          ┌─────────▼────────────┐
                          │   Layer 4: Decision   │
                          │  ┌─────────────────┐  │
                          │  │ Risk Guardian ◄────── Constitution
                          │  │ Position Sizer  │  │  (Hard Rules)
                          │  │ Audit Logger    │  │
                          │  └────────┬────────┘  │
                          └───────────┼───────────┘
                                      │
                          ┌───────────▼───────────┐
                          │  Layer 3: Normalizer  │
                          │  ┌─────────────────┐  │
                          │  │ Weighted Agg    │  │
                          │  │ Conflict Res    │  │
                          │  │ Darwinian Wt    │◄──── Strategy
                          │  └────────┬────────┘  │  Lifecycle
                          └───────────┼───────────┘
                                      │
                   ┌──────────┬───────▼───────┬──────────┐
                   │          │               │          │
             ┌─────▼───┐ ┌───▼─────┐ ┌───────▼──┐ ┌────▼────┐
             │Technical│ │Sentiment│ │Liquidity │ │On-Chain │
             │ Sensor  │ │ Sensor  │ │  Sensor  │ │ Sensor  │
             └─────┬───┘ └───┬─────┘ └───────┬──┘ └────┬────┘
                   │         │               │         │
             ┌─────▼─────────▼───────────────▼─────────▼────┐
             │        Layer 1: Regime Detection             │
             │   ┌──────────────────────────────────────┐   │
             │   │ Classifier │ Transitions │ Confidence │   │
             │   └──────────────────────────────────────┘   │
             └──────────────────────┬───────────────────────┘
                                    │
             ┌──────────────────────▼───────────────────────┐
             │         Layer 0: Data Foundation             │
             │  ┌───────┐ ┌─────────┐ ┌───────┐ ┌───────┐ │
             │  │Binance│ │CoinCap  │ │Polygn │ │Finnhb │ │
             │  └───────┘ └─────────┘ └───────┘ └───────┘ │
             │        AutoSwitch Data Engine                │
             └─────────────────────────────────────────────┘
```

---

## Honest Notes

> We believe in radical transparency. Here are the limitations and clarifications you should know before using this project.

| Claim | Reality |
|-------|---------|
| "Deterministic Decision Intelligence" | The **data flow pipeline** is deterministic — same inputs follow the same path. This does **not** mean outputs are guaranteed correct. |
| "Decision Intelligence OS" | This is a **decision-support tool**. It produces structured decision artifacts for human review, not autonomous trade execution. |
| "Risk Guardian" | Reduces risk through hard-coded safety rules, but **cannot eliminate risk**. Market conditions can exceed any risk model. |
| "Darwinian Strategy Lifecycle" | Automatically retires poor strategies based on metrics, but **past performance does not guarantee future results**. |
| "Multi-Agent Analysis" | Multiple agents provide diverse perspectives, but **diverse analysis does not equal correct analysis**. |
| Part of HermesQuantOS | This project is one component of the larger [HermesQuantOS](https://github.com/mulkymalikuldhrs/HermesQuantOS) ecosystem. |

**Critical reminders:**
- All trading involves **significant risk of loss**
- This software is for **education and research** purposes
- Always test with **paper trading** before committing real capital
- Never risk more than you can afford to lose
- Past backtest results do not predict future performance

---

## Quick Start

### Prerequisites

- **Python** >= 3.11
- **pip** >= 23.x (or uv/poetry)
- Binance API key (use **testnet** first)

### Installation

```bash
# Clone the repository

<!-- AUTO-PACKAGE-BADGES:START -->
<!-- Auto-generated package badges -->

![npm version](https://img.shields.io/npm/v/crucix?style=flat-square&logo=npm&color=blue) ![npm downloads](https://img.shields.io/npm/dw/crucix?style=flat-square&color=brightgreen) ![npm license](https://img.shields.io/npm/l/crucix?style=flat-square) [![Deployed](https://img.shields.io/badge/deployed-2.1.0-blue?style=flat-square)](https://www.npmjs.com/package/crucix)
![PyPI version](https://img.shields.io/pypi/v/quant-nanggroe-ai?style=flat-square&logo=pypi&color=green) ![PyPI downloads](https://img.shields.io/pypi/dm/quant-nanggroe-ai?style=flat-square&color=brightgreen) ![PyPI license](https://img.shields.io/pypi/l/quant-nanggroe-ai?style=flat-square) [![Deployed](https://img.shields.io/badge/deployed-0.2.0-blue?style=flat-square)](https://pypi.org/project/quant-nanggroe-ai)

<!-- AUTO-PACKAGE-BADGES:END -->
git clone https://github.com/mulkymalikuldhrs/Quant-Nanggroe-AI.git
cd Quant-Nanggroe-AI

# Install dependencies
pip install -r requirements.txt

# Or install the quant-nanggroe-ai package
pip install -e .

# Configure environment
cp .env.example .env
# Edit .env with your API keys (use testnet keys for initial testing)

# Run the CLI
qnai run --symbols BTC/USDT --provider openai

# Or start the API server
qnai serve --port 8000
```

### Environment Variables

```env
# Required — Data Provider
QNAI_BINANCE_API_KEY=your_testnet_key
QNAI_BINANCE_API_SECRET=your_testnet_secret

# Optional — Fallback Data Providers
QNAI_ALPHA_VANTAGE_API_KEY=
QNAI_POLYGON_API_KEY=
QNAI_FINNHUB_API_KEY=

# Optional — LLM Reasoning Engine
QNAI_OPENAI_API_KEY=

# IMPORTANT: Risk limits are CONSTITUTIONAL and CANNOT be overridden via env vars.
# They are defined in quant_nanggroe/engine/risk/constants.py
# Do NOT set QNAI_RISK_MAX_PER_TRADE or similar — they will be rejected at startup.
```

> **Important**: Always start with Binance Testnet. Never connect to mainnet with untested configurations.

---

## API Reference

### Core Modules (Python)

#### Layer 0 — Data Engine

```python
from quant_nanggroe.exchange.ccxt_broker import CCXTBroker
from quant_nanggroe.exchange.paper_broker import PaperExchangeBroker

# Paper trading (default, safe)
broker = PaperExchangeBroker()
await broker.connect()

# Real exchange via CCXT
broker = CCXTBroker(exchange_id="binance", api_key=key, api_secret=secret)
await broker.connect()

# Get ticker data
ticker = await broker.get_ticker("BTC/USDT")
print(ticker.last_price, ticker.bid, ticker.ask)
```

#### Layer 1 — Regime Detection

```python
from quant_nanggroe.engine.risk.manager import RiskManager

rm = RiskManager()
status = rm.status()
# status includes: daily_pnl, weekly_pnl, drawdown, kill_switch state
```

#### Layer 2 — Agent Sensors

```python
from quant_nanggroe.agents import TradingGraph

# Build the multi-agent trading graph
graph = TradingGraph(
    llm_provider="openai",
    deep_think_model="gpt-4o",
    quick_think_model="gpt-4o-mini",
    api_key="your-openai-key",
)

# Run the pipeline
result = graph.run(
    symbols=["BTC/USDT", "ETH/USDT"],
    trade_date="2025-01-15",
)
# result includes: risk_verdict, decisions, signals, agent_outputs
```

#### Layer 3 — Risk Assessment

```python
from quant_nanggroe.engine.risk.checks import RiskCheckGate
from quant_nanggroe.engine.risk.constants import (
    MAX_RISK_PER_TRADE, MAX_DAILY_LOSS, MAX_WEEKLY_LOSS,
)

# All constants are Final and cannot be overridden
print(f"Max risk per trade: {MAX_RISK_PER_TRADE:.2%}")  # 0.50%
print(f"Max daily loss: {MAX_DAILY_LOSS:.2%}")           # 1.00%
print(f"Max weekly loss: {MAX_WEEKLY_LOSS:.2%}")         # 3.00%

# Run the 9-checkpoint risk gate
gate = RiskCheckGate()
result = gate.evaluate(symbol="BTC/USDT", direction="BUY",
                       position_size_pct=0.05, portfolio_value=100000)
```

#### Layer 4 — Decision Synthesizer

```python
from quant_nanggroe.engine.risk.kill_switch import KillSwitch

# Kill switch with file-based persistence
ks = KillSwitch()

# Check if kill switch is active (persists across restarts)
if ks.is_active:
    print("TRADING HALTED - manual reset required")

# Auto-trigger based on risk limits
ks.check_auto_trigger(
    daily_loss_pct=0.009,
    weekly_loss_pct=0.02,
    drawdown_pct=0.12,
)
```

### Risk Guardian Constitution

```python
from quant_nanggroe.engine.risk.constants import (
    MAX_RISK_PER_TRADE,      # 0.5% per trade (Final, immutable)
    MAX_DAILY_LOSS,          # 1% daily loss (Final, immutable)
    MAX_WEEKLY_LOSS,         # 3% weekly loss (Final, immutable)
    MAX_DRAWDOWN_PCT,        # 15% max drawdown (Final, immutable)
    KILL_SWITCH_DAILY_PNL,   # -0.8% early warning before 1% hard limit
)

# These limits are constitutional — they CANNOT be overridden
# by environment variables, agents, or configuration.
# Any attempt to set QNAI_RISK_MAX_PER_TRADE etc. will cause
# a RuntimeError at startup.
```

---

## Contributing

Contributions are welcome! We especially value contributions that improve transparency, risk management, and honest documentation.

### How to Contribute

1. **Fork** the repository
2. Create a **feature branch** (`git checkout -b feature/amazing-feature`)
3. **Commit** your changes (`git commit -m 'Add amazing feature'`)
4. **Push** to the branch (`git push origin feature/amazing-feature`)
5. Open a **Pull Request**

### Contribution Guidelines

- **Do not** add features that overclaim about trading performance or guaranteed returns
- **Do** improve risk management, error handling, and audit trail capabilities
- **Do** add tests for any new logic in the execution stack
- **Do** update documentation to reflect any behavioral changes
- Code style follows the existing Python strict configuration

### Development Setup

```bash
# Install dependencies
pip install -e ".[dev]"

# Run the CLI
qnai run --symbols BTC/USDT

# Run type checking
mypy quant_nanggroe/

# Run linting
ruff check quant_nanggroe/

# Run tests
pytest

# Start API server
qnai serve
```

---

## Disclaimer

**FOR EDUCATION AND RESEARCH PURPOSE ONLY**

This project is provided strictly for educational and research purposes. The authors and contributors assume **no responsibility or liability** for any financial damages, losses, or risks arising from the use of this software.

**Key risks:**

- **All trading involves significant risk of loss.** You can lose your entire investment and more.
- **Past performance does not guarantee future results.** Backtested strategies may fail in live markets.
- **The Risk Guardian reduces but cannot eliminate risk.** Market conditions can exceed any risk model's assumptions.
- **Decision-support outputs are not financial advice.** The system produces structured decision artifacts — you are solely responsible for any trading decisions you make.
- **We do not bear any responsibility or risk** for how this software is used.
- **Always use testnet/paper trading** before connecting to live markets with real capital.

---



---

## AI-MultiColony Framework (`ai_multicolony/`)

This repository contains the **ai_multicolony** framework — a colony-based autonomous agent operating system that provides the infrastructure layer for the broader AI-MultiColony-Ecosystem. It is distinct from the Quant-Nanggroe-AI trading layer and serves as the general-purpose multi-agent orchestration platform.

### Architecture Overview

```
┌──────────────────────────────────────────────────────────────┐
│                   API Layer (FastAPI + WebSocket)            │
│         REST routes, schemas, auth, rate limiting            │
├──────────────────────────────────────────────────────────────┤
│                   Colony Layer                               │
│   Colony Manager • Hands • A2A Communication • Scheduling    │
├────────────┬────────────┬────────────┬───────────────────────┤
│  Agents    │   Tools    │   Memory   │   MCP                 │
│  Registry  │  Registry  │  Manager   │  Server/Client        │
│  Lifecycle │  Shell/Code│  Paging    │  JSON-RPC             │
│  Planner   │  Browser   │  Vector    │  Permissions          │
│  Executor  │  Search    │  Knowledge │  Rate Limiting         │
│  Coder     │  Docker    │  Condensers│  Transport (stdio/sse)│
├────────────┴────────────┴────────────┴───────────────────────┤
│                   Infrastructure                              │
│  Config • Logging • Security • Audit • Exceptions • Worker   │
└──────────────────────────────────────────────────────────────┘
```

### Module Descriptions

| Module | Path | Description |
|--------|------|-------------|
| **agents** | `ai_multicolony/agents/` | Agent types (Manus, Planner, Executor, Coder, Browser, Voice, Security, Researcher, Colony), registry, shared state |
| **colony** | `ai_multicolony/colony/` | Colony management, Hands system (Security, Code, Research, Browser, Voice, Compute, Integration), A2A coordinator, task scheduler |
| **api** | `ai_multicolony/api/` | FastAPI application with REST routes (agents, colonies, tasks, tools, memory, ecosystem, WebSocket), middleware (auth, rate limit, logging, error handling) |
| **tools** | `ai_multicolony/tools/` | Built-in tool implementations: Shell, File, Browser, Search, Code, MCP, Docker, Voice, Memory, Channel |
| **memory** | `ai_multicolony/memory/` | Multi-tier memory with paging, vector store, knowledge base, and 8 condenser types (summary, extraction, temporal, rollup, dedup, priority, sliding window, hierarchical) |
| **mcp** | `ai_multicolony/mcp/` | Model Context Protocol server and client with JSON-RPC, SSE/stdio transport, permissions engine, rate limiting |
| **types** | `ai_multicolony/types/` | All Pydantic v2 models: agent, colony, task, tool, memory, security, A2A, channel, event types |
| **security** | `ai_multicolony/security/` | Security analyzer, audit trail, permission engine |
| **channels** | `ai_multicolony/channels/` | Telegram, WhatsApp, Discord, Slack integrations |
| **browser** | `ai_multicolony/browser/` | Browser automation with stealth patterns and human behavior simulation |
| **harness** | `ai_multicolony/harness/` | Agent orchestration graph, skill registry, sandbox manager, harness memory |
| **organism** | `ai_multicolony/organism/` | Self-evolution: sense engine, decision engine, solution factory, immune system, growth engine |
| **finance** | `ai_multicolony/finance/` | Financial intelligence: risk guard, kill switch, market regime detector, pressure engine, autoswitcher |
| **sources** | `ai_multicolony/sources/` | Intelligence sources: OSINT, economic, market data with source manager |
| **integrations** | `ai_multicolony/integrations/` | External framework adapters: CrewAI, AutoGen, LangGraph |
| **config** | `ai_multicolony/config/` | Pydantic-settings based configuration with env var support (`MULTICOLONY_*` prefix) |
| **sandbox** | `ai_multicolony/sandbox/` | Docker and WASM sandbox implementations |

### Relationship to the Ecosystem

```
┌─────────────────────────────────────────┐
│         AI-MultiColony-Ecosystem         │
│  ┌──────────────┐  ┌──────────────────┐ │
│  │ ai_multicolony│  │ quant_nanggroe   │ │
│  │ (framework)  │  │ (trading layer)  │ │
│  │              │  │                  │ │
│  │ Colony mgmt  │  │ 5-Layer Stack    │ │
│  │ Agent infra  │  │ Risk Guardian    │ │
│  │ MCP/Tools    │  │ Data Engine      │ │
│  │ Memory       │  │ Strategy Engine  │ │
│  └──────┬───────┘  └────────┬─────────┘ │
│         └──────────┬────────┘            │
│                    │                     │
│         ┌──────────▼──────────┐          │
│         │   Shared Infrastructure        │
│         │   API, DB, Redis, Worker       │
│         └─────────────────────┘          │
└─────────────────────────────────────────┘
```

The `ai_multicolony` framework provides the general-purpose multi-agent infrastructure (colony management, tool execution, memory, MCP, security). The `quant_nanggroe` package layers trading-specific logic (5-layer execution stack, risk guardian, data engine) on top. Both share the same API server, database, and worker infrastructure.

### Honest Capability Assessment

| Component | Status | Notes |
|-----------|--------|-------|
| **Type definitions** | ✅ Real | Comprehensive Pydantic v2 models with validators |
| **Agent base classes** | ✅ Real | BaseAgent with lifecycle, event bus, circuit breaker |
| **Colony management** | ✅ Real | Colony, Hands, A2A coordinator, scheduler |
| **MCP server/client** | ✅ Real | JSON-RPC, SSE transport, permissions |
| **Memory system** | ⚠️ Partial | Models and managers defined; vector store needs ChromaDB backend |
| **Tools** | ⚠️ Partial | Shell/File tools work; Browser/Search need external services |
| **Channels** | ⚠️ Partial | Structured but need actual bot tokens and API keys |
| **API routes** | ✅ Real | FastAPI routes with proper schemas |
| **Security** | ⚠️ Partial | Audit trail works; permission engine is scaffolded |
| **Organism/Self-evolution** | 🔄 Planned | Sense/Decision/Factory/Immune/Growth are architectural stubs |
| **Finance layer** | 🔄 Planned | Models exist but need real market data connections |
| **Dashboard** | ⚠️ Mock | Next.js UI with hardcoded mock data — see `USE_MOCK_DATA` flags |
| **Integrations** | 🔄 Planned | Adapter stubs for CrewAI, AutoGen, LangGraph |
| **Sandbox** | 🔄 Planned | Docker/WASM sandbox scaffolding exists |

**Legend:** ✅ Real and functional | ⚠️ Partial — works but needs external dependencies | 🔄 Planned — architectural stub, not production-ready

### Quick Start (ai_multicolony)

```bash
# Install the framework
pip install -e .

# Configure environment
export MULTICOLONY_API_JWT_SECRET="your-secret-key-here"
export MULTICOLONY_DEBUG=true  # Allows empty JWT secret for development

# Start the API server
amce serve --port 8000

# Or use the CLI
amce status
amce run --help
```

---

## 🔗 Related Projects

We're building a family of open source tools! Check out our other projects:

| Project | Description | Stars |
|---------|-------------|-------|
| [📈 Quant-Nanggroe-AI](https://github.com/mulkymalikuldhrs/Quant-Nanggroe-AI) | AI-powered quantitative analysis for Nanggroe market | ⭐ |
| [🧠 AI-MultiColony-Ecosystem](https://github.com/mulkymalikuldhrs/AI-MultiColony-Ecosystem) | Multi-agent AI colony simulation | ⭐ 3 |
| [📋 Kalen](https://github.com/mulkymalikuldhrs/kalen) | Smart scheduling & AI task management | ⭐ |
| [🤖 ProxyGateLLM](https://github.com/mulkymalikuldhrs/ProxyGateLLM) | Multi-LLM gateway with priority fallback | ⭐ 36 |
| [🧩 Mnemosyne](https://github.com/mulkymalikuldhrs/mnemosyne) | Knowledge management & note-taking | ⭐ |

🚀 **[Visit our Contributor Hub](https://mulkymalikuldhrs.github.io/contribute-to-our-projects/)** — 28 open source projects seeking contributors!

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

[![GitHub](https://img.shields.io/badge/GitHub-mulkymalikuldhrs-181717?style=for-the-badge&logo=github)](https://github.com/mulkymalikuldhrs)
[![Email](https://img.shields.io/badge/Email-mulkymalikudhr%40mail.com-EA4335?style=for-the-badge&logo=gmail&logoColor=white)](mailto:mulkymalikudhr@mail.com)

---

<div align="center">

**Part of the [HermesQuantOS](https://github.com/mulkymalikuldhrs/HermesQuantOS) Unified Project**

</div>

<a href="https://github.com/mulkymalikuldhrs/Quant-Nanggroe-AI">
  <img width="100%" src="https://capsule-render.vercel.app/api?type=waving&color=100:005c2a,50:003d1a,0:001a0a&height=100&section=footer" />
</a>


<!-- Schema.org Structured Data for Search Engines -->
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "SoftwareSourceCode",
  "name": "Quant-Nanggroe-AI",
  "author": {
    "@type": "Person",
    "name": "Mulky Malikul Adhr",
    "url": "https://github.com/mulkymalikuldhrs"
  },
  "programmingLanguage": "Python",
  "license": "https://spdx.org/licenses/MIT",
  "codeRepository": "https://github.com/mulkymalikuldhrs/Quant-Nanggroe-AI",
  "contributor": {
    "@type": "Organization",
    "name": "Open Source Contributors",
    "url": "https://mulkymalikuldhrs.github.io/contribute-to-our-projects/"
  }
}
</script>

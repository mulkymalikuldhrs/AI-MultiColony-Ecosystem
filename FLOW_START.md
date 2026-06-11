# Agentic AI System - Flow Start Guide

<div align="center">

![Agentic AI System](web_interface/static/cover.svg)

**Getting Started with AI MultiColony Ecosystem**

**Created by Mulky Malikul Dhaher from Indonesia 🇮🇩**

</div>

---

## Welcome to AI MultiColony Ecosystem

**Agentic AI System v0.3.0** is a multi-agent AI platform with 25 implemented agents, a multi-LLM gateway, and substantial core libraries for quantitative trading, autonomous organism systems, and intelligence briefing.

> **Note**: This is an early-stage project (v0.3.0). See README.md for current capabilities and limitations.

---

## Quick Start Flow (5 Minutes)

### Step 1: Clone & Install (2 minutes)
```bash
# Get the system
git clone https://github.com/mulkymalikuldhrs/AI-MultiColony-Ecosystem.git
cd AI-MultiColony-Ecosystem

# Install dependencies
pip install -r requirements.txt

# Quick setup
cp .env.example .env
```

### Step 2: Launch System (1 minute)
```bash
# Start the system
python web_interface/app.py

# Open your browser to: http://localhost:5000
```

### Step 3: Explore
- **Agents**: `/agents` - See all registered agents
- **Credentials**: `/credentials` - Secure credential storage
- **LLM Providers**: `/llm-providers` - Multi-LLM management
- **Dashboard**: `/dashboard` - System overview

---

## What's Available

### 25 Implemented Agents
- CyberShell, Agent Maker, Dev Engine, UI Designer, FullStack Dev
- Bug Hunter, Deploy Manager, Code Executor, System Optimizer
- And more — see README.md for the complete list

### 5 LLM Providers
- LLM7 (Free, Priority #1)
- OpenRouter (Multi-model hub)
- CAMEL AI
- OpenAI (GPT models)
- Local models (Ollama)

### Core Libraries
- **HermesQuantOS** — Quantitative trading engine (23 tool modules)
- **Autonomous Organism** — Self-organizing agent scheduler
- **Crucix Intelligence** — Multi-source intelligence briefing (27+ data sources)
- **8 IM Channels** — Slack, Telegram, Discord, Feishu, WeChat, WeCom, DingTalk

---

## What's NOT Available Yet

These features are documented for planning but do NOT have implementations:
- Built-in user authentication (JWT library exists but not wired into Flask)
- Enterprise SSO, Global CDN, Auto-scaling
- REST API endpoints for credential CRUD, code execution, LLM queries
- Many planned agents (see README.md Planned Agents section)

---

## Configuration

### Required Environment Variables
```env
SECRET_KEY=your-secret-key
CREDENTIAL_MASTER_PASSWORD=your-master-password
```

### Optional LLM Provider Keys
```env
LLM7_API_KEY=           # Free tier available
OPENROUTER_API_KEY=     # https://openrouter.ai/
CAMEL_API_KEY=          # https://camel-ai.org/
OPENAI_API_KEY=         # https://platform.openai.com/
```

---

## Troubleshooting & Support

| Issue | Solution |
|-------|----------|
| Agents not loading | Check import errors in logs; some agents need optional dependencies |
| LLM providers disabled | Set API keys in .env file |
| Credentials not saving | Verify CREDENTIAL_MASTER_PASSWORD is set |
| Slow performance | Check system resources; enable caching |

### Get Help
- **Bug Reports**: [GitHub Issues](https://github.com/mulkymalikuldhrs/AI-MultiColony-Ecosystem/issues)
- **Documentation**: See README.md for comprehensive documentation

---

## Next Steps

1. Configure at least one LLM provider
2. Store credentials in the encrypted vault
3. Explore the agent ecosystem
4. Check out the core libraries (quant, organism, crucix, channels)
5. Contribute planned agents or missing features

---

<div align="center">

**🇮🇩 Built with Indonesian innovation for global impact 🇮🇩**

*Mulky Malikul Dhaher*

</div>

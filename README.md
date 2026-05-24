[![Typing SVG](https://readme-typing-svg.demolab.com?font=Fira+Code&size=32&duration=3000&pause=1000&color=2E9EF7&center=true&vCenter=true&width=800&lines=AI-MultiColony-Ecosystem;Multi-Agent+Colony+Coordination+Platform;v8.0.0+by+Mulky+Malikul+Dhaher)](https://github.com/mulkymalikuldhrs/AI-MultiColony-Ecosystem)

<p align="center">
  <img src="https://img.shields.io/badge/version-8.0.0-gold?style=for-the-badge&logo=semver" alt="Version 8.0.0"/>
  <img src="https://img.shields.io/badge/python-3.8+-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python 3.8+"/>
  <img src="https://img.shields.io/badge/multi--agent-40%2B-FF6F00?style=for-the-badge&logo=robotframework&logoColor=white" alt="40+ Agents"/>
  <img src="https://img.shields.io/badge/license-MIT-green?style=for-the-badge" alt="MIT License"/>
  <img src="https://img.shields.io/badge/FastAPI-0.100+-009688?style=for-the-badge&logo=fastapi&logoColor=white" alt="FastAPI"/>
  <img src="https://img.shields.io/badge/Next.js-Dashboard-000000?style=for-the-badge&logo=nextdotjs&logoColor=white" alt="Next.js"/>
</p>

<p align="center">
  <a href="./README.md">🇬🇧 English</a> |
  <a href="./README_id.md">🇮🇩 Bahasa Indonesia</a> |
  <a href="./README_zh.md">🇨🇳 中文</a>
</p>

---

## Overview

**AI-MultiColony-Ecosystem** is a cutting-edge multi-agent colony coordination platform designed to orchestrate dozens of specialized AI agents in a unified, collaborative ecosystem. Built by [Mulky Malikul Dhaher](https://github.com/mulkymalikuldhrs), this platform provides a robust framework for deploying, managing, and coordinating intelligent agents across diverse domains including autonomous software development, financial trading, web automation, security monitoring, and more.

At its core, the ecosystem follows a **colony metaphor** — each agent operates as a specialized member of a larger colony, communicating through a shared memory bus, coordinated by a central agent registry, and orchestrated through schedulers and daemon managers. The platform integrates with leading AI frameworks (CAMEL AI, AutoGen, CrewAI, LangGraph) and provides a modern web dashboard built with Next.js and FastAPI for real-time monitoring and control.

The system architecture supports dynamic agent creation, self-improving autonomous loops, multi-provider LLM access through a unified gateway, and extensible connectors for Model Context Protocol (MCP) tools. Whether you are building autonomous trading systems, AI-powered development pipelines, or multi-agent research platforms, the AI-MultiColony-Ecosystem provides the foundational infrastructure to make it happen.

> **Related Project**: [HermesQuantOS](https://github.com/mulkymalikuldhrs/HermesQuantOS) — A production-ready quantitative trading OS built with this ecosystem.

---

## Architecture

The AI-MultiColony-Ecosystem is organized into five principal layers, each responsible for a critical aspect of the platform's operation. These layers work together to provide a seamless experience from agent creation to deployment and monitoring.

### Colony Core

The Colony Core is the central nervous system of the platform. It manages the entire lifecycle of agents, from registration and discovery to scheduling and memory management. The key components include:

| Component | File | Description |
|-----------|------|-------------|
| **Agent Registry** | `colony/core/agent_registry.py` | Decorator-based registration system that discovers and catalogs all agent classes automatically. Supports metadata, API routes, and dependency tracking. |
| **Base Agent** | `colony/core/base_agent.py` | Abstract base class that all agents inherit from. Provides status management, error handling, output persistence, task validation, and lifecycle hooks (`run`, `process_task`, `stop`, `restart`). |
| **Agent Manager** | `colony/core/agent_manager.py` | Orchestrates agent execution, manages agent instances, handles inter-agent communication, and provides centralized agent control. |
| **Unified Agent Registry** | `colony/core/unified_agent_registry.py` | Enhanced registry with factory methods for dynamic agent creation, instance management, and cross-colony agent discovery. |
| **Scheduler** | `colony/core/scheduler.py` | Task scheduling engine that supports cron-like patterns, priority queues, recurring tasks, and dependency-aware execution ordering. |
| **Memory Bus** | `colony/core/memory_bus.py` | Shared communication backbone that enables agents to exchange messages, share state, and coordinate activities in real-time. |
| **Daemon Manager** | `colony/core/daemon_manager.py` | Manages long-running background processes (daemons), health checks, automatic restarts, and resource monitoring. |
| **Config Loader** | `colony/core/config_loader.py` | YAML-based configuration system with environment variable interpolation, validation, and hot-reload support. |
| **Prompt Master** | `colony/core/prompt_master.py` | Advanced prompt engineering and management system for optimized LLM interactions across agents. |
| **System Bootstrap** | `colony/core/system_bootstrap.py` | Startup initialization sequence that loads configurations, initializes databases, registers agents, and starts system services. |
| **Reporting Engine** | `colony/core/reporting/` | Result collection, validation, conflict resolution, report generation, and output storage subsystem. |

### Colony Agents

The platform ships with 40+ specialized agents, each designed for a specific domain. Agents inherit from `BaseAgent` and are auto-discovered by the registry. Key agents include:

| Category | Key Agents | Description |
|----------|-----------|-------------|
| **Command & Control** | `commander_agi` | Security monitoring, threat detection, system health tracking, and agent mission coordination with autonomous response capabilities. |
| **Trading & Finance** | `smart_money_trading_agent`, `money_making_agent`, `money_making_orchestrator` | Smart Money Concepts (SMC) and ICT-based trading with order block analysis, fair value gap detection, liquidity mapping, and multi-timeframe confluence scanning. |
| **Development** | `autonomous_fullstack_dev_agent`, `fullstack_dev`, `fullstack_agent`, `dev_engine` | Autonomous code generation, system analysis, continuous improvement loops, and self-directed development with research capabilities. |
| **Web Automation** | `web_automation_agent`, `cybershell` | Selenium-powered browser automation, credential management, form filling, login/registration automation, and web interaction. |
| **Agent Creation** | `dynamic_agent_factory`, `enhanced_agent_creator`, `meta_agent_creator`, `agent_maker` | Runtime agent generation from templates, dynamic capability injection, and agent blueprint management. |
| **Operations** | `deployment_agent`, `deploy_manager`, `auto_deployment_system` | Automated deployment pipelines, service management, and infrastructure provisioning. |
| **Security** | `authentication_agent`, `credential_manager`, `auto_redactor_agent` | Credential storage, authentication flows, sensitive data redaction, and security policy enforcement. |
| **Research & AI** | `ai_research_agent`, `knowledge_management_agent`, `camel_agent_integration` | AI research automation, knowledge base management, and CAMEL AI collaborative reasoning. |
| **Design & UI** | `ui_designer`, `agent_05_designer` | UI/UX design generation, component creation, and visual interface development. |
| **System** | `system_supervisor`, `system_optimizer`, `autonomous_maintainer`, `bug_hunter_bot` | System health monitoring, performance optimization, automated maintenance, and bug detection. |
| **Specialists** | `agent_06_specialist`, `quality_control_specialist`, `deployment_specialist`, `specialist_agents` | Domain-specific expertise for quality control, deployment operations, and specialized task execution. |
| **Marketing** | `marketing_agent` | Marketing automation, content generation, and campaign management. |

### Colony API

The Colony API layer provides RESTful and WebSocket endpoints for interacting with the ecosystem:

- **FastAPI / Flask Backend** (`colony/api/app.py`) — High-performance API server with dynamic endpoint generation from the agent registry
- **WebSocket Server** (`colony/api/websocket.py`) — Real-time bidirectional communication for live updates and streaming
- **Launcher API** (`colony/api/launcher_api.py`) — System control endpoints for starting, stopping, and managing agents
- **Agent Endpoints** (`colony/api/endpoints/agents.py`, `tasks.py`, `agent_creator.py`) — CRUD operations for agents and tasks
- **Chat API** — `/api/chat/message`, `/api/chat/history`, `/api/chat/clear` for conversational AI interactions
- **System API** — `/api/system/status`, `/api/system/emergency-stop`, `/api/system/restart-all` for system management
- **Memory API** — `/api/memory/stats` for shared memory bus statistics

### Colony Integrations

The platform integrates with leading AI and cloud frameworks:

| Integration | File | Description |
|-------------|------|-------------|
| **CAMEL AI** | `colony/integrations/camel_ai_integration.py` | Multi-agent collaborative reasoning, role-playing conversations, and cooperative task solving |
| **AutoGen** | `colony/integrations/autogen_integration.py` | Microsoft AutoGen multi-agent conversation framework for complex reasoning tasks |
| **CrewAI** | `colony/integrations/crewai_integration.py` | Role-based agent crews with sequential and parallel task execution |
| **LangGraph** | `colony/integrations/langgraph_integration.py` | Graph-based agent workflows with stateful execution and conditional routing |
| **Supabase** | `colony/integrations/supabase_integration.py` | Cloud database, authentication, and real-time subscriptions |
| **Netlify** | `colony/integrations/netlify_integration.py` | Automated web deployment and hosting integration |

### Web Interface

The Next.js dashboard provides a modern, responsive control panel:

- **Dashboard** — Real-time system monitoring, agent status, and performance metrics
- **Agent Manager** — Browse, create, configure, and control all registered agents
- **Chat Interface** — Conversational AI with multi-agent routing and context management
- **Agent Creator** — Dynamic agent creation from templates with capability customization
- **Deployment Panel** — One-click deployment with environment configuration
- **Monitoring** — System health, resource usage, and alert management
- **Credential Vault** — Secure credential management with encrypted storage
- **Platform Integrations** — Configure CAMEL AI, AutoGen, CrewAI, LangGraph, and cloud providers
- **PWA Support** — Progressive Web App with offline capabilities and push notifications

### Connectors

| Connector | File | Description |
|-----------|------|-------------|
| **MCP Connector** | `connectors/mcp_connector.py` | Model Context Protocol client for connecting to MCP servers, accessing tools/resources/prompts via WebSocket |
| **LLM Gateway** | `connectors/llm_gateway.py` | Multi-provider LLM access with automatic failover, load balancing, and usage tracking. Supports LLM7, OpenRouter, and custom providers |

---

## Key Features

- **Colony-Style Agent Coordination** — Agents operate as specialized members of a colony, communicating through a shared memory bus and coordinated by a unified registry. This enables emergent collective intelligence where agents collaborate on complex tasks that no single agent could handle alone.

- **Dynamic Agent Factory** — Create new agents at runtime from templates or from scratch using the enhanced agent creator. The factory system supports capability injection, template inheritance, and runtime configuration, allowing you to rapidly prototype and deploy new agent types without modifying core code.

- **Multi-Framework Integration** — Seamlessly integrate with CAMEL AI for collaborative reasoning, AutoGen for conversational agent networks, CrewAI for role-based crews, and LangGraph for stateful graph workflows. Switch between frameworks or combine them based on your task requirements.

- **Smart Money Trading Engine** — The built-in Smart Money Concepts (SMC) and ICT trading agent provides institutional-grade market analysis including order block identification, fair value gap detection, liquidity pool mapping, and multi-timeframe confluence scanning with configurable risk management.

- **Unified LLM Gateway** — Access multiple LLM providers (LLM7, OpenRouter, OpenAI, custom endpoints) through a single interface with automatic failover, rate limiting, token tracking, and provider health monitoring. Never worry about provider outages again.

- **MCP Connector** — Connect to Model Context Protocol servers to access external tools, resources, and prompts. The connector handles the full MCP lifecycle including initialization, capability discovery, and tool invocation.

- **Real-Time Web Dashboard** — Monitor your entire colony from a modern Next.js dashboard with live agent status updates via WebSocket, interactive chat, system health metrics, and one-click deployment controls. Works as a PWA for mobile access.

- **Autonomous Self-Improvement** — The autonomous development agent continuously analyzes the system, identifies improvement opportunities, conducts research, and executes enhancements — creating a self-evolving ecosystem that gets better over time.

- **Security-First Design** — Commander AGI provides real-time security monitoring, threat detection, and autonomous response. Credential management with encrypted storage, authentication agents, and auto-redaction protect sensitive data.

---

## Quick Start

### Prerequisites

- Python 3.8 or higher
- Node.js 18+ (for web interface)
- 4GB+ RAM recommended
- Internet connection for LLM provider access

### Installation

```bash
# Clone the repository
git clone https://github.com/mulkymalikuldhrs/AI-MultiColony-Ecosystem.git
cd AI-MultiColony-Ecosystem

# Install Python dependencies
pip install -r requirements.txt

# Install web interface dependencies (optional)
cd web-interface && npm install && cd ..

# Copy environment configuration
cp .env.example .env
# Edit .env with your API keys and configuration
```

### Running the Ecosystem

```bash
# Start the full ecosystem with web interface
python main.py --start-all

# Start with specific mode
python main.py --mode ultimate

# Start web interface only
python main.py --web-ui --port 8080

# Check system status
python main.py --status --detailed

# List all registered agents
python main.py --list-agents
```

### Access the Dashboard

Once running, open your browser to:

```
http://localhost:8080
```

The dashboard provides real-time monitoring, agent management, chat interface, and system controls.

### Docker Deployment

```bash
# Build and run with Docker Compose
docker-compose up -d

# Or build manually
docker build -t ai-multicolony .
docker run -p 8080:8080 -p 5000:5000 ai-multicolony
```

---

## Project Structure

```
AI-MultiColony-Ecosystem/
├── main.py                          # Unified entry point / launcher
├── colony/
│   ├── core/                        # Colony core engine
│   │   ├── base_agent.py            # Abstract base agent class
│   │   ├── agent_registry.py        # Agent discovery & registration
│   │   ├── unified_agent_registry.py # Enhanced registry with factory
│   │   ├── agent_manager.py         # Agent lifecycle management
│   │   ├── scheduler.py             # Task scheduling engine
│   │   ├── memory_bus.py            # Shared communication bus
│   │   ├── daemon_manager.py        # Background process manager
│   │   ├── config_loader.py         # YAML configuration system
│   │   ├── prompt_master.py         # Prompt engineering system
│   │   ├── system_bootstrap.py      # Startup initialization
│   │   ├── llm_client.py            # LLM client utilities
│   │   ├── reporting/               # Result & report subsystem
│   │   └── ...                      # Additional core modules
│   ├── agents/                      # 40+ specialized agents
│   │   ├── commander_agi.py         # Security & command agent
│   │   ├── smart_money_trading_agent.py  # SMC/ICT trading
│   │   ├── autonomous_fullstack_dev_agent.py  # Auto dev
│   │   ├── web_automation_agent.py  # Browser automation
│   │   ├── dynamic_agent_factory.py # Runtime agent creation
│   │   └── ...                      # 35+ more agents
│   ├── api/                         # REST & WebSocket API
│   │   ├── app.py                   # Flask/FastAPI server
│   │   ├── websocket.py             # WebSocket handler
│   │   └── endpoints/               # API endpoint modules
│   └── integrations/                # AI framework integrations
│       ├── camel_ai_integration.py
│       ├── autogen_integration.py
│       ├── crewai_integration.py
│       ├── langgraph_integration.py
│       ├── supabase_integration.py
│       └── netlify_integration.py
├── connectors/                      # External connectors
│   ├── mcp_connector.py             # Model Context Protocol
│   └── llm_gateway.py               # Multi-provider LLM gateway
├── web-interface/                   # Next.js dashboard
│   ├── src/                         # React/Next.js source
│   ├── templates/                   # Flask HTML templates
│   ├── static/                      # CSS, JS, icons
│   └── package.json
├── config/                          # Configuration files
│   ├── system_config.yaml
│   ├── agent_templates.yaml
│   └── prompts.yaml
├── data/                            # Runtime data (gitignored)
├── database/                        # Database models & init
├── docs/                            # Documentation
├── examples/                        # Usage examples
├── scripts/                         # Utility scripts
├── sandbox/                         # Sandbox manager
├── requirements.txt                 # Python dependencies
├── docker-compose.yml               # Docker configuration
├── Dockerfile                       # Container definition
└── LICENSE                          # MIT License
```

---

## Agent Catalog

Below is a detailed catalog of the key agents available in the ecosystem. Each agent is auto-discovered by the registry and can be accessed via API endpoints or the web dashboard.

| Agent | ID | Category | Description |
|-------|----|----------|-------------|
| Commander AGI | `commander_agi` | Command & Control | Advanced security monitoring, threat detection, system health tracking, and autonomous mission coordination with real-time network analysis and incident response |
| Smart Money Trading | `smart_money_trading_agent` | Trading & Finance | Institutional-grade trading using Smart Money Concepts (SMC) and ICT methodologies — order blocks, fair value gaps, liquidity pools, multi-timeframe analysis |
| Autonomous Fullstack Dev | `autonomous_fullstack_dev_agent` | Development | Self-directed development agent that continuously analyzes the system, identifies improvements, conducts research, and executes code changes autonomously |
| Web Automation | `web_automation_agent` | Web Automation | Selenium-powered browser automation with credential management, automated login/registration, form filling, and web interaction capabilities |
| Dynamic Agent Factory | `dynamic_agent_factory` | Agent Creation | Runtime agent generation from templates with capability injection, custom configuration, and automatic registry integration |
| Enhanced Agent Creator | `enhanced_agent_creator` | Agent Creation | Advanced agent builder with template management, validation, and deployment automation |
| Meta Agent Creator | `meta_agent_creator` | Agent Creation | Creates other agent creators — meta-level factory for generating specialized agent factories |
| Chatbot Agent | `chatbot_agent` | Communication | Conversational AI agent with session management, context tracking, and multi-turn dialogue support |
| Deployment Agent | `deployment_agent` | Operations | Automated deployment pipeline management with environment configuration and rollback support |
| Deploy Manager | `deploy_manager` | Operations | Centralized deployment orchestration across multiple environments and platforms |
| Auto Deployment System | `auto_deployment_system` | Operations | Fully autonomous deployment system with health checks, canary releases, and automatic rollback |
| Authentication Agent | `authentication_agent` | Security | User authentication flows, token management, and access control enforcement |
| Credential Manager | `credential_manager` | Security | Encrypted credential storage, retrieval, and lifecycle management with usage tracking |
| Auto Redactor | `auto_redactor_agent` | Security | Automatic detection and redaction of sensitive information in agent outputs and logs |
| AI Research Agent | `ai_research_agent` | Research | Autonomous AI research with literature review, hypothesis generation, and experiment design |
| Knowledge Management | `knowledge_management_agent` | Research | Knowledge base curation, retrieval-augmented generation, and information lifecycle management |
| CAMEL Agent Integration | `camel_agent_integration` | Research | Bridge to CAMEL AI collaborative reasoning framework for multi-agent dialogue |
| Fullstack Dev | `fullstack_dev` | Development | General-purpose fullstack development agent with code generation and debugging |
| Fullstack Agent | `fullstack_agent` | Development | End-to-end development from requirements to deployment |
| Dev Engine | `dev_engine` | Development | Development task execution engine with testing and CI/CD integration |
| System Supervisor | `system_supervisor` | System | High-level system monitoring, health checks, and automated remediation |
| System Optimizer | `system_optimizer` | System | Performance profiling, resource optimization, and configuration tuning |
| Autonomous Maintainer | `autonomous_maintainer` | System | Self-healing system maintenance with log rotation, cache cleanup, and dependency updates |
| Bug Hunter Bot | `bug_hunter_bot` | System | Automated bug detection, reproduction, and reporting with severity classification |
| Quality Control Specialist | `quality_control_specialist` | Quality | Code review, testing oversight, and quality metrics enforcement |
| Marketing Agent | `marketing_agent` | Marketing | Content generation, campaign management, and social media automation |
| UI Designer | `ui_designer` | Design | Visual interface design generation with component library integration |
| Agent 05 Designer | `agent_05_designer` | Design | Specialized UI/UX design agent for dashboard and control panel interfaces |
| Backup Colony System | `backup_colony_system` | Operations | Automated backup, disaster recovery, and data replication |
| Data Sync | `data_sync` | Operations | Cross-system data synchronization and consistency management |
| LLM Provider Manager | `llm_provider_manager` | Infrastructure | Multi-provider LLM configuration, health monitoring, and cost tracking |
| Prompt Generator | `prompt_generator` | Infrastructure | Automated prompt engineering, optimization, and template management |
| CyberShell | `cybershell` | Security | Advanced shell and terminal automation with security auditing |
| Launcher Agent | `launcher_agent` | Infrastructure | System startup orchestration and service dependency management |
| AGI Colony Connector | `agi_colony_connector` | Integration | Cross-colony communication and resource sharing between separate deployments |
| Output Handler | `output_handler` | System | Result formatting, delivery, and persistence management |
| Agent 02 Meta Spawner | `agent_02_meta_spawner` | Agent Creation | Meta-agent that spawns other agents based on system needs and workload analysis |
| Agent 03 Planner | `agent_03_planner` | Planning | Strategic task planning with dependency resolution and resource allocation |
| Agent 04 Executor | `agent_04_executor` | Execution | Task execution engine with retry logic and error recovery |
| Agent 06 Specialist | `agent_06_specialist` | Specialist | Domain-specific specialist agent for targeted task execution |
| Money Making Orchestrator | `money_making_orchestrator` | Trading | Orchestrates multiple revenue-generating agents and strategies |
| Autonomous Money Ecosystem | `autonomous_money_making_ecosystem` | Trading | Complete autonomous revenue generation system with market analysis and execution |
| Code Executor | `code_executor` | Development | Safe code execution environment with sandboxing and result validation |
| Advanced Agent Creator | `advanced_agent_creator` | Agent Creation | Sophisticated agent builder with ML-powered capability suggestions |
---

## 🤝 Contributing

Contributions are welcome! We encourage the community to help improve this project.

1. **Fork** the repository
2. Create a **feature branch** (`git checkout -b feature/amazing-feature`)
3. **Commit** your changes (`git commit -m 'Add amazing feature'`)
4. **Push** to the branch (`git push origin feature/amazing-feature`)
5. Open a **Pull Request**

Please make sure to update tests as appropriate and follow the existing code style.

---

## 📬 Contact

**Mulky Malikul Dhaher** — [mulkymalikuldhaher@email.com](mailto:mulkymalikuldhaher@email.com)

GitHub: [https://github.com/mulkymalikuldhrs](https://github.com/mulkymalikuldhrs)

---

## ⚠️ Disclaimer

**This project is for Education Purpose only.**

All content, code, and documentation provided in this repository are intended solely for educational and research purposes. Nothing in this repository constitutes financial, investment, legal, or professional advice.

**Risiko apapun tidak kita tanggung.** (We are not responsible for any risks or damages.)

Use at your own risk. The authors and contributors assume no liability for any losses, damages, or consequences arising from the use of this software or information provided herein.

---

## 📄 License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.

Copyright © Mulky Malikul Dhaher. All rights reserved.


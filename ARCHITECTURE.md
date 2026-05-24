# AI-MultiColony-Ecosystem Architecture

This document provides a comprehensive technical overview of the AI-MultiColony-Ecosystem architecture. It describes the system's layered design, core components, data flows, and the lifecycle of agents within the platform. This is intended for developers who want to understand the internals, extend the platform, or contribute new agents and integrations.

> **Repository**: [https://github.com/mulkymalikuldhrs/AI-MultiColony-Ecosystem](https://github.com/mulkymalikuldhrs/AI-MultiColony-Ecosystem)
> **Related Project**: [HermesQuantOS](https://github.com/mulkymalikuldhrs/HermesQuantOS) — A production-ready quantitative trading OS built with this ecosystem.

---

## Table of Contents

- [Architectural Overview](#architectural-overview)
- [Colony Core](#colony-core)
  - [Agent Registry](#agent-registry)
  - [Base Agent](#base-agent)
  - [Agent Manager](#agent-manager)
  - [Unified Agent Registry](#unified-agent-registry)
  - [Scheduler](#scheduler)
  - [Memory Bus](#memory-bus)
  - [Daemon Manager](#daemon-manager)
  - [Configuration Loader](#configuration-loader)
  - [Prompt Master](#prompt-master)
  - [System Bootstrap](#system-bootstrap)
  - [Reporting Engine](#reporting-engine)
- [Colony Agents](#colony-agents)
  - [Agent Categories](#agent-categories)
  - [Agent Catalog](#agent-catalog)
- [Colony API](#colony-api)
  - [REST Endpoints](#rest-endpoints)
  - [WebSocket Server](#websocket-server)
  - [API Architecture](#api-architecture)
- [Colony Integrations](#colony-integrations)
  - [CAMEL AI](#camel-ai)
  - [AutoGen](#autogen)
  - [CrewAI](#crewai)
  - [LangGraph](#langgraph)
  - [Supabase](#supabase)
  - [Netlify](#netlify)
- [Connectors](#connectors)
  - [MCP Connector](#mcp-connector)
  - [LLM Gateway](#llm-gateway)
- [Web Interface](#web-interface)
- [Data Flow](#data-flow)
- [Agent Lifecycle](#agent-lifecycle)
- [Security Architecture](#security-architecture)
- [Deployment Architecture](#deployment-architecture)

---

## Architectural Overview

The AI-MultiColony-Ecosystem follows a **layered architecture** pattern organized around the metaphor of a colony of specialized agents working together toward common goals. The system is composed of five principal layers that communicate through well-defined interfaces:

```
┌──────────────────────────────────────────────────────┐
│                   Web Interface                       │
│              (Next.js + React Dashboard)              │
├──────────────────────────────────────────────────────┤
│                    Colony API                         │
│         (FastAPI + WebSocket + REST Endpoints)        │
├──────────────────────────────────────────────────────┤
│                 Colony Agents                         │
│           (40+ Specialized Agent Classes)             │
├──────────────────────────────────────────────────────┤
│                  Colony Core                          │
│    (Registry, Scheduler, Memory Bus, Daemon Mgr)      │
├──────────────────────────────────────────────────────┤
│         Connectors & Integrations                     │
│   (LLM Gateway, MCP, CAMEL, AutoGen, CrewAI, etc.)   │
└──────────────────────────────────────────────────────┘
```

Each layer has a distinct responsibility. The **Connectors & Integrations** layer provides access to external AI frameworks, LLM providers, and cloud services. The **Colony Core** layer manages the fundamental infrastructure for agent lifecycle, communication, and scheduling. The **Colony Agents** layer contains the specialized intelligent agents that perform actual work. The **Colony API** layer exposes the ecosystem through REST and WebSocket interfaces. The **Web Interface** layer provides a human-friendly dashboard for monitoring and control.

The architecture emphasizes **loose coupling** between layers, **event-driven communication** through the memory bus, and **automatic discovery** of agents through the registry system. This design allows new agents to be added without modifying core infrastructure, and integrations to be swapped or extended without affecting agent logic.

---

## Colony Core

The Colony Core is the central nervous system of the platform. It provides the foundational infrastructure upon which all agents operate. Every component in the core is designed to be extensible, thread-safe, and capable of supporting the full lifecycle of agents from registration through execution to termination.

### Agent Registry

**File**: `colony/core/agent_registry.py`

The Agent Registry is the discovery and cataloging system for all agents in the ecosystem. It uses a decorator-based registration pattern that allows agents to self-register when their Python modules are loaded. This eliminates the need for manual configuration and ensures that adding a new agent file to the `colony/agents/` directory automatically makes it available throughout the system.

**Key Capabilities**:
- **Decorator-Based Registration**: The `@register_agent` decorator captures agent metadata (name, description, route, category, dependencies) at class definition time. When the module is imported, the decorator registers the class with the global registry without requiring any additional boilerplate code.
- **Metadata Management**: Each registered agent carries rich metadata including its display name, description, API route, category classification, configuration schema, and dependency list. This metadata is used by the API layer to auto-generate endpoints and by the web dashboard to display agent information.
- **Dependency Tracking**: Agents can declare dependencies on other agents through the registry. The scheduler uses this information to determine execution order and ensure that prerequisite agents are running before dependent agents are started.
- **API Route Generation**: The registry automatically generates REST API endpoints for each registered agent based on the route metadata. This means every agent is immediately accessible via the API without additional configuration.
- **Discovery Interface**: The registry provides query interfaces for discovering agents by category, capability, or name. This enables dynamic agent selection and routing in multi-agent workflows.

```python
# Registration example
@register_agent(
    name="smart_money_trading_agent",
    description="SMC/ICT institutional trading analysis",
    route="/api/agents/smart_money_trading_agent",
    category="Trading & Finance",
    dependencies=["llm_provider_manager", "credential_manager"]
)
class SmartMoneyTradingAgent(BaseAgent):
    ...
```

### Base Agent

**File**: `colony/core/base_agent.py`

The Base Agent is the abstract base class that all agents in the ecosystem inherit from. It defines the contract for agent behavior, provides common infrastructure for status management, error handling, output persistence, and task validation, and implements the lifecycle hooks that the scheduler and agent manager use to control agent execution.

**Key Capabilities**:
- **Lifecycle Hooks**: The base class defines four primary lifecycle methods that every agent must implement or can override: `run()` for the main execution loop, `process_task()` for handling incoming tasks, `stop()` for graceful shutdown, and `restart()` for reinitialization. These hooks are called by the agent manager and scheduler at appropriate points in the agent lifecycle.
- **Status Management**: Agents maintain a status state machine with states including `idle`, `running`, `completed`, `error`, `stopping`, and `stopped`. The `update_status()` method transitions between states and notifies the memory bus, enabling real-time monitoring through the dashboard and API.
- **Error Handling**: The base class provides a standardized error handling framework through `handle_error()`. Errors are logged, stored in the agent's error history, and reported to the memory bus. Critical errors can trigger automatic restart through the daemon manager.
- **Output Persistence**: The `save_output()` method provides a consistent interface for agents to persist their results. Outputs are stored with metadata including timestamp, agent ID, task ID, and execution context. This enables the reporting engine to collect and validate results across agents.
- **Task Validation**: Before processing a task, the base class validates the task structure against the agent's expected input schema. Invalid tasks are rejected with descriptive error messages rather than causing runtime failures.
- **Format Response**: The `format_response()` method ensures all agent responses follow a consistent structure with success status, data payload, error information, and execution metadata.

### Agent Manager

**File**: `colony/core/agent_manager.py`

The Agent Manager orchestrates the execution of agents, manages agent instances, handles inter-agent communication, and provides centralized control over the agent ecosystem. It serves as the primary interface between the API layer and the agent layer, translating API requests into agent actions.

**Key Capabilities**:
- **Instance Management**: The agent manager maintains a pool of agent instances, creating new instances on demand and reusing existing ones when possible. It handles the lifecycle of each instance from creation through execution to cleanup, ensuring proper resource management and preventing memory leaks.
- **Execution Orchestration**: When a task needs to be executed, the agent manager selects the appropriate agent based on the task type, checks agent availability, and dispatches the task. It manages concurrent execution of multiple agents and handles queuing when all instances of a particular agent are busy.
- **Inter-Agent Communication**: The agent manager facilitates communication between agents through the memory bus. It provides methods for agents to send messages, share state, and coordinate activities. This enables complex multi-agent workflows where agents collaborate on tasks.
- **Centralized Control**: Through the agent manager, the API layer can start, stop, restart, and query agents. The manager provides a unified control interface that abstracts away the details of individual agent implementation.

### Unified Agent Registry

**File**: `colony/core/unified_agent_registry.py`

The Unified Agent Registry extends the basic agent registry with factory methods for dynamic agent creation, instance management, and cross-colony agent discovery. It represents an enhanced version of the registry that supports the full operational lifecycle of agents, not just their static metadata.

**Key Capabilities**:
- **Factory Methods**: The unified registry provides factory methods for creating agent instances dynamically. Given an agent name or category, the factory can instantiate the appropriate agent class with the correct configuration, dependencies, and memory manager. This is used by the dynamic agent factory and agent creator agents.
- **Instance Management**: Beyond class-level registration, the unified registry tracks active agent instances, their states, and their resource usage. This enables the system to provide real-time statistics on agent deployment and utilization.
- **Cross-Colony Discovery**: For deployments with multiple AI-MultiColony-Ecosystem instances, the unified registry supports cross-colony agent discovery. Agents in one colony can discover and communicate with agents in another colony through the AGI Colony Connector, enabling distributed multi-colony architectures.

### Scheduler

**File**: `colony/core/scheduler.py`

The Scheduler is the task scheduling engine that manages when and how agents execute their tasks. It supports multiple scheduling patterns, priority-based execution, and dependency-aware ordering to ensure that tasks are executed efficiently and in the correct sequence.

**Key Capabilities**:
- **Cron-Like Scheduling**: The scheduler supports cron-like patterns for recurring tasks, allowing agents to be scheduled to run at specific times or intervals. This is particularly useful for monitoring agents, periodic reporting, and scheduled maintenance tasks.
- **Priority Queues**: Tasks are organized in priority queues, with higher-priority tasks executing before lower-priority ones. The priority system supports dynamic reprioritization, allowing the system to respond to urgent tasks (such as security alerts from Commander AGI) by elevating their priority.
- **Recurring Tasks**: The scheduler supports one-time and recurring task definitions. Recurring tasks can be configured with intervals, cron expressions, or custom recurrence rules. The scheduler automatically reschedules recurring tasks after completion.
- **Dependency-Aware Execution**: Tasks can declare dependencies on other tasks or agents. The scheduler uses this information to determine the correct execution order, ensuring that prerequisite tasks are completed before dependent tasks begin. This prevents race conditions and ensures data consistency.
- **Concurrency Control**: The scheduler manages concurrent task execution, respecting resource limits and agent capacity. It prevents overloading the system by limiting the number of concurrent tasks per agent and per category.

### Memory Bus

**File**: `colony/core/memory_bus.py`

The Memory Bus is the shared communication backbone that enables agents to exchange messages, share state, and coordinate activities in real-time. It implements a publish-subscribe pattern that decouples agents from each other while enabling flexible communication patterns.

**Key Capabilities**:
- **Publish-Subscribe Messaging**: Agents publish messages to named channels (topics) and subscribe to channels they are interested in. The memory bus handles message routing and delivery, ensuring that messages reach all subscribers without requiring agents to know about each other directly.
- **State Sharing**: The memory bus maintains a shared state store where agents can read and write key-value data. This enables agents to share context, configuration, and intermediate results without point-to-point communication. State changes trigger notifications to subscribed agents.
- **Real-Time Coordination**: Messages on the memory bus are delivered in real-time, enabling agents to coordinate their activities dynamically. For example, when Commander AGI detects a security threat, it can broadcast an alert that is immediately received by all security-related agents.
- **Message Persistence**: The memory bus optionally persists messages to disk, enabling replay and recovery after system restarts. This ensures that no critical messages are lost even in the event of a crash.
- **Statistics and Monitoring**: The memory bus tracks message throughput, subscriber counts, and channel activity. These statistics are exposed through the Memory API endpoint (`/api/memory/stats`) and displayed on the web dashboard.

### Daemon Manager

**File**: `colony/core/daemon_manager.py`

The Daemon Manager manages long-running background processes (daemons) within the ecosystem. It provides health monitoring, automatic restarts, and resource management for agents that need to run continuously rather than on a task-by-task basis.

**Key Capabilities**:
- **Process Lifecycle**: The daemon manager starts, monitors, and stops daemon processes. It maintains a registry of active daemons and their resource usage, providing a centralized view of background operations.
- **Health Checks**: The daemon manager performs periodic health checks on all running daemons. Health checks include process liveness, memory usage, CPU consumption, and custom health endpoints. Unhealthy daemons are automatically flagged for restart.
- **Automatic Restarts**: When a daemon crashes or becomes unresponsive, the daemon manager automatically restarts it with configurable retry policies. It respects backoff intervals and maximum retry limits to prevent restart loops.
- **Resource Monitoring**: The daemon manager tracks resource consumption (CPU, memory, disk I/O) for each daemon process. This information is used for capacity planning, performance optimization, and alerting when resource limits are approached.

### Configuration Loader

**File**: `colony/core/config_loader.py`

The Configuration Loader provides a YAML-based configuration system with environment variable interpolation, validation, and hot-reload support. It is responsible for loading and managing all system configuration, including agent configurations, API settings, integration credentials, and scheduling parameters.

**Key Capabilities**:
- **YAML Configuration**: All system configuration is expressed in YAML files located in the `config/` directory. The configuration loader parses these files and provides a structured access interface.
- **Environment Variable Interpolation**: Configuration values can reference environment variables using `${VAR_NAME}` syntax. This enables sensitive values (API keys, database passwords) to be stored in environment variables rather than in configuration files.
- **Validation**: The configuration loader validates configuration files against schemas, ensuring that required fields are present and values are within acceptable ranges. Validation errors are reported at startup to prevent misconfiguration.
- **Hot Reload**: The configuration loader monitors configuration files for changes and can reload them without restarting the system. This enables runtime configuration changes such as adjusting agent parameters or adding new integrations.

### Prompt Master

**File**: `colony/core/prompt_master.py`

The Prompt Master is an advanced prompt engineering and management system that optimizes LLM interactions across all agents in the ecosystem. It provides template management, variable substitution, prompt chaining, and performance tracking to ensure that agents communicate effectively with LLM providers.

**Key Capabilities**:
- **Template Management**: Prompts are stored as reusable templates in `config/prompts.yaml`. The Prompt Master loads, parses, and caches these templates, providing a centralized prompt library that all agents can reference.
- **Variable Substitution**: Templates support variable placeholders that are substituted with runtime values. This enables dynamic prompt construction based on task context, agent state, and user input.
- **Prompt Chaining**: Complex interactions can be broken into sequences of prompts, where the output of one prompt becomes the input to the next. The Prompt Master manages these chains, ensuring proper context flow and state management.
- **Performance Tracking**: The Prompt Master tracks prompt performance metrics including token usage, response quality, and latency. This data is used to optimize prompts over time and identify opportunities for improvement.

### System Bootstrap

**File**: `colony/core/system_bootstrap.py`

The System Bootstrap is the startup initialization sequence that brings the ecosystem from a cold start to full operational readiness. It orchestrates the loading of configurations, initialization of databases, registration of agents, and starting of system services in the correct order.

**Bootstrap Sequence**:
1. **Load Configuration** — Parse YAML files, interpolate environment variables, validate schemas
2. **Initialize Database** — Connect to Supabase or local database, run migrations, seed initial data
3. **Initialize Memory Bus** — Create shared state store, set up message persistence
4. **Register Agents** — Scan `colony/agents/` directory, import modules, execute `@register_agent` decorators
5. **Initialize LLM Gateway** — Configure LLM providers, perform health checks, set up failover
6. **Start Daemon Manager** — Launch daemon processes for long-running agents
7. **Start Scheduler** — Load scheduled tasks, begin cron-based execution
8. **Start API Server** — Launch FastAPI/Flask server, register dynamic endpoints
9. **Start WebSocket Server** — Enable real-time communication channels
10. **Health Verification** — Verify all components are operational, report system status

### Reporting Engine

**File**: `colony/core/reporting/`

The Reporting Engine is a subsystem responsible for collecting, validating, resolving conflicts in, and persisting the outputs generated by agents. It provides a structured pipeline from raw agent output to validated, stored results that can be accessed through the API and displayed on the dashboard.

**Key Capabilities**:
- **Result Collection**: The reporting engine collects outputs from all agents through the memory bus and direct agent output methods. It maintains a queue of pending results and processes them asynchronously.
- **Validation**: Each result is validated against the agent's expected output schema. Invalid results are flagged and routed to error handling, preventing corrupt data from entering the system.
- **Conflict Resolution**: When multiple agents produce conflicting results for the same task, the reporting engine applies configurable conflict resolution strategies (e.g., priority-based, voting, latest-wins) to determine the authoritative result.
- **Report Generation**: The reporting engine can generate aggregate reports from individual agent outputs, summarizing performance metrics, task completion rates, and system health indicators.
- **Output Storage**: Validated results are persisted to the database and file system, with metadata for search, retrieval, and audit purposes.

---

## Colony Agents

The platform ships with 40+ specialized agents, each designed for a specific domain. All agents inherit from `BaseAgent` and are auto-discovered by the registry at startup. The agent layer is where the core intelligence of the ecosystem resides — each agent encapsulates domain-specific knowledge, LLM interaction patterns, and autonomous decision-making logic.

### Agent Categories

Agents are organized into functional categories that reflect their domain of expertise. This categorization helps with discovery, routing, and resource allocation within the system.

#### Command & Control

The Command & Control category contains the strategic oversight agents that monitor and coordinate the broader ecosystem. The primary agent in this category is **Commander AGI** (`commander_agi`), which provides security monitoring, threat detection, system health tracking, and agent mission coordination. Commander AGI operates as a continuous daemon that observes system activity, detects anomalies, and can autonomously initiate response actions such as shutting down compromised agents, alerting security personnel, or adjusting system parameters.

#### Trading & Finance

The Trading & Finance category contains agents focused on financial market analysis and trading execution. The flagship agent is **Smart Money Trading Agent** (`smart_money_trading_agent`), which implements Smart Money Concepts (SMC) and Inner Circle Trader (ICT) methodologies for institutional-grade market analysis. It performs order block identification, fair value gap detection, liquidity pool mapping, and multi-timeframe confluence scanning. Supporting agents include **Money Making Orchestrator** (`money_making_orchestrator`), which coordinates multiple revenue-generating strategies, and **Autonomous Money Making Ecosystem** (`autonomous_money_making_ecosystem`), which provides a complete autonomous revenue generation pipeline.

#### Development

The Development category contains agents focused on software development tasks. **Autonomous Fullstack Dev Agent** (`autonomous_fullstack_dev_agent`) is a self-directed development agent that continuously analyzes the system, identifies improvement opportunities, conducts research, and executes code changes autonomously. It implements a self-improving loop where the agent evaluates its own output and iteratively refines it. **Fullstack Dev** (`fullstack_dev`) and **Fullstack Agent** (`fullstack_agent`) provide general-purpose and end-to-end development capabilities respectively, while **Dev Engine** (`dev_engine`) serves as the development task execution engine with testing and CI/CD integration. **Code Executor** (`code_executor`) provides a safe sandboxed environment for executing generated code.

#### Web Automation

The Web Automation category contains agents for browser automation and web interaction. **Web Automation Agent** (`web_automation_agent`) provides Selenium-powered browser automation with credential management, automated login/registration, form filling, and web interaction. **CyberShell** (`cybershell`) extends these capabilities with advanced shell and terminal automation, including security auditing features.

#### Agent Creation

The Agent Creation category contains the meta-agents responsible for creating other agents. **Dynamic Agent Factory** (`dynamic_agent_factory`) generates new agents at runtime from templates, injecting capabilities and registering them automatically. **Enhanced Agent Creator** (`enhanced_agent_creator`) provides an advanced builder with template management and validation. **Meta Agent Creator** (`meta_agent_creator`) takes this a level further by creating other agent creators — a meta-level factory for generating specialized agent factories. **Advanced Agent Creator** (`advanced_agent_creator`) uses ML-powered capability suggestions to recommend agent configurations.

#### Operations

The Operations category contains agents focused on deployment and infrastructure management. **Deployment Agent** (`deployment_agent`) manages automated deployment pipelines with environment configuration and rollback support. **Deploy Manager** (`deploy_manager`) provides centralized deployment orchestration across multiple environments. **Auto Deployment System** (`auto_deployment_system`) implements a fully autonomous deployment workflow with health checks, canary releases, and automatic rollback. **Backup Colony System** (`backup_colony_system`) handles automated backup, disaster recovery, and data replication. **Data Sync** (`data_sync`) manages cross-system data synchronization and consistency.

#### Security

The Security category contains agents focused on protecting the ecosystem and its data. **Authentication Agent** (`authentication_agent`) manages user authentication flows, token management, and access control enforcement. **Credential Manager** (`credential_manager`) provides encrypted credential storage, retrieval, and lifecycle management with usage tracking. **Auto Redactor** (`auto_redactor_agent`) automatically detects and redacts sensitive information in agent outputs and logs, preventing data leakage.

#### Research & AI

The Research & AI category contains agents focused on AI research and knowledge management. **AI Research Agent** (`ai_research_agent`) performs autonomous AI research including literature review, hypothesis generation, and experiment design. **Knowledge Management Agent** (`knowledge_management_agent`) curates the knowledge base, implements retrieval-augmented generation, and manages the information lifecycle. **CAMEL Agent Integration** (`camel_agent_integration`) bridges to the CAMEL AI collaborative reasoning framework for multi-agent dialogue.

#### System

The System category contains agents that maintain and optimize the platform itself. **System Supervisor** (`system_supervisor`) provides high-level system monitoring, health checks, and automated remediation. **System Optimizer** (`system_optimizer`) performs performance profiling, resource optimization, and configuration tuning. **Autonomous Maintainer** (`autonomous_maintainer`) implements self-healing system maintenance including log rotation, cache cleanup, and dependency updates. **Bug Hunter Bot** (`bug_hunter_bot`) performs automated bug detection, reproduction, and reporting with severity classification.

#### Design & UI

The Design & UI category contains agents focused on visual design and interface creation. **UI Designer** (`ui_designer`) generates visual interface designs with component library integration. **Agent 05 Designer** (`agent_05_designer`) specializes in dashboard and control panel interfaces.

#### Marketing

The Marketing category contains the **Marketing Agent** (`marketing_agent`), which handles content generation, campaign management, and social media automation for promoting the ecosystem and its outputs.

### Agent Catalog

| Agent | ID | Category | Description |
|-------|----|----------|-------------|
| Commander AGI | `commander_agi` | Command & Control | Advanced security monitoring, threat detection, and autonomous mission coordination |
| Smart Money Trading | `smart_money_trading_agent` | Trading & Finance | SMC/ICT institutional trading with order blocks, FVG, liquidity mapping |
| Autonomous Fullstack Dev | `autonomous_fullstack_dev_agent` | Development | Self-directed development with research and self-improvement loops |
| Web Automation | `web_automation_agent` | Web Automation | Selenium browser automation with credential management |
| Dynamic Agent Factory | `dynamic_agent_factory` | Agent Creation | Runtime agent generation with capability injection |
| Enhanced Agent Creator | `enhanced_agent_creator` | Agent Creation | Advanced agent builder with template management |
| Meta Agent Creator | `meta_agent_creator` | Agent Creation | Meta-level factory for generating agent factories |
| Advanced Agent Creator | `advanced_agent_creator` | Agent Creation | ML-powered agent builder with capability suggestions |
| Chatbot Agent | `chatbot_agent` | Communication | Conversational AI with multi-turn dialogue support |
| Deployment Agent | `deployment_agent` | Operations | Automated deployment pipeline management |
| Deploy Manager | `deploy_manager` | Operations | Centralized deployment orchestration |
| Auto Deployment System | `auto_deployment_system` | Operations | Fully autonomous deployment with canary releases |
| Authentication Agent | `authentication_agent` | Security | Authentication flows and access control |
| Credential Manager | `credential_manager` | Security | Encrypted credential storage and lifecycle management |
| Auto Redactor | `auto_redactor_agent` | Security | Automatic sensitive data redaction |
| AI Research Agent | `ai_research_agent` | Research | Autonomous AI research and experimentation |
| Knowledge Management | `knowledge_management_agent` | Research | Knowledge base curation and RAG |
| CAMEL Agent Integration | `camel_agent_integration` | Research | CAMEL AI collaborative reasoning bridge |
| Fullstack Dev | `fullstack_dev` | Development | General-purpose fullstack development |
| Fullstack Agent | `fullstack_agent` | Development | End-to-end development from requirements to deployment |
| Dev Engine | `dev_engine` | Development | Development task execution with CI/CD |
| Code Executor | `code_executor` | Development | Sandboxed code execution environment |
| System Supervisor | `system_supervisor` | System | System monitoring and automated remediation |
| System Optimizer | `system_optimizer` | System | Performance profiling and optimization |
| Autonomous Maintainer | `autonomous_maintainer` | System | Self-healing maintenance and cleanup |
| Bug Hunter Bot | `bug_hunter_bot` | System | Automated bug detection and reporting |
| Quality Control Specialist | `quality_control_specialist` | Quality | Code review and quality metrics enforcement |
| Marketing Agent | `marketing_agent` | Marketing | Content generation and campaign management |
| UI Designer | `ui_designer` | Design | Visual interface design generation |
| Agent 05 Designer | `agent_05_designer` | Design | Dashboard and control panel design |
| CyberShell | `cybershell` | Security | Shell and terminal automation with security auditing |
| Backup Colony System | `backup_colony_system` | Operations | Automated backup and disaster recovery |
| Data Sync | `data_sync` | Operations | Cross-system data synchronization |
| LLM Provider Manager | `llm_provider_manager` | Infrastructure | Multi-provider LLM configuration and monitoring |
| Prompt Generator | `prompt_generator` | Infrastructure | Automated prompt engineering and optimization |
| Launcher Agent | `launcher_agent` | Infrastructure | System startup orchestration |
| AGI Colony Connector | `agi_colony_connector` | Integration | Cross-colony communication and resource sharing |
| Output Handler | `output_handler` | System | Result formatting and persistence management |
| Agent 02 Meta Spawner | `agent_02_meta_spawner` | Agent Creation | Meta-agent that spawns agents based on workload |
| Agent 03 Planner | `agent_03_planner` | Planning | Strategic task planning with dependency resolution |
| Agent 04 Executor | `agent_04_executor` | Execution | Task execution with retry logic and error recovery |
| Agent 06 Specialist | `agent_06_specialist` | Specialist | Domain-specific specialist for targeted execution |
| Money Making Orchestrator | `money_making_orchestrator` | Trading | Multi-strategy revenue orchestration |
| Autonomous Money Ecosystem | `autonomous_money_making_ecosystem` | Trading | Complete autonomous revenue generation system |

---

## Colony API

The Colony API layer provides the external interface to the ecosystem, exposing all system capabilities through RESTful HTTP endpoints and WebSocket connections. The API is built on FastAPI for high-performance async request handling, with Flask compatibility for legacy endpoints.

### REST Endpoints

The API dynamically generates endpoints for each registered agent, providing a consistent interface for agent interaction. The following endpoint groups are available:

#### Agent Endpoints
- `GET /api/agents` — List all registered agents with metadata
- `GET /api/agents/{agent_id}` — Get agent details, status, and configuration
- `POST /api/agents/{agent_id}/start` — Start a specific agent
- `POST /api/agents/{agent_id}/stop` — Stop a specific agent
- `POST /api/agents/{agent_id}/restart` — Restart a specific agent
- `POST /api/agents/{agent_id}/task` — Submit a task to a specific agent
- `GET /api/agents/{agent_id}/output` — Retrieve agent output history

#### Task Endpoints
- `GET /api/tasks` — List all tasks with filtering options
- `POST /api/tasks` — Create a new task
- `GET /api/tasks/{task_id}` — Get task details and status
- `DELETE /api/tasks/{task_id}` — Cancel a pending task

#### Chat Endpoints
- `POST /api/chat/message` — Send a message to the conversational AI
- `GET /api/chat/history` — Retrieve chat history
- `POST /api/chat/clear` — Clear chat history

#### System Endpoints
- `GET /api/system/status` — Get overall system status and health
- `POST /api/system/emergency-stop` — Emergency shutdown of all agents
- `POST /api/system/restart-all` — Restart all agents and services

#### Memory Endpoints
- `GET /api/memory/stats` — Get memory bus statistics

#### Agent Creator Endpoints
- `POST /api/agent-creator/create` — Create a new agent from a template
- `GET /api/agent-creator/templates` — List available agent templates

#### Launcher Endpoints
- `GET /api/launcher/status` — Get launcher status
- `POST /api/launcher/start` — Start the ecosystem
- `POST /api/launcher/stop` — Stop the ecosystem

### WebSocket Server

**File**: `colony/api/websocket.py`

The WebSocket server provides real-time bidirectional communication between the ecosystem and connected clients. It enables live updates for agent status changes, task progress, system alerts, and streaming agent outputs. The WebSocket server runs alongside the REST API on the same port and supports multiple concurrent client connections.

**WebSocket Channels**:
- `agent_status` — Real-time agent status updates (running, stopped, error)
- `task_progress` — Task execution progress and completion notifications
- `system_alerts` — Security alerts, resource warnings, and system notifications
- `chat_stream` — Streaming chat responses from conversational agents
- `memory_updates` — Shared state changes from the memory bus

### API Architecture

The API architecture follows a layered pattern within the API layer itself:

```
Request → Router → Middleware → Endpoint Handler → Agent Manager → Agent
                                                       ↓
                                              Memory Bus → WebSocket → Client
```

1. **Router**: FastAPI's router directs incoming requests to the appropriate endpoint handler based on the URL path and HTTP method.
2. **Middleware**: Authentication, rate limiting, request logging, and CORS middleware process requests before they reach the endpoint handler.
3. **Endpoint Handler**: The handler validates request parameters, constructs task objects, and delegates to the agent manager.
4. **Agent Manager**: The agent manager selects the appropriate agent, dispatches the task, and collects the result.
5. **Memory Bus**: Status changes and results are published to the memory bus, which forwards them to WebSocket subscribers for real-time updates.

---

## Colony Integrations

The platform integrates with leading AI frameworks and cloud services, providing agents with access to diverse capabilities beyond what is built into the core system. Each integration is implemented as a separate module in `colony/integrations/`, following a consistent interface pattern.

### CAMEL AI

**File**: `colony/integrations/camel_ai_integration.py`

The CAMEL AI integration provides access to the CAMEL (Communicative Agents for Mind Exploration of Large Language Model Society) framework. CAMEL enables multi-agent collaborative reasoning through role-playing conversations where agents take on different roles and work together to solve tasks. The integration wraps CAMEL's conversation patterns into the colony's agent model, allowing any agent to leverage CAMEL's collaborative capabilities.

**Key Features**:
- Role-playing conversation setup between multiple AI agents
- Cooperative task solving with turn-based dialogue
- Integration with the colony's memory bus for cross-framework communication
- Support for CAMEL's built-in role templates and custom role definitions

### AutoGen

**File**: `colony/integrations/autogen_integration.py`

The AutoGen integration connects the ecosystem to Microsoft's AutoGen framework, which provides multi-agent conversation capabilities for complex reasoning tasks. AutoGen excels at structured conversations between agents with different specialties, enabling the colony to leverage AutoGen's conversation patterns for tasks that benefit from deliberative, step-by-step reasoning.

**Key Features**:
- Multi-agent conversation flows with configurable participant roles
- Integration with AutoGen's AssistantAgent and UserProxyAgent patterns
- Code execution capabilities through AutoGen's code execution engine
- Support for human-in-the-loop workflows via AutoGen's human input mode

### CrewAI

**File**: `colony/integrations/crewai_integration.py`

The CrewAI integration provides access to CrewAI's role-based agent crew system. CrewAI organizes agents into crews where each agent has a defined role, goal, and backstory. Tasks are executed sequentially or in parallel by the crew, with agents collaborating and delegating based on their roles. This integration maps the colony's agents into CrewAI's crew model.

**Key Features**:
- Role-based crew composition with defined agent roles and goals
- Sequential and parallel task execution within crews
- Agent delegation and collaboration within the crew framework
- Task tool integration for connecting crew agents to external services

### LangGraph

**File**: `colony/integrations/langgraph_integration.py`

The LangGraph integration provides graph-based agent workflows with stateful execution and conditional routing. LangGraph allows the colony to define complex agent workflows as directed graphs, where nodes represent agent actions and edges represent transitions with optional conditions. This is particularly useful for multi-step processes that require branching logic and state persistence.

**Key Features**:
- Directed graph workflow definition with nodes and conditional edges
- Stateful execution with persistent state across workflow steps
- Conditional routing based on agent output or external conditions
- Support for cycles and loops in workflows for iterative processes
- Checkpoint and recovery for long-running workflows

### Supabase

**File**: `colony/integrations/supabase_integration.py`

The Supabase integration provides cloud database, authentication, and real-time subscription capabilities. Supabase serves as the primary persistence layer for agent outputs, system state, user data, and configuration. The integration supports real-time subscriptions that push database changes to connected agents and dashboard clients.

**Key Features**:
- PostgreSQL database access through Supabase's client library
- Row-level security for data isolation between users and colonies
- Real-time subscriptions for live data updates
- Authentication integration for user management
- Storage buckets for agent output files and artifacts

### Netlify

**File**: `colony/integrations/netlify_integration.py`

The Netlify integration provides automated web deployment and hosting. Agents that generate web content (such as the UI Designer or Fullstack Dev agents) can deploy their outputs directly to Netlify through this integration, making them accessible on the web within seconds.

**Key Features**:
- Automated site creation and deployment
- Continuous deployment from Git repositories
- Serverless function deployment for API endpoints
- Custom domain and SSL certificate management
- Deploy previews for testing before going live

---

## Connectors

### MCP Connector

**File**: `connectors/mcp_connector.py`

The Model Context Protocol (MCP) connector implements a client for the Model Context Protocol, enabling the ecosystem to connect to MCP servers and access external tools, resources, and prompts. MCP is an open protocol that standardizes how AI systems interact with external capabilities, and this connector handles the full MCP lifecycle.

**Key Features**:
- WebSocket-based communication with MCP servers
- Capability discovery — automatically discover available tools, resources, and prompts
- Tool invocation — call MCP tools with structured parameters and receive results
- Resource access — read and subscribe to MCP resources
- Prompt management — list and execute MCP prompts
- Connection lifecycle management — initialize, negotiate capabilities, and gracefully disconnect

### LLM Gateway

**File**: `connectors/llm_gateway.py`

The LLM Gateway provides unified access to multiple LLM providers through a single interface. It abstracts away the differences between providers, handles failover, load balancing, and usage tracking, ensuring that agents always have access to LLM capabilities regardless of individual provider availability.

**Key Features**:
- **Multi-Provider Support**: LLM7, OpenRouter, OpenAI, and custom endpoints
- **Automatic Failover**: When a provider fails, requests are automatically routed to the next available provider
- **Load Balancing**: Distribute requests across providers based on cost, latency, or round-robin strategies
- **Rate Limiting**: Enforce per-provider and global rate limits to prevent API abuse
- **Token Tracking**: Track token usage per agent, per provider, and globally for cost management
- **Health Monitoring**: Periodically check provider availability and response times, routing traffic away from degraded providers
- **Streaming Support**: Stream LLM responses for real-time output in chat and agent workflows

---

## Web Interface

**Directory**: `web-interface/`

The web interface is a modern Next.js dashboard that provides a comprehensive control panel for the entire ecosystem. It communicates with the Colony API through REST calls and WebSocket connections for real-time updates.

### Technology Stack

- **Framework**: Next.js with React
- **Styling**: Tailwind CSS for responsive, utility-first styling
- **State Management**: React hooks and context for local state, WebSocket for server state
- **Real-Time**: WebSocket connections for live agent status, task progress, and chat
- **PWA**: Progressive Web App support for offline access and mobile installation

### Dashboard Pages

| Page | Route | Description |
|------|-------|-------------|
| Dashboard | `/` | System overview with agent counts, health metrics, and recent activity |
| Agent Manager | `/agents` | Browse, create, configure, and control all registered agents |
| Chat Interface | `/chat` | Conversational AI with multi-agent routing and context management |
| Agent Creator | `/creator` | Dynamic agent creation from templates with capability customization |
| Deployment Panel | `/deploy` | One-click deployment with environment configuration |
| Monitoring | `/monitoring` | System health, resource usage, and alert management |
| Credential Vault | `/credentials` | Secure credential management with encrypted storage |
| Integrations | `/integrations` | Configure CAMEL AI, AutoGen, CrewAI, LangGraph, and cloud providers |

---

## Data Flow

The following diagram illustrates the primary data flow patterns within the ecosystem:

### Task Submission Flow

```
User → Web Dashboard → REST API → Agent Manager → Agent Instance → LLM Gateway → LLM Provider
                                      ↓                                    ↓
                               Memory Bus ← ← ← ← ← ← ← ← ← ← ← ← ← ←
                                  ↓
                          WebSocket → Dashboard (real-time update)
```

1. A user submits a task through the web dashboard or API
2. The REST API routes the request to the appropriate endpoint handler
3. The endpoint handler delegates to the Agent Manager
4. The Agent Manager selects and dispatches the task to the appropriate agent instance
5. The agent processes the task, calling the LLM Gateway as needed for AI capabilities
6. The LLM Gateway routes the request to an available LLM provider
7. The agent publishes status updates and results to the Memory Bus
8. The WebSocket server forwards real-time updates to connected dashboard clients

### Agent Coordination Flow

```
Agent A → Memory Bus → Agent B
              ↓
          Scheduler → Agent C (dependency on Agent B's output)
```

1. Agent A completes its task and publishes results to the Memory Bus
2. Agent B, subscribed to Agent A's output channel, receives the results and begins processing
3. The Scheduler, aware of the dependency chain, triggers Agent C after Agent B completes
4. Results are aggregated by the Reporting Engine for final output

### Autonomous Improvement Flow

```
Autonomous Fullstack Dev Agent
    ↓
Analyze System → Identify Improvements → Research Solutions
    ↓                                       ↓
Execute Changes ← ← ← ← ← ← ← ← ← ← ← ←
    ↓
Report Results → Memory Bus → Commander AGI (security review)
```

The autonomous development agent implements a self-improving loop: it analyzes the system, identifies areas for improvement, researches potential solutions, executes changes, and reports results. Commander AGI monitors these changes for security implications.

---

## Agent Lifecycle

Every agent in the ecosystem follows a defined lifecycle managed by the core infrastructure:

```
Registration → Initialization → Idle → Running → Completed → Idle
                   ↑               ↓          ↓
                   │            Stopping    Error → Recovery → Idle
                   │               ↓
                   └───── Stopped ┘
```

### Lifecycle States

| State | Description | Transitions |
|-------|-------------|-------------|
| **Registered** | Agent class is registered with the agent registry. Metadata is available but no instance exists. | → Initializing |
| **Initializing** | Agent instance is being created. Configuration is loaded, dependencies are resolved, and resources are allocated. | → Idle, → Error |
| **Idle** | Agent is ready to accept tasks but not currently processing any. | → Running, → Stopping |
| **Running** | Agent is actively processing a task. | → Completed, → Error, → Stopping |
| **Completed** | Agent has finished processing a task successfully. | → Idle |
| **Error** | Agent encountered an error during execution. Error details are logged and reported. | → Recovery, → Stopping |
| **Recovery** | Agent is attempting to recover from an error. The daemon manager may restart the agent. | → Idle, → Error |
| **Stopping** | Agent is being gracefully shut down. Resources are being released. | → Stopped |
| **Stopped** | Agent is fully stopped and not consuming resources. | → Initializing (restart) |

### Lifecycle Hooks

Each state transition triggers corresponding lifecycle hooks in the BaseAgent class:

- `on_initialize()` — Called when the agent is being initialized
- `on_start()` — Called when transitioning from Idle to Running
- `on_complete()` — Called when a task completes successfully
- `on_error(error)` — Called when an error occurs
- `on_recovery()` — Called during error recovery
- `on_stop()` — Called during graceful shutdown
- `on_restart()` — Called when the agent is being restarted

---

## Security Architecture

The AI-MultiColony-Ecosystem implements a multi-layered security architecture:

### Authentication & Authorization

- **Authentication Agent** handles user authentication with JWT token management
- **Credential Manager** provides encrypted storage for API keys, database passwords, and other secrets
- Access control is enforced at the API layer through middleware

### Data Protection

- **Auto Redactor Agent** automatically detects and redacts sensitive information (PII, API keys, credentials) in agent outputs and logs
- Credentials are stored in encrypted form and decrypted only at runtime
- Environment variable interpolation prevents secrets from appearing in configuration files

### Network Security

- **Commander AGI** provides real-time threat detection and network analysis
- All API communication supports HTTPS/TLS encryption
- WebSocket connections are authenticated and authorized

### Agent Isolation

- Each agent runs in its own execution context with limited access to system resources
- The **Code Executor** agent uses sandboxing to isolate untrusted code execution
- Inter-agent communication is mediated through the memory bus, preventing direct access between agents

---

## Deployment Architecture

### Single-Node Deployment

The simplest deployment model runs all components on a single server:

```
┌─────────────────────────────────────┐
│           Single Server              │
│  ┌───────────┐  ┌───────────────┐   │
│  │ Next.js   │  │ FastAPI       │   │
│  │ Dashboard │←→│ API Server    │   │
│  └───────────┘  └───────┬───────┘   │
│                         │           │
│                 ┌───────┴───────┐   │
│                 │ Colony Core   │   │
│                 │ (Agents,      │   │
│                 │  Scheduler,   │   │
│                 │  Memory Bus)  │   │
│                 └───────────────┘   │
│                                     │
│  Port 8080 (Web)  Port 5000 (API)   │
└─────────────────────────────────────┘
```

### Docker Deployment

The ecosystem provides Docker and Docker Compose configurations for containerized deployment:

```bash
# Build and run with Docker Compose
docker-compose up -d

# Or build manually
docker build -t ai-multicolony .
docker run -p 8080:8080 -p 5000:5000 ai-multicolony
```

### Multi-Colony Deployment

For large-scale deployments, multiple colony instances can be connected through the AGI Colony Connector:

```
Colony A ←→ AGI Colony Connector ←→ Colony B
(Singapore)                         (US-East)
     ↑                                   ↑
     └──────── AGI Colony Connector ─────┘
                    ↕
              Colony C
              (Europe)
```

Each colony runs its own set of agents, scheduler, and memory bus. The AGI Colony Connector enables cross-colony communication, resource sharing, and coordinated task execution across geographically distributed deployments.

---

*This architecture document is maintained alongside the codebase. For the latest updates, refer to the [GitHub repository](https://github.com/mulkymalikuldhrs/AI-MultiColony-Ecosystem).*

*Built by [Mulky Malikul Dhaher](https://github.com/mulkymalikuldhrs) in Indonesia.*

"""
AI-MultiColony-Ecosystem - Multi-Agent Operating System with Autonomous Colonies
Developed by: Mulky Malikul Dhaher (Mul)

Modules:
    quant: Quantitative trading tools (HermesQuantOS integration)
    organism: Autonomous organism modules (scheduler, sense, immune, decision, factory, memory)
    gateway: API gateway with routing, middleware, auth, and localization
    backend: Backend services (memory, persistence, skills, middleware)
    agents: Agent implementations (Agentic-AI-System + deer-flow lead_agent/factory)
    core: Core system components
    integrations: External integrations
    channels: IM channel integrations (Slack, Telegram, Discord, Feishu, WeChat, etc.)
    mcp: Model Context Protocol client and tools
    guardrails: Pre-tool-call authorization middleware
    memory: Conversation memory management with LLM summarization
    skills: Dynamic skill system with installer, parser, validation
    persistence: SQLAlchemy 2.0 async ORM for runs, threads, users
    runtime: Agent runtime (checkpointer, events, runs, serialization)
    subagents: Sub-agent orchestration (bash, general-purpose)
    df_tools: Deer-flow built-in tools (clarification, task, tool_search, etc.)
    config: Application configuration (model, memory, skills, guardrails, etc.)
    sandbox: Local sandbox for code execution
    tracing: OpenTelemetry tracing factory and metadata
    community: Community integrations (ddg_search, exa, firecrawl, tavily, etc.)
    llm_models: LLM provider abstractions (OpenAI, Claude, vLLM, MindIE, etc.)
    middlewares: Agent middlewares (clarification, safety, summarization, etc.)
    uploads: File upload management
    utils: Shared utilities (messages, network, time, readability)
    reflection: Class reflection and dependency resolution
"""

__version__ = "0.4.0"
__author__ = "Mulky Malikul Dhaher (Mul)"

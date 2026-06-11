# AI MultiColony Ecosystem

A consolidated colony-based agent operating system merging 21 repos into a unified platform.

## Quick Start

```bash
# Install
pip install -e ".[dev]"

# Run tests
make test

# Start API server
make api

# CLI
ai-multicolony run
```

## Architecture

- **Core**: BaseAgent, AgentLoop, ToolRegistry, EventBus, LLMProvider, MemoryManager
- **Agents**: Manus, Planner, Executor, Coder, Browser, Voice, Security, Researcher, Colony
- **Tools**: Shell, File, Browser, Search, Code, MCP, Docker, Voice, Memory, Channel
- **Colony**: Manager, Hands, Scheduler, Coordinator
- **Memory**: Condensers, Vector Store, Paging, Session, Knowledge
- **Channels**: Telegram, WhatsApp, Discord, Slack
- **Security**: Analyzer, Audit, Permissions
- **API**: FastAPI with WebSocket support

## License

MIT

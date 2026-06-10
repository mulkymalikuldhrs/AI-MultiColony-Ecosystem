# Contributing to This Project

First off, thanks for taking the time to contribute! 🎉

The following is a set of guidelines for contributing to this project. These are mostly guidelines, not rules. Use your best judgment, and feel free to propose changes to this document in a pull request.

## How Can I Contribute?

### Report Bugs

- Use the GitHub Issues section to report bugs
- Include as much detail as possible: OS, version, steps to reproduce
- Use a clear and descriptive title

### Suggest Enhancements

- Open a GitHub Issue with the tag `enhancement`
- Describe the enhancement in detail
- Explain why this enhancement would be useful

### Pull Requests

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Commit your changes (`git commit -m 'Add amazing feature'`)
5. Push to the branch (`git push origin feature/amazing-feature`)
6. Open a Pull Request

## Development Process

1. **Clone** the repository
2. Create a **branch** for your feature/fix
3. **Test** your changes thoroughly
4. **Document** any new features
5. Submit a **Pull Request**

## Agent Contribution Guidelines

### Creating a New Agent

When adding a new agent to the ecosystem, follow these requirements:

1. **File location**: Place the agent in `agents/<agent_name>.py`
2. **Class structure**: Create a class with the following interface:
   ```python
   class MyAgent:
       def __init__(self):
           self.agent_id = "my_agent"
           self.name = "My Agent"
           self.status = "ready"
           self.capabilities = ["capability_1", "capability_2"]

       async def process_task(self, task: dict) -> dict:
           """Route tasks to appropriate handlers."""
           action = task.get("action", "default_action")
           # Dispatch to handler methods
           ...

       def get_performance_metrics(self) -> dict:
           """Return agent performance metrics for monitoring."""
           return {
               "agent_id": self.agent_id,
               "status": self.status,
               "capabilities": self.capabilities,
               "stats": self._stats,
           }
   ```

3. **Required methods**:
   - `process_task(task: dict) -> dict` — Main task dispatcher
   - `get_performance_metrics() -> dict` — Returns metrics for Agent Watcher

4. **Error handling**:
   - Use `try/except` around all handler methods
   - Return standardized error responses: `{"success": False, "error": "...", "agent": self.agent_id}`
   - Never raise unhandled exceptions from `process_task`

5. **Optional dependencies**:
   - Wrap optional imports in `try/except ImportError`
   - Set a flag (e.g., `_AIOHTTP_AVAILABLE = True`) to check at runtime
   - Provide graceful degradation when dependencies are missing

6. **Global instance**:
   - Create a global instance at the bottom of the file: `my_agent = MyAgent()`
   - This allows the agent registry to import it

7. **Register with Agent Watcher**:
   - Add the agent to the `module_map` in `agents/agent_watcher.py`
   - Add the agent ID to the `known_agents` list in `_discover_agents()`

### Specific Agent Types

#### API Integration Agents (like GitHub Agent)
- Handle rate limiting explicitly (track remaining requests, wait when needed)
- Use async HTTP clients (aiohttp) for non-blocking I/O
- Provide configuration via environment variables
- Track request statistics (total, successful, failed, avg response time)

#### Voice/Audio Agents (like Voice Agent)
- Support multiple providers with fallback chains
- Handle audio data securely (process in-memory, don't persist unnecessarily)
- Cache transcriptions by audio hash to avoid redundant API calls
- Support configurable providers via environment variables

#### Blockchain/Web3 Agents (like Web3 Plugin)
- **Default to read-only operations** — no transaction signing
- Never store private keys or wallet secrets
- Support multiple networks/chains with configurable RPC endpoints
- Wrap synchronous library calls in `asyncio.run_in_executor`
- Document all security considerations

#### Monitoring Agents (like Agent Watcher)
- Implement health checks with configurable timeouts
- Provide alerting with severity levels (info/warning/critical)
- Persist state for recovery across restarts
- Support auto-restart with configurable cooldown and max attempts

### Testing Requirements for New Agents

All new agents must include tests:

1. **Unit tests**: Test each handler method independently
   ```python
   # tests/test_agents.py
   import pytest
   from agents.my_agent import MyAgent

   @pytest.mark.asyncio
   async def test_my_agent_process_task():
       agent = MyAgent()
       result = await agent.process_task({"action": "default_action"})
       assert result["success"] is True
   ```

2. **Error handling tests**: Verify graceful degradation
   ```python
   @pytest.mark.asyncio
   async def test_my_agent_handles_unknown_action():
       agent = MyAgent()
       result = await agent.process_task({"action": "nonexistent"})
       assert result["success"] is False
   ```

3. **Optional dependency tests**: Verify behavior when dependencies are unavailable
4. **Performance metrics tests**: Verify `get_performance_metrics()` returns valid data
5. **Integration tests**: Test the agent via the API endpoints (if applicable)

Run tests:
```bash
# Run all tests
python -m pytest tests/

# Run specific test file
python -m pytest tests/test_agents.py

# Run with verbose output
python -m pytest tests/ -v
```

### Adding New Monitoring Targets

When adding services that should be monitored:

1. Add a scrape configuration to `monitoring/prometheus.yml`
2. Include appropriate labels (component, service, framework)
3. Add the exporter as a Docker Compose service if needed
4. Document the monitoring target in `DEPLOYMENT_STATUS.md`

## Code Style

- Follow PEP 8 for Python code
- Write clear, descriptive commit messages
- Add comments for complex logic
- Keep functions small and focused
- Use descriptive variable and function names
- Add docstrings to public functions and classes
- Handle `ImportError` gracefully for optional dependencies

## Documentation Standards

When adding or updating features:

1. **Code documentation**:
   - Add a module docstring at the top of each file
   - Include the author credit: `Made with ❤️ by Mulky Malikul Dhaher in Indonesia 🇮🇩`
   - Document all public methods with docstrings
   - Include type hints for function parameters and return values

2. **README.md updates**:
   - Add new agents to the Agent Ecosystem table
   - Update the agent count in the badges and description
   - Add any new environment variables to the Configuration section

3. **CHANGELOG.md updates**:
   - Add entries under the appropriate section (Added, Fixed, Changed, etc.)
   - Use the format: `**Agent Name** (`path/to/file.py`): Brief description`

4. **SECURITY.md updates**:
   - Document any new security considerations for new agents
   - Update the Version History table

5. **FLOW_START.md updates**:
   - Add new voice commands for new agents
   - Update the Explore section with new features
   - Add new integration flows

## Priority Areas for Contribution

| Priority | Area | Description |
|----------|------|-------------|
| 🔴 High | **Agent implementations** | Complete remaining `TODO` placeholders in partially implemented agents |
| 🔴 High | **Test coverage** | Add unit and integration tests for existing and new agents |
| 🔴 High | **Missing requirements.txt entries** | Identify and add missing third-party dependencies |
| 🟡 Medium | **Authentication** | Add optional built-in user authentication module |
| 🟡 Medium | **Deduplicate credential managers** | Consolidate into a single, well-tested implementation |
| 🟡 Medium | **PostgreSQL support** | Add database backend option beyond SQLite |
| 🟡 Medium | **Prometheus alerting rules** | Add alerting rules for critical service failures |
| 🟡 Medium | **Grafana dashboards** | Create pre-built Grafana dashboard configurations |
| 🟢 Low | **Documentation** | Improve agent documentation and usage examples |
| 🟢 Low | **Web3 write operations** | Add optional transaction signing with proper security controls |

## Community

Be respectful and constructive. We're all here to learn and build together.

---

## 📬 Contact

**Mulky Malikul Dhaher** — [mulkymalikuldhaher@email.com](mailto:mulkymalikuldhaher@email.com)

GitHub: [https://github.com/mulkymalikuldhrs](https://github.com/mulkymalikuldhrs)

---

> This project is for **Education Purpose** only. **Risiko apapun tidak kita tanggung.** (We are not responsible for any risks or damages.)

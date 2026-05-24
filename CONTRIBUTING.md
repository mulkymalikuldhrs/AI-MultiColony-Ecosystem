# Contributing to AI-MultiColony-Ecosystem

First off, thank you for considering contributing to **AI-MultiColony-Ecosystem**! We appreciate your time and effort, and we want to make the contribution process as smooth and transparent as possible. This document provides guidelines and instructions for contributing to the project.

The AI-MultiColony-Ecosystem is a multi-agent colony coordination platform with 40+ specialized AI agents. Whether you are fixing bugs, adding new agents, improving the web dashboard, or enhancing documentation, your contributions help make this ecosystem better for everyone.

---

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [How to Contribute](#how-to-contribute)
- [Development Setup](#development-setup)
- [Creating a New Agent](#creating-a-new-agent)
- [Coding Standards](#coding-standards)
- [Commit Guidelines](#commit-guidelines)
- [Pull Request Process](#pull-request-process)
- [Reporting Bugs](#reporting-bugs)
- [Feature Requests](#feature-requests)
- [Documentation Contributions](#documentation-contributions)
- [Community](#community)

---

## Code of Conduct

This project and everyone participating in it is governed by a commitment to creating a welcoming and inclusive environment. By participating, you are expected to uphold this standard. We are committed to providing a friendly, safe, and welcoming environment for all, regardless of experience level, gender, gender identity and expression, sexual orientation, disability, personal appearance, body size, race, ethnicity, age, religion, or nationality.

Unacceptable behavior includes harassment, offensive comments, personal attacks, and any conduct that would be considered inappropriate in a professional setting. If you witness or experience unacceptable behavior, please report it to [mulkymalikuldhaher@email.com](mailto:mulkymalikuldhaher@email.com).

---

## Getting Started

### Prerequisites

Before you begin contributing, ensure you have the following tools installed on your development machine:

- **Python 3.8+** — The core platform and all agents are written in Python
- **Node.js 18+** — Required for building and developing the web interface
- **Git** — For version control and submitting contributions
- **pip** — Python package manager
- **npm** — Node.js package manager (included with Node.js)
- 4GB+ RAM recommended for running the full ecosystem locally

### Fork and Clone

1. **Fork** the repository by clicking the "Fork" button on [GitHub](https://github.com/mulkymalikuldhrs/AI-MultiColony-Ecosystem/fork)
2. **Clone** your fork to your local machine:

```bash
git clone https://github.com/YOUR_USERNAME/AI-MultiColony-Ecosystem.git
cd AI-MultiColony-Ecosystem
```

3. **Add the upstream** remote to stay in sync with the main repository:

```bash
git remote add upstream https://github.com/mulkymalikuldhrs/AI-MultiColony-Ecosystem.git
```

4. **Create a branch** for your contribution:

```bash
git checkout -b feature/your-feature-name
```

---

## How to Contribute

There are many ways to contribute to AI-MultiColony-Ecosystem:

### Types of Contributions

- **New Agents** — Create specialized agents by inheriting from `BaseAgent` and registering with the agent registry
- **Bug Fixes** — Identify and fix issues in existing agents, core modules, or the web interface
- **Feature Enhancements** — Improve existing functionality or add new capabilities
- **Documentation** — Improve README, add guides, write tutorials, or translate documentation
- **Testing** — Write unit tests, integration tests, or improve test coverage
- **Web Interface** — Enhance the Next.js dashboard with new features or UI improvements
- **Integrations** — Add support for new AI frameworks or cloud services
- **Performance** — Optimize agent execution, memory bus throughput, or API response times

### Contribution Workflow

1. **Check existing issues** — Look at the [issue tracker](https://github.com/mulkymalikuldhrs/AI-MultiColony-Ecosystem/issues) to see if your idea or bug is already being discussed
2. **Create an issue** — If none exists, create a new issue describing the bug or feature
3. **Claim the issue** — Comment on the issue to let others know you are working on it
4. **Create a branch** — Branch off from `main` with a descriptive name (e.g., `feature/trading-agent-v2`, `fix/memory-bus-leak`)
5. **Develop** — Implement your changes following the coding standards below
6. **Test** — Ensure all existing tests pass and add new tests for your changes
7. **Submit a PR** — Create a pull request with a clear description of your changes

---

## Development Setup

### Install Dependencies

```bash
# Install Python dependencies
pip install -r requirements.txt

# Install development dependencies
pip install -r requirements-dev.txt

# Install web interface dependencies (optional)
cd web-interface && npm install && cd ..
```

### Environment Configuration

```bash
# Copy the example environment file
cp .env.example .env

# Edit .env with your API keys and configuration
# Required keys depend on which agents and integrations you plan to use
```

### Run Tests

```bash
# Run the full test suite
python -m pytest tests/

# Run tests with verbose output
python -m pytest tests/ -v

# Run tests for a specific module
python -m pytest tests/test_agent_registry.py

# Run with coverage reporting
python -m pytest tests/ --cov=colony --cov-report=html
```

### Code Formatting

We use **Black** for Python code formatting and **ESLint/Prettier** for the web interface:

```bash
# Format Python code
black colony/ connectors/

# Check formatting without making changes
black --check colony/ connectors/

# Lint the web interface
cd web-interface && npm run lint
```

### Run the Ecosystem Locally

```bash
# Start the full ecosystem
python main.py --start-all

# Start with web interface
python main.py --web-ui --port 8080

# Check system status
python main.py --status --detailed
```

---

## Creating a New Agent

All agents in the ecosystem inherit from `BaseAgent` and are registered using the `@register_agent` decorator. This ensures automatic discovery by the agent registry and dynamic API endpoint generation. Follow this template when creating a new agent:

```python
from colony.core.base_agent import BaseAgent
from colony.core.agent_registry import register_agent

@register_agent(
    name="my_custom_agent",
    description="A custom agent that performs specialized tasks",
    route="/api/agents/my_custom_agent"
)
class MyCustomAgent(BaseAgent):
    """Custom agent for specialized task execution.

    This agent demonstrates the standard pattern for creating new agents
    within the AI-MultiColony-Ecosystem. All agents must inherit from
    BaseAgent and implement the required lifecycle methods.
    """

    def __init__(self, name="my_custom_agent", config=None, memory_manager=None):
        super().__init__(name=name, config=config, memory_manager=memory_manager)
        # Initialize agent-specific attributes here
        self.capabilities = ["task_execution", "data_processing"]

    def run(self):
        """Main agent execution loop.

        This method is called when the agent is started. It should contain
        the primary logic for the agent's operation.
        """
        self.update_status("running")
        try:
            # Your agent logic here
            result = self.execute_primary_task()
            self.save_output(result)
            self.update_status("completed")
        except Exception as e:
            self.handle_error(e)
            self.update_status("error")

    async def process_task(self, task):
        """Process an incoming task from the task queue.

        Args:
            task: A task dictionary containing the task type, parameters,
                  and any required context.

        Returns:
            A formatted response dictionary with success status and data.
        """
        task_type = task.get("type", "default")
        params = task.get("params", {})

        result = {"success": True, "data": "processed", "task_type": task_type}
        return self.format_response(str(result))

    def stop(self):
        """Gracefully stop the agent."""
        self.update_status("stopping")
        # Cleanup resources
        self.update_status("stopped")

    def restart(self):
        """Restart the agent after a stop."""
        self.stop()
        self.run()
```

### Agent Registration Requirements

When registering a new agent, the `@register_agent` decorator requires the following:

- **name** — A unique identifier for the agent (snake_case, used as the agent ID)
- **description** — A clear, concise description of the agent's purpose and capabilities
- **route** — The API endpoint path where the agent can be accessed

Optional registration parameters:

- **category** — The agent's category (e.g., "Trading", "Development", "Security")
- **dependencies** — List of other agent IDs this agent depends on
- **config_schema** — JSON schema for validating agent configuration

### Agent File Location

Place your new agent file in the `colony/agents/` directory:

```
colony/agents/
├── my_custom_agent.py       # Your new agent
├── commander_agi.py         # Existing agents
├── smart_money_trading_agent.py
└── ...
```

The agent registry will automatically discover and register your agent when the system starts.

---

## Coding Standards

### Python Code Style

- Follow **PEP 8** style guidelines
- Use **Black** formatter (line length: 88 characters)
- Use **type hints** for function signatures
- Write **docstrings** for all classes and public methods (Google style)
- Maximum function length: 50 lines (refactor if longer)
- Use meaningful variable and function names

### Example Docstring Style

```python
def process_trading_signal(self, signal: dict, timeframe: str = "1h") -> dict:
    """Process a trading signal and generate execution orders.

    Args:
        signal: A dictionary containing the trading signal data,
            including entry price, stop loss, and take profit levels.
        timeframe: The timeframe for the signal analysis.
            Defaults to "1h".

    Returns:
        A dictionary containing the execution order with keys:
        - 'action': 'BUY' or 'SELL'
        - 'entry_price': float
        - 'stop_loss': float
        - 'take_profit': float
        - 'confidence': float between 0 and 1

    Raises:
        ValueError: If the signal data is invalid or incomplete.
    """
```

### Web Interface Code Style

- Follow the existing Next.js/React patterns in the `web-interface/` directory
- Use **TypeScript** for new files
- Use **Tailwind CSS** for styling
- Follow the component structure established in `web-interface/src/`

---

## Commit Guidelines

We follow conventional commit messages to maintain a clean and readable git history:

### Commit Message Format

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Types

- **feat**: A new feature (e.g., `feat(agents): add sentiment analysis agent`)
- **fix**: A bug fix (e.g., `fix(memory-bus): resolve message ordering issue`)
- **docs**: Documentation changes (e.g., `docs(readme): add Chinese translation`)
- **style**: Code style changes (formatting, semicolons, etc.)
- **refactor**: Code refactoring without behavior changes
- **test**: Adding or updating tests
- **chore**: Maintenance tasks, dependency updates, etc.

### Examples

```
feat(agents): add sentiment analysis agent

Add a new sentiment analysis agent that processes text data
and returns sentiment scores. The agent integrates with the
LLM gateway for multi-provider support.

Closes #42
```

```
fix(scheduler): resolve priority queue deadlock

Fix a deadlock issue in the scheduler that occurred when
high-priority tasks were scheduled while lower-priority
tasks were already executing.

Fixes #38
```

---

## Pull Request Process

### Before Submitting

1. **Sync with upstream** — Ensure your branch is up to date with the main repository:

```bash
git fetch upstream
git rebase upstream/main
```

2. **Run all tests** — Make sure the full test suite passes:

```bash
python -m pytest tests/
```

3. **Format your code** — Ensure code passes formatting checks:

```bash
black colony/ connectors/
```

4. **Update documentation** — If your PR adds features or changes behavior, update the relevant documentation files (README.md, README_id.md, README_zh.md)

### PR Description Template

When creating a pull request, include the following information:

- **Description**: What does this PR do and why?
- **Type of Change**: Bug fix / New feature / Breaking change / Documentation update
- **Related Issues**: Link to any related issues (e.g., "Closes #12")
- **Testing**: How was this change tested?
- **Screenshots**: If applicable, add screenshots of UI changes
- **Breaking Changes**: List any breaking changes and migration steps

### Review Process

1. A maintainer will review your PR within 3-5 business days
2. Address any feedback or requested changes
3. Once approved, a maintainer will merge your PR
4. Your contribution will be credited in the CHANGELOG

### PR Requirements

- All tests must pass
- Code must be formatted with Black (Python) and Prettier (JavaScript)
- New agents must include unit tests
- New features must include documentation updates
- No unnecessary files or large binary assets

---

## Reporting Bugs

If you find a bug, please create an issue on [GitHub Issues](https://github.com/mulkymalikuldhrs/AI-MultiColony-Ecosystem/issues) with the following information:

### Bug Report Template

```markdown
**Bug Description**
A clear description of what the bug is.

**To Reproduce**
Steps to reproduce the behavior:
1. Start the ecosystem with `python main.py --start-all`
2. Trigger the specific agent or feature
3. Observe the error

**Expected Behavior**
A clear description of what you expected to happen.

**Actual Behavior**
A clear description of what actually happened.

**Environment**
- OS: [e.g., Ubuntu 22.04]
- Python version: [e.g., 3.10.12]
- Node.js version: [e.g., 18.17.0]
- Ecosystem version: [e.g., v8.0.0]

**Logs**
Paste any relevant log output or error messages.

**Additional Context**
Any other context about the problem.
```

---

## Feature Requests

We welcome feature requests! Please create an issue on [GitHub Issues](https://github.com/mulkymalikuldhrs/AI-MultiColony-Ecosystem/issues) with the following:

- **Feature Description**: A clear description of the feature you would like
- **Use Case**: Why is this feature needed? What problem does it solve?
- **Proposed Implementation**: If you have ideas on how to implement it
- **Alternatives Considered**: Any alternative solutions you have considered

---

## Documentation Contributions

Documentation is critical for the project's success. We welcome contributions to:

- **README.md**, **README_id.md**, **README_zh.md** — Translations and improvements
- **ARCHITECTURE.md** — Architecture documentation updates
- **Code comments** — Improving inline documentation
- **Tutorials and guides** — Adding examples and how-to guides in the `docs/` directory
- **API documentation** — Documenting API endpoints and request/response formats
- **Changelog** — Keeping [CHANGELOG.md](./CHANGELOG.md) up to date

When updating documentation, please ensure all three language versions (English, Bahasa Indonesia, Chinese) are updated if the change applies to all versions.

---

## Community

### Contact the Maintainer

- **Owner**: Mulky Malikul Dhaher
- **Email**: [mulkymalikuldhaher@email.com](mailto:mulkymalikuldhaher@email.com)
- **GitHub**: [https://github.com/mulkymalikuldhrs](https://github.com/mulkymalikuldhrs)
- **Repository**: [https://github.com/mulkymalikuldhrs/AI-MultiColony-Ecosystem](https://github.com/mulkymalikuldhrs/AI-MultiColony-Ecosystem)

### Related Projects

- [HermesQuantOS](https://github.com/mulkymalikuldhrs/HermesQuantOS) — A production-ready quantitative trading OS built with this ecosystem

### Getting Help

If you need help with contributing or have questions about the project:

1. Check the existing [issues](https://github.com/mulkymalikuldhrs/AI-MultiColony-Ecosystem/issues) and [discussions](https://github.com/mulkymalikuldhrs/AI-MultiColony-Ecosystem/discussions)
2. Reach out via email at [mulkymalikuldhaher@email.com](mailto:mulkymalikuldhaher@email.com)

---

Thank you for contributing to AI-MultiColony-Ecosystem! Your efforts help build a more powerful and accessible multi-agent coordination platform for everyone.

---

*Made with ❤️ by the AI-MultiColony-Ecosystem community*

---

> ⚠️ **For Education Purpose Only** — This project is provided strictly for educational and research purposes. The authors and contributors assume **no responsibility or liability** for any damages, losses, or risks arising from the use of this software. **We do not bear any responsibility or risk** for how this software is used.

**Contact:** Mulky Malikul Dhaher | mulkymalikuldhaher@email.com

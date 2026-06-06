# Agentic AI System v2.0.0 - Autonomous Multi-Agent Intelligence

<div align="center">

![Agentic AI System Cover](web_interface/static/cover.svg)

![Version](https://img.shields.io/badge/version-2.0.0-blue.svg)
![Python](https://img.shields.io/badge/python-3.8+-green.svg)
![PWA](https://img.shields.io/badge/PWA-enabled-purple.svg)
![Security](https://img.shields.io/badge/security-AES256-red.svg)
![LLM](https://img.shields.io/badge/LLM-Multi--Provider-ff6b6b.svg)
![License](https://img.shields.io/badge/license-MIT-yellow.svg)
![Made with love](https://img.shields.io/badge/made%20with-❤️%20in%20Indonesia-red.svg)

**Multi-Agent AI System with PWA Support, Encrypted Credential Storage & Multi-LLM Gateway**

**Made in Indonesia by Mulky Malikul Dhaher**

</div>

---

## Project Overview

**Agentic AI System** is a multi-agent AI platform built with Flask. It provides a web-based interface for managing specialized AI agents, storing credentials securely, and routing requests through multiple LLM providers with automatic failover.

> **Note**: This is an early-stage project under active development. Some features described below are partially implemented or planned. See the [Known Limitations](#known-limitations) section for details.

---

## Features

### Multi-LLM Provider Gateway
- **7 LLM providers** with automatic failover: LLM7 (free), OpenRouter, DeepSeek, OpenAI, Anthropic, Google AI, Hugging Face
- **Intelligent failover** - automatic provider switching on failures
- **Cost optimization** - LLM7 free tier used as primary provider
- **Response caching** - improved efficiency and reduced costs

### Encrypted Credential Management
- **AES-256 encryption** via Fernet for stored credentials (requires `cryptography` package)
- **PBKDF2HMAC key derivation** with SHA-256 and 100,000 iterations
- **Master password required** via `CREDENTIAL_MASTER_PASSWORD` environment variable
- **10 platform integrations**: GitHub, Google, AWS, OpenAI, Anthropic, HuggingFace, Docker, Netlify, Vercel, Heroku
- **Audit logging** for credential access events
- **Web UI** for credential management at `/credentials`

### Agent Ecosystem
The system includes agents across two directories:

**`agents/` directory (24 agent modules)**:
- Core: CyberShell, Agent Maker, UI Designer, Dev Engine, Data Sync, Full Stack Dev, Prompt Generator
- Advanced: Meta Agent Creator, System Optimizer, Code Executor, AI Research Agent
- Security: Credential Manager, Authentication Agent, Bug Hunter Bot
- Infrastructure: LLM Provider Manager, Deploy Manager, Deployment Specialist, Data Sync
- Specialized: Marketing Agent, Knowledge Management Agent, Quality Control Specialist, AGI Colony Connector, Backup Colony System, Money Making Agent, Commander AGI

**`src/agents/` directory (12 agent modules)**:
- Agent Base, Advanced Agent Creator, Dynamic Agent Factory, Launcher Agent
- Agent 02-06: Meta Spawner, Planner, Executor, Designer, Specialist
- Deployment Agent, Output Handler, Web Automation Agent

### Progressive Web App (PWA)
- **Installable** on supported browsers
- **Service worker** for offline caching of static assets
- **Responsive design** - mobile, tablet, desktop

### Code Execution Environment
- **8+ Languages**: Python, JavaScript, TypeScript, Java, C++, Rust, Go, Bash
- **Real-time output** with syntax highlighting and error detection
- **Docker sandboxing** support for secure execution

---

## System Architecture

### Core Philosophy
```
Human Intent -> AI Understanding -> Agent Coordination -> Intelligent Execution -> Results
```

### Agent Network
```mermaid
graph TD
    A[Prompt Master] --> B[Meta Agent Creator]
    A --> C[LLM Provider Manager]
    B --> D[System Optimizer]
    B --> E[Code Executor]
    C --> F[Credential Manager]
    F --> G[Authentication Agent]
    D --> H[AI Research Agent]
    E --> I[CyberShell Agent]
```

### Technology Stack
- **Backend**: Python 3.8+, Flask, SQLite/PostgreSQL
- **Frontend**: HTML5, CSS3, JavaScript ES6+, Bootstrap 5
- **AI Integration**: Multi-provider LLM support with failover
- **Security**: AES-256 encryption (Fernet), PBKDF2HMAC key derivation
- **PWA**: Service Worker, Web App Manifest
- **Deployment**: Docker, Kubernetes configurations provided

---

## Quick Start Guide

### Prerequisites
```bash
Python 3.8+ (recommended: Python 3.11+)
4GB RAM minimum
Modern web browser (Chrome, Firefox, Safari, Edge)
```

### Installation
```bash
# Clone the repository
git clone https://github.com/mulkymalikuldhrs/AI-MultiColony-Ecosystem.git
cd AI-MultiColony-Ecosystem

# Install dependencies
pip install -r requirements.txt

# Setup environment
cp .env.example .env
# Edit .env with your API keys and configurations
# IMPORTANT: Set CREDENTIAL_MASTER_PASSWORD and SECRET_KEY before running
```

### Launch System
```bash
# Start the web interface
python web_interface/app.py

# Or use the system launcher
python start_system.py

# Or use the CLI
python cli.py start
```

### Access
- **Web Interface**: http://localhost:5000
- **Credential Management**: http://localhost:5000/credentials
- **Agent Dashboard**: http://localhost:5000/agents
- **LLM Providers**: http://localhost:5000/llm_providers

---

## Known Limitations

> This section documents areas where the project is still maturing. Contributions are welcome!

- **No built-in user authentication**: The web interface and API endpoints do not require login. For production, place behind a reverse proxy with authentication (see [SECURITY.md](SECURITY.md)).
- **Voice interaction**: Uses the Web Speech API (browser-dependent). Offline voice support depends on the browser's capabilities.
- **Money Making Agent**: This agent provides scaffolding for revenue-generating workflows (bug bounty, freelancing, etc.) but does not autonomously generate income. Claims of automatic revenue should not be taken literally.
- **SOC 2 / GDPR compliance**: The project uses industry-standard encryption but has not undergone formal compliance audits. "SOC 2 Type II ready" and "GDPR compliant" claims from previous documentation were inaccurate.
- **Performance benchmarks**: Previously published benchmark numbers were aspirational targets, not measured results. Actual performance depends on hardware, network, and LLM provider response times.
- **Some agents are scaffolding**: A few agent modules contain TODO placeholders and are not fully implemented (notably `agent_maker.py` has 4 unresolved TODOs, `money_making_agent.py` has 2).
- **Duplicate credential managers**: Both `agents/credential_manager.py` and `src/core/credential_manager.py` exist. The `src/core/` version is the more secure implementation (requires `CREDENTIAL_MASTER_PASSWORD` env var).
- **Many third-party imports not in requirements.txt**: Some agent code imports packages like `arxiv`, `boto3`, `cv2`, `playwright`, `selenium`, `paramiko`, etc. that are not listed in requirements.txt. These are optional and will fail gracefully if not installed.

---

## Configuration

### Environment Variables
```bash
# Core System
SECRET_KEY=your_secure_secret_key          # REQUIRED in production
CREDENTIAL_MASTER_PASSWORD=your_password   # REQUIRED for credential storage
FLASK_ENV=production
WEB_INTERFACE_PORT=5000
WEB_INTERFACE_HOST=0.0.0.0

# Database
DATABASE_URL=sqlite:///data/agentic.db
# For production: postgresql://user:pass@host:5432/db

# LLM Providers (at least one recommended)
LLM7_API_KEY=your_llm7_key
OPENROUTER_API_KEY=your_openrouter_key
OPENAI_API_KEY=your_openai_key
ANTHROPIC_API_KEY=your_anthropic_key
HUGGINGFACE_TOKEN=your_hf_token

# Platform Integrations (optional)
GITHUB_TOKEN=your_github_token
GOOGLE_CLIENT_ID=your_client_id
GOOGLE_CLIENT_SECRET=your_client_secret

# Agent Configuration
MAX_CONCURRENT_AGENTS=10
DEFAULT_AI_MODEL=gpt-3.5-turbo
```

See [.env.example](.env.example) for the complete list with documentation.

---

## API Documentation

### REST API Endpoints
```bash
# System Management
GET    /api/system/status           # System health and metrics

# Agent Management
GET    /api/agents                  # List all agents
POST   /api/task/submit             # Submit task to agent

# LLM Provider Management
GET    /api/llm/providers           # List LLM providers
POST   /api/llm/chat                # Chat completion with failover

# Credential Management
GET    /api/credentials             # List stored credentials (no passwords)
POST   /api/credentials             # Add new credential
DELETE /api/credentials/{id}        # Delete credential
POST   /api/credentials/test        # Test credential validity
```

---

## Deployment

### Docker
```bash
docker build -t agentic-ai:latest .
docker run -p 5000:5000 -v $(pwd)/data:/app/data agentic-ai:latest
```

### Docker Compose
```bash
docker-compose up -d
```

### Kubernetes
A `k8s-deployment.yaml` is provided for Kubernetes deployment.

> **Important**: Always set `SECRET_KEY` and `CREDENTIAL_MASTER_PASSWORD` as environment variables or secrets. Never use default values in production.

---

## Security

See [SECURITY.md](SECURITY.md) for the full security policy, including:
- Encryption architecture (AES-256 via Fernet)
- API key handling practices
- Code execution sandboxing
- Known security considerations
- Deployment security checklist

---

## Contributing

Contributions are welcome! Please follow these steps:

```bash
# 1. Fork the repository
git clone https://github.com/mulkymalikuldhrs/AI-MultiColony-Ecosystem.git

# 2. Create a feature branch
git checkout -b feature/your-feature

# 3. Make your changes and test
python -m pytest tests/

# 4. Commit with descriptive messages
git commit -m "feat: add your feature description"

# 5. Push and open a Pull Request
git push origin feature/your-feature
```

### Priority Areas for Contribution
- **Authentication**: Add user authentication to web interface and API
- **Agent completion**: Implement remaining TODO items in agent_maker.py
- **Tests**: Expand test coverage (currently minimal)
- **Documentation**: Improve API docs and usage examples
- **Security audit**: Independent security review of credential storage
- **Missing requirements**: Document optional dependencies for agent modules

---

## Creator

**Mulky Malikul Dhaher** - AI Engineer from Indonesia

[![GitHub](https://img.shields.io/badge/GitHub-@mulkymalikuldhrs-black.svg)](https://github.com/mulkymalikuldhrs)
[![Email](https://img.shields.io/badge/Email-Contact-red.svg)](mailto:mulkymalikuldhr@gmail.com)

---

## License

MIT License - see [LICENSE](LICENSE) for details.

Copyright (c) 2024 Mulky Malikul Dhaher

---

<div align="center">

**Made with love in Indonesia**

*Advancing the future of AI-human collaboration, one agent at a time.*

</div>

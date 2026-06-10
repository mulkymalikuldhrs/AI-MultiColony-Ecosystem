<a href="https://github.com/mulkymalikuldhrs/AI-MultiColony-Ecosystem">
  <img width="100%" src="https://capsule-render.vercel.app/api?type=waving&color=0:1a0a00,50:3d1f00,100:5c3000&height=220&section=header&text=AI%20MultiColony%20Ecosystem&fontSize=42&fontColor=f59e0b&animation=fadeIn&fontAlignY=30&desc=Multi-Agent%20Colony%20Coordination%20Platform&descSize=16&descColor=ef4444&descAlignY=50" />
</a>

<div align="center">

[![Typing SVG](https://readme-typing-svg.demolab.com?font=Fira+Code&size=20&duration=3000&pause=1000&color=f59e0b&center=true&vCenter=true&width=700&lines=40%2B+Specialized+AI+Agents;Multi-LLM+Gateway+%2B+Automatic+Failover;AES-256+Encrypted+Credential+Vault;Prometheus+%2B+Grafana+Monitoring;PWA+%2B+Docker+%2B+Kubernetes+Ready)](https://git.io/typing-svg)

<br/>

[![Python](https://img.shields.io/badge/Python-3.8+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-3-000000?style=for-the-badge&logo=flask&logoColor=white)](https://flask.palletsprojects.com/)
[![SQLite](https://img.shields.io/badge/SQLite-DB-003B57?style=for-the-badge&logo=sqlite&logoColor=white)](https://www.sqlite.org/)
[![AES-256](https://img.shields.io/badge/AES-256-Encryption-e74c3c?style=for-the-badge&logo=lock&logoColor=white)](https://cryptography.io/)
[![PWA](https://img.shields.io/badge/PWA-Ready-5A0FC8?style=for-the-badge&logo=pwa&logoColor=white)](https://web.dev/progressive-web-apps/)
[![Version](https://img.shields.io/badge/Version-2.0.0-brightgreen?style=for-the-badge&logo=semanticrelease&logoColor=white)](https://github.com/mulkymalikuldhrs/AI-MultiColony-Ecosystem/releases)
[![MIT License](https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge&logo=opensourceinitiative&logoColor=white)](LICENSE)

<br/>

[![GitHub Stars](https://img.shields.io/github/stars/mulkymalikuldhrs/AI-MultiColony-Ecosystem?style=for-the-badge&logo=github&color=gold)](https://github.com/mulkymalikuldhrs/AI-MultiColony-Ecosystem/stargazers)
[![GitHub Forks](https://img.shields.io/github/forks/mulkymalikuldhrs/AI-MultiColony-Ecosystem?style=for-the-badge&logo=github&color=blue)](https://github.com/mulkymalikuldhrs/AI-MultiColony-Ecosystem/fork)
[![GitHub Issues](https://img.shields.io/github/issues/mulkymalikuldhrs/AI-MultiColony-Ecosystem?style=for-the-badge&logo=github&color=red)](https://github.com/mulkymalikuldhrs/AI-MultiColony-Ecosystem/issues)
[![GitHub Last Commit](https://img.shields.io/github/last-commit/mulkymalikuldhrs/AI-MultiColony-Ecosystem?style=for-the-badge&logo=github&color=orange)](https://github.com/mulkymalikuldhrs/AI-MultiColony-Ecosystem/commits/main)

</div>

---

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Agent Ecosystem](#agent-ecosystem)
- [Architecture](#architecture)
- [Known Limitations](#known-limitations)
- [Honest Notes](#honest-notes)
- [Quick Start](#quick-start)
- [Configuration](#configuration)
- [API Documentation](#api-documentation)
- [Deployment](#deployment)
- [Security](#security)
- [Contributing](#contributing)
- [Disclaimer](#disclaimer)
- [License](#license)
- [Author](#author)

---

## Overview

AI MultiColony Ecosystem is a **multi-agent AI platform** built with Python and Flask that orchestrates 40+ specialized AI agents across a unified web interface. It features a multi-LLM gateway with automatic failover, AES-256 encrypted credential management, Prometheus + Grafana monitoring, and Progressive Web App support.

The platform organizes agents into colony-style categories — **Core**, **Security**, **Infrastructure**, **Development**, **Data & Knowledge**, **Business & Marketing**, **Quality**, and **Integration** — enabling coordinated multi-agent workflows through a central dispatcher.

> **Transparency Notice**: This is an **early-stage project** under active development. Some agent modules contain `TODO` placeholders and are not fully implemented. The "Money Making Agent" provides workflow scaffolding for revenue-generating tasks but does **not** autonomously generate income. No built-in user authentication exists — a reverse proxy is required for production deployments. See [Known Limitations](#known-limitations) and [Honest Notes](#honest-notes) for full details.

---

## Features

### 🤖 40+ Specialized AI Agents
A diverse colony of agents spanning core orchestration, security auditing, infrastructure management, code generation, knowledge curation, business operations, and integration (GitHub, Voice, Web3, Monitoring) — each designed for a focused domain.

### 🔀 Multi-LLM Gateway with Failover
Route requests through **7 LLM providers** with automatic failover: LLM7 (free tier), OpenRouter, DeepSeek, OpenAI, Anthropic, Google AI, and Hugging Face. If one provider is unavailable, the gateway transparently falls back to the next.

### 🔐 AES-256 Encrypted Credential Vault
All stored credentials (API keys, tokens, secrets) are encrypted at rest using **AES-256 via Fernet**, with keys derived through **PBKDF2HMAC** at 100,000 iterations. The master password never leaves the server.

### 📱 Progressive Web App (PWA)
Installable as a native-like app on desktop and mobile. Includes a service worker for offline caching and a web app manifest for home screen installation.

### 💻 Multi-Language Code Execution
Execute code in **8+ programming languages** with optional Docker sandboxing for secure, isolated execution environments.

### 🌐 Web Dashboard
A Flask-based management interface for agent configuration, credential storage, LLM provider management, and real-time agent status monitoring.

### 🔄 Colony Coordination
Agents communicate through a central dispatch system, enabling multi-step workflows where the output of one agent feeds into the next — forming coordinated colony behaviors.

### 🐳 Container-Ready
Full Docker, Docker Compose, and Kubernetes deployment support with health checks, volume mounts, and scalable configurations.

### 📊 Production Monitoring
Prometheus + Grafana observability stack with preconfigured scrape targets for the Flask app, PostgreSQL, Redis, Nginx, and Node Exporter. Agent Watcher provides agent-level health monitoring with alerting and auto-restart capabilities.

---

## Agent Ecosystem

### 🧠 Core Agents
| Agent | Description |
|-------|-------------|
| **CyberShell** | Primary orchestration agent and system coordinator |
| **Agent Maker** | Dynamically creates and configures new agents |
| **Dev Engine** | Development workflow automation and code generation |
| **Colony Coordinator** | Manages inter-agent communication and task routing |
| **System Monitor** | Tracks system health, resource usage, and agent status |

### 🛡️ Security Agents
| Agent | Description |
|-------|-------------|
| **Bug Hunter** | Scans code and infrastructure for vulnerabilities |
| **Credential Manager** | Securely stores and retrieves encrypted credentials |
| **Security Scanner** | Performs security audits and penetration testing |
| **Vulnerability Analyzer** | Classifies and prioritizes discovered vulnerabilities |
| **Auth Guardian** | Monitors and enforces access control policies |

### ⚙️ Infrastructure Agents
| Agent | Description |
|-------|-------------|
| **Deploy Manager** | Handles application deployment pipelines |
| **LLM Provider Manager** | Configures and manages LLM provider connections |
| **Infrastructure Monitor** | Tracks server health, uptime, and performance metrics |
| **Backup Manager** | Schedules and manages data backups |
| **Network Manager** | Network configuration and connectivity monitoring |
| **Resource Optimizer** | Allocates and optimizes compute resources |

### 💻 Development Agents
| Agent | Description |
|-------|-------------|
| **Code Generator** | Generates code from natural language specifications |
| **Code Reviewer** | Reviews code for quality, style, and correctness |
| **Test Runner** | Executes test suites and reports coverage |
| **Documentation Generator** | Creates and maintains project documentation |
| **Refactoring Agent** | Suggests and applies code refactoring improvements |
| **Version Control Agent** | Manages Git operations and branch strategies |

### 📊 Data & Knowledge Agents
| Agent | Description |
|-------|-------------|
| **Knowledge Manager** | Curates and retrieves organizational knowledge |
| **Data Analyzer** | Processes and analyzes datasets |
| **Research Agent** | Conducts automated research and information gathering |
| **Data Pipeline Agent** | Manages ETL workflows and data transformations |
| **Search Agent** | Performs intelligent search across indexed content |
| **Memory Agent** | Manages conversation history and context persistence |

### 💼 Business & Marketing Agents
| Agent | Description |
|-------|-------------|
| **Marketing Agent** | Creates and manages marketing content strategies |
| **SEO Agent** | Optimizes content for search engine visibility |
| **Content Writer** | Generates blog posts, copy, and marketing materials |
| **Social Media Agent** | Manages social media posting and engagement |
| **Money Making Agent** | ⚠️ Workflow scaffolding for revenue tasks — **not** autonomous income generation |
| **Analytics Agent** | Tracks and reports on business metrics |

### ✅ Quality Agents
| Agent | Description |
|-------|-------------|
| **Quality Controller** | Ensures output meets quality standards |
| **Compliance Checker** | Validates outputs against compliance requirements |
| **Performance Tester** | Runs performance benchmarks and load tests |
| **Integration Tester** | Tests integration points between agents and services |

### 🔗 Integration Agents
| Agent | Description |
|-------|-------------|
| **GitHub Agent** | GitHub API integration — repo management, PRs, issues, file operations, CI status, code search |
| **Voice Agent** | Speech-to-text (Whisper), text-to-speech, voice command parsing and routing, audio processing |
| **Web3 Plugin** | Multi-chain blockchain queries (read-only) — ERC-20, DeFi reads, gas estimation, ENS resolution |
| **Agent Watcher** | Agent health monitoring, heartbeat checks, auto-restart, alerting, and health reports |

> **Note**: Some agents listed above contain `TODO` placeholders and are under active development. Agent availability and functionality may vary. See [Known Limitations](#known-limitations) for details.

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                        AI MultiColony Ecosystem                     │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌──────────────────────┐    ┌──────────────────────────────────┐  │
│  │   PWA Frontend       │    │   Web Dashboard (Flask/Jinja2)   │  │
│  │  ┌────────────────┐  │    │  ┌────────┐ ┌────────┐ ┌──────┐ │  │
│  │  │ Service Worker │  │    │  │ Agents │ │ Creds  │ │ LLM  │ │  │
│  │  │ Web Manifest  │  │    │  │ Panel  │ │ Vault  │ │ Config│ │  │
│  │  └────────────────┘  │    │  └────────┘ └────────┘ └──────┘ │  │
│  └──────────┬───────────┘    └──────────────┬───────────────────┘  │
│             │                               │                      │
│             └──────────────┬────────────────┘                      │
│                            │                                       │
│                   ┌────────▼────────┐                              │
│                   │  Colony         │                              │
│                   │  Coordinator    │                              │
│                   │  (Dispatcher)   │                              │
│                   └────────┬────────┘                              │
│                            │                                       │
│          ┌─────────────────┼─────────────────┐                    │
│          │                 │                  │                    │
│  ┌───────▼──────┐ ┌───────▼──────┐ ┌────────▼─────┐             │
│  │  Core Colony │ │ Sec Colony   │ │ Infra Colony │  ...         │
│  │ ┌──────────┐ │ │ ┌──────────┐ │ │ ┌──────────┐ │             │
│  │ │CyberShell│ │ │ │BugHunter │ │ │ │DeployMgr │ │             │
│  │ │AgentMaker│ │ │ │CredMgmt  │ │ │ │LLMProvMgr│ │             │
│  │ │DevEngine │ │ │ │SecScanner│ │ │ │InfraMon  │ │             │
│  │ └──────────┘ │ │ └──────────┘ │ │ └──────────┘ │             │
│  └───────┬──────┘ └───────┬──────┘ └────────┬─────┘             │
│          │                │                  │                    │
│          └─────────────────┼─────────────────┘                    │
│                            │                                       │
│                   ┌────────▼────────┐                              │
│                   │  Multi-LLM      │                              │
│                   │  Gateway        │                              │
│                   │  (Failover)     │                              │
│                   └────────┬────────┘                              │
│                            │                                       │
│     ┌──────┬──────┬───────┼───────┬──────┬──────┬──────┐         │
│     │LLM7  │Open  │Deep   │OpenAI │Anthro│Google│Hugg  │         │
│     │(Free)│Routr │Seek   │       │pic   │ AI   │Face  │         │
│     └──────┴──────┴───────┴───────┴──────┴──────┴──────┘         │
│                                                                     │
│  ┌──────────────────────┐    ┌──────────────────────────────────┐  │
│  │  Credential Vault    │    │   SQLite Database               │  │
│  │  AES-256 / Fernet   │    │   (Agents, Config, Logs)        │  │
│  │  PBKDF2HMAC 100k    │    │                                  │  │
│  └──────────────────────┘    └──────────────────────────────────┘  │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Known Limitations

> These are important constraints inherited from the original project. Please review before deploying.

| Limitation | Impact | Workaround |
|-----------|--------|------------|
| **No built-in authentication** | Anyone with network access can use the platform | Basic auth endpoints available; use reverse proxy (Nginx) with HTTP Basic Auth or OAuth |
| **Duplicate credential managers** | Two implementations exist — potential confusion | Use the `src/core/` version which is the more secure implementation |
| **Incomplete agent implementations** | Some agents contain `TODO` placeholders | Check agent source before relying on functionality |
| **Missing imports in requirements.txt** | Some third-party imports are not listed | Agents fail gracefully; install missing packages as needed |
| **"Money Making Agent" is scaffolding only** | Does not autonomously generate income | Use it as a template for building custom revenue workflows |
| **SQLite for production** | Not ideal for high-concurrency workloads | Consider PostgreSQL for production deployments |
| **Single-process Flask** | Not suitable for high-traffic production | Use Gunicorn/uWSGI with multiple workers |
| **Web3 is read-only** | Cannot sign or broadcast transactions | By design for safety; implement separate signing service if needed |

---

## Honest Notes

> We believe in radical transparency. Here are important clarifications about this project.

1. **Early-stage project** — Some agents contain `TODO` placeholders and are not fully implemented. The agent list represents the intended architecture, not necessarily the current state of every module.

2. **No built-in user authentication** — The platform does not include user login, session management, or role-based access control. Basic auth API endpoints are now available with rate limiting. For production deployments, use a reverse proxy (e.g., Nginx with `auth_basic`, Traefik with forward auth, or Cloudflare Access).

3. **"Money Making Agent" is workflow scaffolding** — This agent provides templates and workflow structures for revenue-related tasks. It does **not** autonomously generate income, trade assets, or make financial decisions. Any revenue generation requires significant human configuration and oversight.

4. **Missing third-party imports** — Some agents import optional packages that are not listed in `requirements.txt`. These agents fail gracefully (catching `ImportError`) but will not function until the missing dependency is installed.

5. **Duplicate credential managers** — Two credential manager implementations exist in the codebase. The version in `src/core/` uses the more secure AES-256/Fernet implementation with PBKDF2HMAC key derivation. Prefer this version for production use.

---

## Quick Start

### Prerequisites

- Python 3.8 or higher
- pip package manager
- (Optional) Docker for containerized deployment

### Installation

```bash
# Clone the repository
git clone https://github.com/mulkymalikuldhrs/AI-MultiColony-Ecosystem.git
cd AI-MultiColony-Ecosystem

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env — set CREDENTIAL_MASTER_PASSWORD and SECRET_KEY (see Configuration below)

# Launch the platform
python web_interface/app.py
```

The dashboard will be available at **http://localhost:5000**.

### Verify Installation

```bash
# Check that the Flask app starts correctly
python -c "from web_interface.app import app; print('OK')"

# Verify credential encryption is working
python -c "from src.core.credential_manager import CredentialManager; print('Vault OK')"
```

---

## Configuration

All configuration is managed through environment variables and the `.env` file.

### `.env` Template

```env
# ============================================
# AI MultiColony Ecosystem Configuration
# ============================================

# --- Core Settings ---
SECRET_KEY=your-super-secret-flask-key-change-this
CREDENTIAL_MASTER_PASSWORD=your-master-password-for-aes256-encryption
FLASK_ENV=development
FLASK_DEBUG=1
PORT=5000
HOST=0.0.0.0

# --- Database ---
DATABASE_PATH=data/multicolony.db

# --- LLM Provider API Keys ---
# Only configure the providers you intend to use.
# The gateway will skip unconfigured providers and failover to the next.

LLM7_API_KEY=                    # Free tier — no key required
OPENROUTER_API_KEY=              # https://openrouter.ai/
DEEPSEEK_API_KEY=                # https://platform.deepseek.com/
OPENAI_API_KEY=                  # https://platform.openai.com/
ANTHROPIC_API_KEY=               # https://console.anthropic.com/
GOOGLE_AI_API_KEY=               # https://makersuite.google.com/
HUGGINGFACE_API_KEY=             # https://huggingface.co/settings/tokens

# --- Default LLM Settings ---
DEFAULT_LLM_PROVIDER=llm7
DEFAULT_LLM_MODEL=default
LLM_TEMPERATURE=0.7
LLM_MAX_TOKENS=2048

# --- Code Execution ---
ENABLE_CODE_EXECUTION=true
DOCKER_SANDBOX_ENABLED=false
DOCKER_SANDBOX_IMAGE=python:3.11-slim

# --- PWA Settings ---
PWA_CACHE_NAME=multicolony-v2
PWA_OFFLINE_PAGE=/offline.html

# --- Security ---
CREDENTIAL_ENCRYPTION_ITERATIONS=100000
SESSION_TIMEOUT=3600
```

### Key Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `SECRET_KEY` | ✅ | Flask session signing key — use a strong random string |
| `CREDENTIAL_MASTER_PASSWORD` | ✅ | Master password for AES-256 credential encryption |
| `LLM7_API_KEY` | ❌ | Free-tier LLM provider (no key required for basic use) |
| `OPENAI_API_KEY` | ❌ | OpenAI GPT models |
| `ANTHROPIC_API_KEY` | ❌ | Claude models |
| `DOCKER_SANDBOX_ENABLED` | ❌ | Enable Docker isolation for code execution (default: `false`) |

---

## API Documentation

### Base URL

```
http://localhost:5000/api
```

### Agent Management

#### List All Agents

```http
GET /api/agents
```

**Response:**
```json
{
  "agents": [
    {
      "id": "cybershell",
      "name": "CyberShell",
      "category": "core",
      "status": "active",
      "description": "Primary orchestration agent"
    }
  ]
}
```

#### Get Agent Details

```http
GET /api/agents/{agent_id}
```

#### Execute Agent Task

```http
POST /api/agents/{agent_id}/execute
Content-Type: application/json

{
  "task": "Scan the codebase for security vulnerabilities",
  "parameters": {
    "severity": "high",
    "language": "python"
  }
}
```

**Response:**
```json
{
  "task_id": "task_abc123",
  "agent_id": "bug_hunter",
  "status": "running",
  "created_at": "2025-01-15T10:30:00Z"
}
```

### LLM Gateway

#### List Available Providers

```http
GET /api/llm/providers
```

#### Query LLM

```http
POST /api/llm/query
Content-Type: application/json

{
  "prompt": "Explain multi-agent systems",
  "provider": "openai",
  "model": "gpt-4",
  "temperature": 0.7,
  "max_tokens": 1024
}
```

**Response:**
```json
{
  "response": "Multi-agent systems are...",
  "provider": "openai",
  "model": "gpt-4",
  "tokens_used": 856,
  "failover": false
}
```

### Credential Management

#### Store Credential

```http
POST /api/credentials
Content-Type: application/json

{
  "name": "my_api_key",
  "value": "sk-xxxxxxxxxxxx",
  "category": "api_keys"
}
```

#### Retrieve Credential

```http
GET /api/credentials/{name}
```

#### Delete Credential

```http
DELETE /api/credentials/{name}
```

### Code Execution

#### Execute Code

```http
POST /api/code/execute
Content-Type: application/json

{
  "language": "python",
  "code": "print('Hello from MultiColony!')",
  "timeout": 30
}
```

**Response:**
```json
{
  "stdout": "Hello from MultiColony!\n",
  "stderr": "",
  "exit_code": 0,
  "execution_time": 0.12
}
```

---

## Deployment

### Docker

```bash
# Build the image
docker build -t multicolony-ecosystem .

# Run the container
docker run -d \
  --name multicolony \
  -p 5000:5000 \
  -e SECRET_KEY=your-secret-key \
  -e CREDENTIAL_MASTER_PASSWORD=your-master-password \
  -v multicolony-data:/app/data \
  multicolony-ecosystem
```

### Docker Compose

```yaml
version: '3.8'

services:
  multicolony:
    build: .
    container_name: multicolony-ecosystem
    ports:
      - "5000:5000"
    environment:
      - SECRET_KEY=${SECRET_KEY}
      - CREDENTIAL_MASTER_PASSWORD=${CREDENTIAL_MASTER_PASSWORD}
      - FLASK_ENV=production
      - DOCKER_SANDBOX_ENABLED=true
    volumes:
      - multicolony-data:/app/data
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:5000/"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

volumes:
  multicolony-data:
    driver: local
```

```bash
# Start the stack
docker compose up -d

# View logs
docker compose logs -f multicolony

# Stop
docker compose down
```

### Kubernetes

```yaml
# deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: multicolony-ecosystem
  labels:
    app: multicolony
spec:
  replicas: 2
  selector:
    matchLabels:
      app: multicolony
  template:
    metadata:
      labels:
        app: multicolony
    spec:
      containers:
        - name: multicolony
          image: multicolony-ecosystem:latest
          ports:
            - containerPort: 5000
          env:
            - name: SECRET_KEY
              valueFrom:
                secretKeyRef:
                  name: multicolony-secrets
                  key: secret-key
            - name: CREDENTIAL_MASTER_PASSWORD
              valueFrom:
                secretKeyRef:
                  name: multicolony-secrets
                  key: master-password
            - name: FLASK_ENV
              value: "production"
          resources:
            requests:
              memory: "256Mi"
              cpu: "250m"
            limits:
              memory: "512Mi"
              cpu: "500m"
          livenessProbe:
            httpGet:
              path: /
              port: 5000
            initialDelaySeconds: 30
            periodSeconds: 30
          readinessProbe:
            httpGet:
              path: /
              port: 5000
            initialDelaySeconds: 10
            periodSeconds: 10
          volumeMounts:
            - name: data
              mountPath: /app/data
      volumes:
        - name: data
          persistentVolumeClaim:
            claimName: multicolony-pvc
---
apiVersion: v1
kind: Service
metadata:
  name: multicolony-service
spec:
  selector:
    app: multicolony
  ports:
    - protocol: TCP
      port: 80
      targetPort: 5000
  type: ClusterIP
---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: multicolony-pvc
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 1Gi
```

```bash
# Create secrets
kubectl create secret generic multicolony-secrets \
  --from-literal=secret-key='your-secret-key' \
  --from-literal=master-password='your-master-password'

# Deploy
kubectl apply -f deployment.yaml

# Check status
kubectl get pods -l app=multicolony
```

### Production Checklist

- [ ] Set strong `SECRET_KEY` and `CREDENTIAL_MASTER_PASSWORD`
- [x] Use a reverse proxy (Nginx/Traefik) with TLS termination — `nginx/nginx.conf` provided
- [ ] Enable HTTP Basic Auth or OAuth at the proxy level
- [ ] Set `FLASK_ENV=production` and `FLASK_DEBUG=0`
- [ ] Use Gunicorn with multiple workers: `gunicorn -w 4 -b 0.0.0.0:5000 web_interface.app:app`
- [ ] Enable Docker sandboxing for code execution
- [ ] Configure regular database backups
- [x] Set up monitoring and alerting — Prometheus + Grafana stack configured

---

## Security

### Credential Encryption

All credentials stored in the vault are encrypted at rest using **AES-256** via the Fernet symmetric encryption scheme:

- **Key Derivation**: PBKDF2HMAC with SHA-256
- **Iterations**: 100,000 (configurable via `CREDENTIAL_ENCRYPTION_ITERATIONS`)
- **Salt**: Randomly generated per encryption key
- **Master Password**: Never stored — derived into an encryption key at runtime

```python
# Encryption flow (simplified)
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.fernet import Fernet
import base64

kdf = PBKDF2HMAC(
    algorithm=hashes.SHA256(),
    length=32,
    salt=salt,
    iterations=100000,
)
key = base64.urlsafe_b64encode(kdf.derive(master_password.encode()))
fernet = Fernet(key)
encrypted = fernet.encrypt(credential_value.encode())
```

### Security Considerations

| Area | Status | Recommendation |
|------|--------|---------------|
| Encryption at rest | ✅ AES-256 | Ensure `CREDENTIAL_MASTER_PASSWORD` is strong |
| TLS/HTTPS | ✅ Nginx config provided | Use `nginx/nginx.conf` with TLS termination |
| Authentication | ⚠️ Basic auth endpoints | Use reverse proxy with HTTP Basic Auth / OAuth |
| Code execution sandboxing | ⚠️ Optional | Enable `DOCKER_SANDBOX_ENABLED=true` in production |
| Rate limiting | ✅ Nginx-level | Configure via `nginx/nginx.conf` (30r/s general, 10r/s API, 5r/s auth) |
| Input validation | ⚠️ Partial | Review agent inputs before production use |
| CORS | ✅ Configurable | Set `CORS_ALLOWED_ORIGINS` in production |
| Monitoring | ✅ Prometheus + Grafana | See `monitoring/prometheus.yml` |

---

## Contributing

Contributions are welcome! This project has specific areas where help is most needed.

### Priority Areas

| Priority | Area | Description |
|----------|------|-------------|
| 🔴 High | **Agent implementations** | Complete `TODO` placeholders in partially implemented agents |
| 🔴 High | **Missing requirements.txt entries** | Identify and add missing third-party dependencies |
| 🔴 High | **Test coverage** | Add unit and integration tests for new and existing agents |
| 🟡 Medium | **Authentication** | Add optional built-in user authentication module |
| 🟡 Medium | **Deduplicate credential managers** | Consolidate into a single, well-tested implementation |
| 🟡 Medium | **Prometheus alerting rules** | Add alerting rules for critical service failures |
| 🟡 Medium | **Grafana dashboards** | Create pre-built dashboard configurations |
| 🟢 Low | **Documentation** | Improve agent documentation and usage examples |
| 🟢 Low | **PostgreSQL support** | Add database backend option beyond SQLite |
| 🟢 Low | **Web3 write operations** | Add optional transaction signing with proper security controls |

### How to Contribute

1. **Fork** the repository
2. Create a **feature branch** (`git checkout -b feature/amazing-feature`)
3. **Commit** your changes (`git commit -m 'Add amazing feature'`)
4. **Push** to the branch (`git push origin feature/amazing-feature`)
5. Open a **Pull Request**

### Development Setup

```bash
# Clone and install in development mode
git clone https://github.com/mulkymalikuldhrs/AI-MultiColony-Ecosystem.git
cd AI-MultiColony-Ecosystem
pip install -r requirements.txt
pip install -r requirements-dev.txt  # If available

# Run in debug mode
FLASK_ENV=development FLASK_DEBUG=1 python web_interface/app.py
```

### Code Style

- Follow PEP 8 for Python code
- Use descriptive variable and function names
- Add docstrings to public functions and classes
- Handle `ImportError` gracefully for optional dependencies

---

## Disclaimer

**For Education and Research Purpose Only**

This project is provided strictly for educational and research purposes. The authors and contributors assume **no responsibility or liability** for any damages, losses, or risks arising from the use of this software.

**Important:**
- **We do not guarantee** that any agent will function as described, especially those marked with `TODO` placeholders.
- **We do not bear any responsibility or risk** for how this software is used.
- **The "Money Making Agent"** is workflow scaffolding only — it does not generate income autonomously and should not be relied upon for financial decisions.
- **No warranty** is provided, express or implied. Use at your own risk.

---

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

[![GitHub](https://img.shields.io/badge/GitHub-mulkymalikuldhrs-181717?style=for-the-badge&logo=github&logoColor=white)](https://github.com/mulkymalikuldhrs)
[![Email](https://img.shields.io/badge/Email-mulkymalikudhr%40mail.com-D14836?style=for-the-badge&logo=gmail&logoColor=white)](mailto:mulkymalikudhr@mail.com)

---

<a href="https://github.com/mulkymalikuldhrs/AI-MultiColony-Ecosystem">
  <img width="100%" src="https://capsule-render.vercel.app/api?type=waving&color=100:5c3000,50:3d1f00,0:1a0a00&height=100&section=footer" />
</a>

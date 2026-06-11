# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.1.0] - 2026-03-04

### Added
- **GitHub Agent** (`agents/github_agent.py`): Full GitHub API integration with async operations, repository management, PR/issue creation, file operations, CI status, code search, and rate-limit-aware request handling
- **Voice Agent** (`agents/voice_agent.py`): Speech-to-text (OpenAI Whisper + local fallback), text-to-speech (OpenAI TTS + gTTS/pyttsx3 fallbacks), voice command parsing and routing to other agents, audio file processing (metadata, validation, conversion)
- **Web3 Plugin** (`agents/web3_plugin.py`): Multi-chain blockchain interactions (Ethereum, Polygon, BSC, Arbitrum, Optimism, Avalanche), ERC-20 token queries, DeFi protocol reads (Uniswap V3, Aave V3, Compound V3), gas estimation, ENS resolution — all read-only by default for safety
- **Agent Watcher** (`agents/agent_watcher.py`): Comprehensive agent health monitoring system with heartbeat checks, error tracking, auto-restart capabilities, alerting (info/warning/critical), health report generation, and state persistence
- **Prometheus monitoring** (`monitoring/prometheus.yml`): Full scrape configuration for Flask app, PostgreSQL, Redis, Nginx, Node Exporter, and Grafana self-monitoring with 15s intervals
- **Nginx production configuration** (`nginx/nginx.conf`): Reverse proxy with HTTP/2, SSL/TLS, WebSocket support (Socket.IO), rate limiting (general/API/auth zones), security headers, static file caching, gzip compression, and JSON access logs
- **Basic auth API endpoints**: Authentication endpoints for login/register/forgot-password with stricter rate limiting at the Nginx level
- **CORS configuration**: Configurable via `CORS_ALLOWED_ORIGINS` environment variable with Nginx-level CORS headers for JSON responses
- **Comprehensive test suite** (`tests/test_comprehensive.py`, `tests/test_agents.py`): Expanded test coverage for new agents and existing functionality
- **Community files restored from main branch**: Issue templates, PR template, and CODE_OF_CONDUCT.md

### Fixed
- Removed all `TODO` placeholders across agent modules — replaced with working implementations or graceful degradation paths
- Replaced bare `pass` statements in agent methods with meaningful implementations or proper `NotImplementedError` raises
- Fixed missing imports in agent modules — all agents now handle `ImportError` gracefully for optional dependencies
- Fixed import path issues in agent discovery and registration
- Corrected credential manager initialization order to avoid crashes when cryptography is not installed

### Changed
- Agent ecosystem expanded from 36+ to 40+ agents with the addition of GitHub Agent, Voice Agent, Web3 Plugin, and Agent Watcher
- Monitoring infrastructure now includes Prometheus + Grafana stack for production observability
- Deployment configurations updated with Nginx reverse proxy for production-grade security and performance
- Docker Compose configuration improved with health checks, resource limits, and proper service dependencies

## [Unreleased]

### Added
- Initial documentation standardization
- Standard README.md with contributor guidelines, contact, and disclaimers
- CONTRIBUTING.md for community onboarding
- LICENSE (MIT)

---

> Maintained by **Mulky Malikul Dhaher** | [mulkymalikuldhaher@email.com](mailto:mulkymalikuldhaher@email.com)

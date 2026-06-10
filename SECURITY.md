# Security Policy

## Reporting Security Vulnerabilities

**Please do not report security vulnerabilities through public GitHub issues.**

Instead, please report them via email to: mulkymalikuldhhr@gmail.com

You should receive a response within 48 hours. If for some reason you do not, please follow up via the same email.

## Security Architecture

### Encryption
- **AES-256** encryption for all stored credentials via Fernet (cryptography library)
- **PBKDF2HMAC** key derivation with SHA-256 and 100,000 iterations
- **Random salt** stored in `data/credentials.salt` (never committed to git)
- Master password required via `CREDENTIAL_MASTER_PASSWORD` environment variable

### API Keys
- All LLM provider API keys are loaded from **environment variables only**
- Never hardcode API keys in source code
- Use `.env` file for local development (`.env` is in `.gitignore`)
- `.env.example` is provided as a template (contains no real keys)

### Web Interface
- Flask `SECRET_KEY` must be set in production via environment variable
- If not set, a random key is generated (sessions will not persist across restarts)
- CORS is configurable via `CORS_ALLOWED_ORIGINS` environment variable

### Authentication (New)
- Basic auth API endpoints are now available at `/api/auth`, `/api/login`, `/api/register`, `/api/forgot-password`
- Auth endpoints have stricter rate limiting at the Nginx level (5 requests/second per IP)
- For production, use a reverse proxy (Nginx) with HTTP Basic Auth or OAuth
- Consider using OAuth2, JWT, or API key-based authentication for API access

### CORS Configuration
- CORS is configurable via the `CORS_ALLOWED_ORIGINS` environment variable
- Set to a comma-separated list of allowed origins (e.g., `https://example.com,https://app.example.com`)
- If not set, CORS defaults to allowing all origins — **restrict this in production**
- Nginx also applies CORS headers for JSON API responses

### Rate Limiting (New)
- Rate limiting is enforced at the Nginx reverse proxy level:
  - **General requests**: 30 requests/second per IP (burst: 40)
  - **API endpoints** (`/api/`): 10 requests/second per IP (burst: 20)
  - **Auth endpoints** (`/api/auth`, `/api/login`, etc.): 5 requests/second per IP (burst: 5)
  - **Connection limiting**: 50 concurrent connections per IP
- Rate-limited requests return HTTP 429 (Too Many Requests)
- Rate limiting zones use 10MB of shared memory each

### Nginx Reverse Proxy (New)
- Production deployments should use the provided Nginx configuration (`nginx/nginx.conf`)
- Features:
  - **TLS 1.2/1.3** with modern cipher suite (Mozilla Intermediate)
  - **HTTP/2** support
  - **Security headers**: HSTS, CSP, X-Frame-Options, X-Content-Type-Options, Referrer-Policy, Permissions-Policy
  - **WebSocket support** for Socket.IO real-time communication
  - **Gzip compression** for text-based content
  - **Static file caching** with aggressive expiry (30-90 days)
  - **JSON structured access logs** for monitoring and analysis
  - **Hidden file access denied** (`.env`, `.git`, etc.)
  - **Metrics endpoint** restricted to internal Docker network only

## Known Security Considerations

### Code Execution Agent
The Code Executor agent can execute arbitrary code. In production:
1. **Always use Docker mode** (`environment: 'docker'`) for code execution
2. Docker containers run with network disabled, memory limits, and CPU limits
3. Local execution mode should only be used in trusted development environments
4. Never expose the code execution API to untrusted users without authentication

### Web3 Plugin Agent (New)
The Web3 Plugin interacts with blockchain networks. Important security notes:
1. **Read-only by default** — all built-in actions use `eth_call` (view/pure functions), not `eth_sendTransaction`
2. **No private key management** — the agent does not store, manage, or access private keys
3. **No transaction signing** — the agent cannot sign or broadcast transactions
4. **RPC endpoint configuration** — RPC URLs are loaded from environment variables; use trusted RPC providers
5. **Gas estimation only** — `estimate_gas` returns cost estimates but cannot execute transactions
6. **DeFi reads are view-only** — Uniswap V3, Aave V3, and Compound V3 interactions are limited to reading contract state
7. **CoinGecko API** — price fetches use the free CoinGecko API; no authentication required but rate-limited
8. **Multi-chain support** — 8 networks configured by default (Ethereum, Goerli, Sepolia, Polygon, BSC, Arbitrum, Optimism, Avalanche)

If you need transaction signing capabilities, you must:
- Implement a separate secure signing service
- Never store private keys in the credential vault or environment variables
- Use hardware wallets or HSMs for key management
- Audit all transaction-related code thoroughly

### GitHub Agent (New)
The GitHub Agent makes authenticated requests to the GitHub API:
1. **Token-based auth** — uses `GITHUB_TOKEN` environment variable for authentication
2. **Rate limit awareness** — tracks GitHub API rate limits and waits when approaching limits
3. **Token scope** — the agent can only perform actions allowed by the token's scopes
4. **Write operations** — file creation, PR creation, and issue creation require a token with appropriate scopes
5. **Minimum scope recommendation** — use a fine-grained personal access token with least-privilege access

### Voice Agent (New)
The Voice Agent processes audio data:
1. **Audio data handling** — audio data is processed in-memory and cached temporarily; not persisted to disk by default
2. **Transcription cache** — transcriptions are cached by audio hash (SHA-256) with a 500-entry limit
3. **API key exposure** — OpenAI API key is used server-side only; never sent to the client
4. **External API calls** — STT/TTS calls go to OpenAI's API (or local fallback); audio data is transmitted to the configured provider

### Agent Watcher (New)
The Agent Watcher monitors agent health:
1. **Health state persistence** — health state is saved to `data/health_reports/watcher_state.json`; ensure this directory is not publicly accessible
2. **Auto-restart capability** — the watcher can re-instantiate agents; this is limited by configurable cooldown and max attempts
3. **Alert log** — alerts are stored in-memory (bounded to 1000 entries) and persisted with state; may contain sensitive error details

### Authentication
- Basic auth API endpoints are now available with stricter rate limiting
- For full production security, place behind a reverse proxy (Nginx) with authentication
- Consider using OAuth2, JWT, or API key-based authentication
- The `/api/` endpoints are designed to be private network only
- Nginx configuration includes HTTP Basic Auth support (commented out by default)

### Docker Compose Defaults
- Default passwords in `docker-compose.yml` are placeholders (`changeme_secure_password`)
- **You MUST change all default passwords** before deploying
- Set these via `.env` file or environment variables

## Security Best Practices for Deployment

1. **Always set `SECRET_KEY`** to a strong random value
2. **Always set `CREDENTIAL_MASTER_PASSWORD`** to a strong unique password
3. **Use HTTPS** in production (via Nginx reverse proxy with TLS termination)
4. **Restrict network access** — do not expose ports directly to the internet
5. **Keep dependencies updated** — run `pip audit` regularly
6. **Review API key permissions** — use least-privilege principle
7. **Enable audit logging** for credential access
8. **Regularly rotate** API keys and passwords
9. **Configure `CORS_ALLOWED_ORIGINS`** — restrict to your actual domain(s) in production
10. **Enable Nginx rate limiting** — use the provided `nginx/nginx.conf` for production
11. **Restrict metrics endpoint** — Prometheus `/metrics` should only be accessible from internal networks
12. **Monitor with Agent Watcher** — set up periodic health checks to detect anomalies
13. **Review Web3 RPC providers** — use trusted, authenticated RPC endpoints when possible
14. **Limit GitHub token scope** — use fine-grained PATs with minimum required permissions
15. **Secure health report directory** — ensure `data/health_reports/` is not publicly accessible

## Dependency Security

Run security audits on dependencies:
```bash
pip install pip-audit
pip-audit -r requirements.txt
```

### Duplicate Credential Managers
There are two credential manager implementations:
- `agents/credential_manager.py` - `CredentialManagerAgent` class. Generates a master key file at `data/master.key` on first run without requiring a master password. **Less secure** for production use.
- `src/core/credential_manager.py` - `SecureCredentialManager` class. **Requires** `CREDENTIAL_MASTER_PASSWORD` environment variable. Uses a random salt stored in `data/credentials.salt`. Uses a lazy-loading proxy pattern (`_CredentialManagerProxy`) that defers initialization until first access. **Recommended** for production.

Both use the same database path (`data/credentials.db`) which could cause conflicts if both are active.

### Module-Level Instantiation
- `agents/credential_manager.py` creates a global `credential_manager` instance at module import time (line 696). This will crash if the `cryptography` package is not installed, though it does have a graceful degradation path.
- `src/core/credential_manager.py` uses a lazy-loading proxy pattern (`_CredentialManagerProxy`) that defers initialization until first access. This is the safer approach and is the recommended implementation for production.

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 2.1.0 | 2026-03 | Cluster 1 production readiness: Nginx reverse proxy config, Prometheus monitoring, rate limiting, CORS config, basic auth endpoints, Web3/GitHub/Voice/Watcher agent security considerations |
| 2.0.1 | 2025-03 | Documentation audit: honest claims, fix repo URLs, .gitignore updates |
| 2.0.0 | 2024-06 | Initial security audit by AGENT-01 (Dhaher Corp) |

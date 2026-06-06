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

## Known Security Considerations

### Code Execution Agent
The Code Executor agent can execute arbitrary code. In production:
1. **Always use Docker mode** (`environment: 'docker'`) for code execution
2. Docker containers run with network disabled, memory limits, and CPU limits
3. Local execution mode should only be used in trusted development environments
4. Never expose the code execution API to untrusted users without authentication

### Authentication
- The current version does **not include built-in user authentication** on API endpoints
- For production deployment, place behind a reverse proxy (nginx) with authentication
- Consider using OAuth2, JWT, or API key-based authentication
- The `/api/` endpoints are designed to be private network only

### Docker Compose Defaults
- Default passwords in `docker-compose.yml` are placeholders (`changeme_secure_password`)
- **You MUST change all default passwords** before deploying
- Set these via `.env` file or environment variables

## Security Best Practices for Deployment

1. **Always set `SECRET_KEY`** to a strong random value
2. **Always set `CREDENTIAL_MASTER_PASSWORD`** to a strong unique password
3. **Use HTTPS** in production (via nginx reverse proxy or cloud load balancer)
4. **Restrict network access** - do not expose ports directly to the internet
5. **Keep dependencies updated** - run `pip audit` regularly
6. **Review API key permissions** - use least-privilege principle
7. **Enable audit logging** for credential access
8. **Regularly rotate** API keys and passwords

## Dependency Security

Run security audits on dependencies:
```bash
pip install pip-audit
pip-audit -r requirements.txt
```

### Duplicate Credential Managers
There are two credential manager implementations:
- `agents/credential_manager.py` - `CredentialManagerAgent` class. Generates a master key file at `data/master.key` on first run without requiring a master password. **Less secure** for production use.
- `src/core/credential_manager.py` - `SecureCredentialManager` class. **Requires** `CREDENTIAL_MASTER_PASSWORD` environment variable. Uses a random salt stored in `data/credentials.salt`. **Recommended** for production.

Both use the same database path (`data/credentials.db`) which could cause conflicts if both are active.

### Module-Level Instantiation
- `agents/credential_manager.py` creates a global `credential_manager` instance at module import time (line 696). This will crash if the `cryptography` package is not installed, though it does have a graceful degradation path.
- `src/core/credential_manager.py` uses a lazy-loading proxy pattern (`_CredentialManagerProxy`) that defers initialization until first access. This is the safer approach.

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 2.0.1 | 2025-03 | Documentation audit: honest claims, fix repo URLs, .gitignore updates |
| 2.0.0 | 2024-06 | Initial security audit by AGENT-01 (Dhaher Corp) |

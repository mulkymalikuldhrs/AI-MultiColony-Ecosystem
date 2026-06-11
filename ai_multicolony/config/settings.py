"""Configuration settings for AI-MultiColony.

Uses pydantic-settings for environment variable and .env file support.
All settings can be overridden via MULTICOLONY_ prefixed env vars.
"""

from __future__ import annotations

import logging
import os
import sys
import threading
import warnings
from typing import Any, Dict, List, Optional

from pydantic import Field, model_validator
from pydantic_settings import BaseSettings

_logger = logging.getLogger(__name__)


class ColonySettings(BaseSettings):
    """Colony-specific configuration."""
    heartbeat_interval_ms: int = 30_000
    max_agents: int = 50
    default_autonomy: int = 1
    routing_strategy: str = "least-loaded"
    a2a_enabled: bool = True
    inter_colony_enabled: bool = True
    skill_sharing: bool = True
    health_check_interval_ms: int = 60_000
    health_score_threshold: float = 0.5

    model_config = {"env_prefix": "MULTICOLONY_COLONY_"}


class MCPSettings(BaseSettings):
    """MCP (Model Context Protocol) configuration."""
    server_port: int = 8081
    sse_port: int = 8080
    max_connections: int = 1000
    rate_limit_rpm: int = 60
    rate_limit_burst: int = 10
    audit_enabled: bool = True
    circuit_breaker_threshold: int = 5
    circuit_breaker_timeout_s: int = 60
    circuit_breaker_half_open_max: int = 3
    transport: str = "stdio"  # stdio | sse | streamable-http
    supported_transports: List[str] = Field(default_factory=lambda: ["stdio", "sse", "streamable-http"])

    model_config = {"env_prefix": "MULTICOLONY_MCP_"}


class MemorySettings(BaseSettings):
    """Memory system configuration."""
    page_size: int = 4096
    compaction_threshold: float = 0.8
    working_set_size: int = 1024
    summary_max_tokens: int = 512
    max_pages_per_session: int = 100
    page_retention_days: int = 90
    preload_enabled: bool = True
    preload_top_k: int = 3
    vector_db_url: str = "http://localhost:6333"
    vector_db_collection: str = "colony-general"
    vector_embedding_dims: int = 1536
    vector_distance: str = "Cosine"
    compaction_interval_s: int = 300

    model_config = {"env_prefix": "MULTICOLONY_MEMORY_"}


class APISettings(BaseSettings):
    """API server configuration."""
    host: str = "0.0.0.0"
    port: int = 8000
    workers: int = 4
    cors_origins: List[str] = Field(default_factory=list)
    cors_methods: List[str] = Field(default_factory=list)
    cors_headers: List[str] = Field(default_factory=list)
    api_key_enabled: bool = True
    jwt_secret: str = ""
    jwt_expiry_hours: int = 24
    rate_limit_per_minute: int = 60
    rate_limit_burst: int = 10
    request_timeout_s: int = 30
    ws_heartbeat_s: int = 30
    ws_max_connections: int = 100

    model_config = {"env_prefix": "MULTICOLONY_API_"}

    @model_validator(mode="after")
    def _validate_security_settings(self) -> "APISettings":
        """Validate JWT secret and CORS wildcard settings."""
        dev_mode = os.environ.get("MULTICOLONY_DEV_MODE", "").lower() in ("1", "true", "yes")

        # JWT secret validation
        if not dev_mode:
            if not self.jwt_secret:
                raise ValueError(
                    "MULTICOLONY_API_JWT_SECRET must be set in production. "
                    "Set MULTICOLONY_DEV_MODE=true for local development."
                )
            if self.jwt_secret == "change-me-in-production":
                raise ValueError(
                    "MULTICOLONY_API_JWT_SECRET must not be the default value 'change-me-in-production' "
                    "in production. Set MULTICOLONY_DEV_MODE=true for local development."
                )

        # CORS wildcard warning
        if "*" in self.cors_origins:
            warnings.warn(
                "CORS is configured to allow ALL origins ('*'). This is insecure for production.",
                UserWarning,
                stacklevel=2,
            )
        if "*" in self.cors_methods:
            warnings.warn(
                "CORS is configured to allow ALL methods ('*'). This is insecure for production.",
                UserWarning,
                stacklevel=2,
            )
        if "*" in self.cors_headers:
            warnings.warn(
                "CORS is configured to allow ALL headers ('*'). This is insecure for production.",
                UserWarning,
                stacklevel=2,
            )

        return self


class ChannelSettings(BaseSettings):
    """Communication channel configuration."""
    telegram_bot_token: str = ""
    telegram_api_url: str = "https://api.telegram.org"
    telegram_webhook_url: str = ""
    telegram_allowed_chat_ids: List[str] = Field(default_factory=list)

    whatsapp_api_key: str = ""
    whatsapp_api_url: str = "https://api.whatsapp.com"
    whatsapp_phone_number_id: str = ""
    whatsapp_webhook_verify_token: str = ""

    discord_bot_token: str = ""
    discord_application_id: str = ""
    discord_guild_id: str = ""

    slack_bot_token: str = ""
    slack_signing_secret: str = ""
    slack_app_token: str = ""

    model_config = {"env_prefix": "MULTICOLONY_CHANNEL_"}


class SecuritySettings(BaseSettings):
    """Security and audit configuration."""
    audit_level: str = "full"  # minimal | summary | full
    audit_storage: str = "memory"  # memory | file
    audit_file_path: str = "/var/log/multicolony/audit.jsonl"
    audit_retention_days: int = 90
    audit_flush_interval_s: int = 10
    credential_encryption_key: str = ""
    credential_encryption_enabled: bool = True
    auto_approve_l0_to_l1: bool = True
    escalation_default_ttl_s: int = 3600
    approval_timeout_s: int = 300

    model_config = {"env_prefix": "MULTICOLONY_SECURITY_"}


class Settings(BaseSettings):
    """Top-level settings aggregating all sub-configurations."""

    # ── Core ──
    app_name: str = "ai-multicolony"
    version: str = "0.1.0"
    debug: bool = False
    log_level: str = "INFO"

    # ── LLM ──
    llm_provider: str = "openai"
    llm_model: str = "gpt-4o"
    llm_api_key: str = ""
    llm_base_url: str = ""
    llm_temperature: float = 0.7
    llm_max_tokens: int = 4096
    llm_timeout: int = 60

    # ── Sandbox ──
    sandbox_docker_enabled: bool = True
    sandbox_wasm_enabled: bool = False
    sandbox_startup_timeout: int = 30
    sandbox_resource_limits: Dict[str, Any] = Field(default_factory=lambda: {
        "cpu": "2",
        "memory": "4Gi",
        "timeout": 300,
    })

    # ── Browser ──
    browser_stealth_mode: bool = True
    browser_headless: bool = True
    browser_pool_size: int = 5
    browser_page_timeout: int = 30_000
    browser_stealth_target_score: float = 0.9

    # ── Sub-configs ──
    colony: ColonySettings = Field(default_factory=ColonySettings)
    mcp: MCPSettings = Field(default_factory=MCPSettings)
    memory: MemorySettings = Field(default_factory=MemorySettings)
    api: APISettings = Field(default_factory=APISettings)
    channel: ChannelSettings = Field(default_factory=ChannelSettings)
    security: SecuritySettings = Field(default_factory=SecuritySettings)

    model_config = {"env_prefix": "MULTICOLONY_", "env_file": ".env", "extra": "ignore"}


_settings: Optional[Settings] = None
_settings_lock = threading.Lock()


def get_settings() -> Settings:
    """Return the cached Settings singleton (lazy-initialised).

    Thread-safe: uses a lock to prevent race conditions during
    initialisation.
    """
    global _settings
    if _settings is None:
        with _settings_lock:
            if _settings is None:
                _check_dev_mode_safety()
                _settings = Settings()
    return _settings


def _check_dev_mode_safety() -> None:
    """Log a CRITICAL warning if dev mode is active without explicit opt-in.

    If ``MULTICOLONY_DEV_MODE=true`` is set **and**
    ``MULTICOLONY_ALLOW_DEV_MODE_IN_PROD`` is **not** set, this function
    emits a very visible startup warning because dev mode disables
    several production safety checks (e.g. JWT secret validation).
    """
    dev_mode = os.environ.get("MULTICOLONY_DEV_MODE", "").lower() in ("1", "true", "yes")
    allow_in_prod = os.environ.get("MULTICOLONY_ALLOW_DEV_MODE_IN_PROD", "")

    if dev_mode and not allow_in_prod:
        msg = (
            "\n"
            "=" * 70 + "\n"
            "⚠️  CRITICAL SECURITY WARNING ⚠️\n"
            "MULTICOLONY_DEV_MODE is ENABLED but "
            "MULTICOLONY_ALLOW_DEV_MODE_IN_PROD is NOT set.\n"
            "Dev mode disables production safety checks (JWT, CORS, etc.).\n"
            "If this is a production environment, unset MULTICOLONY_DEV_MODE\n"
            "immediately or set MULTICOLONY_ALLOW_DEV_MODE_IN_PROD to\n"
            "acknowledge the risk.\n"
            "=" * 70
        )
        _logger.critical(msg)
        # Also print to stderr so it's visible even if logging is not configured
        print(msg, file=sys.stderr)


def reset_settings() -> None:
    """Reset the cached settings (useful for tests)."""
    global _settings
    with _settings_lock:
        _settings = None

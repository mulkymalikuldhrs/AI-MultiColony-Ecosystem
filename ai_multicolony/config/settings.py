"""Pydantic Settings for the AI MultiColony Ecosystem.

All settings support environment variable overrides. Nested settings use
the __ delimiter (e.g., LLM__MODEL=gpt-4o overrides llm.model).
"""

from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path
from typing import Optional

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class LLMSettings(BaseSettings):
    """LLM provider configuration."""

    model_config = SettingsConfigDict(env_prefix="LLM_")

    model: str = Field(default="gpt-4o", description="Default LLM model")
    temperature: float = Field(default=0.1, ge=0.0, le=2.0, description="Temperature for generation")
    max_tokens: int = Field(default=4096, ge=1, le=128000, description="Max tokens per request")
    timeout: int = Field(default=120, ge=1, description="Request timeout in seconds")
    max_retries: int = Field(default=3, ge=0, le=10, description="Max retry attempts")
    top_p: float = Field(default=1.0, ge=0.0, le=1.0)
    frequency_penalty: float = Field(default=0.0, ge=-2.0, le=2.0)
    presence_penalty: float = Field(default=0.0, ge=-2.0, le=2.0)
    streaming: bool = Field(default=False, description="Enable streaming responses")
    cost_limit_daily: float = Field(default=100.0, ge=0.0, description="Daily cost limit in USD")


class DatabaseSettings(BaseSettings):
    """Database configuration."""

    model_config = SettingsConfigDict(env_prefix="DATABASE_")

    url: str = Field(default="sqlite:///./data/ecosystem.db", description="Database URL")
    pool_size: int = Field(default=5, ge=1)
    max_overflow: int = Field(default=10, ge=0)
    echo: bool = Field(default=False)


class RedisSettings(BaseSettings):
    """Redis configuration."""

    model_config = SettingsConfigDict(env_prefix="REDIS_")

    url: str = Field(default="redis://localhost:6379/0")
    password: Optional[str] = None
    db: int = Field(default=0, ge=0, le=15)


class QdrantSettings(BaseSettings):
    """Qdrant vector store configuration."""

    model_config = SettingsConfigDict(env_prefix="QDRANT_")

    url: str = Field(default="http://localhost:6333")
    api_key: Optional[str] = None
    collection: str = Field(default="ai_multicolony")
    embedding_dimension: int = Field(default=1536, ge=1)


class ChromaSettings(BaseSettings):
    """ChromaDB vector store configuration."""

    model_config = SettingsConfigDict(env_prefix="CHROMA_")

    persist_directory: str = Field(default="./data/chroma")
    collection: str = Field(default="ai_multicolony")


class SandboxSettings(BaseSettings):
    """Sandbox configuration."""

    model_config = SettingsConfigDict(env_prefix="SANDBOX_")

    docker_host: str = Field(default="unix:///var/run/docker.sock")
    image: str = Field(default="python:3.12-slim")
    timeout: int = Field(default=300, ge=1)
    memory_limit: str = Field(default="512m")
    cpu_limit: float = Field(default=1.0)
    network_disabled: bool = Field(default=False)


class BrowserSettings(BaseSettings):
    """Browser automation configuration."""

    model_config = SettingsConfigDict(env_prefix="BROWSER_")

    headless: bool = Field(default=True)
    stealth_mode: bool = Field(default=True)
    user_agent: Optional[str] = None
    viewport_width: int = Field(default=1920, ge=320)
    viewport_height: int = Field(default=1080, ge=240)
    page_timeout: int = Field(default=30000, ge=1000)
    navigation_timeout: int = Field(default=60000, ge=1000)


class SecuritySettings(BaseSettings):
    """Security configuration."""

    model_config = SettingsConfigDict(env_prefix="SECURITY_")

    allowed_commands: list[str] = Field(
        default=["ls", "cat", "head", "tail", "grep", "find", "wc", "echo", "pwd", "whoami"],
        description="Allowed shell commands",
    )
    blocked_commands: list[str] = Field(
        default=["rm -rf", "mkfs", "dd", "format"],
        description="Blocked shell command patterns",
    )
    max_file_size_mb: int = Field(default=50, ge=1)
    enable_audit: bool = Field(default=True)
    sandbox_all_commands: bool = Field(default=False)


class MCPSettings(BaseSettings):
    """MCP protocol configuration."""

    model_config = SettingsConfigDict(env_prefix="MCP_")

    server_host: str = Field(default="0.0.0.0")
    server_port: int = Field(default=5000, ge=1, le=65535)


class APISettings(BaseSettings):
    """API server configuration."""

    model_config = SettingsConfigDict(env_prefix="API_")

    host: str = Field(default="0.0.0.0")
    port: int = Field(default=8000, ge=1, le=65535)
    workers: int = Field(default=1, ge=1)
    cors_origins: list[str] = Field(default_factory=lambda: ["*"])
    api_key: Optional[str] = None


class Settings(BaseSettings):
    """Main application settings aggregating all sub-settings.

    Environment variables can override any setting using double-underscore
    as a delimiter for nested models:
        LLM__MODEL=gpt-4o            -> settings.llm.model
        DATABASE__URL=postgres://...  -> settings.database.url
        REDIS__URL=redis://...        -> settings.redis.url

    Top-level settings use their own prefix:
        APP_ENV=production            -> settings.app_env
        OPENAI_API_KEY=sk-...         -> settings.openai_api_key
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_nested_delimiter="__",
        extra="ignore",
    )

    # General
    app_name: str = Field(default="AI-MultiColony-Ecosystem")
    app_env: str = Field(default="development")
    debug: bool = Field(default=False)
    log_level: str = Field(default="INFO")
    log_json: bool = Field(default=False, description="Output logs in JSON format")

    # API Keys
    openai_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    google_api_key: Optional[str] = None
    azure_api_key: Optional[str] = None
    azure_api_base: Optional[str] = None
    azure_api_version: Optional[str] = None

    # Channel API Keys
    telegram_bot_token: Optional[str] = None
    discord_bot_token: Optional[str] = None
    slack_bot_token: Optional[str] = None
    slack_app_token: Optional[str] = None

    # Sub-settings
    llm: LLMSettings = Field(default_factory=LLMSettings)
    database: DatabaseSettings = Field(default_factory=DatabaseSettings)
    redis: RedisSettings = Field(default_factory=RedisSettings)
    qdrant: QdrantSettings = Field(default_factory=QdrantSettings)
    chroma: ChromaSettings = Field(default_factory=ChromaSettings)
    sandbox: SandboxSettings = Field(default_factory=SandboxSettings)
    browser: BrowserSettings = Field(default_factory=BrowserSettings)
    security: SecuritySettings = Field(default_factory=SecuritySettings)
    mcp: MCPSettings = Field(default_factory=MCPSettings)
    api: APISettings = Field(default_factory=APISettings)

    @field_validator("app_env")
    @classmethod
    def validate_app_env(cls, v: str) -> str:
        allowed = {"development", "staging", "production", "test"}
        if v not in allowed:
            raise ValueError(f"app_env must be one of {allowed}, got '{v}'")
        return v

    @field_validator("log_level")
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        allowed = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
        v_upper = v.upper()
        if v_upper not in allowed:
            raise ValueError(f"log_level must be one of {allowed}, got '{v}'")
        return v_upper

    @property
    def is_development(self) -> bool:
        return self.app_env == "development"

    @property
    def is_production(self) -> bool:
        return self.app_env == "production"

    @property
    def data_dir(self) -> Path:
        return Path("./data")

    def ensure_data_dir(self) -> Path:
        """Ensure the data directory exists and return it."""
        path = self.data_dir
        path.mkdir(parents=True, exist_ok=True)
        return path

    def apply_to_env(self) -> None:
        """Push API keys into environment variables for litellm auto-detection."""
        if self.openai_api_key:
            os.environ.setdefault("OPENAI_API_KEY", self.openai_api_key)
        if self.anthropic_api_key:
            os.environ.setdefault("ANTHROPIC_API_KEY", self.anthropic_api_key)
        if self.google_api_key:
            os.environ.setdefault("GOOGLE_API_KEY", self.google_api_key)
        if self.azure_api_key:
            os.environ.setdefault("AZURE_API_KEY", self.azure_api_key)
        if self.azure_api_base:
            os.environ.setdefault("AZURE_API_BASE", self.azure_api_base)
        if self.azure_api_version:
            os.environ.setdefault("AZURE_API_VERSION", self.azure_api_version)


@lru_cache(maxsize=1)
def get_settings(config_path: Optional[str] = None) -> Settings:
    """Get cached application settings.

    Args:
        config_path: Optional path to a .env file. If provided, clears cache and reloads.

    Returns:
        Settings instance.
    """
    if config_path:
        get_settings.cache_clear()
        os.environ["ENV_FILE"] = config_path
    return Settings()

"""Unified configuration for the AI-MultiColony-Ecosystem."""

from __future__ import annotations

from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class QuantConfig(BaseModel):
    """Quant trading module configuration."""
    max_risk_per_trade: float = 0.005
    max_daily_loss: float = 0.01
    max_weekly_loss: float = 0.03
    min_risk_reward: float = 2.0
    max_correlated_positions: int = 3
    backtest_initial_balance: float = 10000.0
    base_spread: float = 0.0002
    commission_pct: float = 0.001


class OrganismConfig(BaseModel):
    """Organism module configuration."""
    scheduler_enabled: bool = True
    max_iterations_per_task: int = 10
    hard_timeout_ms: int = 300_000
    max_consecutive_errors: int = 5
    max_loop_detection: int = 100
    memory_storage_path: str = "data/organism_memory.json"


class GatewayConfig(BaseModel):
    """API gateway configuration."""
    rate_limit_per_minute: int = 60
    auth_enabled: bool = True
    default_locale: str = "en"
    cors_enabled: bool = True
    max_request_size_mb: int = 10


class BackendConfig(BaseModel):
    """Backend services configuration."""
    data_dir: str = "data"
    memory_max_entries: int = 1000
    memory_max_tokens: int = 8000
    agent_max_iterations: int = 10
    agent_max_tokens: int = 100_000


class EcosystemSettings(BaseSettings):
    """Main ecosystem settings loaded from environment variables.

    All settings can be overridden via environment variables with the ECOSYS_ prefix.
    Example: ECOSYS_QUANT__MAX_RISK_PER_TRADE=0.01
    """

    model_config = SettingsConfigDict(
        env_prefix="ECOSYS_",
        env_nested_delimiter="__",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Module configurations
    quant: QuantConfig = Field(default_factory=QuantConfig)
    organism: OrganismConfig = Field(default_factory=OrganismConfig)
    gateway: GatewayConfig = Field(default_factory=GatewayConfig)
    backend: BackendConfig = Field(default_factory=BackendConfig)

    # Global settings
    debug: bool = False
    log_level: str = "INFO"
    version: str = "0.3.0"


# Singleton instance
_settings: EcosystemSettings | None = None


def get_settings() -> EcosystemSettings:
    """Get the global ecosystem settings instance."""
    global _settings
    if _settings is None:
        _settings = EcosystemSettings()
    return _settings


def reset_settings() -> None:
    """Reset the global settings instance (useful for testing)."""
    global _settings
    _settings = None

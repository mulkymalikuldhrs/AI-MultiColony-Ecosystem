"""
Application settings using Pydantic Settings.

All configuration is loaded from environment variables with sensible defaults.
API keys, database URLs, and other secrets MUST be set via environment variables.

IMPORTANT: Constitutional risk limits (risk_max_per_trade, risk_max_daily_loss, etc.)
are NOT configurable here. They are IMMUTABLE constants defined in:
    quant_nanggroe/engine/risk/constants.py

That file is the SINGLE SOURCE OF TRUTH for all risk limits. Any attempt to
override them via environment variables is detected and rejected at startup.
"""

from __future__ import annotations

import os
import logging
from functools import lru_cache
from typing import Optional

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

logger = logging.getLogger(__name__)

# ── Constitutional override detection ────────────────────────────────────────
# These env var names are FORBIDDEN — they would override immutable risk limits.
_CONSTITUTIONAL_ENV_VARS = [
    "QNAI_RISK_MAX_PER_TRADE",
    "QNAI_RISK_MAX_DAILY_LOSS",
    "QNAI_RISK_MAX_WEEKLY_LOSS",
    "QNAI_RISK_MAX_DRAWDOWN",
]


def _check_no_constitutional_overrides() -> list[str]:
    """Detect any attempt to override constitutional limits via env vars.

    Returns a list of violation messages (empty if clean).
    """
    violations: list[str] = []
    for env_var in _CONSTITUTIONAL_ENV_VARS:
        value = os.environ.get(env_var)
        if value is not None:
            violations.append(
                f"SECURITY VIOLATION: Environment variable {env_var}={value!r} "
                f"attempts to override a constitutional risk limit. "
                f"Constitutional limits are IMMUTABLE and defined in "
                f"quant_nanggroe/engine/risk/constants.py. "
                f"Remove this environment variable to proceed."
            )
    return violations


class Settings(BaseSettings):
    """
    Central application configuration.

    All values are loaded from environment variables with the prefix QNAI_.
    For example, QNAI_DATABASE_URL maps to database_url.

    IMPORTANT: Risk limits are NOT here. See quant_nanggroe/engine/risk/constants.py
    for the SINGLE SOURCE OF TRUTH on constitutional risk limits.

    Attributes:
        app_name: Application name
        version: Application version
        debug: Enable debug mode
        database_url: SQLAlchemy database connection URL
        redis_url: Redis connection URL for caching
        openai_api_key: OpenAI API key
        anthropic_api_key: Anthropic API key
        google_api_key: Google AI API key
        alpaca_api_key: Alpaca trading API key
        alpaca_api_secret: Alpaca trading API secret
        binance_api_key: Binance API key
        binance_api_secret: Binance API secret
        alpha_vantage_api_key: Alpha Vantage API key (free tier: 25 req/day)
        polygon_api_key: Polygon.io API key
        fred_api_key: FRED API key (free, 120 req/min)
        coingecko_api_key: CoinGecko Pro API key (free tier works without key)
        finnhub_api_key: Finnhub API key (free tier: 60 calls/min)
        twelvedata_api_key: Twelve Data API key (free tier: 800 credits/day)
        sec_edgar_user_email: SEC EDGAR User-Agent email (required, no key needed)
        ecb_api_key: ECB API key (not needed, API is free)
        default_llm_provider: Default LLM provider
        default_llm_model: Default LLM model name
        log_level: Logging level
    """

    model_config = SettingsConfigDict(
        env_prefix="QNAI_",
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Application
    app_name: str = "Quant Nanggroe AI"
    version: str = "0.2.0"
    debug: bool = False

    # Database
    database_url: str = "sqlite:///quant_nanggroe.db"
    redis_url: Optional[str] = None

    # CORS
    cors_origins: list[str] = Field(
        default_factory=lambda: ["http://localhost:3000", "http://localhost:8000"],
        description="Allowed CORS origins. Set via QNAI_CORS_ORIGINS (comma-separated).",
    )

    # LLM API Keys
    openai_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    google_api_key: Optional[str] = None
    nvidia_api_key: Optional[str] = None
    nvidia_base_url: str = "https://integrate.api.nvidia.com/v1"

    # Trading API Keys
    alpaca_api_key: Optional[str] = None
    alpaca_api_secret: Optional[str] = None
    alpaca_paper: bool = True
    binance_api_key: Optional[str] = None
    binance_api_secret: Optional[str] = None

    # Data Provider API Keys (free tiers available)
    alpha_vantage_api_key: Optional[str] = None
    polygon_api_key: Optional[str] = None
    fred_api_key: Optional[str] = None
    coingecko_api_key: Optional[str] = None      # Pro tier (free works without key)
    finnhub_api_key: Optional[str] = None         # Free tier: 60 calls/min
    twelvedata_api_key: Optional[str] = None       # Free tier: 800 credits/day
    sec_edgar_user_email: Optional[str] = None     # Required User-Agent email (no key needed)
    ecb_api_key: Optional[str] = None              # Not needed (ECB is free, no key)

    # LLM Defaults
    default_llm_provider: str = "openai"
    default_llm_model: str = "gpt-4o"
    default_llm_temperature: float = 0.0

    # NVIDIA NIM
    nvidia_nim_api_key: Optional[str] = None
    nvidia_nim_base_url: str = "https://integrate.api.nvidia.com/v1"
    nvidia_nim_default_model: str = "meta/llama-3.1-70b-instruct"

    # Logging
    log_level: str = "INFO"
    log_format: str = "json"

    # ── Constitutional Risk Limits REMOVED from settings ────────────────
    # Risk limits are IMMUTABLE and defined in quant_nanggroe/engine/risk/constants.py
    # They CANNOT be overridden via environment variables.
    # See that file for: MAX_RISK_PER_TRADE, MAX_DAILY_LOSS, MAX_WEEKLY_LOSS,
    #   MAX_DRAWDOWN_PCT, KILL_SWITCH_DAILY_PNL, KILL_SWITCH_WEEKLY_PNL, etc.

    # Backtesting
    backtest_default_commission: float = 0.001
    backtest_default_slippage: float = 0.0005
    backtest_default_initial_capital: float = 100000.0

    # Data
    data_cache_ttl: int = 300  # 5 minutes
    data_provider_timeout: int = 30

    @field_validator("log_level")
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        """Validate log level is a valid Python logging level."""
        valid_levels = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
        v_upper = v.upper()
        if v_upper not in valid_levels:
            raise ValueError(f"log_level must be one of {valid_levels}, got {v}")
        return v_upper


@lru_cache
def get_settings() -> Settings:
    """
    Get cached application settings instance.

    On first call, this also checks for forbidden constitutional override
    environment variables and logs a critical warning if any are found.

    Returns:
        Cached Settings instance loaded from environment variables

    Raises:
        RuntimeError: If any QNAI_RISK_* env vars are set (constitutional override attempt)
    """
    violations = _check_no_constitutional_overrides()
    if violations:
        for v in violations:
            logger.critical(v)
        raise RuntimeError(
            "Constitutional risk limit override detected! "
            "Remove the forbidden environment variables listed above and restart. "
            "Constitutional limits are defined in quant_nanggroe/engine/risk/constants.py "
            "and CANNOT be overridden."
        )
    return Settings()

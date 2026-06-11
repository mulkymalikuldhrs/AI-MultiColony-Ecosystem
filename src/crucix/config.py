"""
Crucix Configuration — pydantic-settings based configuration.

Port of crucix.config.mjs to Python with full env-var overrides.
All settings can be overridden via environment variables prefixed with CRUCIX_.
"""

from __future__ import annotations

from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class LLMConfig(BaseSettings):
    """LLM provider configuration."""

    model_config = SettingsConfigDict(env_prefix="CRUCIX_LLM_")

    provider: Optional[str] = Field(
        default=None,
        description="LLM provider: anthropic | openai | gemini | openrouter | minimax | mistral | ollama | grok",
    )
    api_key: Optional[str] = Field(default=None, description="LLM API key")
    model: Optional[str] = Field(default=None, description="Model name for the chosen provider")
    base_url: Optional[str] = Field(
        default=None,
        description="Base URL (used for Ollama or custom endpoints)",
    )

    @property
    def is_configured(self) -> bool:
        return bool(self.provider and self.api_key)


class TelegramConfig(BaseSettings):
    """Telegram bot / alert configuration."""

    model_config = SettingsConfigDict(env_prefix="CRUCIX_TELEGRAM_")

    bot_token: Optional[str] = Field(default=None)
    chat_id: Optional[str] = Field(default=None)
    poll_interval_ms: int = Field(default=5000, description="Bot polling interval in ms")
    channels: Optional[str] = Field(
        default=None,
        description="Comma-separated extra channel IDs",
    )

    @property
    def is_configured(self) -> bool:
        return bool(self.bot_token and self.chat_id)


class DiscordConfig(BaseSettings):
    """Discord bot / alert configuration."""

    model_config = SettingsConfigDict(env_prefix="CRUCIX_DISCORD_")

    bot_token: Optional[str] = Field(default=None)
    channel_id: Optional[str] = Field(default=None)
    guild_id: Optional[str] = Field(default=None)
    webhook_url: Optional[str] = Field(default=None)

    @property
    def is_configured(self) -> bool:
        return bool(self.bot_token or self.webhook_url)


class DeltaThresholdConfig(BaseSettings):
    """Delta engine threshold overrides."""

    model_config = SettingsConfigDict(env_prefix="CRUCIX_DELTA_")

    # Numeric metric % change thresholds
    vix: float = 5.0
    hy_spread: float = 5.0
    yield_10y2y: float = 10.0
    wti: float = 3.0
    brent: float = 3.0
    natgas: float = 5.0
    gold: float = 2.0
    silver: float = 3.0
    unemployment: float = 2.0
    fed_funds: float = 1.0
    yield_10y: float = 3.0
    usd_index: float = 1.0
    mortgage: float = 2.0

    # Count metric thresholds
    urgent_posts: int = 2
    thermal_total: int = 500
    air_total: int = 50
    who_alerts: int = 1
    conflict_events: int = 5
    conflict_fatalities: int = 10
    sdr_online: int = 3
    news_count: int = 5
    sources_ok: int = 1


class CrucixConfig(BaseSettings):
    """Crucix top-level configuration with env-var overrides."""

    model_config = SettingsConfigDict(
        env_prefix="CRUCIX_",
        env_nested_delimiter="__",
    )

    port: int = Field(default=3117, description="HTTP server port")
    public_url: Optional[str] = Field(default=None)
    refresh_interval_minutes: int = Field(default=15)
    language: str = Field(default="en", description="Default locale code")
    source_timeout_seconds: float = Field(default=30.0)
    runs_dir: str = Field(default="runs", description="Directory for sweep data storage")

    llm: LLMConfig = Field(default_factory=LLMConfig)
    telegram: TelegramConfig = Field(default_factory=TelegramConfig)
    discord: DiscordConfig = Field(default_factory=DiscordConfig)
    delta_thresholds: DeltaThresholdConfig = Field(default_factory=DeltaThresholdConfig)

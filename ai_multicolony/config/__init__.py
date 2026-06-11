"""Configuration module for the AI MultiColony Ecosystem.

Provides Pydantic Settings with ENV override and structured logging
with structlog + rich console output.
"""

from ai_multicolony.config.settings import Settings, get_settings
from ai_multicolony.config.logging_config import setup_logging, get_logger

__all__ = ["Settings", "get_settings", "setup_logging", "get_logger"]

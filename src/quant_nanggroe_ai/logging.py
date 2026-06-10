"""
Structured Logging Setup
========================
Uses structlog for structured, JSON-formatted logs.
Integrates with the engine's audit system.

Supports both console and file-based logging.
In production, JSON output and file logging are enabled automatically.
"""

from __future__ import annotations

import logging
import logging.handlers
import os
import sys
from pathlib import Path
from typing import Any

import structlog


def setup_logging(
    log_level: str = "INFO",
    json_output: bool | None = None,
    log_file: str | None = None,
    log_dir: str | None = None,
) -> None:
    """
    Configure structured logging for the entire application.

    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        json_output: If True, output JSON-formatted logs (for production).
            If None, auto-enables when APP_ENV=production.
        log_file: Optional log file name (e.g., "app.log").
        log_dir: Optional log directory. Defaults to "./logs".
    """
    # Auto-enable JSON in production if not explicitly set
    if json_output is None:
        env = os.getenv("APP_ENV", os.getenv("app_env", "development"))
        json_output = env == "production"

    shared_processors: list[Any] = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
    ]

    if json_output:
        renderer = structlog.processors.JSONRenderer()
    else:
        renderer = structlog.dev.ConsoleRenderer()

    structlog.configure(
        processors=[
            *shared_processors,
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ],
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=False,  # Allow runtime reconfiguration
    )

    formatter = structlog.stdlib.ProcessorFormatter(
        processors=[
            structlog.stdlib.ProcessorFormatter.remove_processors_meta,
            renderer,
        ],
        foreign_pre_chain=shared_processors,
    )

    # ── Console Handler ──────────────────────────────────────────────
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)

    root_logger = logging.getLogger()
    root_logger.handlers.clear()
    root_logger.addHandler(console_handler)
    root_logger.setLevel(getattr(logging, log_level.upper(), logging.INFO))

    # ── File Handler (optional) ──────────────────────────────────────
    if log_file:
        log_path = Path(log_dir or "./logs")
        log_path.mkdir(parents=True, exist_ok=True)
        file_path = log_path / log_file

        file_handler = logging.handlers.RotatingFileHandler(
            file_path,
            maxBytes=50 * 1024 * 1024,  # 50 MB
            backupCount=5,
            encoding="utf-8",
        )
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)

    # Quieten noisy libraries
    for name in ["uvicorn.access", "httpx", "httpcore", "asyncio"]:
        logging.getLogger(name).setLevel(logging.WARNING)


def get_logger(name: str) -> structlog.stdlib.BoundLogger:
    """Get a structured logger for a module."""
    return structlog.get_logger(name)

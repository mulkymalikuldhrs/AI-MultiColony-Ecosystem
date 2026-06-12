"""Logging configuration for the AI MultiColony Ecosystem.

Configures structlog with rich console rendering for development and
JSON output for production. Supports both synchronous and asynchronous
logging patterns.

Falls back to standard logging when structlog is not installed.
"""

from __future__ import annotations

import logging
import sys
from typing import Optional

try:
    import structlog
    # Verify structlog is actually usable — some versions have API incompatibilities
    _structlog_test = structlog.get_logger("test")
    if not hasattr(_structlog_test, 'info'):
        structlog = None  # type: ignore[assignment]
except (ImportError, TypeError, AttributeError):
    structlog = None  # type: ignore[assignment]

# PII redaction is imported lazily inside setup functions to avoid circular imports:
#   logging_config → core.pii_redaction → core.__init__ → base_agent → logging_config
# Instead, we import the module directly when needed.
_pii_redaction_module = None


def _get_pii_redaction():
    """Lazily import and cache the PII redaction module."""
    global _pii_redaction_module
    if _pii_redaction_module is None:
        from ai_multicolony.core import pii_redaction as _mod
        _pii_redaction_module = _mod
    return _pii_redaction_module


def setup_logging(
    level: str = "INFO",
    json_format: bool = False,
    log_file: Optional[str] = None,
    rich_tracebacks: bool = True,
) -> None:
    """Configure structured logging for the application.

    Uses structlog for structured output with rich console rendering
    in development and JSON rendering in production.  Falls back to
    standard ``logging`` when structlog is not installed.

    Args:
        level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL).
        json_format: Whether to output logs in JSON format (for production).
        log_file: Optional file path to write logs to.
        rich_tracebacks: Whether to use rich traceback rendering.
    """
    log_level = getattr(logging, level.upper(), logging.INFO)

    if structlog is not None:
        _setup_structlog(log_level, json_format, log_file, rich_tracebacks)
    else:
        _setup_stdlib_logging(log_level, log_file)


def _setup_structlog(
    log_level: int,
    json_format: bool,
    log_file: Optional[str],
    rich_tracebacks: bool,
) -> None:
    """Configure structlog-based logging."""
    shared_processors: list[structlog.types.Processor] = [  # type: ignore[union-attr]
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.UnicodeDecoder(),
        _get_pii_redaction().pii_redaction_processor,
    ]

    if json_format:
        renderer: structlog.types.Processor = structlog.processors.JSONRenderer()
    else:
        try:
            from rich.traceback import Traceback
            from rich.console import Console

            # Use rich-enhanced console renderer for development
            renderer = structlog.dev.ConsoleRenderer(
                colors=True,
                exception_formatter=structlog.dev.rich_traceback_formatter
                if rich_tracebacks
                else structlog.dev.plain_traceback_formatter,
            )
        except ImportError:
            renderer = structlog.dev.ConsoleRenderer(colors=True)

    structlog.configure(
        processors=[
            *shared_processors,
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ],
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

    formatter = structlog.stdlib.ProcessorFormatter(
        processors=[
            structlog.stdlib.ProcessorFormatter.remove_processors_meta,
            renderer,
        ],
        foreign_pre_chain=shared_processors,
    )

    pii_filter = _get_pii_redaction().PIIRedactionFilter()

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)
    handler.addFilter(pii_filter)

    root_logger = logging.getLogger()
    root_logger.handlers.clear()
    root_logger.addHandler(handler)
    root_logger.setLevel(log_level)

    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        file_handler.addFilter(pii_filter)
        root_logger.addHandler(file_handler)

    # Quiet down noisy libraries
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("docker").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("asyncio").setLevel(logging.WARNING)
    logging.getLogger("chromadb").setLevel(logging.WARNING)
    logging.getLogger("qdrant_client").setLevel(logging.WARNING)


def _setup_stdlib_logging(log_level: int, log_file: Optional[str]) -> None:
    """Fallback: configure standard library logging without structlog."""
    formatter = logging.Formatter(
        fmt="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%S",
    )

    pii_filter = _get_pii_redaction().PIIRedactionFilter()

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)
    handler.addFilter(pii_filter)

    root_logger = logging.getLogger()
    root_logger.handlers.clear()
    root_logger.addHandler(handler)
    root_logger.setLevel(log_level)

    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        file_handler.addFilter(pii_filter)
        root_logger.addHandler(file_handler)

    # Quiet down noisy libraries
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("docker").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("asyncio").setLevel(logging.WARNING)
    logging.getLogger("chromadb").setLevel(logging.WARNING)
    logging.getLogger("qdrant_client").setLevel(logging.WARNING)


def get_logger(name: str):
    """Get a structured logger instance.

    When structlog is available, returns a ``BoundLogger``; otherwise
    falls back to a standard ``logging.Logger``.

    Args:
        name: Logger name, typically ``__name__``.

    Returns:
        Bound structured logger (structlog) or standard logger.
    """
    if structlog is not None:
        return structlog.get_logger(name)
    return logging.getLogger(name)

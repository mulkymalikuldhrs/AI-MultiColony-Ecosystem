"""Correlation Context — Request correlation tracking for distributed tracing.

Provides a lightweight context manager for correlating requests across
the multi-agent pipeline, enabling end-to-end traceability from market
data ingestion through execution.
"""

from __future__ import annotations

import logging
import uuid
from contextvars import ContextVar
from dataclasses import dataclass, field
from typing import Optional

logger = logging.getLogger(__name__)

# Thread-safe correlation ID storage
_current_correlation_id: ContextVar[Optional[str]] = ContextVar("correlation_id", default=None)


@dataclass
class CorrelationContext:
    """Correlation context for tracking request flow across the pipeline.

    Provides a unique ID per trading cycle that propagates through
    all agents, risk checks, and execution decisions.
    """
    correlation_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    parent_id: Optional[str] = None
    cycle_number: int = 0
    agent_trail: list = field(default_factory=list)

    @classmethod
    def new_cycle(cls, parent_id: Optional[str] = None) -> str:
        """Create a new correlation cycle and return the correlation ID.

        Args:
            parent_id: Optional parent correlation ID for nested flows.

        Returns:
            The new correlation ID string.
        """
        ctx = cls(parent_id=parent_id)
        _current_correlation_id.set(ctx.correlation_id)
        logger.debug("New correlation cycle: %s (parent: %s)", ctx.correlation_id, parent_id)
        return ctx.correlation_id

    @classmethod
    def get_current_id(cls) -> Optional[str]:
        """Get the current correlation ID."""
        return _current_correlation_id.get()

    @classmethod
    def clear(cls) -> None:
        """Clear the current correlation context."""
        _current_correlation_id.set(None)

    def add_agent_step(self, agent_name: str, action: str) -> None:
        """Record an agent step in the correlation trail."""
        self.agent_trail.append({
            "agent": agent_name,
            "action": action,
            "cycle": self.cycle_number,
        })


__all__ = ["CorrelationContext"]

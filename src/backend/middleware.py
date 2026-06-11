"""
Agent Middleware - Deer-flow style agent middleware pipeline.
Includes loop detection, token tracking, and error handling middleware.
"""

from __future__ import annotations

import logging
import time
from abc import ABC, abstractmethod
from typing import Optional

from pydantic import BaseModel, Field

logger = logging.getLogger("ecosystem.backend.middleware")


class AgentContext(BaseModel):
    """Context for agent middleware processing."""
    agent_id: str
    task: str = ""
    iteration: int = 0
    token_count: int = 0
    errors: int = 0
    extra: dict = Field(default_factory=dict)


class MiddlewareAction(BaseModel):
    """Result of middleware processing."""
    continue_: bool = True  # renamed to avoid Python keyword
    reason: str = ""
    modified_context: AgentContext | None = None


class AgentMiddleware(ABC):
    """Base class for agent middleware."""

    @abstractmethod
    def process(self, context: AgentContext) -> MiddlewareAction:
        """Process an agent context. Return action to control flow."""
        ...


class LoopDetectionMiddleware(AgentMiddleware):
    """Detects when an agent is looping by tracking iteration count."""

    def __init__(self, max_iterations: int = 10) -> None:
        self.max_iterations = max_iterations

    def process(self, context: AgentContext) -> MiddlewareAction:
        if context.iteration >= self.max_iterations:
            return MiddlewareAction(
                continue_=False,
                reason=f"Loop detected: {context.iteration} iterations (max: {self.max_iterations})",
            )
        return MiddlewareAction(continue_=True)


class TokenBudgetMiddleware(AgentMiddleware):
    """Enforces token budget limits for agents."""

    def __init__(self, max_tokens: int = 100000) -> None:
        self.max_tokens = max_tokens

    def process(self, context: AgentContext) -> MiddlewareAction:
        if context.token_count >= self.max_tokens:
            return MiddlewareAction(
                continue_=False,
                reason=f"Token budget exceeded: {context.token_count} (max: {self.max_tokens})",
            )
        return MiddlewareAction(continue_=True)


class ErrorThresholdMiddleware(AgentMiddleware):
    """Stops agent when error count exceeds threshold."""

    def __init__(self, max_errors: int = 5) -> None:
        self.max_errors = max_errors

    def process(self, context: AgentContext) -> MiddlewareAction:
        if context.errors >= self.max_errors:
            return MiddlewareAction(
                continue_=False,
                reason=f"Too many errors: {context.errors} (max: {self.max_errors})",
            )
        return MiddlewareAction(continue_=True)


class AgentMiddlewarePipeline:
    """Pipeline for processing agent actions through multiple middleware."""

    def __init__(self) -> None:
        self.middlewares: list[AgentMiddleware] = []

    def add(self, middleware: AgentMiddleware) -> None:
        """Add middleware to the pipeline."""
        self.middlewares.append(middleware)

    def process(self, context: AgentContext) -> MiddlewareAction:
        """Process context through all middleware.

        Returns the first denial or success.
        """
        for middleware in self.middlewares:
            action = middleware.process(context)
            if not action.continue_:
                return action
            if action.modified_context:
                context = action.modified_context
        return MiddlewareAction(continue_=True)

"""
Conversation Memory - Deer-flow style conversation memory management.
Features: episodic memory storage, retrieval, and summarization hooks.
"""

from __future__ import annotations

import logging
import time
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

logger = logging.getLogger("ecosystem.backend.memory")


class MemoryEntry(BaseModel):
    """A single memory entry in conversation memory."""
    id: int
    role: str  # user, assistant, system
    content: str
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())
    token_count: int = 0
    metadata: dict = Field(default_factory=dict)


class ConversationMemory:
    """Conversation memory with episodic storage and retrieval.

    Inspired by deer-flow's memory system with:
    - Episodic memory storage
    - Context window management
    - Summarization hooks for long conversations
    - Token budget tracking
    """

    def __init__(self, max_entries: int = 1000, max_tokens: int = 8000) -> None:
        self.max_entries = max_entries
        self.max_tokens = max_tokens
        self._entries: list[MemoryEntry] = []
        self._next_id = 1
        self._total_tokens = 0

    def add(self, role: str, content: str, token_count: int = 0, metadata: dict | None = None) -> MemoryEntry:
        """Add a memory entry.

        Args:
            role: Message role (user, assistant, system)
            content: Message content
            token_count: Estimated token count
            metadata: Optional metadata dict

        Returns:
            The created MemoryEntry
        """
        entry = MemoryEntry(
            id=self._next_id,
            role=role,
            content=content,
            token_count=token_count,
            metadata=metadata or {},
        )

        self._entries.append(entry)
        self._next_id += 1
        self._total_tokens += token_count

        # Trim if over limits
        self._maybe_trim()

        logger.debug("Memory add: %s (%d tokens)", role, token_count)
        return entry

    def _maybe_trim(self) -> None:
        """Trim old entries if over limits."""
        while len(self._entries) > self.max_entries:
            removed = self._entries.pop(0)
            self._total_tokens -= removed.token_count

        while self._total_tokens > self.max_tokens and len(self._entries) > 1:
            removed = self._entries.pop(0)
            self._total_tokens -= removed.token_count

    def get_recent(self, n: int = 10) -> list[MemoryEntry]:
        """Get the N most recent entries."""
        return self._entries[-n:]

    def get_context_window(self, max_tokens: int = 4000) -> list[MemoryEntry]:
        """Get entries that fit within a token budget, starting from most recent.

        Args:
            max_tokens: Maximum total tokens for the context window.

        Returns:
            List of MemoryEntry entries fitting within the budget.
        """
        result: list[MemoryEntry] = []
        total = 0
        for entry in reversed(self._entries):
            if total + entry.token_count > max_tokens:
                break
            result.append(entry)
            total += entry.token_count
        result.reverse()
        return result

    def search(self, query: str, limit: int = 5) -> list[MemoryEntry]:
        """Simple keyword search through memory entries.

        Args:
            query: Search query string
            limit: Maximum results to return

        Returns:
            List of matching MemoryEntry entries
        """
        query_lower = query.lower()
        matches = [
            entry for entry in self._entries
            if query_lower in entry.content.lower()
        ]
        return matches[-limit:]

    def summarize(self) -> dict:
        """Get a summary of the conversation memory state."""
        role_counts: dict[str, int] = {}
        for entry in self._entries:
            role_counts[entry.role] = role_counts.get(entry.role, 0) + 1

        return {
            "total_entries": len(self._entries),
            "total_tokens": self._total_tokens,
            "max_entries": self.max_entries,
            "max_tokens": self.max_tokens,
            "role_counts": role_counts,
        }

    def clear(self) -> None:
        """Clear all memory entries."""
        self._entries.clear()
        self._total_tokens = 0

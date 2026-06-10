"""
Conversation Memory — Tracks multi-turn conversations with agents.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class ConversationMessage(BaseModel):
    """A single conversation message."""

    role: str  # user, assistant, system
    content: str
    timestamp: datetime = Field(default_factory=datetime.now)
    metadata: dict[str, Any] = Field(default_factory=dict)


class ConversationMemory:
    """
    Manages conversation history for agent interactions.

    Features:
    - Per-session conversation tracking
    - Automatic summarization for long conversations
    - Context window management
    """

    def __init__(self, max_messages: int = 100) -> None:
        self.max_messages = max_messages
        self.conversations: dict[str, list[ConversationMessage]] = {}

    def add_message(self, session_id: str, role: str, content: str, **metadata: Any) -> ConversationMessage:
        """Add a message to a conversation."""
        if session_id not in self.conversations:
            self.conversations[session_id] = []

        msg = ConversationMessage(role=role, content=content, metadata=metadata)
        self.conversations[session_id].append(msg)

        # Trim if over max
        if len(self.conversations[session_id]) > self.max_messages:
            self.conversations[session_id] = self.conversations[session_id][-self.max_messages:]

        return msg

    def get_history(self, session_id: str, limit: int | None = None) -> list[ConversationMessage]:
        """Get conversation history."""
        messages = self.conversations.get(session_id, [])
        if limit:
            return messages[-limit:]
        return messages

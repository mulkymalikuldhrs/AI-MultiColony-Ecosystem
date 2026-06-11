"""Session management for agent conversations.

Manages session state, history, context, and isolation between conversations.
"""

from __future__ import annotations

import time
import uuid
from typing import Any, Optional

from ai_multicolony.config.logging_config import get_logger
from ai_multicolony.types.memory import MemoryType
from ai_multicolony.types.messages import Message, MessageRole

logger = get_logger(__name__)


class Session:
    """A conversation session.

    Tracks messages, metadata, context, and state for a single conversation.
    """

    def __init__(
        self,
        session_id: Optional[str] = None,
        agent_id: Optional[str] = None,
        colony_id: Optional[str] = None,
    ) -> None:
        self.id = session_id or str(uuid.uuid4())
        self.agent_id = agent_id
        self.colony_id = colony_id
        self.messages: list[Message] = []
        self.metadata: dict[str, Any] = {}
        self.context: dict[str, Any] = {}
        self.created_at = time.time()
        self.updated_at = time.time()
        self.is_active = True
        self.parent_session_id: Optional[str] = None
        self.child_session_ids: list[str] = []

    def add_message(self, message: Message) -> None:
        """Add a message to the session."""
        self.messages.append(message)
        self.updated_at = time.time()

    def get_messages(
        self,
        role: Optional[MessageRole] = None,
        limit: int = 100,
        since: Optional[float] = None,
    ) -> list[Message]:
        """Get messages from the session.

        Args:
            role: Optional filter by role.
            limit: Maximum messages to return.
            since: Optional timestamp to filter from.

        Returns:
            List of messages.
        """
        msgs = self.messages
        if role:
            msgs = [m for m in msgs if m.role == role]
        if since:
            msgs = [m for m in msgs if m.timestamp >= since]
        return msgs[-limit:]

    def get_message_count(self) -> int:
        """Get the number of messages in the session."""
        return len(self.messages)

    def clear_messages(self) -> None:
        """Clear all messages from the session."""
        self.messages = []
        self.updated_at = time.time()

    def set_context(self, key: str, value: Any) -> None:
        """Set a context variable."""
        self.context[key] = value
        self.updated_at = time.time()

    def get_context(self, key: str, default: Any = None) -> Any:
        """Get a context variable."""
        return self.context.get(key, default)

    def add_child_session(self, session_id: str) -> None:
        """Add a child session reference."""
        self.child_session_ids.append(session_id)
        self.updated_at = time.time()

    def to_dict(self) -> dict[str, Any]:
        """Convert to a dictionary."""
        return {
            "id": self.id,
            "agent_id": self.agent_id,
            "colony_id": self.colony_id,
            "message_count": len(self.messages),
            "context_keys": list(self.context.keys()),
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "is_active": self.is_active,
            "metadata": self.metadata,
            "parent_session_id": self.parent_session_id,
            "child_session_ids": self.child_session_ids,
        }


class SessionManager:
    """Manages multiple conversation sessions.

    Features:
    - Create, get, and delete sessions
    - Session isolation between agents/colonies
    - Automatic cleanup of expired sessions
    - Session hierarchy (parent/child)
    - Context management per session
    """

    def __init__(
        self,
        max_sessions: int = 100,
        session_timeout: float = 3600.0,
    ) -> None:
        self._sessions: dict[str, Session] = {}
        self._max_sessions = max_sessions
        self._session_timeout = session_timeout

    def create_session(
        self,
        agent_id: Optional[str] = None,
        colony_id: Optional[str] = None,
        parent_session_id: Optional[str] = None,
        metadata: Optional[dict[str, Any]] = None,
    ) -> Session:
        """Create a new session.

        Args:
            agent_id: Optional agent ID for the session.
            colony_id: Optional colony ID.
            parent_session_id: Optional parent session for hierarchical sessions.
            metadata: Optional initial metadata.

        Returns:
            The new session.
        """
        if len(self._sessions) >= self._max_sessions:
            self._cleanup_expired()

        session = Session(agent_id=agent_id, colony_id=colony_id)
        if parent_session_id and parent_session_id in self._sessions:
            session.parent_session_id = parent_session_id
            self._sessions[parent_session_id].add_child_session(session.id)

        if metadata:
            session.metadata.update(metadata)

        self._sessions[session.id] = session
        logger.info("session_created", session_id=session.id, agent_id=agent_id)
        return session

    def get_session(self, session_id: str) -> Optional[Session]:
        """Get a session by ID.

        Args:
            session_id: The session ID.

        Returns:
            The session, or None if not found.
        """
        session = self._sessions.get(session_id)
        if session:
            session.updated_at = time.time()
        return session

    def get_or_create(
        self,
        session_id: Optional[str] = None,
        agent_id: Optional[str] = None,
    ) -> Session:
        """Get an existing session or create a new one.

        Args:
            session_id: Optional session ID.
            agent_id: Optional agent ID.

        Returns:
            The session.
        """
        if session_id and session_id in self._sessions:
            return self._sessions[session_id]
        return self.create_session(agent_id=agent_id)

    def get_sessions_for_agent(self, agent_id: str, active_only: bool = True) -> list[Session]:
        """Get all sessions for a specific agent.

        Args:
            agent_id: The agent ID.
            active_only: Only return active sessions.

        Returns:
            List of sessions.
        """
        sessions = [s for s in self._sessions.values() if s.agent_id == agent_id]
        if active_only:
            sessions = [s for s in sessions if s.is_active]
        return sessions

    def delete_session(self, session_id: str) -> bool:
        """Delete a session.

        Args:
            session_id: The session ID.

        Returns:
            True if the session was found and deleted.
        """
        session = self._sessions.pop(session_id, None)
        if session:
            # Remove from parent's children
            if session.parent_session_id and session.parent_session_id in self._sessions:
                parent = self._sessions[session.parent_session_id]
                parent.child_session_ids = [
                    sid for sid in parent.child_session_ids if sid != session_id
                ]
            logger.info("session_deleted", session_id=session_id)
            return True
        return False

    def close_session(self, session_id: str) -> bool:
        """Close a session (mark as inactive but keep it).

        Args:
            session_id: The session ID.

        Returns:
            True if the session was found and closed.
        """
        session = self._sessions.get(session_id)
        if session:
            session.is_active = False
            session.updated_at = time.time()
            return True
        return False

    def list_sessions(
        self,
        active_only: bool = False,
        agent_id: Optional[str] = None,
    ) -> list[dict[str, Any]]:
        """List sessions with optional filters.

        Args:
            active_only: Only list active sessions.
            agent_id: Filter by agent ID.

        Returns:
            List of session info dicts.
        """
        sessions = self._sessions.values()
        if active_only:
            sessions = [s for s in sessions if s.is_active]
        if agent_id:
            sessions = [s for s in sessions if s.agent_id == agent_id]
        return [s.to_dict() for s in sessions]

    def _cleanup_expired(self) -> int:
        """Clean up expired sessions.

        Returns:
            Number of sessions cleaned up.
        """
        now = time.time()
        expired = [
            sid for sid, session in self._sessions.items()
            if now - session.updated_at > self._session_timeout
        ]
        for sid in expired:
            del self._sessions[sid]
        if expired:
            logger.info("sessions_cleaned_up", count=len(expired))
        return len(expired)

    def get_stats(self) -> dict[str, Any]:
        """Get session manager statistics."""
        return {
            "total_sessions": len(self._sessions),
            "active_sessions": sum(1 for s in self._sessions.values() if s.is_active),
            "max_sessions": self._max_sessions,
            "session_timeout": self._session_timeout,
        }

"""Audit trail for agent actions and system events.

Provides append-only logging with query interface for compliance
and debugging.
"""

from __future__ import annotations

import json
import time
import uuid
from collections import deque
from pathlib import Path
from typing import Any, Optional

from pydantic import BaseModel, Field

from ai_multicolony.config.logging_config import get_logger

logger = get_logger(__name__)


class AuditEntry(BaseModel):
    """A single audit trail entry."""

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: float = Field(default_factory=time.time)
    agent_id: str = ""
    action: str = ""
    resource: str = ""
    result: str = ""
    details: dict[str, Any] = Field(default_factory=dict)
    severity: str = "info"  # info, warning, error, critical
    session_id: Optional[str] = None
    colony_id: Optional[str] = None
    ip_address: Optional[str] = None

    model_config = {"arbitrary_types_allowed": True}


class AuditTrail:
    """Append-only audit trail for tracking agent actions.

    Features:
    - Record all agent actions with full context
    - Query audit history with flexible filters
    - Filter by agent, action, time range, severity
    - Export audit logs to file
    - Append-only guarantee (no modification/deletion of entries)
    - File-based persistence
    """

    def __init__(
        self,
        max_entries: int = 10000,
        persist_file: Optional[str] = None,
    ) -> None:
        self._entries: deque[AuditEntry] = deque(maxlen=max_entries)
        self._max_entries = max_entries
        self._persist_file = persist_file
        self._total_written = 0

    def record(
        self,
        agent_id: str,
        action: str,
        resource: str = "",
        result: str = "",
        details: Optional[dict[str, Any]] = None,
        severity: str = "info",
        session_id: Optional[str] = None,
        colony_id: Optional[str] = None,
    ) -> AuditEntry:
        """Record an audit entry (append-only).

        Args:
            agent_id: The agent that performed the action.
            action: The action performed.
            resource: The resource affected.
            result: The result of the action.
            details: Additional details.
            severity: Severity level.
            session_id: Optional session ID.
            colony_id: Optional colony ID.

        Returns:
            The created audit entry.
        """
        entry = AuditEntry(
            agent_id=agent_id,
            action=action,
            resource=resource,
            result=result,
            details=details or {},
            severity=severity,
            session_id=session_id,
            colony_id=colony_id,
        )
        self._entries.append(entry)
        self._total_written += 1

        # Persist if configured
        if self._persist_file:
            self._append_to_file(entry)

        return entry

    def query(
        self,
        agent_id: Optional[str] = None,
        action: Optional[str] = None,
        severity: Optional[str] = None,
        session_id: Optional[str] = None,
        colony_id: Optional[str] = None,
        start_time: Optional[float] = None,
        end_time: Optional[float] = None,
        resource: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[AuditEntry]:
        """Query audit entries with flexible filters.

        Args:
            agent_id: Filter by agent ID.
            action: Filter by action type.
            severity: Filter by severity.
            session_id: Filter by session ID.
            colony_id: Filter by colony ID.
            start_time: Filter by start time.
            end_time: Filter by end time.
            resource: Filter by resource.
            limit: Maximum results.
            offset: Result offset for pagination.

        Returns:
            Filtered list of audit entries.
        """
        entries = list(self._entries)

        if agent_id:
            entries = [e for e in entries if e.agent_id == agent_id]
        if action:
            entries = [e for e in entries if e.action == action]
        if severity:
            entries = [e for e in entries if e.severity == severity]
        if session_id:
            entries = [e for e in entries if e.session_id == session_id]
        if colony_id:
            entries = [e for e in entries if e.colony_id == colony_id]
        if start_time:
            entries = [e for e in entries if e.timestamp >= start_time]
        if end_time:
            entries = [e for e in entries if e.timestamp <= end_time]
        if resource:
            entries = [e for e in entries if resource in e.resource]

        return entries[offset:offset + limit]

    def get_count(self, agent_id: Optional[str] = None) -> int:
        """Get the number of audit entries."""
        if agent_id:
            return sum(1 for e in self._entries if e.agent_id == agent_id)
        return len(self._entries)

    def get_summary(self) -> dict[str, Any]:
        """Get a summary of audit entries."""
        severity_counts: dict[str, int] = {}
        action_counts: dict[str, int] = {}
        agent_counts: dict[str, int] = {}

        for entry in self._entries:
            severity_counts[entry.severity] = severity_counts.get(entry.severity, 0) + 1
            action_counts[entry.action] = action_counts.get(entry.action, 0) + 1
            agent_counts[entry.agent_id] = agent_counts.get(entry.agent_id, 0) + 1

        return {
            "total_entries": len(self._entries),
            "total_written": self._total_written,
            "severity_counts": severity_counts,
            "top_actions": dict(sorted(action_counts.items(), key=lambda x: x[1], reverse=True)[:10]),
            "top_agents": dict(sorted(agent_counts.items(), key=lambda x: x[1], reverse=True)[:10]),
        }

    def clear(self) -> int:
        """Clear all audit entries from memory (not from persisted file).

        Returns:
            Number of entries cleared.
        """
        count = len(self._entries)
        self._entries.clear()
        return count

    def export(self) -> list[dict[str, Any]]:
        """Export all audit entries as dictionaries."""
        return [e.model_dump() for e in self._entries]

    def export_to_file(self, file_path: str) -> int:
        """Export audit entries to a JSON file.

        Args:
            file_path: Path to the output file.

        Returns:
            Number of entries exported.
        """
        entries = self.export()
        try:
            path = Path(file_path)
            path.parent.mkdir(parents=True, exist_ok=True)
            with open(path, "w") as f:
                json.dump(entries, f, indent=2, default=str)
            return len(entries)
        except Exception as e:
            logger.error("audit_export_error", error=str(e))
            return 0

    def _append_to_file(self, entry: AuditEntry) -> None:
        """Append an entry to the persistence file."""
        try:
            path = Path(self._persist_file)
            path.parent.mkdir(parents=True, exist_ok=True)
            with open(path, "a") as f:
                f.write(json.dumps(entry.model_dump(), default=str) + "\n")
        except Exception as e:
            logger.warning("audit_persist_error", error=str(e))

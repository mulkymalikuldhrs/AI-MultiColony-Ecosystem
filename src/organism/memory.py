"""
Memory Engine - Experience logging and pattern analysis.
Port of autonomous-organism/memory/index.js to Python with Pydantic v2.
"""

from __future__ import annotations

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional

from pydantic import BaseModel, Field

logger = logging.getLogger("ecosystem.organism.memory")


class MemoryEntry(BaseModel):
    """A single memory log entry."""
    id: int
    entry_type: str  # PRODUCT, AGENT, CAMPAIGN
    name: str
    result: str  # SUCCESS, FAILED, PIVOT
    reason: str
    date: str = Field(default_factory=lambda: datetime.now().isoformat())


class FailurePattern(BaseModel):
    """A pattern found in failures."""
    reason: str
    count: int


class MemoryEngine:
    """Experience logging and pattern analysis for the organism.

    Features:
    - Log outcomes (success/failed/pivot)
    - Analyze failure patterns
    - Analyze success patterns
    - Weekly review summarization
    - Persistent JSON storage
    """

    def __init__(self, storage_path: str | Path | None = None) -> None:
        self.storage_path = Path(storage_path) if storage_path else None
        self.logs: list[MemoryEntry] = []
        self._next_id = 1
        if self.storage_path:
            self._load()

    def _load(self) -> None:
        """Load logs from storage."""
        if self.storage_path and self.storage_path.exists():
            try:
                data = json.loads(self.storage_path.read_text())
                self.logs = [MemoryEntry(**entry) for entry in data]
                self._next_id = max((e.id for e in self.logs), default=0) + 1
            except (json.JSONDecodeError, Exception):
                self.logs = []

    def _save(self) -> None:
        """Save logs to storage."""
        if self.storage_path:
            self.storage_path.parent.mkdir(parents=True, exist_ok=True)
            self.storage_path.write_text(
                json.dumps([e.model_dump() for e in self.logs], indent=2)
            )

    def log(self, entry_type: str, name: str, result: str, reason: str) -> MemoryEntry:
        """Log an outcome.

        Args:
            entry_type: Type of entry (PRODUCT, AGENT, CAMPAIGN)
            name: Name of the item
            result: Outcome (SUCCESS, FAILED, PIVOT)
            reason: Reason for the outcome

        Returns:
            The created MemoryEntry
        """
        entry = MemoryEntry(
            id=self._next_id,
            entry_type=entry_type,
            name=name,
            result=result,
            reason=reason,
        )
        self.logs.append(entry)
        self._next_id += 1
        self._save()

        logger.info("Logged: %s - %s = %s", entry_type, name, result)
        return entry

    def analyze_failures(self) -> list[FailurePattern]:
        """Analyze patterns in failures.

        Returns:
            List of FailurePattern sorted by count descending.
        """
        reason_counts: dict[str, int] = {}
        for entry in self.logs:
            if entry.result == "FAILED":
                reason_counts[entry.reason] = reason_counts.get(entry.reason, 0) + 1

        patterns = [
            FailurePattern(reason=reason, count=count)
            for reason, count in sorted(reason_counts.items(), key=lambda x: x[1], reverse=True)
        ]
        return patterns[:5]

    def analyze_success(self) -> dict[str, int]:
        """Analyze patterns in successes.

        Returns:
            Dict mapping entry type to success count.
        """
        type_counts: dict[str, int] = {}
        for entry in self.logs:
            if entry.result == "SUCCESS":
                type_counts[entry.entry_type] = type_counts.get(entry.entry_type, 0) + 1
        return type_counts

    def weekly_review(self) -> dict:
        """Perform a weekly review summarizing failures and successes.

        Returns:
            Dict with failure_patterns, success_types, and recommendations.
        """
        failures = self.analyze_failures()
        successes = self.analyze_success()

        recommendations: list[str] = []
        if failures:
            recommendations.append(f"Avoid: {failures[0].reason}")
        if successes:
            recommendations.append(f"Focus: {list(successes.keys())[0]}")

        return {
            "total_entries": len(self.logs),
            "failure_patterns": [f.model_dump() for f in failures],
            "success_types": successes,
            "recommendations": recommendations,
        }

    def get_status(self) -> dict:
        """Get memory engine status."""
        return {
            "total_logs": len(self.logs),
            "storage_path": str(self.storage_path) if self.storage_path else None,
        }

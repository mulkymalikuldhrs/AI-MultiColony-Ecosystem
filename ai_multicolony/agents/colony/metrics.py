"""Colony metrics model for the Colony agent."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, Optional


class ColonyMetrics:
    """Tracks colony-level metrics for monitoring and balancing."""

    def __init__(self):
        self.total_tasks_delegated: int = 0
        self.total_tasks_completed: int = 0
        self.total_tasks_failed: int = 0
        self.heartbeat_misses: int = 0
        self.rebalance_count: int = 0
        self.last_heartbeat_check: Optional[datetime] = None

    @property
    def task_success_rate(self) -> float:
        total = self.total_tasks_completed + self.total_tasks_failed
        if total == 0:
            return 1.0
        return self.total_tasks_completed / total

    def to_dict(self) -> Dict[str, Any]:
        return {
            "total_tasks_delegated": self.total_tasks_delegated,
            "total_tasks_completed": self.total_tasks_completed,
            "total_tasks_failed": self.total_tasks_failed,
            "task_success_rate": self.task_success_rate,
            "heartbeat_misses": self.heartbeat_misses,
            "rebalance_count": self.rebalance_count,
        }

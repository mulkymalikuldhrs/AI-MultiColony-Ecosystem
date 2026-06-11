"""Task scheduling for colony operations.

Provides task scheduling with priority queue, deadline tracking,
task dependencies, and multiple scheduling strategies.
"""

from __future__ import annotations

import heapq
import time
from enum import Enum
from typing import Any, Optional

from ai_multicolony.config.logging_config import get_logger
from ai_multicolony.types.colony import ColonyTask

logger = get_logger(__name__)


class SchedulingStrategy(str, Enum):
    """Task scheduling strategies."""

    FIFO = "fifo"
    ROUND_ROBIN = "round_robin"
    PRIORITY = "priority"
    LEAST_LOADED = "least_loaded"
    DEADLINE = "deadline"


class TaskScheduler:
    """Task scheduler for colony operations.

    Features:
    - Multiple scheduling strategies (FIFO, priority, deadline)
    - Priority-based queuing with heap
    - Deadline tracking and overdue detection
    - Task dependency management
    - Timeout handling
    - Agent load tracking
    """

    def __init__(self, strategy: SchedulingStrategy = SchedulingStrategy.PRIORITY) -> None:
        self._strategy = strategy
        self._task_queue: list[ColonyTask] = []
        self._ready_queue: list[tuple[int, float, ColonyTask]] = []  # (-priority, deadline, task)
        self._running_tasks: dict[str, ColonyTask] = {}
        self._completed_tasks: dict[str, ColonyTask] = {}
        self._failed_tasks: dict[str, ColonyTask] = {}
        self._agent_loads: dict[str, int] = {}  # agent_id -> task count
        self._round_robin_index = 0
        self._dependency_graph: dict[str, set[str]] = {}  # task_id -> set of task_ids it depends on

    def add_task(self, task: ColonyTask) -> None:
        """Add a task to the queue.

        Also registers task dependencies for resolution.

        Args:
            task: The task to schedule.
        """
        self._task_queue.append(task)

        # Register dependencies
        for dep_id in task.dependencies:
            if task.id not in self._dependency_graph:
                self._dependency_graph[task.id] = set()
            self._dependency_graph[task.id].add(dep_id)

        # Add to ready queue if no pending dependencies
        if self._are_dependencies_met(task):
            priority = task.priority
            deadline = task.metadata.get("deadline", float('inf'))
            heapq.heappush(self._ready_queue, (-priority, deadline, task))

        logger.info("task_queued", task_id=task.id, title=task.title, priority=task.priority)

    def add_tasks(self, tasks: list[ColonyTask]) -> None:
        """Add multiple tasks to the queue.

        Args:
            tasks: The tasks to schedule.
        """
        for task in tasks:
            self.add_task(task)

    def _are_dependencies_met(self, task: ColonyTask) -> bool:
        """Check if all dependencies for a task are completed."""
        deps = self._dependency_graph.get(task.id, set())
        for dep_id in deps:
            if dep_id not in self._completed_tasks and dep_id not in self._running_tasks:
                # Check if dependency is still pending
                if any(t.id == dep_id for t in self._task_queue):
                    return False
        return True

    def next_task(self, agent_ids: Optional[list[str]] = None) -> Optional[ColonyTask]:
        """Get the next task to execute based on scheduling strategy.

        Args:
            agent_ids: Available agent IDs for least-loaded strategy.

        Returns:
            The next task, or None if queue is empty.
        """
        # Re-check dependency resolution for queued tasks
        self._resolve_dependencies()

        if self._strategy == SchedulingStrategy.DEADLINE:
            return self._next_by_deadline()
        elif self._strategy == SchedulingStrategy.PRIORITY:
            return self._next_by_priority()
        elif self._strategy == SchedulingStrategy.FIFO:
            return self._next_fifo()
        elif self._strategy == SchedulingStrategy.LEAST_LOADED:
            return self._next_by_priority()  # Same ordering, different assignment
        elif self._strategy == SchedulingStrategy.ROUND_ROBIN:
            return self._next_fifo()
        else:
            return self._next_by_priority()

    def _next_by_priority(self) -> Optional[ColonyTask]:
        """Get the highest priority task."""
        if not self._ready_queue:
            return None
        _, _, task = heapq.heappop(self._ready_queue)
        self._task_queue = [t for t in self._task_queue if t.id != task.id]
        return task

    def _next_by_deadline(self) -> Optional[ColonyTask]:
        """Get the task with the earliest deadline."""
        # Re-heap by deadline
        if not self._ready_queue:
            return None
        # The heap is already sorted by (-priority, deadline), let's re-sort by deadline
        tasks = []
        while self._ready_queue:
            _, _, task = heapq.heappop(self._ready_queue)
            deadline = task.metadata.get("deadline", float('inf'))
            tasks.append((deadline, task))
        if not tasks:
            return None
        tasks.sort(key=lambda x: x[0])
        _, selected = tasks.pop(0)
        # Re-add remaining
        for deadline, task in tasks:
            heapq.heappush(self._ready_queue, (-task.priority, deadline, task))
        self._task_queue = [t for t in self._task_queue if t.id != selected.id]
        return selected

    def _next_fifo(self) -> Optional[ColonyTask]:
        """Get the first task in the queue."""
        if not self._task_queue:
            return None
        # Get first task with met dependencies
        for i, task in enumerate(self._task_queue):
            if self._are_dependencies_met(task):
                self._task_queue.pop(i)
                # Remove from ready queue if present
                self._ready_queue = [
                    (p, d, t) for p, d, t in self._ready_queue if t.id != task.id
                ]
                heapq.heapify(self._ready_queue)
                return task
        return None

    def _resolve_dependencies(self) -> None:
        """Move tasks with resolved dependencies to the ready queue."""
        newly_ready = []
        remaining = []
        for task in self._task_queue:
            if task.id not in [t.id for _, _, t in self._ready_queue]:
                if self._are_dependencies_met(task):
                    priority = task.priority
                    deadline = task.metadata.get("deadline", float('inf'))
                    heapq.heappush(self._ready_queue, (-priority, deadline, task))
                    newly_ready.append(task)
        # Tasks stay in task_queue for tracking

    def mark_running(self, task_id: str, agent_id: str) -> None:
        """Mark a task as running.

        Args:
            task_id: The task ID.
            agent_id: The agent running the task.
        """
        # Find task in any queue
        task = None
        for t in self._task_queue:
            if t.id == task_id:
                task = t
                break
        if not task:
            return

        task.status = "in_progress"
        task.assigned_agent_id = agent_id
        task.started_at = time.time()
        self._running_tasks[task_id] = task
        self._agent_loads[agent_id] = self._agent_loads.get(agent_id, 0) + 1

    def mark_completed(self, task_id: str, result: Optional[str] = None) -> None:
        """Mark a task as completed.

        Args:
            task_id: The task ID.
            result: Optional result text.
        """
        task = self._running_tasks.pop(task_id, None)
        if task:
            task.status = "completed"
            task.result = result
            task.completed_at = time.time()
            self._completed_tasks[task_id] = task
            # Update agent load
            if task.assigned_agent_id:
                self._agent_loads[task.assigned_agent_id] = max(
                    0, self._agent_loads.get(task.assigned_agent_id, 0) - 1
                )
            # Resolve dependencies that might now be unblocked
            self._resolve_dependencies()

    def mark_failed(self, task_id: str, error: str) -> None:
        """Mark a task as failed.

        Args:
            task_id: The task ID.
            error: Error description.
        """
        task = self._running_tasks.pop(task_id, None)
        if task:
            task.status = "failed"
            task.error = error
            task.completed_at = time.time()
            self._failed_tasks[task_id] = task
            # Update agent load
            if task.assigned_agent_id:
                self._agent_loads[task.assigned_agent_id] = max(
                    0, self._agent_loads.get(task.assigned_agent_id, 0) - 1
                )

    def get_overdue_tasks(self) -> list[ColonyTask]:
        """Get tasks that have passed their deadline.

        Returns:
            List of overdue tasks.
        """
        now = time.time()
        overdue = []
        for task in self._running_tasks.values():
            deadline = task.metadata.get("deadline")
            if deadline and now > deadline:
                overdue.append(task)
        for task in self._task_queue:
            deadline = task.metadata.get("deadline")
            if deadline and now > deadline:
                overdue.append(task)
        return overdue

    def get_dependents(self, task_id: str) -> list[str]:
        """Get tasks that depend on a given task.

        Args:
            task_id: The task ID.

        Returns:
            List of dependent task IDs.
        """
        return [
            tid for tid, deps in self._dependency_graph.items()
            if task_id in deps
        ]

    @property
    def pending_count(self) -> int:
        """Number of pending tasks."""
        return len(self._task_queue)

    @property
    def running_count(self) -> int:
        """Number of running tasks."""
        return len(self._running_tasks)

    @property
    def completed_count(self) -> int:
        """Number of completed tasks."""
        return len(self._completed_tasks)

    @property
    def failed_count(self) -> int:
        """Number of failed tasks."""
        return len(self._failed_tasks)

    def get_stats(self) -> dict[str, Any]:
        """Get scheduler statistics."""
        return {
            "strategy": self._strategy.value,
            "pending": self.pending_count,
            "ready": len(self._ready_queue),
            "running": self.running_count,
            "completed": self.completed_count,
            "failed": self.failed_count,
            "overdue": len(self.get_overdue_tasks()),
            "agent_loads": dict(self._agent_loads),
            "dependency_count": sum(len(deps) for deps in self._dependency_graph.values()),
        }

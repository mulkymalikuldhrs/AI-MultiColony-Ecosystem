"""🤝 SecurityOrchestrator
Coordinates BugHunterAgent instances, task queue, and idle-worker assignment.
Lightweight MVP version – can be replaced by advanced scheduler later.
"""
from __future__ import annotations

import asyncio
import os
import random
from pathlib import Path
from typing import List, Dict

from agents import AGENTS_REGISTRY, get_agent_by_id

_TASK_STORE = Path("data/bug_queue.txt")


class SecurityOrchestrator:
    """Simple in-memory orchestrator for bug-hunting agents."""

    def __init__(self, team_size: int = 3) -> None:
        self.team_size = team_size
        self.team: List = []
        self.load_team()
        self.loop = asyncio.get_event_loop()

    # ------------------------------------------------------------------
    def load_team(self) -> None:
        if "bug_hunter" not in AGENTS_REGISTRY:
            raise RuntimeError("BugHunterAgent not registered – cannot create team")
        for _ in range(self.team_size):
            self.team.append(get_agent_by_id("bug_hunter")())

    # ------------------------------------------------------------------
    def add_target(self, url: str) -> None:
        with _TASK_STORE.open("a", encoding="utf-8") as fp:
            fp.write(url + "\n")

    def _pop_tasks(self, n: int) -> List[str]:
        if not _TASK_STORE.exists():
            return []
        with _TASK_STORE.open("r", encoding="utf-8") as fp:
            lines = [l.strip() for l in fp.readlines() if l.strip()]
        if not lines:
            return []
        selected = lines[:n]
        remaining = lines[n:]
        _TASK_STORE.write_text("\n".join(remaining) + ("\n" if remaining else ""))
        return selected

    # ------------------------------------------------------------------
    async def _worker(self, agent, target_url: str) -> None:
        print(f"[Orchestrator] {agent} scanning {target_url}")
        findings = agent.hunt_and_report(target_url)
        print(f"[Orchestrator] Completed scan for {target_url}: {findings.keys()}")

    async def _run_loop(self):
        while True:
            idle_agents = [a for a in self.team if getattr(a, "status", "ready") == "ready"]
            if idle_agents:
                tasks = self._pop_tasks(len(idle_agents))
                for agent, url in zip(idle_agents, tasks):
                    self.loop.create_task(self._worker(agent, url))
            await asyncio.sleep(10)

    # ------------------------------------------------------------------
    def start(self):
        print("[Orchestrator] Security orchestrator starting …")
        self.loop.create_task(self._run_loop())
        self.loop.run_forever()


# Factory for registry

def security_orchestrator_agent():
    return SecurityOrchestrator()
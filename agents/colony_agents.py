"""🌍 Colony Agent Suite
This module defines advanced multi-layered agents:
- ColonyAgent: manages a self-contained AI colony node
- AgentGeneral: high-level strategy supervisor across colonies
- AgentMayor: manages resources & scheduling inside a colony
- EliteAgent: specialized expert spawned on-demand by Mayor

All agents can spawn sub-agents via MetaAgentCreator.
"""
from __future__ import annotations

import uuid
from typing import List, Dict

from agents.meta_agent_creator import meta_agent_creator  # type: ignore


class BaseAgent:
    id: str
    name: str
    role: str
    capabilities: List[str]

    def __init__(self, name: str, role: str):
        self.id = str(uuid.uuid4())
        self.name = name
        self.role = role
        self.capabilities = []

    def info(self) -> Dict:
        return {
            "id": self.id,
            "name": self.name,
            "role": self.role,
            "capabilities": self.capabilities,
        }


class EliteAgent(BaseAgent):
    def __init__(self, specialty: str):
        super().__init__(name=f"Elite-{specialty}", role="elite")
        self.capabilities = [specialty, "rapid_task"]

    def execute(self, task: str):
        print(f"[EliteAgent] ({self.capabilities[0]}) executing {task} …")
        # Place holder for specialist logic


class AgentMayor(BaseAgent):
    def __init__(self, colony):
        super().__init__(name="Mayor", role="mayor")
        self.colony = colony
        self.capabilities = ["schedule", "resource_manage", "spawn_elite"]

    def assign_task(self, task: str, specialty: str):
        elite = EliteAgent(specialty)
        self.colony.elites.append(elite)
        elite.execute(task)


class ColonyAgent(BaseAgent):
    def __init__(self, colony_name: str):
        super().__init__(name=colony_name, role="colony")
        self.capabilities = ["self_govern", "spawn_agents", "sync_parent"]
        self.mayor = AgentMayor(self)
        self.elites: List[EliteAgent] = []

    # -- spawn new specialized agent using MetaAgentCreator
    def spawn_specialist(self, spec: str):
        print(f"[ColonyAgent] spawning specialist for {spec}")
        prompt = f"Create an agent specialized in {spec} inside colony {self.name}"
        meta_agent_creator().create_agent_from_prompt(prompt)


class AgentGeneral(BaseAgent):
    def __init__(self):
        super().__init__(name="General", role="general")
        self.colonies: List[ColonyAgent] = []
        self.capabilities = ["strategy", "create_colony", "global_sync"]

    def create_colony(self, colony_name: str):
        colony = ColonyAgent(colony_name)
        self.colonies.append(colony)
        print(f"[AgentGeneral] Colony '{colony_name}' created ✔️")
        return colony

    def overview(self):
        return {
            "total_colonies": len(self.colonies),
            "colonies": [c.info() for c in self.colonies],
        }


# Factory functions for registry

def colony_agent_factory(name: str = "Colony-Alpha"):
    return ColonyAgent(name)

def agent_general_factory():
    return AgentGeneral()
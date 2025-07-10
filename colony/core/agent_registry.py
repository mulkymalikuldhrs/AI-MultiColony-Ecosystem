# colony/core/agent_registry.py
import importlib
import pkgutil
from pathlib import Path

REGISTRY = {}

def discover_agents():
    agents_dir = Path(__file__).parent.parent / "agents"
    for module in pkgutil.iter_modules([str(agents_dir)]):
        agent_module = importlib.import_module(f"colony.agents.{module.name}")
        for attr in dir(agent_module):
            cls = getattr(agent_module, attr)
            if isinstance(cls, type) and issubclass(cls, BaseAgent) and cls is not BaseAgent:
                REGISTRY[cls.__name__] = cls

def get_agent(name):
    return REGISTRY.get(name)

def list_all_agents():
    return list(REGISTRY.keys())

discover_agents()
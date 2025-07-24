from typing import Any, Callable, Dict, List, Optional, Type


class AgentRegistry:
    """
    A centralized registry for managing AI agents.
    Agents can register themselves with metadata, allowing for dynamic loading
    and discovery within the ecosystem.
    """

    _agents: Dict[str, Dict[str, Any]] = {}
    _agent_classes: Dict[str, Type[Any]] = {}

    def register_agent(
        self, name: str, agent_class: Type[Any], metadata: Dict[str, Any]
    ):
        """
        Registers an agent with its class and metadata.
        """
        if name in self._agents:
            print(f"⚠️ Warning: Agent '{name}' is already registered. Overwriting.")

        self._agents[name] = {"name": name, "class": agent_class, "metadata": metadata}
        self._agent_classes[name] = agent_class
        print(f"✅ Agent '{name}' registered with metadata: {metadata}")

    def get_agent_info(self, name: str) -> Optional[Dict[str, Any]]:
        """
        Retrieves the information (class and metadata) for a registered agent.
        """
        return self._agents.get(name)

    def get_agent_class(self, name: str) -> Optional[Type[Any]]:
        """
        Retrieves the class for a registered agent.
        """
        return self._agent_classes.get(name)

    def get_all_agents(self) -> Dict[str, Dict[str, Any]]:
        """
        Returns a dictionary of all registered agents and their metadata.
        """
        return self._agents

    def clear_registry(self):
        """
        Clears all registered agents. Useful for testing.
        """
        self._agents.clear()
        self._agent_classes.clear()
        print("🗑️ Agent registry cleared.")


# Global instance of the AgentRegistry
agent_registry = AgentRegistry()


def register_agent(
    name: str, route: str, dependencies: List[str] = None, description: str = ""
) -> Callable:
    """
    Decorator to register an agent class with the global AgentRegistry.
    """
    if dependencies is None:
        dependencies = []

    def decorator(cls: Type[Any]) -> Type[Any]:
        metadata = {
            "id": name,  # Use name as id for consistency
            "name": name.replace("_", " ").title(),
            "route": route,
            "dependencies": dependencies,
            "description": description,
            "status": "inactive",  # Default status
        }
        agent_registry.register_agent(name, cls, metadata)
        return cls

    return decorator

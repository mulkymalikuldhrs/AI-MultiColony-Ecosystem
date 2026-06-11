"""Agent registry and factory for the AI MultiColony Ecosystem.

Provides:
- AgentRegistry: Stores agent classes, creates instances, tracks agent states.
- AgentFactory: Creates agents from config, supports dynamic registration.

The registry auto-discovers all built-in agent types and allows
runtime registration of custom agents. The factory builds fully
configured agent instances ready for execution.
"""

from __future__ import annotations

import time
from typing import Any, Optional, Type

from ai_multicolony.config.logging_config import get_logger
from ai_multicolony.core.base_agent import BaseAgent
from ai_multicolony.core.event_bus import EventBus
from ai_multicolony.core.llm_provider import LLMProvider
from ai_multicolony.core.memory_manager import MemoryManager
from ai_multicolony.core.tool_registry import ToolRegistry
from ai_multicolony.exceptions import AgentError, AgentNotFoundError
from ai_multicolony.types.agent import AgentCapabilities, AgentConfig, AgentRole, AgentState, AgentStatus

logger = get_logger(__name__)


class AgentRegistry:
    """Registry and factory for agent types.

    Stores agent classes indexed by role name, creates instances with
    configuration, and tracks the runtime state of every agent created
    through the registry.

    Supports:
    - Register agent classes by role name
    - Create agent instances with full configuration
    - Track live agent states (IDLE, RUNNING, PAUSED, etc.)
    - List available agent types and their metadata
    - Auto-discover built-in agent types on initialization
    """

    _instance: Optional[AgentRegistry] = None

    def __init__(self) -> None:
        self._agents: dict[str, Type[BaseAgent]] = {}
        self._instances: dict[str, BaseAgent] = {}
        self._states: dict[str, AgentStatus] = {}
        self._auto_discover()

    @classmethod
    def get_instance(cls) -> AgentRegistry:
        """Get the global singleton registry."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    @classmethod
    def reset(cls) -> None:
        """Reset the global registry (for testing)."""
        cls._instance = None

    # ------------------------------------------------------------------
    # Auto-discovery
    # ------------------------------------------------------------------

    def _auto_discover(self) -> None:
        """Auto-discover and register all built-in agent types.

        Each import is guarded so that a missing or broken agent module
        does not prevent the rest from loading.
        """
        _discoveries: list[tuple[str, str]] = [
            ("manus", "ai_multicolony.agents.manus.agent", "ManusAgent"),
            ("planner", "ai_multicolony.agents.planner.agent", "PlannerAgent"),
            ("executor", "ai_multicolony.agents.executor.agent", "ExecutorAgent"),
            ("coder", "ai_multicolony.agents.coder.agent", "CoderAgent"),
            ("browser", "ai_multicolony.agents.browser.agent", "BrowserAgent"),
            ("voice", "ai_multicolony.agents.voice.agent", "VoiceAgent"),
            ("security", "ai_multicolony.agents.security.agent", "SecurityAgent"),
            ("researcher", "ai_multicolony.agents.researcher.agent", "ResearcherAgent"),
            ("colony", "ai_multicolony.agents.colony.agent", "ColonyAgent"),
        ]
        for role_name, module_path, class_name in _discoveries:
            try:
                import importlib
                module = importlib.import_module(module_path)
                agent_cls = getattr(module, class_name)
                self._agents[role_name] = agent_cls
                logger.debug("auto_discovered_agent", role=role_name, cls=class_name)
            except (ImportError, AttributeError) as exc:
                logger.warning("auto_discover_skip", role=role_name, error=str(exc))

    # ------------------------------------------------------------------
    # Registration
    # ------------------------------------------------------------------

    def register(self, name: str, agent_cls: Type[BaseAgent]) -> None:
        """Register an agent class.

        Args:
            name: The agent type name (typically matches an AgentRole value).
            agent_cls: The agent class (must extend BaseAgent).
        """
        if not (isinstance(agent_cls, type) and issubclass(agent_cls, BaseAgent)):
            raise TypeError(f"Expected a BaseAgent subclass, got {agent_cls}")
        self._agents[name] = agent_cls
        logger.info("agent_registered", name=name, cls=agent_cls.__name__)

    def unregister(self, name: str) -> None:
        """Unregister an agent type by name.

        Args:
            name: The agent type name to remove.
        """
        if name in self._agents:
            del self._agents[name]
            logger.info("agent_unregistered", name=name)

    # ------------------------------------------------------------------
    # Lookup
    # ------------------------------------------------------------------

    def get(self, name: str) -> Type[BaseAgent]:
        """Get an agent class by name.

        Args:
            name: The agent type name.

        Returns:
            The agent class.

        Raises:
            KeyError: If the agent type is not found.
        """
        if name not in self._agents:
            raise KeyError(
                f"Agent type '{name}' not found. Available: {list(self._agents.keys())}"
            )
        return self._agents[name]

    # ------------------------------------------------------------------
    # Instance creation & tracking
    # ------------------------------------------------------------------

    def create(
        self,
        name: str,
        model: str = "gpt-4o",
        tools: Optional[list[str]] = None,
        capabilities: Optional[AgentCapabilities] = None,
        event_bus: Optional[EventBus] = None,
        llm_provider: Optional[LLMProvider] = None,
        tool_registry: Optional[ToolRegistry] = None,
        memory_manager: Optional[MemoryManager] = None,
        **kwargs: Any,
    ) -> BaseAgent:
        """Create an agent instance with full infrastructure wiring.

        Args:
            name: The agent type name.
            model: LLM model to use.
            tools: List of tool names the agent may call.
            capabilities: Explicit capability flags (merged with defaults).
            event_bus: Shared event bus instance.
            llm_provider: Shared LLM provider instance.
            tool_registry: Shared tool registry instance.
            memory_manager: Shared memory manager instance.
            **kwargs: Additional AgentConfig fields.

        Returns:
            A new agent instance with infrastructure injected.

        Raises:
            KeyError: If the agent type is not registered.
        """
        agent_cls = self.get(name)

        config = AgentConfig(
            role=AgentRole(name) if name in [r.value for r in AgentRole] else AgentRole.MANUS,
            model=model,
            tools=tools or [],
            **kwargs,
        )

        # Merge caller-supplied capabilities with the class default
        if capabilities is not None:
            existing = config.capabilities.model_dump()
            overrides = capabilities.model_dump()
            merged = {**existing, **{k: v for k, v in overrides.items() if v}}
            config.capabilities = AgentCapabilities(**merged)

        instance = agent_cls(config=config)

        # Wire infrastructure
        if event_bus is not None:
            instance.set_event_bus(event_bus)
        if llm_provider is not None:
            instance.set_llm_provider(llm_provider)
        if tool_registry is not None:
            instance.set_tool_registry(tool_registry)
        if memory_manager is not None:
            instance.set_memory_manager(memory_manager)

        # Track instance
        self._instances[instance.agent_id] = instance
        self._update_state(instance)

        logger.info(
            "agent_created",
            agent_id=instance.agent_id,
            name=name,
            role=config.role.value,
        )
        return instance

    def get_instance_by_id(self, agent_id: str) -> BaseAgent:
        """Retrieve a previously created agent instance by its ID.

        Args:
            agent_id: The unique agent identifier.

        Returns:
            The agent instance.

        Raises:
            AgentNotFoundError: If no instance with the given ID exists.
        """
        if agent_id not in self._instances:
            raise AgentNotFoundError(
                f"No agent instance with id '{agent_id}'",
                agent_id=agent_id,
            )
        return self._instances[agent_id]

    def _update_state(self, agent: BaseAgent) -> None:
        """Refresh the tracked state snapshot for an agent."""
        self._states[agent.agent_id] = agent.get_status()

    def refresh_states(self) -> None:
        """Refresh state snapshots for all tracked instances."""
        for agent_id, agent in self._instances.items():
            self._states[agent_id] = agent.get_status()

    def get_state(self, agent_id: str) -> AgentStatus:
        """Get the tracked state for an agent.

        Args:
            agent_id: The agent ID.

        Returns:
            The AgentStatus snapshot.

        Raises:
            AgentNotFoundError: If the agent is not tracked.
        """
        if agent_id not in self._states:
            raise AgentNotFoundError(
                f"No state for agent '{agent_id}'",
                agent_id=agent_id,
            )
        return self._states[agent_id]

    def get_agents_by_state(self, state: AgentState) -> list[BaseAgent]:
        """Get all tracked agents currently in a specific state.

        Args:
            state: The target AgentState.

        Returns:
            List of agent instances in that state.
        """
        self.refresh_states()
        return [
            self._instances[aid]
            for aid, status in self._states.items()
            if status.state == state and aid in self._instances
        ]

    def terminate_all(self) -> int:
        """Terminate all tracked agent instances.

        Returns:
            Number of agents terminated.
        """
        count = 0
        for agent in list(self._instances.values()):
            if agent.state != AgentState.TERMINATED:
                try:
                    import asyncio
                    loop = asyncio.get_event_loop()
                    if loop.is_running():
                        asyncio.ensure_future(agent.terminate())
                    else:
                        loop.run_until_complete(agent.terminate())
                except Exception:
                    agent.state = AgentState.TERMINATED
                count += 1
        return count

    # ------------------------------------------------------------------
    # Listing
    # ------------------------------------------------------------------

    def list_all(self) -> dict[str, dict[str, Any]]:
        """List all registered agent types with metadata.

        Returns:
            Dictionary of agent name -> info dict.
        """
        result: dict[str, dict[str, Any]] = {}
        for name, agent_cls in self._agents.items():
            try:
                instance = agent_cls()
                result[name] = {
                    "name": name,
                    "description": instance.config.description or agent_cls.__doc__ or "",
                    "role": instance.role.value,
                    "tools": instance.config.tools,
                    "required_tools": instance.get_required_tools(),
                    "capabilities": instance.capabilities.to_list(),
                }
            except Exception:
                result[name] = {
                    "name": name,
                    "description": agent_cls.__doc__ or "",
                }
        return result

    def list_instances(self) -> dict[str, dict[str, Any]]:
        """List all tracked agent instances with their current state.

        Returns:
            Dictionary of agent_id -> status dict.
        """
        self.refresh_states()
        return {
            aid: status.model_dump()
            for aid, status in self._states.items()
        }

    @property
    def agent_names(self) -> list[str]:
        """Names of all registered agent types."""
        return list(self._agents.keys())

    @property
    def agent_count(self) -> int:
        """Number of registered agent types."""
        return len(self._agents)

    @property
    def instance_count(self) -> int:
        """Number of tracked agent instances."""
        return len(self._instances)


class AgentFactory:
    """Factory for creating pre-configured agent instances.

    Wraps AgentRegistry with a higher-level interface that handles:
    - Building agents from config dictionaries
    - Dynamic registration of new agent classes at runtime
    - Bulk creation of agent teams
    - Shared infrastructure injection across all created agents
    """

    def __init__(
        self,
        registry: Optional[AgentRegistry] = None,
        event_bus: Optional[EventBus] = None,
        llm_provider: Optional[LLMProvider] = None,
        tool_registry: Optional[ToolRegistry] = None,
        memory_manager: Optional[MemoryManager] = None,
    ) -> None:
        self._registry = registry or AgentRegistry.get_instance()
        self._event_bus = event_bus
        self._llm_provider = llm_provider
        self._tool_registry = tool_registry
        self._memory_manager = memory_manager

    # ------------------------------------------------------------------
    # Dynamic registration
    # ------------------------------------------------------------------

    def register_agent_type(self, name: str, agent_cls: Type[BaseAgent]) -> None:
        """Dynamically register a new agent type at runtime.

        Args:
            name: The role name for the agent type.
            agent_cls: The agent class (must extend BaseAgent).
        """
        self._registry.register(name, agent_cls)
        logger.info("factory_registered_agent", name=name, cls=agent_cls.__name__)

    # ------------------------------------------------------------------
    # Single agent creation
    # ------------------------------------------------------------------

    def create_from_config(self, config: dict[str, Any]) -> BaseAgent:
        """Create an agent instance from a configuration dictionary.

        The dictionary must contain at least a ``type`` key that maps to
        a registered agent role name. All other keys are forwarded to
        AgentConfig or passed as kwargs.

        Supported top-level keys:
            type (str): Agent type name (required).
            model (str): LLM model.
            tools (list[str]): Tool names.
            name (str): Human-readable agent name.
            description (str): Agent description.
            temperature (float): LLM temperature.
            max_iterations (int): Maximum loop iterations.
            max_tokens (int): Maximum LLM tokens.
            capabilities (dict): Capability flags.
            system_prompt (str): Override system prompt.
            metadata (dict): Extra metadata.

        Args:
            config: Configuration dictionary.

        Returns:
            A new agent instance.

        Raises:
            ValueError: If ``type`` is missing or unknown.
        """
        agent_type = config.pop("type", None)
        if agent_type is None:
            raise ValueError("Agent config must include a 'type' key")

        # Extract known fields
        model = config.pop("model", "gpt-4o")
        tools = config.pop("tools", None)
        capabilities = None
        if "capabilities" in config:
            capabilities = AgentCapabilities(**config.pop("capabilities"))

        # Extract the agent instance name (distinct from the type name)
        agent_instance_name = config.pop("name", None)

        # Build keyword arguments for AgentConfig
        # Note: "name" is NOT included here because AgentRegistry.create()
        # uses its own `name` parameter for the agent TYPE name, not the
        # instance name.  We set the instance name on the config after
        # creation to avoid a keyword collision.
        config_kwargs: dict[str, Any] = {}
        for key in ("description", "temperature", "max_iterations",
                     "max_tokens", "system_prompt", "metadata", "colony_id",
                     "parent_id", "timeout"):
            if key in config:
                config_kwargs[key] = config.pop(key)

        # Remaining keys go into metadata
        if config:
            meta = config_kwargs.get("metadata", {})
            meta.update(config)
            config_kwargs["metadata"] = meta

        instance = self._registry.create(
            name=agent_type,
            model=model,
            tools=tools,
            capabilities=capabilities,
            event_bus=self._event_bus,
            llm_provider=self._llm_provider,
            tool_registry=self._tool_registry,
            memory_manager=self._memory_manager,
            **config_kwargs,
        )

        # Override the auto-generated instance name if one was provided
        if agent_instance_name is not None:
            instance.config.name = agent_instance_name

        return instance

    # ------------------------------------------------------------------
    # Team creation
    # ------------------------------------------------------------------

    def create_team(
        self,
        team_config: list[dict[str, Any]],
    ) -> dict[str, BaseAgent]:
        """Create a team of agents from a list of config dicts.

        Args:
            team_config: List of agent config dictionaries (each needs ``type``).

        Returns:
            Dictionary mapping agent name -> agent instance.
        """
        agents: dict[str, BaseAgent] = {}
        for cfg in team_config:
            # Deep-copy to avoid mutation across iterations
            agent = self.create_from_config(dict(cfg))
            agents[agent.name] = agent
        logger.info("team_created", size=len(agents), names=list(agents.keys()))
        return agents

    def create_default_team(self) -> dict[str, BaseAgent]:
        """Create the default colony team with one of each built-in type.

        Returns:
            Dictionary mapping agent name -> agent instance.
        """
        team: dict[str, BaseAgent] = {}
        for role_name in self._registry.agent_names:
            agent = self._registry.create(
                name=role_name,
                event_bus=self._event_bus,
                llm_provider=self._llm_provider,
                tool_registry=self._tool_registry,
                memory_manager=self._memory_manager,
            )
            team[agent.name] = agent
        logger.info("default_team_created", size=len(team))
        return team

    # ------------------------------------------------------------------
    # Infrastructure injection
    # ------------------------------------------------------------------

    def set_event_bus(self, bus: EventBus) -> None:
        """Set the shared event bus for future agent creations."""
        self._event_bus = bus

    def set_llm_provider(self, provider: LLMProvider) -> None:
        """Set the shared LLM provider for future agent creations."""
        self._llm_provider = provider

    def set_tool_registry(self, registry: ToolRegistry) -> None:
        """Set the shared tool registry for future agent creations."""
        self._tool_registry = registry

    def set_memory_manager(self, manager: MemoryManager) -> None:
        """Set the shared memory manager for future agent creations."""
        self._memory_manager = manager

    # ------------------------------------------------------------------
    # Delegation
    # ------------------------------------------------------------------

    @property
    def registry(self) -> AgentRegistry:
        """Access the underlying AgentRegistry."""
        return self._registry

    @property
    def available_types(self) -> list[str]:
        """List available agent type names."""
        return self._registry.agent_names

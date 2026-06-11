"""Colony lifecycle management.

Manages colony creation, configuration, scaling, and destruction.
From OpenFang colony patterns and MultiColony coordination.
"""

from __future__ import annotations

import time
from typing import Any, Optional

from ai_multicolony.config.logging_config import get_logger
from ai_multicolony.core.event_bus import EventBus
from ai_multicolony.core.llm_provider import LLMProvider
from ai_multicolony.core.memory_manager import MemoryManager
from ai_multicolony.core.tool_registry import ToolRegistry
from ai_multicolony.exceptions import ColonyError
from ai_multicolony.types.agent import AgentConfig, AgentRole
from ai_multicolony.types.colony import ColonyConfig, ColonyState, ColonyStatus

logger = get_logger(__name__)


class ColonyManager:
    """Manages colony lifecycle.

    Features:
    - Create and destroy colonies
    - Configure colony settings
    - Scale colony agent count
    - Get colony status and metrics
    - Coordinate colony agents
    """

    def __init__(
        self,
        event_bus: Optional[EventBus] = None,
        llm_provider: Optional[LLMProvider] = None,
        tool_registry: Optional[ToolRegistry] = None,
        memory_manager: Optional[MemoryManager] = None,
    ) -> None:
        self._event_bus = event_bus
        self._llm_provider = llm_provider
        self._tool_registry = tool_registry or ToolRegistry()
        self._memory_manager = memory_manager or MemoryManager()
        self._colonies: dict[str, ColonyConfig] = {}
        self._agents: dict[str, Any] = {}  # colony_id -> colony agent
        self._hand_managers: dict[str, Any] = {}  # colony_id -> HandManager

    async def create(self, name: str, model: str = "gpt-4o", **kwargs: Any) -> ColonyConfig:
        """Create a new colony.

        Args:
            name: Colony name.
            model: Default LLM model.
            **kwargs: Additional configuration.

        Returns:
            The colony configuration.
        """
        config = ColonyConfig(
            name=name,
            model=model,
            state=ColonyState.INITIALIZING,
            **{k: v for k, v in kwargs.items() if k in ColonyConfig.model_fields},
        )
        self._colonies[config.colony_id] = config

        # Create the colony agent
        try:
            from ai_multicolony.agents.colony.agent import ColonyAgent
            agent = ColonyAgent(
                config=AgentConfig(
                    role=AgentRole.COLONY,
                    name=f"{name}-overseer",
                    model=model,
                    colony_id=config.colony_id,
                )
            )
            self._agents[config.colony_id] = agent
        except Exception as e:
            logger.warning("colony_agent_creation_error", error=str(e))

        # Create hand manager
        try:
            from ai_multicolony.colony.hands import HandManager
            self._hand_managers[config.colony_id] = HandManager(config.colony_id)
        except Exception as e:
            logger.warning("hand_manager_creation_error", error=str(e))

        # Transition to active
        config.state = ColonyState.ACTIVE
        logger.info("colony_created", colony_id=config.colony_id, name=name)
        return config

    async def get_or_create(self, colony_id: str, model: str = "gpt-4o", **kwargs: Any) -> Any:
        """Get an existing colony agent or create a new one.

        Args:
            colony_id: Colony ID.
            model: LLM model.
            **kwargs: Additional config.

        Returns:
            The colony agent.
        """
        if colony_id in self._agents:
            return self._agents[colony_id]
        config = await self.create(colony_id, model=model, **kwargs)
        return self._agents.get(config.colony_id)

    async def configure(self, colony_id: str, **kwargs: Any) -> ColonyConfig:
        """Configure a colony's settings.

        Args:
            colony_id: The colony ID.
            **kwargs: Configuration fields to update.

        Returns:
            The updated colony configuration.

        Raises:
            ColonyError: If the colony is not found.
        """
        if colony_id not in self._colonies:
            raise ColonyError(f"Colony not found: {colony_id}", colony_id=colony_id)

        config = self._colonies[colony_id]
        for key, value in kwargs.items():
            if hasattr(config, key):
                setattr(config, key, value)
        config.updated_at = time.time()
        logger.info("colony_configured", colony_id=colony_id)
        return config

    async def scale(self, colony_id: str, target_agents: int) -> dict[str, Any]:
        """Scale a colony to a target number of agents.

        Args:
            colony_id: The colony ID.
            target_agents: Desired number of agents.

        Returns:
            Scaling result with current agent count.

        Raises:
            ColonyError: If the colony is not found.
        """
        if colony_id not in self._colonies:
            raise ColonyError(f"Colony not found: {colony_id}", colony_id=colony_id)

        config = self._colonies[colony_id]
        config.max_agents = max(1, target_agents)
        config.state = ColonyState.SCALING

        logger.info("colony_scaled", colony_id=colony_id, target=target_agents)

        config.state = ColonyState.ACTIVE
        return {
            "colony_id": colony_id,
            "target_agents": target_agents,
            "max_agents": config.max_agents,
            "state": config.state.value,
        }

    async def pause(self, colony_id: str) -> None:
        """Pause a colony.

        Args:
            colony_id: The colony ID.

        Raises:
            ColonyError: If the colony is not found.
        """
        if colony_id not in self._colonies:
            raise ColonyError(f"Colony not found: {colony_id}", colony_id=colony_id)
        self._colonies[colony_id].state = ColonyState.PAUSED
        logger.info("colony_paused", colony_id=colony_id)

    async def resume(self, colony_id: str) -> None:
        """Resume a paused colony.

        Args:
            colony_id: The colony ID.

        Raises:
            ColonyError: If the colony is not found.
        """
        if colony_id not in self._colonies:
            raise ColonyError(f"Colony not found: {colony_id}", colony_id=colony_id)
        self._colonies[colony_id].state = ColonyState.ACTIVE
        logger.info("colony_resumed", colony_id=colony_id)

    async def destroy(self, colony_id: str) -> None:
        """Destroy a colony.

        Args:
            colony_id: The colony ID.

        Raises:
            ColonyError: If the colony is not found.
        """
        if colony_id not in self._colonies:
            raise ColonyError(f"Colony not found: {colony_id}", colony_id=colony_id)

        config = self._colonies[colony_id]
        config.state = ColonyState.TERMINATED

        # Terminate the colony agent
        if colony_id in self._agents:
            try:
                await self._agents[colony_id].terminate()
            except Exception as e:
                logger.warning("colony_agent_terminate_error", error=str(e))
            del self._agents[colony_id]

        # Clean up hand manager
        self._hand_managers.pop(colony_id, None)

        del self._colonies[colony_id]
        logger.info("colony_destroyed", colony_id=colony_id)

    async def get_status(self, colony_id: str) -> dict[str, Any]:
        """Get the status of a colony.

        Args:
            colony_id: The colony ID.

        Returns:
            Colony status information.

        Raises:
            ColonyError: If the colony is not found.
        """
        if colony_id not in self._colonies:
            raise ColonyError(f"Colony not found: {colony_id}", colony_id=colony_id)

        config = self._colonies[colony_id]
        agent = self._agents.get(colony_id)
        hand_mgr = self._hand_managers.get(colony_id)

        agent_count = 0
        active_agents = 0
        if agent:
            agent_count = 1 + len(getattr(agent, 'subagent_ids', []))
            active_agents = 1 if getattr(agent, 'state', None) and agent.state.value == "running" else 0

        hand_status = {}
        if hand_mgr:
            hand_status = hand_mgr.get_status()

        return ColonyStatus(
            colony_id=colony_id,
            name=config.name,
            state=config.state,
            agent_count=agent_count,
            active_agents=active_agents,
            hands=hand_status,
        ).model_dump()

    def list_colonies(self) -> list[dict[str, Any]]:
        """List all colonies."""
        return [
            {
                "colony_id": config.colony_id,
                "name": config.name,
                "state": config.state.value,
                "max_agents": config.max_agents,
            }
            for config in self._colonies.values()
        ]

    def get_agent(self, colony_id: str) -> Optional[Any]:
        """Get the colony agent."""
        return self._agents.get(colony_id)

    def get_hand_manager(self, colony_id: str) -> Optional[Any]:
        """Get the hand manager for a colony."""
        return self._hand_managers.get(colony_id)

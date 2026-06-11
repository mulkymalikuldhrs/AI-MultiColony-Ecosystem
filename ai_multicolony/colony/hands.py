"""Colony hand types - 7 specialized agent groups.

From OpenFang colony hand architecture - manages specialized
agent groups (hands) within a colony:
SecurityHand, CodeHand, ResearchHand, BrowserHand, VoiceHand,
ComputeHand, IntegrationHand.
"""

from __future__ import annotations

import time
from abc import ABC, abstractmethod
from typing import Any, Optional

from ai_multicolony.config.logging_config import get_logger
from ai_multicolony.exceptions import ColonyHandError
from ai_multicolony.types.agent import AgentConfig, AgentRole
from ai_multicolony.types.colony import HandType

logger = get_logger(__name__)


class BaseHand(ABC):
    """Abstract base class for colony hands.

    Each hand represents a specialized group of agents
    with specific tools and capabilities.
    """

    hand_type: HandType = HandType.EXECUTION
    role: AgentRole = AgentRole.EXECUTOR
    tools: list[str] = []
    description: str = ""

    def __init__(self, colony_id: str, max_agents: int = 3) -> None:
        self.colony_id = colony_id
        self.max_agents = max_agents
        self._agents: list[Any] = []
        self._task_history: list[dict[str, Any]] = []

    @abstractmethod
    async def create_agents(self, count: int = 1, model: str = "gpt-4o") -> list[Any]:
        """Create agents for this hand."""
        ...

    async def assign_task(self, task: str, **kwargs: Any) -> dict[str, Any]:
        """Assign a task to the best available agent in this hand.

        Args:
            task: Task description.
            **kwargs: Additional task parameters.

        Returns:
            Assignment result.
        """
        if not self._agents:
            raise ColonyHandError(
                f"No agents in {self.hand_type.value} hand",
                colony_id=self.colony_id,
                hand_type=self.hand_type.value,
            )

        # Find an available agent
        assigned_agent = None
        for agent in self._agents:
            state = getattr(agent, 'state', None)
            if state and state.value in ("idle", "error"):
                assigned_agent = agent
                break

        if not assigned_agent:
            assigned_agent = self._agents[0]

        assignment = {
            "agent_id": getattr(assigned_agent, 'agent_id', str(id(assigned_agent))),
            "hand_type": self.hand_type.value,
            "task": task,
            "assigned_at": time.time(),
        }
        self._task_history.append(assignment)
        return assignment

    async def destroy_agents(self) -> int:
        """Destroy all agents in this hand.

        Returns:
            Number of agents destroyed.
        """
        count = len(self._agents)
        for agent in self._agents:
            try:
                await agent.terminate()
            except Exception as e:
                logger.warning("hand_agent_terminate_error", error=str(e))
        self._agents.clear()
        return count

    def get_status(self) -> dict[str, Any]:
        """Get hand status."""
        return {
            "hand_type": self.hand_type.value,
            "description": self.description,
            "agent_count": len(self._agents),
            "max_agents": self.max_agents,
            "tools": self.tools,
            "tasks_assigned": len(self._task_history),
        }


class SecurityHand(BaseHand):
    """Security hand for vulnerability analysis, penetration testing, and monitoring.

    Tools: shell, file, code, memory
    """

    hand_type = HandType.SECURITY
    role = AgentRole.SECURITY
    tools = ["shell", "file", "code", "memory"]
    description = "Security analysis, vulnerability scanning, and compliance monitoring"

    async def create_agents(self, count: int = 1, model: str = "gpt-4o") -> list[Any]:
        """Create security agents."""
        from ai_multicolony.agents.registry import AgentRegistry
        registry = AgentRegistry()
        for _ in range(min(count, self.max_agents - len(self._agents))):
            try:
                agent = registry.create(name=self.role.value, model=model, tools=self.tools)
                self._agents.append(agent)
            except Exception as e:
                logger.error("security_hand_agent_error", error=str(e))
        return self._agents[-count:]

    async def scan(self, target: str, scan_type: str = "full") -> dict[str, Any]:
        """Perform a security scan.

        Args:
            target: Target to scan.
            scan_type: Type of scan (full, quick, targeted).

        Returns:
            Scan result.
        """
        return await self.assign_task(f"Security scan ({scan_type}) on: {target}")


class CodeHand(BaseHand):
    """Code hand for development, review, and refactoring.

    Tools: code, file, shell, search, memory
    """

    hand_type = HandType.CODE
    role = AgentRole.CODER
    tools = ["code", "file", "shell", "search", "memory"]
    description = "Code development, review, testing, and refactoring"

    async def create_agents(self, count: int = 1, model: str = "gpt-4o") -> list[Any]:
        """Create code agents."""
        from ai_multicolony.agents.registry import AgentRegistry
        registry = AgentRegistry()
        for _ in range(min(count, self.max_agents - len(self._agents))):
            try:
                agent = registry.create(name=self.role.value, model=model, tools=self.tools)
                self._agents.append(agent)
            except Exception as e:
                logger.error("code_hand_agent_error", error=str(e))
        return self._agents[-count:]

    async def implement(self, specification: str) -> dict[str, Any]:
        """Implement a feature from specification.

        Args:
            specification: Feature specification.

        Returns:
            Implementation result.
        """
        return await self.assign_task(f"Implement: {specification}")


class ResearchHand(BaseHand):
    """Research hand for information gathering and analysis.

    Tools: search, browser, file, memory
    """

    hand_type = HandType.RESEARCH
    role = AgentRole.RESEARCHER
    tools = ["search", "browser", "file", "memory"]
    description = "Research, information gathering, and analysis"

    async def create_agents(self, count: int = 1, model: str = "gpt-4o") -> list[Any]:
        """Create research agents."""
        from ai_multicolony.agents.registry import AgentRegistry
        registry = AgentRegistry()
        for _ in range(min(count, self.max_agents - len(self._agents))):
            try:
                agent = registry.create(name=self.role.value, model=model, tools=self.tools)
                self._agents.append(agent)
            except Exception as e:
                logger.error("research_hand_agent_error", error=str(e))
        return self._agents[-count:]

    async def research(self, topic: str, depth: str = "medium") -> dict[str, Any]:
        """Research a topic.

        Args:
            topic: Research topic.
            depth: Research depth (shallow, medium, deep).

        Returns:
            Research result.
        """
        return await self.assign_task(f"Research ({depth}): {topic}")


class BrowserHand(BaseHand):
    """Browser hand for web automation and scraping.

    Tools: browser, search, file, memory
    """

    hand_type = HandType.BROWSER
    role = AgentRole.BROWSER
    tools = ["browser", "search", "file", "memory"]
    description = "Web automation, scraping, and testing"

    async def create_agents(self, count: int = 1, model: str = "gpt-4o") -> list[Any]:
        """Create browser agents."""
        from ai_multicolony.agents.registry import AgentRegistry
        registry = AgentRegistry()
        for _ in range(min(count, self.max_agents - len(self._agents))):
            try:
                agent = registry.create(name=self.role.value, model=model, tools=self.tools)
                self._agents.append(agent)
            except Exception as e:
                logger.error("browser_hand_agent_error", error=str(e))
        return self._agents[-count:]

    async def browse(self, url: str, action: str = "read") -> dict[str, Any]:
        """Perform a browser action.

        Args:
            url: URL to browse.
            action: Action to perform (read, screenshot, interact).

        Returns:
            Browse result.
        """
        return await self.assign_task(f"Browse ({action}): {url}")


class VoiceHand(BaseHand):
    """Voice hand for speech processing and voice interactions.

    Tools: voice, memory, channel
    """

    hand_type = HandType.VOICE
    role = AgentRole.VOICE
    tools = ["voice", "memory", "channel"]
    description = "Speech-to-text, text-to-speech, and voice interactions"

    async def create_agents(self, count: int = 1, model: str = "gpt-4o") -> list[Any]:
        """Create voice agents."""
        from ai_multicolony.agents.registry import AgentRegistry
        registry = AgentRegistry()
        for _ in range(min(count, self.max_agents - len(self._agents))):
            try:
                agent = registry.create(name=self.role.value, model=model, tools=self.tools)
                self._agents.append(agent)
            except Exception as e:
                logger.error("voice_hand_agent_error", error=str(e))
        return self._agents[-count:]

    async def process_audio(self, audio_input: str, operation: str = "transcribe") -> dict[str, Any]:
        """Process audio input.

        Args:
            audio_input: Audio input reference.
            operation: Operation (transcribe, synthesize).

        Returns:
            Processing result.
        """
        return await self.assign_task(f"Audio {operation}: {audio_input}")


class ComputeHand(BaseHand):
    """Compute hand for data processing and computation.

    Tools: file, code, shell, memory
    """

    hand_type = HandType.DATA
    role = AgentRole.EXECUTOR
    tools = ["file", "code", "shell", "memory"]
    description = "Data processing, computation, and pipeline execution"

    async def create_agents(self, count: int = 1, model: str = "gpt-4o") -> list[Any]:
        """Create compute agents."""
        from ai_multicolony.agents.registry import AgentRegistry
        registry = AgentRegistry()
        for _ in range(min(count, self.max_agents - len(self._agents))):
            try:
                agent = registry.create(name=self.role.value, model=model, tools=self.tools)
                self._agents.append(agent)
            except Exception as e:
                logger.error("compute_hand_agent_error", error=str(e))
        return self._agents[-count:]

    async def compute(self, task: str, data_source: str = "") -> dict[str, Any]:
        """Execute a compute task.

        Args:
            task: Computation task description.
            data_source: Optional data source.

        Returns:
            Computation result.
        """
        return await self.assign_task(f"Compute: {task}" + (f" (source: {data_source})" if data_source else ""))


class IntegrationHand(BaseHand):
    """Integration hand for connecting systems and managing workflows.

    Tools: channel, memory, search
    """

    hand_type = HandType.COMMUNICATION
    role = AgentRole.MANUS
    tools = ["channel", "memory", "search", "mcp"]
    description = "System integration, workflow management, and communication"

    async def create_agents(self, count: int = 1, model: str = "gpt-4o") -> list[Any]:
        """Create integration agents."""
        from ai_multicolony.agents.registry import AgentRegistry
        registry = AgentRegistry()
        for _ in range(min(count, self.max_agents - len(self._agents))):
            try:
                agent = registry.create(name=self.role.value, model=model, tools=self.tools)
                self._agents.append(agent)
            except Exception as e:
                logger.error("integration_hand_agent_error", error=str(e))
        return self._agents[-count:]

    async def integrate(self, source: str, target: str, operation: str = "sync") -> dict[str, Any]:
        """Execute an integration operation.

        Args:
            source: Source system.
            target: Target system.
            operation: Operation (sync, transform, route).

        Returns:
            Integration result.
        """
        return await self.assign_task(f"Integration ({operation}): {source} -> {target}")


# Hand type to class mapping
HAND_CLASSES: dict[HandType, type[BaseHand]] = {
    HandType.SECURITY: SecurityHand,
    HandType.CODE: CodeHand,
    HandType.RESEARCH: ResearchHand,
    HandType.BROWSER: BrowserHand,
    HandType.VOICE: VoiceHand,
    HandType.DATA: ComputeHand,
    HandType.COMMUNICATION: IntegrationHand,
}


class HandManager:
    """Manages colony hands (specialized agent groups).

    From OpenFang colony hand architecture. Creates and manages
    groups of specialized agents for different task categories.
    """

    def __init__(self, colony_id: str) -> None:
        self.colony_id = colony_id
        self._hands: dict[HandType, BaseHand] = {}
        self._max_agents_per_hand = 3

    async def create_hand(self, hand_type: HandType, count: int = 1, model: str = "gpt-4o") -> BaseHand:
        """Create a hand with agents.

        Args:
            hand_type: The hand type.
            count: Number of agents to create.
            model: LLM model for the agents.

        Returns:
            The created hand.
        """
        hand_cls = HAND_CLASSES.get(hand_type)
        if not hand_cls:
            raise ColonyHandError(
                f"Unknown hand type: {hand_type.value}",
                colony_id=self.colony_id,
                hand_type=hand_type.value,
            )

        hand = hand_cls(colony_id=self.colony_id, max_agents=self._max_agents_per_hand)
        await hand.create_agents(count=count, model=model)
        self._hands[hand_type] = hand

        logger.info("hand_created", colony_id=self.colony_id, hand_type=hand_type.value, count=len(hand._agents))
        return hand

    async def get_hand(self, hand_type: HandType) -> Optional[BaseHand]:
        """Get a hand by type."""
        return self._hands.get(hand_type)

    async def assign_task(self, hand_type: HandType, task: str) -> dict[str, Any]:
        """Assign a task to a hand.

        Args:
            hand_type: The hand type.
            task: Task description.

        Returns:
            Assignment result.
        """
        hand = self._hands.get(hand_type)
        if not hand:
            raise ColonyHandError(
                f"No agents in hand: {hand_type.value}",
                colony_id=self.colony_id,
                hand_type=hand_type.value,
            )
        return await hand.assign_task(task)

    async def destroy_hand(self, hand_type: HandType) -> int:
        """Destroy all agents in a hand.

        Args:
            hand_type: The hand type.

        Returns:
            Number of agents destroyed.
        """
        hand = self._hands.pop(hand_type, None)
        if hand:
            return await hand.destroy_agents()
        return 0

    def get_status(self) -> dict[str, Any]:
        """Get status of all hands."""
        return {
            hand_type.value: hand.get_status()
            for hand_type, hand in self._hands.items()
        }

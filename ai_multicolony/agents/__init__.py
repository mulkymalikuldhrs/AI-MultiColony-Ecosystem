"""Agent framework for AI-MultiColony.

Exports all agent classes, the registry, event bus, circuit breaker,
graph orchestration, shared state, and Pydantic state models.
"""

from .base import BaseAgent, EventBus, CircuitBreaker, RetryPolicy
from .manus import ManusAgent
from .planner import PlannerAgent
from .executor import ExecutorAgent
from .coder import CoderAgent
from .browser import BrowserAgent
from .voice import VoiceAgent
from .security import SecurityAgent
from .researcher import ResearcherAgent
from .colony import ColonyAgent
from .graph import AgentGraph, GraphNode, GraphEdge, ConditionalEdge, ParallelBranch, GraphCheckpoint
from .registry import AgentRegistry, AGENT_TYPES
from .state import (
    SharedAgentState,
    AgentStateModel,
    AgentConfig,
    ColonyState,
    TaskStateModel,
    A2AMessageState,
    HealthReport,
)

# ── Re-exports from flat modules (backward compatibility) ─────────────────────
# These classes live in the flat .py files alongside the package directories.
# They may or may not be available depending on import order.
try:
    from ai_multicolony.agents.executor.executor import SandboxConfig, SandboxHandle  # type: ignore[no-redef]
except ImportError:
    SandboxConfig = None  # type: ignore[misc,assignment]
    SandboxHandle = None  # type: ignore[misc,assignment]

try:
    from ai_multicolony.agents.coder.coder import CodeArtifact  # type: ignore[no-redef]
except ImportError:
    CodeArtifact = None  # type: ignore[misc,assignment]

try:
    from ai_multicolony.agents.browser.browser import BrowserPage  # type: ignore[no-redef]
except ImportError:
    BrowserPage = None  # type: ignore[misc,assignment]

try:
    from ai_multicolony.agents.voice.voice import VoiceSession  # type: ignore[no-redef]
except ImportError:
    VoiceSession = None  # type: ignore[misc,assignment]

try:
    from ai_multicolony.agents.researcher.researcher import ResearchDocument, ResearchReport  # type: ignore[no-redef]
except ImportError:
    ResearchDocument = None  # type: ignore[misc,assignment]
    ResearchReport = None  # type: ignore[misc,assignment]

try:
    from ai_multicolony.agents.colony.colony import ColonyMetrics  # type: ignore[no-redef]
except ImportError:
    ColonyMetrics = None  # type: ignore[misc,assignment]

__all__ = [
    # Base
    "BaseAgent", "EventBus", "CircuitBreaker", "RetryPolicy",
    # Agents
    "ManusAgent", "PlannerAgent", "ExecutorAgent",
    "CoderAgent", "BrowserAgent", "VoiceAgent",
    "SecurityAgent", "ResearcherAgent", "ColonyAgent",
    # Executor helpers
    "SandboxConfig", "SandboxHandle",
    # Coder helpers
    "CodeArtifact",
    # Browser helpers
    "BrowserPage",
    # Voice helpers
    "VoiceSession",
    # Researcher helpers
    "ResearchDocument", "ResearchReport",
    # Colony helpers
    "ColonyMetrics",
    # Graph
    "AgentGraph", "GraphNode", "GraphEdge", "ConditionalEdge",
    "ParallelBranch", "GraphCheckpoint",
    # Registry
    "AgentRegistry", "AGENT_TYPES",
    # State
    "SharedAgentState", "AgentStateModel", "AgentConfig",
    "ColonyState", "TaskStateModel", "A2AMessageState", "HealthReport",
]

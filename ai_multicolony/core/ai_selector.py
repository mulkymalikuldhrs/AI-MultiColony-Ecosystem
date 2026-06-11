"""Intelligent agent selection with dynamic discovery and provider failover.

This module replaces the legacy ``core.legacy.ai_selector`` which relied on a
hardcoded ``mock_registry``.  The modern :class:`AISelector` discovers agents
at runtime through :mod:`importlib` scanning of the ``ai_multicolony.agents``
package and integrates with :class:`ProviderRegistry` for LLM-provider-based
selection with an automatic failover chain (NIM → Groq → OpenRouter → OpenAI).

Backward compatibility
----------------------
The public API (``AISelector``, ``ai_selector``) is unchanged so that existing
code importing from the legacy module can be transparently migrated via::

    from ai_multicolony.core.ai_selector import AISelector, ai_selector

Made with ❤️ by Mulky Malikul Dhaher in Indonesia 🇮🇩
"""

from __future__ import annotations

import importlib
import pkgutil
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional, Set, Tuple, Type, TYPE_CHECKING

import structlog

from ai_multicolony.core.llm_providers import ProviderRegistry

# Lazy imports to avoid circular dependency:
#   core.__init__ → ai_selector → agents.registry → agents.manus → core.base_agent → core.__init__
# We import agents.base, agents.registry, and types inside functions that need them.
if TYPE_CHECKING:
    from ai_multicolony.agents.base import BaseAgent
    from ai_multicolony.agents.registry import AgentRegistry
    from ai_multicolony.types import AgentType

logger = structlog.get_logger(__name__)

# ── Default provider failover chain (lower number = higher priority) ──────────

DEFAULT_FAILOVER_CHAIN: List[Tuple[str, int]] = [
    ("nim", 0),
    ("groq", 1),
    ("openrouter", 2),
    ("openai", 3),
]


# ── Agent descriptor (discovered at runtime) ─────────────────────────────────


@dataclass
class AgentDescriptor:
    """Metadata for a dynamically discovered agent class.

    Attributes
    ----------
    agent_id:
        Unique identifier (typically the agent-type value).
    agent_type:
        The ``AgentType`` enum member (or its string value).
    agent_class:
        The concrete ``BaseAgent`` subclass.
    capabilities:
        Declared capabilities (from ``agent_class.capabilities()`` if
        available, otherwise empty).
    priority:
        Default priority (lower = higher priority).
    status:
        Availability status string (``"active"`` by default).
    """

    agent_id: str
    agent_type: Any  # AgentType at runtime, Any for forward-ref safety
    agent_class: Type[Any]  # Type[BaseAgent] at runtime
    capabilities: List[str] = field(default_factory=list)
    priority: int = 5
    status: str = "active"

    def to_dict(self) -> Dict[str, Any]:
        """Return a plain-dict representation suitable for legacy consumers."""
        return {
            "agent_id": self.agent_id,
            "agent_type": getattr(self.agent_type, "value", str(self.agent_type)),
            "capabilities": list(self.capabilities),
            "priority": self.priority,
            "status": self.status,
        }


# ── Dynamic discovery ────────────────────────────────────────────────────────

# The package we scan for agent modules
_AGENTS_PACKAGE: str = "ai_multicolony.agents"

# Modules inside the agents package that are *not* agent implementations
_SKIP_MODULES: Set[str] = {
    "base",
    "registry",
    "state",
    "graph",
    "__init__",
    "legacy",  # legacy sub-package – skip to avoid importing old code
}


def _lazy_import_agents_module() -> Tuple[Any, Any, Any]:
    """Lazily import agent-related modules to avoid circular imports.

    Returns
    -------
    tuple[BaseAgent, dict, AgentType]
        ``(BaseAgent, AGENT_TYPES, AgentType)``
    """
    from ai_multicolony.agents.base import BaseAgent  # noqa: F811
    from ai_multicolony.agents.registry import AGENT_TYPES
    from ai_multicolony.types import AgentType  # noqa: F811
    return BaseAgent, AGENT_TYPES, AgentType


def discover_agents(
    package_name: str = _AGENTS_PACKAGE,
    skip: Optional[Set[str]] = None,
) -> Dict[str, AgentDescriptor]:
    """Dynamically discover agent classes from the agents package.

    Scans every sub-module of *package_name* for concrete ``BaseAgent``
    subclasses and builds an :class:`AgentDescriptor` for each.

    Parameters
    ----------
    package_name:
        Dotted package path to scan.
    skip:
        Set of sub-module names to skip (e.g. ``{"legacy", "base"}``).

    Returns
    -------
    dict[str, AgentDescriptor]
        Mapping of ``agent_id`` → descriptor.

    Raises
    ------
    RuntimeError
        If the agents package cannot be imported at all.
    """
    BaseAgent, AGENT_TYPES, AgentType = _lazy_import_agents_module()

    skip = skip or _SKIP_MODULES
    discovered: Dict[str, AgentDescriptor] = {}

    # First, consume the canonical AGENT_TYPES registry which is always
    # authoritative and doesn't require scanning.
    for agent_type_enum, agent_class in AGENT_TYPES.items():
        _add_descriptor(discovered, agent_type_enum, agent_class)

    # Then scan the package for any *additional* agents not in AGENT_TYPES
    # (e.g. user-defined or plugin agents).
    try:
        package = importlib.import_module(package_name)
    except ImportError as exc:
        logger.warning("dynamic_discovery_package_missing", package=package_name, error=str(exc))
        if not discovered:
            raise RuntimeError(
                f"Cannot import agents package '{package_name}' and no agents "
                f"were found in AGENT_TYPES. Dynamic discovery failed."
            ) from exc
        return discovered

    package_path = getattr(package, "__path__", None)
    if package_path is None:
        logger.debug("dynamic_discovery_no_package_path", package=package_name)
        return discovered

    for _importer, module_name, is_pkg in pkgutil.iter_modules(package_path):
        if module_name in skip:
            continue

        full_module = f"{package_name}.{module_name}"

        try:
            mod = importlib.import_module(full_module)
        except Exception as exc:
            logger.debug("dynamic_discovery_module_skip", module=full_module, error=str(exc))
            continue

        # Walk module dict for BaseAgent subclasses
        for _attr_name, obj in vars(mod).items():
            if not isinstance(obj, type):
                continue
            if not issubclass(obj, BaseAgent):
                continue
            if obj is BaseAgent:
                continue

            # Attempt to match to an AgentType
            agent_type_enum = _agent_type_for_class(obj, AGENT_TYPES)
            if agent_type_enum is not None and agent_type_enum.value in discovered:
                continue  # already registered via AGENT_TYPES

            if agent_type_enum is None:
                # Synthesize a pseudo key for agents not in the enum
                pseudo_key = obj.__name__.lower()
                _add_descriptor_direct(discovered, pseudo_key, obj)
            else:
                _add_descriptor(discovered, agent_type_enum, obj)

    logger.info(
        "dynamic_discovery_complete",
        agents=list(discovered.keys()),
        total=len(discovered),
    )
    return discovered


def _agent_type_for_class(
    cls: Type[Any],
    agent_types: Dict[Any, Type[Any]],
) -> Any:
    """Try to map an agent class back to its ``AgentType`` enum."""
    for at, ac in agent_types.items():
        if ac is cls or issubclass(cls, ac):
            return at
    return None


def _add_descriptor(
    registry: Dict[str, AgentDescriptor],
    agent_type_enum: Any,
    agent_class: Type[Any],
) -> None:
    """Add a descriptor for a known agent type to *registry*."""
    caps = _safe_capabilities(agent_class)
    registry[agent_type_enum.value] = AgentDescriptor(
        agent_id=agent_type_enum.value,
        agent_type=agent_type_enum,
        agent_class=agent_class,
        capabilities=caps,
    )


def _add_descriptor_direct(
    registry: Dict[str, AgentDescriptor],
    key: str,
    agent_class: Type[Any],
) -> None:
    """Add a descriptor for an un-enumerated agent class."""
    BaseAgent, AGENT_TYPES, AgentType = _lazy_import_agents_module()
    caps = _safe_capabilities(agent_class)
    registry[key] = AgentDescriptor(
        agent_id=key,
        agent_type=AgentType.MANUS,  # placeholder – not in enum
        agent_class=agent_class,
        capabilities=caps,
    )


def _safe_capabilities(cls: Type[Any]) -> List[str]:
    """Attempt to read capabilities from a class without instantiation."""
    try:
        if hasattr(cls, "CAPABILITIES"):
            return list(cls.CAPABILITIES)
        # Try calling the instance method if it's not abstract
        import inspect
        sig = inspect.signature(cls.capabilities)
        if "self" in sig.parameters and len(sig.parameters) == 1:
            # Requires instance – skip
            return []
    except Exception:
        pass
    return []


# ── Capability similarity map ────────────────────────────────────────────────

_CAPABILITY_SIMILARITY: Dict[str, List[str]] = {
    "ui_design": ["frontend", "react", "design", "css"],
    "backend": ["api", "server", "database"],
    "frontend": ["ui", "react", "vue", "angular", "css"],
    "database": ["sql", "nosql", "storage", "data"],
    "deployment": ["deploy", "docker", "cloud", "devops"],
    "automation": ["script", "cli", "shell", "workflow"],
}


# ── AISelector (modern) ──────────────────────────────────────────────────────


class AISelector:
    """Intelligent agent selection with dynamic discovery and provider failover.

    Replaces the legacy mock-registry-based selector.  On instantiation the
    selector performs dynamic discovery of available agents via
    :func:`discover_agents`.  It can also integrate with a
    :class:`ProviderRegistry` so that provider health feeds into the selection
    scoring.

    Usage::

        selector = AISelector()
        best = selector.select_best_agent(
            task_type="web_app",
            required_capabilities=["frontend", "backend"],
        )

    For provider-aware selection::

        from ai_multicolony.core.llm_providers import ProviderRegistry

        prov_reg = ProviderRegistry()
        prov_reg.register("nim", NIMProvider(api_key="..."), priority=0)

        selector = AISelector(provider_registry=prov_reg)
        best = selector.select_best_agent("web_app", ["frontend"])
    """

    def __init__(
        self,
        provider_registry: Optional[ProviderRegistry] = None,
        agent_registry: Optional[AgentRegistry] = None,
    ) -> None:
        # ── Registries ────────────────────────────────────────────
        self._provider_registry = provider_registry
        self._agent_registry = agent_registry

        # ── Dynamic discovery ─────────────────────────────────────
        try:
            self._discovered_agents: Dict[str, AgentDescriptor] = discover_agents()
        except RuntimeError:
            logger.error("dynamic_discovery_failed_fallback")
            self._discovered_agents = {}

        # ── Performance tracking (legacy compat) ──────────────────
        self.selection_history: List[Dict[str, Any]] = []
        self.agent_performance: Dict[str, Dict[str, Any]] = {}
        self.capability_weights: Dict[str, float] = {
            "shell_execution": 1.0,
            "ui_design": 1.0,
            "backend": 1.0,
            "frontend": 1.0,
            "database": 1.0,
            "deployment": 1.0,
            "ai_development": 1.0,
            "automation": 1.0,
        }

    # ── Public API ────────────────────────────────────────────────

    def select_best_agent(
        self,
        task_type: str,
        required_capabilities: Optional[List[str]] = None,
        agent_registry: Optional[Dict[str, Any]] = None,
        exclude_agents: Optional[List[str]] = None,
    ) -> str:
        """Select the best agent for a given task.

        Parameters
        ----------
        task_type:
            Type of task (``"web_app"``, ``"automation"``, etc.).
        required_capabilities:
            List of required capabilities for the task.
        agent_registry:
            *Legacy parameter* – a dict of ``{agent_id: info}``.  If
            provided, the selector will use it as the source of agents
            instead of dynamic discovery, maintaining backward compat.
        exclude_agents:
            Agent IDs to skip during selection.

        Returns
        -------
        str
            The selected agent identifier.
        """
        required_capabilities = required_capabilities or []
        exclude_agents = exclude_agents or []

        # Decide on agent source: legacy dict → dynamic discovery
        if agent_registry is not None:
            agents = agent_registry
        else:
            agents = self._build_registry_from_discovery()

        if not agents:
            logger.warning("select_best_agent_no_agents", task_type=task_type)
            return "fullstack_dev"  # safe default fallback

        scores: Dict[str, float] = {}

        for agent_id, agent_info in agents.items():
            if agent_id in exclude_agents:
                continue
            if agent_info.get("status", "active") != "active":
                continue

            score = self._calculate_agent_score(
                agent_id, agent_info, task_type, required_capabilities
            )
            scores[agent_id] = score

        if not scores:
            logger.warning("select_best_agent_no_eligible", task_type=task_type)
            return "fullstack_dev"

        best_agent = max(scores, key=scores.get)  # type: ignore[arg-type]
        self._record_selection(task_type, required_capabilities, best_agent, scores)

        logger.info(
            "agent_selected",
            agent=best_agent,
            score=scores[best_agent],
            task_type=task_type,
        )
        return best_agent

    def get_agent_recommendations(
        self,
        task_type: str,
        required_capabilities: Optional[List[str]] = None,
        top_n: int = 5,
    ) -> List[Dict[str, Any]]:
        """Return ranked agent recommendations with explanations.

        Parameters
        ----------
        task_type:
            Task type to match against.
        required_capabilities:
            Optional capability list.
        top_n:
            Maximum number of recommendations.

        Returns
        -------
        list[dict[str, Any]]
            Sorted list of recommendation dicts.
        """
        required_capabilities = required_capabilities or []
        agents = self._build_registry_from_discovery()

        if not agents:
            logger.warning("get_recommendations_no_agents")
            return []

        recommendations: List[Dict[str, Any]] = []

        for agent_id, agent_info in agents.items():
            if agent_info.get("status", "active") != "active":
                continue
            score = self._calculate_agent_score(
                agent_id, agent_info, task_type, required_capabilities
            )
            recommendations.append(
                {
                    "agent_id": agent_id,
                    "score": round(score, 2),
                    "reason": self._get_recommendation_reason(agent_id, task_type),
                    "capabilities": agent_info.get("capabilities", []),
                    "estimated_time": self._estimate_completion_time(agent_id, task_type),
                }
            )

        recommendations.sort(key=lambda x: x["score"], reverse=True)
        return recommendations[:top_n]

    def update_agent_performance(
        self,
        agent_id: str,
        task_success: bool,
        completion_time: float,
        task_type: Optional[str] = None,
    ) -> None:
        """Update agent performance metrics for future scoring.

        Parameters
        ----------
        agent_id:
            The agent whose performance is being recorded.
        task_success:
            Whether the task completed successfully.
        completion_time:
            Wall-clock time in seconds.
        task_type:
            Optional task type for per-type tracking.
        """
        if agent_id not in self.agent_performance:
            self.agent_performance[agent_id] = {
                "total_tasks": 0,
                "successful_tasks": 0,
                "total_time": 0.0,
                "success_rate": 0.0,
                "avg_completion_time": 0.0,
                "task_types": {},
            }

        perf = self.agent_performance[agent_id]
        perf["total_tasks"] += 1
        if task_success:
            perf["successful_tasks"] += 1
        perf["total_time"] += completion_time
        perf["success_rate"] = perf["successful_tasks"] / perf["total_tasks"]
        perf["avg_completion_time"] = perf["total_time"] / perf["total_tasks"]

        if task_type:
            tt = perf["task_types"]
            if task_type not in tt:
                tt[task_type] = {"count": 0, "success": 0}
            tt[task_type]["count"] += 1
            if task_success:
                tt[task_type]["success"] += 1

    def optimize_selection_weights(self) -> None:
        """Adjust capability weights based on historical performance data."""
        successful = [
            s for s in self.selection_history if s.get("task_success", True)
        ]

        for capability in list(self.capability_weights.keys()):
            total_with_cap = len([
                s
                for s in self.selection_history
                if capability in s.get("required_capabilities", [])
            ])
            if total_with_cap <= 10:
                continue

            success_with_cap = len([
                s
                for s in successful
                if capability in s.get("required_capabilities", [])
            ])
            rate = success_with_cap / total_with_cap

            if rate > 0.8:
                self.capability_weights[capability] *= 1.1
            elif rate < 0.6:
                self.capability_weights[capability] *= 0.9

            self.capability_weights[capability] = max(
                0.1, min(2.0, self.capability_weights[capability])
            )

    def get_selection_analytics(self) -> Dict[str, Any]:
        """Return analytics on agent selection patterns."""
        if not self.selection_history:
            return {"message": "No selection history available"}

        agent_usage: Dict[str, int] = {}
        task_type_dist: Dict[str, int] = {}

        for sel in self.selection_history:
            agent_usage[sel["selected_agent"]] = agent_usage.get(sel["selected_agent"], 0) + 1
            task_type_dist[sel["task_type"]] = task_type_dist.get(sel["task_type"], 0) + 1

        most_used = sorted(agent_usage.items(), key=lambda x: x[1], reverse=True)[:5]
        common_tasks = sorted(task_type_dist.items(), key=lambda x: x[1], reverse=True)[:5]

        return {
            "total_selections": len(self.selection_history),
            "most_used_agents": most_used,
            "common_task_types": common_tasks,
            "current_weights": self.capability_weights,
            "agents_with_performance_data": len(self.agent_performance),
            "discovered_agents": list(self._discovered_agents.keys()),
        }

    # ── Discovery helpers ─────────────────────────────────────────

    @property
    def discovered_agents(self) -> Dict[str, AgentDescriptor]:
        """Return the current discovered-agent mapping."""
        return dict(self._discovered_agents)

    def refresh_discovery(self) -> None:
        """Re-run dynamic agent discovery."""
        try:
            self._discovered_agents = discover_agents()
            logger.info("discovery_refreshed", total=len(self._discovered_agents))
        except RuntimeError as exc:
            logger.error("discovery_refresh_failed", error=str(exc))

    def _build_registry_from_discovery(self) -> Dict[str, Dict[str, Any]]:
        """Convert discovered agents to the legacy dict format."""
        # If a live AgentRegistry is available, merge live instance info
        live_info: Dict[str, Dict[str, Any]] = {}
        if self._agent_registry is not None:
            for agent in self._agent_registry.list_agents():
                try:
                    caps = list(agent.capabilities())
                except Exception:
                    caps = []
                live_info[agent.agent_id] = {
                    "capabilities": caps,
                    "priority": getattr(agent, "priority", 5),
                    "status": "active" if agent.state.value in ("ready", "active") else "inactive",
                }

        # Merge: discovered descriptors + live instances
        registry: Dict[str, Dict[str, Any]] = {}
        for agent_id, desc in self._discovered_agents.items():
            registry[agent_id] = desc.to_dict()

        # Live instances override (more up-to-date)
        registry.update(live_info)
        return registry

    # ── Scoring ───────────────────────────────────────────────────

    def _calculate_agent_score(
        self,
        agent_id: str,
        agent_info: Dict[str, Any],
        task_type: str,
        required_capabilities: List[str],
    ) -> float:
        """Calculate a composite score for an agent.

        Score components:
        * Base priority (weight 10)
        * Capability match (weight 50)
        * Performance history (weight 30)
        * Load balance (weight 20)
        * Task specialization (weight 40)
        * Provider health bonus (weight 25)
        """
        score = 0.0

        # Base priority
        score += agent_info.get("priority", 5) * 10

        # Capability match
        score += (
            self._calculate_capability_score(
                agent_info.get("capabilities", []), required_capabilities
            )
            * 50
        )

        # Performance history
        score += self._get_performance_score(agent_id) * 30

        # Load balance
        score += self._get_load_balance_score(agent_id) * 20

        # Task specialization
        score += self._get_specialization_score(agent_id, task_type) * 40

        # Provider health bonus (if provider registry is wired)
        score += self._get_provider_health_score(agent_id) * 25

        return score

    def _calculate_capability_score(
        self,
        agent_capabilities: List[str],
        required_capabilities: List[str],
    ) -> float:
        """Score how well agent capabilities match requirements."""
        if not required_capabilities:
            return 0.5

        matches = 0.0
        total_weight = 0.0

        for req_cap in required_capabilities:
            weight = self.capability_weights.get(req_cap, 1.0)
            total_weight += weight

            if req_cap in agent_capabilities:
                matches += weight
                continue

            # Partial / keyword match
            for agent_cap in agent_capabilities:
                if self._capabilities_similar(req_cap, agent_cap):
                    matches += weight * 0.7
                    break

        return matches / total_weight if total_weight > 0 else 0.0

    @staticmethod
    def _capabilities_similar(cap1: str, cap2: str) -> bool:
        """Check if two capability strings are similar."""
        for base_cap, similar_caps in _CAPABILITY_SIMILARITY.items():
            if cap1 == base_cap and any(sim in cap2.lower() for sim in similar_caps):
                return True
            if cap2 == base_cap and any(sim in cap1.lower() for sim in similar_caps):
                return True
        return False

    def _get_performance_score(self, agent_id: str) -> float:
        """Score based on historical performance data."""
        if agent_id not in self.agent_performance:
            return 0.5

        perf = self.agent_performance[agent_id]
        success_rate = perf.get("success_rate", 0.5)
        avg_time = perf.get("avg_completion_time", 300)
        total_tasks = perf.get("total_tasks", 0)

        score = success_rate
        score += max(0, 1 - (avg_time / 3600)) * 0.3
        score += min(0.2, total_tasks / 100)
        return min(1.0, score)

    def _get_load_balance_score(self, agent_id: str) -> float:
        """Score based on recent assignment load."""
        recent = len([
            s for s in self.selection_history[-50:]
            if s.get("selected_agent") == agent_id
        ])
        if recent == 0:
            return 1.0
        elif recent <= 2:
            return 0.8
        elif recent <= 5:
            return 0.6
        elif recent <= 10:
            return 0.4
        return 0.2

    @staticmethod
    def _get_specialization_score(agent_id: str, task_type: str) -> float:
        """Score based on agent-task specialization mapping."""
        specializations: Dict[str, List[str]] = {
            "manus": ["automation", "cli", "system_admin", "scripting"],
            "browser": ["web_browsing", "scraping", "ui_testing"],
            "planner": ["project_setup", "architecture", "scaffolding"],
            "coder": ["web_app", "mobile_app", "coding", "development"],
            "executor": ["execution", "sandbox", "runtime", "deployment"],
            "security": ["security", "audit", "vulnerability", "compliance"],
            "researcher": ["research", "analysis", "data_processing", "nlp"],
            "colony": ["colony_management", "coordination", "orchestration"],
            "voice": ["voice_processing", "speech", "audio", "nlp"],
            # Legacy IDs (kept for backward compat)
            "cybershell": ["automation", "cli", "system_admin", "scripting"],
            "ui_designer": ["web_app", "mobile_app", "design", "frontend"],
            "dev_engine": ["project_setup", "architecture", "scaffolding"],
            "fullstack_dev": ["web_app", "mobile_app", "api", "full_development"],
            "backend_dev": ["api", "backend", "server", "database"],
            "frontend_dev": ["web_app", "mobile_app", "ui", "frontend"],
            "data_sync": ["database", "data_processing", "sync", "storage"],
            "github_agent": ["version_control", "ci_cd", "deployment", "collaboration"],
            "deploy_manager": ["deployment", "cloud", "devops", "infrastructure"],
            "web3_plugin": ["blockchain", "smart_contracts", "defi", "crypto"],
            "voice_agent": ["voice_processing", "speech", "audio", "nlp"],
        }

        specs = specializations.get(agent_id, [])
        if task_type in specs:
            return 1.0
        for spec in specs:
            if spec in task_type or task_type in spec:
                return 0.7
        return 0.1

    def _get_provider_health_score(self, agent_id: str) -> float:
        """Bonus score derived from provider health (if wired).

        If a :class:`ProviderRegistry` is available and the agent's preferred
        provider is healthy the agent gets a boost.  Unhealthy or missing
        providers reduce the score slightly.
        """
        if self._provider_registry is None:
            return 0.5  # neutral when no provider registry

        health_map = self._provider_registry.get_health()
        active = self._provider_registry.active_provider

        if active and active in health_map:
            h = health_map[active]
            if h.available:
                return 1.0
            return 0.2

        # Any provider available?
        for name, h in health_map.items():
            if h.available:
                return 0.7

        return 0.0

    # ── Recording / reporting ─────────────────────────────────────

    def _record_selection(
        self,
        task_type: str,
        required_capabilities: List[str],
        selected_agent: str,
        all_scores: Dict[str, float],
    ) -> None:
        """Record a selection for analytics and self-optimization."""
        record = {
            "timestamp": datetime.now().isoformat(),
            "task_type": task_type,
            "required_capabilities": required_capabilities,
            "selected_agent": selected_agent,
            "all_scores": all_scores,
            "selection_reason": self._generate_selection_reason(selected_agent, all_scores),
        }
        self.selection_history.append(record)
        if len(self.selection_history) > 1000:
            self.selection_history = self.selection_history[-1000:]

    @staticmethod
    def _generate_selection_reason(selected_agent: str, scores: Dict[str, float]) -> str:
        """Human-readable explanation of why an agent was selected."""
        max_score = scores.get(selected_agent, 0)
        other_scores = [s for a, s in scores.items() if a != selected_agent]

        if not other_scores:
            return f"Only available agent: {selected_agent}"

        margin = max_score - max(other_scores)
        if margin > 20:
            return f"Clear best choice: {selected_agent} (score: {max_score:.1f})"
        elif margin > 10:
            return f"Good match: {selected_agent} (score: {max_score:.1f})"
        return f"Close decision: {selected_agent} (score: {max_score:.1f})"

    def _get_recommendation_reason(self, agent_id: str, task_type: str) -> str:
        """Return a short reason for recommending an agent."""
        desc = self._discovered_agents.get(agent_id)
        if desc:
            caps = ", ".join(desc.capabilities[:3]) or "general purpose"
            return f"Capabilities: {caps}"
        return f"Suitable for {task_type} tasks"

    def _estimate_completion_time(self, agent_id: str, task_type: str) -> str:
        """Return a human-readable time estimate."""
        if agent_id in self.agent_performance:
            avg_time = self.agent_performance[agent_id].get("avg_completion_time", 300)
        else:
            avg_time = 300

        complexity: Dict[str, float] = {
            "web_app": 2.0,
            "mobile_app": 2.5,
            "automation": 1.0,
            "ui_design": 1.5,
            "backend": 1.8,
            "deployment": 1.2,
        }
        est = avg_time * complexity.get(task_type, 1.0)

        if est < 60:
            return f"{int(est)}s"
        elif est < 3600:
            return f"{int(est / 60)}min"
        return f"{est / 3600:.1f}h"


# ── Module-level singleton (backward compat with legacy module) ───────────────

class _LazySingleton:
    """Lazy proxy that defers ``AISelector`` instantiation until first access.

    Avoids circular-import issues because the heavy discovery logic runs only
    when the selector is actually *used*, not at import time.
    """

    def __init__(self) -> None:
        self._instance: Optional[AISelector] = None

    def _get(self) -> AISelector:
        if self._instance is None:
            self._instance = AISelector()
        return self._instance

    # Delegate attribute access
    def __getattr__(self, name: str) -> Any:
        return getattr(self._get(), name)

    # Allow pickling / copy
    def __reduce__(self) -> Tuple[Any, ...]:
        return (_LazySingleton, ())


ai_selector = _LazySingleton()


# ``__getattr__`` at module level so that ``from ai_multicolony.core.ai_selector import ai_selector``
# still works while also avoiding eager instantiation.

__all__ = [
    "AISelector",
    "AgentDescriptor",
    "ai_selector",
    "discover_agents",
    "DEFAULT_FAILOVER_CHAIN",
]

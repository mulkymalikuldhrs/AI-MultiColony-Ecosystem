"""
Integration Adapters - Connect all ecosystem modules together.

Provides:
- EcosystemBus: Central message bus for inter-module communication
- QuantAdapter: Connects quant tools to the agent system
- OrganismAdapter: Connects organism modules to colony management
- GatewayAdapter: Connects API gateway to the ecosystem
- BackendAdapter: Connects backend services (memory, persistence, skills)
"""

from __future__ import annotations

import logging
from datetime import datetime
from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, Field

from src.quant.risk_officer import RiskOfficerTool
from src.quant.kill_switch import KillSwitchTool
from src.quant.pressure_engine import PressureNormalizationEngine
from src.quant.decision_engine import DecisionSynthesisEngine
from src.quant.market_state import MarketStateEngine
from src.quant.news_sentinel import NewsSentinelTool
from src.quant.autoswitch import AutoSwitchEngine
from src.organism.scheduler import OrganismScheduler, CycleType
from src.organism.immune import ImmuneSystem
from src.organism.decision import DecisionCore
from src.organism.memory import MemoryEngine
from src.gateway.router import APIRouter, Route, HTTPMethod
from src.gateway.middleware import MiddlewarePipeline, RateLimitMiddleware, AuthMiddleware, LoggingMiddleware
from src.gateway.localization import LocalizationManager
from src.backend.memory import ConversationMemory
from src.backend.persistence import PersistenceEngine
from src.backend.skills import SkillManager, SkillDefinition
from src.backend.middleware import AgentMiddlewarePipeline, LoopDetectionMiddleware, TokenBudgetMiddleware

logger = logging.getLogger("ecosystem.integration")


class MessageType(str, Enum):
    """Types of messages on the ecosystem bus."""
    TRADE_SIGNAL = "trade_signal"
    RISK_ALERT = "risk_alert"
    REGIME_CHANGE = "regime_change"
    NEWS_EVENT = "news_event"
    ORGANISM_CYCLE = "organism_cycle"
    SKILL_REGISTERED = "skill_registered"
    MEMORY_UPDATE = "memory_update"
    SYSTEM_STATUS = "system_status"


class BusMessage(BaseModel):
    """A message on the ecosystem bus."""
    type: MessageType
    source: str
    payload: dict = Field(default_factory=dict)
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())


class EcosystemBus:
    """Central message bus for inter-module communication.

    Provides publish/subscribe pattern for loose coupling between modules.
    """

    def __init__(self) -> None:
        self._subscribers: dict[MessageType, list] = {}
        self._history: list[BusMessage] = []

    def subscribe(self, message_type: MessageType, callback) -> None:
        """Subscribe to a message type."""
        if message_type not in self._subscribers:
            self._subscribers[message_type] = []
        self._subscribers[message_type].append(callback)

    def publish(self, message: BusMessage) -> int:
        """Publish a message to all subscribers.

        Returns the number of subscribers that received the message.
        """
        self._history.append(message)
        if len(self._history) > 1000:
            self._history = self._history[-500:]

        subscribers = self._subscribers.get(message.type, [])
        for callback in subscribers:
            try:
                callback(message)
            except Exception as e:
                logger.error("Bus subscriber error: %s", e)

        return len(subscribers)


class QuantAdapter:
    """Connects quant trading tools to the ecosystem agent system.

    Provides a unified interface for:
    - Risk-gated trade execution
    - Pressure-based signal synthesis
    - Market regime-aware decision making
    """

    def __init__(self, bus: EcosystemBus | None = None) -> None:
        self.bus = bus or EcosystemBus()
        self.risk_officer = RiskOfficerTool()
        self.kill_switch = KillSwitchTool()
        self.pressure_engine = PressureNormalizationEngine()
        self.decision_engine = DecisionSynthesisEngine()
        self.market_state = MarketStateEngine()
        self.news_sentinel = NewsSentinelTool()
        self.autoswitch = AutoSwitchEngine()

    def evaluate_trade(
        self,
        symbol: str,
        direction: str,
        lot_size: float,
        entry: float,
        stop_loss: float,
        take_profit: float | None = None,
        account_balance: float = 10000.0,
    ) -> dict:
        """Evaluate a trade through risk + kill switch + decision pipeline.

        Returns a dict with risk_check, kill_switch_status, and final decision.
        """
        # Check kill switch first
        if self.kill_switch.is_active:
            return {
                "allowed": False,
                "reason": "Kill switch is active",
                "kill_switch": self.kill_switch.status(),
            }

        # Risk check
        risk_result = self.risk_officer.check_trade(
            symbol=symbol,
            direction=direction,
            lot_size=lot_size,
            entry=entry,
            stop_loss=stop_loss,
            account_balance=account_balance,
            take_profit=take_profit,
        )

        if risk_result.verdict == "VETOED":
            self.bus.publish(BusMessage(
                type=MessageType.RISK_ALERT,
                source="quant_adapter",
                payload={"symbol": symbol, "verdict": "VETOED"},
            ))
            return {
                "allowed": False,
                "reason": "Risk officer vetoed",
                "risk_check": risk_result.model_dump(),
            }

        return {
            "allowed": True,
            "risk_check": risk_result.model_dump(),
            "kill_switch": self.kill_switch.status(),
        }


class OrganismAdapter:
    """Connects organism modules to colony management.

    Provides:
    - Scheduled cycle execution
    - Immune system protection
    - Decision scoring
    - Experience logging
    """

    def __init__(self, bus: EcosystemBus | None = None) -> None:
        self.bus = bus or EcosystemBus()
        self.scheduler = OrganismScheduler()
        self.immune = ImmuneSystem()
        self.decision = DecisionCore()
        self.memory = MemoryEngine()

    async def run_scheduled_cycle(self) -> dict:
        """Run scheduled organism cycles."""
        callbacks = {
            CycleType.HOURLY: self._hourly_action,
            CycleType.DAILY: self._daily_action,
            CycleType.WEEKLY: self._weekly_action,
            CycleType.MONTHLY: self._monthly_action,
        }
        results = await self.scheduler.run_all(callbacks)
        return {ct.value: executed for ct, executed in results.items()}

    async def _hourly_action(self) -> None:
        """Hourly cycle: scan for problems, update analytics."""
        self.bus.publish(BusMessage(
            type=MessageType.ORGANISM_CYCLE,
            source="organism_adapter",
            payload={"cycle": "hourly"},
        ))

    async def _daily_action(self) -> None:
        """Daily cycle: build products, collect revenue."""
        self.bus.publish(BusMessage(
            type=MessageType.ORGANISM_CYCLE,
            source="organism_adapter",
            payload={"cycle": "daily"},
        ))

    async def _weekly_action(self) -> None:
        """Weekly cycle: kill failures, analyze patterns."""
        review = self.memory.weekly_review()
        self.bus.publish(BusMessage(
            type=MessageType.ORGANISM_CYCLE,
            source="organism_adapter",
            payload={"cycle": "weekly", "review": review},
        ))

    async def _monthly_action(self) -> None:
        """Monthly cycle: evaluate species, spawn new agents."""
        self.bus.publish(BusMessage(
            type=MessageType.ORGANISM_CYCLE,
            source="organism_adapter",
            payload={"cycle": "monthly"},
        ))


class GatewayAdapter:
    """Connects the API gateway to the ecosystem.

    Sets up routes, middleware, and localization for the
    AI-MultiColony-Ecosystem API.
    """

    def __init__(self, bus: EcosystemBus | None = None) -> None:
        self.bus = bus or EcosystemBus()
        self.router = APIRouter()
        self.middleware = MiddlewarePipeline()
        self.localization = LocalizationManager()

    def setup_default_routes(self) -> None:
        """Set up default API routes for the ecosystem."""
        routes = [
            Route(path="/api/health", method=HTTPMethod.GET, handler_name="health_check", description="System health check"),
            Route(path="/api/agents", method=HTTPMethod.GET, handler_name="list_agents", description="List all agents"),
            Route(path="/api/agents/{agent_id}", method=HTTPMethod.GET, handler_name="get_agent", auth_required=True, description="Get agent details"),
            Route(path="/api/quant/evaluate", method=HTTPMethod.POST, handler_name="evaluate_trade", auth_required=True, rate_limit=30, description="Evaluate a trade"),
            Route(path="/api/quant/regime", method=HTTPMethod.GET, handler_name="get_regime", description="Get current market regime"),
            Route(path="/api/organism/status", method=HTTPMethod.GET, handler_name="organism_status", description="Get organism status"),
            Route(path="/api/skills", method=HTTPMethod.GET, handler_name="list_skills", description="List available skills"),
            Route(path="/api/threads", method=HTTPMethod.GET, handler_name="list_threads", auth_required=True, description="List conversation threads"),
            Route(path="/api/threads/{thread_id}", method=HTTPMethod.GET, handler_name="get_thread", auth_required=True, description="Get thread details"),
        ]
        self.router.add_routes(routes)

    def setup_default_middleware(self) -> None:
        """Set up default middleware pipeline."""
        self.middleware.add(LoggingMiddleware())
        self.middleware.add(RateLimitMiddleware(default_limit=60))
        self.middleware.add(AuthMiddleware())

    def setup_default_localization(self) -> None:
        """Set up default localization strings."""
        self.localization.register_locale(
            __import__("src.gateway.localization", fromlist=["LocaleConfig"]).LocaleConfig(code="id", name="Bahasa Indonesia")
        )
        self.localization.add_strings("en", {
            "health.ok": "System is healthy",
            "agent.not_found": "Agent not found",
            "trade.vetoed": "Trade vetoed by risk officer",
            "auth.required": "Authentication required",
        })
        self.localization.add_strings("id", {
            "health.ok": "Sistem sehat",
            "agent.not_found": "Agen tidak ditemukan",
            "trade.vetoed": "Trade ditolak oleh risk officer",
            "auth.required": "Autentikasi diperlukan",
        })


class BackendAdapter:
    """Connects backend services to the ecosystem.

    Manages conversation memory, persistence, skills, and agent middleware.
    """

    def __init__(self, bus: EcosystemBus | None = None, data_dir: str | None = None) -> None:
        self.bus = bus or EcosystemBus()
        self.memory = ConversationMemory()
        self.persistence = PersistenceEngine(data_dir)
        self.skills = SkillManager()
        self.agent_middleware = AgentMiddlewarePipeline()

        # Setup default agent middleware
        self.agent_middleware.add(LoopDetectionMiddleware(max_iterations=10))
        self.agent_middleware.add(TokenBudgetMiddleware(max_tokens=100000))

    def register_default_skills(self) -> None:
        """Register default ecosystem skills."""
        default_skills = [
            SkillDefinition(name="quant-analysis", description="Quantitative market analysis", category="trading"),
            SkillDefinition(name="risk-assessment", description="Risk assessment and management", category="trading"),
            SkillDefinition(name="code-generation", description="Code generation and review", category="development"),
            SkillDefinition(name="web-search", description="Web search and information retrieval", category="research"),
            SkillDefinition(name="data-analysis", description="Data analysis and visualization", category="analytics"),
        ]
        for skill in default_skills:
            try:
                self.skills.register(skill)
            except ValueError:
                pass  # Already registered


class EcosystemOrchestrator:
    """Top-level orchestrator that connects all adapters.

    This is the main entry point for the integrated AI-MultiColony-Ecosystem.
    """

    def __init__(self, data_dir: str | None = None) -> None:
        self.bus = EcosystemBus()
        self.quant = QuantAdapter(bus=self.bus)
        self.organism = OrganismAdapter(bus=self.bus)
        self.gateway = GatewayAdapter(bus=self.bus)
        self.backend = BackendAdapter(bus=self.bus, data_dir=data_dir)

        # Setup defaults
        self.gateway.setup_default_routes()
        self.gateway.setup_default_middleware()
        self.gateway.setup_default_localization()
        self.backend.register_default_skills()

    def get_system_status(self) -> dict:
        """Get comprehensive system status across all modules."""
        return {
            "quant": {
                "regime": self.quant.market_state.get_regime(),
                "kill_switch": self.quant.kill_switch.status(),
                "risk_status": self.quant.risk_officer.status(),
                "autoswitch": self.quant.autoswitch.get_status(),
                "news_events": len(self.quant.news_sentinel.events),
            },
            "organism": {
                "scheduler": self.organism.scheduler.get_status(),
                "immune": self.organism.immune.get_status(),
                "memory": self.organism.memory.get_status(),
            },
            "gateway": {
                "routes": len(self.gateway.router.routes),
                "localization": self.gateway.localization.get_status(),
            },
            "backend": {
                "memory": self.backend.memory.summarize(),
                "persistence": self.backend.persistence.get_status(),
                "skills": self.backend.skills.get_status(),
            },
        }

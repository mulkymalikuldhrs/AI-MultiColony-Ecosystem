"""Pressure Synthesis — Weighted signal aggregation from multi-agent analysis.

Combines signals from multiple agents into a unified pressure vector
that drives the final trading decision. Supports configurable weights,
confidence thresholds, and risk-adjusted aggregation.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class SignalDirection(str, Enum):
    """Signal direction."""
    BULLISH = "bullish"
    BEARISH = "bearish"
    NEUTRAL = "neutral"


@dataclass
class AgentSignal:
    """A single agent's signal contribution.

    Attributes:
        agent_name: Name of the contributing agent.
        direction: Signal direction (bullish/bearish/neutral).
        confidence: Confidence score [0.0, 1.0].
        weight: Weight multiplier for this agent's contribution.
        reasoning: Human-readable reasoning for the signal.
        metadata: Additional agent-specific data.
    """
    agent_name: str = ""
    direction: SignalDirection = SignalDirection.NEUTRAL
    confidence: float = 0.0
    weight: float = 1.0
    reasoning: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PressureSynthesisConfig:
    """Configuration for pressure synthesis.

    Attributes:
        min_agents: Minimum number of agents required for synthesis.
        confidence_threshold: Minimum confidence to include a signal.
        risk_weight_multiplier: Extra weight for risk agent signals.
        max_conflict_ratio: Maximum ratio of conflicting signals before hold.
    """
    min_agents: int = 3
    confidence_threshold: float = 0.3
    risk_weight_multiplier: float = 2.0
    max_conflict_ratio: float = 0.7


@dataclass
class PressureResult:
    """Result of pressure synthesis.

    Attributes:
        direction: Aggregated direction.
        confidence: Aggregated confidence.
        bullish_pressure: Sum of bullish weights.
        bearish_pressure: Sum of bearish weights.
        contributing_agents: Number of agents that contributed.
        conflict_ratio: Ratio of conflicting signals.
    """
    direction: SignalDirection = SignalDirection.NEUTRAL
    confidence: float = 0.0
    bullish_pressure: float = 0.0
    bearish_pressure: float = 0.0
    contributing_agents: int = 0
    conflict_ratio: float = 0.0


class PressureSynthesizer:
    """Aggregates multi-agent signals into a unified pressure vector.

    Uses weighted confidence aggregation with risk-adjusted weighting.
    Risk agent signals receive a configurable multiplier.
    """

    def __init__(self, config: Optional[PressureSynthesisConfig] = None) -> None:
        self._config = config or PressureSynthesisConfig()

    def synthesize(self, signals: List[AgentSignal]) -> PressureResult:
        """Synthesize a list of agent signals into a pressure result.

        Args:
            signals: List of agent signals to aggregate.

        Returns:
            PressureResult with aggregated direction, confidence, and pressures.
        """
        if not signals:
            return PressureResult()

        # Filter by confidence threshold
        valid_signals = [s for s in signals if s.confidence >= self._config.confidence_threshold]
        if len(valid_signals) < self._config.min_agents:
            logger.warning(
                "Insufficient valid signals: %d < %d minimum",
                len(valid_signals), self._config.min_agents,
            )
            return PressureResult(contributing_agents=len(valid_signals))

        bullish_pressure = 0.0
        bearish_pressure = 0.0
        total_weight = 0.0

        for signal in valid_signals:
            weight = signal.weight
            # Risk agent gets extra weight
            if "risk" in signal.agent_name.lower():
                weight *= self._config.risk_weight_multiplier

            if signal.direction == SignalDirection.BULLISH:
                bullish_pressure += signal.confidence * weight
            elif signal.direction == SignalDirection.BEARISH:
                bearish_pressure += signal.confidence * weight
            total_weight += weight

        if total_weight == 0:
            return PressureResult(contributing_agents=len(valid_signals))

        # Determine direction
        net_pressure = bullish_pressure - bearish_pressure
        max_pressure = max(bullish_pressure, bearish_pressure)
        conflict_ratio = min(bullish_pressure, bearish_pressure) / max_pressure if max_pressure > 0 else 0.0

        if conflict_ratio > self._config.max_conflict_ratio:
            direction = SignalDirection.NEUTRAL
        elif net_pressure > 0:
            direction = SignalDirection.BULLISH
        elif net_pressure < 0:
            direction = SignalDirection.BEARISH
        else:
            direction = SignalDirection.NEUTRAL

        confidence = min(1.0, abs(net_pressure) / total_weight) if total_weight > 0 else 0.0

        return PressureResult(
            direction=direction,
            confidence=confidence,
            bullish_pressure=bullish_pressure,
            bearish_pressure=bearish_pressure,
            contributing_agents=len(valid_signals),
            conflict_ratio=conflict_ratio,
        )


@dataclass
class RegimeState:
    """Current regime state snapshot for synthesis.

    Attributes:
        regime_type: The detected market regime.
        confidence: Confidence in the regime detection.
        volatility: Current volatility level.
        trend_strength: Trend strength metric.
    """
    regime_type: str = "ranging"
    confidence: float = 0.0
    volatility: float = 0.0
    trend_strength: float = 0.0


@dataclass
class FactorSnapshot:
    """Snapshot of top factor scores for synthesis.

    Attributes:
        top_factors: List of top factor names.
        scores: Dict mapping factor name to score.
        timestamp: When the snapshot was taken.
    """
    top_factors: List[str] = field(default_factory=list)
    scores: Dict[str, float] = field(default_factory=dict)
    timestamp: str = ""


@dataclass
class RiskState:
    """Current risk state snapshot for synthesis.

    Attributes:
        var_pct: Current Value at Risk percentage.
        drawdown_pct: Current drawdown percentage.
        daily_pnl_pct: Today's P&L percentage.
        kill_switch_level: Current kill switch level (0-3).
        circuit_breakers_tripped: Number of tripped circuit breakers.
    """
    var_pct: float = 0.0
    drawdown_pct: float = 0.0
    daily_pnl_pct: float = 0.0
    kill_switch_level: int = 0
    circuit_breakers_tripped: int = 0


def extract_agent_signals(state: Dict[str, Any]) -> List[AgentSignal]:
    """Extract agent signals from a trading graph state dict.

    Args:
        state: The trading graph AgentState dict.

    Returns:
        List of AgentSignal extracted from the state.
    """
    signals = []
    agent_analyses = state.get("agent_analyses", {})
    if isinstance(agent_analyses, dict):
        for agent_name, analysis in agent_analyses.items():
            if isinstance(analysis, dict):
                direction_str = analysis.get("direction", "neutral")
                try:
                    direction = SignalDirection(direction_str)
                except ValueError:
                    direction = SignalDirection.NEUTRAL
                signals.append(AgentSignal(
                    agent_name=agent_name,
                    direction=direction,
                    confidence=analysis.get("confidence", 0.0),
                    weight=analysis.get("weight", 1.0),
                    reasoning=analysis.get("reasoning", ""),
                    metadata=analysis.get("metadata", {}),
                ))
    return signals


__all__ = [
    "PressureSynthesizer", "PressureSynthesisConfig", "AgentSignal",
    "SignalDirection", "PressureResult", "RegimeState", "FactorSnapshot",
    "RiskState", "extract_agent_signals",
]

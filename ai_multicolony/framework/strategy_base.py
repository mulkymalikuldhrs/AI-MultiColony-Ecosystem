"""Strategy development framework for AI-MultiColony.

Provides the abstract base class, signal model, configuration, and registry
for building and managing trading strategies.  Includes three production-ready
strategy implementations:

* ``SMCTrendStrategy`` — Smart Money Concepts (BOS, CHoCH, Order Blocks, FVGs)
* ``MeanReversionStrategy`` — Bollinger Bands + RSI
* ``MomentumBreakoutStrategy`` — Volume breakout with ATR-based stops

All strategies follow a strict lifecycle: ``on_init`` → ``on_bar`` /
``on_tick`` → ``on_signal`` → ``on_exit``.
"""

from __future__ import annotations

import math
import time as _time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional, Type

import structlog

logger = structlog.get_logger(__name__)


# ═══════════════════════════════════════════════════════════════════════════════
# SIGNAL MODEL
# ═══════════════════════════════════════════════════════════════════════════════


class SignalType(str, Enum):
    """Trading signal direction."""

    BUY = "BUY"
    SELL = "SELL"
    HOLD = "HOLD"
    EXIT = "EXIT"
    NO_SIGNAL = "NO_SIGNAL"


@dataclass
class Signal:
    """A trading signal emitted by a strategy.

    Parameters
    ----------
    type:
        Direction of the signal.
    strength:
        Confidence / strength in the range ``[0.0, 1.0]``.
    asset:
        Ticker or instrument identifier.
    price:
        Reference price at signal generation time.
    timestamp:
        Unix-epoch timestamp (seconds).
    metadata:
        Arbitrary strategy-specific data (indicators, patterns, etc.).
    source:
        Fully-qualified name of the strategy that produced this signal.
    """

    type: SignalType = SignalType.NO_SIGNAL
    strength: float = 0.0
    asset: str = ""
    price: float = 0.0
    timestamp: float = field(default_factory=lambda: _time.time())
    metadata: Dict[str, Any] = field(default_factory=dict)
    source: str = ""

    def __post_init__(self) -> None:
        # Clamp strength to [0, 1]
        if self.strength < 0.0:
            self.strength = 0.0
        elif self.strength > 1.0:
            self.strength = 1.0


# ═══════════════════════════════════════════════════════════════════════════════
# STRATEGY CONFIG
# ═══════════════════════════════════════════════════════════════════════════════


@dataclass
class StrategyConfig:
    """Configuration for a strategy instance.

    Parameters
    ----------
    name:
        Human-readable strategy name.
    version:
        Semantic version string.
    parameters:
        Strategy-specific parameters (e.g. lookback periods, thresholds).
    risk_limits:
        Risk guardrails (e.g. ``{"max_position_pct": 0.05}``).
    """

    name: str = "unnamed_strategy"
    version: str = "0.1.0"
    parameters: Dict[str, Any] = field(default_factory=dict)
    risk_limits: Dict[str, float] = field(default_factory=dict)


# ═══════════════════════════════════════════════════════════════════════════════
# STRATEGY BASE (Abstract)
# ═══════════════════════════════════════════════════════════════════════════════


class StrategyBase(ABC):
    """Abstract base class for all trading strategies.

    Subclasses **must** implement ``generate_signal()`` and **should**
    override the lifecycle hooks they need.  The lifecycle is::

        on_init(config)      # Called once at creation
        on_bar(bar)          # Called per bar / candle
        on_tick(tick)        # Called per tick (if subscribed)
        on_signal(signal)    # Called when a signal is emitted
        on_exit()            # Called on strategy shutdown

    Signals are **not** automatically emitted — the subclass calls
    ``generate_signal()`` inside ``on_bar()`` or ``on_tick()``, and
    the result is validated via ``validate_signal()`` before ``on_signal()``
    is invoked.
    """

    def __init__(self) -> None:
        self._config: Optional[StrategyConfig] = None
        self._signal_history: List[Signal] = []
        self._bar_count: int = 0
        self._initialized: bool = False

    # ── Lifecycle Hooks ──────────────────────────────────────────────

    def on_init(self, config: StrategyConfig) -> None:
        """Initialise the strategy with the given configuration.

        Override to read parameters from *config* and set up internal
        state (indicators, buffers, etc.).
        """
        self._config = config
        self._initialized = True
        logger.info(
            "strategy_initialized",
            name=config.name,
            version=config.version,
        )

    def on_bar(self, bar: Dict[str, Any]) -> None:
        """Process a new bar / candle.

        The default implementation increments the bar counter and
        delegates to ``generate_signal()``.  Override for custom logic.
        """
        self._bar_count += 1
        signal = self.generate_signal(bar)
        if signal is not None and signal.type != SignalType.NO_SIGNAL:
            if self.validate_signal(signal):
                self._signal_history.append(signal)
                self.on_signal(signal)

    def on_tick(self, tick: Dict[str, Any]) -> None:
        """Process a new tick.  Override for tick-level strategies."""
        pass

    def on_signal(self, signal: Signal) -> None:
        """React to a signal that has passed validation.

        Override to push the signal to an execution engine, log it,
        or aggregate with other signals.
        """
        logger.debug(
            "signal_emitted",
            type=signal.type.value,
            asset=signal.asset,
            strength=signal.strength,
            source=signal.source,
        )

    def on_exit(self) -> None:
        """Clean up resources on strategy shutdown."""
        logger.info(
            "strategy_exit",
            name=self._config.name if self._config else "unknown",
            bars_processed=self._bar_count,
            signals_emitted=len(self._signal_history),
        )

    # ── Abstract / Core ──────────────────────────────────────────────

    @abstractmethod
    def generate_signal(self, data: Dict[str, Any]) -> Optional[Signal]:
        """Analyse *data* and return a ``Signal``, or *None*.

        This is the **core** method every strategy must implement.
        """
        ...

    def validate_signal(self, signal: Signal) -> bool:
        """Risk-check a signal before it is emitted.

        The default implementation checks the signal strength floor
        (must be > 0) and validates against ``risk_limits`` in the
        config.  Override for custom risk logic.
        """
        if signal.strength <= 0.0:
            return False

        if self._config is not None:
            max_strength = self._config.risk_limits.get("max_signal_strength", 1.0)
            if signal.strength > max_strength:
                logger.warning(
                    "signal_strength_exceeded_limit",
                    strength=signal.strength,
                    limit=max_strength,
                )
                return False

        return True

    def get_performance(self) -> Dict[str, Any]:
        """Return strategy metrics and diagnostics.

        Returns
        -------
        Dict[str, Any]
            Metrics including bar count, signal counts by type, etc.
        """
        signal_counts: Dict[str, int] = {}
        for sig in self._signal_history:
            key = sig.type.value
            signal_counts[key] = signal_counts.get(key, 0) + 1

        return {
            "name": self._config.name if self._config else "unknown",
            "bars_processed": self._bar_count,
            "total_signals": len(self._signal_history),
            "signal_counts": signal_counts,
        }

    # ── Properties ───────────────────────────────────────────────────

    @property
    def config(self) -> Optional[StrategyConfig]:
        """Current strategy configuration."""
        return self._config

    @property
    def signal_history(self) -> List[Signal]:
        """Read-only view of emitted signals."""
        return list(self._signal_history)


# ═══════════════════════════════════════════════════════════════════════════════
# STRATEGY REGISTRY (Singleton)
# ═══════════════════════════════════════════════════════════════════════════════


class _StrategyRegistryMeta(type):
    """Metaclass implementing the Singleton pattern for StrategyRegistry."""

    _instance: Optional[StrategyRegistry] = None

    def __call__(cls, *args: Any, **kwargs: Any) -> StrategyRegistry:
        if cls._instance is None:
            cls._instance = super().__call__(*args, **kwargs)
        return cls._instance


class StrategyRegistry(metaclass=_StrategyRegistryMeta):
    """Singleton registry for strategy classes.

    Allows strategies to be registered by name and later instantiated
    by that name — useful for configuration-driven strategy selection.

    Usage::

        StrategyRegistry.register("smc_trend", SMCTrendStrategy)
        cls = StrategyRegistry.get("smc_trend")
        strategy = StrategyRegistry.create("smc_trend", config)
    """

    def __init__(self) -> None:
        self._registry: Dict[str, Type[StrategyBase]] = {}

    def register(self, name: str, cls: Type[StrategyBase]) -> None:
        """Register a strategy class under *name*.

        Parameters
        ----------
        name:
            Unique identifier for the strategy.
        cls:
            A concrete subclass of ``StrategyBase``.
        """
        if name in self._registry:
            logger.warning("strategy_overwrite", name=name)
        self._registry[name] = cls
        logger.debug("strategy_registered", name=name, cls=cls.__qualname__)

    def get(self, name: str) -> Type[StrategyBase]:
        """Look up a strategy class by name.

        Raises
        ------
        KeyError
            If *name* is not registered.
        """
        if name not in self._registry:
            raise KeyError(
                f"Strategy '{name}' not found. "
                f"Available: {list(self._registry.keys())}"
            )
        return self._registry[name]

    def create(self, name: str, config: StrategyConfig) -> StrategyBase:
        """Instantiate and initialise a strategy.

        Parameters
        ----------
        name:
            Registered strategy name.
        config:
            Configuration passed to ``on_init()``.

        Returns
        -------
        StrategyBase
            Fully-initialised strategy instance.
        """
        cls = self.get(name)
        instance = cls()
        instance.on_init(config)
        return instance

    def list_strategies(self) -> List[str]:
        """Return sorted list of registered strategy names."""
        return sorted(self._registry.keys())

    def clear(self) -> None:
        """Remove all registrations (useful for testing)."""
        self._registry.clear()


# Module-level convenience singleton
_registry = StrategyRegistry()


def register_strategy(name: str, cls: Type[StrategyBase]) -> None:
    """Module-level helper to register a strategy on the default registry."""
    _registry.register(name, cls)


def get_strategy_class(name: str) -> Type[StrategyBase]:
    """Module-level helper to look up a strategy on the default registry."""
    return _registry.get(name)


# ═══════════════════════════════════════════════════════════════════════════════
# SMC TREND STRATEGY
# ═══════════════════════════════════════════════════════════════════════════════


class SMCTrendStrategy(StrategyBase):
    """Smart Money Concepts trend-following strategy.

    Detects:
    * **BOS** (Break of Structure) — trend continuation.
    * **CHoCH** (Change of Character) — potential trend reversal.
    * **Order Blocks** — institutional supply/demand zones.
    * **Fair Value Gaps** — 3-candle price imbalances.

    Aggregates detected patterns to generate BUY / SELL signals with
    strength proportional to the number of confluences.
    """

    def __init__(self) -> None:
        super().__init__()
        self._swing_highs: List[float] = []
        self._swing_lows: List[float] = []
        self._last_structure: str = "none"  # "bullish" | "bearish" | "none"

    def on_init(self, config: StrategyConfig) -> None:
        super().on_init(config)

    def generate_signal(self, data: Dict[str, Any]) -> Optional[Signal]:
        """Analyse OHLCV data for SMC patterns."""
        try:
            if hasattr(data, "iloc"):
                # DataFrame-like
                close = data["close"].values  # type: ignore[index]
                high = data["high"].values  # type: ignore[index]
                low = data["low"].values  # type: ignore[index]
                open_p = data["open"].values if "open" in data else close  # type: ignore[index]
                volume = data["volume"].values if "volume" in data else None  # type: ignore[index]
            elif isinstance(data, dict):
                close = data.get("close", [])
                high = data.get("high", [])
                low = data.get("low", [])
                open_p = data.get("open", close)
                volume = data.get("volume")
            else:
                return None

            if len(close) < 10:
                return None

            metadata: Dict[str, Any] = {}
            bullish_evidence: List[str] = []
            bearish_evidence: List[str] = []

            # Detect BOS / CHoCH
            structure = self._detect_structure(close, high, low)
            if structure:
                metadata["structure"] = structure
                direction = structure.get("direction", "")
                if direction == "bullish":
                    bullish_evidence.append(structure["type"])
                elif direction == "bearish":
                    bearish_evidence.append(structure["type"])

            # Detect Order Blocks
            ob = self._detect_order_block(close, high, low, open_p)
            if ob:
                metadata["order_block"] = ob
                direction = ob.get("direction", "")
                if direction == "bullish":
                    bullish_evidence.append("order_block")
                elif direction == "bearish":
                    bearish_evidence.append("order_block")

            # Detect Fair Value Gaps
            fvg = self._detect_fvg(close, high, low)
            if fvg:
                metadata["fvg"] = fvg
                direction = fvg.get("direction", "")
                if direction == "bullish":
                    bullish_evidence.append("fvg")
                elif direction == "bearish":
                    bearish_evidence.append("fvg")

            if not bullish_evidence and not bearish_evidence:
                return Signal(
                    type=SignalType.HOLD,
                    strength=0.0,
                    asset=data.get("symbol", ""),
                    price=float(close[-1]),
                    source=self.__class__.__qualname__,
                    metadata=metadata,
                )

            current_price = float(close[-1])

            if len(bullish_evidence) > len(bearish_evidence):
                strength = min(0.3 + 0.2 * len(bullish_evidence), 0.95)
                return Signal(
                    type=SignalType.BUY,
                    strength=strength,
                    asset=data.get("symbol", ""),
                    price=current_price,
                    source=self.__class__.__qualname__,
                    metadata={
                        **metadata,
                        "evidence": bullish_evidence,
                        "pattern": "SMC_bullish",
                    },
                )
            elif len(bearish_evidence) > len(bullish_evidence):
                strength = min(0.3 + 0.2 * len(bearish_evidence), 0.95)
                return Signal(
                    type=SignalType.SELL,
                    strength=strength,
                    asset=data.get("symbol", ""),
                    price=current_price,
                    source=self.__class__.__qualname__,
                    metadata={
                        **metadata,
                        "evidence": bearish_evidence,
                        "pattern": "SMC_bearish",
                    },
                )

            return Signal(
                type=SignalType.HOLD,
                strength=0.0,
                asset=data.get("symbol", ""),
                price=current_price,
                source=self.__class__.__qualname__,
                metadata=metadata,
            )

        except Exception as exc:
            logger.error("smc_strategy_error", error=str(exc))
            return None

    # ── SMC Detection Helpers ─────────────────────────────────────────

    @staticmethod
    def _detect_structure(
        close: Any, high: Any, low: Any
    ) -> Optional[Dict[str, Any]]:
        """Detect BOS (Break of Structure) or CHoCH (Change of Character).

        Compares the most recent 5-bar swing to the prior 5-bar swing.
        """
        n = len(high)
        if n < 10:
            return None

        recent_high = float(max(high[-5:]))
        prev_high = float(max(high[-10:-5])) if n >= 10 else float(max(high[:5]))
        recent_low = float(min(low[-5:]))
        prev_low = float(min(low[-10:-5])) if n >= 10 else float(min(low[:5]))

        if recent_high > prev_high and recent_low > prev_low:
            return {"type": "BOS_bullish", "direction": "bullish"}
        elif recent_high < prev_high and recent_low < prev_low:
            return {"type": "BOS_bearish", "direction": "bearish"}
        elif recent_high > prev_high and recent_low < prev_low:
            return {"type": "CHoCH_bullish", "direction": "bullish"}
        elif recent_high < prev_high and recent_low > prev_low:
            return {"type": "CHoCH_bearish", "direction": "bearish"}

        return None

    @staticmethod
    def _detect_order_block(
        close: Any, high: Any, low: Any, open_p: Any
    ) -> Optional[Dict[str, Any]]:
        """Detect Order Block — last opposing candle before an impulse."""
        if len(close) < 4:
            return None

        c = [float(x) for x in close]
        o = [float(x) for x in open_p]
        h = [float(x) for x in high]
        l = [float(x) for x in low]

        # Bullish OB: bearish candle [-2] followed by bullish candle [-1]
        if c[-1] > o[-1] and c[-2] < o[-2] and c[-1] > c[-2]:
            return {"type": "bullish_ob", "direction": "bullish", "level": h[-2]}
        # Bearish OB: bullish candle [-2] followed by bearish candle [-1]
        if c[-1] < o[-1] and c[-2] > o[-2] and c[-1] < c[-2]:
            return {"type": "bearish_ob", "direction": "bearish", "level": l[-2]}

        return None

    @staticmethod
    def _detect_fvg(
        close: Any, high: Any, low: Any
    ) -> Optional[Dict[str, Any]]:
        """Detect Fair Value Gap — 3-candle price imbalance."""
        if len(high) < 3:
            return None

        c = float(close[-1])

        # Bullish FVG
        if float(low[-1]) > float(high[-3]):
            gap_pct = (float(low[-1]) - float(high[-3])) / c
            return {
                "type": "fvg_bullish",
                "direction": "bullish",
                "gap_pct": round(gap_pct, 6),
            }

        # Bearish FVG
        if float(high[-1]) < float(low[-3]):
            gap_pct = (float(low[-3]) - float(high[-1])) / c
            return {
                "type": "fvg_bearish",
                "direction": "bearish",
                "gap_pct": round(gap_pct, 6),
            }

        return None


# ═══════════════════════════════════════════════════════════════════════════════
# MEAN REVERSION STRATEGY
# ═══════════════════════════════════════════════════════════════════════════════


class MeanReversionStrategy(StrategyBase):
    """Mean-reversion strategy using Bollinger Bands + RSI confirmation.

    Generates BUY signals when price touches the lower Bollinger Band
    and RSI is oversold, and SELL signals when price touches the upper
    band and RSI is overbought.
    """

    def __init__(self) -> None:
        super().__init__()
        self._bb_period: int = 20
        self._bb_std: float = 2.0
        self._rsi_period: int = 14
        self._rsi_ob: float = 70.0
        self._rsi_os: float = 30.0

    def on_init(self, config: StrategyConfig) -> None:
        super().on_init(config)
        params = config.parameters
        self._bb_period = params.get("bb_period", 20)
        self._bb_std = params.get("bb_std", 2.0)
        self._rsi_period = params.get("rsi_period", 14)
        self._rsi_ob = params.get("rsi_overbought", 70.0)
        self._rsi_os = params.get("rsi_oversold", 30.0)

    def generate_signal(self, data: Dict[str, Any]) -> Optional[Signal]:
        try:
            if hasattr(data, "iloc"):
                close = data["close"].values  # type: ignore[index]
            elif isinstance(data, dict):
                close = data.get("close", [])
            else:
                return None

            if len(close) < max(self._bb_period, self._rsi_period) + 1:
                return None

            closes = [float(c) for c in close]
            n = len(closes)

            # Bollinger Bands
            sma = sum(closes[-self._bb_period :]) / self._bb_period
            variance = sum((c - sma) ** 2 for c in closes[-self._bb_period :]) / self._bb_period
            std = math.sqrt(variance)
            upper_band = sma + self._bb_std * std
            lower_band = sma - self._bb_std * std

            # RSI
            rsi = self._compute_rsi(closes, self._rsi_period)

            current_price = closes[-1]
            metadata = {
                "bb_upper": round(upper_band, 6),
                "bb_middle": round(sma, 6),
                "bb_lower": round(lower_band, 6),
                "rsi": round(rsi, 2) if rsi is not None else None,
            }

            # BUY: price at/below lower band + RSI oversold
            if current_price <= lower_band and rsi is not None and rsi < self._rsi_os:
                strength = min(0.5 + (self._rsi_os - rsi) / 100.0, 0.95)
                return Signal(
                    type=SignalType.BUY,
                    strength=strength,
                    asset=data.get("symbol", "") if isinstance(data, dict) else "",
                    price=current_price,
                    source=self.__class__.__qualname__,
                    metadata={**metadata, "pattern": "mean_reversion_buy"},
                )

            # SELL: price at/above upper band + RSI overbought
            if current_price >= upper_band and rsi is not None and rsi > self._rsi_ob:
                strength = min(0.5 + (rsi - self._rsi_ob) / 100.0, 0.95)
                return Signal(
                    type=SignalType.SELL,
                    strength=strength,
                    asset=data.get("symbol", "") if isinstance(data, dict) else "",
                    price=current_price,
                    source=self.__class__.__qualname__,
                    metadata={**metadata, "pattern": "mean_reversion_sell"},
                )

            return Signal(
                type=SignalType.HOLD,
                strength=0.0,
                asset=data.get("symbol", "") if isinstance(data, dict) else "",
                price=current_price,
                source=self.__class__.__qualname__,
                metadata=metadata,
            )

        except Exception as exc:
            logger.error("mean_reversion_error", error=str(exc))
            return None

    @staticmethod
    def _compute_rsi(closes: List[float], period: int) -> Optional[float]:
        """Compute RSI using Wilder's smoothing method."""
        if len(closes) < period + 1:
            return None

        deltas = [closes[i] - closes[i - 1] for i in range(1, len(closes))]
        gains = [d if d > 0 else 0.0 for d in deltas]
        losses = [-d if d < 0 else 0.0 for d in deltas]

        avg_gain = sum(gains[:period]) / period
        avg_loss = sum(losses[:period]) / period

        for i in range(period, len(gains)):
            avg_gain = (avg_gain * (period - 1) + gains[i]) / period
            avg_loss = (avg_loss * (period - 1) + losses[i]) / period

        if avg_loss == 0.0:
            return 100.0

        rs = avg_gain / avg_loss
        return 100.0 - (100.0 / (1.0 + rs))


# ═══════════════════════════════════════════════════════════════════════════════
# MOMENTUM BREAKOUT STRATEGY
# ═══════════════════════════════════════════════════════════════════════════════


class MomentumBreakoutStrategy(StrategyBase):
    """Momentum breakout strategy with volume confirmation and ATR stops.

    Detects breakouts above/below N-period high/low when accompanied
    by above-average volume.  Uses ATR for stop-loss and take-profit
    placement.
    """

    def __init__(self) -> None:
        super().__init__()
        self._lookback: int = 20
        self._volume_mult: float = 1.5
        self._atr_period: int = 14
        self._atr_sl_mult: float = 1.5
        self._atr_tp_mult: float = 3.0

    def on_init(self, config: StrategyConfig) -> None:
        super().on_init(config)
        params = config.parameters
        self._lookback = params.get("lookback", 20)
        self._volume_mult = params.get("volume_mult", 1.5)
        self._atr_period = params.get("atr_period", 14)
        self._atr_sl_mult = params.get("atr_sl_mult", 1.5)
        self._atr_tp_mult = params.get("atr_tp_mult", 3.0)

    def generate_signal(self, data: Dict[str, Any]) -> Optional[Signal]:
        try:
            if hasattr(data, "iloc"):
                close = data["close"].values  # type: ignore[index]
                high = data["high"].values  # type: ignore[index]
                low = data["low"].values  # type: ignore[index]
                volume = data["volume"].values if "volume" in data else None  # type: ignore[index]
            elif isinstance(data, dict):
                close = data.get("close", [])
                high = data.get("high", [])
                low = data.get("low", [])
                volume = data.get("volume")
            else:
                return None

            n = len(close)
            if n < self._lookback + 1 or volume is None:
                return None

            closes = [float(c) for c in close]
            highs = [float(h) for h in high]
            lows = [float(l) for l in low]
            volumes = [float(v) for v in volume]

            current_price = closes[-1]

            # Channel high/low (exclude current bar)
            channel_high = max(highs[-(self._lookback + 1) : -1])
            channel_low = min(lows[-(self._lookback + 1) : -1])

            # Average volume
            avg_volume = sum(volumes[-(self._lookback + 1) : -1]) / self._lookback
            current_volume = volumes[-1]
            volume_confirmed = current_volume > avg_volume * self._volume_mult

            # ATR
            atr = self._compute_atr(highs, lows, closes, self._atr_period)
            if atr is None or atr == 0.0:
                return Signal(
                    type=SignalType.HOLD,
                    strength=0.0,
                    asset=data.get("symbol", "") if isinstance(data, dict) else "",
                    price=current_price,
                    source=self.__class__.__qualname__,
                    metadata={"reason": "insufficient_atr"},
                )

            metadata: Dict[str, Any] = {
                "channel_high": round(channel_high, 6),
                "channel_low": round(channel_low, 6),
                "atr": round(atr, 6),
                "current_volume": round(current_volume, 2),
                "avg_volume": round(avg_volume, 2),
                "volume_confirmed": volume_confirmed,
            }

            # Bullish breakout
            if current_price > channel_high and volume_confirmed:
                stop_loss = current_price - self._atr_sl_mult * atr
                take_profit = current_price + self._atr_tp_mult * atr
                strength = min(
                    0.4
                    + (current_volume / avg_volume - 1.0) * 0.1
                    + (current_price - channel_high) / atr * 0.1,
                    0.95,
                )
                return Signal(
                    type=SignalType.BUY,
                    strength=strength,
                    asset=data.get("symbol", "") if isinstance(data, dict) else "",
                    price=current_price,
                    source=self.__class__.__qualname__,
                    metadata={
                        **metadata,
                        "pattern": "momentum_breakout_buy",
                        "stop_loss": round(stop_loss, 6),
                        "take_profit": round(take_profit, 6),
                    },
                )

            # Bearish breakout
            if current_price < channel_low and volume_confirmed:
                stop_loss = current_price + self._atr_sl_mult * atr
                take_profit = current_price - self._atr_tp_mult * atr
                strength = min(
                    0.4
                    + (current_volume / avg_volume - 1.0) * 0.1
                    + (channel_low - current_price) / atr * 0.1,
                    0.95,
                )
                return Signal(
                    type=SignalType.SELL,
                    strength=strength,
                    asset=data.get("symbol", "") if isinstance(data, dict) else "",
                    price=current_price,
                    source=self.__class__.__qualname__,
                    metadata={
                        **metadata,
                        "pattern": "momentum_breakout_sell",
                        "stop_loss": round(stop_loss, 6),
                        "take_profit": round(take_profit, 6),
                    },
                )

            return Signal(
                type=SignalType.HOLD,
                strength=0.0,
                asset=data.get("symbol", "") if isinstance(data, dict) else "",
                price=current_price,
                source=self.__class__.__qualname__,
                metadata=metadata,
            )

        except Exception as exc:
            logger.error("momentum_breakout_error", error=str(exc))
            return None

    @staticmethod
    def _compute_atr(
        highs: List[float], lows: List[float], closes: List[float], period: int
    ) -> Optional[float]:
        """Compute Average True Range using Wilder's smoothing."""
        if len(highs) < period + 1:
            return None

        true_ranges: List[float] = []
        for i in range(1, len(highs)):
            tr = max(
                highs[i] - lows[i],
                abs(highs[i] - closes[i - 1]),
                abs(lows[i] - closes[i - 1]),
            )
            true_ranges.append(tr)

        if len(true_ranges) < period:
            return None

        atr = sum(true_ranges[:period]) / period
        for i in range(period, len(true_ranges)):
            atr = (atr * (period - 1) + true_ranges[i]) / period

        return atr


# ── Auto-register built-in strategies ────────────────────────────────────────

_registry.register("smc_trend", SMCTrendStrategy)
_registry.register("mean_reversion", MeanReversionStrategy)
_registry.register("momentum_breakout", MomentumBreakoutStrategy)


__all__ = [
    "SignalType",
    "Signal",
    "StrategyConfig",
    "StrategyBase",
    "StrategyRegistry",
    "SMCTrendStrategy",
    "MeanReversionStrategy",
    "MomentumBreakoutStrategy",
    "register_strategy",
    "get_strategy_class",
]

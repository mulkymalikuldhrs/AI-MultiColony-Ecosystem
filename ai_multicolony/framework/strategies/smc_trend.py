"""Smart Money Concepts (SMC) Trend-Following Strategy.

Detects institutional footprints in price action using four core SMC
patterns and generates directional signals when multiple confluences
align.

Patterns Detected
-----------------
* **BOS** (Break of Structure) — trend continuation when price makes
  a new higher-high / higher-low (bullish) or lower-low / lower-high
  (bearish).
* **CHoCH** (Change of Character) — potential trend reversal when
  price breaks the prevailing structure in the opposite direction.
* **Order Blocks** — institutional supply/demand zones identified as
  the last opposing candle before an impulse move.
* **Fair Value Gaps (FVG)** — 3-candle price imbalances where the
  wick of candle 1 and candle 3 do not overlap, signalling rapid
  institutional order flow.

Signal Strength
~~~~~~~~~~~~~~~
Each detected confluence adds weight.  The base strength is 0.3 and
each additional confluence adds 0.2, capped at 0.95.

Configuration Parameters
------------------------
ob_lookback : int
    Number of bars to scan for Order Blocks (default 4).
fvg_min_gap_pct : float
    Minimum gap size (as % of price) to qualify as an FVG (default 0.0001).
structure_window : int
    Number of bars per swing window for BOS/CHoCH detection (default 5).

Example
-------
>>> from ai_multicolony.framework.strategy_base import StrategyConfig
>>> from ai_multicolony.framework.strategies import SMCTrendStrategy
>>> cfg = StrategyConfig(name="smc", parameters={"ob_lookback": 6})
>>> strategy = SMCTrendStrategy()
>>> strategy.on_init(cfg)
>>> signal = strategy.generate_signal(bar_data)
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

import structlog

from ai_multicolony.framework.strategy_base import (
    Signal,
    SignalType,
    StrategyBase,
    StrategyConfig,
)

logger = structlog.get_logger(__name__)


class SMCTrendStrategy(StrategyBase):
    """Smart Money Concepts trend-following strategy.

    Detects BOS (Break of Structure), CHoCH (Change of Character),
    Order Blocks, and Fair Value Gaps.  Aggregates detected patterns
    to generate BUY / SELL signals with strength proportional to the
    number of confluences.

    Parameters
    ----------
    ob_lookback : int
        Bars to scan for Order Block patterns (default 4).
    fvg_min_gap_pct : float
        Minimum gap percentage to qualify as an FVG (default 0.0001).
    structure_window : int
        Bars per swing window for BOS / CHoCH (default 5).
    """

    def __init__(self) -> None:
        super().__init__()
        self._swing_highs: List[float] = []
        self._swing_lows: List[float] = []
        self._last_structure: str = "none"  # "bullish" | "bearish" | "none"
        # Configurable defaults (overridden in on_init)
        self._ob_lookback: int = 4
        self._fvg_min_gap_pct: float = 0.0001
        self._structure_window: int = 5

    def on_init(self, config: StrategyConfig) -> None:
        """Initialise the SMC strategy with configuration.

        Reads the following keys from ``config.parameters``:

        * ``ob_lookback`` (int) — Order Block lookback window.
        * ``fvg_min_gap_pct`` (float) — Minimum FVG gap percentage.
        * ``structure_window`` (int) — BOS/CHoCH swing window.
        """
        super().on_init(config)
        params = config.parameters
        self._ob_lookback = params.get("ob_lookback", 4)
        self._fvg_min_gap_pct = params.get("fvg_min_gap_pct", 0.0001)
        self._structure_window = params.get("structure_window", 5)

    def generate_signal(self, data: Dict[str, Any]) -> Optional[Signal]:
        """Analyse OHLCV data for SMC patterns.

        Parameters
        ----------
        data : dict
            Must contain ``close``, ``high``, ``low`` sequences.
            Optionally ``open`` and ``symbol``.

        Returns
        -------
        Signal or None
            BUY if bullish confluences dominate, SELL if bearish,
            HOLD when no edge is detected, None on error.
        """
        try:
            # ── Normalise input ────────────────────────────────────
            if hasattr(data, "iloc"):
                # pandas DataFrame-like
                close = data["close"].values  # type: ignore[index]
                high = data["high"].values  # type: ignore[index]
                low = data["low"].values  # type: ignore[index]
                open_p = data["open"].values if "open" in data else close  # type: ignore[index]
            elif isinstance(data, dict):
                close = data.get("close", [])
                high = data.get("high", [])
                low = data.get("low", [])
                open_p = data.get("open", close)
            else:
                return None

            min_bars = max(self._structure_window * 2, 10)
            if len(close) < min_bars:
                return None

            metadata: Dict[str, Any] = {}
            bullish_evidence: List[str] = []
            bearish_evidence: List[str] = []

            # ── 1. BOS / CHoCH Detection ──────────────────────────
            structure = self._detect_structure(close, high, low)
            if structure:
                metadata["structure"] = structure
                direction = structure.get("direction", "")
                if direction == "bullish":
                    bullish_evidence.append(structure["type"])
                elif direction == "bearish":
                    bearish_evidence.append(structure["type"])

            # ── 2. Order Block Detection ───────────────────────────
            ob = self._detect_order_block(close, high, low, open_p)
            if ob:
                metadata["order_block"] = ob
                direction = ob.get("direction", "")
                if direction == "bullish":
                    bullish_evidence.append("order_block")
                elif direction == "bearish":
                    bearish_evidence.append("order_block")

            # ── 3. Fair Value Gap Detection ────────────────────────
            fvg = self._detect_fvg(close, high, low)
            if fvg:
                metadata["fvg"] = fvg
                direction = fvg.get("direction", "")
                if direction == "bullish":
                    bullish_evidence.append("fvg")
                elif direction == "bearish":
                    bearish_evidence.append("fvg")

            # ── 4. Emit Signal ─────────────────────────────────────
            if not bullish_evidence and not bearish_evidence:
                return Signal(
                    type=SignalType.HOLD,
                    strength=0.0,
                    asset=data.get("symbol", "") if isinstance(data, dict) else "",
                    price=float(close[-1]),
                    source=self.__class__.__qualname__,
                    metadata=metadata,
                )

            current_price = float(close[-1])
            asset = data.get("symbol", "") if isinstance(data, dict) else ""

            if len(bullish_evidence) > len(bearish_evidence):
                strength = min(0.3 + 0.2 * len(bullish_evidence), 0.95)
                return Signal(
                    type=SignalType.BUY,
                    strength=strength,
                    asset=asset,
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
                    asset=asset,
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
                asset=asset,
                price=current_price,
                source=self.__class__.__qualname__,
                metadata=metadata,
            )

        except Exception as exc:
            logger.error("smc_strategy_error", error=str(exc))
            return None

    # ── SMC Detection Helpers ─────────────────────────────────────────

    def _detect_structure(
        self, close: Any, high: Any, low: Any
    ) -> Optional[Dict[str, Any]]:
        """Detect BOS (Break of Structure) or CHoCH (Change of Character).

        Compares the most recent *structure_window*-bar swing to the
        prior *structure_window*-bar swing.

        Returns
        -------
        dict or None
            ``{"type": "BOS_bullish"|"CHoCH_bullish"|..., "direction": "bullish"|"bearish"}``
        """
        n = len(high)
        w = self._structure_window
        if n < w * 2:
            return None

        recent_high = float(max(high[-w:]))
        prev_high = float(max(high[-(2 * w) : -w]))
        recent_low = float(min(low[-w:]))
        prev_low = float(min(low[-(2 * w) : -w]))

        # Update internal swing tracking
        self._swing_highs.append(recent_high)
        self._swing_lows.append(recent_low)

        if recent_high > prev_high and recent_low > prev_low:
            self._last_structure = "bullish"
            return {"type": "BOS_bullish", "direction": "bullish"}
        elif recent_high < prev_high and recent_low < prev_low:
            self._last_structure = "bearish"
            return {"type": "BOS_bearish", "direction": "bearish"}
        elif recent_high > prev_high and recent_low < prev_low:
            return {"type": "CHoCH_bullish", "direction": "bullish"}
        elif recent_high < prev_high and recent_low > prev_low:
            return {"type": "CHoCH_bearish", "direction": "bearish"}

        return None

    def _detect_order_block(
        self, close: Any, high: Any, low: Any, open_p: Any
    ) -> Optional[Dict[str, Any]]:
        """Detect Order Block — last opposing candle before an impulse.

        A bullish Order Block is a bearish candle immediately followed
        by a bullish candle that engulfs it.  Vice-versa for bearish.

        Parameters
        ----------
        close, high, low, open_p : array-like
            OHLC price series.

        Returns
        -------
        dict or None
            ``{"type": "bullish_ob"|"bearish_ob", "direction": ..., "level": float}``
        """
        lookback = min(self._ob_lookback, len(close) - 1)
        if lookback < 2:
            return None

        c = [float(x) for x in close[-lookback:]]
        o = [float(x) for x in open_p[-lookback:]]
        h = [float(x) for x in high[-lookback:]]
        l = [float(x) for x in low[-lookback:]]

        # Bullish OB: bearish candle [-2] followed by bullish candle [-1]
        if c[-1] > o[-1] and c[-2] < o[-2] and c[-1] > c[-2]:
            return {"type": "bullish_ob", "direction": "bullish", "level": h[-2]}
        # Bearish OB: bullish candle [-2] followed by bearish candle [-1]
        if c[-1] < o[-1] and c[-2] > o[-2] and c[-1] < c[-2]:
            return {"type": "bearish_ob", "direction": "bearish", "level": l[-2]}

        return None

    def _detect_fvg(
        self, close: Any, high: Any, low: Any
    ) -> Optional[Dict[str, Any]]:
        """Detect Fair Value Gap — 3-candle price imbalance.

        A bullish FVG occurs when the low of candle [-1] is above the
        high of candle [-3], leaving a gap.  A bearish FVG is the
        mirror image.

        Parameters
        ----------
        close, high, low : array-like
            Price series.

        Returns
        -------
        dict or None
            ``{"type": "fvg_bullish"|"fvg_bearish", "direction": ..., "gap_pct": float}``
        """
        if len(high) < 3:
            return None

        c = float(close[-1])

        # Bullish FVG: gap between candle [-3] high and candle [-1] low
        if float(low[-1]) > float(high[-3]):
            gap_pct = (float(low[-1]) - float(high[-3])) / c
            if gap_pct >= self._fvg_min_gap_pct:
                return {
                    "type": "fvg_bullish",
                    "direction": "bullish",
                    "gap_pct": round(gap_pct, 6),
                }

        # Bearish FVG: gap between candle [-3] low and candle [-1] high
        if float(high[-1]) < float(low[-3]):
            gap_pct = (float(low[-3]) - float(high[-1])) / c
            if gap_pct >= self._fvg_min_gap_pct:
                return {
                    "type": "fvg_bearish",
                    "direction": "bearish",
                    "gap_pct": round(gap_pct, 6),
                }

        return None

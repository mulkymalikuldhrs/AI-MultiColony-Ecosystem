"""Volume-Confirmed Momentum Breakout Strategy.

A breakout strategy that combines channel breakouts with volume
confirmation and ATR-based dynamic stop/take-profit levels.  Signals
are generated when price breaks above or below an N-period channel
**and** volume exceeds a configurable multiple of the average.

Signal Logic
------------
BUY
    Current close > N-period channel high **and** current volume >
    ``volume_mult`` × average volume.
SELL
    Current close < N-period channel low **and** current volume >
    ``volume_mult`` × average volume.

Stop-loss and take-profit are placed using ATR:

* Stop-loss  = entry ∓ ``atr_sl_mult`` × ATR
* Take-profit = entry ± ``atr_tp_mult`` × ATR

Signal strength increases with:
1. Higher volume ratio relative to the average.
2. Larger distance between the breakout price and the channel
   boundary, expressed in ATR units.

Configuration Parameters
------------------------
lookback : int
    Channel lookback period (default 20).
volume_mult : float
    Volume must exceed this multiple of the average to confirm
    the breakout (default 1.5).
atr_period : int
    ATR lookback period (default 14).
atr_sl_mult : float
    ATR multiplier for stop-loss placement (default 1.5).
atr_tp_mult : float
    ATR multiplier for take-profit placement (default 3.0).
breakout_atr_multiplier : float
    Minimum breakout distance as a fraction of ATR to qualify
    as a valid breakout (default 0.0, i.e. any distance qualifies).

Example
-------
>>> from ai_multicolony.framework.strategy_base import StrategyConfig
>>> from ai_multicolony.framework.strategies import MomentumBreakoutStrategy
>>> cfg = StrategyConfig(
...     name="mom_brk",
...     parameters={"lookback": 20, "volume_mult": 1.5, "atr_period": 14},
... )
>>> strategy = MomentumBreakoutStrategy()
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


class MomentumBreakoutStrategy(StrategyBase):
    """Momentum breakout strategy with volume confirmation and ATR stops.

    Detects breakouts above/below N-period high/low when accompanied
    by above-average volume.  Uses ATR for stop-loss and take-profit
    placement.

    Parameters
    ----------
    lookback : int
        Channel lookback period (default 20).
    volume_mult : float
        Volume confirmation multiplier (default 1.5).
    atr_period : int
        ATR lookback period (default 14).
    atr_sl_mult : float
        ATR stop-loss multiplier (default 1.5).
    atr_tp_mult : float
        ATR take-profit multiplier (default 3.0).
    breakout_atr_multiplier : float
        Minimum breakout distance in ATR units (default 0.0).
    """

    def __init__(self) -> None:
        super().__init__()
        self._lookback: int = 20
        self._volume_mult: float = 1.5
        self._atr_period: int = 14
        self._atr_sl_mult: float = 1.5
        self._atr_tp_mult: float = 3.0
        self._breakout_atr_mult: float = 0.0

    def on_init(self, config: StrategyConfig) -> None:
        """Initialise the momentum breakout strategy with configuration.

        Reads the following keys from ``config.parameters``:

        * ``lookback`` (int) — Channel lookback period.
        * ``volume_mult`` (float) — Volume confirmation multiplier.
        * ``atr_period`` (int) — ATR lookback period.
        * ``atr_sl_mult`` (float) — ATR stop-loss multiplier.
        * ``atr_tp_mult`` (float) — ATR take-profit multiplier.
        * ``breakout_atr_multiplier`` (float) — Min breakout distance in ATR.
        """
        super().on_init(config)
        params = config.parameters
        self._lookback = params.get("lookback", 20)
        self._volume_mult = params.get("volume_mult", 1.5)
        self._atr_period = params.get("atr_period", 14)
        self._atr_sl_mult = params.get("atr_sl_mult", 1.5)
        self._atr_tp_mult = params.get("atr_tp_mult", 3.0)
        self._breakout_atr_mult = params.get("breakout_atr_multiplier", 0.0)

    def generate_signal(self, data: Dict[str, Any]) -> Optional[Signal]:
        """Analyse OHLCV data for volume-confirmed momentum breakouts.

        Parameters
        ----------
        data : dict
            Must contain ``close``, ``high``, ``low``, ``volume``
            sequences.  Optionally ``symbol``.

        Returns
        -------
        Signal or None
            BUY on bullish breakout with volume confirmation, SELL on
            bearish breakout with volume confirmation, HOLD otherwise,
            None on error.
        """
        try:
            # ── Normalise input ────────────────────────────────────
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

            # ── Channel high/low (exclude current bar) ────────────
            channel_high = max(highs[-(self._lookback + 1) : -1])
            channel_low = min(lows[-(self._lookback + 1) : -1])

            # ── Volume analysis ───────────────────────────────────
            avg_volume = sum(volumes[-(self._lookback + 1) : -1]) / self._lookback
            current_volume = volumes[-1]
            volume_confirmed = current_volume > avg_volume * self._volume_mult

            # ── ATR ───────────────────────────────────────────────
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
                "volume_ratio": round(current_volume / avg_volume, 4) if avg_volume > 0 else 0.0,
            }

            asset = data.get("symbol", "") if isinstance(data, dict) else ""

            # ── Bullish breakout ──────────────────────────────────
            if current_price > channel_high and volume_confirmed:
                breakout_distance = (current_price - channel_high) / atr
                # Apply minimum breakout distance filter
                if breakout_distance >= self._breakout_atr_mult:
                    stop_loss = current_price - self._atr_sl_mult * atr
                    take_profit = current_price + self._atr_tp_mult * atr
                    strength = min(
                        0.4
                        + (current_volume / avg_volume - 1.0) * 0.1
                        + breakout_distance * 0.1,
                        0.95,
                    )
                    return Signal(
                        type=SignalType.BUY,
                        strength=strength,
                        asset=asset,
                        price=current_price,
                        source=self.__class__.__qualname__,
                        metadata={
                            **metadata,
                            "pattern": "momentum_breakout_buy",
                            "stop_loss": round(stop_loss, 6),
                            "take_profit": round(take_profit, 6),
                            "breakout_distance_atr": round(breakout_distance, 4),
                        },
                    )

            # ── Bearish breakout ──────────────────────────────────
            if current_price < channel_low and volume_confirmed:
                breakout_distance = (channel_low - current_price) / atr
                # Apply minimum breakout distance filter
                if breakout_distance >= self._breakout_atr_mult:
                    stop_loss = current_price + self._atr_sl_mult * atr
                    take_profit = current_price - self._atr_tp_mult * atr
                    strength = min(
                        0.4
                        + (current_volume / avg_volume - 1.0) * 0.1
                        + breakout_distance * 0.1,
                        0.95,
                    )
                    return Signal(
                        type=SignalType.SELL,
                        strength=strength,
                        asset=asset,
                        price=current_price,
                        source=self.__class__.__qualname__,
                        metadata={
                            **metadata,
                            "pattern": "momentum_breakout_sell",
                            "stop_loss": round(stop_loss, 6),
                            "take_profit": round(take_profit, 6),
                            "breakout_distance_atr": round(breakout_distance, 4),
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
            logger.error("momentum_breakout_error", error=str(exc))
            return None

    # ── Indicator Helpers ──────────────────────────────────────────────

    @staticmethod
    def _compute_atr(
        highs: List[float], lows: List[float], closes: List[float], period: int
    ) -> Optional[float]:
        """Compute Average True Range using Wilder's smoothing.

        Parameters
        ----------
        highs, lows, closes : list[float]
            Price series.
        period : int
            ATR lookback period.

        Returns
        -------
        float or None
            ATR value, or None if insufficient data.
        """
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

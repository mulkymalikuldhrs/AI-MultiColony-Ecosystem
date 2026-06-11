"""Bollinger Bands + RSI Mean Reversion Strategy.

A mean-reversion strategy that identifies overextended price conditions
using Bollinger Bands for statistical extremes and RSI for momentum
exhaustion.  Signals are generated when both indicators confirm an
overbought or oversold condition.

Signal Logic
------------
BUY
    Price touches or falls below the lower Bollinger Band **and** RSI
    is below the oversold threshold (default 30).
SELL
    Price touches or rises above the upper Bollinger Band **and** RSI
    is above the overbought threshold (default 70).

Signal strength scales with the magnitude of the deviation — deeper
oversold RSI readings or more extreme band touches produce stronger
signals (capped at 0.95).

Configuration Parameters
------------------------
bb_period : int
    Lookback period for the Bollinger Band SMA (default 20).
bb_std : float
    Number of standard deviations for the bands (default 2.0).
rsi_period : int
    Lookback period for RSI calculation (default 14).
rsi_oversold : float
    RSI threshold for oversold condition (default 30.0).
rsi_overbought : float
    RSI threshold for overbought condition (default 70.0).

Example
-------
>>> from ai_multicolony.framework.strategy_base import StrategyConfig
>>> from ai_multicolony.framework.strategies import MeanReversionStrategy
>>> cfg = StrategyConfig(
...     name="mean_rev",
...     parameters={"bb_period": 20, "bb_std": 2.0, "rsi_period": 14},
... )
>>> strategy = MeanReversionStrategy()
>>> strategy.on_init(cfg)
>>> signal = strategy.generate_signal(bar_data)
"""

from __future__ import annotations

import math
from typing import Any, Dict, List, Optional

import structlog

from ai_multicolony.framework.strategy_base import (
    Signal,
    SignalType,
    StrategyBase,
    StrategyConfig,
)

logger = structlog.get_logger(__name__)


class MeanReversionStrategy(StrategyBase):
    """Mean-reversion strategy using Bollinger Bands + RSI confirmation.

    Generates BUY signals when price touches the lower Bollinger Band
    and RSI is oversold, and SELL signals when price touches the upper
    band and RSI is overbought.

    Parameters
    ----------
    bb_period : int
        SMA period for Bollinger Bands (default 20).
    bb_std : float
        Standard deviation multiplier for bands (default 2.0).
    rsi_period : int
        RSI lookback period (default 14).
    rsi_oversold : float
        RSI oversold threshold (default 30.0).
    rsi_overbought : float
        RSI overbought threshold (default 70.0).
    """

    def __init__(self) -> None:
        super().__init__()
        self._bb_period: int = 20
        self._bb_std: float = 2.0
        self._rsi_period: int = 14
        self._rsi_ob: float = 70.0
        self._rsi_os: float = 30.0

    def on_init(self, config: StrategyConfig) -> None:
        """Initialise the mean-reversion strategy with configuration.

        Reads the following keys from ``config.parameters``:

        * ``bb_period`` (int) — Bollinger Band SMA period.
        * ``bb_std`` (float) — Standard deviation multiplier.
        * ``rsi_period`` (int) — RSI lookback period.
        * ``rsi_oversold`` (float) — RSI oversold threshold.
        * ``rsi_overbought`` (float) — RSI overbought threshold.
        """
        super().on_init(config)
        params = config.parameters
        self._bb_period = params.get("bb_period", 20)
        self._bb_std = params.get("bb_std", 2.0)
        self._rsi_period = params.get("rsi_period", 14)
        self._rsi_ob = params.get("rsi_overbought", 70.0)
        self._rsi_os = params.get("rsi_oversold", 30.0)

    def generate_signal(self, data: Dict[str, Any]) -> Optional[Signal]:
        """Analyse price data for Bollinger + RSI mean-reversion setups.

        Parameters
        ----------
        data : dict
            Must contain a ``close`` sequence.  Optionally ``symbol``.

        Returns
        -------
        Signal or None
            BUY on lower-band + oversold RSI confluence, SELL on
            upper-band + overbought RSI confluence, HOLD otherwise,
            None on error.
        """
        try:
            # ── Normalise input ────────────────────────────────────
            if hasattr(data, "iloc"):
                close = data["close"].values  # type: ignore[index]
            elif isinstance(data, dict):
                close = data.get("close", [])
            else:
                return None

            required_len = max(self._bb_period, self._rsi_period) + 1
            if len(close) < required_len:
                return None

            closes = [float(c) for c in close]
            current_price = closes[-1]

            # ── Bollinger Bands ────────────────────────────────────
            bb_upper, bb_middle, bb_lower = self._compute_bollinger_bands(
                closes, self._bb_period, self._bb_std
            )

            # ── RSI ────────────────────────────────────────────────
            rsi = self._compute_rsi(closes, self._rsi_period)

            metadata = {
                "bb_upper": round(bb_upper, 6),
                "bb_middle": round(bb_middle, 6),
                "bb_lower": round(bb_lower, 6),
                "rsi": round(rsi, 2) if rsi is not None else None,
            }

            asset = data.get("symbol", "") if isinstance(data, dict) else ""

            # ── BUY: price at/below lower band + RSI oversold ─────
            if current_price <= bb_lower and rsi is not None and rsi < self._rsi_os:
                # Deeper oversold = stronger signal
                strength = min(0.5 + (self._rsi_os - rsi) / 100.0, 0.95)
                return Signal(
                    type=SignalType.BUY,
                    strength=strength,
                    asset=asset,
                    price=current_price,
                    source=self.__class__.__qualname__,
                    metadata={**metadata, "pattern": "mean_reversion_buy"},
                )

            # ── SELL: price at/above upper band + RSI overbought ──
            if current_price >= bb_upper and rsi is not None and rsi > self._rsi_ob:
                # Higher overbought = stronger signal
                strength = min(0.5 + (rsi - self._rsi_ob) / 100.0, 0.95)
                return Signal(
                    type=SignalType.SELL,
                    strength=strength,
                    asset=asset,
                    price=current_price,
                    source=self.__class__.__qualname__,
                    metadata={**metadata, "pattern": "mean_reversion_sell"},
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
            logger.error("mean_reversion_error", error=str(exc))
            return None

    # ── Indicator Helpers ──────────────────────────────────────────────

    @staticmethod
    def _compute_bollinger_bands(
        closes: List[float], period: int, num_std: float
    ) -> tuple:
        """Compute Bollinger Bands (upper, middle, lower).

        Parameters
        ----------
        closes : list[float]
            Closing prices (must have at least *period* elements).
        period : int
            SMA lookback window.
        num_std : float
            Standard deviation multiplier.

        Returns
        -------
        tuple[float, float, float]
            ``(upper_band, middle_band, lower_band)``
        """
        window = closes[-period:]
        sma = sum(window) / period
        variance = sum((c - sma) ** 2 for c in window) / period
        std = math.sqrt(variance)
        upper = sma + num_std * std
        lower = sma - num_std * std
        return upper, sma, lower

    @staticmethod
    def _compute_rsi(closes: List[float], period: int) -> Optional[float]:
        """Compute RSI using Wilder's smoothing method.

        Parameters
        ----------
        closes : list[float]
            Closing prices.
        period : int
            RSI lookback period.

        Returns
        -------
        float or None
            RSI value in [0, 100], or None if insufficient data.
        """
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

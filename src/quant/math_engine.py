"""
Pure deterministic indicator calculations - no AI, no approximation.

All calculations are 100% deterministic mathematical functions.
Supports: SMA, EMA, WMA, RSI, MACD, Bollinger Bands, ATR, Stochastic,
CCI, ADX, VWAP, Volume Profile, Pearson Correlation, Kelly Criterion.
"""

from __future__ import annotations

import math
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class IndicatorResult(BaseModel):
    """Container for a full indicator analysis result."""
    latest_close: float
    bars: int
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())
    indicators: dict = Field(default_factory=dict)


class MathEngine:
    """Pure mathematical indicator calculations - no AI, no approximation."""

    # ── Moving Averages ────────────────────────────────────────────

    @staticmethod
    def sma(data: list[float], period: int) -> list[Optional[float]]:
        """Simple Moving Average."""
        result: list[Optional[float]] = [None] * len(data)
        for i in range(period - 1, len(data)):
            result[i] = sum(data[i - period + 1 : i + 1]) / period
        return result

    @staticmethod
    def ema(data: list[float], period: int) -> list[Optional[float]]:
        """Exponential Moving Average (Wilder's smoothing)."""
        result: list[Optional[float]] = [None] * len(data)
        if len(data) < period:
            return result
        multiplier = 2.0 / (period + 1)
        result[period - 1] = sum(data[:period]) / period
        for i in range(period, len(data)):
            result[i] = (data[i] - result[i - 1]) * multiplier + result[i - 1]
        return result

    @staticmethod
    def wma(data: list[float], period: int) -> list[Optional[float]]:
        """Weighted Moving Average."""
        result: list[Optional[float]] = [None] * len(data)
        weight_sum = period * (period + 1) / 2
        for i in range(period - 1, len(data)):
            w_sum = sum(data[i - period + 1 + j] * (j + 1) for j in range(period))
            result[i] = w_sum / weight_sum
        return result

    # ── RSI (Wilder's) ────────────────────────────────────────────

    @staticmethod
    def rsi(closes: list[float], period: int = 14) -> list[Optional[float]]:
        """RSI using Wilder's smoothing method."""
        result: list[Optional[float]] = [None] * len(closes)
        if len(closes) < period + 1:
            return result

        deltas = [closes[i] - closes[i - 1] for i in range(1, len(closes))]
        gains = [d if d > 0 else 0 for d in deltas]
        losses = [-d if d < 0 else 0 for d in deltas]

        avg_gain = sum(gains[:period]) / period
        avg_loss = sum(losses[:period]) / period

        for i in range(period, len(deltas)):
            avg_gain = (avg_gain * (period - 1) + gains[i]) / period
            avg_loss = (avg_loss * (period - 1) + losses[i]) / period

            if avg_loss == 0:
                result[i + 1] = 100.0
            else:
                rs = avg_gain / avg_loss
                result[i + 1] = 100.0 - (100.0 / (1.0 + rs))
        return result

    # ── MACD ───────────────────────────────────────────────────────

    @staticmethod
    def macd(
        closes: list[float], fast: int = 12, slow: int = 26, signal: int = 9
    ) -> dict[str, list[Optional[float]]]:
        """MACD, Signal Line, Histogram."""
        ema_fast = MathEngine.ema(closes, fast)
        ema_slow = MathEngine.ema(closes, slow)

        macd_line: list[Optional[float]] = [None] * len(closes)
        for i in range(len(closes)):
            if ema_fast[i] is not None and ema_slow[i] is not None:
                macd_line[i] = ema_fast[i] - ema_slow[i]

        macd_values = [v if v is not None else 0 for v in macd_line]
        signal_line = MathEngine.ema(macd_values, signal)

        histogram: list[Optional[float]] = [None] * len(closes)
        for i in range(len(closes)):
            if macd_line[i] is not None and signal_line[i] is not None:
                histogram[i] = macd_line[i] - signal_line[i]

        return {"macd": macd_line, "signal": signal_line, "histogram": histogram}

    # ── Bollinger Bands ────────────────────────────────────────────

    @staticmethod
    def bollinger_bands(
        closes: list[float], period: int = 20, num_std: float = 2.0
    ) -> dict[str, list[Optional[float]]]:
        """Bollinger Bands with SMA middle, +/- N*sigma bands."""
        middle = MathEngine.sma(closes, period)
        upper: list[Optional[float]] = [None] * len(closes)
        lower: list[Optional[float]] = [None] * len(closes)
        bandwidth: list[Optional[float]] = [None] * len(closes)
        percent_b: list[Optional[float]] = [None] * len(closes)

        for i in range(period - 1, len(closes)):
            if middle[i] is None:
                continue
            slice_data = closes[i - period + 1 : i + 1]
            std = math.sqrt(sum((x - middle[i]) ** 2 for x in slice_data) / period)
            upper[i] = middle[i] + num_std * std
            lower[i] = middle[i] - num_std * std
            bandwidth[i] = (upper[i] - lower[i]) / middle[i] if middle[i] else 0
            percent_b[i] = (
                (closes[i] - lower[i]) / (upper[i] - lower[i])
                if (upper[i] - lower[i])
                else 0.5
            )

        return {
            "middle": middle,
            "upper": upper,
            "lower": lower,
            "bandwidth": bandwidth,
            "percent_b": percent_b,
        }

    # ── ATR ────────────────────────────────────────────────────────

    @staticmethod
    def atr(
        highs: list[float], lows: list[float], closes: list[float], period: int = 14
    ) -> list[Optional[float]]:
        """Average True Range (Wilder's)."""
        result: list[Optional[float]] = [None] * len(closes)
        if len(closes) < 2:
            return result

        true_ranges = [0.0]
        for i in range(1, len(closes)):
            tr = max(
                highs[i] - lows[i],
                abs(highs[i] - closes[i - 1]),
                abs(lows[i] - closes[i - 1]),
            )
            true_ranges.append(tr)

        if len(true_ranges) < period + 1:
            return result

        result[period] = sum(true_ranges[1 : period + 1]) / period
        for i in range(period + 1, len(true_ranges)):
            result[i] = (result[i - 1] * (period - 1) + true_ranges[i]) / period
        return result

    # ── Stochastic ─────────────────────────────────────────────────

    @staticmethod
    def stochastic(
        highs: list[float],
        lows: list[float],
        closes: list[float],
        k_period: int = 14,
        k_smooth: int = 3,
        d_period: int = 3,
    ) -> dict[str, list[Optional[float]]]:
        """Stochastic Oscillator %K and %D."""
        raw_k: list[Optional[float]] = [None] * len(closes)

        for i in range(k_period - 1, len(closes)):
            highest = max(highs[i - k_period + 1 : i + 1])
            lowest = min(lows[i - k_period + 1 : i + 1])
            if highest - lowest == 0:
                raw_k[i] = 50.0
            else:
                raw_k[i] = ((closes[i] - lowest) / (highest - lowest)) * 100

        k_values: list[Optional[float]] = [None] * len(closes)
        for i in range(k_period - 1 + k_smooth - 1, len(closes)):
            slice_data = [v for v in raw_k[i - k_smooth + 1 : i + 1] if v is not None]
            if len(slice_data) == k_smooth:
                k_values[i] = sum(slice_data) / k_smooth

        d_values = MathEngine.sma(
            [v if v is not None else 0 for v in k_values], d_period
        )

        return {"k": k_values, "d": d_values}

    # ── CCI ────────────────────────────────────────────────────────

    @staticmethod
    def cci(
        highs: list[float], lows: list[float], closes: list[float], period: int = 20
    ) -> list[Optional[float]]:
        """Commodity Channel Index."""
        result: list[Optional[float]] = [None] * len(closes)
        tp = [(h + l + c) / 3 for h, l, c in zip(highs, lows, closes)]
        tp_sma = MathEngine.sma(tp, period)

        for i in range(period - 1, len(closes)):
            if tp_sma[i] is None:
                continue
            mean_dev = sum(abs(tp[j] - tp_sma[i]) for j in range(i - period + 1, i + 1)) / period
            result[i] = (tp[i] - tp_sma[i]) / (0.015 * mean_dev) if mean_dev else 0
        return result

    # ── ADX ────────────────────────────────────────────────────────

    @staticmethod
    def adx(
        highs: list[float], lows: list[float], closes: list[float], period: int = 14
    ) -> dict[str, list[Optional[float]]]:
        """ADX with +DI and -DI (Wilder's method)."""
        n = len(closes)
        plus_dm = [0.0] * n
        minus_dm = [0.0] * n
        tr = [0.0] * n

        for i in range(1, n):
            high_diff = highs[i] - highs[i - 1]
            low_diff = lows[i - 1] - lows[i]

            plus_dm[i] = high_diff if (high_diff > low_diff and high_diff > 0) else 0
            minus_dm[i] = low_diff if (low_diff > high_diff and low_diff > 0) else 0
            tr[i] = max(
                highs[i] - lows[i],
                abs(highs[i] - closes[i - 1]),
                abs(lows[i] - closes[i - 1]),
            )

        atr_vals: list[Optional[float]] = [None] * n
        smooth_plus_dm: list[Optional[float]] = [None] * n
        smooth_minus_dm: list[Optional[float]] = [None] * n

        if n > period:
            atr_vals[period] = sum(tr[1 : period + 1]) / period
            smooth_plus_dm[period] = sum(plus_dm[1 : period + 1]) / period
            smooth_minus_dm[period] = sum(minus_dm[1 : period + 1]) / period

            for i in range(period + 1, n):
                atr_vals[i] = (atr_vals[i - 1] * (period - 1) + tr[i]) / period  # type: ignore
                smooth_plus_dm[i] = (smooth_plus_dm[i - 1] * (period - 1) + plus_dm[i]) / period  # type: ignore
                smooth_minus_dm[i] = (smooth_minus_dm[i - 1] * (period - 1) + minus_dm[i]) / period  # type: ignore

        plus_di: list[Optional[float]] = [None] * n
        minus_di: list[Optional[float]] = [None] * n
        dx: list[Optional[float]] = [None] * n

        for i in range(period, n):
            if atr_vals[i] and atr_vals[i] > 0:
                plus_di[i] = (smooth_plus_dm[i] / atr_vals[i]) * 100  # type: ignore
                minus_di[i] = (smooth_minus_dm[i] / atr_vals[i]) * 100  # type: ignore
                di_sum = plus_di[i] + minus_di[i]  # type: ignore
                dx[i] = abs(plus_di[i] - minus_di[i]) / di_sum * 100 if di_sum else 0  # type: ignore

        adx_values: list[Optional[float]] = [None] * n
        if n > 2 * period:
            adx_values[2 * period - 1] = sum(
                dx[j] for j in range(period, 2 * period) if dx[j] is not None
            ) / period
            for i in range(2 * period, n):
                if dx[i] is not None and adx_values[i - 1] is not None:
                    adx_values[i] = (adx_values[i - 1] * (period - 1) + dx[i]) / period  # type: ignore

        return {"adx": adx_values, "plus_di": plus_di, "minus_di": minus_di, "dx": dx}

    # ── VWAP ───────────────────────────────────────────────────────

    @staticmethod
    def vwap(
        highs: list[float], lows: list[float], closes: list[float], volumes: list[float]
    ) -> list[Optional[float]]:
        """Cumulative VWAP."""
        result: list[Optional[float]] = [None] * len(closes)
        cum_tp_vol = 0.0
        cum_vol = 0.0

        for i in range(len(closes)):
            tp = (highs[i] + lows[i] + closes[i]) / 3
            cum_tp_vol += tp * volumes[i]
            cum_vol += volumes[i]
            result[i] = cum_tp_vol / cum_vol if cum_vol > 0 else None
        return result

    # ── Volume Profile ─────────────────────────────────────────────

    @staticmethod
    def volume_profile(
        highs: list[float], lows: list[float], volumes: list[float], num_bins: int = 20
    ) -> dict:
        """Volume profile with High Volume Node detection."""
        if not highs:
            return {"bins": [], "hvn": None, "lvn": None}

        price_min = min(lows)
        price_max = max(highs)
        price_range = price_max - price_min

        if price_range == 0:
            return {"bins": [], "hvn": None, "lvn": None}

        bin_size = price_range / num_bins
        bins = [
            {"low": price_min + i * bin_size, "high": price_min + (i + 1) * bin_size, "volume": 0}
            for i in range(num_bins)
        ]

        for i in range(len(volumes)):
            mid = (highs[i] + lows[i]) / 2
            bin_idx = min(int((mid - price_min) / bin_size), num_bins - 1)
            bins[bin_idx]["volume"] += volumes[i]

        total_vol = sum(b["volume"] for b in bins)
        for b in bins:
            b["pct"] = round(b["volume"] / total_vol * 100, 1) if total_vol else 0

        max_vol_bin = max(bins, key=lambda b: b["volume"])
        min_vol_bin = min(bins, key=lambda b: b["volume"])

        return {
            "bins": bins,
            "hvn": {
                "price": (max_vol_bin["low"] + max_vol_bin["high"]) / 2,
                "volume": max_vol_bin["volume"],
                "pct": max_vol_bin["pct"],
            },
            "lvn": {
                "price": (min_vol_bin["low"] + min_vol_bin["high"]) / 2,
                "volume": min_vol_bin["volume"],
                "pct": min_vol_bin["pct"],
            },
        }

    # ── Correlation ────────────────────────────────────────────────

    @staticmethod
    def correlation(x: list[float], y: list[float]) -> Optional[float]:
        """Pearson correlation coefficient."""
        n = min(len(x), len(y))
        if n < 2:
            return None

        mean_x = sum(x[:n]) / n
        mean_y = sum(y[:n]) / n

        cov = sum((x[i] - mean_x) * (y[i] - mean_y) for i in range(n)) / n
        std_x = math.sqrt(sum((x[i] - mean_x) ** 2 for i in range(n)) / n)
        std_y = math.sqrt(sum((y[i] - mean_y) ** 2 for i in range(n)) / n)

        if std_x == 0 or std_y == 0:
            return 0.0
        return cov / (std_x * std_y)

    # ── Kelly Criterion ────────────────────────────────────────────

    @staticmethod
    def kelly_criterion(
        win_rate: float, avg_win: float, avg_loss: float, fraction: float = 0.25
    ) -> dict:
        """Kelly Criterion position sizing with fractional safety."""
        if avg_loss == 0 or win_rate <= 0 or win_rate >= 1:
            return {"kelly_pct": 0, "fractional_kelly": 0, "recommendation": "NO_TRADE"}

        r = avg_win / avg_loss
        full_kelly = win_rate - ((1 - win_rate) / r)
        fractional = full_kelly * fraction

        return {
            "win_rate": round(win_rate, 4),
            "win_loss_ratio": round(r, 4),
            "full_kelly": round(full_kelly, 4),
            "fraction": fraction,
            "fractional_kelly": round(fractional, 4),
            "recommendation": f"Risk {fractional:.2%} of capital per trade",
        }

    # ── Master Analysis ────────────────────────────────────────────

    @staticmethod
    def analyze_sequence(
        closes: list[float],
        highs: list[float] | None = None,
        lows: list[float] | None = None,
        volumes: list[float] | None = None,
    ) -> IndicatorResult:
        """Run full indicator analysis on price data."""
        if not closes or len(closes) < 30:
            return IndicatorResult(
                latest_close=0, bars=0, indicators={"error": "Insufficient data (need 30+ bars)"}
            )

        highs = highs or closes
        lows = lows or closes
        volumes = volumes or [1.0] * len(closes)

        indicators: dict = {}

        # RSI
        rsi = MathEngine.rsi(closes, 14)
        indicators["rsi_14"] = rsi[-1]

        # EMAs
        for period in [9, 20, 50, 200]:
            ema = MathEngine.ema(closes, period)
            indicators[f"ema_{period}"] = ema[-1]

        # SMAs
        for period in [20, 50, 200]:
            sma = MathEngine.sma(closes, period)
            indicators[f"sma_{period}"] = sma[-1]

        # MACD
        macd = MathEngine.macd(closes)
        indicators["macd"] = {
            "line": macd["macd"][-1],
            "signal": macd["signal"][-1],
            "histogram": macd["histogram"][-1],
        }

        # Bollinger Bands
        bb = MathEngine.bollinger_bands(closes)
        indicators["bollinger"] = {
            "upper": bb["upper"][-1],
            "middle": bb["middle"][-1],
            "lower": bb["lower"][-1],
            "bandwidth": bb["bandwidth"][-1],
            "percent_b": bb["percent_b"][-1],
        }

        # ATR
        atr = MathEngine.atr(highs, lows, closes, 14)
        indicators["atr_14"] = atr[-1]
        indicators["atr_pct"] = (atr[-1] / closes[-1] * 100) if atr[-1] and closes[-1] else None

        # Stochastic
        stoch = MathEngine.stochastic(highs, lows, closes)
        indicators["stochastic"] = {"k": stoch["k"][-1], "d": stoch["d"][-1]}

        # CCI
        cci = MathEngine.cci(highs, lows, closes)
        indicators["cci_20"] = cci[-1]

        # ADX
        adx = MathEngine.adx(highs, lows, closes)
        indicators["adx"] = {
            "adx": adx["adx"][-1],
            "plus_di": adx["plus_di"][-1],
            "minus_di": adx["minus_di"][-1],
        }

        # VWAP
        vwap = MathEngine.vwap(highs, lows, closes, volumes)
        indicators["vwap"] = vwap[-1]

        # Volume Profile
        vp = MathEngine.volume_profile(highs[-50:], lows[-50:], volumes[-50:])
        indicators["volume_profile"] = vp

        return IndicatorResult(
            latest_close=closes[-1], bars=len(closes), indicators=indicators
        )

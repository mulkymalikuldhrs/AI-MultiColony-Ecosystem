"""Regime Detector — HMM-based and statistical fallback market regime detection.

Implements the RegimeDetector class that identifies market regimes using
either a Gaussian Hidden Markov Model (hmmlearn) or a statistical
heuristic fallback based on volatility, trend, and drawdown signals.

Research basis:
  - Hamilton (1989): Rational-expectations econometric analysis of changes
    in regime using Markov-switching models.
  - Ryden et al. (1998): Parameter estimation for Markov-switching models
    of returns via EM algorithm.
  - Nystrup et al. (2020): Regime-based asset allocation with hidden Markov
    models — demonstrates superior risk-adjusted returns vs. static allocation.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import pandas as pd

from quant_nanggroe.engine.regime.types import RegimeResult, RegimeType

logger = logging.getLogger(__name__)

# ─── Thresholds for statistical fallback ──────────────────────────────────────
_VOL_HIGH_PCTILE = 80          # percentile above which vol = "high"
_VOL_LOW_PCTILE = 30           # percentile below which vol = "low"
_TREND_STRONG = 0.10           # annualized return threshold for strong trend
_DRAWDOWN_SEVERE = 0.15        # drawdown threshold for crisis classification
_RECOVERY_THRESHOLD = 0.05     # drawdown below this + positive drift = recovery


class RegimeDetector:
    """Detect market regimes from return series.

    Uses a Gaussian Hidden Markov Model when ``hmmlearn`` is available,
    otherwise falls back to a statistical heuristic based on realized
    volatility, trend, and drawdown.

    Args:
        n_regimes: Number of HMM states (default 5 corresponding to
            the five RegimeType values).
        random_seed: Seed for reproducibility. Passed to both the HMM
            initializer and numpy random state.
    """

    def __init__(
        self,
        n_regimes: int = 5,
        random_seed: int = 42,
    ) -> None:
        self._n_regimes = n_regimes
        self._random_seed = random_seed
        self._hmm = None
        self._rng = np.random.RandomState(random_seed)

        # Try to import hmmlearn
        try:
            from hmmlearn.hmm import GaussianHMM  # noqa: F401

            self._hmm_available = True
        except ImportError:
            self._hmm_available = False
            logger.info(
                "hmmlearn not available — using statistical fallback for regime detection"
            )

    # ─── Public API ──────────────────────────────────────────────────────

    def detect_regime(
        self,
        returns: pd.Series,
        window: int = 252,
    ) -> RegimeResult:
        """Detect the current market regime from a return series.

        Args:
            returns: Daily (or periodic) return series with DatetimeIndex.
            window: Lookback window in periods (default 252 trading days).

        Returns:
            RegimeResult with current regime, confidence, history, and
            transition probabilities.
        """
        if len(returns) < window:
            logger.warning(
                "Return series length (%d) < window (%d); using full series",
                len(returns),
                window,
            )
            window = len(returns)

        recent = returns.iloc[-window:]

        if self._hmm_available:
            return self._detect_hmm(recent)
        else:
            return self._detect_statistical(recent)

    # ─── HMM-based detection ─────────────────────────────────────────────

    def _detect_hmm(self, returns: pd.Series) -> RegimeResult:
        """Run Gaussian HMM regime detection."""
        from hmmlearn.hmm import GaussianHMM

        X = returns.dropna().values.reshape(-1, 1)

        model = GaussianHMM(
            n_components=self._n_regimes,
            covariance_type="full",
            n_iter=200,
            random_state=self._random_seed,
        )
        model.fit(X)
        hidden_states = model.predict(X)

        # Map HMM states to regime types based on mean returns
        state_means = model.means_.flatten()
        state_order = np.argsort(state_means)  # lowest mean → bear/crisis

        # Map: worst state = CRISIS, 2nd worst = BEAR, middle = SIDEWAYS,
        # 2nd best = RECOVERY, best = BULL
        regime_order = [RegimeType.CRISIS, RegimeType.BEAR, RegimeType.SIDEWAYS,
                        RegimeType.RECOVERY, RegimeType.BULL]
        state_to_regime: Dict[int, RegimeType] = {}
        for rank, state_idx in enumerate(state_order):
            if rank < len(regime_order):
                state_to_regime[state_idx] = regime_order[rank]
            else:
                state_to_regime[state_idx] = RegimeType.SIDEWAYS

        # Current regime
        current_state = hidden_states[-1]
        current_regime = state_to_regime[current_state]

        # Confidence from posterior probabilities
        posteriors = model.predict_proba(X)
        confidence = float(posteriors[-1, current_state])

        # Build regime history
        dates = returns.dropna().index
        regime_history: List[Tuple[str, RegimeType]] = []
        for i, state in enumerate(hidden_states):
            if i < len(dates):
                regime_history.append(
                    (str(dates[i].date()) if hasattr(dates[i], "date") else str(dates[i]),
                     state_to_regime[state])
                )

        # Build transition matrix from model
        transition_probs = self._build_transition_probs(
            model.transmat_, state_to_regime
        )

        return RegimeResult(
            current_regime=current_regime,
            confidence=confidence,
            regime_history=regime_history,
            transition_probs=transition_probs,
            metadata={"method": "hmm", "n_regimes": self._n_regimes},
        )

    # ─── Statistical fallback ────────────────────────────────────────────

    def _detect_statistical(self, returns: pd.Series) -> RegimeResult:
        """Statistical heuristic regime detection.

        Uses three signals:
          1. Realized volatility percentile rank
          2. Trend (annualized mean return over window)
          3. Maximum drawdown

        Decision logic:
          - CRISIS:    high vol + severe drawdown + negative trend
          - BEAR:      moderate-to-high vol + negative trend
          - RECOVERY:  positive trend after drawdown (drawdown < 5% from recent peak)
          - BULL:      low vol + positive trend
          - SIDEWAYS:  default / ambiguous
        """
        clean = returns.dropna()
        n = len(clean)
        if n < 10:
            return RegimeResult(
                current_regime=RegimeType.SIDEWAYS,
                confidence=0.0,
                metadata={"method": "statistical", "reason": "insufficient_data"},
            )

        # Realized volatility (annualized)
        realized_vol = float(clean.std() * np.sqrt(252))
        vol_pctile = float(
            (clean.rolling(21, min_periods=10).std().rank(pct=True).iloc[-1])
            if n >= 21
            else 0.5
        )

        # Trend — annualized mean return
        trend = float(clean.mean() * 252)

        # Maximum drawdown
        cum = (1 + clean).cumprod()
        running_max = cum.cummax()
        drawdown = float(((cum - running_max) / running_max).min())

        # Current drawdown from peak
        current_dd = float((cum.iloc[-1] - running_max.iloc[-1]) / running_max.iloc[-1])

        # ─── Classification logic ────────────────────────────────────
        regime: RegimeType
        confidence: float
        signals: Dict[str, float] = {
            "vol_pctile": vol_pctile,
            "trend_annual": trend,
            "max_drawdown": drawdown,
            "current_drawdown": current_dd,
            "realized_vol": realized_vol,
        }

        if vol_pctile >= _VOL_HIGH_PCTILE / 100 and current_dd <= -_DRAWDOWN_SEVERE and trend < 0:
            regime = RegimeType.CRISIS
            confidence = min(1.0, 0.5 + abs(current_dd) + vol_pctile)
        elif trend < -_TREND_STRONG:
            regime = RegimeType.BEAR
            confidence = min(1.0, 0.5 + abs(trend) + (vol_pctile * 0.5))
        elif current_dd > -_RECOVERY_THRESHOLD and trend > 0 and drawdown <= -_DRAWDOWN_SEVERE:
            regime = RegimeType.RECOVERY
            confidence = min(1.0, 0.5 + abs(drawdown) * 2 + trend)
        elif trend > _TREND_STRONG and vol_pctile < _VOL_LOW_PCTILE / 100:
            regime = RegimeType.BULL
            confidence = min(1.0, 0.5 + trend + (1 - vol_pctile) * 0.5)
        elif trend > _TREND_STRONG:
            regime = RegimeType.BULL
            confidence = min(1.0, 0.5 + trend)
        elif current_dd <= -_DRAWDOWN_SEVERE and trend < 0:
            regime = RegimeType.BEAR
            confidence = min(1.0, 0.5 + abs(current_dd))
        else:
            regime = RegimeType.SIDEWAYS
            confidence = 0.5  # default confidence for ambiguous

        confidence = max(0.0, min(1.0, confidence))

        # Build rolling regime history using the same heuristic on sub-windows
        regime_history = self._build_statistical_history(clean)

        # Simple estimated transition probs
        transition_probs = self._estimate_transition_probs(regime_history)

        return RegimeResult(
            current_regime=regime,
            confidence=confidence,
            regime_history=regime_history,
            transition_probs=transition_probs,
            metadata={"method": "statistical", "signals": signals},
        )

    # ─── Helpers ─────────────────────────────────────────────────────────

    def _build_statistical_history(
        self, returns: pd.Series, sub_window: int = 63
    ) -> List[Tuple[str, RegimeType]]:
        """Build regime history by applying the statistical heuristic
        on rolling sub-windows."""
        history: List[Tuple[str, RegimeType]] = []
        n = len(returns)

        if n < sub_window:
            # Just classify the whole series once
            result = self._classify_subwindow(returns)
            idx = returns.index[-1] if len(returns.index) > 0 else "unknown"
            history.append((str(idx.date()) if hasattr(idx, "date") else str(idx), result))
            return history

        step = max(sub_window // 4, 1)
        for start in range(0, n - sub_window + 1, step):
            end = start + sub_window
            sub = returns.iloc[start:end]
            regime = self._classify_subwindow(sub)
            idx = sub.index[-1] if len(sub.index) > 0 else "unknown"
            history.append(
                (str(idx.date()) if hasattr(idx, "date") else str(idx), regime)
            )

        return history

    def _classify_subwindow(self, returns: pd.Series) -> RegimeType:
        """Classify a single sub-window of returns into a regime."""
        clean = returns.dropna()
        n = len(clean)
        if n < 5:
            return RegimeType.SIDEWAYS

        vol_pctile = float(
            (clean.rolling(min(21, n), min_periods=min(10, n // 2))
             .std().rank(pct=True).iloc[-1])
            if n >= 10 else 0.5
        )
        trend = float(clean.mean() * 252)
        cum = (1 + clean).cumprod()
        running_max = cum.cummax()
        current_dd = float(((cum - running_max) / running_max).iloc[-1])
        max_dd = float(((cum - running_max) / running_max).min())

        if vol_pctile >= _VOL_HIGH_PCTILE / 100 and current_dd <= -_DRAWDOWN_SEVERE and trend < 0:
            return RegimeType.CRISIS
        elif trend < -_TREND_STRONG:
            return RegimeType.BEAR
        elif current_dd > -_RECOVERY_THRESHOLD and trend > 0 and max_dd <= -_DRAWDOWN_SEVERE:
            return RegimeType.RECOVERY
        elif trend > _TREND_STRONG:
            return RegimeType.BULL
        elif current_dd <= -_DRAWDOWN_SEVERE and trend < 0:
            return RegimeType.BEAR
        else:
            return RegimeType.SIDEWAYS

    @staticmethod
    def _build_transition_probs(
        transmat: np.ndarray,
        state_to_regime: Dict[int, RegimeType],
    ) -> Dict[str, Dict[str, float]]:
        """Convert HMM transition matrix to regime-keyed dict."""
        result: Dict[str, Dict[str, float]] = {}
        for i in range(transmat.shape[0]):
            from_regime = state_to_regime.get(i, RegimeType.SIDEWAYS).value
            result[from_regime] = {}
            for j in range(transmat.shape[1]):
                to_regime = state_to_regime.get(j, RegimeType.SIDEWAYS).value
                result[from_regime][to_regime] = round(float(transmat[i, j]), 4)
        return result

    @staticmethod
    def _estimate_transition_probs(
        history: List[Tuple[str, RegimeType]],
    ) -> Dict[str, Dict[str, float]]:
        """Estimate transition probabilities from regime history."""
        if len(history) < 2:
            # Return uniform priors
            regimes = [r.value for r in RegimeType]
            n = len(regimes)
            uniform = round(1.0 / n, 4)
            return {r: {rr: uniform for rr in regimes} for r in regimes}

        # Count transitions
        counts: Dict[str, Dict[str, int]] = {}
        for regime in RegimeType:
            counts[regime.value] = {r.value: 0 for r in RegimeType}

        for i in range(1, len(history)):
            from_r = history[i - 1][1].value
            to_r = history[i][1].value
            if from_r in counts and to_r in counts[from_r]:
                counts[from_r][to_r] += 1

        # Normalize
        probs: Dict[str, Dict[str, float]] = {}
        for from_r, transitions in counts.items():
            total = sum(transitions.values())
            if total == 0:
                n = len(RegimeType)
                probs[from_r] = {r.value: round(1.0 / n, 4) for r in RegimeType}
            else:
                probs[from_r] = {
                    to_r: round(cnt / total, 4) for to_r, cnt in transitions.items()
                }

        return probs


__all__ = ["RegimeDetector"]

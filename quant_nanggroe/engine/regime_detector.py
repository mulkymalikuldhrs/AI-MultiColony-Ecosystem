"""Market Regime Detection — HMM-based with Statistical Fallback.

Implements Hidden Markov Model regime detection for identifying market
regimes (BULL, BEAR, SIDEWAYS, CRISIS) from price and volume data.
When ``hmmlearn`` is unavailable, falls back to a deterministic
ADX + ATR heuristic classifier.

Features
--------
* 4-regime detection: BULL, BEAR, SIDEWAYS, CRISIS
* Features: daily returns, 20-day rolling volatility, volume change
* HMM via ``hmmlearn`` with Gaussian emissions
* Statistical fallback using ADX + ATR heuristics
* Transition probability estimation
* Serializable results via Pydantic models

Usage::

    from quant_nanggroe.engine.regime_detector import HMMRegimeDetector

    detector = HMMRegimeDetector(n_regimes=4)
    detector.fit(returns=returns_list, volumes=volumes_list)
    state = detector.predict(recent_returns, recent_volumes)
    print(state.regime, state.confidence)
"""

from __future__ import annotations

import logging
import math
import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
from pydantic import BaseModel, Field, ConfigDict

logger = logging.getLogger(__name__)

# ── Optional hmmlearn import ─────────────────────────────────────────────

try:
    from hmmlearn.hmm import GaussianHMM

    _HMM_AVAILABLE = True
except ImportError:
    _HMM_AVAILABLE = False
    GaussianHMM = None  # type: ignore[assignment, misc]

# ── Enums ────────────────────────────────────────────────────────────────


class Regime(str, Enum):
    """Market regime classification (4-regime model)."""

    BULL = "BULL"
    BEAR = "BEAR"
    SIDEWAYS = "SIDEWAYS"
    CRISIS = "CRISIS"


# ── Pydantic Models ─────────────────────────────────────────────────────


class RegimeState(BaseModel):
    """Result from regime detection — fully serializable for API responses.

    Attributes:
        regime: Detected regime name.
        confidence: Confidence score (0.0–1.0).
        transition_probabilities: Probability of transitioning to each regime.
        regime_index: Numeric index of the regime (0=BULL, 1=BEAR, 2=SIDEWAYS, 3=CRISIS).
        method: Detection method used ("hmm" or "simple").
        features: Feature values used for detection.
        timestamp: UTC timestamp of detection.
        result_id: Unique result identifier.
    """

    model_config = ConfigDict(frozen=False)

    regime: Regime = Regime.SIDEWAYS
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    transition_probabilities: Dict[str, float] = Field(default_factory=dict)
    regime_index: int = Field(default=2, ge=0, le=3)
    method: str = "simple"
    features: Dict[str, float] = Field(default_factory=dict)
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    result_id: str = Field(default_factory=lambda: uuid.uuid4().hex[:12])

    @property
    def is_stressed(self) -> bool:
        """True if market is in a stressed regime (BEAR or CRISIS)."""
        return self.regime in (Regime.BEAR, Regime.CRISIS)

    def to_api_dict(self) -> Dict[str, Any]:
        """Convert to API-safe dictionary (JSON-serializable)."""
        return {
            "regime": self.regime.value,
            "confidence": round(self.confidence, 4),
            "transition_probabilities": {
                k: round(v, 4) for k, v in self.transition_probabilities.items()
            },
            "regime_index": self.regime_index,
            "method": self.method,
            "features": {k: round(v, 6) for k, v in self.features.items()},
            "timestamp": self.timestamp.isoformat(),
            "result_id": self.result_id,
        }


# ── Regime Mapping ──────────────────────────────────────────────────────

# HMM state indices to regime names (based on mean return ordering)
# Will be remapped after fitting based on actual emission means
_REGIME_ORDER = [Regime.BULL, Regime.SIDEWAYS, Regime.BEAR, Regime.CRISIS]
_REGIME_INDEX = {r: i for i, r in enumerate(_REGIME_ORDER)}


# ── HMM Regime Detector ────────────────────────────────────────────────


class HMMRegimeDetector:
    """Hidden Markov Model regime detector with statistical fallback.

    Detects 4 market regimes (BULL, BEAR, SIDEWAYS, CRISIS) from
    price returns and volume data using a Gaussian HMM.

    When ``hmmlearn`` is not installed, automatically falls back to
    a deterministic ADX + ATR heuristic classifier.

    Usage::

        detector = HMMRegimeDetector(n_regimes=4)
        detector.fit(returns=[0.01, -0.02, ...], volumes=[1e6, 1.2e6, ...])
        state = detector.predict(recent_returns, recent_volumes)
        print(state.regime, state.confidence)

    Attributes:
        n_regimes: Number of regimes to detect.
        hmm: Fitted GaussianHMM model (None if hmmlearn not available).
        is_fitted: Whether the model has been fitted.
        use_hmm: Whether HMM is being used (False → fallback).
    """

    def __init__(
        self,
        n_regimes: int = 4,
        lookback: int = 252,
        volatility_window: int = 20,
        random_state: int = 42,
    ) -> None:
        """Initialize the regime detector.

        Args:
            n_regimes: Number of hidden states (default: 4).
            lookback: Minimum data points required for fitting.
            volatility_window: Rolling window for volatility calculation.
            random_state: Random seed for reproducibility.
        """
        self.n_regimes = n_regimes
        self.lookback = lookback
        self.volatility_window = volatility_window
        self.random_state = random_state

        self.hmm: Any = None
        self.is_fitted: bool = False
        self.use_hmm: bool = _HMM_AVAILABLE

        # Mapping from HMM state index → Regime enum
        self._state_map: Dict[int, Regime] = {}
        self._last_transition_matrix: Optional[np.ndarray] = None

    # ── Feature Engineering ──────────────────────────────────────────

    @staticmethod
    def _compute_rolling_volatility(
        returns: List[float], window: int = 20
    ) -> List[float]:
        """Compute rolling volatility (standard deviation of returns).

        Args:
            returns: List of daily returns.
            window: Rolling window size.

        Returns:
            List of rolling volatility values (NaN-padded at start).
        """
        if len(returns) < window:
            if not returns:
                return []
            return [float(np.std(returns))] * len(returns)

        arr = np.array(returns)
        vol = np.full(len(returns), np.nan)
        for i in range(window - 1, len(returns)):
            vol[i] = float(np.std(arr[i - window + 1 : i + 1]))
        # Fill initial NaN with first valid value
        first_valid = vol[window - 1] if window - 1 < len(vol) else 0.0
        vol[: window - 1] = first_valid
        return vol.tolist()

    @staticmethod
    def _compute_volume_change(volumes: List[float]) -> List[float]:
        """Compute percentage change in volume.

        Args:
            volumes: List of volume values.

        Returns:
            List of volume change ratios (first element is 0.0).
        """
        if len(volumes) < 2:
            return [0.0] * len(volumes)
        changes = [0.0]
        for i in range(1, len(volumes)):
            prev = volumes[i - 1]
            if prev > 0:
                changes.append((volumes[i] - prev) / prev)
            else:
                changes.append(0.0)
        return changes

    def _build_features(
        self,
        returns: List[float],
        volumes: Optional[List[float]] = None,
    ) -> np.ndarray:
        """Build the feature matrix for HMM.

        Features: [daily_returns, rolling_volatility, volume_change]

        Args:
            returns: List of daily returns.
            volumes: Optional list of volume values.

        Returns:
            Feature matrix of shape (n_samples, n_features).
        """
        vol = self._compute_rolling_volatility(
            returns, self.volatility_window
        )

        if volumes and len(volumes) == len(returns):
            vol_change = self._compute_volume_change(volumes)
        else:
            vol_change = [0.0] * len(returns)

        features = np.column_stack(
            [
                np.array(returns),
                np.array(vol),
                np.array(vol_change),
            ]
        )

        # Replace any NaN/inf with 0
        features = np.nan_to_num(features, nan=0.0, posinf=0.0, neginf=0.0)
        return features

    # ── HMM Fitting ──────────────────────────────────────────────────

    def fit(
        self,
        returns: List[float],
        volumes: Optional[List[float]] = None,
    ) -> "HMMRegimeDetector":
        """Fit the HMM model on historical returns and volumes.

        When ``hmmlearn`` is not installed, stores data for the
        statistical fallback method.

        Args:
            returns: List of daily returns (log or simple).
            volumes: Optional list of volume values (same length as returns).

        Returns:
            Self, for method chaining.

        Raises:
            ValueError: If insufficient data provided.
        """
        if len(returns) < max(50, self.lookback // 2):
            logger.warning(
                "regime_detector_insufficient_data",
                extra={"n_points": len(returns), "min_required": 50},
            )
            self.is_fitted = False
            return self

        self._features_cache = self._build_features(returns, volumes)

        if not self.use_hmm or not _HMM_AVAILABLE:
            logger.info(
                "regime_detector_using_fallback",
                extra={"reason": "hmmlearn not available"},
            )
            self.is_fitted = True
            return self

        try:
            self.hmm = GaussianHMM(
                n_components=self.n_regimes,
                covariance_type="full",
                n_iter=100,
                random_state=self.random_state,
                tol=1e-4,
            )
            self.hmm.fit(self._features_cache)
            self._build_state_map()
            self._last_transition_matrix = self.hmm.transmat_.copy()
            self.is_fitted = True
            logger.info(
                "regime_detector_fitted",
                extra={
                    "n_samples": len(returns),
                    "n_regimes": self.n_regimes,
                    "state_map": {k: v.value for k, v in self._state_map.items()},
                },
            )
        except Exception as exc:
            logger.warning(
                "regime_detector_hmm_fit_failed",
                extra={"error": str(exc)},
            )
            self.use_hmm = False
            self.is_fitted = True

        return self

    def _build_state_map(self) -> None:
        """Map HMM state indices to regime names based on emission means.

        Ordering by mean return:
        - Highest mean → BULL
        - Second → SIDEWAYS
        - Third → BEAR
        - Lowest → CRISIS (negative + high variance)
        """
        if self.hmm is None:
            return

        means = self.hmm.means_[:, 0]  # First column = return mean
        variances = np.diag(self.hmm.covars_[0]) if self.hmm.covars_.ndim == 3 else np.var(self._features_cache, axis=0)

        # Sort states by mean return (descending)
        sorted_indices = np.argsort(-means)

        self._state_map = {}
        for rank, idx in enumerate(sorted_indices):
            if rank == 0:
                self._state_map[int(idx)] = Regime.BULL
            elif rank == 1:
                self._state_map[int(idx)] = Regime.SIDEWAYS
            elif rank == 2:
                self._state_map[int(idx)] = Regime.BEAR
            else:
                self._state_map[int(idx)] = Regime.CRISIS

    # ── Prediction ───────────────────────────────────────────────────

    def predict(
        self,
        recent_returns: List[float],
        recent_volumes: Optional[List[float]] = None,
    ) -> RegimeState:
        """Predict the current market regime from recent data.

        Args:
            recent_returns: Recent daily returns (at least 10 data points).
            recent_volumes: Optional recent volume data.

        Returns:
            RegimeState with detected regime, confidence, and transition
            probabilities.
        """
        if not self.is_fitted:
            # Auto-fit if we have enough data
            if len(recent_returns) >= 50:
                self.fit(recent_returns, recent_volumes)
            else:
                return RegimeState(
                    regime=Regime.SIDEWAYS,
                    confidence=0.0,
                    method="unfitted",
                )

        if self.use_hmm and self.hmm is not None:
            return self._predict_hmm(recent_returns, recent_volumes)
        else:
            return self._compute_regime_simple(recent_returns, recent_volumes)

    def _predict_hmm(
        self,
        returns: List[float],
        volumes: Optional[List[float]] = None,
    ) -> RegimeState:
        """Predict regime using the fitted HMM model.

        Args:
            returns: Recent daily returns.
            volumes: Optional recent volume data.

        Returns:
            RegimeState from HMM prediction.
        """
        features = self._build_features(returns, volumes)

        try:
            state_sequence = self.hmm.predict(features)
            posteriors = self.hmm.predict_proba(features)

            # Use the most recent state
            current_state_idx = int(state_sequence[-1])
            current_posterior = posteriors[-1]

            # Map to regime
            regime = self._state_map.get(current_state_idx, Regime.SIDEWAYS)
            confidence = float(np.max(current_posterior))

            # Build transition probabilities from current state
            trans_probs: Dict[str, float] = {}
            if self._last_transition_matrix is not None:
                for j in range(self.n_regimes):
                    target_regime = self._state_map.get(j, Regime.SIDEWAYS)
                    trans_probs[target_regime.value] = float(
                        self._last_transition_matrix[current_state_idx, j]
                    )

            # Compute feature summary
            feature_summary = {
                "mean_return": float(np.mean(returns)),
                "volatility": float(np.std(returns)),
                "max_drawdown": float(
                    min(0.0, min(np.cumsum(returns)))
                ),
            }

            return RegimeState(
                regime=regime,
                confidence=min(1.0, confidence),
                transition_probabilities=trans_probs,
                regime_index=_REGIME_INDEX.get(regime, 2),
                method="hmm",
                features=feature_summary,
            )

        except Exception as exc:
            logger.warning(
                "hmm_predict_failed_using_fallback",
                extra={"error": str(exc)},
            )
            return self._compute_regime_simple(returns, volumes)

    # ── Statistical Fallback ─────────────────────────────────────────

    def _compute_regime_simple(
        self,
        returns: List[float],
        volumes: Optional[List[float]] = None,
    ) -> RegimeState:
        """Compute regime using ADX + ATR heuristics (fallback method).

        This deterministic classifier uses:
        - Mean return → direction (bull vs bear)
        - Volatility → regime stability
        - Max drawdown → crisis detection
        - Volume ratio → confirmation

        Args:
            returns: Recent daily returns.
            volumes: Optional recent volume data.

        Returns:
            RegimeState from statistical classification.
        """
        if len(returns) < 5:
            return RegimeState(
                regime=Regime.SIDEWAYS,
                confidence=0.0,
                method="simple",
            )

        arr = np.array(returns)
        mean_return = float(np.mean(arr))
        volatility = float(np.std(arr))
        max_drawdown = float(min(0.0, min(np.cumsum(arr))))
        min_return = float(np.min(arr))

        # ADX approximation: directional movement ratio
        adx = self._compute_adx_approx(returns)

        # ATR approximation: normalized volatility
        atr_pct = volatility * 100  # As percentage

        # Volume analysis
        vol_ratio = 1.0
        if volumes and len(volumes) >= 10:
            recent_vol = np.mean(volumes[-5:])
            avg_vol = np.mean(volumes)
            if avg_vol > 0:
                vol_ratio = float(recent_vol / avg_vol)

        # ── Regime Classification ────────────────────────────────────

        confidence = 0.5
        regime = Regime.SIDEWAYS

        # Priority 1: CRISIS — extreme negative move
        if min_return < -0.05 or max_drawdown < -0.10:
            regime = Regime.CRISIS
            confidence = 0.85 + min(0.15, abs(min_return) * 2)

        # Priority 2: High volatility
        elif volatility > 0.03:
            if mean_return < -0.005:
                regime = Regime.BEAR
                confidence = 0.7 + min(0.2, abs(mean_return) * 10)
            else:
                regime = Regime.SIDEWAYS
                confidence = 0.5

        # Priority 3: BULL — positive drift with trend
        elif mean_return > 0.002 and adx > 25:
            regime = Regime.BULL
            confidence = 0.6 + min(0.3, (adx - 25) / 50)

        # Priority 4: BEAR — negative drift with trend
        elif mean_return < -0.002 and adx > 25:
            regime = Regime.BEAR
            confidence = 0.6 + min(0.3, (adx - 25) / 50)

        # Priority 5: SIDEWAYS — low ADX, small drift
        elif adx < 20 and abs(mean_return) < 0.002:
            regime = Regime.SIDEWAYS
            confidence = 0.6 + min(0.3, (20 - adx) / 20)

        # Default by drift direction
        elif mean_return > 0:
            regime = Regime.BULL
            confidence = 0.4
        else:
            regime = Regime.BEAR
            confidence = 0.4

        # Volume confirmation boost
        if vol_ratio > 1.5 and regime in (Regime.BULL, Regime.BEAR):
            confidence = min(0.95, confidence + 0.05)

        # ── Transition Probabilities ─────────────────────────────────

        trans_probs = self._compute_simple_transitions(
            regime, mean_return, volatility, adx
        )

        feature_summary = {
            "mean_return": mean_return,
            "volatility": volatility,
            "max_drawdown": max_drawdown,
            "min_return": min_return,
            "adx_approx": adx,
            "atr_pct": atr_pct,
            "volume_ratio": vol_ratio,
        }

        return RegimeState(
            regime=regime,
            confidence=min(1.0, confidence),
            transition_probabilities=trans_probs,
            regime_index=_REGIME_INDEX.get(regime, 2),
            method="simple",
            features=feature_summary,
        )

    @staticmethod
    def _compute_adx_approx(returns: List[float]) -> float:
        """Compute a simplified ADX approximation from returns.

        Real ADX uses high/low/close; this approximation uses
        directional movement ratio from returns.

        Args:
            returns: List of daily returns.

        Returns:
            ADX-like value (0–100).
        """
        if len(returns) < 3:
            return 0.0

        up_moves = 0.0
        down_moves = 0.0
        for r in returns:
            if r > 0:
                up_moves += r
            else:
                down_moves += abs(r)

        total = up_moves + down_moves
        if total == 0:
            return 0.0

        dx = abs(up_moves - down_moves) / total * 100
        return min(100.0, dx)

    def _compute_simple_transitions(
        self,
        current: Regime,
        mean_return: float,
        volatility: float,
        adx: float,
    ) -> Dict[str, float]:
        """Compute rough transition probabilities from current regime.

        Based on regime persistence patterns and feature drift.

        Args:
            current: Current regime.
            mean_return: Mean return of the period.
            volatility: Return volatility.
            adx: ADX approximation.

        Returns:
            Dictionary mapping regime name → transition probability.
        """
        # Base transition matrix (empirical prior)
        base: Dict[Regime, Dict[Regime, float]] = {
            Regime.BULL: {
                Regime.BULL: 0.65,
                Regime.SIDEWAYS: 0.20,
                Regime.BEAR: 0.10,
                Regime.CRISIS: 0.05,
            },
            Regime.BEAR: {
                Regime.BEAR: 0.55,
                Regime.SIDEWAYS: 0.20,
                Regime.BULL: 0.10,
                Regime.CRISIS: 0.15,
            },
            Regime.SIDEWAYS: {
                Regime.SIDEWAYS: 0.50,
                Regime.BULL: 0.25,
                Regime.BEAR: 0.20,
                Regime.CRISIS: 0.05,
            },
            Regime.CRISIS: {
                Regime.CRISIS: 0.30,
                Regime.BEAR: 0.35,
                Regime.SIDEWAYS: 0.25,
                Regime.BULL: 0.10,
            },
        }

        probs = base.get(current, base[Regime.SIDEWAYS]).copy()

        # Adjust based on features: high volatility → more likely crisis/bear
        if volatility > 0.03:
            probs[Regime.CRISIS] += 0.05
            probs[Regime.BEAR] += 0.05
            probs[Regime.SIDEWAYS] -= 0.05
            probs[Regime.BULL] -= 0.05

        # Mean return drift adjustment
        if mean_return > 0.005:
            probs[Regime.BULL] += 0.05
            probs[Regime.BEAR] -= 0.05
        elif mean_return < -0.005:
            probs[Regime.BEAR] += 0.05
            probs[Regime.BULL] -= 0.05

        # Normalize to sum to 1.0
        total = sum(probs.values())
        if total > 0:
            for k in probs:
                probs[k] = max(0.0, probs[k] / total)

        return {r.value: round(p, 4) for r, p in probs.items()}

    # ── Utility Methods ──────────────────────────────────────────────

    @property
    def stats(self) -> Dict[str, Any]:
        """Get detector statistics."""
        return {
            "is_fitted": self.is_fitted,
            "use_hmm": self.use_hmm,
            "n_regimes": self.n_regimes,
            "hmm_available": _HMM_AVAILABLE,
            "state_map": {k: v.value for k, v in self._state_map.items()},
        }


# ═══════════════════════════════════════════════════════════════════════
# Demo
# ═══════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    import asyncio

    # Generate synthetic data for demo
    np.random.seed(42)

    # Bull phase: positive drift, low vol
    bull_returns = np.random.normal(0.002, 0.008, 100).tolist()
    # Crisis phase: negative drift, high vol
    crisis_returns = np.random.normal(-0.01, 0.04, 30).tolist()
    # Recovery (sideways): near-zero drift, moderate vol
    sideways_returns = np.random.normal(0.0001, 0.012, 50).tolist()
    # Bear phase: negative drift, moderate vol
    bear_returns = np.random.normal(-0.003, 0.015, 50).tolist()

    all_returns = bull_returns + crisis_returns + sideways_returns + bear_returns
    all_volumes = [1e6 + np.random.normal(0, 1e5) for _ in all_returns]

    # ── Demo with HMM (if available) ─────────────────────────────────
    detector = HMMRegimeDetector(n_regimes=4)
    detector.fit(all_returns, all_volumes)

    print(f"HMM available: {_HMM_AVAILABLE}")
    print(f"Using HMM: {detector.use_hmm}")
    print(f"Is fitted: {detector.is_fitted}")

    # Predict on recent data
    recent = all_returns[-30:]
    recent_vol = all_volumes[-30:]
    state = detector.predict(recent, recent_vol)

    print(f"\nDetected Regime: {state.regime.value}")
    print(f"Confidence: {state.confidence:.2%}")
    print(f"Method: {state.method}")
    print(f"Features: {state.features}")
    print(f"Transitions: {state.transition_probabilities}")
    print(f"API dict: {state.to_api_dict()}")

    # ── Test each regime type ─────────────────────────────────────────
    print("\n--- Testing each regime type ---")

    # Bull: positive drift, low vol
    bull_test = detector.predict(
        np.random.normal(0.003, 0.008, 30).tolist()
    )
    print(f"Bull test → {bull_test.regime.value} (conf: {bull_test.confidence:.2%})")

    # Bear: negative drift, moderate vol
    bear_test = detector.predict(
        np.random.normal(-0.004, 0.015, 30).tolist()
    )
    print(f"Bear test → {bear_test.regime.value} (conf: {bear_test.confidence:.2%})")

    # Crisis: extreme negative, high vol
    crisis_test = detector.predict(
        np.random.normal(-0.015, 0.05, 20).tolist()
    )
    print(f"Crisis test → {crisis_test.regime.value} (conf: {crisis_test.confidence:.2%})")

    # Sideways: near-zero drift, low vol
    sideways_test = detector.predict(
        np.random.normal(0.0001, 0.005, 30).tolist()
    )
    print(f"Sideways test → {sideways_test.regime.value} (conf: {sideways_test.confidence:.2%})")

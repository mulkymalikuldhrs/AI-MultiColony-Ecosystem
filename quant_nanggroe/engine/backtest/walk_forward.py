"""Walk-Forward Analysis — Production-Grade Validation.

Implements proper walk-forward analysis for robust strategy validation,
including:

1. Anchored walk-forward (expanding window)
2. Rolling walk-forward (fixed window)
3. Combinatorial purged cross-validation (CPCV) — de Prado method
4. Purged k-fold cross-validation with embargo
5. Proper in-sample/out-of-sample split with gap (embargo period)
6. Leakage prevention (no lookahead bias)
7. Multiple optimization criteria (Sharpe, Sortino, Calmar, etc.)
8. Parameter grid search and random search
9. Results aggregation with statistical significance tests
10. Overfitting detection (deflated Sharpe ratio)

References:
- Pardo (2008), "The Evaluation and Optimization of Trading Strategies"
- De Prado (2018), "Advances in Financial Machine Learning"
- Bailey, Borwein, Lopez de Prado, Zhu (2017), "The Probability of Backtest Overfitting"
"""

from __future__ import annotations

import logging
import itertools
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
from scipy import stats as sp_stats

logger = logging.getLogger(__name__)


class WFMethod(str, Enum):
    """Walk-forward method."""
    ANCHORED = "anchored"
    ROLLING = "rolling"
    PURGED_KFOLD = "purged_kfold"
    CPCV = "cpcv"


class OptimizationCriterion(str, Enum):
    """Optimization criterion for parameter selection."""
    SHARPE = "sharpe"
    SORTINO = "sortino"
    CALMAR = "calmar"
    TOTAL_RETURN = "total_return"
    OMEGA = "omega"
    INFORMATION_RATIO = "information_ratio"


@dataclass
class WFWindowResult:
    """Result from a single walk-forward window."""

    fold_id: int
    train_start: pd.Timestamp
    train_end: pd.Timestamp
    test_start: pd.Timestamp
    test_end: pd.Timestamp
    embargo_bars: int
    in_sample_metrics: Dict[str, float]
    out_of_sample_metrics: Dict[str, float]
    best_params: Dict[str, Any]
    degradation_ratio: float  # OOS/IS performance ratio
    oos_sharpe: float
    oos_return: float
    oos_max_dd: float

    # Backward-compatible properties
    @property
    def in_sample_return(self) -> float:
        return self.in_sample_metrics.get("total_return", 0.0)

    @property
    def out_of_sample_return(self) -> float:
        return self.oos_return

    @property
    def in_sample_sharpe(self) -> float:
        return self.in_sample_metrics.get("sharpe_ratio", 0.0)

    @property
    def out_of_sample_sharpe(self) -> float:
        return self.oos_sharpe

    @property
    def in_sample_max_dd(self) -> float:
        return self.in_sample_metrics.get("max_drawdown", 0.0)

    @property
    def out_of_sample_max_dd(self) -> float:
        return self.oos_max_dd


@dataclass
class WFResult:
    """Complete walk-forward analysis result.

    Supports dict-style access for backward compatibility:
        result["windows"], result["aggregate"], result["degradation_stats"]
    """

    method: WFMethod
    windows: List[WFWindowResult]
    aggregate: Dict[str, Any]
    degradation_stats: Dict[str, Any]
    significance_tests: Dict[str, Any]
    overfitting_detection: Dict[str, Any]
    all_oos_returns: pd.Series
    all_oos_sharpes: List[float]

    _KEY_MAPPING = {
        "windows": "windows",
        "aggregate": "aggregate",
        "degradation_stats": "degradation_stats",
        "significance_tests": "significance_tests",
        "overfitting_detection": "overfitting_detection",
        "method": "method",
        "all_oos_returns": "all_oos_returns",
        "all_oos_sharpes": "all_oos_sharpes",
    }

    def __getitem__(self, key: str) -> Any:
        """Dict-style access for backward compatibility."""
        if isinstance(key, str) and key in self._KEY_MAPPING:
            return getattr(self, self._KEY_MAPPING[key])
        raise KeyError(key)

    def __contains__(self, key: object) -> bool:
        """Support `in` operator for dict-style membership testing."""
        return isinstance(key, str) and key in self._KEY_MAPPING


@dataclass
class ParameterGrid:
    """Parameter grid for optimization.

    Attributes:
        params: Dict of parameter_name -> list of values.
    """

    params: Dict[str, List[Any]]

    def combinations(self) -> List[Dict[str, Any]]:
        """Generate all parameter combinations."""
        if not self.params:
            return [{}]
        keys = list(self.params.keys())
        values = list(self.params.values())
        combos = list(itertools.product(*values))
        return [dict(zip(keys, combo)) for combo in combos]

    def random_combinations(
        self,
        n: int,
        random_seed: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        """Generate n random parameter combinations."""
        rng = np.random.default_rng(random_seed)
        combos = self.combinations()
        if n >= len(combos):
            return combos
        indices = rng.choice(len(combos), size=n, replace=False)
        return [combos[i] for i in indices]


class WalkForwardAnalyzer:
    """Production-grade Walk-Forward Analysis for strategy validation.

    Implements anchored, rolling, purged k-fold, and CPCV methods with
    proper leakage prevention, embargo periods, and statistical
    significance testing.

    Usage:
        analyzer = WalkForwardAnalyzer(
            engine=my_engine,
            train_window=252,
            test_window=63,
            method=WFMethod.ROLLING,
            embargo_bars=5,
        )
        result = analyzer.analyze(prices, signals)
    """

    def __init__(
        self,
        engine: Any,  # BacktestEngine
        train_window: int = 252,
        test_window: int = 63,
        method: WFMethod = WFMethod.ROLLING,
        embargo_bars: int = 5,
        min_observations: int = 60,
        optimization_criterion: OptimizationCriterion = OptimizationCriterion.SHARPE,
        param_grid: Optional[ParameterGrid] = None,
        n_random_search: Optional[int] = None,
        random_seed: Optional[int] = None,
        bars_per_year: int = 252,
        anchored: bool = False,
    ) -> None:
        """Initialize walk-forward analyzer.

        Args:
            engine: BacktestEngine instance.
            train_window: Training window in bars.
            test_window: Test window in bars.
            method: Walk-forward method (anchored, rolling, purged_kfold, cpcv).
            embargo_bars: Number of bars to exclude between train and test
                to prevent lookahead bias (leakage prevention).
            min_observations: Minimum observations required for a valid window.
            optimization_criterion: Criterion for parameter optimization.
            param_grid: Parameter grid for optimization.
            n_random_search: If set, use random search with this many combos.
            random_seed: Seed for random search reproducibility.
            bars_per_year: Bars per year for annualization.
        """
        self.engine = engine
        self.train_window = train_window
        self.test_window = test_window
        self.method = method
        self.embargo_bars = embargo_bars
        self.min_observations = min_observations
        self.optimization_criterion = optimization_criterion
        self.param_grid = param_grid
        self.n_random_search = n_random_search
        self.random_seed = random_seed
        self.bars_per_year = bars_per_year

        # Backward compatible: anchored parameter
        if anchored and method == WFMethod.ROLLING:
            self.method = WFMethod.ANCHORED

    def analyze(
        self,
        prices: pd.DataFrame,
        signals: pd.DataFrame,
        signal_generator: Optional[Callable] = None,
        **kwargs: Any,
    ) -> WFResult:
        """Run walk-forward analysis.

        Args:
            prices: Price data with DatetimeIndex.
            signals: Signal data with same index.
            signal_generator: Optional callable that takes (prices_train, params)
                and returns signals DataFrame. If None, uses signals directly.
            **kwargs: Additional arguments passed to engine.run().

        Returns:
            WFResult with detailed results and statistical tests.
        """
        if self.method == WFMethod.ANCHORED:
            return self._anchored_wf(prices, signals, signal_generator, **kwargs)
        elif self.method == WFMethod.ROLLING:
            return self._rolling_wf(prices, signals, signal_generator, **kwargs)
        elif self.method == WFMethod.PURGED_KFOLD:
            return self._purged_kfold(prices, signals, signal_generator, **kwargs)
        elif self.method == WFMethod.CPCV:
            return self._cpcv(prices, signals, signal_generator, **kwargs)
        else:
            return self._rolling_wf(prices, signals, signal_generator, **kwargs)

    # ══════════════════════════════════════════════════════════════════
    # Anchored Walk-Forward (Expanding Window)
    # ══════════════════════════════════════════════════════════════════

    def _anchored_wf(
        self,
        prices: pd.DataFrame,
        signals: pd.DataFrame,
        signal_generator: Optional[Callable],
        **kwargs: Any,
    ) -> WFResult:
        """Anchored walk-forward: training window expands from start.

        Each fold uses ALL data from the beginning up to train_end,
        with embargo period before test_start.
        """
        n_bars = len(prices)
        total_window = self.train_window + self.embargo_bars + self.test_window

        if n_bars < total_window:
            logger.warning("Insufficient data for anchored WF: %d < %d", n_bars, total_window)
            return self._empty_result()

        windows: List[WFWindowResult] = []
        test_start_idx = self.train_window + self.embargo_bars

        fold_id = 0
        while test_start_idx + self.test_window <= n_bars:
            train_start_idx = 0  # Anchored: always from start
            train_end_idx = test_start_idx - self.embargo_bars

            if train_end_idx - train_start_idx < self.min_observations:
                break

            wf_result = self._run_fold(
                fold_id=fold_id,
                prices=prices,
                signals=signals,
                signal_generator=signal_generator,
                train_start=train_start_idx,
                train_end=train_end_idx,
                test_start=test_start_idx,
                test_end=test_start_idx + self.test_window,
                **kwargs,
            )

            if wf_result is not None:
                windows.append(wf_result)

            fold_id += 1
            test_start_idx += self.test_window

        return self._build_result(windows)

    # ══════════════════════════════════════════════════════════════════
    # Rolling Walk-Forward (Fixed Window)
    # ══════════════════════════════════════════════════════════════════

    def _rolling_wf(
        self,
        prices: pd.DataFrame,
        signals: pd.DataFrame,
        signal_generator: Optional[Callable],
        **kwargs: Any,
    ) -> WFResult:
        """Rolling walk-forward: fixed-size training window rolls forward.

        Each fold uses a fixed-size training window that rolls forward,
        with embargo period before test_start.
        """
        n_bars = len(prices)
        total_window = self.train_window + self.embargo_bars + self.test_window

        if n_bars < total_window:
            logger.warning("Insufficient data for rolling WF: %d < %d", n_bars, total_window)
            return self._empty_result()

        windows: List[WFWindowResult] = []
        start_idx = 0
        fold_id = 0

        while start_idx + total_window <= n_bars:
            train_start = start_idx
            train_end = start_idx + self.train_window
            test_start = train_end + self.embargo_bars
            test_end = test_start + self.test_window

            if test_end > n_bars:
                break

            wf_result = self._run_fold(
                fold_id=fold_id,
                prices=prices,
                signals=signals,
                signal_generator=signal_generator,
                train_start=train_start,
                train_end=train_end,
                test_start=test_start,
                test_end=test_end,
                **kwargs,
            )

            if wf_result is not None:
                windows.append(wf_result)

            fold_id += 1
            start_idx += self.test_window  # Roll by test_window

        return self._build_result(windows)

    # ══════════════════════════════════════════════════════════════════
    # Purged K-Fold Cross-Validation
    # ══════════════════════════════════════════════════════════════════

    def _purged_kfold(
        self,
        prices: pd.DataFrame,
        signals: pd.DataFrame,
        signal_generator: Optional[Callable],
        n_folds: int = 5,
        **kwargs: Any,
    ) -> WFResult:
        """Purged k-fold cross-validation with embargo.

        Implements de Prado's purged k-fold CV:
        1. Split data into k folds
        2. For each fold, use it as test set
        3. Purge observations from train set that overlap with test
        4. Apply embargo period after test set

        This prevents information leakage from the test set into
        the training set, which is critical for time series data.

        Args:
            prices: Price data.
            signals: Signal data.
            signal_generator: Optional signal generator.
            n_folds: Number of folds.
        """
        n_bars = len(prices)
        fold_size = n_bars // n_folds

        if fold_size < self.min_observations:
            logger.warning("Insufficient data for %d-fold CV", n_folds)
            return self._empty_result()

        windows: List[WFWindowResult] = []

        for fold_id in range(n_folds):
            # Test set: this fold
            test_start = fold_id * fold_size
            test_end = min((fold_id + 1) * fold_size, n_bars)

            # Train set: everything except test + embargo
            # Purge: remove overlap period before test
            # Embargo: remove period after test
            embargo_end = min(test_end + self.embargo_bars, n_bars)
            purge_start = max(0, test_start - self.embargo_bars)

            # Build train indices: before purge and after embargo
            train_indices = list(range(0, purge_start)) + list(range(embargo_end, n_bars))

            if len(train_indices) < self.min_observations:
                continue

            # Extract train data (may be non-contiguous)
            train_prices = prices.iloc[train_indices]
            train_signals = signals.iloc[train_indices] if signal_generator is None else signals.iloc[train_indices]
            test_prices = prices.iloc[test_start:test_end]
            test_signals = signals.iloc[test_start:test_end]

            # Run in-sample and out-of-sample
            is_metrics, oos_metrics, best_params = self._optimize_and_evaluate(
                train_prices, train_signals,
                test_prices, test_signals,
                signal_generator, **kwargs,
            )

            # Calculate degradation
            criterion_key = self._criterion_key()
            is_val = is_metrics.get(criterion_key, 0.0)
            oos_val = oos_metrics.get(criterion_key, 0.0)
            degradation = oos_val / is_val if abs(is_val) > 1e-10 else 0.0

            wf_result = WFWindowResult(
                fold_id=fold_id,
                train_start=prices.index[train_indices[0]],
                train_end=prices.index[train_indices[-1]],
                test_start=prices.index[test_start],
                test_end=prices.index[min(test_end - 1, n_bars - 1)],
                embargo_bars=self.embargo_bars,
                in_sample_metrics=is_metrics,
                out_of_sample_metrics=oos_metrics,
                best_params=best_params,
                degradation_ratio=degradation,
                oos_sharpe=oos_metrics.get("sharpe_ratio", 0.0),
                oos_return=oos_metrics.get("total_return", 0.0),
                oos_max_dd=oos_metrics.get("max_drawdown", 0.0),
            )
            windows.append(wf_result)

        return self._build_result(windows)

    # ══════════════════════════════════════════════════════════════════
    # Combinatorial Purged Cross-Validation (CPCV)
    # ══════════════════════════════════════════════════════════════════

    def _cpcv(
        self,
        prices: pd.DataFrame,
        signals: pd.DataFrame,
        signal_generator: Optional[Callable],
        n_groups: int = 6,
        n_test_groups: int = 2,
        **kwargs: Any,
    ) -> WFResult:
        """Combinatorial Purged Cross-Validation (de Prado method).

        CPCV generates all combinations of n_test_groups out of n_groups,
        where each combination defines a test set. This provides many
        backtest paths for robust evaluation.

        Args:
            prices: Price data.
            signals: Signal data.
            signal_generator: Optional signal generator.
            n_groups: Number of groups to split data into.
            n_test_groups: Number of groups to use as test set per combination.
        """
        from itertools import combinations

        n_bars = len(prices)
        group_size = n_bars // n_groups

        if group_size < self.min_observations:
            logger.warning("Insufficient data for CPCV with %d groups", n_groups)
            return self._empty_result()

        windows: List[WFWindowResult] = []
        fold_id = 0

        # Generate all combinations of test groups
        group_indices = list(range(n_groups))
        test_combos = list(combinations(group_indices, n_test_groups))

        for test_groups in test_combos:
            # Build test indices
            test_indices = []
            for g in test_groups:
                start = g * group_size
                end = min((g + 1) * group_size, n_bars)
                test_indices.extend(range(start, end))

            # Build train indices (all groups not in test, with purge/embargo)
            train_groups = [g for g in group_indices if g not in test_groups]
            train_indices = []
            for g in train_groups:
                start = g * group_size
                end = min((g + 1) * group_size, n_bars)
                # Apply embargo: skip bars near test groups
                for idx in range(start, end):
                    is_near_test = False
                    for test_idx in test_indices:
                        if abs(idx - test_idx) <= self.embargo_bars:
                            is_near_test = True
                            break
                    if not is_near_test:
                        train_indices.append(idx)

            if len(train_indices) < self.min_observations or len(test_indices) < 10:
                continue

            # Extract data
            train_prices = prices.iloc[train_indices]
            train_signals = signals.iloc[train_indices]
            test_prices = prices.iloc[test_indices]
            test_signals = signals.iloc[test_indices]

            # Run optimization and evaluation
            is_metrics, oos_metrics, best_params = self._optimize_and_evaluate(
                train_prices, train_signals,
                test_prices, test_signals,
                signal_generator, **kwargs,
            )

            criterion_key = self._criterion_key()
            is_val = is_metrics.get(criterion_key, 0.0)
            oos_val = oos_metrics.get(criterion_key, 0.0)
            degradation = oos_val / is_val if abs(is_val) > 1e-10 else 0.0

            wf_result = WFWindowResult(
                fold_id=fold_id,
                train_start=prices.index[train_indices[0]],
                train_end=prices.index[train_indices[-1]],
                test_start=prices.index[test_indices[0]],
                test_end=prices.index[test_indices[-1]],
                embargo_bars=self.embargo_bars,
                in_sample_metrics=is_metrics,
                out_of_sample_metrics=oos_metrics,
                best_params=best_params,
                degradation_ratio=degradation,
                oos_sharpe=oos_metrics.get("sharpe_ratio", 0.0),
                oos_return=oos_metrics.get("total_return", 0.0),
                oos_max_dd=oos_metrics.get("max_drawdown", 0.0),
            )
            windows.append(wf_result)
            fold_id += 1

        return self._build_result(windows)

    # ══════════════════════════════════════════════════════════════════
    # Core Evaluation Methods
    # ══════════════════════════════════════════════════════════════════

    def _run_fold(
        self,
        fold_id: int,
        prices: pd.DataFrame,
        signals: pd.DataFrame,
        signal_generator: Optional[Callable],
        train_start: int,
        train_end: int,
        test_start: int,
        test_end: int,
        **kwargs: Any,
    ) -> Optional[WFWindowResult]:
        """Run a single walk-forward fold with optional parameter optimization."""
        # Extract data slices
        train_prices = prices.iloc[train_start:train_end]
        train_signals = signals.iloc[train_start:train_end]
        test_prices = prices.iloc[test_start:test_end]
        test_signals = signals.iloc[test_start:test_end]

        if len(train_prices) < self.min_observations or len(test_prices) < 5:
            return None

        # Optimize and evaluate
        is_metrics, oos_metrics, best_params = self._optimize_and_evaluate(
            train_prices, train_signals,
            test_prices, test_signals,
            signal_generator, **kwargs,
        )

        # Calculate degradation
        criterion_key = self._criterion_key()
        is_val = is_metrics.get(criterion_key, 0.0)
        oos_val = oos_metrics.get(criterion_key, 0.0)
        degradation = oos_val / is_val if abs(is_val) > 1e-10 else 0.0

        return WFWindowResult(
            fold_id=fold_id,
            train_start=prices.index[train_start],
            train_end=prices.index[min(train_end - 1, len(prices) - 1)],
            test_start=prices.index[test_start],
            test_end=prices.index[min(test_end - 1, len(prices) - 1)],
            embargo_bars=self.embargo_bars,
            in_sample_metrics=is_metrics,
            out_of_sample_metrics=oos_metrics,
            best_params=best_params,
            degradation_ratio=degradation,
            oos_sharpe=oos_metrics.get("sharpe_ratio", 0.0),
            oos_return=oos_metrics.get("total_return", 0.0),
            oos_max_dd=oos_metrics.get("max_drawdown", 0.0),
        )

    def _optimize_and_evaluate(
        self,
        train_prices: pd.DataFrame,
        train_signals: pd.DataFrame,
        test_prices: pd.DataFrame,
        test_signals: pd.DataFrame,
        signal_generator: Optional[Callable],
        **kwargs: Any,
    ) -> Tuple[Dict[str, float], Dict[str, float], Dict[str, Any]]:
        """Optimize parameters on training data and evaluate on test data.

        Returns:
            Tuple of (is_metrics, oos_metrics, best_params).
        """
        if self.param_grid is None:
            # No optimization: use signals as-is
            is_result = self.engine.run(train_prices, train_signals, **kwargs)
            oos_result = self.engine.run(test_prices, test_signals, **kwargs)
            return (
                is_result.get("metrics", {}),
                oos_result.get("metrics", {}),
                {},
            )

        # Parameter optimization
        if self.n_random_search is not None:
            param_combos = self.param_grid.random_combinations(
                self.n_random_search, self.random_seed
            )
        else:
            param_combos = self.param_grid.combinations()

        best_is_score = float("-inf")
        best_params: Dict[str, Any] = {}
        best_is_metrics: Dict[str, float] = {}

        criterion_key = self._criterion_key()

        for params in param_combos:
            # Generate signals with these parameters
            if signal_generator is not None:
                try:
                    train_sig = signal_generator(train_prices, params)
                except Exception as e:
                    logger.warning("Signal generation failed for params %s: %s", params, e)
                    continue
            else:
                train_sig = train_signals

            try:
                result = self.engine.run(train_prices, train_sig, **kwargs)
                metrics = result.get("metrics", {})
                score = metrics.get(criterion_key, float("-inf"))

                if score > best_is_score:
                    best_is_score = score
                    best_params = params
                    best_is_metrics = metrics
            except Exception as e:
                logger.warning("Backtest failed for params %s: %s", params, e)
                continue

        # Evaluate best parameters on test set
        if signal_generator is not None and best_params:
            try:
                test_sig = signal_generator(test_prices, best_params)
            except Exception:
                test_sig = test_signals
        else:
            test_sig = test_signals

        try:
            oos_result = self.engine.run(test_prices, test_sig, **kwargs)
            oos_metrics = oos_result.get("metrics", {})
        except Exception as e:
            logger.warning("OOS backtest failed: %s", e)
            oos_metrics = {}

        return best_is_metrics, oos_metrics, best_params

    # ══════════════════════════════════════════════════════════════════
    # Result Aggregation
    # ══════════════════════════════════════════════════════════════════

    def _build_result(self, windows: List[WFWindowResult]) -> WFResult:
        """Build complete WFResult from window results."""
        aggregate = self._calculate_aggregate(windows)
        degradation_stats = self._calculate_degradation_stats(windows)
        significance_tests = self._calculate_significance(windows)
        overfitting = self._detect_overfitting(windows)

        # Collect OOS returns and Sharpes
        oos_returns_list = [w.oos_return for w in windows]
        oos_sharpes = [w.oos_sharpe for w in windows]
        oos_returns_series = pd.Series(oos_returns_list)

        return WFResult(
            method=self.method,
            windows=windows,
            aggregate=aggregate,
            degradation_stats=degradation_stats,
            significance_tests=significance_tests,
            overfitting_detection=overfitting,
            all_oos_returns=oos_returns_series,
            all_oos_sharpes=oos_sharpes,
        )

    def _calculate_aggregate(self, windows: List[WFWindowResult]) -> Dict[str, Any]:
        """Calculate aggregate walk-forward statistics."""
        if not windows:
            return {}

        oos_returns = [w.oos_return for w in windows]
        oos_sharpes = [w.oos_sharpe for w in windows]
        oos_dds = [w.oos_max_dd for w in windows]

        return {
            "num_windows": len(windows),
            "avg_oos_return": float(np.mean(oos_returns)),
            "median_oos_return": float(np.median(oos_returns)),
            "std_oos_return": float(np.std(oos_returns)) if len(oos_returns) > 1 else 0.0,
            "avg_oos_sharpe": float(np.mean(oos_sharpes)),
            "median_oos_sharpe": float(np.median(oos_sharpes)),
            "std_oos_sharpe": float(np.std(oos_sharpes)) if len(oos_sharpes) > 1 else 0.0,
            "avg_oos_max_dd": float(np.mean(oos_dds)),
            "win_rate": sum(1 for r in oos_returns if r > 0) / len(oos_returns),
            "worst_oos_return": min(oos_returns),
            "best_oos_return": max(oos_returns),
            "cumulative_oos_return": float(np.prod([1 + r for r in oos_returns]) - 1),
        }

    def _calculate_degradation_stats(self, windows: List[WFWindowResult]) -> Dict[str, Any]:
        """Calculate degradation statistics (IS vs OOS)."""
        if not windows:
            return {}

        ratios = [w.degradation_ratio for w in windows]

        return {
            "avg_degradation": float(np.mean(ratios)),
            "median_degradation": float(np.median(ratios)),
            "min_degradation": float(np.min(ratios)),
            "max_degradation": float(np.max(ratios)),
            "std_degradation": float(np.std(ratios)) if len(ratios) > 1 else 0.0,
            "healthy_windows": sum(1 for d in ratios if d > 0.5),
            "total_windows": len(windows),
            "pass_rate": sum(1 for d in ratios if d > 0.5) / len(windows),
        }

    def _calculate_significance(self, windows: List[WFWindowResult]) -> Dict[str, Any]:
        """Statistical significance tests on OOS results."""
        if len(windows) < 3:
            return {"note": "Insufficient windows for significance testing"}

        oos_returns = np.array([w.oos_return for w in windows])
        oos_sharpes = np.array([w.oos_sharpe for w in windows])

        result: Dict[str, Any] = {}

        # t-test: H0 = mean OOS return = 0
        if len(oos_returns) > 1 and np.std(oos_returns) > 1e-10:
            t_stat, p_value = sp_stats.ttest_1samp(oos_returns, 0.0)
            result["t_test_return"] = {
                "statistic": float(t_stat),
                "p_value": float(p_value),
                "significant_at_5pct": p_value < 0.05,
            }

        # t-test: H0 = mean OOS Sharpe = 0
        if len(oos_sharpes) > 1 and np.std(oos_sharpes) > 1e-10:
            t_stat, p_value = sp_stats.ttest_1samp(oos_sharpes, 0.0)
            result["t_test_sharpe"] = {
                "statistic": float(t_stat),
                "p_value": float(p_value),
                "significant_at_5pct": p_value < 0.05,
            }

        # Wilcoxon signed-rank test (non-parametric)
        if len(oos_returns) >= 5:
            try:
                stat, p_value = sp_stats.wilcoxon(oos_returns, alternative="greater")
                result["wilcoxon_return"] = {
                    "statistic": float(stat),
                    "p_value": float(p_value),
                    "significant_at_5pct": p_value < 0.05,
                }
            except ValueError:
                pass

        return result

    def _detect_overfitting(self, windows: List[WFWindowResult]) -> Dict[str, Any]:
        """Detect overfitting using deflated Sharpe ratio and other methods.

        Uses the De Prado/Bailey deflated Sharpe ratio to detect if
        the observed Sharpe ratio is likely due to multiple testing.
        """
        if not windows:
            return {}

        oos_sharpes = [w.oos_sharpe for w in windows]
        is_sharpes = [w.in_sample_metrics.get("sharpe_ratio", 0.0) for w in windows]

        avg_oos_sharpe = float(np.mean(oos_sharpes))
        avg_is_sharpe = float(np.mean(is_sharpes))
        n_windows = len(windows)

        # Overfitting detection: IS >> OOS
        avg_degradation = avg_oos_sharpe / avg_is_sharpe if abs(avg_is_sharpe) > 1e-10 else 0.0

        # Deflated Sharpe Ratio
        # E[max SR] under multiple testing
        from scipy.stats import norm
        gamma = 0.5772  # Euler-Mascheroni constant
        n_trials = max(n_windows, 1)

        if n_trials > 1:
            z_1 = norm.ppf(1 - 1.0 / n_trials)
            z_2 = norm.ppf(1 - 1.0 / (n_trials * np.e))
            expected_max_sr = (1 - gamma) * z_1 + gamma * z_2
        else:
            expected_max_sr = 0.0

        # Variance of Sharpe ratio estimator
        oos_sharpe_std = float(np.std(oos_sharpes)) if len(oos_sharpes) > 1 else 1.0
        var_sr = oos_sharpe_std ** 2 / max(n_windows - 1, 1)

        if var_sr > 0:
            dsr = float(norm.cdf(avg_oos_sharpe, loc=expected_max_sr, scale=np.sqrt(var_sr)))
        else:
            dsr = 0.0

        # Probability of backtest overfitting (PBO)
        # Simplified: fraction of windows where IS > OOS
        is_better_count = sum(1 for w in windows if w.degradation_ratio < 1.0)
        pbo = is_better_count / n_windows if n_windows > 0 else 0.0

        return {
            "avg_is_sharpe": round(avg_is_sharpe, 4),
            "avg_oos_sharpe": round(avg_oos_sharpe, 4),
            "avg_degradation": round(avg_degradation, 4),
            "deflated_sharpe_ratio": round(dsr, 4),
            "probability_of_backtest_overfitting": round(pbo, 4),
            "is_overfit": avg_degradation < 0.5 or dsr < 0.05,
            "overfit_severity": "high" if avg_degradation < 0.3 else ("moderate" if avg_degradation < 0.5 else "low"),
        }

    def _criterion_key(self) -> str:
        """Get the metric key for the optimization criterion."""
        mapping = {
            OptimizationCriterion.SHARPE: "sharpe_ratio",
            OptimizationCriterion.SORTINO: "sortino_ratio",
            OptimizationCriterion.CALMAR: "calmar_ratio",
            OptimizationCriterion.TOTAL_RETURN: "total_return",
            OptimizationCriterion.OMEGA: "omega_ratio",
            OptimizationCriterion.INFORMATION_RATIO: "information_ratio",
        }
        return mapping.get(self.optimization_criterion, "sharpe_ratio")

    def _empty_result(self) -> WFResult:
        """Return empty result when insufficient data."""
        return WFResult(
            method=self.method,
            windows=[],
            aggregate={},
            degradation_stats={},
            significance_tests={},
            overfitting_detection={},
            all_oos_returns=pd.Series(dtype=float),
            all_oos_sharpes=[],
        )

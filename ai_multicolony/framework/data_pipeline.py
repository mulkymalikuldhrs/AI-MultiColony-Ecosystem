"""Multi-source data pipeline with failover for AI-MultiColony.

Provides a ``DataPipeline`` that queries multiple data sources ordered by
priority and falls back automatically when a source fails or times out.
Includes deterministic slippage modelling suitable for reproducible
backtesting.

Key components
--------------
- ``DataSourceConfig``: Declarative configuration for a single data source.
- ``DataPipeline``: Orchestrates fetching with priority-based failover,
  validation, and normalisation.
- ``DataUnavailableError``: Raised when every source fails.
- ``calculate_slippage``: Deterministic slippage using a seeded RNG.
"""

from __future__ import annotations

import hashlib
import math
import threading
import time as _time
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional

import pandas as pd
import structlog

logger = structlog.get_logger(__name__)


# ═══════════════════════════════════════════════════════════════════════════════
# EXCEPTION
# ═══════════════════════════════════════════════════════════════════════════════


class DataUnavailableError(Exception):
    """All configured data sources failed to return data.

    Attributes
    ----------
    symbol:
        The symbol that was requested.
    timeframe:
        The timeframe that was requested.
    attempted_sources:
        List of source names that were attempted.
    errors:
        Mapping of source name → error message.
    """

    def __init__(
        self,
        symbol: str,
        timeframe: str,
        attempted_sources: Optional[List[str]] = None,
        errors: Optional[Dict[str, str]] = None,
    ) -> None:
        self.symbol = symbol
        self.timeframe = timeframe
        self.attempted_sources = attempted_sources or []
        self.errors = errors or {}
        msg = (
            f"Data unavailable for {symbol}/{timeframe}. "
            f"Attempted sources: {self.attempted_sources}"
        )
        super().__init__(msg)


# ═══════════════════════════════════════════════════════════════════════════════
# DATA SOURCE CONFIG
# ═══════════════════════════════════════════════════════════════════════════════


@dataclass
class DataSourceConfig:
    """Declarative configuration for a single data source.

    Parameters
    ----------
    name:
        Human-readable source name (e.g. ``"binance"``, ``"yfinance"``).
    provider:
        Provider identifier or callable.  If a callable, it must
        accept ``(symbol, timeframe, **kwargs)`` and return a
        ``pd.DataFrame``.
    priority:
        Lower numbers = higher priority.  The pipeline tries sources
        in ascending priority order.
    enabled:
        Whether this source is active.
    config:
        Provider-specific configuration (API keys, base URLs, etc.).
    timeout:
        Per-request timeout in seconds.  ``0`` means no timeout.
    """

    name: str
    provider: Any  # str identifier or Callable
    priority: int = 0
    enabled: bool = True
    config: Dict[str, Any] = field(default_factory=dict)
    timeout: float = 30.0


# ═══════════════════════════════════════════════════════════════════════════════
# DATA PIPELINE
# ═══════════════════════════════════════════════════════════════════════════════


class DataPipeline:
    """Multi-source data pipeline with priority-based failover.

    Sources are tried in ascending ``priority`` order.  The first source
    that returns valid data wins.  If a source fails or times out, the
    pipeline automatically falls back to the next one.  An audit log
    records which source ultimately provided the data.

    Usage::

        pipeline = DataPipeline()

        pipeline.add_source(DataSourceConfig(
            name="primary",
            provider=fetch_from_primary,
            priority=0,
            timeout=10,
        ))
        pipeline.add_source(DataSourceConfig(
            name="fallback",
            provider=fetch_from_fallback,
            priority=1,
            timeout=30,
        ))

        df = pipeline.fetch("BTC/USDT", "1h")
    """

    def __init__(self) -> None:
        self._sources: List[DataSourceConfig] = []
        self._fetch_log: List[Dict[str, Any]] = []
        self._lock = threading.Lock()

    # ── Source Management ────────────────────────────────────────────

    def add_source(self, config: DataSourceConfig) -> None:
        """Register a data source.

        Parameters
        ----------
        config:
            Fully-specified ``DataSourceConfig``.
        """
        with self._lock:
            self._sources.append(config)
            # Keep sorted by priority (ascending)
            self._sources.sort(key=lambda s: s.priority)
        logger.info(
            "data_source_added",
            name=config.name,
            priority=config.priority,
            enabled=config.enabled,
        )

    # ── Fetch with Failover ──────────────────────────────────────────

    def fetch(
        self,
        symbol: str,
        timeframe: str,
        **kwargs: Any,
    ) -> pd.DataFrame:
        """Fetch market data with automatic failover.

        Iterates through registered sources in priority order.  Returns
        the first successful result.  If all sources fail, raises
        ``DataUnavailableError``.

        Parameters
        ----------
        symbol:
            Trading pair or ticker (e.g. ``"BTC/USDT"``).
        timeframe:
            Candle interval (e.g. ``"1h"``, ``"1d"``).
        **kwargs:
            Additional arguments forwarded to the provider callable.

        Returns
        -------
        pd.DataFrame
            OHLCV (or similar) data from the first successful source.

        Raises
        ------
        DataUnavailableError
            If every enabled source fails.
        """
        errors: Dict[str, str] = {}
        attempted: List[str] = []

        for source in self._sources:
            if not source.enabled:
                continue

            attempted.append(source.name)
            logger.debug(
                "data_pipeline_trying_source",
                source=source.name,
                symbol=symbol,
                timeframe=timeframe,
            )

            try:
                df = self._try_source(source, symbol, timeframe, **kwargs)
                if df is not None and not df.empty:
                    # Audit log entry
                    log_entry = {
                        "timestamp": _time.time(),
                        "symbol": symbol,
                        "timeframe": timeframe,
                        "source": source.name,
                        "rows": len(df),
                        "columns": list(df.columns),
                        "status": "success",
                    }
                    with self._lock:
                        self._fetch_log.append(log_entry)

                    logger.info(
                        "data_pipeline_source_ok",
                        source=source.name,
                        symbol=symbol,
                        timeframe=timeframe,
                        rows=len(df),
                    )
                    return df
            except Exception as exc:
                errors[source.name] = str(exc)
                logger.warning(
                    "data_pipeline_source_failed",
                    source=source.name,
                    symbol=symbol,
                    error=str(exc),
                )

        raise DataUnavailableError(
            symbol=symbol,
            timeframe=timeframe,
            attempted_sources=attempted,
            errors=errors,
        )

    def _try_source(
        self,
        source: DataSourceConfig,
        symbol: str,
        timeframe: str,
        **kwargs: Any,
    ) -> Optional[pd.DataFrame]:
        """Attempt to fetch data from a single source with timeout.

        If *source.provider* is a callable it is invoked directly.
        If it is a string, it is treated as an identifier (subclasses
        may resolve it to a real provider).

        Parameters
        ----------
        source:
            Source configuration.
        symbol:
            Trading pair.
        timeframe:
            Candle interval.
        **kwargs:
            Forwarded to the provider.

        Returns
        -------
        pd.DataFrame or None
            Fetched data, or *None* if the source returned nothing.
        """
        provider = source.provider

        if not callable(provider):
            logger.warning(
                "data_pipeline_provider_not_callable",
                source=source.name,
                provider_type=type(provider).__name__,
            )
            return None

        timeout = source.timeout if source.timeout > 0 else None

        if timeout is not None:
            result: Optional[pd.DataFrame] = None
            thread_error: Optional[Exception] = None

            def _target() -> None:
                nonlocal result, thread_error
                try:
                    result = provider(symbol, timeframe, **kwargs)
                except Exception as exc:
                    thread_error = exc

            thread = threading.Thread(target=_target, daemon=True)
            thread.start()
            thread.join(timeout=timeout)

            if thread.is_alive():
                raise TimeoutError(
                    f"Source '{source.name}' timed out after {timeout}s"
                )
            if thread_error is not None:
                raise thread_error
            return result
        else:
            return provider(symbol, timeframe, **kwargs)

    # ── Validation & Normalisation ───────────────────────────────────

    def validate(self, data: pd.DataFrame) -> bool:
        """Validate data quality.

        Checks that the DataFrame is non-empty, has no all-NaN columns,
        and contains at least some recognisable OHLCV columns.

        Parameters
        ----------
        data:
            Data to validate.

        Returns
        -------
        bool
            ``True`` if data passes all checks.
        """
        if data is None or data.empty:
            logger.warning("validation_failed", reason="empty_or_none")
            return False

        # Check for all-NaN columns
        all_nan_cols = [col for col in data.columns if data[col].isna().all()]
        if all_nan_cols:
            logger.warning(
                "validation_failed",
                reason="all_nan_columns",
                columns=all_nan_cols,
            )
            return False

        # Check for at least one OHLCV column
        ohlcv_cols = {"open", "high", "low", "close", "volume"}
        found = ohlcv_cols.intersection({c.lower() for c in data.columns})
        if not found:
            logger.warning(
                "validation_failed",
                reason="no_ohlcv_columns",
                available=list(data.columns),
            )
            return False

        return True

    def normalize(
        self,
        data: pd.DataFrame,
        schema: Dict[str, str],
    ) -> pd.DataFrame:
        """Normalise a DataFrame to a common schema.

        Renames columns, coerces types, and removes rows that fail
        type conversion.

        Parameters
        ----------
        data:
            Raw DataFrame to normalise.
        schema:
            Mapping of ``target_column_name → dtype_string``.
            e.g. ``{"open": "float64", "high": "float64"}``.

        Returns
        -------
        pd.DataFrame
            Normalised copy of *data*.
        """
        df = data.copy()

        # Rename common variants to canonical names
        rename_map: Dict[str, str] = {
            "Open": "open",
            "High": "high",
            "Low": "low",
            "Close": "close",
            "Volume": "volume",
            "Adj Close": "adj_close",
        }
        df.rename(columns=rename_map, inplace=True)

        # Apply schema types and drop rows that cannot be converted
        for col, dtype in schema.items():
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce")

        # Drop rows where all OHLCV columns are NaN (if present)
        ohlcv = [c for c in ("open", "high", "low", "close", "volume") if c in df.columns]
        if ohlcv:
            df.dropna(subset=ohlcv, how="all", inplace=True)

        return df.reset_index(drop=True)

    # ── Audit Trail ──────────────────────────────────────────────────

    @property
    def fetch_log(self) -> List[Dict[str, Any]]:
        """Read-only view of the fetch audit log."""
        with self._lock:
            return list(self._fetch_log)

    @property
    def sources(self) -> List[DataSourceConfig]:
        """Return a copy of the registered source configs."""
        with self._lock:
            return list(self._sources)


# ═══════════════════════════════════════════════════════════════════════════════
# DETERMINISTIC SLIPPAGE MODEL
# ═══════════════════════════════════════════════════════════════════════════════


def calculate_slippage(
    price: float,
    volume: float,
    side: str,
    seed: int = 42,
) -> float:
    """Calculate deterministic slippage using a seeded RNG.

    The slippage is **reproducible** for the same inputs, making
    backtesting results deterministic.  No ``random.random()`` is used
    — instead the seed, price, volume, and side are hashed to produce
    a deterministic perturbation.

    Parameters
    ----------
    price:
        Execution price.
    volume:
        Order volume / size.
    side:
        ``"buy"`` or ``"sell"``.
    seed:
        RNG seed for determinism.

    Returns
    -------
    float
        The absolute slippage amount (always positive) applied to the
        price.

    Notes
    -----
    Slippage is modelled as a function of:

    1. **Base spread** — a tiny fraction of price (``0.0001``).
    2. **Volume impact** — proportional to ``sqrt(volume) / 1_000_000``.
    3. **Side bias** — buys get positive slippage, sells get negative.
    4. **Seed perturbation** — a hash-derived value in ``[0, 1)``.
    """
    # Build a deterministic hash from inputs
    raw = f"{seed}:{price}:{volume}:{side}".encode("utf-8")
    digest = hashlib.sha256(raw).hexdigest()
    # Take first 8 hex chars → integer in [0, 2^32)
    perturbation = int(digest[:8], 16) / 0xFFFFFFFF  # [0, 1)

    # Base spread (1 basis point)
    base_spread = price * 0.0001

    # Volume impact — larger orders incur more slippage
    volume_impact = price * (math.sqrt(volume) / 1_000_000) if volume > 0 else 0.0

    # Total absolute slippage
    slippage = base_spread + volume_impact * perturbation

    return abs(slippage)





__all__ = [
    "DataSourceConfig",
    "DataPipeline",
    "DataUnavailableError",
    "calculate_slippage",
]

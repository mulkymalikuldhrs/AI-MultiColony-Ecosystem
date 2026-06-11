"""
Crucix Intelligence Briefing Generator — the core value of Crucix.

This module orchestrates the full intelligence sweep: running all data
sources in parallel, synthesizing results, computing deltas, and
generating structured intelligence briefings.

Port of apis/briefing.mjs + apis/BRIEFING_PROMPT.md + apis/BRIEFING_TEMPLATE.md
to Python with full async support.

Briefing Structure (from BRIEFING_TEMPLATE.md):
    1. Leverageable Ideas — specific, actionable trade ideas
    2. Executive Thesis — the 1-3 most important things happening
    3. Situation Awareness — top 3-5 global developments
    4. Pattern Recognition — cross-source correlations (CORE of Crucix)
    5. Historical Parallels — what does this rhyme with?
    6. Market and Asset Implications — worldview translated to consequences
    7. Decision Board — concise action items
    8. Source Integrity — which sources are strong/weak
"""

from __future__ import annotations

import asyncio
import hashlib
import json
import time
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Optional

import structlog
from pydantic import BaseModel, Field

from .config import CrucixConfig, DeltaThresholdConfig
from .data_sources import BaseSourceAdapter, FetchResult, get_all_source_adapters

logger = structlog.get_logger("crucix.briefing")

# ── Briefing Models ───────────────────────────────────────────────────


class Confidence(str, Enum):
    """Confidence level for ideas and assessments."""

    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


class IdeaType(str, Enum):
    """Type of actionable idea."""

    LONG = "LONG"
    SHORT = "SHORT"
    HEDGE = "HEDGE"
    WATCH = "WATCH"
    AVOID = "AVOID"


class Direction(str, Enum):
    """Overall risk direction of the sweep."""

    RISK_OFF = "risk-off"
    RISK_ON = "risk-on"
    MIXED = "mixed"


class Severity(str, Enum):
    """Severity level for delta signals."""

    CRITICAL = "critical"
    HIGH = "high"
    MODERATE = "moderate"


class BriefingSaveResult(BaseModel):
    """Result of saving a briefing to disk."""

    path: str
    timestamp: str
    size_bytes: int


class LeverageableIdea(BaseModel):
    """A specific, actionable trade idea with full rationale."""

    title: str
    type: IdeaType
    ticker: str = ""
    confidence: Confidence
    rationale: str = ""
    risk: str = ""
    horizon: str = ""  # "Intraday" | "Days" | "Weeks" | "Months"
    signals: list[str] = Field(default_factory=list)
    thesis: str = ""
    why_now: str = ""
    invalidation: str = ""


class SituationEvent(BaseModel):
    """A significant global development."""

    category: str  # "CONFLICT" | "ECONOMIC" | "HEALTH" | "CLIMATE" | "TECHNOLOGY" | "POLICY"
    what_happened: str
    why_it_matters: str = ""
    what_changes: str = ""


class PatternSignal(BaseModel):
    """A cross-source pattern recognition signal."""

    evidence: str
    interpretation: str
    direction: str  # "strengthening" | "stable" | "fading"
    invalidation: str = ""


class HistoricalParallel(BaseModel):
    """A historical analogy for the current situation."""

    analog: str
    what_matches: str
    what_is_different: str = ""
    what_happened_next: str = ""
    current_position: str = ""


class DecisionBoard(BaseModel):
    """Concise action board."""

    best_long: str = ""
    best_hedge: str = ""
    best_watchlist: str = ""
    biggest_question: str = ""
    monitor_24_72h: str = ""


class SourceIntegrity(BaseModel):
    """Assessment of source quality for this briefing."""

    strong_sources: list[str] = Field(default_factory=list)
    weak_sources: list[str] = Field(default_factory=list)
    hard_data_core: list[str] = Field(default_factory=list)
    soft_signal_support: list[str] = Field(default_factory=list)


class DeltaSignal(BaseModel):
    """A single delta signal between sweeps."""

    key: str
    label: str = ""
    from_value: Any = Field(default=None, alias="from")
    to_value: Any = Field(default=None, alias="to")
    pct_change: Optional[float] = None
    direction: str = ""  # "up" | "down" | "resolved"
    severity: Severity = Severity.MODERATE
    reason: str = ""


class DeltaSignals(BaseModel):
    """Collection of delta signals organized by change type."""

    new: list[dict[str, Any]] = Field(default_factory=list)
    escalated: list[dict[str, Any]] = Field(default_factory=list)
    deescalated: list[dict[str, Any]] = Field(default_factory=list)
    unchanged: list[str] = Field(default_factory=list)


class DeltaSummary(BaseModel):
    """Summary of delta between sweeps."""

    total_changes: int = 0
    critical_changes: int = 0
    direction: Direction = Direction.MIXED
    signal_breakdown: dict[str, int] = Field(default_factory=dict)


class DeltaResult(BaseModel):
    """Full delta computation result."""

    timestamp: str = ""
    previous: Optional[str] = None
    signals: DeltaSignals = Field(default_factory=DeltaSignals)
    summary: DeltaSummary = Field(default_factory=DeltaSummary)


class IntelligenceBriefing(BaseModel):
    """Complete intelligence briefing — the core output of Crucix.

    Follows the BRIEFING_TEMPLATE.md structure:
    1. Leverageable Ideas
    2. Executive Thesis
    3. Situation Awareness
    4. Pattern Recognition
    5. Historical Parallels
    6. Market and Asset Implications
    7. Decision Board
    8. Source Integrity
    """

    # Metadata
    version: str = "2.0.0"
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    total_duration_ms: int = 0
    sources_queried: int = 0
    sources_ok: int = 0
    sources_failed: int = 0

    # Core sections
    leverageable_ideas: list[LeverageableIdea] = Field(default_factory=list)
    executive_thesis: str = ""
    situation_awareness: list[SituationEvent] = Field(default_factory=list)
    pattern_recognition: list[PatternSignal] = Field(default_factory=list)
    historical_parallels: list[HistoricalParallel] = Field(default_factory=list)
    market_implications: dict[str, str] = Field(default_factory=dict)
    decision_board: Optional[DecisionBoard] = None
    source_integrity: Optional[SourceIntegrity] = None

    # Raw data references
    raw_sources: dict[str, Any] = Field(default_factory=dict)
    raw_errors: list[dict[str, str]] = Field(default_factory=list)
    timing: dict[str, dict[str, Any]] = Field(default_factory=dict)
    delta: Optional[DeltaResult] = None


# ── Sweep Result ──────────────────────────────────────────────────────


class SweepResult(BaseModel):
    """Result of a full intelligence sweep (before briefing synthesis)."""

    crucix_version: str = "2.0.0"
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    total_duration_ms: int = 0
    sources_queried: int = 0
    sources_ok: int = 0
    sources_failed: int = 0
    sources: dict[str, Any] = Field(default_factory=dict)
    errors: list[dict[str, str]] = Field(default_factory=list)
    timing: dict[str, dict[str, Any]] = Field(default_factory=dict)


# ── Delta Engine ──────────────────────────────────────────────────────

# Default numeric thresholds (same as JS delta/engine.mjs)
DEFAULT_NUMERIC_THRESHOLDS: dict[str, float] = {
    "vix": 5.0,
    "hy_spread": 5.0,
    "10y2y": 10.0,
    "wti": 3.0,
    "brent": 3.0,
    "natgas": 5.0,
    "gold": 2.0,
    "silver": 3.0,
    "unemployment": 2.0,
    "fed_funds": 1.0,
    "10y_yield": 3.0,
    "usd_index": 1.0,
    "mortgage": 2.0,
}

DEFAULT_COUNT_THRESHOLDS: dict[str, int] = {
    "urgent_posts": 2,
    "thermal_total": 500,
    "air_total": 50,
    "who_alerts": 1,
    "conflict_events": 5,
    "conflict_fatalities": 10,
    "sdr_online": 3,
    "news_count": 5,
    "sources_ok": 1,
}

# Risk-sensitive keys for direction determination
RISK_KEYS = {"vix", "hy_spread", "urgent_posts", "conflict_events", "thermal_total"}


def _extract_numeric(data: dict[str, Any], key: str) -> Optional[float]:
    """Extract a numeric metric from synthesized data."""
    if key == "vix":
        for f in data.get("fred", []):
            if f.get("id") == "VIXCLS":
                return f.get("value")
        return None
    if key == "hy_spread":
        for f in data.get("fred", []):
            if f.get("id") == "BAMLH0A0HYM2":
                return f.get("value")
        return None
    if key == "10y2y":
        for f in data.get("fred", []):
            if f.get("id") == "T10Y2Y":
                return f.get("value")
        return None
    if key in ("wti", "brent", "natgas"):
        return data.get("energy", {}).get(key)
    if key in ("gold", "silver"):
        return data.get("metals", {}).get(key)
    if key == "unemployment":
        for b in data.get("bls", []):
            if b.get("id") in ("LNS14000000", "UNRATE"):
                return b.get("value")
        return None
    if key == "fed_funds":
        for f in data.get("fred", []):
            if f.get("id") == "DFF":
                return f.get("value")
        return None
    if key == "10y_yield":
        for f in data.get("fred", []):
            if f.get("id") == "DGS10":
                return f.get("value")
        return None
    if key == "usd_index":
        for f in data.get("fred", []):
            if f.get("id") == "DTWEXBGS":
                return f.get("value")
        return None
    if key == "mortgage":
        for f in data.get("fred", []):
            if f.get("id") == "MORTGAGE30US":
                return f.get("value")
        return None
    return None


def _extract_count(data: dict[str, Any], key: str) -> float:
    """Extract a count metric from synthesized data."""
    if key == "urgent_posts":
        return len(data.get("tg", {}).get("urgent", []))
    if key == "thermal_total":
        return sum(t.get("det", 0) for t in data.get("thermal", []))
    if key == "air_total":
        return sum(a.get("total", 0) for a in data.get("air", []))
    if key == "who_alerts":
        return len(data.get("who", []))
    if key == "conflict_events":
        return data.get("acled", {}).get("totalEvents", 0)
    if key == "conflict_fatalities":
        return data.get("acled", {}).get("totalFatalities", 0)
    if key == "sdr_online":
        return data.get("sdr", {}).get("online", 0)
    if key == "news_count":
        news = data.get("news", [])
        return len(news) if isinstance(news, list) else news.get("count", 0)
    if key == "sources_ok":
        return data.get("meta", {}).get("sourcesOk", 0)
    return 0


# Numeric metric definitions
NUMERIC_METRICS = [
    {"key": "vix", "label": "VIX"},
    {"key": "hy_spread", "label": "HY Spread"},
    {"key": "10y2y", "label": "10Y-2Y Spread"},
    {"key": "wti", "label": "WTI Crude"},
    {"key": "brent", "label": "Brent Crude"},
    {"key": "natgas", "label": "Natural Gas"},
    {"key": "gold", "label": "Gold"},
    {"key": "silver", "label": "Silver"},
    {"key": "unemployment", "label": "Unemployment"},
    {"key": "fed_funds", "label": "Fed Funds Rate"},
    {"key": "10y_yield", "label": "10Y Yield"},
    {"key": "usd_index", "label": "USD Index"},
    {"key": "mortgage", "label": "30Y Mortgage"},
]

COUNT_METRICS = [
    {"key": "urgent_posts", "label": "Urgent OSINT Posts"},
    {"key": "thermal_total", "label": "Thermal Detections"},
    {"key": "air_total", "label": "Air Activity"},
    {"key": "who_alerts", "label": "WHO Alerts"},
    {"key": "conflict_events", "label": "Conflict Events"},
    {"key": "conflict_fatalities", "label": "Conflict Fatalities"},
    {"key": "sdr_online", "label": "SDR Receivers"},
    {"key": "news_count", "label": "News Items"},
    {"key": "sources_ok", "label": "Sources OK"},
]


def compute_delta(
    current: dict[str, Any],
    previous: dict[str, Any] | None,
    num_thresholds: dict[str, float] | None = None,
    cnt_thresholds: dict[str, int] | None = None,
) -> DeltaResult | None:
    """Compute delta between two sweep results.

    Port of lib/delta/engine.mjs computeDelta().

    Args:
        current: Current sweep's synthesized data.
        previous: Previous sweep's synthesized data (None on first run).
        num_thresholds: Override default numeric % change thresholds.
        cnt_thresholds: Override default count change thresholds.

    Returns:
        DeltaResult or None if no previous data available.
    """
    if previous is None or current is None:
        return None

    nt = {**DEFAULT_NUMERIC_THRESHOLDS, **(num_thresholds or {})}
    ct = {**DEFAULT_COUNT_THRESHOLDS, **(cnt_thresholds or {})}

    new_signals: list[dict[str, Any]] = []
    escalated: list[dict[str, Any]] = []
    deescalated: list[dict[str, Any]] = []
    unchanged: list[str] = []
    critical_changes = 0

    # Numeric metrics — track % change
    for m in NUMERIC_METRICS:
        key = m["key"]
        label = m["label"]
        curr_val = _extract_numeric(current, key)
        prev_val = _extract_numeric(previous, key)
        if curr_val is None or prev_val is None:
            continue

        threshold = nt.get(key, 5.0)
        pct_change = ((curr_val - prev_val) / abs(prev_val)) * 100 if prev_val != 0 else 0.0

        if abs(pct_change) > threshold:
            entry = {
                "key": key,
                "label": label,
                "from": prev_val,
                "to": curr_val,
                "pctChange": round(pct_change, 2),
                "direction": "up" if pct_change > 0 else "down",
                "severity": (
                    "critical" if abs(pct_change) > threshold * 3
                    else "high" if abs(pct_change) > threshold * 2
                    else "moderate"
                ),
            }
            if pct_change > 0:
                escalated.append(entry)
            else:
                deescalated.append(entry)
            if abs(pct_change) > 10:
                critical_changes += 1
        else:
            unchanged.append(key)

    # Count metrics — track absolute change
    for m in COUNT_METRICS:
        key = m["key"]
        label = m["label"]
        curr_val = _extract_count(current, key)
        prev_val = _extract_count(previous, key)
        diff = curr_val - prev_val
        threshold = ct.get(key, 1)

        if abs(diff) >= threshold:
            pct_change = (diff / prev_val) * 100 if prev_val > 0 else (100.0 if diff > 0 else 0.0)
            entry = {
                "key": key,
                "label": label,
                "from": prev_val,
                "to": curr_val,
                "change": diff,
                "direction": "up" if diff > 0 else "down",
                "pctChange": round(pct_change, 1),
                "severity": (
                    "critical" if abs(diff) >= threshold * 5
                    else "high" if abs(diff) >= threshold * 2
                    else "moderate"
                ),
            }
            if diff > 0:
                escalated.append(entry)
            else:
                deescalated.append(entry)
            if entry["severity"] == "critical":
                critical_changes += 1
        else:
            unchanged.append(key)

    # Nuclear anomaly state change
    curr_anom = any(n.get("anom") for n in current.get("nuke", []))
    prev_anom = any(n.get("anom") for n in previous.get("nuke", []))
    if curr_anom and not prev_anom:
        new_signals.append({"key": "nuke_anomaly", "reason": "Nuclear anomaly detected", "severity": "critical"})
        critical_changes += 5
    elif not curr_anom and prev_anom:
        deescalated.append({"key": "nuke_anomaly", "label": "Nuclear Anomaly", "direction": "resolved", "severity": "high"})

    # Source health degradation
    curr_down = sum(1 for s in current.get("health", []) if s.get("err"))
    prev_down = sum(1 for s in previous.get("health", []) if s.get("err"))
    if curr_down > prev_down + 2:
        new_signals.append({
            "key": "source_degradation",
            "reason": f"{curr_down - prev_down} additional sources failing ({curr_down} total down)",
            "severity": "critical" if curr_down > 5 else "moderate",
        })

    # Overall direction
    risk_up = sum(1 for s in escalated if s.get("key") in RISK_KEYS)
    risk_down = sum(1 for s in deescalated if s.get("key") in RISK_KEYS)
    if risk_up > risk_down + 1:
        direction = Direction.RISK_OFF
    elif risk_down > risk_up + 1:
        direction = Direction.RISK_ON
    else:
        direction = Direction.MIXED

    total_changes = len(new_signals) + len(escalated) + len(deescalated)

    return DeltaResult(
        timestamp=current.get("meta", {}).get("timestamp", datetime.now(timezone.utc).isoformat()),
        previous=previous.get("meta", {}).get("timestamp"),
        signals=DeltaSignals(
            new=new_signals,
            escalated=escalated,
            deescalated=deescalated,
            unchanged=unchanged,
        ),
        summary=DeltaSummary(
            total_changes=total_changes,
            critical_changes=critical_changes,
            direction=direction,
            signal_breakdown={
                "new": len(new_signals),
                "escalated": len(escalated),
                "deescalated": len(deescalated),
                "unchanged": len(unchanged),
            },
        ),
    )


# ── Briefing Generator ────────────────────────────────────────────────


class BriefingGenerator:
    """Orchestrates full intelligence sweeps and briefing generation.

    This is the core class of the Crucix Python port. It:
    1. Runs all data sources in parallel with per-source timeouts
    2. Collects results into a structured SweepResult
    3. Computes deltas against previous sweeps
    4. Generates structured IntelligenceBriefing

    Usage:
        generator = BriefingGenerator(config)
        result = await generator.run_full_sweep()
        briefing = generator.synthesize_briefing(result)
    """

    def __init__(
        self,
        config: CrucixConfig | None = None,
        source_adapters: list[BaseSourceAdapter] | None = None,
        api_keys: dict[str, str] | None = None,
    ) -> None:
        self.config = config or CrucixConfig()
        self._api_keys = api_keys or {}
        self._adapters = source_adapters or get_all_source_adapters(self._api_keys)
        self._previous_data: dict[str, Any] | None = None
        self._log = structlog.get_logger("crucix.briefing.generator")

    async def _run_source(self, adapter: BaseSourceAdapter) -> FetchResult:
        """Run a single source adapter with timeout.

        Port of briefing.mjs runSource().
        """
        start = time.monotonic()
        try:
            result = await asyncio.wait_for(
                adapter.fetch_briefing(),
                timeout=self.config.source_timeout_seconds,
            )
            elapsed = int((time.monotonic() - start) * 1000)
            return FetchResult(
                source=adapter.metadata.name,
                status="ok",
                duration_ms=elapsed,
                data=result.model_dump(),
            )
        except asyncio.TimeoutError:
            elapsed = int((time.monotonic() - start) * 1000)
            return FetchResult(
                source=adapter.metadata.name,
                status="timeout",
                duration_ms=elapsed,
                error=f"Timed out after {self.config.source_timeout_seconds}s",
            )
        except Exception as exc:
            elapsed = int((time.monotonic() - start) * 1000)
            return FetchResult(
                source=adapter.metadata.name,
                status="error",
                duration_ms=elapsed,
                error=str(exc),
            )

    async def run_full_sweep(self) -> SweepResult:
        """Run all data sources in parallel and collect results.

        Port of briefing.mjs fullBriefing().
        """
        self._log.info("sweep_starting", source_count=len(self._adapters))
        start = time.monotonic()

        # Run all sources concurrently
        tasks = [self._run_source(adapter) for adapter in self._adapters]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Process results
        sources_ok = 0
        sources_failed = 0
        source_data: dict[str, Any] = {}
        errors: list[dict[str, str]] = []
        timing: dict[str, dict[str, Any]] = {}

        for result in results:
            if isinstance(result, Exception):
                sources_failed += 1
                errors.append({"error": str(result)})
                continue

            if isinstance(result, FetchResult):
                timing[result.source] = {"status": result.status, "ms": result.duration_ms}
                if result.status == "ok":
                    sources_ok += 1
                    if result.data:
                        source_data[result.source] = result.data.get("data", result.data)
                else:
                    sources_failed += 1
                    errors.append({"name": result.source, "error": result.error or "Unknown error"})

        total_ms = int((time.monotonic() - start) * 1000)

        self._log.info(
            "sweep_complete",
            total_ms=total_ms,
            sources_ok=sources_ok,
            sources_failed=sources_failed,
        )

        return SweepResult(
            total_duration_ms=total_ms,
            sources_queried=len(self._adapters),
            sources_ok=sources_ok,
            sources_failed=sources_failed,
            sources=source_data,
            errors=errors,
            timing=timing,
        )

    def compute_sweep_delta(self, current: SweepResult) -> DeltaResult | None:
        """Compute delta between current sweep and previous.

        Uses the delta engine to compare synthesized data.
        """
        current_data = self._synthesize_for_delta(current)
        previous_data = self._previous_data
        self._previous_data = current_data

        if previous_data is None:
            return None

        # Convert DeltaThresholdConfig to plain dicts
        dt = self.config.delta_thresholds
        num_thresholds = {
            "vix": dt.vix, "hy_spread": dt.hy_spread, "10y2y": dt.yield_10y2y,
            "wti": dt.wti, "brent": dt.brent, "natgas": dt.natgas,
            "gold": dt.gold, "silver": dt.silver, "unemployment": dt.unemployment,
            "fed_funds": dt.fed_funds, "10y_yield": dt.yield_10y,
            "usd_index": dt.usd_index, "mortgage": dt.mortgage,
        }
        cnt_thresholds = {
            "urgent_posts": dt.urgent_posts, "thermal_total": dt.thermal_total,
            "air_total": dt.air_total, "who_alerts": dt.who_alerts,
            "conflict_events": dt.conflict_events, "conflict_fatalities": dt.conflict_fatalities,
            "sdr_online": dt.sdr_online, "news_count": dt.news_count,
            "sources_ok": dt.sources_ok,
        }

        return compute_delta(current_data, previous_data, num_thresholds, cnt_thresholds)

    def _synthesize_for_delta(self, result: SweepResult) -> dict[str, Any]:
        """Convert a SweepResult into the synthesized format expected by the delta engine."""
        sources = result.sources

        # Extract FRED indicators
        fred = []
        fred_data = sources.get("FRED", {})
        if isinstance(fred_data, dict) and "indicators" in fred_data:
            fred = fred_data["indicators"]

        # Extract energy data
        energy = {}
        for src in ["FRED", "YFinance"]:
            src_data = sources.get(src, {})
            if isinstance(src_data, dict):
                if "wti" in src_data or "energy" in src_data:
                    energy = src_data.get("energy", src_data)
                    break

        # Extract metals
        metals = {}
        metals_data = sources.get("YFinance", {})
        if isinstance(metals_data, dict) and "metals" in metals_data:
            metals = metals_data["metals"]

        # Extract BLS
        bls = sources.get("BLS", {}).get("indicators", []) if isinstance(sources.get("BLS"), dict) else []

        # Extract ACLED
        acled = sources.get("ACLED", {}) if isinstance(sources.get("ACLED"), dict) else {}

        # Extract WHO
        who = sources.get("WHO", []) if isinstance(sources.get("WHO"), list) else []

        # Extract OSINT (GDELT articles as proxy for urgent posts)
        gdelt_data = sources.get("GDELT", {})
        urgent = []
        if isinstance(gdelt_data, dict) and "articles" in gdelt_data:
            # Treat high-volume articles as urgent OSINT
            for a in gdelt_data.get("articles", [])[:10]:
                urgent.append({"text": a.get("title", ""), "date": a.get("date", "")})

        return {
            "meta": {
                "timestamp": result.timestamp,
                "sourcesOk": result.sources_ok,
                "sourcesQueried": result.sources_queried,
            },
            "fred": fred,
            "energy": energy,
            "metals": metals,
            "bls": bls,
            "acled": acled,
            "who": who,
            "tg": {"urgent": urgent, "posts": len(urgent)},
            "thermal": [],
            "air": [],
            "nuke": [],
            "sdr": {},
            "health": [],
            "news": gdelt_data.get("articles", []) if isinstance(gdelt_data, dict) else [],
        }

    def synthesize_briefing(self, sweep_result: SweepResult, delta: DeltaResult | None = None) -> IntelligenceBriefing:
        """Synthesize a full intelligence briefing from sweep data.

        This is the main output method. It takes raw sweep data and
        produces the structured IntelligenceBriefing following the
        BRIEFING_TEMPLATE.md format.

        Note: For LLM-powered idea generation, use generate_llm_ideas()
        separately and set the results on the briefing.
        """
        # Source integrity
        strong_sources = []
        weak_sources = []
        hard_data_core = []
        soft_signal_support = []

        for name, timing_info in sweep_result.timing.items():
            if timing_info.get("status") == "ok":
                strong_sources.append(name)
                if name in ("FRED", "BLS", "Treasury", "EIA", "GSCPI", "ACLED"):
                    hard_data_core.append(name)
                elif name in ("GDELT", "Reddit", "Telegram", "Bluesky"):
                    soft_signal_support.append(name)
            else:
                weak_sources.append(name)

        # Pattern recognition — cross-correlate signals from source data
        patterns = self._detect_patterns(sweep_result)

        # Situation awareness — extract key events
        events = self._extract_situation_events(sweep_result)

        # Executive thesis
        thesis = self._formulate_executive_thesis(sweep_result, delta, patterns)

        # Market implications
        market = self._infer_market_implications(sweep_result, delta)

        # Decision board
        decision = self._formulate_decision_board(sweep_result, delta, patterns)

        briefing = IntelligenceBriefing(
            total_duration_ms=sweep_result.total_duration_ms,
            sources_queried=sweep_result.sources_queried,
            sources_ok=sweep_result.sources_ok,
            sources_failed=sweep_result.sources_failed,
            executive_thesis=thesis,
            situation_awareness=events,
            pattern_recognition=patterns,
            market_implications=market,
            decision_board=decision,
            source_integrity=SourceIntegrity(
                strong_sources=strong_sources,
                weak_sources=weak_sources,
                hard_data_core=hard_data_core,
                soft_signal_support=soft_signal_support,
            ),
            raw_sources=sweep_result.sources,
            raw_errors=sweep_result.errors,
            timing=sweep_result.timing,
            delta=delta,
        )

        return briefing

    def _detect_patterns(self, result: SweepResult) -> list[PatternSignal]:
        """Cross-correlate signals across sources to detect non-obvious patterns.

        This is the CORE of Crucix — the pattern recognition engine.
        """
        patterns = []

        # Check for conflict + energy + inflation pattern
        has_conflict = "ACLED" in result.sources and result.sources.get("ACLED", {}).get("totalEvents", 0) > 20
        has_energy_stress = False
        fred_data = result.sources.get("FRED", {})
        if isinstance(fred_data, dict):
            for ind in fred_data.get("indicators", []):
                if ind.get("id") == "DCOILWTICO" and ind.get("value", 0) > 80:
                    has_energy_stress = True

        if has_conflict and has_energy_stress:
            patterns.append(PatternSignal(
                evidence="Conflict escalation + elevated oil prices detected across ACLED and FRED",
                interpretation="Geopolitical risk premium in energy markets; inflation pressure likely",
                direction="strengthening",
                invalidation="De-escalation or oil supply increase",
            ))

        # Check for VIX + credit stress pattern
        has_vix_stress = False
        has_credit_stress = False
        if isinstance(fred_data, dict):
            for ind in fred_data.get("indicators", []):
                if ind.get("id") == "VIXCLS" and (ind.get("value") or 0) > 25:
                    has_vix_stress = True
                if ind.get("id") == "BAMLH0A0HYM2" and (ind.get("value") or 0) > 4:
                    has_credit_stress = True

        if has_vix_stress and has_credit_stress:
            patterns.append(PatternSignal(
                evidence="VIX elevated + HY spreads widening — dual fear signal",
                interpretation="Market stress building across equity and credit; risk-off rotation likely",
                direction="strengthening",
                invalidation="Central bank intervention or positive macro surprise",
            ))

        # Check for OSINT surge pattern
        gdelt_data = result.sources.get("GDELT", {})
        if isinstance(gdelt_data, dict):
            article_count = gdelt_data.get("totalArticles", 0)
            if article_count > 30:
                patterns.append(PatternSignal(
                    evidence=f"GDELT reporting high volume: {article_count} articles in 24h",
                    interpretation="Elevated newsflow suggests breaking developments requiring attention",
                    direction="strengthening",
                    invalidation="Volume normalizes below 20 articles/day",
                ))

        return patterns

    def _extract_situation_events(self, result: SweepResult) -> list[SituationEvent]:
        """Extract top 3-5 significant events from source data."""
        events = []

        # From GDELT articles
        gdelt_data = result.sources.get("GDELT", {})
        if isinstance(gdelt_data, dict):
            for article in gdelt_data.get("articles", [])[:3]:
                title = article.get("title", "")
                if title:
                    # Simple categorization
                    category = "POLICY"
                    title_lower = title.lower()
                    if any(w in title_lower for w in ["military", "war", "strike", "attack", "missile"]):
                        category = "CONFLICT"
                    elif any(w in title_lower for w in ["economy", "market", "inflation", "recession"]):
                        category = "ECONOMIC"
                    elif any(w in title_lower for w in ["pandemic", "outbreak", "disease", "virus"]):
                        category = "HEALTH"
                    elif any(w in title_lower for w in ["climate", "fire", "flood", "earthquake"]):
                        category = "CLIMATE"
                    elif any(w in title_lower for w in ["ai", "tech", "cyber", "software"]):
                        category = "TECHNOLOGY"

                    events.append(SituationEvent(
                        category=category,
                        what_happened=title,
                        why_it_matters="Cross-referenced from GDELT global monitoring",
                        what_changes="Monitor for escalation or confirmation from other sources",
                    ))

        # From CISA-KEV
        cisa_data = result.sources.get("CISA-KEV", {})
        if isinstance(cisa_data, dict) and cisa_data.get("recentCount", 0) > 5:
            events.append(SituationEvent(
                category="TECHNOLOGY",
                what_happened=f"{cisa_data['recentCount']} recently added known exploited vulnerabilities",
                why_it_matters="Active exploitation in the wild — potential infrastructure risk",
                what_changes="Patch and mitigate critical vulnerabilities immediately",
            ))

        return events[:5]

    def _formulate_executive_thesis(
        self,
        result: SweepResult,
        delta: DeltaResult | None,
        patterns: list[PatternSignal],
    ) -> str:
        """Formulate the executive thesis — the 1-3 most important things happening."""
        parts = []

        if delta and delta.summary.direction == Direction.RISK_OFF:
            parts.append("Risk-off regime forming: multiple stress signals escalating.")
        elif delta and delta.summary.direction == Direction.RISK_ON:
            parts.append("Risk-on conditions: de-escalation signals outweigh stress indicators.")
        else:
            parts.append("Mixed signals: no clear directional regime emerging.")

        if patterns:
            strongest = patterns[0]
            parts.append(f"Key pattern: {strongest.interpretation}")

        if result.sources_failed > 3:
            parts.append(f"Data quality concern: {result.sources_failed} sources failed.")

        return " ".join(parts) if parts else "Insufficient data for executive thesis."

    def _infer_market_implications(
        self,
        result: SweepResult,
        delta: DeltaResult | None,
    ) -> dict[str, str]:
        """Infer market implications from source data and delta."""
        implications: dict[str, str] = {}

        # Default neutral
        implications["equities"] = "Neutral — no strong directional signal"
        implications["bonds"] = "Neutral — monitor yield curve signals"
        implications["commodities"] = "Neutral — watch energy and metals"
        implications["crypto"] = "Neutral — follow risk sentiment"

        # Upgrade based on signals
        fred_data = result.sources.get("FRED", {})
        if isinstance(fred_data, dict):
            for ind in fred_data.get("indicators", []):
                if ind.get("id") == "VIXCLS" and (ind.get("value") or 0) > 30:
                    implications["equities"] = "Bearish — VIX elevated, expect volatility"
                    implications["bonds"] = "Bullish — flight to quality"
                if ind.get("id") == "DCOILWTICO" and (ind.get("value") or 0) > 90:
                    implications["commodities"] = "Bullish energy — oil above $90"

        if delta and delta.summary.direction == Direction.RISK_OFF:
            implications["crypto"] = "Bearish — risk-off typically pressures crypto"
            implications["equities"] = "Bearish bias — risk-off regime"

        return implications

    def _formulate_decision_board(
        self,
        result: SweepResult,
        delta: DeltaResult | None,
        patterns: list[PatternSignal],
    ) -> DecisionBoard:
        """Formulate the decision board with actionable items."""
        best_long = "Monitor broad market ETFs for risk-on confirmation"
        best_hedge = "Gold or VIX calls as portfolio protection"
        best_watch = "Yield curve and credit spreads for regime change"
        biggest_q = "Are current stress signals transient or structural?"
        monitor = "Key economic data releases and geopolitical developments"

        if delta and delta.summary.direction == Direction.RISK_OFF:
            best_hedge = "Long VIX / short equity exposure — risk-off signals active"
            best_watch = "Credit spreads and high-yield for stress acceleration"
            biggest_q = "Is this a temporary risk-off or start of a broader de-risking?"
            monitor = "Central bank communications and liquidity conditions"
        elif delta and delta.summary.direction == Direction.RISK_ON:
            best_long = "Equity index exposure on risk-on confirmation"
            biggest_q = "Is the risk-on move supported by fundamentals or just sentiment?"

        return DecisionBoard(
            best_long=best_long,
            best_hedge=best_hedge,
            best_watchlist=best_watch,
            biggest_question=biggest_q,
            monitor_24_72h=monitor,
        )

    # ── Save Briefing ──────────────────────────────────────────────

    def save_briefing(
        self,
        sweep_result: SweepResult,
        output_dir: str | Path = "runs",
    ) -> BriefingSaveResult:
        """Save raw sweep data to disk.

        Port of apis/save-briefing.mjs.
        """
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H-%M-%SZ")
        filename = f"briefing_{timestamp}.json"
        filepath = output_path / filename

        data = sweep_result.model_dump_json(indent=2)
        filepath.write_text(data, encoding="utf-8")

        # Also write latest.json
        latest_path = output_path / "latest.json"
        latest_path.write_text(data, encoding="utf-8")

        self._log.info("briefing_saved", path=str(filepath), size=len(data))

        return BriefingSaveResult(
            path=str(filepath),
            timestamp=timestamp,
            size_bytes=len(data.encode("utf-8")),
        )

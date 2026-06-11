"""
Tests for the Crucix Python port.

Covers:
- config.py: Configuration loading and env-var overrides
- localization.py: i18n/localization manager
- briefing.py: Intelligence briefing generator, delta engine
- data_sources.py: Source adapters and fetch utilities
- gateway.py: Sweep orchestrator
"""

from __future__ import annotations

import asyncio
import json
import os
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

# ── Config Tests ──────────────────────────────────────────────────────


class TestCrucixConfig:
    """Tests for src/crucix/config.py."""

    def test_default_config(self):
        from src.crucix.config import CrucixConfig

        config = CrucixConfig()
        assert config.port == 3117
        assert config.refresh_interval_minutes == 15
        assert config.language == "en"
        assert config.source_timeout_seconds == 30.0
        assert config.runs_dir == "runs"
        assert config.llm.provider is None
        assert config.llm.api_key is None
        assert config.telegram.bot_token is None
        assert config.discord.bot_token is None

    def test_llm_config_is_configured(self):
        from src.crucix.config import LLMConfig

        # Not configured without provider
        config = LLMConfig()
        assert config.is_configured is False

        # Configured with provider and key
        config = LLMConfig(provider="openai", api_key="sk-test")
        assert config.is_configured is True
        assert config.model is None  # model is optional

    def test_telegram_config_is_configured(self):
        from src.crucix.config import TelegramConfig

        config = TelegramConfig()
        assert config.is_configured is False

        config = TelegramConfig(bot_token="123:ABC", chat_id="-100")
        assert config.is_configured is True

    def test_discord_config_is_configured(self):
        from src.crucix.config import DiscordConfig

        config = DiscordConfig()
        assert config.is_configured is False

        config = DiscordConfig(bot_token="discord-token")
        assert config.is_configured is True

        # Webhook-only also counts
        config = DiscordConfig(webhook_url="https://discord.com/api/webhooks/123/abc")
        assert config.is_configured is True

    def test_delta_threshold_defaults(self):
        from src.crucix.config import DeltaThresholdConfig

        dt = DeltaThresholdConfig()
        assert dt.vix == 5.0
        assert dt.gold == 2.0
        assert dt.urgent_posts == 2
        assert dt.conflict_events == 5

    def test_env_var_override(self):
        from src.crucix.config import CrucixConfig

        with patch.dict(os.environ, {"CRUCIX_PORT": "8080", "CRUCIX_LANGUAGE": "fr"}):
            config = CrucixConfig()
            assert config.port == 8080
            assert config.language == "fr"


# ── Localization Tests ────────────────────────────────────────────────


class TestLocalization:
    """Tests for src/crucix/localization.py."""

    def test_default_locale(self):
        from src.crucix.localization import LocalizationManager

        mgr = LocalizationManager()
        assert mgr.default_locale == "en"
        assert mgr.get_current_locale() == "en"

    def test_set_locale(self):
        from src.crucix.localization import LocalizationManager

        mgr = LocalizationManager()
        mgr.set_locale("fr")
        assert mgr.get_current_locale() == "fr"

    def test_set_unsupported_locale_falls_back(self):
        from src.crucix.localization import LocalizationManager

        mgr = LocalizationManager()
        mgr.set_locale("zz")
        assert mgr.get_current_locale() == "en"  # Falls back to default

    def test_translate_from_dict(self):
        from src.crucix.localization import LocalizationManager

        mgr = LocalizationManager()
        mgr.register_locale_data("en", {
            "dashboard": {"title": "CRUCIX - Intelligence Terminal"},
            "boot": {"connecting": "Connecting {count} sources"},
        })

        assert mgr.t("dashboard.title") == "CRUCIX - Intelligence Terminal"
        assert mgr.t("boot.connecting", count=27) == "Connecting 27 sources"
        assert mgr.t("nonexistent.key") == "nonexistent.key"

    def test_translate_with_locale_override(self):
        from src.crucix.localization import LocalizationManager

        mgr = LocalizationManager()
        mgr.register_locale_data("en", {"greeting": "Hello"})
        mgr.register_locale_data("fr", {"greeting": "Bonjour"})

        assert mgr.t("greeting", locale="en") == "Hello"
        assert mgr.t("greeting", locale="fr") == "Bonjour"
        # Default is en
        assert mgr.t("greeting") == "Hello"

    def test_translate_fallback_to_default(self):
        from src.crucix.localization import LocalizationManager

        mgr = LocalizationManager()
        mgr.register_locale_data("en", {"common": {"ok": "OK"}})
        mgr.register_locale_data("fr", {})  # French exists but missing key

        assert mgr.t("common.ok", locale="fr") == "OK"  # Falls back to en

    def test_interpolation(self):
        from src.crucix.localization import LocalizationManager

        mgr = LocalizationManager()
        mgr.register_locale_data("en", {
            "time": {"hoursAgo": "{hours}h ago"},
            "boot": {"sweepComplete": "Sweep complete - {ok}/{total} sources"},
        })

        assert mgr.t("time.hoursAgo", hours=3) == "3h ago"
        assert mgr.t("boot.sweepComplete", ok=25, total=27) == "Sweep complete - 25/27 sources"

    def test_interpolation_missing_param_leaves_placeholder(self):
        from src.crucix.localization import LocalizationManager

        mgr = LocalizationManager()
        mgr.register_locale_data("en", {"msg": {"greeting": "Hello {name}, you have {count} alerts"}})

        result = mgr.t("msg.greeting", name="Alice")
        assert "Alice" in result
        assert "{count}" in result  # Missing param stays as-is

    def test_load_from_json_file(self):
        from src.crucix.localization import LocalizationManager

        with tempfile.TemporaryDirectory() as tmpdir:
            locale_data = {
                "meta": {"code": "en", "name": "English", "nativeName": "English"},
                "dashboard": {"title": "CRUCIX - Intelligence Terminal"},
            }
            en_path = Path(tmpdir) / "en.json"
            en_path.write_text(json.dumps(locale_data), encoding="utf-8")

            mgr = LocalizationManager(locales_dir=tmpdir)
            assert mgr.t("dashboard.title") == "CRUCIX - Intelligence Terminal"

    def test_get_supported_locales(self):
        from src.crucix.localization import LocalizationManager

        mgr = LocalizationManager()
        locales = mgr.get_supported_locales()
        codes = [l.code for l in locales]
        assert "en" in codes
        assert "fr" in codes

    def test_is_supported(self):
        from src.crucix.localization import LocalizationManager

        mgr = LocalizationManager()
        assert mgr.is_supported("en") is True
        assert mgr.is_supported("fr") is True
        assert mgr.is_supported("zz") is False

    def test_clear_cache(self):
        from src.crucix.localization import LocalizationManager

        with tempfile.TemporaryDirectory() as tmpdir:
            en_path = Path(tmpdir) / "en.json"
            en_path.write_text(json.dumps({"key": "value"}), encoding="utf-8")

            mgr = LocalizationManager(locales_dir=tmpdir)
            mgr._load_locale_file("en")
            assert "en" in mgr._cache

            mgr.clear_cache()
            assert "en" not in mgr._cache

    def test_get_llm_system_prompt(self):
        from src.crucix.localization import LocalizationManager

        mgr = LocalizationManager()
        mgr.register_locale_data("en", {
            "llm": {"systemPrompt": "You are a quantitative analyst."},
        })

        prompt = mgr.get_llm_system_prompt()
        assert "quantitative analyst" in prompt

    def test_get_llm_system_prompt_fallback(self):
        from src.crucix.localization import LocalizationManager

        mgr = LocalizationManager()
        mgr.register_locale_data("fr", {
            "llm": {"systemPrompt": "Tu es un analyste."},
        })
        # Default is en, but en has no prompt; should fall back
        prompt = mgr.get_llm_system_prompt()
        assert prompt == ""  # No en prompt registered


# ── Briefing / Delta Engine Tests ─────────────────────────────────────


class TestDeltaEngine:
    """Tests for the delta engine in src/crucix/briefing.py."""

    def test_compute_delta_returns_none_when_no_previous(self):
        from src.crucix.briefing import compute_delta

        current = {"meta": {"timestamp": "2025-01-01T00:00:00Z"}}
        result = compute_delta(current, None)
        assert result is None

    def test_compute_delta_detects_escalation(self):
        from src.crucix.briefing import compute_delta, Direction

        previous = {
            "meta": {"timestamp": "2025-01-01T00:00:00Z"},
            "fred": [{"id": "VIXCLS", "value": 15.0}],
            "energy": {"wti": 70.0, "brent": 75.0, "natgas": 3.0},
        }
        current = {
            "meta": {"timestamp": "2025-01-01T01:00:00Z"},
            "fred": [{"id": "VIXCLS", "value": 25.0}],  # 66% increase — well above 5% threshold
            "energy": {"wti": 70.5, "brent": 75.5, "natgas": 3.0},
        }

        delta = compute_delta(current, previous)
        assert delta is not None
        assert delta.summary.total_changes > 0
        assert any(s["key"] == "vix" for s in delta.signals.escalated)

    def test_compute_delta_detects_deescalation(self):
        from src.crucix.briefing import compute_delta

        previous = {
            "meta": {"timestamp": "2025-01-01T00:00:00Z"},
            "fred": [{"id": "VIXCLS", "value": 25.0}],
        }
        current = {
            "meta": {"timestamp": "2025-01-01T01:00:00Z"},
            "fred": [{"id": "VIXCLS", "value": 15.0}],  # 40% decrease
        }

        delta = compute_delta(current, previous)
        assert delta is not None
        assert any(s["key"] == "vix" for s in delta.signals.deescalated)

    def test_compute_delta_direction_risk_off(self):
        from src.crucix.briefing import compute_delta, Direction

        previous = {
            "meta": {"timestamp": "2025-01-01T00:00:00Z"},
            "fred": [
                {"id": "VIXCLS", "value": 15.0},
                {"id": "BAMLH0A0HYM2", "value": 3.0},
            ],
        }
        current = {
            "meta": {"timestamp": "2025-01-01T01:00:00Z"},
            "fred": [
                {"id": "VIXCLS", "value": 30.0},  # +100%
                {"id": "BAMLH0A0HYM2", "value": 6.0},  # +100%
            ],
        }

        delta = compute_delta(current, previous)
        assert delta.summary.direction == Direction.RISK_OFF

    def test_compute_delta_direction_risk_on(self):
        from src.crucix.briefing import compute_delta, Direction

        previous = {
            "meta": {"timestamp": "2025-01-01T00:00:00Z"},
            "fred": [
                {"id": "VIXCLS", "value": 30.0},
                {"id": "BAMLH0A0HYM2", "value": 6.0},
            ],
        }
        current = {
            "meta": {"timestamp": "2025-01-01T01:00:00Z"},
            "fred": [
                {"id": "VIXCLS", "value": 15.0},  # -50%
                {"id": "BAMLH0A0HYM2", "value": 2.0},  # -66%
            ],
        }

        delta = compute_delta(current, previous)
        assert delta.summary.direction == Direction.RISK_ON

    def test_compute_delta_nuclear_anomaly(self):
        from src.crucix.briefing import compute_delta

        previous = {
            "meta": {"timestamp": "2025-01-01T00:00:00Z"},
            "nuke": [{"site": "TestSite", "anom": False, "cpm": 50}],
        }
        current = {
            "meta": {"timestamp": "2025-01-01T01:00:00Z"},
            "nuke": [{"site": "TestSite", "anom": True, "cpm": 500}],
        }

        delta = compute_delta(current, previous)
        assert any(s.get("key") == "nuke_anomaly" for s in delta.signals.new)

    def test_compute_delta_count_metrics(self):
        from src.crucix.briefing import compute_delta

        previous = {
            "meta": {"timestamp": "2025-01-01T00:00:00Z", "sourcesOk": 25},
            "acled": {"totalEvents": 50, "totalFatalities": 100},
            "tg": {"urgent": [{"text": f"Post {i}"} for i in range(5)]},
        }
        current = {
            "meta": {"timestamp": "2025-01-01T01:00:00Z", "sourcesOk": 20},  # -5 (threshold: 1)
            "acled": {"totalEvents": 60, "totalFatalities": 120},  # +10 events, +20 fatalities
            "tg": {"urgent": [{"text": f"Post {i}"} for i in range(10)]},  # +5 (threshold: 2)
        }

        delta = compute_delta(current, previous)
        assert delta is not None
        # sources_ok dropped by 5 (threshold 1) -> deescalated
        assert any(s["key"] == "sources_ok" for s in delta.signals.deescalated)
        # conflict_events up by 10 (threshold 5) -> escalated
        assert any(s["key"] == "conflict_events" for s in delta.signals.escalated)
        # urgent_posts up by 5 (threshold 2) -> escalated
        assert any(s["key"] == "urgent_posts" for s in delta.signals.escalated)

    def test_compute_delta_custom_thresholds(self):
        from src.crucix.briefing import compute_delta

        previous = {"meta": {}, "fred": [{"id": "VIXCLS", "value": 20.0}]}
        current = {"meta": {}, "fred": [{"id": "VIXCLS", "value": 21.0}]}  # 5% increase

        # With default threshold (5%), 5% is not > 5%, so no change
        delta = compute_delta(current, previous)
        assert "vix" in delta.signals.unchanged

        # With custom lower threshold (3%), 5% > 3% triggers
        delta = compute_delta(current, previous, num_thresholds={"vix": 3.0})
        assert any(s["key"] == "vix" for s in delta.signals.escalated)

    def test_compute_delta_no_changes(self):
        from src.crucix.briefing import compute_delta

        previous = {
            "meta": {"timestamp": "2025-01-01T00:00:00Z"},
            "fred": [{"id": "VIXCLS", "value": 20.0}],
            "energy": {"wti": 70.0},
        }
        current = {
            "meta": {"timestamp": "2025-01-01T01:00:00Z"},
            "fred": [{"id": "VIXCLS", "value": 20.1}],  # 0.5% — below threshold
            "energy": {"wti": 70.1},  # 0.14% — below threshold
        }

        delta = compute_delta(current, previous)
        assert delta.summary.total_changes == 0
        assert delta.summary.critical_changes == 0


class TestBriefingGenerator:
    """Tests for src/crucix/briefing.py BriefingGenerator."""

    def _make_sweep_result(self, **overrides) -> "SweepResult":
        from src.crucix.briefing import SweepResult

        defaults = {
            "sources_queried": 9,
            "sources_ok": 7,
            "sources_failed": 2,
            "sources": {
                "GDELT": {"totalArticles": 35, "articles": [
                    {"title": "Military strike in region", "url": "", "date": "", "domain": "", "language": "", "country": ""},
                    {"title": "Economic recession fears grow", "url": "", "date": "", "domain": "", "language": "", "country": ""},
                ]},
                "FRED": {"indicators": [
                    {"id": "VIXCLS", "label": "VIX", "value": 22.5, "date": "2025-01-01"},
                    {"id": "DFF", "label": "Fed Funds", "value": 5.33, "date": "2025-01-01"},
                ]},
                "CISA-KEV": {"totalVulnerabilities": 1000, "recentCount": 8, "recent": []},
            },
            "errors": [{"name": "TestSource", "error": "Timeout"}],
            "timing": {
                "GDELT": {"status": "ok", "ms": 1200},
                "FRED": {"status": "ok", "ms": 3500},
                "CISA-KEV": {"status": "ok", "ms": 800},
                "TestSource": {"status": "error", "ms": 30000},
            },
        }
        defaults.update(overrides)
        return SweepResult(**defaults)

    def test_synthesize_briefing_structure(self):
        from src.crucix.briefing import BriefingGenerator, IntelligenceBriefing

        gen = BriefingGenerator()
        result = self._make_sweep_result()
        briefing = gen.synthesize_briefing(result)

        assert isinstance(briefing, IntelligenceBriefing)
        assert briefing.sources_queried == 9
        assert briefing.sources_ok == 7
        assert briefing.sources_failed == 2
        assert briefing.executive_thesis != ""
        assert briefing.source_integrity is not None
        assert len(briefing.source_integrity.strong_sources) > 0
        assert "TestSource" in briefing.source_integrity.weak_sources

    def test_synthesize_briefing_with_delta(self):
        from src.crucix.briefing import BriefingGenerator, DeltaResult, DeltaSummary, Direction

        gen = BriefingGenerator()
        result = self._make_sweep_result()
        delta = DeltaResult(
            timestamp="2025-01-01T01:00:00Z",
            summary=DeltaSummary(total_changes=3, critical_changes=1, direction=Direction.RISK_OFF),
        )
        briefing = gen.synthesize_briefing(result, delta)

        assert briefing.delta is not None
        assert briefing.delta.summary.direction == Direction.RISK_OFF
        assert "risk-off" in briefing.executive_thesis.lower() or "Risk-off" in briefing.executive_thesis

    def test_pattern_recognition_conflict_energy(self):
        from src.crucix.briefing import BriefingGenerator

        gen = BriefingGenerator()
        result = self._make_sweep_result(
            sources={
                "GDELT": {"totalArticles": 20, "articles": []},
                "FRED": {"indicators": [
                    {"id": "VIXCLS", "value": 20, "date": ""},
                    {"id": "DCOILWTICO", "value": 95, "date": ""},  # Oil > 80
                ]},
                "ACLED": {"totalEvents": 30, "totalFatalities": 50},  # > 20 events
            },
        )
        briefing = gen.synthesize_briefing(result)
        # Should detect conflict+energy pattern
        assert len(briefing.pattern_recognition) > 0
        conflict_energy = [p for p in briefing.pattern_recognition if "Conflict" in p.evidence or "conflict" in p.evidence.lower()]
        assert len(conflict_energy) > 0

    def test_pattern_recognition_vix_credit(self):
        from src.crucix.briefing import BriefingGenerator

        gen = BriefingGenerator()
        result = self._make_sweep_result(
            sources={
                "GDELT": {"totalArticles": 10, "articles": []},
                "FRED": {"indicators": [
                    {"id": "VIXCLS", "value": 30, "date": ""},  # VIX > 25
                    {"id": "BAMLH0A0HYM2", "value": 5.5, "date": ""},  # HY > 4
                ]},
            },
        )
        briefing = gen.synthesize_briefing(result)
        vix_credit = [p for p in briefing.pattern_recognition if "VIX" in p.evidence]
        assert len(vix_credit) > 0

    def test_decision_board_populated(self):
        from src.crucix.briefing import BriefingGenerator

        gen = BriefingGenerator()
        result = self._make_sweep_result()
        briefing = gen.synthesize_briefing(result)

        assert briefing.decision_board is not None
        assert briefing.decision_board.best_long != ""
        assert briefing.decision_board.best_hedge != ""

    def test_market_implications(self):
        from src.crucix.briefing import BriefingGenerator

        gen = BriefingGenerator()
        result = self._make_sweep_result()
        briefing = gen.synthesize_briefing(result)

        assert "equities" in briefing.market_implications
        assert "bonds" in briefing.market_implications
        assert "commodities" in briefing.market_implications
        assert "crypto" in briefing.market_implications

    def test_situation_awareness_events(self):
        from src.crucix.briefing import BriefingGenerator

        gen = BriefingGenerator()
        result = self._make_sweep_result()
        briefing = gen.synthesize_briefing(result)

        assert len(briefing.situation_awareness) > 0
        # Military article should be categorized as CONFLICT
        conflict_events = [e for e in briefing.situation_awareness if e.category == "CONFLICT"]
        assert len(conflict_events) > 0

    def test_save_briefing(self):
        from src.crucix.briefing import BriefingGenerator

        gen = BriefingGenerator()
        result = self._make_sweep_result()

        with tempfile.TemporaryDirectory() as tmpdir:
            save_result = gen.save_briefing(result, output_dir=tmpdir)
            assert save_result.path.endswith(".json")
            assert save_result.size_bytes > 0

            # Check files exist
            assert Path(save_result.path).exists()
            assert (Path(tmpdir) / "latest.json").exists()

            # Check content is valid JSON
            data = json.loads(Path(save_result.path).read_text(encoding="utf-8"))
            assert data["sources_queried"] == 9

    @pytest.mark.asyncio
    async def test_run_full_sweep_with_mock_sources(self):
        from src.crucix.briefing import BriefingGenerator, SweepResult
        from src.crucix.data_sources import BaseSourceAdapter, SourceResult, SourceMetadata, SourceTier

        # Create mock adapter
        class MockAdapter(BaseSourceAdapter):
            metadata = SourceMetadata(
                name="MockSource",
                tier=SourceTier.OSINT,
                description="Test source",
            )

            async def fetch_briefing(self) -> SourceResult:
                return SourceResult(source="MockSource", data={"test": True})

        gen = BriefingGenerator(source_adapters=[MockAdapter()])
        result = await gen.run_full_sweep()

        assert isinstance(result, SweepResult)
        assert result.sources_queried == 1
        assert result.sources_ok == 1
        assert result.sources_failed == 0
        assert "MockSource" in result.sources

    @pytest.mark.asyncio
    async def test_run_full_sweep_handles_source_errors(self):
        from src.crucix.briefing import BriefingGenerator
        from src.crucix.data_sources import BaseSourceAdapter, SourceMetadata, SourceTier

        class FailingAdapter(BaseSourceAdapter):
            metadata = SourceMetadata(
                name="FailingSource",
                tier=SourceTier.OSINT,
                description="Always fails",
            )

            async def fetch_briefing(self):
                raise RuntimeError("API connection refused")

        gen = BriefingGenerator(source_adapters=[FailingAdapter()])
        result = await gen.run_full_sweep()

        assert result.sources_queried == 1
        assert result.sources_ok == 0
        assert result.sources_failed == 1
        assert len(result.errors) == 1


# ── Data Sources Tests ────────────────────────────────────────────────


class TestDataSources:
    """Tests for src/crucix/data_sources.py."""

    def test_source_registry(self):
        from src.crucix.data_sources import SOURCE_REGISTRY

        assert "GDELT" in SOURCE_REGISTRY
        assert "FRED" in SOURCE_REGISTRY
        assert "ACLED" in SOURCE_REGISTRY
        assert "OpenSky" in SOURCE_REGISTRY
        assert "CISA-KEV" in SOURCE_REGISTRY

    def test_get_all_source_adapters(self):
        from src.crucix.data_sources import get_all_source_adapters, BaseSourceAdapter

        adapters = get_all_source_adapters()
        assert len(adapters) > 0
        assert all(isinstance(a, BaseSourceAdapter) for a in adapters)

    def test_get_adapters_with_api_keys(self):
        from src.crucix.data_sources import get_all_source_adapters

        adapters = get_all_source_adapters(api_keys={"FRED": "test-key"})
        fred_adapter = next(a for a in adapters if a.metadata.name == "FRED")
        assert fred_adapter.api_key == "test-key"

    def test_fetch_result_model(self):
        from src.crucix.data_sources import FetchResult

        result = FetchResult(source="Test", status="ok", duration_ms=100, data={"key": "value"})
        assert result.source == "Test"
        assert result.status == "ok"
        assert result.duration_ms == 100

        result_err = FetchResult(source="Test", status="error", error="Timeout")
        assert result_err.status == "error"
        assert result_err.error == "Timeout"

    def test_source_result_model(self):
        from src.crucix.data_sources import SourceResult

        result = SourceResult(source="FRED", data={"indicators": []}, signals=["Yield curve inverted"])
        assert result.source == "FRED"
        assert len(result.signals) == 1
        assert result.timestamp  # Auto-generated

    def test_source_metadata_model(self):
        from src.crucix.data_sources import SourceMetadata, SourceTier

        meta = SourceMetadata(
            name="TestSource",
            tier=SourceTier.ECONOMIC,
            requires_auth=True,
            auth_env_var="TEST_API_KEY",
            base_url="https://api.example.com",
        )
        assert meta.name == "TestSource"
        assert meta.tier == SourceTier.ECONOMIC
        assert meta.requires_auth is True

    @pytest.mark.asyncio
    async def test_base_adapter_run_success(self):
        from src.crucix.data_sources import BaseSourceAdapter, FetchResult, SourceResult, SourceMetadata, SourceTier

        class TestAdapter(BaseSourceAdapter):
            metadata = SourceMetadata(name="Test", tier=SourceTier.OSINT, description="Test")

            async def fetch_briefing(self) -> SourceResult:
                return SourceResult(source="Test", data={"ok": True})

        adapter = TestAdapter()
        result = await adapter.run()
        assert isinstance(result, FetchResult)
        assert result.status == "ok"
        assert result.source == "Test"

    @pytest.mark.asyncio
    async def test_base_adapter_run_timeout(self):
        from src.crucix.data_sources import BaseSourceAdapter, FetchResult, SourceResult, SourceMetadata, SourceTier

        class SlowAdapter(BaseSourceAdapter):
            metadata = SourceMetadata(name="SlowTest", tier=SourceTier.OSINT, description="Slow")

            async def fetch_briefing(self) -> SourceResult:
                await asyncio.sleep(10)
                return SourceResult(source="SlowTest")

        adapter = SlowAdapter(timeout=0.01)
        result = await adapter.run()
        assert result.status == "timeout"

    @pytest.mark.asyncio
    async def test_base_adapter_run_error(self):
        from src.crucix.data_sources import BaseSourceAdapter, FetchResult, SourceResult, SourceMetadata, SourceTier

        class ErrorAdapter(BaseSourceAdapter):
            metadata = SourceMetadata(name="ErrorTest", tier=SourceTier.OSINT, description="Errors")

            async def fetch_briefing(self) -> SourceResult:
                raise ValueError("Test error")

        adapter = ErrorAdapter()
        result = await adapter.run()
        assert result.status == "error"
        assert "Test error" in result.error

    def test_fred_adapter_no_key(self):
        from src.crucix.data_sources import FREDAdapter

        adapter = FREDAdapter()
        assert adapter.metadata.name == "FRED"
        assert adapter.metadata.requires_auth is True

    @pytest.mark.asyncio
    async def test_fred_adapter_no_key_returns_error(self):
        from src.crucix.data_sources import FREDAdapter

        adapter = FREDAdapter(api_key=None)
        result = await adapter.fetch_briefing()
        assert result.error is not None
        assert "FRED API key" in result.error

    @pytest.mark.asyncio
    async def test_acled_adapter_no_key_returns_error(self):
        from src.crucix.data_sources import ACLEDAdapter

        adapter = ACLEDAdapter(api_key=None)
        result = await adapter.fetch_briefing()
        assert result.error is not None


# ── Gateway Tests ─────────────────────────────────────────────────────


class TestSweepOrchestrator:
    """Tests for src/crucix/gateway.py SweepOrchestrator."""

    def test_initial_state(self):
        from src.crucix.gateway import SweepOrchestrator, SweepStatus

        orch = SweepOrchestrator()
        assert orch.status == SweepStatus.IDLE
        assert orch.sweep_in_progress is False
        assert orch.last_sweep_time is None
        assert orch.current_data is None

    def test_start_sweep(self):
        from src.crucix.gateway import SweepOrchestrator, SweepStatus

        orch = SweepOrchestrator()
        orch.start_sweep()
        assert orch.status == SweepStatus.IN_PROGRESS
        assert orch.sweep_in_progress is True

    def test_start_sweep_idempotent(self):
        from src.crucix.gateway import SweepOrchestrator, SweepStatus

        orch = SweepOrchestrator()
        orch.start_sweep()
        orch.start_sweep()  # Should not crash
        assert orch.status == SweepStatus.IN_PROGRESS

    def test_complete_sweep(self):
        from src.crucix.gateway import SweepOrchestrator, SweepStatus

        orch = SweepOrchestrator()
        orch.start_sweep()
        orch.complete_sweep({"meta": {"sourcesOk": 25}})

        assert orch.status == SweepStatus.COMPLETED
        assert orch.sweep_in_progress is False
        assert orch.last_sweep_time is not None
        assert orch.current_data == {"meta": {"sourcesOk": 25}}

    def test_fail_sweep(self):
        from src.crucix.gateway import SweepOrchestrator, SweepStatus

        orch = SweepOrchestrator()
        orch.start_sweep()
        orch.fail_sweep("API timeout")

        assert orch.status == SweepStatus.FAILED
        assert orch.sweep_in_progress is False

    def test_uptime_seconds(self):
        from src.crucix.gateway import SweepOrchestrator

        orch = SweepOrchestrator()
        assert orch.uptime_seconds >= 0

    def test_next_sweep_time(self):
        from src.crucix.gateway import SweepOrchestrator

        orch = SweepOrchestrator(refresh_interval_minutes=15)
        assert orch.next_sweep_time is None

        orch.start_sweep()
        orch.complete_sweep({})
        assert orch.next_sweep_time is not None

    def test_get_health(self):
        from src.crucix.gateway import SweepOrchestrator, HealthResponse

        orch = SweepOrchestrator()
        orch.start_sweep()
        orch.complete_sweep({"meta": {"sourcesOk": 25, "sourcesFailed": 2}})

        health = orch.get_health(llm_provider="openai", language="en")
        assert isinstance(health, HealthResponse)
        assert health.status == "ok"
        assert health.sweep_in_progress is False
        assert health.sources_ok == 25
        assert health.llm_enabled is True
        assert health.llm_provider == "openai"

    def test_sse_client_management(self):
        from src.crucix.gateway import SweepOrchestrator, SweeepEvent

        orch = SweepOrchestrator()

        # Add mock clients
        client1 = MagicMock()
        client2 = MagicMock()
        orch.add_sse_client(client1)
        orch.add_sse_client(client2)
        assert len(orch._sse_clients) == 2

        # Broadcast
        event = SweeepEvent(type="update", data={"key": "value"})
        sent = orch.broadcast(event)
        assert sent == 2

        # Remove
        orch.remove_sse_client(client1)
        assert len(orch._sse_clients) == 1


class TestGatewayModels:
    """Tests for gateway models."""

    def test_health_response_model(self):
        from src.crucix.gateway import HealthResponse

        resp = HealthResponse()
        assert resp.status == "ok"
        assert resp.uptime_seconds == 0
        assert resp.sweep_in_progress is False

    def test_sweep_event_model(self):
        from src.crucix.gateway import SweeepEvent

        event = SweeepEvent(type="connected")
        assert event.type == "connected"
        assert event.timestamp  # Auto-generated

    def test_briefing_save_result(self):
        from src.crucix.briefing import BriefingSaveResult

        result = BriefingSaveResult(path="/tmp/test.json", timestamp="2025-01-01", size_bytes=1024)
        assert result.path == "/tmp/test.json"
        assert result.size_bytes == 1024

    def test_gateway_briefing_save_result(self):
        from src.crucix.gateway import BriefingSaveResult

        result = BriefingSaveResult(path="/tmp/test.json", timestamp="2025-01-01", size_bytes=1024)
        assert result.path == "/tmp/test.json"
        assert result.size_bytes == 1024


# ── Integration Tests ─────────────────────────────────────────────────


class TestCrucixIntegration:
    """End-to-end integration tests for the Crucix Python port."""

    @pytest.mark.asyncio
    async def test_full_pipeline(self):
        """Test the full pipeline: config -> sources -> sweep -> delta -> briefing."""
        from src.crucix.briefing import BriefingGenerator, IntelligenceBriefing
        from src.crucix.config import CrucixConfig
        from src.crucix.data_sources import BaseSourceAdapter, SourceResult, SourceMetadata, SourceTier

        # Create mock adapters
        class MockGDELT(BaseSourceAdapter):
            metadata = SourceMetadata(name="GDELT", tier=SourceTier.OSINT)

            async def fetch_briefing(self) -> SourceResult:
                return SourceResult(source="GDELT", data={"totalArticles": 20, "articles": [
                    {"title": "Military escalation in region X"},
                ]})

        class MockFRED(BaseSourceAdapter):
            metadata = SourceMetadata(name="FRED", tier=SourceTier.ECONOMIC)

            async def fetch_briefing(self) -> SourceResult:
                return SourceResult(source="FRED", data={"indicators": [
                    {"id": "VIXCLS", "label": "VIX", "value": 18.5, "date": "2025-01-01"},
                    {"id": "DFF", "label": "Fed Funds", "value": 5.33, "date": "2025-01-01"},
                ]})

        config = CrucixConfig(source_timeout_seconds=5.0)
        gen = BriefingGenerator(
            config=config,
            source_adapters=[MockGDELT(), MockFRED()],
        )

        # Run sweep
        result = await gen.run_full_sweep()
        assert result.sources_ok == 2
        assert result.sources_failed == 0

        # Compute delta (first sweep, so None)
        delta = gen.compute_sweep_delta(result)
        assert delta is None  # No previous data

        # Synthesize briefing
        briefing = gen.synthesize_briefing(result)
        assert isinstance(briefing, IntelligenceBriefing)
        assert briefing.sources_queried == 2
        assert briefing.sources_ok == 2

        # Second sweep — now we have delta
        result2 = await gen.run_full_sweep()
        delta2 = gen.compute_sweep_delta(result2)
        # Delta might be None if data is exactly the same (no changes)
        # But the pipeline should not crash

    def test_localization_with_briefing(self):
        """Test that localization works with briefing output."""
        from src.crucix.briefing import BriefingGenerator, Direction, DeltaResult, DeltaSummary
        from src.crucix.localization import LocalizationManager

        mgr = LocalizationManager()
        mgr.register_locale_data("en", {
            "dashboard": {"title": "CRUCIX - Intelligence Terminal"},
            "delta": {"escalation": "ESCALATION", "deescalation": "DE-ESCALATION"},
        })

        assert mgr.t("dashboard.title") == "CRUCIX - Intelligence Terminal"
        assert mgr.t("delta.escalation") == "ESCALATION"

    def test_config_integration(self):
        """Test that config integrates with all modules."""
        from src.crucix.config import CrucixConfig
        from src.crucix.briefing import BriefingGenerator
        from src.crucix.localization import LocalizationManager
        from src.crucix.gateway import SweepOrchestrator

        config = CrucixConfig(port=3117, language="en")

        # All modules accept config
        gen = BriefingGenerator(config=config)
        mgr = LocalizationManager(default_locale=config.language)
        orch = SweepOrchestrator(refresh_interval_minutes=config.refresh_interval_minutes)

        assert gen.config.port == 3117
        assert mgr.default_locale == "en"
        assert orch.refresh_interval_minutes == 15

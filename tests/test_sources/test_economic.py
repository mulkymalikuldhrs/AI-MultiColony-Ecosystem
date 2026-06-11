"""Tests for EconomicSource — FRED, BLS, EIA, Treasury sources."""

from __future__ import annotations

import pytest

from ai_multicolony.sources.economic import (
    EconomicIndicator,
    EconomicSource,
    ECONOMIC_PROFILES,
    GDPRate,
    InflationData,
    InterestRateData,
)
from ai_multicolony.sources.base import SourceCategory, SourceReliability


# ── Fixtures ────────────────────────────────────────────────────────────────

@pytest.fixture
def econ():
    return EconomicSource()


@pytest.fixture
def econ_us_only():
    return EconomicSource(countries=["US"])


# ── Economic Profiles ────────────────────────────────────────────────────

class TestEconomicProfiles:
    """Test country economic profiles."""

    def test_us_profile_exists(self):
        assert "US" in ECONOMIC_PROFILES

    def test_eu_profile_exists(self):
        assert "EU" in ECONOMIC_PROFILES

    def test_cn_profile_exists(self):
        assert "CN" in ECONOMIC_PROFILES

    def test_profile_has_required_fields(self):
        for country, profile in ECONOMIC_PROFILES.items():
            assert "gdp_growth_annual" in profile
            assert "cpi_yoy" in profile
            assert "policy_rate" in profile
            assert "central_bank" in profile
            assert "unemployment_rate" in profile


# ── Source Properties ────────────────────────────────────────────────────

class TestEconomicSourceProperties:
    """Test source metadata."""

    def test_name(self, econ):
        assert econ.name == "economic"

    def test_category(self, econ):
        assert econ.category == SourceCategory.ECONOMIC

    def test_reliability(self, econ):
        assert econ.reliability == SourceReliability.RELIABLE

    def test_tracked_countries(self, econ):
        countries = econ.tracked_countries
        assert "US" in countries
        assert len(countries) > 0


# ── Fetch ────────────────────────────────────────────────────────────────

class TestEconomicFetch:
    """Test targeted fetch."""

    @pytest.mark.asyncio
    async def test_fetch_inflation(self, econ_us_only):
        result = await econ_us_only.fetch("inflation", max_items=10)
        assert len(result.items) > 0

    @pytest.mark.asyncio
    async def test_fetch_gdp(self, econ_us_only):
        result = await econ_us_only.fetch("GDP", max_items=10)
        assert len(result.items) > 0

    @pytest.mark.asyncio
    async def test_fetch_interest_rate(self, econ_us_only):
        result = await econ_us_only.fetch("interest rate", max_items=10)
        assert len(result.items) > 0

    @pytest.mark.asyncio
    async def test_fetch_max_items(self, econ_us_only):
        result = await econ_us_only.fetch("GDP", max_items=2)
        assert len(result.items) <= 2

    @pytest.mark.asyncio
    async def test_fetch_no_match(self, econ_us_only):
        result = await econ_us_only.fetch("xyznonexistent123", max_items=10)
        assert len(result.items) == 0


# ── Scan ─────────────────────────────────────────────────────────────────

class TestEconomicScan:
    """Test broad scan."""

    @pytest.mark.asyncio
    async def test_scan_returns_items(self, econ):
        result = await econ.scan(max_items=50)
        assert len(result.items) > 0

    @pytest.mark.asyncio
    async def test_scan_items_are_source_items(self, econ):
        result = await econ.scan(max_items=10)
        for item in result.items:
            assert item.source_name == "economic"
            assert item.category == SourceCategory.ECONOMIC


# ── Data Accessors ───────────────────────────────────────────────────────

class TestEconomicDataAccessors:
    """Test get_gdp_data, get_inflation_data, get_interest_rate_data."""

    def test_get_gdp_data(self, econ):
        gdp = econ.get_gdp_data("US")
        assert gdp is not None
        assert isinstance(gdp, GDPRate)
        assert gdp.country == "US"
        assert gdp.annual_growth_pct > 0

    def test_get_gdp_data_unknown(self, econ):
        assert econ.get_gdp_data("XX") is None

    def test_get_inflation_data(self, econ):
        inflation = econ.get_inflation_data("US")
        assert inflation is not None
        assert isinstance(inflation, InflationData)
        assert inflation.cpi_yoy_pct > 0

    def test_get_inflation_data_unknown(self, econ):
        assert econ.get_inflation_data("XX") is None

    def test_get_interest_rate_data(self, econ):
        rates = econ.get_interest_rate_data("US")
        assert rates is not None
        assert isinstance(rates, InterestRateData)
        assert rates.central_bank == "Federal Reserve"

    def test_get_interest_rate_data_unknown(self, econ):
        assert econ.get_interest_rate_data("XX") is None


# ── Pydantic Models ──────────────────────────────────────────────────────

class TestEconomicModels:
    """Test Pydantic model validation."""

    def test_economic_indicator_to_item(self):
        indicator = EconomicIndicator(
            indicator_id="US_cpi",
            name="CPI",
            country="US",
            value=3.2,
            unit="%",
            category="inflation",
        )
        item = indicator.to_item()
        assert item.source_name == "economic"
        assert item.category == SourceCategory.ECONOMIC

    def test_economic_indicator_with_change(self):
        indicator = EconomicIndicator(
            name="CPI",
            country="US",
            value=3.2,
            change_pct=0.3,
        )
        item = indicator.to_item()
        assert "change" in item.content or "3.2" in item.content

    def test_gdp_rate_model(self):
        gdp = GDPRate(country="US", annual_growth_pct=2.5)
        assert gdp.country == "US"
        assert gdp.annual_growth_pct == 2.5

    def test_inflation_data_model(self):
        inf = InflationData(country="EU", cpi_yoy_pct=2.4)
        assert inf.cpi_yoy_pct == 2.4

    def test_interest_rate_model(self):
        rate = InterestRateData(country="JP", central_bank="BOJ", policy_rate_pct=0.1)
        assert rate.policy_rate_pct == 0.1


# ── Health Check ─────────────────────────────────────────────────────────

class TestEconomicHealthCheck:
    """Test health check."""

    @pytest.mark.asyncio
    async def test_health_check(self, econ):
        result = await econ.health_check()
        assert "status" in result

"""Comprehensive tests for CrucixBridge and DeerFlowBridge integrations.

Covers instantiation, tool listing, tool execution (mocked), error handling,
async lifecycle, MiddlewareChain, ChannelManager, and configuration.
"""

from __future__ import annotations

from typing import Any, Dict
from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest
import pytest_asyncio

from ai_multicolony.integrations.crucix_bridge import (
    OSINT_SOURCES,
    CrucixBridge,
    CrucixBridgeError,
    CrucixUnavailableError,
    IntelligenceError,
    SourceNotFoundError,
)
from ai_multicolony.integrations.deerflow_bridge import (
    SUPPORTED_CHANNELS,
    ChannelManager,
    ChannelNotFoundError,
    DeerFlowBridge,
    DeerFlowBridgeError,
    DeerFlowUnavailableError,
    GraphExecutionError,
    GraphManager,
    LoggingMiddleware,
    MemoryManager,
    Middleware,
    MiddlewareChain,
    MiddlewareError,
)


# ═══════════════════════════════════════════════════════════════════════════════
# FIXTURES
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.fixture
def crucix_config():
    """Config for CrucixBridge."""
    return {"crucix_url": "http://localhost:3117", "timeout": 10.0}


@pytest.fixture
def deerflow_config():
    """Config for DeerFlowBridge."""
    return {"gateway_url": "http://localhost:8001"}


@pytest.fixture
def crucix_bridge(crucix_config):
    """Create a CrucixBridge instance."""
    return CrucixBridge(config=crucix_config)


@pytest.fixture
def deerflow_bridge(deerflow_config):
    """Create a DeerFlowBridge instance."""
    return DeerFlowBridge(config=deerflow_config)


@pytest_asyncio.fixture
async def crucix_bridge_open(crucix_config):
    """Create and properly close a CrucixBridge."""
    bridge = CrucixBridge(config=crucix_config)
    yield bridge
    await bridge.close()


@pytest_asyncio.fixture
async def deerflow_bridge_open(deerflow_config):
    """Create and properly close a DeerFlowBridge."""
    bridge = DeerFlowBridge(config=deerflow_config)
    yield bridge
    await bridge.close()


# ═══════════════════════════════════════════════════════════════════════════════
# CRUCIX BRIDGE TESTS
# ═══════════════════════════════════════════════════════════════════════════════


class TestCrucixBridgeInstantiation:
    """Test CrucixBridge instantiation and configuration."""

    def test_default_config(self):
        """Default config uses localhost:3117 and 30s timeout."""
        bridge = CrucixBridge()
        assert bridge._base_url == "http://localhost:3117"
        assert bridge._timeout == 30.0

    def test_custom_config(self, crucix_bridge):
        """Custom config is applied."""
        assert crucix_bridge._base_url == "http://localhost:3117"
        assert crucix_bridge._timeout == 10.0

    def test_trailing_slash_stripped(self):
        """Trailing slash in URL is stripped."""
        bridge = CrucixBridge(config={"crucix_url": "http://localhost:3117/"})
        assert bridge._base_url == "http://localhost:3117"

    def test_http_client_created(self, crucix_bridge):
        """An httpx.AsyncClient is created on instantiation."""
        assert isinstance(crucix_bridge._client, httpx.AsyncClient)

    def test_none_config_defaults(self):
        """None config uses defaults."""
        bridge = CrucixBridge(config=None)
        assert bridge.config == {}
        assert bridge._base_url == "http://localhost:3117"


class TestCrucixBridgeSources:
    """Test OSINT source listing."""

    @pytest.mark.asyncio
    async def test_get_available_sources(self, crucix_bridge_open):
        """get_available_sources returns all OSINT source names."""
        sources = await crucix_bridge_open.get_available_sources()
        assert isinstance(sources, list)
        assert len(sources) == len(OSINT_SOURCES)
        assert "GDELT" in sources
        assert "CISA-KEV" in sources
        assert "FRED" in sources

    @pytest.mark.asyncio
    async def test_source_details_valid(self, crucix_bridge_open):
        """get_source_details returns metadata for a valid source."""
        details = await crucix_bridge_open.get_source_details("GDELT")
        assert details["name"] == "GDELT"
        assert "tier" in details
        assert "category" in details
        assert details["data_source"] == "crucix_catalogue"

    @pytest.mark.asyncio
    async def test_source_details_invalid(self, crucix_bridge_open):
        """get_source_details raises SourceNotFoundError for invalid source."""
        with pytest.raises(SourceNotFoundError, match="not found"):
            await crucix_bridge_open.get_source_details("NONEXISTENT")

    def test_osint_sources_catalogue(self):
        """OSINT_SOURCES contains expected tiers."""
        assert "GDELT" in OSINT_SOURCES
        assert OSINT_SOURCES["GDELT"]["tier"] == "1"
        assert "CISA-KEV" in OSINT_SOURCES
        assert OSINT_SOURCES["CISA-KEV"]["category"] == "cyber"


class TestCrucixBridgeFetchIntelligence:
    """Test fetch_intelligence with mocked HTTP calls."""

    @pytest.mark.asyncio
    async def test_fetch_intelligence_success(self, crucix_bridge_open):
        """Successful fetch returns structured intelligence data."""
        mock_data = {
            "sources": {"GDELT": {"conflicts": []}, "ACLED": {}},
            "meta": {"sweep_id": "123"},
            "news": [],
            "newsFeed": [],
        }
        with patch.object(crucix_bridge_open, "_get", new_callable=AsyncMock, return_value=mock_data):
            result = await crucix_bridge_open.fetch_intelligence()
            assert result["data_source"] == "crucix_intelligence"
            assert "sources" in result
            assert "timestamp" in result

    @pytest.mark.asyncio
    async def test_fetch_intelligence_with_source_filter(self, crucix_bridge_open):
        """Source filter limits returned sources."""
        mock_data = {
            "sources": {"GDELT": {"conflicts": []}, "ACLED": {"totalEvents": 5}},
            "meta": {},
            "news": [],
            "newsFeed": [],
        }
        with patch.object(crucix_bridge_open, "_get", new_callable=AsyncMock, return_value=mock_data):
            with patch.object(crucix_bridge_open, "_search_gdelt", new_callable=AsyncMock, return_value={}):
                result = await crucix_bridge_open.fetch_intelligence(sources=["GDELT"])
                assert "GDELT" in result["sources"]
                assert "ACLED" not in result["sources"]

    @pytest.mark.asyncio
    async def test_fetch_intelligence_with_query(self, crucix_bridge_open):
        """Query triggers GDELT search."""
        mock_data = {
            "sources": {},
            "meta": {},
            "news": [],
            "newsFeed": [],
        }
        gdelt_result = {"query": "test", "matching_articles": 5, "articles": []}
        with patch.object(crucix_bridge_open, "_get", new_callable=AsyncMock, return_value=mock_data):
            with patch.object(crucix_bridge_open, "_search_gdelt", new_callable=AsyncMock, return_value=gdelt_result):
                result = await crucix_bridge_open.fetch_intelligence(query="test")
                assert "gdelt_search" in result
                assert result["gdelt_search"]["query"] == "test"

    @pytest.mark.asyncio
    async def test_fetch_intelligence_unavailable(self, crucix_bridge_open):
        """Unavailable Crucix service returns error dict."""
        with patch.object(
            crucix_bridge_open, "_get", new_callable=AsyncMock, side_effect=CrucixUnavailableError("down")
        ):
            result = await crucix_bridge_open.fetch_intelligence()
            assert result["status"] == "unavailable"
            assert "error" in result


class TestCrucixBridgeHealthCheck:
    """Test health_check method."""

    @pytest.mark.asyncio
    async def test_health_check_success(self, crucix_bridge_open):
        """Successful health check returns data."""
        mock_data = {"uptime": 3600, "sweeps": 100}
        with patch.object(crucix_bridge_open, "_get", new_callable=AsyncMock, return_value=mock_data):
            result = await crucix_bridge_open.health_check()
            assert result["data_source"] == "crucix_health"

    @pytest.mark.asyncio
    async def test_health_check_unavailable(self, crucix_bridge_open):
        """Unavailable service returns unavailable status."""
        with patch.object(
            crucix_bridge_open, "_get", new_callable=AsyncMock, side_effect=CrucixUnavailableError("down")
        ):
            result = await crucix_bridge_open.health_check()
            assert result["status"] == "unavailable"


class TestCrucixBridgeAnalysis:
    """Test higher-level analysis methods."""

    @pytest.mark.asyncio
    async def test_analyze_threats_with_data(self, crucix_bridge_open):
        """analyze_threats processes provided data."""
        data = {
            "sources": {
                "CISA-KEV": {"signals": [{"severity": "high", "signal": "CVE-2024-0001"}]},
                "GDELT": {"conflicts": ["a"] * 15, "crisis": ["b"] * 8},
                "OFAC": {"sampleEntries": ["entry1", "entry2"]},
            },
            "delta": {"summary": {"direction": "up"}},
        }
        result = await crucix_bridge_open.analyze_threats(data=data)
        assert result["data_source"] == "crucix_threat_analysis"
        assert result["threat_count"] > 0
        assert result["threat_level"] in ("low", "elevated", "high", "critical")
        assert result["delta_direction"] == "up"

    @pytest.mark.asyncio
    async def test_analyze_threats_fetches_when_no_data(self, crucix_bridge_open):
        """analyze_threats fetches data if none provided."""
        mock_data = {"sources": {}, "delta": {}}
        with patch.object(crucix_bridge_open, "_get", new_callable=AsyncMock, return_value=mock_data):
            result = await crucix_bridge_open.analyze_threats()
            assert result["data_source"] == "crucix_threat_analysis"

    @pytest.mark.asyncio
    async def test_analyze_threats_unavailable(self, crucix_bridge_open):
        """analyze_threats handles unavailable service."""
        with patch.object(
            crucix_bridge_open, "_get", new_callable=AsyncMock, side_effect=CrucixUnavailableError("down")
        ):
            result = await crucix_bridge_open.analyze_threats()
            assert result["status"] == "unavailable"

    @pytest.mark.asyncio
    async def test_analyze_threats_critical_level(self, crucix_bridge_open):
        """Critical threats produce critical threat level."""
        data = {
            "sources": {
                "CISA-KEV": {"signals": [{"severity": "critical", "signal": "zero-day"}]},
            },
            "delta": {},
        }
        result = await crucix_bridge_open.analyze_threats(data=data)
        assert result["threat_level"] == "critical"

    @pytest.mark.asyncio
    async def test_analyze_threats_low_level(self, crucix_bridge_open):
        """No threats produce low threat level."""
        data = {"sources": {}, "delta": {}}
        result = await crucix_bridge_open.analyze_threats(data=data)
        assert result["threat_level"] == "low"

    @pytest.mark.asyncio
    async def test_get_geopolitical_risk(self, crucix_bridge_open):
        """get_geopolitical_risk returns risk score."""
        mock_data = {
            "sources": {
                "GDELT": {"conflicts": ["a"] * 10, "crisis": ["b"] * 5, "allArticles": []},
                "ACLED": {"totalEvents": 30},
            },
            "delta": {"summary": {"direction": "up"}},
        }
        with patch.object(crucix_bridge_open, "_get", new_callable=AsyncMock, return_value=mock_data):
            result = await crucix_bridge_open.get_geopolitical_risk()
            assert "risk_score" in result
            assert "risk_level" in result
            assert result["data_source"] == "crucix_geopolitical_risk"

    @pytest.mark.asyncio
    async def test_get_geopolitical_risk_unavailable(self, crucix_bridge_open):
        """get_geopolitical_risk handles unavailable service."""
        with patch.object(
            crucix_bridge_open, "_get", new_callable=AsyncMock, side_effect=CrucixUnavailableError("down")
        ):
            result = await crucix_bridge_open.get_geopolitical_risk()
            assert result["status"] == "unavailable"
            assert result["risk_score"] == 0

    @pytest.mark.asyncio
    async def test_get_supply_chain_risk(self, crucix_bridge_open):
        """get_supply_chain_risk returns risk score."""
        mock_data = {
            "sources": {
                "GSCPI": {"value": 1.5, "trend": "up"},
                "EIA": {},
                "Comtrade": {},
            },
            "energy": {"wti": 95.0, "brent": 98.0, "natgas": 6.0},
            "metals": {"gold": 2000.0},
        }
        with patch.object(crucix_bridge_open, "_get", new_callable=AsyncMock, return_value=mock_data):
            result = await crucix_bridge_open.get_supply_chain_risk(commodity="oil")
            assert "risk_score" in result
            assert "risk_level" in result
            assert result["data_source"] == "crucix_supply_chain_risk"
            assert result["gscpi_value"] == 1.5


class TestCrucixBridgeErrorHandling:
    """Test CrucixBridge error handling."""

    @pytest.mark.asyncio
    async def test_http_error_raises_unavailable(self, crucix_bridge_open):
        """HTTP error is converted to CrucixUnavailableError."""
        with patch.object(
            crucix_bridge_open._client,
            "get",
            new_callable=AsyncMock,
            side_effect=httpx.ConnectError("Connection refused"),
        ):
            with pytest.raises(CrucixUnavailableError):
                await crucix_bridge_open._get("/api/data")

    def test_source_not_found_error(self):
        """SourceNotFoundError is a CrucixBridgeError."""
        assert issubclass(SourceNotFoundError, CrucixBridgeError)

    def test_intelligence_error(self):
        """IntelligenceError is a CrucixBridgeError."""
        assert issubclass(IntelligenceError, CrucixBridgeError)

    def test_unavailable_error_hierarchy(self):
        """CrucixUnavailableError is a CrucixBridgeError."""
        assert issubclass(CrucixUnavailableError, CrucixBridgeError)


class TestCrucixBridgeLifecycle:
    """Test CrucixBridge connection lifecycle."""

    @pytest.mark.asyncio
    async def test_close(self, crucix_bridge):
        """close() closes the HTTP client."""
        with patch.object(crucix_bridge._client, "aclose", new_callable=AsyncMock) as mock_close:
            await crucix_bridge.close()
            mock_close.assert_awaited_once()


# ═══════════════════════════════════════════════════════════════════════════════
# DEERFLOW BRIDGE TESTS
# ═══════════════════════════════════════════════════════════════════════════════


class TestDeerFlowBridgeInstantiation:
    """Test DeerFlowBridge instantiation and configuration."""

    def test_default_config(self):
        """Default config uses localhost:8001."""
        bridge = DeerFlowBridge()
        assert bridge._gateway_url == "http://localhost:8001"

    def test_custom_config(self, deerflow_bridge):
        """Custom gateway URL is applied."""
        assert deerflow_bridge._gateway_url == "http://localhost:8001"

    def test_sub_managers_created(self, deerflow_bridge):
        """Channel, graph, and memory managers are created."""
        assert isinstance(deerflow_bridge.channels, ChannelManager)
        assert isinstance(deerflow_bridge.graphs, GraphManager)
        assert isinstance(deerflow_bridge.memory, MemoryManager)

    def test_middleware_chain_created(self, deerflow_bridge):
        """MiddlewareChain is created with default LoggingMiddleware."""
        assert isinstance(deerflow_bridge.middleware_chain, MiddlewareChain)
        mws = deerflow_bridge.middleware_chain.middlewares
        assert len(mws) >= 1
        assert any(isinstance(m, LoggingMiddleware) for m in mws)

    def test_custom_middlewares(self):
        """Custom middlewares override defaults."""

        class CustomMiddleware(Middleware):
            async def process_request(self, request):
                return request

            async def process_response(self, response):
                return response

        mw = CustomMiddleware()
        bridge = DeerFlowBridge(config={"middlewares": [mw]})
        assert len(bridge.middleware_chain.middlewares) == 1
        assert bridge.middleware_chain.middlewares[0] is mw


class TestMiddlewareChain:
    """Test MiddlewareChain functionality."""

    def test_empty_chain(self):
        """Empty chain passes through requests/responses."""
        chain = MiddlewareChain()
        assert chain.middlewares == []

    def test_add_middleware(self):
        """add() appends middleware and returns self for chaining."""

        class DummyMiddleware(Middleware):
            async def process_request(self, request):
                return request

            async def process_response(self, response):
                return response

        chain = MiddlewareChain()
        mw = DummyMiddleware()
        result = chain.add(mw)
        assert result is chain
        assert len(chain.middlewares) == 1

    def test_remove_middleware(self):
        """remove() removes a specific middleware instance."""

        class DummyMiddleware(Middleware):
            async def process_request(self, request):
                return request

            async def process_response(self, response):
                return response

        mw1 = DummyMiddleware()
        mw2 = DummyMiddleware()
        chain = MiddlewareChain([mw1, mw2])
        chain.remove(mw1)
        assert len(chain.middlewares) == 1
        assert chain.middlewares[0] is mw2

    @pytest.mark.asyncio
    async def test_process_request_forward_order(self):
        """Requests are processed in forward order."""

        class TagMiddleware(Middleware):
            def __init__(self, tag):
                self.tag = tag

            async def process_request(self, request):
                request.setdefault("tags", []).append(self.tag)
                return request

            async def process_response(self, response):
                return response

        chain = MiddlewareChain([TagMiddleware("a"), TagMiddleware("b")])
        result = await chain.process_request({})
        assert result["tags"] == ["a", "b"]

    @pytest.mark.asyncio
    async def test_process_response_reverse_order(self):
        """Responses are processed in reverse order."""

        class TagMiddleware(Middleware):
            def __init__(self, tag):
                self.tag = tag

            async def process_request(self, request):
                return request

            async def process_response(self, response):
                response.setdefault("tags", []).append(self.tag)
                return response

        chain = MiddlewareChain([TagMiddleware("a"), TagMiddleware("b")])
        result = await chain.process_response({})
        assert result["tags"] == ["b", "a"]

    @pytest.mark.asyncio
    async def test_middleware_error_raises(self):
        """Failing middleware raises MiddlewareError."""

        class FailingMiddleware(Middleware):
            async def process_request(self, request):
                raise ValueError("boom")

            async def process_response(self, response):
                return response

        chain = MiddlewareChain([FailingMiddleware()])
        with pytest.raises(MiddlewareError, match="boom"):
            await chain.process_request({})

    @pytest.mark.asyncio
    async def test_middleware_response_error_raises(self):
        """Failing middleware on response raises MiddlewareError."""

        class FailingResponseMiddleware(Middleware):
            async def process_request(self, request):
                return request

            async def process_response(self, response):
                raise ValueError("response boom")

        chain = MiddlewareChain([FailingResponseMiddleware()])
        with pytest.raises(MiddlewareError, match="response boom"):
            await chain.process_response({})

    def test_middlewares_property_returns_copy(self):
        """middlewares property returns a shallow copy."""

        class DummyMiddleware(Middleware):
            async def process_request(self, request):
                return request

            async def process_response(self, response):
                return response

        chain = MiddlewareChain([DummyMiddleware()])
        mws = chain.middlewares
        mws.append(DummyMiddleware())
        assert len(chain.middlewares) == 1  # Original not affected


class TestLoggingMiddleware:
    """Test built-in LoggingMiddleware."""

    @pytest.mark.asyncio
    async def test_process_request(self):
        """LoggingMiddleware passes request through unchanged."""
        mw = LoggingMiddleware()
        request = {"channel": "discord", "action": "send"}
        result = await mw.process_request(request)
        assert result == request

    @pytest.mark.asyncio
    async def test_process_response(self):
        """LoggingMiddleware passes response through unchanged."""
        mw = LoggingMiddleware()
        response = {"status": "ok"}
        result = await mw.process_response(response)
        assert result == response


class TestChannelManager:
    """Test ChannelManager functionality."""

    def test_supported_channels(self):
        """SUPPORTED_CHANNELS contains expected channels."""
        assert "discord" in SUPPORTED_CHANNELS
        assert "slack" in SUPPORTED_CHANNELS
        assert "telegram" in SUPPORTED_CHANNELS

    @pytest.mark.asyncio
    async def test_list_channels_success(self):
        """list_channels returns channel names on success."""
        cm = ChannelManager(gateway_url="http://localhost:8001")
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "channels": {"discord": {"status": "running"}, "slack": {"status": "stopped"}}
        }
        mock_response.raise_for_status = MagicMock()
        with patch.object(cm._client, "get", new_callable=AsyncMock, return_value=mock_response):
            channels = await cm.list_channels()
            assert "discord" in channels
            assert "slack" in channels

    @pytest.mark.asyncio
    async def test_list_channels_unavailable(self):
        """list_channels returns empty list on unavailable service."""
        cm = ChannelManager(gateway_url="http://localhost:8001")
        with patch.object(
            cm._client, "get", new_callable=AsyncMock, side_effect=httpx.ConnectError("refused")
        ):
            channels = await cm.list_channels()
            assert channels == []

    @pytest.mark.asyncio
    async def test_get_channel_success(self):
        """get_channel returns channel status dict."""
        cm = ChannelManager(gateway_url="http://localhost:8001")
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "channels": {"discord": {"status": "running"}}
        }
        mock_response.raise_for_status = MagicMock()
        with patch.object(cm._client, "get", new_callable=AsyncMock, return_value=mock_response):
            result = await cm.get_channel("discord")
            assert result["status"] == "running"

    @pytest.mark.asyncio
    async def test_get_channel_not_found(self):
        """get_channel raises ChannelNotFoundError for unknown channel."""
        cm = ChannelManager(gateway_url="http://localhost:8001")
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"channels": {}}
        mock_response.raise_for_status = MagicMock()
        with patch.object(cm._client, "get", new_callable=AsyncMock, return_value=mock_response):
            with pytest.raises(ChannelNotFoundError, match="not found"):
                await cm.get_channel("nonexistent")

    @pytest.mark.asyncio
    async def test_get_channel_unavailable(self):
        """get_channel returns unavailable dict on service down."""
        cm = ChannelManager(gateway_url="http://localhost:8001")
        with patch.object(
            cm._client, "get", new_callable=AsyncMock, side_effect=httpx.ConnectError("refused")
        ):
            result = await cm.get_channel("discord")
            assert result["status"] == "unavailable"

    @pytest.mark.asyncio
    async def test_restart_channel_success(self):
        """restart_channel returns success on 200."""
        cm = ChannelManager(gateway_url="http://localhost:8001")
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"success": True, "message": "restarted"}
        mock_response.raise_for_status = MagicMock()
        with patch.object(cm._client, "post", new_callable=AsyncMock, return_value=mock_response):
            result = await cm.restart_channel("discord")
            assert result["success"] is True

    @pytest.mark.asyncio
    async def test_restart_channel_unavailable(self):
        """restart_channel returns failure on service down."""
        cm = ChannelManager(gateway_url="http://localhost:8001")
        with patch.object(
            cm._client, "post", new_callable=AsyncMock, side_effect=httpx.ConnectError("refused")
        ):
            result = await cm.restart_channel("discord")
            assert result["success"] is False

    @pytest.mark.asyncio
    async def test_send_message_with_thread(self):
        """send_message creates a thread and run."""
        cm = ChannelManager(gateway_url="http://localhost:8001")

        thread_resp = MagicMock()
        thread_resp.status_code = 201
        thread_resp.json.return_value = {"thread_id": "t_123"}

        run_resp = MagicMock()
        run_resp.status_code = 200
        run_resp.json.return_value = {"run_id": "r_456"}

        with patch.object(cm._client, "post", new_callable=AsyncMock, side_effect=[thread_resp, run_resp]):
            result = await cm.send_message("discord", "hello")
            assert result["status"] == "sent"
            assert result["thread_id"] == "t_123"
            assert result["run_id"] == "r_456"

    @pytest.mark.asyncio
    async def test_send_message_fallback(self):
        """send_message falls back when thread creation fails."""
        cm = ChannelManager(gateway_url="http://localhost:8001")

        thread_resp = MagicMock()
        thread_resp.status_code = 500

        with patch.object(cm._client, "post", new_callable=AsyncMock, return_value=thread_resp):
            result = await cm.send_message("discord", "hello")
            assert result["status"] == "channel_only"

    @pytest.mark.asyncio
    async def test_send_message_http_error(self):
        """send_message handles HTTP errors gracefully."""
        cm = ChannelManager(gateway_url="http://localhost:8001")
        with patch.object(
            cm._client, "post", new_callable=AsyncMock, side_effect=httpx.ConnectError("refused")
        ):
            result = await cm.send_message("discord", "hello")
            assert result["status"] == "unavailable"

    @pytest.mark.asyncio
    async def test_get_status(self):
        """get_status returns channel service status."""
        cm = ChannelManager(gateway_url="http://localhost:8001")
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"service_running": True, "channels": {}}
        mock_response.raise_for_status = MagicMock()
        with patch.object(cm._client, "get", new_callable=AsyncMock, return_value=mock_response):
            result = await cm.get_status()
            assert result["service_running"] is True


class TestGraphManager:
    """Test GraphManager functionality."""

    @pytest.mark.asyncio
    async def test_create_graph(self):
        """create_graph returns a graph ID."""
        gm = GraphManager(gateway_url="http://localhost:8001")
        graph_id = await gm.create_graph({"name": "test_graph"})
        assert graph_id.startswith("graph_")
        assert len(gm.list_graphs()) == 1

    @pytest.mark.asyncio
    async def test_list_graphs(self):
        """list_graphs returns all created graphs."""
        gm = GraphManager(gateway_url="http://localhost:8001")
        await gm.create_graph({"name": "g1"})
        await gm.create_graph({"name": "g2"})
        graphs = gm.list_graphs()
        assert len(graphs) == 2

    @pytest.mark.asyncio
    async def test_run_graph_not_found(self):
        """run_graph raises GraphExecutionError for unknown graph."""
        gm = GraphManager(gateway_url="http://localhost:8001")
        with pytest.raises(GraphExecutionError, match="not found"):
            await gm.run_graph("nonexistent", {"messages": []})

    @pytest.mark.asyncio
    async def test_run_graph_success(self):
        """run_graph executes a graph and returns result."""
        gm = GraphManager(gateway_url="http://localhost:8001")
        graph_id = await gm.create_graph({"name": "test"})

        thread_resp = MagicMock()
        thread_resp.status_code = 201
        thread_resp.json.return_value = {"thread_id": "t_1"}

        run_resp = MagicMock()
        run_resp.status_code = 200
        run_resp.json.return_value = {"run_id": "r_1"}

        with patch.object(gm._client, "post", new_callable=AsyncMock, side_effect=[thread_resp, run_resp]):
            result = await gm.run_graph(graph_id, {"messages": [{"role": "user", "content": "hi"}]})
            assert result["status"] == "completed"
            assert result["graph_id"] == graph_id

    @pytest.mark.asyncio
    async def test_run_graph_thread_creation_fails(self):
        """run_graph handles thread creation failure."""
        gm = GraphManager(gateway_url="http://localhost:8001")
        graph_id = await gm.create_graph({"name": "test"})

        thread_resp = MagicMock()
        thread_resp.status_code = 500

        with patch.object(gm._client, "post", new_callable=AsyncMock, return_value=thread_resp):
            result = await gm.run_graph(graph_id, {"messages": []})
            assert result["status"] == "error"

    @pytest.mark.asyncio
    async def test_run_graph_http_error(self):
        """run_graph handles HTTP errors gracefully."""
        gm = GraphManager(gateway_url="http://localhost:8001")
        graph_id = await gm.create_graph({"name": "test"})

        with patch.object(
            gm._client, "post", new_callable=AsyncMock, side_effect=httpx.ConnectError("refused")
        ):
            result = await gm.run_graph(graph_id, {"messages": []})
            assert result["status"] == "unavailable"


class TestMemoryManager:
    """Test MemoryManager functionality."""

    @pytest.mark.asyncio
    async def test_get_memory_success(self):
        """get_memory returns memory data."""
        mm = MemoryManager(gateway_url="http://localhost:8001")
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"facts": []}
        mock_response.raise_for_status = MagicMock()
        with patch.object(mm._client, "get", new_callable=AsyncMock, return_value=mock_response):
            result = await mm.get_memory()
            assert result["data_source"] == "deerflow_memory"

    @pytest.mark.asyncio
    async def test_get_memory_unavailable(self):
        """get_memory handles unavailable service."""
        mm = MemoryManager(gateway_url="http://localhost:8001")
        with patch.object(
            mm._client, "get", new_callable=AsyncMock, side_effect=httpx.ConnectError("refused")
        ):
            result = await mm.get_memory()
            assert result["status"] == "unavailable"

    @pytest.mark.asyncio
    async def test_create_fact_success(self):
        """create_fact returns fact data."""
        mm = MemoryManager(gateway_url="http://localhost:8001")
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"fact_id": "f_1", "content": "test"}
        mock_response.raise_for_status = MagicMock()
        with patch.object(mm._client, "post", new_callable=AsyncMock, return_value=mock_response):
            result = await mm.create_fact("test fact", category="context", confidence=0.9)
            assert result["data_source"] == "deerflow_memory"

    @pytest.mark.asyncio
    async def test_create_fact_unavailable(self):
        """create_fact handles unavailable service."""
        mm = MemoryManager(gateway_url="http://localhost:8001")
        with patch.object(
            mm._client, "post", new_callable=AsyncMock, side_effect=httpx.ConnectError("refused")
        ):
            result = await mm.create_fact("test")
            assert result["status"] == "unavailable"

    @pytest.mark.asyncio
    async def test_delete_fact_success(self):
        """delete_fact returns result."""
        mm = MemoryManager(gateway_url="http://localhost:8001")
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"deleted": True}
        mock_response.raise_for_status = MagicMock()
        with patch.object(mm._client, "delete", new_callable=AsyncMock, return_value=mock_response):
            result = await mm.delete_fact("f_1")
            assert result["data_source"] == "deerflow_memory"

    @pytest.mark.asyncio
    async def test_delete_fact_unavailable(self):
        """delete_fact handles unavailable service."""
        mm = MemoryManager(gateway_url="http://localhost:8001")
        with patch.object(
            mm._client, "delete", new_callable=AsyncMock, side_effect=httpx.ConnectError("refused")
        ):
            result = await mm.delete_fact("f_1")
            assert result["status"] == "unavailable"

    @pytest.mark.asyncio
    async def test_get_config_success(self):
        """get_config returns memory configuration."""
        mm = MemoryManager(gateway_url="http://localhost:8001")
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"provider": "redis"}
        mock_response.raise_for_status = MagicMock()
        with patch.object(mm._client, "get", new_callable=AsyncMock, return_value=mock_response):
            result = await mm.get_config()
            assert result["data_source"] == "deerflow_memory"

    @pytest.mark.asyncio
    async def test_get_config_unavailable(self):
        """get_config handles unavailable service."""
        mm = MemoryManager(gateway_url="http://localhost:8001")
        with patch.object(
            mm._client, "get", new_callable=AsyncMock, side_effect=httpx.ConnectError("refused")
        ):
            result = await mm.get_config()
            assert result["status"] == "unavailable"


class TestDeerFlowBridgeConvenienceMethods:
    """Test DeerFlowBridge convenience pass-through methods."""

    @pytest.mark.asyncio
    async def test_list_channels(self, deerflow_bridge_open):
        """list_channels delegates to ChannelManager."""
        with patch.object(
            deerflow_bridge_open.channels, "list_channels", new_callable=AsyncMock, return_value=["discord"]
        ):
            result = await deerflow_bridge_open.list_channels()
            assert result == ["discord"]

    @pytest.mark.asyncio
    async def test_get_channel(self, deerflow_bridge_open):
        """get_channel delegates to ChannelManager."""
        with patch.object(
            deerflow_bridge_open.channels, "get_channel", new_callable=AsyncMock, return_value={"status": "running"}
        ):
            result = await deerflow_bridge_open.get_channel("discord")
            assert result["status"] == "running"

    @pytest.mark.asyncio
    async def test_send_message_through_middleware(self, deerflow_bridge_open):
        """send_message passes through middleware chain."""
        mock_result = {"status": "sent", "channel": "discord"}
        with patch.object(
            deerflow_bridge_open.channels, "send_message", new_callable=AsyncMock, return_value=mock_result
        ):
            result = await deerflow_bridge_open.send_message("discord", "hello")
            assert result["status"] == "sent"

    @pytest.mark.asyncio
    async def test_create_graph(self, deerflow_bridge_open):
        """create_graph delegates to GraphManager."""
        with patch.object(
            deerflow_bridge_open.graphs, "create_graph", new_callable=AsyncMock, return_value="graph_abc123"
        ):
            result = await deerflow_bridge_open.create_graph({"name": "test"})
            assert result == "graph_abc123"

    @pytest.mark.asyncio
    async def test_run_graph_through_middleware(self, deerflow_bridge_open):
        """run_graph passes through middleware chain."""
        mock_result = {"status": "completed", "graph_id": "g1"}
        with patch.object(
            deerflow_bridge_open.graphs, "run_graph", new_callable=AsyncMock, return_value=mock_result
        ):
            result = await deerflow_bridge_open.run_graph("g1", {"messages": []})
            assert result["status"] == "completed"


class TestDeerFlowBridgeHealthCheck:
    """Test DeerFlowBridge health_check."""

    @pytest.mark.asyncio
    async def test_health_check_success(self, deerflow_bridge_open):
        """health_check returns ok status."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"service_running": True, "channels": {"discord": {}}}
        mock_response.raise_for_status = MagicMock()
        with patch.object(deerflow_bridge_open._http_client, "get", new_callable=AsyncMock, return_value=mock_response):
            result = await deerflow_bridge_open.health_check()
            assert result["status"] == "ok"
            assert result["service_running"] is True
            assert result["channel_count"] == 1

    @pytest.mark.asyncio
    async def test_health_check_unavailable(self, deerflow_bridge_open):
        """health_check returns unavailable on service down."""
        with patch.object(
            deerflow_bridge_open._http_client,
            "get",
            new_callable=AsyncMock,
            side_effect=httpx.ConnectError("refused"),
        ):
            result = await deerflow_bridge_open.health_check()
            assert result["status"] == "unavailable"


class TestDeerFlowBridgeErrorHierarchy:
    """Test DeerFlow error exception hierarchy."""

    def test_deerflow_unavailable_error(self):
        """DeerFlowUnavailableError is a DeerFlowBridgeError."""
        assert issubclass(DeerFlowUnavailableError, DeerFlowBridgeError)

    def test_channel_not_found_error(self):
        """ChannelNotFoundError is a DeerFlowBridgeError."""
        assert issubclass(ChannelNotFoundError, DeerFlowBridgeError)

    def test_graph_execution_error(self):
        """GraphExecutionError is a DeerFlowBridgeError."""
        assert issubclass(GraphExecutionError, DeerFlowBridgeError)

    def test_middleware_error(self):
        """MiddlewareError is a DeerFlowBridgeError."""
        assert issubclass(MiddlewareError, DeerFlowBridgeError)


class TestDeerFlowBridgeLifecycle:
    """Test DeerFlowBridge connection lifecycle."""

    @pytest.mark.asyncio
    async def test_close(self, deerflow_bridge):
        """close() closes the shared HTTP client."""
        with patch.object(deerflow_bridge._http_client, "aclose", new_callable=AsyncMock) as mock_close:
            await deerflow_bridge.close()
            mock_close.assert_awaited_once()


class TestMiddlewareABC:
    """Test Middleware abstract class enforcement."""

    def test_cannot_instantiate_directly(self):
        """Middleware is abstract; cannot be instantiated."""
        with pytest.raises(TypeError):
            Middleware()  # type: ignore[abstract]

    def test_concrete_subclass_works(self):
        """A concrete subclass can be instantiated."""

        class ConcreteMiddleware(Middleware):
            async def process_request(self, request):
                return request

            async def process_response(self, response):
                return response

        mw = ConcreteMiddleware()
        assert isinstance(mw, Middleware)

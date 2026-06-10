"""
Comprehensive Test Suite for New Agents (Cluster 1)
Tests GitHubAgent, VoiceAgent, Web3Plugin, and AgentWatcherAgent

Made with love by Mulky Malikul Dhaher in Indonesia
"""

import pytest
import asyncio
import json
import os
import sys
import tempfile
from unittest.mock import Mock, patch, AsyncMock, MagicMock
from datetime import datetime

# Ensure project root is in path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


# =============================================================================
# FIXTURES
# =============================================================================

@pytest.fixture
def github_agent_instance():
    """Create a fresh GitHubAgent instance for each test."""
    from agents.github_agent import GitHubAgent
    with patch.dict(os.environ, {"GITHUB_TOKEN": "", "GITHUB_DEFAULT_OWNER": "", "GITHUB_DEFAULT_REPO": ""}):
        return GitHubAgent()


@pytest.fixture
def github_agent_with_token():
    """Create a GitHubAgent instance with a fake token."""
    from agents.github_agent import GitHubAgent
    with patch.dict(os.environ, {"GITHUB_TOKEN": "ghp_test123", "GITHUB_DEFAULT_OWNER": "testowner", "GITHUB_DEFAULT_REPO": "testrepo"}):
        return GitHubAgent()


@pytest.fixture
def voice_agent_instance():
    """Create a fresh VoiceAgent instance for each test."""
    from agents.voice_agent import VoiceAgent
    with patch.dict(os.environ, {
        "OPENAI_API_KEY": "",
        "VOICE_STT_PROVIDER": "openai",
        "VOICE_TTS_PROVIDER": "openai",
    }):
        return VoiceAgent()


@pytest.fixture
def web3_plugin_instance():
    """Create a fresh Web3Plugin instance for each test."""
    from agents.web3_plugin import Web3Plugin
    with patch.dict(os.environ, {"WEB3_DEFAULT_NETWORK": "ethereum"}):
        return Web3Plugin()


@pytest.fixture
def agent_watcher_instance():
    """Create a fresh AgentWatcherAgent instance for each test."""
    from agents.agent_watcher import AgentWatcherAgent
    with patch.dict(os.environ, {
        "WATCHER_HEARTBEAT_TIMEOUT": "30",
        "WATCHER_MAX_ERROR_RATE": "0.5",
        "WATCHER_MAX_RESPONSE_TIME": "10.0",
        "WATCHER_RESTART_COOLDOWN": "300",
        "WATCHER_MAX_RESTART_ATTEMPTS": "3",
        "WATCHER_CHECK_INTERVAL": "60",
    }):
        watcher = AgentWatcherAgent()
        # Clear any state loaded from disk
        watcher._registered_agents = {}
        watcher._agent_health = {}
        watcher._alerts = []
        return watcher


@pytest.fixture
def sample_audio_bytes():
    """Create minimal valid WAV audio bytes for testing."""
    import struct
    import wave
    import io

    buf = io.BytesIO()
    with wave.open(buf, 'wb') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(16000)
        # 0.1 seconds of silence
        frames = struct.pack('<' + 'h' * 1600, *([0] * 1600))
        wf.writeframes(frames)
    return buf.getvalue()


@pytest.fixture
def temp_wav_file(sample_audio_bytes):
    """Create a temporary WAV file for testing."""
    with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as f:
        f.write(sample_audio_bytes)
        path = f.name
    yield path
    if os.path.exists(path):
        os.unlink(path)


# =============================================================================
# GitHubAgent TESTS
# =============================================================================

class TestGitHubAgent:
    """Test GitHubAgent functionality"""

    def test_initialization(self, github_agent_instance):
        """Check agent_id, name, status, capabilities, token config"""
        agent = github_agent_instance
        assert agent.agent_id == "github_agent"
        assert agent.name == "GitHub Agent"
        assert agent.status == "ready"
        assert "git_operations" in agent.capabilities
        assert "repo_management" in agent.capabilities
        assert "ci_cd" in agent.capabilities
        assert "code_sync" in agent.capabilities
        assert "pull_requests" in agent.capabilities
        assert "issue_tracking" in agent.capabilities
        assert "file_operations" in agent.capabilities
        assert "branch_management" in agent.capabilities
        assert agent.token == ""
        assert agent.default_owner == ""
        assert agent.default_repo == ""

    def test_initialization_with_token(self, github_agent_with_token):
        """Check token is configured from environment"""
        agent = github_agent_with_token
        assert agent.token == "ghp_test123"
        assert agent.default_owner == "testowner"
        assert agent.default_repo == "testrepo"

    def test_build_headers_without_token(self, github_agent_instance):
        """Check headers without token"""
        agent = github_agent_instance
        headers = agent._build_headers()
        assert headers["Accept"] == "application/vnd.github+json"
        assert headers["X-GitHub-Api-Version"] == "2022-11-28"
        assert "Authorization" not in headers

    def test_build_headers_with_token(self, github_agent_with_token):
        """Check headers with token"""
        agent = github_agent_with_token
        headers = agent._build_headers()
        assert headers["Accept"] == "application/vnd.github+json"
        assert headers["X-GitHub-Api-Version"] == "2022-11-28"
        assert "Authorization" in headers
        assert headers["Authorization"] == "Bearer ghp_test123"

    @pytest.mark.asyncio
    async def test_process_task_unknown_action(self, github_agent_instance):
        """Should return error for unknown actions"""
        agent = github_agent_instance
        result = await agent.process_task({"action": "nonexistent_action"})
        assert result["success"] is False
        assert "Unknown action" in result["error"]

    @pytest.mark.asyncio
    async def test_process_task_list_repos_no_aiohttp(self, github_agent_instance):
        """Mock aiohttp unavailable - list_repos should fail gracefully"""
        agent = github_agent_instance
        with patch('agents.github_agent._AIOHTTP_AVAILABLE', False):
            result = await agent.process_task({"action": "list_repos"})
            assert result["success"] is False
            assert "aiohttp" in result["error"].lower()

    def test_get_performance_metrics(self, github_agent_instance):
        """Check metrics structure"""
        agent = github_agent_instance
        metrics = agent.get_performance_metrics()
        assert metrics["agent_id"] == "github_agent"
        assert metrics["status"] == "ready"
        assert "capabilities" in metrics
        assert "api_stats" in metrics
        assert "total_requests" in metrics["api_stats"]
        assert "successful_requests" in metrics["api_stats"]
        assert "failed_requests" in metrics["api_stats"]
        assert "rate_limit_waits" in metrics["api_stats"]
        assert "avg_response_time" in metrics["api_stats"]
        assert "rate_limit_remaining" in metrics
        assert "token_configured" in metrics
        assert "default_owner" in metrics

    def test_create_error_response(self, github_agent_instance):
        """Check error response format"""
        agent = github_agent_instance
        error = agent._create_error_response("test error message")
        assert error["success"] is False
        assert error["error"] == "test error message"
        assert "timestamp" in error
        assert error["agent"] == "github_agent"
        # Creating error response should increment failed_requests
        assert agent._stats["failed_requests"] >= 1

    def test_api_base_constant(self, github_agent_instance):
        """Check API base URL is set correctly"""
        assert github_agent_instance.API_BASE == "https://api.github.com"

    def test_rate_limit_tracking_initial(self, github_agent_instance):
        """Check initial rate limit state"""
        agent = github_agent_instance
        assert agent._rate_limit_remaining == 5000
        assert agent._rate_limit_reset is None

    def test_update_avg_response_time(self, github_agent_instance):
        """Check response time averaging"""
        agent = github_agent_instance
        # Simulate: 1st request already recorded with avg 0.5s
        # Now 2nd request takes 1.0s
        # avg = (0.5 * (2-1) + 1.0) / 2 = 0.75
        agent._stats["total_requests"] = 2
        agent._stats["avg_response_time"] = 0.5
        agent._update_avg_response_time(1.0)
        assert agent._stats["avg_response_time"] == 0.75

    @pytest.mark.asyncio
    async def test_list_branches_missing_params(self, github_agent_instance):
        """Test list_branches requires owner and repo"""
        agent = github_agent_instance
        with patch('agents.github_agent._AIOHTTP_AVAILABLE', False):
            # No owner/repo provided, defaults are empty
            result = await agent._list_branches({})
            assert result["success"] is False
            assert "owner and repo are required" in result["error"]

    @pytest.mark.asyncio
    async def test_list_commits_missing_params(self, github_agent_instance):
        """Test list_commits requires owner and repo"""
        agent = github_agent_instance
        with patch('agents.github_agent._AIOHTTP_AVAILABLE', False):
            result = await agent._list_commits({})
            assert result["success"] is False
            assert "owner and repo are required" in result["error"]

    @pytest.mark.asyncio
    async def test_get_file_missing_params(self, github_agent_instance):
        """Test get_file requires owner, repo, and path"""
        agent = github_agent_instance
        result = await agent._get_file({})
        assert result["success"] is False
        assert "owner, repo, and path are required" in result["error"]

    @pytest.mark.asyncio
    async def test_create_file_missing_params(self, github_agent_instance):
        """Test create_file requires owner, repo, and path"""
        agent = github_agent_instance
        result = await agent._create_file({})
        assert result["success"] is False
        assert "owner, repo, and path are required" in result["error"]

    @pytest.mark.asyncio
    async def test_search_code_missing_query(self, github_agent_instance):
        """Test search_code requires query"""
        agent = github_agent_instance
        result = await agent._search_code({})
        assert result["success"] is False
        assert "query is required" in result["error"]

    @pytest.mark.asyncio
    async def test_create_pull_request_missing_params(self, github_agent_instance):
        """Test create_pull_request requires owner, repo, title, head"""
        agent = github_agent_instance
        result = await agent._create_pull_request({})
        assert result["success"] is False
        assert "owner, repo, title, and head branch are required" in result["error"]

    @pytest.mark.asyncio
    async def test_create_issue_missing_params(self, github_agent_instance):
        """Test create_issue requires owner, repo, and title"""
        agent = github_agent_instance
        result = await agent._create_issue({})
        assert result["success"] is False
        assert "owner, repo, and title are required" in result["error"]


# =============================================================================
# VoiceAgent TESTS
# =============================================================================

class TestVoiceAgent:
    """Test VoiceAgent functionality"""

    def test_initialization(self, voice_agent_instance):
        """Check agent_id, name, status, capabilities, providers"""
        agent = voice_agent_instance
        assert agent.agent_id == "voice_agent"
        assert agent.name == "Voice Agent"
        assert agent.status == "ready"
        assert "speech_to_text" in agent.capabilities
        assert "text_to_speech" in agent.capabilities
        assert "voice_commands" in agent.capabilities
        assert "audio_processing" in agent.capabilities
        assert "command_routing" in agent.capabilities
        assert "stream_processing" in agent.capabilities
        assert agent.stt_provider == "openai"
        assert agent.tts_provider == "openai"

    @pytest.mark.asyncio
    async def test_process_task_unknown_action(self, voice_agent_instance):
        """Should return error for unknown actions"""
        agent = voice_agent_instance
        result = await agent.process_task({"action": "nonexistent_action"})
        assert result["success"] is False
        assert "Unknown action" in result["error"]

    @pytest.mark.asyncio
    async def test_speech_to_text_no_audio(self, voice_agent_instance):
        """Should return error when no audio provided"""
        agent = voice_agent_instance
        result = await agent.process_task({"action": "speech_to_text"})
        assert result["success"] is False
        assert "No audio data provided" in result["error"]

    @pytest.mark.asyncio
    async def test_speech_to_text_invalid_base64(self, voice_agent_instance):
        """Should return error for invalid base64 audio"""
        agent = voice_agent_instance
        result = await agent.process_task({
            "action": "speech_to_text",
            "audio_base64": "not-valid-base64!!!"
        })
        assert result["success"] is False
        assert "Invalid base64" in result["error"]

    @pytest.mark.asyncio
    async def test_speech_to_text_file_not_found(self, voice_agent_instance):
        """Should return error for missing audio file"""
        agent = voice_agent_instance
        result = await agent.process_task({
            "action": "speech_to_text",
            "audio_file": "/nonexistent/path/audio.wav"
        })
        assert result["success"] is False
        assert "Audio file not found" in result["error"]

    @pytest.mark.asyncio
    async def test_parse_command(self, voice_agent_instance):
        """Test command parsing with known keywords"""
        agent = voice_agent_instance
        result = await agent.process_task({
            "action": "parse_command",
            "text": "deploy my application"
        })
        assert result["success"] is True
        assert result["command"] == "deploy"
        assert result["routed_agent"] == "deploy_manager"
        assert result["confidence"] > 0.0

    @pytest.mark.asyncio
    async def test_parse_command_create(self, voice_agent_instance):
        """Test parsing 'create' command"""
        agent = voice_agent_instance
        result = await agent.process_task({
            "action": "parse_command",
            "text": "create a new project"
        })
        assert result["success"] is True
        assert result["command"] == "create"
        assert result["routed_agent"] == "dev_engine"

    @pytest.mark.asyncio
    async def test_parse_command_run(self, voice_agent_instance):
        """Test parsing 'run' command"""
        agent = voice_agent_instance
        result = await agent.process_task({
            "action": "parse_command",
            "text": "run the tests"
        })
        assert result["success"] is True
        assert result["command"] == "run"
        assert result["routed_agent"] == "cybershell"

    @pytest.mark.asyncio
    async def test_extract_command_unknown(self, voice_agent_instance):
        """Test with unknown command"""
        agent = voice_agent_instance
        result = agent._extract_command("blah blah nothing matches")
        assert result["command"] == "unknown"
        assert result["routed_agent"] is None
        assert result["confidence"] == 0.0

    @pytest.mark.asyncio
    async def test_parse_command_no_text(self, voice_agent_instance):
        """Test parse_command with empty text"""
        agent = voice_agent_instance
        result = await agent.process_task({
            "action": "parse_command",
            "text": ""
        })
        assert result["success"] is False
        assert "No text provided" in result["error"]

    @pytest.mark.asyncio
    async def test_list_voices(self, voice_agent_instance):
        """Check voice listing returns known voices"""
        agent = voice_agent_instance
        result = await agent.process_task({"action": "list_voices"})
        assert result["success"] is True
        assert "voices" in result
        assert len(result["voices"]) > 0
        # Check for known OpenAI voices
        voice_ids = [v["id"] for v in result["voices"]]
        assert "alloy" in voice_ids
        assert "echo" in voice_ids
        assert "fable" in voice_ids
        assert "onyx" in voice_ids
        assert "nova" in voice_ids
        assert "shimmer" in voice_ids
        assert "default_voice" in result
        assert "tts_provider" in result

    @pytest.mark.asyncio
    async def test_configure(self, voice_agent_instance):
        """Test configuration updates"""
        agent = voice_agent_instance
        result = await agent.process_task({
            "action": "configure",
            "stt_provider": "local",
            "tts_provider": "local",
            "default_voice": "echo",
            "sample_rate": 48000,
        })
        assert result["success"] is True
        config = result["configuration"]
        assert config["stt_provider"] == "local"
        assert config["tts_provider"] == "local"
        assert config["default_voice"] == "echo"
        assert config["sample_rate"] == 48000

    @pytest.mark.asyncio
    async def test_configure_partial(self, voice_agent_instance):
        """Test partial configuration update"""
        agent = voice_agent_instance
        result = await agent.process_task({
            "action": "configure",
            "default_voice": "fable",
        })
        assert result["success"] is True
        assert result["configuration"]["default_voice"] == "fable"
        # Other values should remain default
        assert result["configuration"]["stt_provider"] == "openai"

    def test_get_performance_metrics(self, voice_agent_instance):
        """Check metrics structure"""
        agent = voice_agent_instance
        metrics = agent.get_performance_metrics()
        assert metrics["agent_id"] == "voice_agent"
        assert metrics["status"] == "ready"
        assert "capabilities" in metrics
        assert "stats" in metrics
        assert "total_tasks" in metrics["stats"]
        assert "successful_tasks" in metrics["stats"]
        assert "failed_tasks" in metrics["stats"]
        assert "stt_operations" in metrics["stats"]
        assert "tts_operations" in metrics["stats"]
        assert "commands_parsed" in metrics["stats"]
        assert "avg_processing_time" in metrics["stats"]
        assert "stt_provider" in metrics
        assert "tts_provider" in metrics
        assert "openai_configured" in metrics
        assert "cache_size" in metrics

    def test_command_routes_loaded(self, voice_agent_instance):
        """Check command routes are loaded properly"""
        agent = voice_agent_instance
        assert "create" in agent.command_routes
        assert "deploy" in agent.command_routes
        assert "build" in agent.command_routes
        assert "design" in agent.command_routes
        assert "run" in agent.command_routes
        assert "execute" in agent.command_routes
        assert "sync" in agent.command_routes
        assert "status" in agent.command_routes
        assert "commit" in agent.command_routes
        assert "monitor" in agent.command_routes
        assert "help" in agent.command_routes

    def test_hash_audio(self, voice_agent_instance):
        """Test audio hashing for cache"""
        agent = voice_agent_instance
        hash1 = agent._hash_audio(b"test audio data")
        hash2 = agent._hash_audio(b"test audio data")
        hash3 = agent._hash_audio(b"different data")
        assert hash1 == hash2
        assert hash1 != hash3
        assert len(hash1) == 64  # SHA-256 hex digest

    @pytest.mark.asyncio
    async def test_text_to_speech_no_text(self, voice_agent_instance):
        """Test TTS with no text returns error"""
        agent = voice_agent_instance
        result = await agent.process_task({
            "action": "text_to_speech",
            "text": ""
        })
        assert result["success"] is False
        assert "No text provided" in result["error"]

    @pytest.mark.asyncio
    async def test_process_audio_no_file(self, voice_agent_instance):
        """Test audio processing with no file returns error"""
        agent = voice_agent_instance
        result = await agent.process_task({
            "action": "process_audio",
        })
        assert result["success"] is False
        assert "No audio_file path provided" in result["error"]

    @pytest.mark.asyncio
    async def test_process_audio_file_not_found(self, voice_agent_instance):
        """Test audio processing with nonexistent file returns error"""
        agent = voice_agent_instance
        result = await agent.process_task({
            "action": "process_audio",
            "audio_file": "/nonexistent/audio.wav"
        })
        assert result["success"] is False
        assert "File not found" in result["error"]

    @pytest.mark.asyncio
    async def test_process_audio_metadata(self, voice_agent_instance, temp_wav_file):
        """Test audio metadata extraction"""
        agent = voice_agent_instance
        result = await agent.process_task({
            "action": "process_audio",
            "audio_file": temp_wav_file,
            "operation": "metadata"
        })
        assert result["success"] is True
        assert "file_size" in result
        assert result["extension"] == ".wav"
        assert "channels" in result
        assert "sample_width" in result
        assert "frame_rate" in result

    @pytest.mark.asyncio
    async def test_process_audio_validate(self, voice_agent_instance, temp_wav_file):
        """Test audio validation"""
        agent = voice_agent_instance
        result = await agent.process_task({
            "action": "process_audio",
            "audio_file": temp_wav_file,
            "operation": "validate"
        })
        assert result["success"] is True
        assert result["valid"] is True

    @pytest.mark.asyncio
    async def test_route_command_unknown(self, voice_agent_instance):
        """Test routing an unknown command"""
        agent = voice_agent_instance
        result = await agent.process_task({
            "action": "route_command",
            "text": "xyzzy nothing"
        })
        assert result["success"] is False
        assert "Could not determine target agent" in result.get("error", "") or "Unknown action" in result.get("error", "")


# =============================================================================
# Web3Plugin TESTS
# =============================================================================

class TestWeb3Plugin:
    """Test Web3Plugin functionality"""

    def test_initialization(self, web3_plugin_instance):
        """Check agent_id, name, status, capabilities, default_network"""
        agent = web3_plugin_instance
        assert agent.agent_id == "web3_plugin"
        assert agent.name == "Web3 Agent"
        assert agent.status == "ready"
        assert "smart_contracts" in agent.capabilities
        assert "blockchain" in agent.capabilities
        assert "defi" in agent.capabilities
        assert "nft" in agent.capabilities
        assert "wallet_queries" in agent.capabilities
        assert "gas_estimation" in agent.capabilities
        assert "token_info" in agent.capabilities
        assert "multi_chain" in agent.capabilities
        assert agent.default_network == "ethereum"

    @pytest.mark.asyncio
    async def test_process_task_unknown_action(self, web3_plugin_instance):
        """Should return error for unknown actions"""
        agent = web3_plugin_instance
        result = await agent.process_task({"action": "nonexistent_action"})
        assert result["success"] is False
        assert "Unknown action" in result["error"]

    @pytest.mark.asyncio
    async def test_get_balance_no_address(self, web3_plugin_instance):
        """Should return error when no address provided"""
        agent = web3_plugin_instance
        result = await agent.process_task({"action": "get_balance"})
        assert result["success"] is False
        assert "address is required" in result["error"]

    @pytest.mark.asyncio
    async def test_get_balance_no_web3(self, web3_plugin_instance):
        """Should handle missing web3 gracefully"""
        agent = web3_plugin_instance
        with patch('agents.web3_plugin._WEB3_AVAILABLE', False):
            result = await agent.process_task({
                "action": "get_balance",
                "address": "0x742d35Cc6634C0532925a3b844Bc9e7595f2bD18"
            })
            assert result["success"] is False
            assert "Web3 not available" in result["error"]

    @pytest.mark.asyncio
    async def test_get_network_info_no_web3(self, web3_plugin_instance):
        """Should handle missing web3 gracefully"""
        agent = web3_plugin_instance
        with patch('agents.web3_plugin._WEB3_AVAILABLE', False):
            result = await agent.process_task({
                "action": "get_network_info",
            })
            assert result["success"] is False
            assert "Web3 not available" in result["error"]

    @pytest.mark.asyncio
    async def test_list_networks(self, web3_plugin_instance):
        """Check network listing works even without web3 installed"""
        agent = web3_plugin_instance
        with patch('agents.web3_plugin._WEB3_AVAILABLE', False):
            result = await agent.process_task({"action": "list_networks"})
            assert result["success"] is True
            assert "networks" in result
            assert result["total_networks"] > 0
            assert "default_network" in result
            # Check that known networks are included
            network_names = [n["name"] for n in result["networks"]]
            assert "ethereum" in network_names
            assert "polygon" in network_names
            assert "bsc" in network_names

    def test_list_networks_sync(self, web3_plugin_instance):
        """Test synchronous _list_networks method"""
        agent = web3_plugin_instance
        with patch('agents.web3_plugin._WEB3_AVAILABLE', False):
            result = agent._list_networks({})
            assert result["success"] is True
            assert len(result["networks"]) > 0
            # Each network should have expected fields
            for net in result["networks"]:
                assert "name" in net
                assert "chain_id" in net
                assert "currency" in net
                assert "explorer" in net

    def test_serialize_contract_result_int_small(self, web3_plugin_instance):
        """Test serialization of small integer"""
        agent = web3_plugin_instance
        result = agent._serialize_contract_result(42)
        assert result == 42

    def test_serialize_contract_result_int_large(self, web3_plugin_instance):
        """Test serialization of large integer (>2^53)"""
        agent = web3_plugin_instance
        large_int = 2**56
        result = agent._serialize_contract_result(large_int)
        assert isinstance(result, dict)
        assert "raw" in result
        assert "hex" in result
        assert result["raw"] == large_int

    def test_serialize_contract_result_bytes(self, web3_plugin_instance):
        """Test serialization of bytes"""
        agent = web3_plugin_instance
        result = agent._serialize_contract_result(b'\x01\x02\x03')
        assert result == "010203"

    def test_serialize_contract_result_bool(self, web3_plugin_instance):
        """Test serialization of bool"""
        agent = web3_plugin_instance
        assert agent._serialize_contract_result(True) is True
        assert agent._serialize_contract_result(False) is False

    def test_serialize_contract_result_list(self, web3_plugin_instance):
        """Test serialization of list"""
        agent = web3_plugin_instance
        result = agent._serialize_contract_result([1, 2, 3])
        assert result == [1, 2, 3]

    def test_serialize_contract_result_tuple(self, web3_plugin_instance):
        """Test serialization of tuple (converts to list)"""
        agent = web3_plugin_instance
        result = agent._serialize_contract_result((1, 2, 3))
        assert result == [1, 2, 3]

    def test_serialize_contract_result_dict(self, web3_plugin_instance):
        """Test serialization of dict"""
        agent = web3_plugin_instance
        result = agent._serialize_contract_result({"key": "value", "num": 42})
        assert result == {"key": "value", "num": 42}

    def test_serialize_contract_result_nested(self, web3_plugin_instance):
        """Test serialization of nested structures"""
        agent = web3_plugin_instance
        data = {
            "values": [1, b'\xab\xcd', 2**60],
            "nested": {"inner": True}
        }
        result = agent._serialize_contract_result(data)
        assert result["values"][0] == 1
        assert result["values"][1] == "abcd"
        assert isinstance(result["values"][2], dict)  # large int
        assert result["nested"]["inner"] is True

    def test_serialize_contract_result_string(self, web3_plugin_instance):
        """Test serialization of string (pass-through)"""
        agent = web3_plugin_instance
        result = agent._serialize_contract_result("hello")
        assert result == "hello"

    def test_get_performance_metrics(self, web3_plugin_instance):
        """Check metrics structure"""
        agent = web3_plugin_instance
        metrics = agent.get_performance_metrics()
        assert metrics["agent_id"] == "web3_plugin"
        assert metrics["status"] == "ready"
        assert "capabilities" in metrics
        assert "stats" in metrics
        assert "total_tasks" in metrics["stats"]
        assert "successful_tasks" in metrics["stats"]
        assert "failed_tasks" in metrics["stats"]
        assert "rpc_calls" in metrics["stats"]
        assert "avg_response_time" in metrics["stats"]
        assert "default_network" in metrics
        assert "web3_available" in metrics
        assert "configured_networks" in metrics

    @pytest.mark.asyncio
    async def test_get_token_balance_no_address(self, web3_plugin_instance):
        """Should return error when no address provided"""
        agent = web3_plugin_instance
        result = await agent.process_task({
            "action": "get_token_balance",
        })
        assert result["success"] is False
        assert "address is required" in result["error"]

    @pytest.mark.asyncio
    async def test_get_token_info_no_address(self, web3_plugin_instance):
        """Should return error when no token_address provided"""
        agent = web3_plugin_instance
        result = await agent.process_task({
            "action": "get_token_info",
        })
        assert result["success"] is False
        assert "token_address is required" in result["error"]

    @pytest.mark.asyncio
    async def test_get_transaction_no_hash(self, web3_plugin_instance):
        """Should return error when no tx_hash provided"""
        agent = web3_plugin_instance
        result = await agent.process_task({
            "action": "get_transaction",
        })
        assert result["success"] is False
        assert "tx_hash is required" in result["error"]

    @pytest.mark.asyncio
    async def test_estimate_gas_no_params(self, web3_plugin_instance):
        """Should return error when no transaction params provided"""
        agent = web3_plugin_instance
        result = await agent.process_task({
            "action": "estimate_gas",
        })
        assert result["success"] is False
        assert "transaction parameters are required" in result["error"]

    @pytest.mark.asyncio
    async def test_call_contract_missing_params(self, web3_plugin_instance):
        """Should return error when contract_address or function_name missing"""
        agent = web3_plugin_instance
        result = await agent.process_task({
            "action": "call_contract",
        })
        assert result["success"] is False
        assert "contract_address and function_name are required" in result["error"]

    @pytest.mark.asyncio
    async def test_defi_read_no_protocol(self, web3_plugin_instance):
        """Should return error when no protocol specified"""
        agent = web3_plugin_instance
        result = await agent.process_task({
            "action": "defi_read",
        })
        assert result["success"] is False
        assert "protocol name or contract_address" in result["error"]

    @pytest.mark.asyncio
    async def test_get_ens_no_params(self, web3_plugin_instance):
        """Should return error when no name or address provided"""
        agent = web3_plugin_instance
        result = await agent.process_task({
            "action": "get_ens",
        })
        assert result["success"] is False
        assert "name or address is required" in result["error"]

    def test_network_defaults_structure(self):
        """Check NETWORK_DEFAULTS has all expected networks"""
        from agents.web3_plugin import NETWORK_DEFAULTS
        expected_networks = ["ethereum", "goerli", "sepolia", "polygon", "bsc", "arbitrum", "optimism", "avalanche"]
        for net in expected_networks:
            assert net in NETWORK_DEFAULTS
            assert "chain_id" in NETWORK_DEFAULTS[net]
            assert "currency" in NETWORK_DEFAULTS[net]
            assert "rpc_env" in NETWORK_DEFAULTS[net]
            assert "rpc_default" in NETWORK_DEFAULTS[net]
            assert "explorer" in NETWORK_DEFAULTS[net]


# =============================================================================
# AgentWatcherAgent TESTS
# =============================================================================

class TestAgentWatcherAgent:
    """Test AgentWatcherAgent functionality"""

    def test_initialization(self, agent_watcher_instance):
        """Check agent_id, name, status, capabilities, config"""
        agent = agent_watcher_instance
        assert agent.agent_id == "agent_watcher"
        assert agent.name == "Agent Watcher"
        assert agent.status == "ready"
        assert "health_monitoring" in agent.capabilities
        assert "agent_diagnostics" in agent.capabilities
        assert "error_tracking" in agent.capabilities
        assert "performance_metrics" in agent.capabilities
        assert "auto_restart" in agent.capabilities
        assert "alerting" in agent.capabilities
        assert "health_reports" in agent.capabilities
        assert "agent_lifecycle" in agent.capabilities
        assert agent.heartbeat_timeout == 30
        assert agent.max_error_rate == 0.5
        assert agent.max_response_time == 10.0
        assert agent.restart_cooldown == 300
        assert agent.max_restart_attempts == 3
        assert agent.health_check_interval == 60

    @pytest.mark.asyncio
    async def test_process_task_unknown_action(self, agent_watcher_instance):
        """Should return error for unknown actions"""
        agent = agent_watcher_instance
        result = await agent.process_task({"action": "nonexistent_action"})
        assert result["success"] is False
        assert "Unknown action" in result["error"]

    @pytest.mark.asyncio
    async def test_register_agent(self, agent_watcher_instance):
        """Test manual agent registration"""
        agent = agent_watcher_instance
        # Create a mock agent to register
        mock_agent = Mock()
        mock_agent.__class__.__name__ = "MockAgent"
        result = await agent.process_task({
            "action": "register_agent",
            "agent_id": "test_agent_1",
            "instance": mock_agent,
        })
        assert result["success"] is True
        assert result["agent_id"] == "test_agent_1"
        assert "test_agent_1" in agent._registered_agents

    @pytest.mark.asyncio
    async def test_register_agent_no_id(self, agent_watcher_instance):
        """Test register_agent without agent_id returns error"""
        agent = agent_watcher_instance
        result = await agent.process_task({
            "action": "register_agent",
        })
        assert result["success"] is False
        assert "agent_id is required" in result["error"]

    @pytest.mark.asyncio
    async def test_unregister_agent(self, agent_watcher_instance):
        """Test agent unregistration"""
        agent = agent_watcher_instance
        # Register first
        mock_agent = Mock()
        mock_agent.__class__.__name__ = "MockAgent"
        agent._registered_agents["test_agent_2"] = {
            "instance": mock_agent,
            "class_name": "MockAgent",
            "discovered_at": datetime.now().isoformat(),
        }
        agent._agent_health["test_agent_2"] = {"status": "healthy"}

        # Now unregister
        result = await agent.process_task({
            "action": "unregister_agent",
            "agent_id": "test_agent_2",
        })
        assert result["success"] is True
        assert "test_agent_2" not in agent._registered_agents
        assert "test_agent_2" not in agent._agent_health

    @pytest.mark.asyncio
    async def test_unregister_agent_no_id(self, agent_watcher_instance):
        """Test unregister_agent without agent_id returns error"""
        agent = agent_watcher_instance
        result = await agent.process_task({
            "action": "unregister_agent",
        })
        assert result["success"] is False
        assert "agent_id is required" in result["error"]

    @pytest.mark.asyncio
    async def test_unregister_nonexistent_agent(self, agent_watcher_instance):
        """Test unregistering an agent that doesn't exist (should succeed)"""
        agent = agent_watcher_instance
        result = await agent.process_task({
            "action": "unregister_agent",
            "agent_id": "nonexistent_agent",
        })
        assert result["success"] is True

    @pytest.mark.asyncio
    async def test_list_agents(self, agent_watcher_instance):
        """Check agent listing"""
        agent = agent_watcher_instance
        # Register some mock agents
        for i in range(3):
            mock = Mock()
            mock.__class__.__name__ = f"MockAgent{i}"
            mock.capabilities = ["test"]
            agent._registered_agents[f"test_agent_{i}"] = {
                "instance": mock,
                "class_name": f"MockAgent{i}",
                "discovered_at": datetime.now().isoformat(),
            }

        result = await agent.process_task({"action": "list_agents"})
        assert result["success"] is True
        assert result["total_agents"] == 3
        assert len(result["agents"]) == 3
        # Each agent entry should have expected fields
        for a in result["agents"]:
            assert "agent_id" in a
            assert "class_name" in a
            assert "status" in a
            assert "consecutive_failures" in a
            assert "capabilities" in a

    @pytest.mark.asyncio
    async def test_list_agents_empty(self, agent_watcher_instance):
        """Check listing when no agents are registered"""
        agent = agent_watcher_instance
        result = await agent.process_task({"action": "list_agents"})
        assert result["success"] is True
        assert result["total_agents"] == 0
        assert result["agents"] == []

    @pytest.mark.asyncio
    async def test_get_alerts(self, agent_watcher_instance):
        """Check alert retrieval"""
        agent = agent_watcher_instance
        # Add some alerts
        agent._add_alert("agent_1", "warning", "Test warning")
        agent._add_alert("agent_2", "critical", "Test critical")
        agent._add_alert("agent_1", "info", "Test info")

        result = await agent.process_task({"action": "get_alerts"})
        assert result["success"] is True
        assert result["total"] == 3
        assert len(result["alerts"]) == 3

    @pytest.mark.asyncio
    async def test_get_alerts_filter_severity(self, agent_watcher_instance):
        """Check alert filtering by severity"""
        agent = agent_watcher_instance
        agent._add_alert("agent_1", "warning", "Test warning")
        agent._add_alert("agent_2", "critical", "Test critical")
        agent._add_alert("agent_1", "info", "Test info")

        result = await agent.process_task({
            "action": "get_alerts",
            "severity": "critical"
        })
        assert result["success"] is True
        assert result["total"] == 1
        assert result["alerts"][0]["severity"] == "critical"

    @pytest.mark.asyncio
    async def test_get_alerts_filter_agent(self, agent_watcher_instance):
        """Check alert filtering by agent_id"""
        agent = agent_watcher_instance
        agent._add_alert("agent_1", "warning", "Test warning")
        agent._add_alert("agent_2", "critical", "Test critical")
        agent._add_alert("agent_1", "info", "Test info")

        result = await agent.process_task({
            "action": "get_alerts",
            "agent_id": "agent_1"
        })
        assert result["success"] is True
        assert result["total"] == 2

    @pytest.mark.asyncio
    async def test_configure(self, agent_watcher_instance):
        """Test configuration updates"""
        agent = agent_watcher_instance
        result = await agent.process_task({
            "action": "configure",
            "heartbeat_timeout": 60,
            "max_error_rate": 0.8,
            "max_response_time": 5.0,
            "restart_cooldown": 600,
            "max_restart_attempts": 5,
            "health_check_interval": 120,
        })
        assert result["success"] is True
        config = result["configuration"]
        assert config["heartbeat_timeout"] == 60
        assert config["max_error_rate"] == 0.8
        assert config["max_response_time"] == 5.0
        assert config["restart_cooldown"] == 600
        assert config["max_restart_attempts"] == 5
        assert config["health_check_interval"] == 120

    @pytest.mark.asyncio
    async def test_configure_partial(self, agent_watcher_instance):
        """Test partial configuration update"""
        agent = agent_watcher_instance
        result = await agent.process_task({
            "action": "configure",
            "heartbeat_timeout": 45,
        })
        assert result["success"] is True
        assert result["configuration"]["heartbeat_timeout"] == 45
        # Other values should remain as initial
        assert result["configuration"]["max_error_rate"] == 0.5

    def test_get_performance_metrics(self, agent_watcher_instance):
        """Check metrics structure"""
        agent = agent_watcher_instance
        metrics = agent.get_performance_metrics()
        assert metrics["agent_id"] == "agent_watcher"
        assert metrics["status"] == "ready"
        assert "capabilities" in metrics
        assert "stats" in metrics
        assert "total_checks" in metrics["stats"]
        assert "successful_checks" in metrics["stats"]
        assert "failed_checks" in metrics["stats"]
        assert "alerts_sent" in metrics["stats"]
        assert "restarts_triggered" in metrics["stats"]
        assert "avg_check_duration" in metrics["stats"]
        assert "registered_agents" in metrics
        assert "total_alerts" in metrics
        assert "psutil_available" in metrics
        assert "configuration" in metrics
        config = metrics["configuration"]
        assert "heartbeat_timeout" in config
        assert "max_error_rate" in config
        assert "max_response_time" in config
        assert "restart_cooldown" in config
        assert "max_restart_attempts" in config
        assert "health_check_interval" in config

    def test_add_alert(self, agent_watcher_instance):
        """Test alert creation"""
        agent = agent_watcher_instance
        agent._add_alert("test_agent", "warning", "Test alert message")

        assert len(agent._alerts) == 1
        alert = agent._alerts[0]
        assert alert["agent_id"] == "test_agent"
        assert alert["severity"] == "warning"
        assert alert["message"] == "Test alert message"
        assert "timestamp" in alert
        assert agent._stats["alerts_sent"] == 1

    def test_add_alert_updates_health(self, agent_watcher_instance):
        """Test that adding an alert updates agent health alert count"""
        agent = agent_watcher_instance
        agent._agent_health["test_agent"] = {
            "alerts_triggered": 0
        }
        agent._add_alert("test_agent", "critical", "Critical issue")
        assert agent._agent_health["test_agent"]["alerts_triggered"] == 1

    def test_add_alert_bounded(self, agent_watcher_instance):
        """Test that alerts are bounded (max 1000, trimmed to 500)"""
        agent = agent_watcher_instance
        # Add 1001 alerts
        for i in range(1001):
            agent._add_alert("test_agent", "info", f"Alert {i}")
        # Should be trimmed to 500
        assert len(agent._alerts) == 500

    def test_health_check_constants(self):
        """Check status constants"""
        from agents.agent_watcher import AgentWatcherAgent
        assert AgentWatcherAgent.STATUS_HEALTHY == "healthy"
        assert AgentWatcherAgent.STATUS_DEGRADED == "degraded"
        assert AgentWatcherAgent.STATUS_UNHEALTHY == "unhealthy"
        assert AgentWatcherAgent.STATUS_UNKNOWN == "unknown"
        assert AgentWatcherAgent.STATUS_OFFLINE == "offline"

    def test_severity_constants(self):
        """Check severity level constants"""
        from agents.agent_watcher import AgentWatcherAgent
        assert AgentWatcherAgent.SEVERITY_INFO == "info"
        assert AgentWatcherAgent.SEVERITY_WARNING == "warning"
        assert AgentWatcherAgent.SEVERITY_CRITICAL == "critical"

    @pytest.mark.asyncio
    async def test_check_agent_no_id(self, agent_watcher_instance):
        """Test check_single_agent without agent_id returns error"""
        agent = agent_watcher_instance
        result = await agent.process_task({
            "action": "check_agent",
        })
        assert result["success"] is False
        assert "agent_id is required" in result["error"]

    @pytest.mark.asyncio
    async def test_restart_agent_no_id(self, agent_watcher_instance):
        """Test restart_agent without agent_id returns error"""
        agent = agent_watcher_instance
        result = await agent.process_task({
            "action": "restart_agent",
        })
        assert result["success"] is False
        assert "agent_id is required" in result["error"]

    @pytest.mark.asyncio
    async def test_perform_agent_check_offline(self, agent_watcher_instance):
        """Test health check for an agent with no instance (offline)"""
        agent = agent_watcher_instance
        # Register agent with no instance
        agent._registered_agents["offline_agent"] = {
            "instance": None,
            "class_name": "Unknown",
        }
        result = await agent._perform_agent_check("offline_agent")
        assert result["status"] == "offline"
        assert result["agent_id"] == "offline_agent"

    @pytest.mark.asyncio
    async def test_perform_agent_check_healthy(self, agent_watcher_instance):
        """Test health check for a responsive agent"""
        agent = agent_watcher_instance
        mock_instance = Mock()
        mock_instance.process_task = AsyncMock(return_value={"success": True})
        agent._registered_agents["healthy_agent"] = {
            "instance": mock_instance,
            "class_name": "MockAgent",
        }
        result = await agent._perform_agent_check("healthy_agent")
        assert result["status"] == "healthy"
        assert result["responsive"] is True
        assert "response_time" in result

    @pytest.mark.asyncio
    async def test_perform_agent_check_timeout(self, agent_watcher_instance):
        """Test health check for an agent that times out"""
        agent = agent_watcher_instance
        agent.heartbeat_timeout = 0  # Immediate timeout

        async def slow_response(task):
            await asyncio.sleep(10)
            return {"success": True}

        mock_instance = Mock()
        mock_instance.process_task = slow_response
        agent._registered_agents["slow_agent"] = {
            "instance": mock_instance,
            "class_name": "MockAgent",
        }
        result = await agent._perform_agent_check("slow_agent")
        assert result["status"] == "unhealthy"

    @pytest.mark.asyncio
    async def test_get_metrics_all_agents(self, agent_watcher_instance):
        """Test getting metrics for all registered agents"""
        agent = agent_watcher_instance
        mock_instance = Mock()
        mock_instance.get_performance_metrics = Mock(return_value={"test": True})
        agent._registered_agents["test_agent"] = {
            "instance": mock_instance,
            "class_name": "MockAgent",
        }
        agent._agent_health["test_agent"] = {
            "status": "healthy",
            "last_check": datetime.now().isoformat(),
            "consecutive_failures": 0,
            "total_checks": 5,
            "total_failures": 0,
            "response_times": [0.1, 0.2, 0.15],
        }

        result = await agent.process_task({"action": "get_metrics"})
        assert result["success"] is True
        assert "test_agent" in result["metrics"]

    @pytest.mark.asyncio
    async def test_get_metrics_single_agent(self, agent_watcher_instance):
        """Test getting metrics for a specific agent"""
        agent = agent_watcher_instance
        mock_instance = Mock()
        mock_instance.capabilities = ["test"]
        mock_instance.status = "ready"
        mock_instance.get_performance_metrics = Mock(return_value={"agent_id": "test_agent"})
        agent._registered_agents["test_agent"] = {
            "instance": mock_instance,
            "class_name": "MockAgent",
        }
        agent._agent_health["test_agent"] = {
            "status": "healthy",
        }

        result = await agent.process_task({
            "action": "get_metrics",
            "agent_id": "test_agent",
        })
        assert result["success"] is True
        assert "metrics" in result
        assert result["metrics"]["agent_id"] == "test_agent"


# =============================================================================
# CROSS-AGENT INTEGRATION TESTS
# =============================================================================

class TestNewAgentIntegration:
    """Test integration points between new agents"""

    def test_all_agents_importable(self):
        """Test that all new agent modules can be imported"""
        from agents.github_agent import GitHubAgent, github_agent
        from agents.voice_agent import VoiceAgent, voice_agent
        from agents.web3_plugin import Web3Plugin, web3_plugin
        from agents.agent_watcher import AgentWatcherAgent, agent_watcher

        assert GitHubAgent is not None
        assert VoiceAgent is not None
        assert Web3Plugin is not None
        assert AgentWatcherAgent is not None
        assert github_agent is not None
        assert voice_agent is not None
        assert web3_plugin is not None
        assert agent_watcher is not None

    def test_all_agents_have_common_interface(self):
        """Test that all agents implement the common interface"""
        from agents.github_agent import github_agent
        from agents.voice_agent import voice_agent
        from agents.web3_plugin import web3_plugin
        from agents.agent_watcher import agent_watcher

        for agent in [github_agent, voice_agent, web3_plugin, agent_watcher]:
            assert hasattr(agent, "agent_id"), f"{agent} missing agent_id"
            assert hasattr(agent, "name"), f"{agent} missing name"
            assert hasattr(agent, "status"), f"{agent} missing status"
            assert hasattr(agent, "capabilities"), f"{agent} missing capabilities"
            assert hasattr(agent, "process_task"), f"{agent} missing process_task"
            assert hasattr(agent, "get_performance_metrics"), f"{agent} missing get_performance_metrics"

    def test_all_agents_unique_ids(self):
        """Test that all agents have unique agent_ids"""
        from agents.github_agent import github_agent
        from agents.voice_agent import voice_agent
        from agents.web3_plugin import web3_plugin
        from agents.agent_watcher import agent_watcher

        ids = [a.agent_id for a in [github_agent, voice_agent, web3_plugin, agent_watcher]]
        assert len(ids) == len(set(ids)), f"Duplicate agent_ids found: {ids}"

    def test_all_error_responses_consistent(self):
        """Test that all agents produce consistent error response format"""
        from agents.github_agent import GitHubAgent
        from agents.voice_agent import VoiceAgent
        from agents.web3_plugin import Web3Plugin
        from agents.agent_watcher import AgentWatcherAgent

        for AgentClass in [GitHubAgent, VoiceAgent, Web3Plugin, AgentWatcherAgent]:
            agent = AgentClass()
            error = agent._create_error_response("test error")
            assert error["success"] is False, f"{AgentClass.__name__} error response missing success=False"
            assert "error" in error, f"{AgentClass.__name__} error response missing 'error' key"
            assert "timestamp" in error, f"{AgentClass.__name__} error response missing 'timestamp' key"
            assert "agent" in error, f"{AgentClass.__name__} error response missing 'agent' key"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short", "-x"])

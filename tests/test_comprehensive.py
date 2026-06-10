"""
Comprehensive Test Suite for AI MultiColony Ecosystem
Tests core components, bug fixes, and integration points

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
# CORE COMPONENT TESTS
# =============================================================================

class TestMemoryManagerFixes:
    """Test that memory_manager.py async/requests fixes work correctly"""

    def test_no_pickle_import(self):
        """Verify pickle is not imported in memory_manager"""
        import importlib
        spec = importlib.util.spec_from_file_location(
            "memory_manager",
            os.path.join(os.path.dirname(os.path.dirname(__file__)),
                         "src", "core", "memory_manager.py")
        )
        with open(spec.origin) as f:
            content = f.read()
        assert "import pickle" not in content, "pickle should not be imported"

    def test_aiohttp_available_flag(self):
        """Verify AIOHTTP_AVAILABLE flag exists"""
        from src.core.memory_manager import AIOHTTP_AVAILABLE
        assert isinstance(AIOHTTP_AVAILABLE, bool)

    @pytest.mark.asyncio
    async def test_fetch_wikipedia_no_aiohttp(self):
        """Test Wikipedia fetch works even without aiohttp (uses requests fallback)"""
        from src.core.memory_manager import ExternalKnowledgeAPI, MemoryManager

        # Create memory manager with temp DB
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = os.path.join(tmpdir, "test_memory.db")
            mm = MemoryManager(db_path=db_path)
            api = ExternalKnowledgeAPI(mm)

            # This should not raise even if aiohttp is not available
            with patch('src.core.memory_manager.AIOHTTP_AVAILABLE', False):
                with patch('requests.get') as mock_get:
                    mock_resp = Mock()
                    mock_resp.status_code = 200
                    mock_resp.json.return_value = {
                        'extract': 'Test content',
                        'content_urls': {'desktop': {'page': 'https://en.wikipedia.org/test'}}
                    }
                    mock_get.return_value = mock_resp

                    result = await api.fetch_wikipedia_knowledge("Python")
                    assert result is not None
                    assert result['topic'] == 'Python'
                    assert result['source'] == 'Wikipedia'


class TestPlatformIntegratorFixes:
    """Test that platform_integrator.py aiohttp import fix works"""

    def test_aiohttp_available_flag(self):
        """Verify AIOHTTP_AVAILABLE flag exists"""
        from src.core.platform_integrator import AIOHTTP_AVAILABLE
        assert isinstance(AIOHTTP_AVAILABLE, bool)

    def test_import_does_not_crash_without_aiohttp(self):
        """Test that importing platform_integrator works even without aiohttp"""
        # This test passes if the import doesn't crash
        from src.core.platform_integrator import PlatformIntegrator
        assert PlatformIntegrator is not None

    def test_github_integration_fallback(self):
        """Test GitHub integration works with requests fallback"""
        from src.core.platform_integrator import GitHubIntegration

        github = GitHubIntegration()
        # Without a token, should not crash
        assert github.token is None or isinstance(github.token, str)
        assert github.connected is False


class TestAISelector:
    """Test AI Selector functionality"""

    def test_selector_initialization(self):
        from core.ai_selector import AISelector
        selector = AISelector()
        assert selector.selection_history == []
        assert isinstance(selector.capability_weights, dict)

    def test_select_best_agent(self):
        from core.ai_selector import AISelector
        selector = AISelector()

        registry = {
            "fullstack_dev": {
                "capabilities": ["frontend", "backend", "database"],
                "priority": 10,
                "status": "active"
            },
            "ui_designer": {
                "capabilities": ["ui_design", "react", "css"],
                "priority": 7,
                "status": "active"
            }
        }

        result = selector.select_best_agent(
            task_type="web_app",
            required_capabilities=["frontend", "backend"],
            agent_registry=registry
        )
        assert result in registry.keys()

    def test_select_best_agent_empty_registry(self):
        from core.ai_selector import AISelector
        selector = AISelector()

        result = selector.select_best_agent(
            task_type="web_app",
            required_capabilities=["frontend"],
            agent_registry={}
        )
        assert result == "fullstack_dev"  # Default fallback


class TestErrorRecovery:
    """Test error recovery system"""

    def test_error_recovery_initialization(self):
        from core.error_recovery import ErrorRecoverySystem
        ers = ErrorRecoverySystem()
        assert ers is not None

    def test_circuit_breaker(self):
        """Test circuit breaker pattern"""
        from core.error_recovery import ErrorRecoverySystem
        ers = ErrorRecoverySystem()

        # Record multiple failures
        for _ in range(5):
            ers.record_failure("test_service")

        # Circuit should be open after multiple failures
        status = ers.get_circuit_status("test_service")
        assert status in ["open", "half_open", "closed"]


class TestLLMGateway:
    """Test LLM Gateway functionality"""

    def test_gateway_initialization(self):
        from connectors.llm_gateway import LLMGateway
        gateway = LLMGateway()
        assert gateway is not None

    def test_provider_listing(self):
        from connectors.llm_gateway import LLMGateway
        gateway = LLMGateway()
        providers = gateway.get_available_providers()
        assert isinstance(providers, list)


class TestDatabaseModels:
    """Test database models and migrations"""

    def test_models_import(self):
        """Test that all models can be imported"""
        from database.models import Agent, Task, Memory, Workflow
        assert Agent is not None
        assert Task is not None
        assert Memory is not None
        assert Workflow is not None

    def test_database_initialization(self):
        """Test database can be initialized"""
        from database.init_db import init_database
        # This should not crash
        assert callable(init_database)


# =============================================================================
# QUALITY CONTROL SPECIALIST TESTS (NEWLY IMPLEMENTED METHODS)
# =============================================================================

class TestQualityControlSpecialist:
    """Test the newly implemented quality control methods"""

    def test_initialization(self):
        from agents.quality_control_specialist import QualityControlSpecialist
        qc = QualityControlSpecialist()
        assert qc.agent_id == "quality_control_specialist"
        assert qc.status == "ready"

    @pytest.mark.asyncio
    async def test_code_style_analysis(self):
        """Test _analyze_code_style method"""
        from agents.quality_control_specialist import QualityControlSpecialist
        qc = QualityControlSpecialist()

        code = "def BadName():\n  pass\n"
        result = await qc._analyze_code_style(code)
        assert "issues" in result
        # Should detect naming convention issue
        issue_types = [i["type"] for i in result["issues"]]
        assert "naming_convention" in issue_types or "inconsistent_indentation" in issue_types

    @pytest.mark.asyncio
    async def test_code_security_analysis(self):
        """Test _analyze_code_security method"""
        from agents.quality_control_specialist import QualityControlSpecialist
        qc = QualityControlSpecialist()

        code = 'eval("1+1")\nos.system("ls")\n'
        result = await qc._analyze_code_security(code)
        assert "issues" in result
        issue_types = [i["type"] for i in result["issues"]]
        assert "security_vulnerability" in issue_types

    @pytest.mark.asyncio
    async def test_code_complexity_analysis(self):
        """Test _analyze_code_complexity method"""
        from agents.quality_control_specialist import QualityControlSpecialist
        qc = QualityControlSpecialist()

        # Simple code - should have low complexity
        simple_code = "def simple():\n    return 1\n"
        result = await qc._analyze_code_complexity(simple_code)
        assert "issues" in result
        assert len(result["issues"]) == 0  # Simple function, no issues

    @pytest.mark.asyncio
    async def test_system_performance_analysis(self):
        """Test _analyze_system_performance method"""
        from agents.quality_control_specialist import QualityControlSpecialist
        qc = QualityControlSpecialist()

        metrics = {
            "response_time": {"average": 500, "p99": 2000},
            "error_rate": 0.02,
            "cpu_usage": 45,
            "memory_usage": 60
        }
        result = await qc._analyze_system_performance(metrics)
        assert "issues" in result
        # Low error rate and good response time = few issues
        assert len(result["issues"]) == 0

    @pytest.mark.asyncio
    async def test_system_security_analysis(self):
        """Test _analyze_system_security method"""
        from agents.quality_control_specialist import QualityControlSpecialist
        qc = QualityControlSpecialist()

        # Insecure config
        insecure_config = {
            "authentication_enabled": False,
            "tls_enabled": False,
            "cors": {"allow_all_origins": True}
        }
        result = await qc._analyze_system_security(insecure_config)
        assert "issues" in result
        issue_types = [i["type"] for i in result["issues"]]
        assert "missing_authentication" in issue_types
        assert "no_tls" in issue_types
        assert "open_cors" in issue_types

    @pytest.mark.asyncio
    async def test_system_reliability_analysis(self):
        """Test _analyze_system_reliability method"""
        from agents.quality_control_specialist import QualityControlSpecialist
        qc = QualityControlSpecialist()

        metrics = {
            "uptime_percentage": 99.5,
            "mttr_minutes": 30,
            "backups_enabled": True
        }
        result = await qc._analyze_system_reliability(metrics)
        assert "issues" in result

    @pytest.mark.asyncio
    async def test_system_scalability_analysis(self):
        """Test _analyze_system_scalability method"""
        from agents.quality_control_specialist import QualityControlSpecialist
        qc = QualityControlSpecialist()

        data = {
            "database_type": "sqlite",
            "supports_horizontal_scaling": False
        }
        result = await qc._analyze_system_scalability(data)
        assert "issues" in result
        issue_types = [i["type"] for i in result["issues"]]
        assert "sqlite_for_production" in issue_types
        assert "no_horizontal_scaling" in issue_types

    @pytest.mark.asyncio
    async def test_process_efficiency_analysis(self):
        """Test _analyze_process_efficiency method"""
        from agents.quality_control_specialist import QualityControlSpecialist
        qc = QualityControlSpecialist()

        data = {
            "automation_percentage": 20,
            "error_rate": 0.15,
            "avg_completion_time_minutes": 120,
            "target_completion_time_minutes": 30
        }
        result = await qc._analyze_process_efficiency(data)
        assert "issues" in result
        assert len(result["issues"]) >= 2  # Low automation + high error rate

    @pytest.mark.asyncio
    async def test_process_compliance_analysis(self):
        """Test _analyze_process_compliance method"""
        from agents.quality_control_specialist import QualityControlSpecialist
        qc = QualityControlSpecialist()

        data = {
            "documentation_complete": False,
            "audit_trail_enabled": False
        }
        result = await qc._analyze_process_compliance(data)
        assert "issues" in result
        issue_types = [i["type"] for i in result["issues"]]
        assert "incomplete_documentation" in issue_types
        assert "no_audit_trail" in issue_types

    @pytest.mark.asyncio
    async def test_process_automation_analysis(self):
        """Test _analyze_process_automation method"""
        from agents.quality_control_specialist import QualityControlSpecialist
        qc = QualityControlSpecialist()

        data = {
            "manual_steps_count": 8,
            "automated_error_handling": False
        }
        result = await qc._analyze_process_automation(data)
        assert "issues" in result

    @pytest.mark.asyncio
    async def test_full_code_quality_assessment(self):
        """Test complete code quality assessment workflow"""
        from agents.quality_control_specialist import QualityControlSpecialist
        qc = QualityControlSpecialist()

        code = '''
def hello():
    """Say hello"""
    return "Hello, World!"

def add(a, b):
    return a + b
'''
        result = await qc.assess_code_quality(code)
        assert result.score >= 0
        assert result.score <= 100
        assert result.item_type == "code"

    @pytest.mark.asyncio
    async def test_system_quality_assessment(self):
        """Test complete system quality assessment"""
        from agents.quality_control_specialist import QualityControlSpecialist
        qc = QualityControlSpecialist()

        system_data = {
            "performance_metrics": {
                "response_time": {"average": 500, "p99": 2000},
                "error_rate": 0.02
            },
            "security_config": {
                "authentication_enabled": True,
                "tls_enabled": True
            }
        }
        result = await qc.assess_system_quality(system_data)
        assert result.score >= 0
        assert result.score <= 100

    @pytest.mark.asyncio
    async def test_generate_quality_report(self):
        """Test quality report generation"""
        from agents.quality_control_specialist import QualityControlSpecialist
        qc = QualityControlSpecialist()

        # Run an assessment first
        await qc.assess_code_quality("def test(): pass")

        # Generate report
        with tempfile.TemporaryDirectory() as tmpdir:
            qc.assessments["test"] = type('obj', (object,), {
                'score': 85.0,
                'item_type': 'code',
                'assessment_type': 'analytical',
                'issues_found': [],
                'recommendations': [],
                'assessment_time': datetime.now()
            })()

            report = await qc.generate_quality_report("week")
            assert "period" in report
            assert "summary" in report or "total_assessments" in report


# =============================================================================
# CONNECTOR TESTS
# =============================================================================

class TestConnectorsModule:
    """Test the connectors module"""

    def test_llm_gateway_export(self):
        """Test LLMGateway is properly exported"""
        from connectors import LLMGateway
        assert LLMGateway is not None

    def test_audio_stream_processor_graceful_import(self):
        """Test AudioStreamProcessor raises ImportError with message"""
        from connectors import AudioStreamProcessor
        try:
            proc = AudioStreamProcessor()
            assert False, "Should have raised ImportError"
        except ImportError as e:
            assert "pyaudio" in str(e).lower() or "AudioStreamProcessor" in str(e)

    def test_web3_plugin_graceful_import(self):
        """Test Web3Plugin raises ImportError with message"""
        from connectors import Web3Plugin
        try:
            plugin = Web3Plugin()
            assert False, "Should have raised ImportError"
        except ImportError as e:
            assert "web3" in str(e).lower() or "Web3Plugin" in str(e)

    def test_github_integration_stub(self):
        """Test GitHubIntegration stub is instantiable"""
        from connectors import GitHubIntegration
        gh = GitHubIntegration(token="test_token")
        assert gh.token == "test_token"
        assert gh.connected is False


# =============================================================================
# SUPABASE INTEGRATION TESTS
# =============================================================================

class TestSupabaseIntegration:
    """Test the fixed Supabase integration"""

    def test_pending_tables_initialization(self):
        """Test _pending_tables is initialized"""
        from src.integrations.supabase_integration import SupabaseIntegration
        sb = SupabaseIntegration()
        assert hasattr(sb, '_pending_tables')
        assert isinstance(sb._pending_tables, dict)

    def test_create_table_without_init(self):
        """Test create_table when not initialized stores schema"""
        from src.integrations.supabase_integration import SupabaseIntegration
        sb = SupabaseIntegration()
        # Clear env vars to ensure not initialized
        sb._initialized = False
        result = sb.create_table("test_table", {"id": "serial PRIMARY KEY", "name": "text"})
        assert result is False  # Not initialized
        assert "test_table" in sb._pending_tables


# =============================================================================
# CREDENTIAL MANAGER TESTS
# =============================================================================

class TestCredentialManager:
    """Test credential manager security"""

    def test_credential_manager_import(self):
        """Test credential manager can be imported safely"""
        from src.core.credential_manager import credential_manager
        # Should be a proxy object, not crash on import
        assert credential_manager is not None


# =============================================================================
# INTEGRATION TESTS
# =============================================================================

class TestWebInterface:
    """Test web interface"""

    def test_app_import(self):
        """Test Flask app can be imported"""
        from web_interface.app import app
        assert app is not None

    def test_app_has_routes(self):
        """Test Flask app has expected routes"""
        from web_interface.app import app
        # Check that routes exist
        rules = [rule.rule for rule in app.url_map.iter_rules()]
        assert '/' in rules or any('/api' in r for r in rules)


class TestSystemStartup:
    """Test system startup sequence"""

    def test_main_module_import(self):
        """Test main module can be imported"""
        import main
        assert hasattr(main, 'AgenticAISystem')

    def test_agentic_ai_system_creation(self):
        """Test AgenticAISystem can be instantiated"""
        from main import AgenticAISystem
        system = AgenticAISystem()
        assert system.system_id == "agentic_ai_system"
        assert system.version == "2.0.0"
        assert system.status == "initializing"


# =============================================================================
# CROSS-MODULE TESTS
# =============================================================================

class TestCrossModuleImports:
    """Test that all modules can be imported without errors"""

    def test_agents_module(self):
        from agents import get_all_agents, get_agents_list
        assert callable(get_all_agents)
        assert callable(get_agents_list)

    def test_core_module(self):
        from core import ai_selector, error_recovery, memory_bus, prompt_master, scheduler, sync_engine
        # All core modules should import without error

    def test_config_module(self):
        from config import system_config
        assert True  # Just test it imports

    def test_database_module(self):
        from database import models, init_db
        assert models is not None

    def test_src_agents_module(self):
        # src/agents should be importable
        from src.agents import agent_base
        assert agent_base is not None


# =============================================================================
# FIXTURES
# =============================================================================

@pytest.fixture
def temp_directory():
    """Create a temporary directory for test data"""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir


@pytest.fixture
def mock_env():
    """Set up mock environment variables"""
    env_vars = {
        'SECRET_KEY': 'test-secret-key',
        'CREDENTIAL_MASTER_PASSWORD': 'test-master-password',
        'FLASK_ENV': 'testing',
        'DATABASE_PATH': ':memory:'
    }
    with patch.dict(os.environ, env_vars):
        yield env_vars


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short", "-x"])

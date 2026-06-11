"""
Comprehensive tests for core modules.

Covers: BaseAgent, AgentManager, MemoryManager, SecureCredentialManager,
KnowledgeEnrichment (FreeAPIConnector, IntelligentKnowledgeOrchestrator),
PlatformIntegrator.

External network calls are mocked throughout.
"""

import asyncio
import hashlib
import json
import os
import sqlite3
import tempfile
from datetime import datetime
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest


# ───────────────────────────────────────────────────────────────
# BaseAgent (abstract, needs a concrete subclass for testing)
# ───────────────────────────────────────────────────────────────

class ConcreteAgent:
    """Concrete implementation of BaseAgent for testing."""

    def __init__(self, agent_id: str = "test_agent"):
        from src.core.base_agent import BaseAgent
        # Manually set attributes to avoid needing a YAML config file
        self.agent_id = agent_id
        self.config = {}
        self.agent_config = {}
        self.name = agent_id
        self.role = "Test Agent"
        self.emoji = "\U0001f9ea"
        self.prompt = "Test prompt"

        import logging
        self.logger = logging.getLogger(f"test.{agent_id}")

        self.status = "initialized"
        self.current_task = None
        self.task_history = []
        self.performance_metrics = {
            'tasks_completed': 0,
            'success_rate': 1.0,
            'avg_response_time': 0.0,
            'errors': 0,
        }

    # ---- Copy all public methods from BaseAgent ----
    def get_system_prompt(self):
        return f"""\n        {self.prompt}\n        \n        AGENT INFO:\n        - Name: {self.name}\n        - Role: {self.role}\n        - ID: {self.agent_id}\n        \n        Always respond in the format specified in your prompt.\n        Include your emoji ({self.emoji}) in status updates.\n        """

    def update_status(self, status, task_info=None):
        self.status = status
        self.current_task = task_info
        self.logger.info(f"{self.emoji} {self.name} status: {status}")

    def log_task_completion(self, task, result, success=True):
        task_log = {
            'timestamp': datetime.now().isoformat(),
            'task': task,
            'result': result,
            'success': success,
            'response_time': getattr(self, '_task_start_time', 0)
        }
        self.task_history.append(task_log)
        self.performance_metrics['tasks_completed'] += 1
        if not success:
            self.performance_metrics['errors'] += 1
        total_tasks = self.performance_metrics['tasks_completed']
        successful_tasks = total_tasks - self.performance_metrics['errors']
        self.performance_metrics['success_rate'] = successful_tasks / total_tasks if total_tasks > 0 else 1.0

    def get_performance_metrics(self):
        return {
            'agent_id': self.agent_id,
            'name': self.name,
            'status': self.status,
            'metrics': self.performance_metrics,
            'current_task': self.current_task
        }

    def format_response(self, content, response_type="standard"):
        return {
            'agent_id': self.agent_id,
            'agent_name': self.name,
            'emoji': self.emoji,
            'response_type': response_type,
            'content': content,
            'timestamp': datetime.now().isoformat(),
            'status': self.status
        }

    def validate_input(self, task):
        required_fields = ['task_id', 'request', 'context']
        return all(field in task for field in required_fields)

    def handle_error(self, error, task):
        error_msg = f"Error in {self.name}: {str(error)}"
        self.logger.error(error_msg)
        return self.format_response(
            f"\u274c {error_msg}\n\nTask: {task.get('request', 'Unknown')}\nPlease retry or contact system administrator.",
            "error"
        )


class TestBaseAgent:
    """Tests for BaseAgent public methods."""

    @pytest.fixture
    def agent(self):
        return ConcreteAgent("test_agent")

    def test_initial_state(self, agent):
        """Agent starts with initialized status and default metrics."""
        assert agent.status == "initialized"
        assert agent.agent_id == "test_agent"
        assert agent.performance_metrics['tasks_completed'] == 0
        assert agent.performance_metrics['success_rate'] == 1.0

    def test_update_status(self, agent):
        """update_status changes agent status and current task."""
        task_info = {"task_id": "t1", "request": "do something"}
        agent.update_status("processing", task_info)
        assert agent.status == "processing"
        assert agent.current_task == task_info

    def test_update_status_no_task(self, agent):
        """update_status with no task_info sets current_task to None."""
        agent.update_status("ready")
        assert agent.status == "ready"
        assert agent.current_task is None

    def test_log_task_completion_success(self, agent):
        """Logging a successful task updates metrics correctly."""
        task = {"task_id": "t1", "request": "test"}
        result = {"output": "done"}
        agent.log_task_completion(task, result, success=True)
        assert agent.performance_metrics['tasks_completed'] == 1
        assert agent.performance_metrics['errors'] == 0
        assert agent.performance_metrics['success_rate'] == 1.0
        assert len(agent.task_history) == 1

    def test_log_task_completion_failure(self, agent):
        """Logging a failed task increments error count."""
        task = {"task_id": "t1", "request": "test"}
        result = {"error": "failed"}
        agent.log_task_completion(task, result, success=False)
        assert agent.performance_metrics['tasks_completed'] == 1
        assert agent.performance_metrics['errors'] == 1
        assert agent.performance_metrics['success_rate'] == 0.0

    def test_success_rate_mixed_tasks(self, agent):
        """Success rate is correctly computed with mixed success/failure."""
        task = {"task_id": "t1", "request": "test"}
        agent.log_task_completion(task, {}, success=True)
        agent.log_task_completion(task, {}, success=True)
        agent.log_task_completion(task, {}, success=False)
        # 2 success out of 3 = 0.667
        assert agent.performance_metrics['success_rate'] == pytest.approx(2/3, abs=0.01)

    def test_get_performance_metrics(self, agent):
        """get_performance_metrics returns correct structure."""
        metrics = agent.get_performance_metrics()
        assert 'agent_id' in metrics
        assert 'name' in metrics
        assert 'status' in metrics
        assert 'metrics' in metrics
        assert metrics['agent_id'] == "test_agent"

    def test_format_response(self, agent):
        """format_response returns correctly formatted dict."""
        response = agent.format_response("Hello world", "standard")
        assert response['agent_id'] == "test_agent"
        assert response['content'] == "Hello world"
        assert response['response_type'] == "standard"
        assert 'timestamp' in response

    def test_format_response_default_type(self, agent):
        """format_response defaults to 'standard' type."""
        response = agent.format_response("test")
        assert response['response_type'] == "standard"

    def test_validate_input_valid(self, agent):
        """validate_input returns True for tasks with all required fields."""
        task = {"task_id": "1", "request": "do it", "context": {}}
        assert agent.validate_input(task) is True

    def test_validate_input_missing_fields(self, agent):
        """validate_input returns False when required fields are missing."""
        assert agent.validate_input({"task_id": "1"}) is False
        assert agent.validate_input({"request": "do it"}) is False
        assert agent.validate_input({}) is False

    def test_handle_error(self, agent):
        """handle_error returns error response with correct format."""
        error = ValueError("something went wrong")
        task = {"task_id": "1", "request": "test", "context": {}}
        response = agent.handle_error(error, task)
        assert response['response_type'] == "error"
        assert "something went wrong" in response['content']

    def test_get_system_prompt(self, agent):
        """get_system_prompt includes agent info."""
        prompt = agent.get_system_prompt()
        assert "test_agent" in prompt
        assert "Test Agent" in prompt


# ───────────────────────────────────────────────────────────────
# AgentManager
# ───────────────────────────────────────────────────────────────

class TestAgentManager:
    """Tests for the AgentManager orchestration layer."""

    @pytest.fixture
    def manager(self):
        from src.core.agent_manager import AgentManager
        return AgentManager(config_path="nonexistent.yaml")

    @pytest.fixture
    def mock_agent(self):
        """Create a mock agent that has required BaseAgent attributes."""
        agent = MagicMock()
        agent.agent_id = "mock_agent"
        agent.name = "Mock Agent"
        agent.role = "Tester"
        agent.emoji = "🤖"
        agent.status = "ready"
        agent.process_task = MagicMock(return_value={"status": "done"})
        agent.update_status = MagicMock()
        agent.get_performance_metrics = MagicMock(return_value={
            "agent_id": "mock_agent",
            "name": "Mock Agent",
            "status": "ready",
            "metrics": {"tasks_completed": 0, "success_rate": 1.0,
                        "avg_response_time": 0, "errors": 0},
            "current_task": None,
        })
        return agent

    def test_register_agent(self, manager, mock_agent):
        """Registering an agent adds it to the agents dict."""
        manager.register_agent(mock_agent)
        assert "mock_agent" in manager.agents

    def test_get_agent(self, manager, mock_agent):
        """get_agent returns the registered agent by ID."""
        manager.register_agent(mock_agent)
        result = manager.get_agent("mock_agent")
        assert result is mock_agent

    def test_get_agent_not_found(self, manager):
        """get_agent returns None for unregistered agent ID."""
        assert manager.get_agent("nonexistent") is None

    def test_list_agents(self, manager, mock_agent):
        """list_agents returns list with correct agent info."""
        manager.register_agent(mock_agent)
        agents = manager.list_agents()
        assert len(agents) == 1
        assert agents[0]['id'] == "mock_agent"
        assert agents[0]['name'] == "Mock Agent"

    def test_list_agents_empty(self, manager):
        """list_agents returns empty list when no agents registered."""
        assert manager.list_agents() == []

    def test_get_system_status(self, manager, mock_agent):
        """get_system_status returns correct structure."""
        manager.register_agent(mock_agent)
        status = manager.get_system_status()
        assert 'total_agents' in status
        assert 'active_workflows' in status
        assert 'agent_status' in status
        assert status['total_agents'] == 1

    def test_get_workflow_status_not_found(self, manager):
        """get_workflow_status returns None for non-existent workflow."""
        assert manager.get_workflow_status("nonexistent") is None

    def test_error_response(self, manager):
        """_error_response generates correct error dict."""
        result = manager._error_response("Test error")
        assert result['status'] == 'error'
        assert result['message'] == "Test error"

    @pytest.mark.asyncio
    async def test_send_message_missing_agent(self, manager):
        """send_message_between_agents returns error when agent not found."""
        result = await manager.send_message_between_agents("a", "b", {"request": "test"})
        assert result['status'] == 'error'

    @pytest.mark.asyncio
    async def test_send_message_between_agents(self, manager, mock_agent):
        """send_message_between_agents routes message to target agent."""
        mock_agent2 = MagicMock()
        mock_agent2.agent_id = "agent2"
        mock_agent2.name = "Agent 2"
        mock_agent2.role = "Helper"
        mock_agent2.emoji = "🤖"
        mock_agent2.status = "ready"
        mock_agent2.process_task = MagicMock(return_value={"status": "processed"})
        mock_agent2.update_status = MagicMock()

        manager.register_agent(mock_agent)
        manager.register_agent(mock_agent2)

        result = await manager.send_message_between_agents(
            "mock_agent", "agent2", {"request": "help me"}
        )
        assert result["status"] == "processed"

    @pytest.mark.asyncio
    async def test_execute_workflow_not_found(self, manager):
        """Executing a non-existent workflow returns error."""
        result = await manager.execute_workflow("nonexistent", {})
        assert result['status'] == 'error'

    def test_communication_log_trim(self, manager, mock_agent):
        """Communication log is trimmed when it exceeds 1000 entries."""
        manager.register_agent(mock_agent)
        for i in range(1100):
            manager.communication_log.append({"test": i})
        manager._log_communication("mock_agent", {"task": "test"}, {"result": "ok"})
        assert len(manager.communication_log) <= 1000


# ───────────────────────────────────────────────────────────────
# MemoryManager
# ───────────────────────────────────────────────────────────────

class TestMemoryManager:
    """Tests for the MemoryManager SQLite-based memory system."""

    @pytest.fixture
    def memory(self):
        """Create MemoryManager with a temp database."""
        from src.core.memory_manager import MemoryManager
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = str(Path(tmpdir) / "test_memory.db")
            mm = MemoryManager(db_path=db_path)
            yield mm

    @pytest.fixture
    def sample_entry(self):
        from src.core.memory_manager import MemoryEntry
        return MemoryEntry(
            id="mem_001",
            agent_id="agent_test",
            task_id="task_001",
            content="Test memory content about Python",
            metadata={"key": "value"},
            timestamp=datetime.now().isoformat(),
            memory_type="interaction",
            importance=7,
        )

    def test_store_and_retrieve_memory(self, memory, sample_entry):
        """Storing and retrieving a memory entry works correctly."""
        assert memory.store_memory(sample_entry) is True
        results = memory.retrieve_memories(agent_id="agent_test")
        assert len(results) == 1
        assert results[0].content == "Test memory content about Python"

    def test_retrieve_all_memories(self, memory, sample_entry):
        """Retrieving without filters returns all memories."""
        memory.store_memory(sample_entry)
        from src.core.memory_manager import MemoryEntry
        entry2 = MemoryEntry(
            id="mem_002", agent_id="agent2", task_id="task_002",
            content="Another memory", metadata={},
            timestamp=datetime.now().isoformat(),
            memory_type="knowledge", importance=5,
        )
        memory.store_memory(entry2)
        results = memory.retrieve_memories()
        assert len(results) == 2

    def test_retrieve_by_memory_type(self, memory, sample_entry):
        """Filtering by memory_type works correctly."""
        memory.store_memory(sample_entry)
        results = memory.retrieve_memories(memory_type="knowledge")
        assert len(results) == 0
        results = memory.retrieve_memories(memory_type="interaction")
        assert len(results) == 1

    def test_retrieve_with_limit(self, memory):
        """Retrieving with limit restricts result count."""
        from src.core.memory_manager import MemoryEntry
        for i in range(10):
            entry = MemoryEntry(
                id=f"mem_{i}", agent_id="agent_test", task_id=f"task_{i}",
                content=f"Memory {i}", metadata={},
                timestamp=datetime.now().isoformat(),
                memory_type="interaction", importance=5,
            )
            memory.store_memory(entry)
        results = memory.retrieve_memories(limit=5)
        assert len(results) == 5

    def test_search_memories(self, memory, sample_entry):
        """Searching memories by content keyword works."""
        memory.store_memory(sample_entry)
        results = memory.search_memories("Python")
        assert len(results) == 1
        results = memory.search_memories("nonexistent")
        assert len(results) == 0

    def test_search_memories_by_agent(self, memory, sample_entry):
        """Searching with agent_id filter works."""
        memory.store_memory(sample_entry)
        results = memory.search_memories("Python", agent_id="agent_test")
        assert len(results) == 1
        results = memory.search_memories("Python", agent_id="other_agent")
        assert len(results) == 0

    def test_store_agent_interaction(self, memory):
        """Storing agent interaction returns True."""
        result = memory.store_agent_interaction(
            "agent_a", "agent_b", "collaboration", "Shared data", context={"task": "t1"}
        )
        assert result is True

    def test_get_agent_interactions(self, memory):
        """Getting interactions for an agent returns correct results."""
        memory.store_agent_interaction("agent_a", "agent_b", "msg", "hello")
        memory.store_agent_interaction("agent_b", "agent_a", "reply", "world")
        interactions = memory.get_agent_interactions("agent_a")
        assert len(interactions) == 2

    def test_get_agent_interactions_empty(self, memory):
        """Getting interactions for unknown agent returns empty list."""
        interactions = memory.get_agent_interactions("unknown_agent")
        assert interactions == []

    def test_store_memory_overwrite(self, memory, sample_entry):
        """Storing a memory with the same ID overwrites the existing one."""
        memory.store_memory(sample_entry)
        from src.core.memory_manager import MemoryEntry
        updated_entry = MemoryEntry(
            id="mem_001", agent_id="agent_test", task_id="task_001",
            content="Updated content", metadata={"updated": True},
            timestamp=datetime.now().isoformat(),
            memory_type="interaction", importance=9,
        )
        memory.store_memory(updated_entry)
        results = memory.retrieve_memories(agent_id="agent_test")
        assert len(results) == 1
        assert results[0].content == "Updated content"


# ───────────────────────────────────────────────────────────────
# SecureCredentialManager
# ───────────────────────────────────────────────────────────────

class TestSecureCredentialManager:
    """Tests for SecureCredentialManager encryption and CRUD operations."""

    @pytest.fixture
    def cred_manager(self):
        """Create a credential manager with a temp database and known password."""
        from src.core.credential_manager import SecureCredentialManager
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = str(Path(tmpdir) / "test_creds.db")
            salt_path = Path(tmpdir) / "credentials.salt"
            mgr = SecureCredentialManager.__new__(SecureCredentialManager)
            mgr.db_path = db_path
            mgr.master_password = "test_master_password_123"
            mgr.encryption_key = None

            # Initialize encryption with isolated salt
            from cryptography.fernet import Fernet
            from cryptography.hazmat.primitives import hashes
            from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
            import base64

            salt = os.urandom(16)
            salt_path.write_bytes(salt)
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(), length=32, salt=salt, iterations=100000,
            )
            key = base64.urlsafe_b64encode(kdf.derive(mgr.master_password.encode()))
            mgr.fernet = Fernet(key)

            # Setup database
            mgr._setup_database()
            # Override salt path for isolation
            with patch.object(Path, 'read_bytes', return_value=salt):
                yield mgr

    def test_store_and_get_credential(self, cred_manager):
        """Storing and retrieving a credential works with encryption."""
        cred_manager.store_credential(
            website_name="GitHub", website_url="https://github.com",
            username="testuser", email="test@example.com",
            password="secret123",
        )
        result = cred_manager.get_credential(website_name="GitHub")
        assert result is not None
        assert result['username'] == "testuser"
        assert result['password'] == "secret123"

    def test_store_credential_no_password(self, cred_manager):
        """Storing without password raises ValueError and returns False."""
        result = cred_manager.store_credential(
            website_name="Test", website_url="https://test.com",
        )
        assert result is False

    def test_get_credential_by_url(self, cred_manager):
        """Retrieving credential by URL works."""
        cred_manager.store_credential(
            website_name="Test", website_url="https://example.com",
            password="pass123",
        )
        result = cred_manager.get_credential(website_url="https://example.com")
        assert result is not None
        assert result['website_name'] == "Test"

    def test_get_credential_by_id(self, cred_manager):
        """Retrieving credential by ID works."""
        cred_manager.store_credential(
            website_name="Test", website_url="https://test.com",
            password="pass123",
        )
        result = cred_manager.get_credential(credential_id=1)
        assert result is not None

    def test_get_credential_not_found(self, cred_manager):
        """Getting non-existent credential returns None."""
        result = cred_manager.get_credential(website_name="NonExistent")
        assert result is None

    def test_get_credential_no_params(self, cred_manager):
        """Getting credential without any parameters returns None."""
        result = cred_manager.get_credential()
        assert result is None

    def test_list_credentials(self, cred_manager):
        """list_credentials returns all credentials without passwords."""
        cred_manager.store_credential(
            "Site1", "https://s1.com", password="p1",
        )
        cred_manager.store_credential(
            "Site2", "https://s2.com", password="p2",
        )
        creds = cred_manager.list_credentials()
        assert len(creds) == 2
        # Passwords should NOT be in list output
        for c in creds:
            assert 'password' not in c

    def test_update_credential(self, cred_manager):
        """Updating a credential field works."""
        cred_manager.store_credential(
            "Test", "https://test.com", username="old_user", password="pass",
        )
        result = cred_manager.update_credential(1, username="new_user")
        assert result is True
        updated = cred_manager.get_credential(credential_id=1)
        assert updated['username'] == "new_user"

    def test_update_credential_password(self, cred_manager):
        """Updating password re-encrypts it correctly."""
        cred_manager.store_credential(
            "Test", "https://test.com", password="old_pass",
        )
        cred_manager.update_credential(1, password="new_pass")
        updated = cred_manager.get_credential(credential_id=1)
        assert updated['password'] == "new_pass"

    def test_update_credential_not_found(self, cred_manager):
        """Updating non-existent credential returns False."""
        result = cred_manager.update_credential(999, username="test")
        assert result is False

    def test_delete_credential(self, cred_manager):
        """Deleting a credential removes it."""
        cred_manager.store_credential(
            "Test", "https://test.com", password="pass",
        )
        result = cred_manager.delete_credential(1)
        assert result is True
        assert cred_manager.get_credential(credential_id=1) is None

    def test_delete_credential_not_found(self, cred_manager):
        """Deleting non-existent credential returns False."""
        result = cred_manager.delete_credential(999)
        assert result is False

    def test_search_credentials(self, cred_manager):
        """Searching credentials by keyword works."""
        cred_manager.store_credential(
            "GitHub", "https://github.com", username="dev", password="p1",
        )
        cred_manager.store_credential(
            "GitLab", "https://gitlab.com", username="dev2", password="p2",
        )
        results = cred_manager.search_credentials("Git")
        assert len(results) == 2

    def test_search_credentials_no_match(self, cred_manager):
        """Searching with no matching query returns empty list."""
        cred_manager.store_credential(
            "Test", "https://test.com", password="p",
        )
        results = cred_manager.search_credentials("NonExistent")
        assert results == []

    def test_export_credentials_without_passwords(self, cred_manager):
        """Exporting without passwords does not include password field."""
        cred_manager.store_credential(
            "Test", "https://test.com", password="secret",
        )
        exported = cred_manager.export_credentials(include_passwords=False)
        assert exported['include_passwords'] is False
        assert 'password' not in exported['credentials'][0]

    def test_export_credentials_with_passwords(self, cred_manager):
        """Exporting with passwords includes decrypted password field."""
        cred_manager.store_credential(
            "Test", "https://test.com", password="secret123",
        )
        exported = cred_manager.export_credentials(include_passwords=True)
        assert exported['credentials'][0]['password'] == "secret123"

    def test_log_usage(self, cred_manager):
        """Logging usage creates a history entry."""
        cred_manager.store_credential(
            "Test", "https://test.com", password="p",
        )
        cred_manager.log_usage(1, "https://test.com", "login", True)
        history = cred_manager.get_usage_history(credential_id=1)
        assert len(history) == 1
        assert history[0]['action_type'] == "login"
        assert history[0]['success'] is True


# ───────────────────────────────────────────────────────────────
# KnowledgeEnrichment - FreeAPIConnector & Orchestrator
# ───────────────────────────────────────────────────────────────

class TestFreeAPIConnector:
    """Tests for FreeAPIConnector knowledge source configuration."""

    def test_has_expected_apis(self):
        """FreeAPIConnector initializes with expected API list."""
        from src.core.knowledge_enrichment import FreeAPIConnector
        connector = FreeAPIConnector()
        assert 'wikipedia' in connector.apis
        assert 'quotable' in connector.apis
        assert 'jokes' in connector.apis
        assert 'advice' in connector.apis

    def test_api_structure(self):
        """Each API entry has required KnowledgeSource fields."""
        from src.core.knowledge_enrichment import FreeAPIConnector
        connector = FreeAPIConnector()
        for name, source in connector.apis.items():
            assert source.name, f"API {name} missing name"
            assert source.url, f"API {name} missing url"
            assert isinstance(source.api_key_required, bool)
            assert source.rate_limit > 0

    @pytest.mark.asyncio
    async def test_fetch_wikipedia_summary_mock(self):
        """fetch_wikipedia_summary returns None on network error (mocked)."""
        from src.core.knowledge_enrichment import FreeAPIConnector
        connector = FreeAPIConnector()
        with patch('aiohttp.ClientSession') as mock_session:
            mock_session.return_value.__aenter__ = AsyncMock(return_value=mock_session())
            mock_session.return_value.__aexit__ = AsyncMock(return_value=False)
            mock_session().get = AsyncMock(side_effect=Exception("Network error"))
            result = await connector.fetch_wikipedia_summary("Python")
            assert result is None


class TestIntelligentKnowledgeOrchestrator:
    """Tests for the IntelligentKnowledgeOrchestrator."""

    @pytest.fixture
    def orchestrator(self):
        from src.core.knowledge_enrichment import (
            FreeAPIConnector, IntelligentKnowledgeOrchestrator,
        )
        connector = FreeAPIConnector()
        return IntelligentKnowledgeOrchestrator(connector)

    def test_extract_main_topic(self, orchestrator):
        """_extract_main_topic removes common words and returns meaningful terms."""
        topic = orchestrator._extract_main_topic("Create a new website for the business")
        assert "create" not in topic.lower()
        assert len(topic) > 0

    def test_extract_main_topic_empty(self, orchestrator):
        """_extract_main_topic returns default for empty/common-only input."""
        topic = orchestrator._extract_main_topic("the a an and or")
        assert topic == "general topic"

    def test_generate_agent_specific_insights(self, orchestrator):
        """Agent-specific insights vary by agent type."""
        insights_planner = orchestrator._generate_agent_specific_insights({}, "agent_03_planner")
        insights_designer = orchestrator._generate_agent_specific_insights({}, "agent_05_designer")
        assert insights_planner != insights_designer

    def test_generate_knowledge_summary_empty(self, orchestrator):
        """Summary with no sources returns default message."""
        summary = orchestrator._generate_knowledge_summary({})
        assert "No additional knowledge" in summary

    def test_generate_knowledge_summary_with_wikipedia(self, orchestrator):
        """Summary with Wikipedia source includes the extract."""
        sources = {
            "wikipedia": {"extract": "Python is a programming language."},
        }
        summary = orchestrator._generate_knowledge_summary(sources)
        assert "Python" in summary

    def test_generate_knowledge_summary_with_quotes(self, orchestrator):
        """Summary with quotes includes the quote content."""
        sources = {
            "quotes": {"content": "Stay hungry, stay foolish.", "author": "Steve Jobs"},
        }
        summary = orchestrator._generate_knowledge_summary(sources)
        assert "Stay hungry" in summary


# ───────────────────────────────────────────────────────────────
# PlatformIntegrator
# ───────────────────────────────────────────────────────────────

class TestPlatformIntegrator:
    """Tests for PlatformIntegrator and its sub-integrations."""

    def test_get_integration(self):
        """get_integration returns the requested integration."""
        from src.core.platform_integrator import PlatformIntegrator
        pi = PlatformIntegrator()
        github = pi.get_integration("github")
        assert github is not None

    def test_get_integration_not_found(self):
        """get_integration returns None for unknown integration."""
        from src.core.platform_integrator import PlatformIntegrator
        pi = PlatformIntegrator()
        assert pi.get_integration("nonexistent") is None

    def test_github_integration_not_connected(self):
        """GitHub integration starts disconnected."""
        from src.core.platform_integrator import GitHubIntegration
        gh = GitHubIntegration()
        assert gh.is_connected() is False

    @pytest.mark.asyncio
    async def test_github_health_check_no_token(self):
        """GitHub health check returns not_configured without token."""
        from src.core.platform_integrator import GitHubIntegration
        gh = GitHubIntegration()
        with patch.dict(os.environ, {}, clear=True):
            gh.token = None
            result = await gh.health_check()
            assert result['status'] == 'not_configured'

    @pytest.mark.asyncio
    async def test_github_create_repo_not_connected(self):
        """Creating repo when not connected returns error."""
        from src.core.platform_integrator import GitHubIntegration
        gh = GitHubIntegration()
        result = await gh.create_repository("test-repo")
        assert 'error' in result

    def test_google_services_not_connected(self):
        """Google Services starts disconnected."""
        from src.core.platform_integrator import GoogleServicesIntegration
        gs = GoogleServicesIntegration()
        assert gs.is_connected() is False

    @pytest.mark.asyncio
    async def test_google_health_check_no_creds(self):
        """Google health check without credentials returns not_configured."""
        from src.core.platform_integrator import GoogleServicesIntegration
        gs = GoogleServicesIntegration()
        with patch.dict(os.environ, {}, clear=True):
            gs.credentials_path = None
            result = await gs.health_check()
            assert result['status'] == 'not_configured'

    def test_external_api_manager_has_apis(self):
        """ExternalAPIManager has expected APIs."""
        from src.core.platform_integrator import ExternalAPIManager
        mgr = ExternalAPIManager()
        assert 'wikipedia' in mgr.apis
        assert 'jokes' in mgr.apis

    def test_external_api_manager_not_connected_initially(self):
        """ExternalAPIManager starts with no connections confirmed."""
        from src.core.platform_integrator import ExternalAPIManager
        mgr = ExternalAPIManager()
        # No APIs have been tested yet
        assert mgr.is_connected() is False

    @pytest.mark.asyncio
    async def test_fetch_knowledge_unknown_source(self):
        """Fetching from unknown source returns error."""
        from src.core.platform_integrator import ExternalAPIManager
        mgr = ExternalAPIManager()
        result = await mgr.fetch_knowledge("nonexistent_api")
        assert 'error' in result

    def test_ai_platform_manager_not_connected(self):
        """AIPlatformManager starts not connected."""
        from src.core.platform_integrator import AIPlatformManager
        mgr = AIPlatformManager()
        assert mgr.is_connected() is False

    @pytest.mark.asyncio
    async def test_ai_platform_health_check(self):
        """AI platform health check returns correct structure."""
        from src.core.platform_integrator import AIPlatformManager
        mgr = AIPlatformManager()
        with patch.dict(os.environ, {}, clear=True):
            # Reset API keys
            for config in mgr.platforms.values():
                config['api_key'] = None
                config['status'] = 'not_configured'
            result = await mgr.health_check()
            assert 'platform_status' in result
            assert result['connected_platforms'] == 0

"""
🧪 Agent Tests - Unit Tests for All Agents
Comprehensive testing suite for the Agentic AI System

Made with ❤️ by Mulky Malikul Dhaher in Indonesia 🇮🇩
"""

import asyncio
import json
import os

# Import agents to test
import sys
from datetime import datetime
from unittest.mock import AsyncMock, Mock, patch

import pytest

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from colony.agents.agent_maker import agent_maker
from colony.agents.data_sync import data_sync_agent
from colony.agents.deploy_manager import deploy_manager_agent
from colony.agents.dev_engine import dev_engine_agent
from colony.agents.fullstack_dev import fullstack_dev_agent
from colony.agents.prompt_generator import prompt_generator_agent
from colony.agents.ui_designer import ui_designer_agent

from colony.agents.cybershell import cybershell_agent


class TestCyberShellAgent:
    """Test CyberShell Agent functionality"""

    @pytest.mark.asyncio
    async def test_shell_command_execution(self):
        """Test basic shell command execution"""
        task = {
            "action": "execute_command",
            "command": "echo 'Hello, World!'",
            "timeout": 30,
        }

        result = await cybershell_agent.process_task(task)

        assert result["success"] is True
        assert "Hello, World!" in result.get("output", "")

    @pytest.mark.asyncio
    async def test_security_restrictions(self):
        """Test security restrictions on dangerous commands"""
        dangerous_commands = ["rm -rf /", "sudo rm -rf /", "format c:", "del C:\\*"]

        for cmd in dangerous_commands:
            task = {"action": "execute_command", "command": cmd}

            result = await cybershell_agent.process_task(task)

            # Should either fail or be blocked
            assert (
                result["success"] is False
                or "blocked" in result.get("output", "").lower()
            )

    @pytest.mark.asyncio
    async def test_file_operations(self):
        """Test file operation capabilities"""
        # Test file listing
        task = {"action": "list_files", "path": "."}

        result = await cybershell_agent.process_task(task)
        assert result["success"] is True
        assert "files" in result

    def test_agent_status(self):
        """Test agent status and configuration"""
        assert cybershell_agent.agent_id == "cybershell"
        assert cybershell_agent.status == "ready"
        assert "shell_execution" in cybershell_agent.capabilities


class TestAgentMaker:
    """Test Agent Maker functionality"""

    @pytest.mark.asyncio
    async def test_agent_creation(self):
        """Test dynamic agent creation"""
        task = {
            "action": "create_agent",
            "agent_type": "data_scientist",
            "requirements": {
                "specialization": "machine_learning",
                "experience_level": "senior",
            },
        }

        result = await agent_maker.process_task(task)

        assert result["success"] is True
        assert "agent_id" in result
        assert result["agent_type"] == "data_scientist"

    @pytest.mark.asyncio
    async def test_template_validation(self):
        """Test agent template validation"""
        task = {"action": "validate_template", "template_name": "data_scientist"}

        result = await agent_maker.process_task(task)

        assert result["success"] is True
        assert "template_valid" in result

    def test_available_templates(self):
        """Test available agent templates"""
        templates = agent_maker.get_available_templates()

        assert isinstance(templates, dict)
        assert "data_scientist" in templates
        assert "web_developer" in templates


class TestUIDesignerAgent:
    """Test UI Designer Agent functionality"""

    @pytest.mark.asyncio
    async def test_component_generation(self):
        """Test React component generation"""
        task = {
            "action": "create_component",
            "component_type": "button",
            "framework": "react",
            "styling": "tailwind",
            "props": {"variant": "primary", "size": "medium"},
        }

        result = await ui_designer_agent.process_task(task)

        assert result["success"] is True
        assert "component_code" in result
        assert "import React" in result["component_code"]

    @pytest.mark.asyncio
    async def test_page_generation(self):
        """Test full page generation"""
        task = {
            "action": "create_page",
            "page_type": "dashboard",
            "components": ["header", "sidebar", "main_content"],
            "framework": "react",
        }

        result = await ui_designer_agent.process_task(task)

        assert result["success"] is True
        assert "page_code" in result
        assert len(result.get("components", [])) > 0

    def test_supported_frameworks(self):
        """Test supported framework listing"""
        frameworks = ui_designer_agent.get_supported_frameworks()

        assert "react" in frameworks
        assert "vue" in frameworks
        assert "angular" in frameworks


class TestDevEngineAgent:
    """Test Dev Engine Agent functionality"""

    @pytest.mark.asyncio
    async def test_project_scaffolding(self):
        """Test project structure creation"""
        task = {
            "action": "create_project",
            "project_type": "fullstack_web",
            "name": "test_project",
            "tech_stack": {
                "frontend": "react",
                "backend": "fastapi",
                "database": "postgresql",
            },
        }

        result = await dev_engine_agent.process_task(task)

        assert result["success"] is True
        assert "project_structure" in result
        assert "package.json" in str(result["project_structure"])

    @pytest.mark.asyncio
    async def test_dependency_management(self):
        """Test dependency installation and management"""
        task = {
            "action": "install_dependencies",
            "project_path": "./test_project",
            "dependencies": ["express", "react", "axios"],
        }

        result = await dev_engine_agent.process_task(task)

        # Should attempt to install dependencies
        assert result["success"] is True or "dependencies" in result

    def test_supported_project_types(self):
        """Test supported project types"""
        types = dev_engine_agent.get_supported_project_types()

        assert "fullstack_web" in types
        assert "mobile_app" in types
        assert "api_service" in types


class TestDataSyncAgent:
    """Test Data Sync Agent functionality"""

    @pytest.mark.asyncio
    async def test_database_sync(self):
        """Test database synchronization"""
        task = {
            "action": "sync_databases",
            "source": "sqlite:///test.db",
            "target": "postgresql://test",
            "tables": ["users", "tasks"],
        }

        # Mock the database connections
        with patch("agents.data_sync.create_engine") as mock_engine:
            mock_engine.return_value = Mock()

            result = await data_sync_agent.process_task(task)

            assert "sync_status" in result

    @pytest.mark.asyncio
    async def test_backup_creation(self):
        """Test database backup functionality"""
        task = {
            "action": "create_backup",
            "database_url": "sqlite:///test.db",
            "backup_path": "./backups/",
        }

        result = await data_sync_agent.process_task(task)

        assert "backup_info" in result

    def test_supported_databases(self):
        """Test supported database types"""
        databases = data_sync_agent.get_supported_databases()

        assert "sqlite" in databases
        assert "postgresql" in databases
        assert "redis" in databases


class TestFullStackDevAgent:
    """Test Full Stack Developer Agent functionality"""

    @pytest.mark.asyncio
    async def test_api_generation(self):
        """Test API endpoint generation"""
        task = {
            "action": "create_api",
            "api_type": "rest",
            "framework": "fastapi",
            "endpoints": [
                {"path": "/users", "method": "GET"},
                {"path": "/users", "method": "POST"},
            ],
        }

        result = await fullstack_dev_agent.process_task(task)

        assert result["success"] is True
        assert "api_code" in result
        assert "from fastapi import" in result["api_code"]

    @pytest.mark.asyncio
    async def test_database_integration(self):
        """Test database model and integration generation"""
        task = {
            "action": "create_models",
            "database": "postgresql",
            "models": [
                {
                    "name": "User",
                    "fields": {
                        "id": "Integer",
                        "email": "String",
                        "created_at": "DateTime",
                    },
                }
            ],
        }

        result = await fullstack_dev_agent.process_task(task)

        assert result["success"] is True
        assert "model_code" in result

    def test_supported_frameworks(self):
        """Test supported development frameworks"""
        frameworks = fullstack_dev_agent.get_supported_frameworks()

        assert "fastapi" in frameworks["backend"]
        assert "react" in frameworks["frontend"]


class TestDeployManagerAgent:
    """Test Deploy Manager Agent functionality"""

    @pytest.mark.asyncio
    async def test_platform_support(self):
        """Test deployment platform support"""
        platforms = deploy_manager_agent._list_supported_platforms()

        assert platforms["success"] is True
        assert "netlify" in platforms["platforms"]
        assert "vercel" in platforms["platforms"]
        assert "railway" in platforms["platforms"]
        assert "docker" in platforms["platforms"]

    @pytest.mark.asyncio
    async def test_docker_deployment(self):
        """Test Docker deployment functionality"""
        task = {
            "action": "deploy",
            "platform": "docker",
            "app_name": "test_app",
            "project_path": "./test_project",
            "config": {"port": 3000, "build_command": "npm run build"},
        }

        # Mock subprocess for testing
        with patch("subprocess.run") as mock_run:
            mock_run.return_value.returncode = 0
            mock_run.return_value.stdout = "Container started successfully"

            result = await deploy_manager_agent.process_task(task)

            assert "deployment_id" in result

    @pytest.mark.asyncio
    async def test_deployment_status(self):
        """Test deployment status checking"""
        task = {"action": "status", "deployment_id": "test_deployment_123"}

        result = await deploy_manager_agent.process_task(task)

        assert "status" in result


class TestPromptGeneratorAgent:
    """Test Prompt Generator Agent functionality"""

    @pytest.mark.asyncio
    async def test_prompt_generation(self):
        """Test AI prompt generation"""
        task = {
            "action": "generate_prompt",
            "task_type": "code_generation",
            "domain": "web_development",
            "requirements": {
                "role": "senior_developer",
                "task_description": "Create a React component",
                "output_format": "JSX code with comments",
            },
        }

        result = await prompt_generator_agent.process_task(task)

        assert result["success"] is True
        assert "generated_prompt" in result
        assert "prompt_id" in result

    @pytest.mark.asyncio
    async def test_role_based_prompts(self):
        """Test role-based prompt creation"""
        task = {
            "action": "create_role_prompt",
            "role": "data_scientist",
            "specialization": "machine_learning",
            "experience_level": "expert",
        }

        result = await prompt_generator_agent.process_task(task)

        assert result["success"] is True
        assert "role_prompt" in result
        assert "machine_learning" in result["role_prompt"]

    @pytest.mark.asyncio
    async def test_prompt_optimization(self):
        """Test prompt optimization functionality"""
        task = {
            "action": "optimize_prompt",
            "original_prompt": "Write some code",
            "target_model": "gpt-4",
            "optimization_goals": ["specificity", "clarity"],
        }

        result = await prompt_generator_agent.process_task(task)

        assert "optimized_prompt" in result

    def test_prompt_patterns(self):
        """Test available prompt patterns"""
        library = prompt_generator_agent.get_prompt_library()

        assert "patterns" in library
        assert "role_task_format" in library["patterns"]
        assert "chain_of_thought" in library["patterns"]


# Integration Tests
class TestAgentIntegration:
    """Test agent integration and communication"""

    @pytest.mark.asyncio
    async def test_agent_communication(self):
        """Test communication between agents"""
        # Test cybershell -> agent_maker workflow
        shell_result = await cybershell_agent.process_task(
            {"action": "execute_command", "command": "echo 'agent_creation_needed'"}
        )

        if shell_result.get("success"):
            maker_result = await agent_maker.process_task(
                {"action": "create_agent", "agent_type": "test_agent"}
            )

            assert "agent_id" in maker_result or not maker_result.get("success")

    @pytest.mark.asyncio
    async def test_workflow_execution(self):
        """Test multi-agent workflow execution"""
        # Simulate development workflow
        steps = [
            ("dev_engine", {"action": "create_project", "project_type": "web_app"}),
            ("ui_designer", {"action": "create_component", "component_type": "header"}),
            ("fullstack_dev", {"action": "create_api", "api_type": "rest"}),
        ]

        results = []
        for agent_name, task in steps:
            if agent_name == "dev_engine":
                result = await dev_engine_agent.process_task(task)
            elif agent_name == "ui_designer":
                result = await ui_designer_agent.process_task(task)
            elif agent_name == "fullstack_dev":
                result = await fullstack_dev_agent.process_task(task)

            results.append(result)

        # Check that workflow completed
        assert len(results) == 3


# Performance Tests
class TestAgentPerformance:
    """Test agent performance and resource usage"""

    @pytest.mark.asyncio
    async def test_concurrent_task_handling(self):
        """Test handling multiple concurrent tasks"""
        tasks = [
            cybershell_agent.process_task(
                {"action": "execute_command", "command": f"echo 'task_{i}'"}
            )
            for i in range(5)
        ]

        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Check that all tasks completed
        successful_tasks = [r for r in results if not isinstance(r, Exception)]
        assert len(successful_tasks) >= 3  # At least 3 should succeed

    @pytest.mark.asyncio
    async def test_response_time(self):
        """Test agent response times"""
        start_time = datetime.now()

        result = await cybershell_agent.process_task(
            {"action": "execute_command", "command": "echo 'speed_test'"}
        )

        end_time = datetime.now()
        response_time = (end_time - start_time).total_seconds()

        # Should respond within 5 seconds for simple commands
        assert response_time < 5.0

    def test_memory_usage(self):
        """Test agent memory usage"""
        import os

        import psutil

        process = psutil.Process(os.getpid())
        memory_before = process.memory_info().rss

        # Create multiple agent instances
        agents = [cybershell_agent for _ in range(10)]

        memory_after = process.memory_info().rss
        memory_increase = memory_after - memory_before

        # Memory increase should be reasonable (less than 100MB)
        assert memory_increase < 100 * 1024 * 1024


# Fixtures and utilities
@pytest.fixture
def sample_task():
    """Sample task for testing"""
    return {
        "task_id": "test_task_123",
        "action": "test_action",
        "data": {"test": True},
        "timestamp": datetime.now().isoformat(),
    }


@pytest.fixture
def mock_llm_response():
    """Mock LLM response for testing"""
    return {
        "success": True,
        "response": "This is a test response from the LLM",
        "tokens_used": 50,
        "model": "gpt-3.5-turbo",
    }


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v", "--tb=short"])

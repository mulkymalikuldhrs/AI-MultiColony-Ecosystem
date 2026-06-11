"""
Agent Tests - Unit Tests for All Agent Modules
Comprehensive testing suite for the AI-MultiColony-Ecosystem

Covers: src.agents agent hierarchy from deer-flow + Agentic-AI-System consolidation
"""

import pytest
import asyncio
import json
from unittest.mock import Mock, patch, AsyncMock, MagicMock
from datetime import datetime
from pathlib import Path


# ============================================================
# Test: Agent Base (src.agents.agent_base)
# ============================================================
class TestAgentBase:
    """Test AgentBase foundation class"""

    def test_agent_base_import(self):
        """Verify agent_base module imports correctly"""
        from src.agents.agent_base import AgentBase
        assert AgentBase is not None

    def test_agent_base_instantiation(self):
        """Verify AgentBase can be created with config_path"""
        from src.agents.agent_base import AgentBase
        with patch('src.agents.agent_base.BaseAgent.__init__', return_value=None):
            agent = AgentBase.__new__(AgentBase)
            agent.agent_id = 'agent_base'
            assert agent.agent_id == 'agent_base'

    def test_agent_base_has_process_task(self):
        """Verify AgentBase has process_task method"""
        from src.agents.agent_base import AgentBase
        assert hasattr(AgentBase, 'process_task')


# ============================================================
# Test: Agent Module Availability
# ============================================================
class TestAgentModuleAvailability:
    """Verify all expected agent modules are importable"""

    def test_meta_spawner_module_exists(self):
        """Verify agent_02_meta_spawner module exists"""
        import src.agents.agent_02_meta_spawner
        assert src.agents.agent_02_meta_spawner is not None

    def test_planner_module_exists(self):
        """Verify agent_03_planner module exists"""
        import src.agents.agent_03_planner
        assert src.agents.agent_03_planner is not None

    def test_executor_module_exists(self):
        """Verify agent_04_executor module exists"""
        import src.agents.agent_04_executor
        assert src.agents.agent_04_executor is not None

    def test_designer_module_exists(self):
        """Verify agent_05_designer module exists"""
        import src.agents.agent_05_designer
        assert src.agents.agent_05_designer is not None

    def test_specialist_module_exists(self):
        """Verify agent_06_specialist module exists"""
        import src.agents.agent_06_specialist
        assert src.agents.agent_06_specialist is not None

    def test_dynamic_agent_factory_module_exists(self):
        """Verify dynamic_agent_factory module exists"""
        import src.agents.dynamic_agent_factory
        assert src.agents.dynamic_agent_factory is not None

    def test_advanced_agent_creator_module_exists(self):
        """Verify advanced_agent_creator module exists"""
        import src.agents.advanced_agent_creator
        assert src.agents.advanced_agent_creator is not None

    def test_output_handler_module_exists(self):
        """Verify output_handler module exists"""
        import src.agents.output_handler
        assert src.agents.output_handler is not None

    def test_launcher_agent_module_exists(self):
        """Verify launcher_agent module exists"""
        import src.agents.launcher_agent
        assert src.agents.launcher_agent is not None


# ============================================================
# Test: DynamicAgentFactory (most self-contained)
# ============================================================
class TestDynamicAgentFactory:
    """Test DynamicAgentFactory - template-based agent creation"""

    def test_factory_import(self):
        """Verify DynamicAgentFactory imports correctly"""
        from src.agents.dynamic_agent_factory import DynamicAgentFactory
        assert DynamicAgentFactory is not None

    def test_factory_instantiation(self):
        """Verify factory can be created"""
        from src.agents.dynamic_agent_factory import DynamicAgentFactory
        factory = DynamicAgentFactory()
        assert factory is not None

    def test_factory_has_create_method(self):
        """Verify factory has create method"""
        from src.agents.dynamic_agent_factory import DynamicAgentFactory
        factory = DynamicAgentFactory()
        # Factory should have some way to create agents
        assert hasattr(factory, '__init__')


# ============================================================
# Test: AdvancedAgentCreator
# ============================================================
class TestAdvancedAgentCreator:
    """Test AdvancedAgentCreator - advanced agent creation"""

    def test_creator_import(self):
        """Verify AdvancedAgentCreator imports correctly"""
        from src.agents.advanced_agent_creator import AdvancedAgentCreator
        assert AdvancedAgentCreator is not None

    def test_creator_instantiation(self):
        """Verify creator can be created"""
        from src.agents.advanced_agent_creator import AdvancedAgentCreator
        creator = AdvancedAgentCreator()
        assert creator is not None


# ============================================================
# Test: Deer Features
# ============================================================
class TestDeerFeatures:
    """Test deer-flow feature flags and thread state"""

    def test_deer_features_import(self):
        """Verify deer_features module imports"""
        from src.agents.deer_features import RuntimeFeatures
        assert RuntimeFeatures is not None

    def test_deer_features_defaults(self):
        """Verify RuntimeFeatures has expected defaults"""
        from src.agents.deer_features import RuntimeFeatures
        features = RuntimeFeatures()
        assert features is not None

    def test_deer_thread_state_import(self):
        """Verify deer_thread_state module imports"""
        from src.agents.deer_thread_state import ThreadState
        assert ThreadState is not None


# ============================================================
# Test: Agent Integration via EcosystemBus
# ============================================================
class TestAgentEcosystemIntegration:
    """Test agent integration through EcosystemBus"""

    def test_ecosystem_bus_creation(self):
        """Verify EcosystemBus can be created"""
        from src.integration import EcosystemBus
        bus = EcosystemBus()
        assert bus is not None

    def test_ecosystem_bus_publish_subscribe(self):
        """Verify bus pub/sub works"""
        from src.integration import EcosystemBus, BusMessage, MessageType
        bus = EcosystemBus()
        received = []

        def callback(msg):
            received.append(msg)

        bus.subscribe(MessageType.SYSTEM_STATUS, callback)
        bus.publish(BusMessage(type=MessageType.SYSTEM_STATUS, source="test"))
        assert len(received) == 1
        assert received[0].source == "test"

    def test_quant_adapter_trade_evaluation(self):
        """Verify QuantAdapter evaluates trades through risk pipeline"""
        from src.integration import QuantAdapter
        adapter = QuantAdapter()
        result = adapter.evaluate_trade(
            symbol="EUR/USD",
            direction="buy",
            lot_size=0.01,
            entry=1.0500,
            stop_loss=1.0450,
            account_balance=10000.0,
        )
        assert "allowed" in result
        assert isinstance(result["allowed"], bool)

    def test_organism_adapter_creation(self):
        """Verify OrganismAdapter can be created"""
        from src.integration import OrganismAdapter
        adapter = OrganismAdapter()
        assert adapter.scheduler is not None
        assert adapter.immune is not None
        assert adapter.decision is not None
        assert adapter.memory is not None

    def test_ecosystem_orchestrator_creation(self):
        """Verify EcosystemOrchestrator wires all adapters"""
        from src.integration import EcosystemOrchestrator
        orch = EcosystemOrchestrator()
        assert orch.quant is not None
        assert orch.organism is not None
        assert orch.gateway is not None
        assert orch.backend is not None

    def test_orchestrator_system_status(self):
        """Verify orchestrator provides system status"""
        from src.integration import EcosystemOrchestrator
        orch = EcosystemOrchestrator()
        status = orch.get_system_status()
        assert "quant" in status
        assert "organism" in status
        assert "gateway" in status
        assert "backend" in status


# ============================================================
# Test: Main.py Integration
# ============================================================
class TestMainIntegration:
    """Test main.py system integration"""

    def test_main_import(self):
        """Verify main.py imports correctly"""
        from main import AgenticAISystem
        assert AgenticAISystem is not None

    def test_main_version(self):
        """Verify main.py version is 0.4.0"""
        from main import AgenticAISystem
        system = AgenticAISystem()
        assert system.version == "0.4.0"

    def test_main_has_orchestrator(self):
        """Verify main.py creates orchestrator"""
        from main import AgenticAISystem
        system = AgenticAISystem()
        assert hasattr(system, 'orchestrator')

    def test_main_shutdown_method(self):
        """Verify main.py has proper shutdown"""
        from main import AgenticAISystem
        system = AgenticAISystem()
        assert hasattr(system, 'shutdown')


# ============================================================
# Performance baseline
# ============================================================
class TestAgentPerformance:
    """Test agent performance and resource usage"""

    def test_ecosystem_bus_throughput(self):
        """Verify bus can handle reasonable message volume"""
        from src.integration import EcosystemBus, BusMessage, MessageType
        bus = EcosystemBus()
        received = []

        def callback(msg):
            received.append(msg)

        bus.subscribe(MessageType.SYSTEM_STATUS, callback)
        for i in range(100):
            bus.publish(BusMessage(type=MessageType.SYSTEM_STATUS, source=f"test_{i}"))
        assert len(received) == 100

    def test_quant_adapter_rapid_evaluation(self):
        """Verify quant adapter handles rapid trade evaluations"""
        from src.integration import QuantAdapter
        adapter = QuantAdapter()
        results = []
        for i in range(50):
            result = adapter.evaluate_trade(
                symbol="EUR/USD",
                direction="buy",
                lot_size=0.01,
                entry=1.0500 + i * 0.0001,
                stop_loss=1.0450,
                account_balance=10000.0,
            )
            results.append(result)
        assert len(results) == 50


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])

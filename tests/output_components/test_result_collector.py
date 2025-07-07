import unittest
import os
from unittest.mock import patch, MagicMock
from datetime import datetime

# Ensure the src directory is in the Python path
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from src.agents.output_components.result_collector import ResultCollector
from src.agents.output_components.simulation_provider import SimulationProvider

class TestResultCollector(unittest.TestCase):
    """Test suite for the ResultCollector component."""

    def setUp(self):
        """Set up the test environment before each test."""
        self.collector = ResultCollector(use_simulation=True)
        # Patch SimulationProvider to control simulated results
        self.patcher_simulation_provider = patch('src.agents.output_components.result_collector.SimulationProvider')
        self.MockSimulationProvider = self.patcher_simulation_provider.start()

    def tearDown(self):
        """Clean up the test environment after each test."""
        self.patcher_simulation_provider.stop()

    def test_initialization(self):
        """Test that ResultCollector initializes correctly."""
        collector_live = ResultCollector(use_simulation=False)
        self.assertFalse(collector_live.use_simulation)
        self.assertTrue(self.collector.use_simulation)

    @patch('src.agents.output_components.result_collector.datetime')
    def test_collect_agent_results_with_simulation(self, mock_datetime):
        """Test collecting results with simulation enabled."""
        mock_datetime.now.return_value.isoformat.return_value = "2025-01-01T12:00:00"

        # Configure mock simulation provider
        self.MockSimulationProvider.get_simulation_for.side_effect = [
            {"agent_type": "planner_sim"},
            {"agent_type": "executor_sim"},
            {"agent_type": "designer_sim"},
            {"agent_type": "specialist_sim"},
            {"agent_type": "agent_base_sim"}
        ]

        task = {
            "request": "plan, execute, design, and get expert advice",
            "context": {
                "workflow_id": "wf_test_sim",
                "planning_completed": True,
                "execution_completed": True,
                "design_completed": True,
                "specialist_consultation": True
            }
        }

        collected = self.collector.collect_agent_results(task)

        self.assertIn("original_request", collected)
        self.assertEqual(collected["workflow_id"], "wf_test_sim")
        self.assertEqual(collected["collection_timestamp"], "2025-01-01T12:00:00")
        
        # Assert that get_simulation_for was called for expected agents
        self.MockSimulationProvider.get_simulation_for.assert_any_call('planner')
        self.MockSimulationProvider.get_simulation_for.assert_any_call('executor')
        self.MockSimulationProvider.get_simulation_for.assert_any_call('designer')
        self.MockSimulationProvider.get_simulation_for.assert_any_call('specialist')
        self.MockSimulationProvider.get_simulation_for.assert_any_call('agent_base', task)
        self.assertEqual(self.MockSimulationProvider.get_simulation_for.call_count, 5)

        # Verify collected contributions
        self.assertIn("planner", collected["agent_contributions"])
        self.assertIn("executor", collected["agent_contributions"])
        self.assertIn("designer", collected["agent_contributions"])
        self.assertIn("specialist", collected["agent_contributions"])
        self.assertIn("agent_base", collected["agent_contributions"])
        self.assertEqual(collected["agent_contributions"]["planner"]["agent_type"], "planner_sim")
        self.assertEqual(collected["agent_contributions"]["agent_base"]["agent_type"], "agent_base_sim")

    @patch('src.agents.output_components.result_collector.datetime')
    def test_collect_agent_results_no_simulation(self, mock_datetime):
        """Test collecting results when simulation is disabled (placeholder logic)."""
        mock_datetime.now.return_value.isoformat.return_value = "2025-01-01T12:00:00"
        collector_live = ResultCollector(use_simulation=False)
        task = {"request": "live data test", "context": {"workflow_id": "wf_live"}}

        collected = collector_live.collect_agent_results(task)

        self.assertIn("original_request", collected)
        self.assertEqual(collected["workflow_id"], "wf_live")
        self.assertEqual(collected["agent_contributions"], {}) # Should be empty as no real data collection is implemented
        self.MockSimulationProvider.get_simulation_for.assert_not_called() # Ensure simulation is not used

    @patch('src.agents.output_components.result_collector.datetime')
    def test_collect_agent_results_partial_completion(self, mock_datetime):
        """Test collecting results with only some agents completed."""
        mock_datetime.now.return_value.isoformat.return_value = "2025-01-01T12:00:00"
        self.MockSimulationProvider.get_simulation_for.side_effect = [
            {"agent_type": "planner_sim"},
            {"agent_type": "agent_base_sim"}
        ]
        task = {
            "request": "plan a project",
            "context": {
                "workflow_id": "wf_partial",
                "planning_completed": True,
                "execution_completed": False,
                "design_completed": False,
                "specialist_consultation": False
            }
        }
        collected = self.collector.collect_agent_results(task)
        self.assertIn("planner", collected["agent_contributions"])
        self.assertIn("agent_base", collected["agent_contributions"])
        self.assertNotIn("executor", collected["agent_contributions"])
        self.assertEqual(self.MockSimulationProvider.get_simulation_for.call_count, 2)

    @patch('src.agents.output_components.result_collector.datetime')
    def test_collect_agent_results_empty_context(self, mock_datetime):
        """Test collecting results with an empty context."""
        mock_datetime.now.return_value.isoformat.return_value = "2025-01-01T12:00:00"
        self.MockSimulationProvider.get_simulation_for.return_value = {"agent_type": "agent_base_sim"}
        task = {"request": "simple request", "context": {}}
        collected = self.collector.collect_agent_results(task)
        self.assertIn("agent_base", collected["agent_contributions"])
        self.assertNotIn("planner", collected["agent_contributions"])
        self.assertEqual(collected["workflow_id"], "standalone")
        self.MockSimulationProvider.get_simulation_for.assert_called_once_with('agent_base', task)

    @patch('src.agents.output_components.result_collector.datetime')
    def test_collect_agent_results_no_context(self, mock_datetime):
        """Test collecting results with no context key in task."""
        mock_datetime.now.return_value.isoformat.return_value = "2025-01-01T12:00:00"
        self.MockSimulationProvider.get_simulation_for.return_value = {"agent_type": "agent_base_sim"}
        task = {"request": "another simple request"}
        collected = self.collector.collect_agent_results(task)
        self.assertIn("agent_base", collected["agent_contributions"])
        self.assertEqual(collected["workflow_id"], "standalone")
        self.MockSimulationProvider.get_simulation_for.assert_called_once_with('agent_base', task)

if __name__ == '__main__':
    unittest.main()
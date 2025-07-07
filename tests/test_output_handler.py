import unittest
import os
from unittest.mock import patch, MagicMock

# Ensure the src directory is in the Python path
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.agents.output_handler import OutputHandler
from src.core.base_agent import BaseAgent

class TestOutputHandler(unittest.TestCase):
    """Test suite for the OutputHandler agent."""

    def setUp(self):
        """Set up the test environment before each test."""
        # Create a dummy config file for the agent
        self.config_path = "temp_config.yaml"
        with open(self.config_path, "w") as f:
            f.write("output_handler:\n")
            f.write("  prompts:\n")
            f.write("    some_prompt: 'Test prompt'\n")

        self.output_handler = OutputHandler(config_path=self.config_path)

    def tearDown(self):
        """Clean up the test environment after each test."""
        if os.path.exists(self.config_path):
            os.remove(self.config_path)

    def test_initialization(self):
        """Test that the OutputHandler initializes correctly."""
        self.assertIsInstance(self.output_handler, BaseAgent)
        self.assertEqual(self.output_handler.agent_id, "output_handler")
        self.assertIn('executive_summary', self.output_handler.delivery_formats)

    def test_process_task_with_valid_input(self):
        """Test the main process_task method with a valid task."""
        task = {
            "request": "plan and execute a new marketing campaign",
            "context": {
                "workflow_id": "wf_123",
                "planning_completed": True,
                "execution_completed": True,
                "design_completed": False,
                "specialist_consultation": False
            }
        }

        result = self.output_handler.process_task(task)

        self.assertIn("status", result)
        self.assertEqual(result["status"], "success")
        self.assertIn("response_type", result)
        self.assertEqual(result["response_type"], "final_deliverable")
        self.assertIn("content", result)
        self.assertIn("EXECUTIVE SUMMARY", result["content"])
        self.assertIn("planner", result["content"])
        self.assertIn("executor", result["content"])

    def test_process_task_with_invalid_input(self):
        """Test process_task with missing required fields."""
        task = {"wrong_key": "some_value"}
        result = self.output_handler.process_task(task)
        self.assertEqual(result["status"], "error")
        self.assertIn("Invalid task format", result["content"])

    def test_collect_agent_results(self):
        """Test the internal method for collecting agent results."""
        task = {
            "request": "design a new UI",
            "context": {
                "workflow_id": "wf_456",
                "design_completed": True
            }
        }
        collected = self.output_handler._collect_agent_results(task)
        self.assertIn("designer", collected["agent_contributions"])
        self.assertIn("agent_base", collected["agent_contributions"])
        self.assertEqual(collected["workflow_id"], "wf_456")

    def test_validate_completeness_quality(self):
        """Test the validation of collected results."""
        # Test for a high-quality, complete submission
        collected_results = {
            "original_request": "plan and execute",
            "agent_contributions": {
                "planner": self.output_handler._simulate_planner_results(),
                "executor": self.output_handler._simulate_executor_results(),
                "agent_base": self.output_handler._simulate_base_results({})
            }
        }
        validation = self.output_handler._validate_completeness_quality(collected_results)
        self.assertEqual(validation["completion_status"], "complete_high_quality")
        self.assertGreater(validation["quality_score"], 0.8)

        # Test for an incomplete submission
        collected_results_incomplete = {
            "original_request": "plan and execute",
            "agent_contributions": {
                "agent_base": self.output_handler._simulate_base_results({})
            }
        }
        validation_incomplete = self.output_handler._validate_completeness_quality(collected_results_incomplete)
        self.assertEqual(validation_incomplete["completion_status"], "incomplete")
        self.assertIn("Missing planner contribution", validation_incomplete["missing_components"])

    def test_generate_summary_insights(self):
        """Test the generation of summary and insights."""
        task = {"request": "Generate a report"}
        resolved_results = {
            "unified_results": {
                "planner": {"deliverables": ["plan"], "key_output": "A great plan"},
                "executor": {"deliverables": ["code"], "key_output": "Working code"}
            }
        }
        insights = self.output_handler._generate_summary_insights(resolved_results, task)
        self.assertIn("Successfully completed", insights["executive_summary"])
        self.assertEqual(len(insights["key_findings"]), 4) # 2 from agents + 2 general
        self.assertGreater(insights["metrics"]["total_deliverables"], 0)

    def test_store_and_retrieve_compiled_output(self):
        """Test storing and retrieving a compiled output."""
        task = {"request": "Test storage"}
        collected_results = {"agent_contributions": {"test_agent": {"status": "completed"}}}
        final_deliverables = {"primary_deliverable": "Test content"}

        # Mock datetime to control the output_id
        with patch('src.agents.output_handler.datetime') as mock_dt:
            mock_dt.now.return_value.strftime.return_value = "20250101_120000"
            mock_dt.now.return_value.isoformat.return_value = "2025-01-01T12:00:00"
            
            output_id = "output_20250101_120000"
            self.output_handler._store_compiled_output(output_id, task, collected_results, final_deliverables)

            retrieved_output = self.output_handler.get_compiled_output(output_id)
            self.assertIsNotNone(retrieved_output)
            self.assertEqual(retrieved_output["output_id"], output_id)
            self.assertEqual(retrieved_output["original_task"], task)

            listed_outputs = self.output_handler.list_compiled_outputs()
            self.assertEqual(len(listed_outputs), 1)
            self.assertEqual(listed_outputs[0]['output_id'], output_id)

if __name__ == '__main__':
    unittest.main()
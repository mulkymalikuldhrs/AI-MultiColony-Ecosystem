import unittest
import os
from unittest.mock import patch, MagicMock

# Ensure the src directory is in the Python path
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.agents.output_handler import OutputHandler
from src.core.base_agent import BaseAgent

class TestOutputHandlerRefactored(unittest.TestCase):
    """Test suite for the refactored OutputHandler agent."""

    def setUp(self):
        """Set up the test environment before each test."""
        self.config_path = "temp_config.yaml"
        with open(self.config_path, "w") as f:
            f.write("output_handler:\n  prompts:\n    some_prompt: 'Test prompt'\n")

        # We patch the components that OutputHandler depends on
        self.patcher_collector = patch('src.agents.output_handler.ResultCollector')
        self.patcher_validator = patch('src.agents.output_handler.ResultValidator')
        self.patcher_resolver = patch('src.agents.output_handler.ConflictResolver')
        self.patcher_generator = patch('src.agents.output_handler.ReportGenerator')
        self.patcher_store = patch('src.agents.output_handler.OutputStore')

        self.MockResultCollector = self.patcher_collector.start()
        self.MockResultValidator = self.patcher_validator.start()
        self.MockConflictResolver = self.patcher_resolver.start()
        self.MockReportGenerator = self.patcher_generator.start()
        self.MockOutputStore = self.patcher_store.start()

        # Instantiate the OutputHandler, which will now use the mocked components
        self.output_handler = OutputHandler(config_path=self.config_path)

    def tearDown(self):
        """Clean up the test environment after each test."""
        if os.path.exists(self.config_path):
            os.remove(self.config_path)
        
        self.patcher_collector.stop()
        self.patcher_validator.stop()
        self.patcher_resolver.stop()
        self.patcher_generator.stop()
        self.patcher_store.stop()

    def test_initialization(self):
        """Test that the OutputHandler initializes correctly and creates its components."""
        self.assertIsInstance(self.output_handler, BaseAgent)
        self.assertEqual(self.output_handler.agent_id, "output_handler")
        
        # Check that component instances were created
        self.MockResultCollector.assert_called_once_with(use_simulation=True)
        self.MockResultValidator.assert_called_once()
        self.MockConflictResolver.assert_called_once()
        self.MockReportGenerator.assert_called_once()
        self.MockOutputStore.assert_called_once_with(max_size=50)

    def test_process_task_orchestration_flow(self):
        """Test the main process_task method orchestrates calls to components correctly."""
        task = {
            "request": "plan and execute a new marketing campaign",
            "context": {"workflow_id": "wf_123"}
        }

        # Mock the return values of each component's main method
        mock_collector_instance = self.MockResultCollector.return_value
        mock_validator_instance = self.MockResultValidator.return_value
        mock_resolver_instance = self.MockConflictResolver.return_value
        mock_generator_instance = self.MockReportGenerator.return_value
        mock_store_instance = self.MockOutputStore.return_value

        collected_results = {"data": "collected"}
        validation_report = {"status": "valid"}
        resolved_results = {"data": "resolved", "unified_results": {}}
        summary_insights = {"summary": "great summary"}
        formatted_outputs = {"format": "pretty"}
        final_deliverables = {"deliverable": "final_package"}
        response_text = "Final report text."

        mock_collector_instance.collect_agent_results.return_value = collected_results
        mock_validator_instance.validate_results.return_value = validation_report
        mock_resolver_instance.resolve_conflicts.return_value = resolved_results
        mock_generator_instance.generate_summary_insights.return_value = summary_insights
        mock_generator_instance.format_outputs.return_value = formatted_outputs
        mock_generator_instance.generate_final_deliverables.return_value = final_deliverables
        mock_generator_instance.generate_response_text.return_value = response_text
        mock_store_instance.generate_output_id.return_value = "output_123"
        # Mock the internal call within _store_compiled_output
        mock_generator_instance._extract_all_deliverables.return_value = []


        # Execute the task
        result = self.output_handler.process_task(task)

        # Assertions to verify the orchestration flow
        mock_collector_instance.collect_agent_results.assert_called_once_with(task)
        mock_validator_instance.validate_results.assert_called_once_with(collected_results)
        mock_resolver_instance.resolve_conflicts.assert_called_once_with(collected_results)
        mock_generator_instance.generate_summary_insights.assert_called_once_with(resolved_results, task)
        mock_generator_instance.format_outputs.assert_called_once_with(resolved_results, task)
        mock_generator_instance.generate_final_deliverables.assert_called_once_with(resolved_results, summary_insights, task)
        mock_generator_instance.generate_response_text.assert_called_once_with(summary_insights, formatted_outputs, collected_results, validation_report)
        
        # Check that the output was stored
        mock_store_instance.store_output.assert_called_once()
        
        # Check the final response
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["response_type"], "final_deliverable")
        self.assertEqual(result["content"], response_text)

    def test_process_task_with_invalid_input(self):
        """Test process_task with missing required fields."""
        task = {"wrong_key": "some_value"}
        result = self.output_handler.process_task(task)
        self.assertEqual(result["status"], "error")
        self.assertIn("Invalid task format", result["content"])

    def test_get_and_list_compiled_outputs(self):
        """Test that retrieval and listing methods call the store component."""
        mock_store_instance = self.MockOutputStore.return_value
        
        # Test get
        self.output_handler.get_compiled_output("output_123")
        mock_store_instance.get_output.assert_called_once_with("output_123")

        # Test list
        self.output_handler.list_compiled_outputs()
        mock_store_instance.list_outputs.assert_called_once()

if __name__ == '__main__':
    unittest.main()
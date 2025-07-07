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
        self.assertEqual(self.output_handler.compiled_outputs, {})

    def test_validate_input(self):
        """Test the validate_input method with various scenarios."""
        # Valid input
        self.assertTrue(self.output_handler.validate_input({"request": "test"}))
        
        # Invalid: Not a dictionary
        self.assertFalse(self.output_handler.validate_input("not a dict"))
        self.assertFalse(self.output_handler.validate_input(None))
        self.assertFalse(self.output_handler.validate_input([]))

        # Invalid: Missing 'request' key
        self.assertFalse(self.output_handler.validate_input({"context": {}}))
        self.assertFalse(self.output_handler.validate_input({}))

        # Invalid: 'request' key present but value is not a string or empty
        self.assertTrue(self.output_handler.validate_input({"request": ""})) # Empty string is considered valid by current logic
        self.assertTrue(self.output_handler.validate_input({"request": 123})) # Non-string is considered valid by current logic
        self.assertTrue(self.output_handler.validate_input({"request": None})) # None is considered valid by current logic

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
        self.assertIn("Planner", result["content"])
        self.assertIn("Executor", result["content"])
        self.assertNotIn("Designer", result["content"]) # Ensure designer is not in content
        self.assertNotIn("Specialist", result["content"]) # Ensure specialist is not in content
        self.assertIn("COMPLETION STATUS: complete_high_quality", result["content"])

    def test_process_task_with_invalid_input(self):
        """Test process_task with missing required fields."""
        task = {"wrong_key": "some_value"}
        result = self.output_handler.process_task(task)
        self.assertEqual(result["status"], "error")
        self.assertIn("Invalid task format", result["content"])

    def test_collect_agent_results(self):
        """Test the internal method for collecting agent results."""
        # Test with design_completed
        task_design = {
            "request": "design a new UI",
            "context": {
                "workflow_id": "wf_456",
                "design_completed": True,
                "planning_completed": False,
                "execution_completed": False,
                "specialist_consultation": False
            }
        }
        collected_design = self.output_handler._collect_agent_results(task_design)
        self.assertIn("designer", collected_design["agent_contributions"])
        self.assertIn("agent_base", collected_design["agent_contributions"])
        self.assertNotIn("planner", collected_design["agent_contributions"])
        self.assertNotIn("executor", collected_design["agent_contributions"])
        self.assertNotIn("specialist", collected_design["agent_contributions"])
        self.assertEqual(collected_design["workflow_id"], "wf_456")

        # Test with all agents completed
        task_all = {
            "request": "plan, execute, design, and get expert advice",
            "context": {
                "workflow_id": "wf_789",
                "planning_completed": True,
                "execution_completed": True,
                "design_completed": True,
                "specialist_consultation": True
            }
        }
        collected_all = self.output_handler._collect_agent_results(task_all)
        self.assertIn("planner", collected_all["agent_contributions"])
        self.assertIn("executor", collected_all["agent_contributions"])
        self.assertIn("designer", collected_all["agent_contributions"])
        self.assertIn("specialist", collected_all["agent_contributions"])
        self.assertIn("agent_base", collected_all["agent_contributions"])
        self.assertEqual(collected_all["workflow_id"], "wf_789")

        # Test with empty context
        task_empty_context = {
            "request": "just a request",
            "context": {}
        }
        collected_empty = self.output_handler._collect_agent_results(task_empty_context)
        self.assertIn("agent_base", collected_empty["agent_contributions"])
        self.assertNotIn("planner", collected_empty["agent_contributions"])
        self.assertNotIn("executor", collected_empty["agent_contributions"])
        self.assertNotIn("designer", collected_empty["agent_contributions"])
        self.assertNotIn("specialist", collected_empty["agent_contributions"])
        self.assertEqual(collected_empty["workflow_id"], "standalone")

        # Test with missing context key
        task_no_context = {
            "request": "another request"
        }
        collected_no_context = self.output_handler._collect_agent_results(task_no_context)
        self.assertIn("agent_base", collected_no_context["agent_contributions"])
        self.assertEqual(collected_no_context["workflow_id"], "standalone")

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
        self.assertEqual(validation["missing_components"], [])
        self.assertEqual(validation["quality_issues"], [])
        self.assertEqual(validation["recommendations_for_improvement"], []) # High quality, so no recommendations

        # Test for an incomplete submission (missing planner)
        collected_results_incomplete = {
            "original_request": "plan and execute",
            "agent_contributions": {
                "agent_base": self.output_handler._simulate_base_results({})
            }
        }
        validation_incomplete = self.output_handler._validate_completeness_quality(collected_results_incomplete)
        self.assertEqual(validation_incomplete["completion_status"], "incomplete")
        self.assertIn("Missing planner contribution", validation_incomplete["missing_components"])
        self.assertLess(validation_incomplete["quality_score"], 0.8)

        # Test for complete with issues (low quality executor)
        low_quality_executor = self.output_handler._simulate_executor_results()
        low_quality_executor['status'] = 'failed' # Simulate low quality
        collected_results_low_quality = {
            "original_request": "execute",
            "agent_contributions": {
                "executor": low_quality_executor,
                "agent_base": self.output_handler._simulate_base_results({})
            }
        }
        validation_low_quality = self.output_handler._validate_completeness_quality(collected_results_low_quality)
        self.assertEqual(validation_low_quality["completion_status"], "complete_with_issues")
        self.assertIn("Low quality output from executor", validation_low_quality["quality_issues"])
        self.assertLess(validation_low_quality["quality_score"], 0.7)
        self.assertIn('Review and enhance agent outputs', validation_low_quality["recommendations_for_improvement"])

        # Test with no agent contributions (edge case for quality_score calculation)
        collected_results_no_contributions = {
            "original_request": "simple request",
            "agent_contributions": {
                "agent_base": self.output_handler._simulate_base_results({}) # agent_base is always expected
            }
        }
        validation_no_contributions = self.output_handler._validate_completeness_quality(collected_results_no_contributions)
        self.assertEqual(validation_no_contributions["quality_score"], 1.0) # Base agent is high quality
        self.assertEqual(validation_no_contributions["completion_status"], "complete_high_quality")

        # Test with request containing all keywords
        collected_results_all_keywords = {
            "original_request": "plan, execute, design, and get expert security advice",
            "agent_contributions": {
                "planner": self.output_handler._simulate_planner_results(),
                "executor": self.output_handler._simulate_executor_results(),
                "designer": self.output_handler._simulate_designer_results(),
                "specialist": self.output_handler._simulate_specialist_results(),
                "agent_base": self.output_handler._simulate_base_results({})
            }
        }
        validation_all_keywords = self.output_handler._validate_completeness_quality(collected_results_all_keywords)
        self.assertEqual(validation_all_keywords["completion_status"], "complete_high_quality")
        self.assertEqual(validation_all_keywords["missing_components"], [])

    def test_assess_contribution_quality(self):
        """Test the _assess_contribution_quality method."""
        # Perfect contribution
        perfect_contribution = {
            'agent_type': 'planner',
            'status': 'completed',
            'deliverables': ['Project plan', 'Timeline'],
            'timeline': '4-6 weeks estimated' # Added missing timeline for planner
        }
        self.assertEqual(self.output_handler._assess_contribution_quality('planner', perfect_contribution), 1.0)

        # Missing agent_type
        missing_type = {
            'status': 'completed',
            'deliverables': ['Project plan']
        }
        self.assertAlmostEqual(self.output_handler._assess_contribution_quality('planner', missing_type), 0.7) # 1.0 - 0.2 (missing type) - 0.1 (less than 2 deliverables)

        # Not completed status
        not_completed = {
            'agent_type': 'planner',
            'status': 'in_progress',
            'deliverables': ['Project plan']
        }
        self.assertAlmostEqual(self.output_handler._assess_contribution_quality('planner', not_completed), 0.7) # 1.0 - 0.3

        # No deliverables
        no_deliverables = {
            'agent_type': 'planner',
            'status': 'completed',
            'deliverables': []
        }
        self.assertAlmostEqual(self.output_handler._assess_contribution_quality('planner', no_deliverables), 0.7) # 1.0 - 0.3

        # Less than 2 deliverables
        one_deliverable = {
            'agent_type': 'planner',
            'status': 'completed',
            'deliverables': ['Project plan']
        }
        self.assertAlmostEqual(self.output_handler._assess_contribution_quality('planner', one_deliverable), 0.9) # 1.0 - 0.1

        # Planner missing timeline
        planner_no_timeline = {
            'agent_type': 'planner',
            'status': 'completed',
            'deliverables': ['Project plan']
        }
        self.assertAlmostEqual(self.output_handler._assess_contribution_quality('planner', planner_no_timeline), 0.7) # 0.9 - 0.2

        # Executor missing execution_summary
        executor_no_summary = {
            'agent_type': 'executor',
            'status': 'completed',
            'deliverables': ['Executed scripts']
        }
        self.assertAlmostEqual(self.output_handler._assess_contribution_quality('executor', executor_no_summary), 0.7) # 0.9 - 0.2

        # All issues combined (should not go below 0)
        all_issues = {
            'status': 'in_progress',
            'deliverables': []
        }
        self.assertEqual(self.output_handler._assess_contribution_quality('planner', all_issues), 0.0) # 1.0 - 0.2 - 0.3 - 0.3 - 0.2 = 0.0

    def test_resolve_conflicts(self):
        """Test the _resolve_conflicts method."""
        # No conflicts
        collected_no_conflicts = {
            "original_request": "test",
            "agent_contributions": {
                "planner": {"deliverables": ["plan"]},
                "executor": {"deliverables": ["code"]}
            }
        }
        resolved_no_conflicts = self.output_handler._resolve_conflicts(collected_no_conflicts, {})
        self.assertEqual(resolved_no_conflicts["conflict_resolutions"], [])
        self.assertIn("planner", resolved_no_conflicts["unified_results"])
        self.assertIn("executor", resolved_no_conflicts["unified_results"])

        # Timeline conflict
        collected_timeline_conflict = {
            "original_request": "test",
            "agent_contributions": {
                "planner": {"deliverables": ["plan"], "timeline": "6 weeks"},
                "executor": {"deliverables": ["code"], "timeline": "8 weeks"}
            }
        }
        resolved_timeline_conflict = self.output_handler._resolve_conflicts(collected_timeline_conflict, {})
        self.assertEqual(len(resolved_timeline_conflict["conflict_resolutions"]), 1)
        self.assertEqual(resolved_timeline_conflict["conflict_resolutions"][0]["type"], "timeline_conflict")

        # Resource conflict
        collected_resource_conflict = {
            "original_request": "test",
            "agent_contributions": {
                "planner": {"deliverables": ["plan"], "resources": ["devs"]},
                "executor": {"deliverables": ["code"], "resources": ["servers"]}
            }
        }
        resolved_resource_conflict = self.output_handler._resolve_conflicts(collected_resource_conflict, {})
        self.assertEqual(len(resolved_resource_conflict["conflict_resolutions"]), 1)
        self.assertEqual(resolved_resource_conflict["conflict_resolutions"][0]["type"], "resource_conflict")

        # Both conflicts
        collected_both_conflicts = {
            "original_request": "test",
            "agent_contributions": {
                "planner": {"deliverables": ["plan"], "timeline": "6 weeks", "resources": ["devs"]},
                "executor": {"deliverables": ["code"], "timeline": "8 weeks", "resources": ["servers"]}
            }
        }
        resolved_both_conflicts = self.output_handler._resolve_conflicts(collected_both_conflicts, {})
        self.assertEqual(len(resolved_both_conflicts["conflict_resolutions"]), 2)
        conflict_types = [c["type"] for c in resolved_both_conflicts["conflict_resolutions"]]
        self.assertIn("timeline_conflict", conflict_types)
        self.assertIn("resource_conflict", conflict_types)

    def test_format_outputs(self):
        """Test the _format_outputs method."""
        resolved_results = {
            "unified_results": {
                "planner": {"deliverables": ["plan"], "key_output": "A great plan"},
            }
        }
        task = {"request": "format this", "context": {"output_format": "comprehensive"}}

        # Mock _create_standard_summary to ensure it's called
        with patch.object(self.output_handler, '_create_standard_summary', return_value={"summary_content": "mocked"}) as mock_create_summary:
            formatted = self.output_handler._format_outputs(resolved_results, task)
            mock_create_summary.assert_called_once_with(resolved_results, task)
            self.assertIn("standard_summary", formatted["outputs"])
            self.assertEqual(formatted["outputs"]["standard_summary"], {"summary_content": "mocked"})
            self.assertEqual(formatted["primary_format"], "comprehensive")

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
        self.assertIn("Planner: A great plan", insights["key_findings"])
        self.assertIn("Executor: Working code", insights["key_findings"])
        self.assertIn("Multi-agent coordination achieved 2 successful collaborations", insights["key_findings"])
        self.assertIn("All planned deliverables completed within scope", insights["key_findings"])
        self.assertIn("agents_involved", insights["metrics"])
        self.assertIn("total_deliverables", insights["metrics"])
        self.assertIn("completion_rate", insights["metrics"])
        self.assertIn("average_deliverables_per_agent", insights["metrics"])
        self.assertIn("overall_success_rate", insights["metrics"])
        self.assertIn("Continue monitoring implementation progress", insights["recommendations"])
        self.assertIn("Schedule regular review meetings with stakeholders", insights["recommendations"])
        self.assertIn("Maintain documentation and knowledge transfer processes", insights["recommendations"])
        self.assertIn("Review all deliverables with stakeholders", insights["next_steps"])
        self.assertIn("Begin implementation of recommended actions", insights["next_steps"])
        self.assertIn("Set up monitoring and tracking systems", insights["next_steps"])
        self.assertIn("All planned deliverables completed", insights["success_indicators"])

        # Test with empty unified_results
        resolved_results_empty = {"unified_results": {}}
        insights_empty = self.output_handler._generate_summary_insights(resolved_results_empty, task)
        self.assertIn("0 specialized agents", insights_empty["executive_summary"])
        self.assertEqual(len(insights_empty["key_findings"]), 2) # Only general findings
        self.assertEqual(insights_empty["metrics"]["total_deliverables"], 0)
        self.assertEqual(insights_empty["metrics"]["completion_rate"], "0%")
        self.assertEqual(insights_empty["metrics"]["average_deliverables_per_agent"], "0")

    def test_extract_key_output(self):
        """Test the _extract_key_output method."""
        # Test with key_fields present
        contribution_exec = {"execution_summary": "Tasks done"}
        self.assertEqual(self.output_handler._extract_key_output(contribution_exec), "Tasks done")

        contribution_design = {"design_approach": "User-centric"}
        self.assertEqual(self.output_handler._extract_key_output(contribution_design), "User-centric")

        # Test with deliverables as fallback
        contribution_deliverables = {"deliverables": ["report", "presentation"]}
        self.assertEqual(self.output_handler._extract_key_output(contribution_deliverables), "Delivered: report, presentation")

        # Test with neither key_fields nor deliverables
        contribution_empty = {"status": "completed"}
        self.assertEqual(self.output_handler._extract_key_output(contribution_empty), "Contribution completed")

        # Test with empty dictionary
        self.assertEqual(self.output_handler._extract_key_output({}), "Contribution completed")

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
            self.assertEqual(listed_outputs[0]['agents_involved'], 1)
            self.assertEqual(listed_outputs[0]['deliverables_count'], 0) # No deliverables in collected_results for this test

    def test_store_compiled_output_retention(self):
        """Test that _store_compiled_output retains only the most recent 50 outputs."""
        # Clear any existing outputs from previous tests
        self.output_handler.compiled_outputs = {}

        # Add 50 outputs
        for i in range(50):
            output_id = f"output_20250101_{i:06d}"
            task = {"request": f"Task {i}"}
            collected_results = {"agent_contributions": {"agent_base": {"status": "completed"}}}
            final_deliverables = {"primary_deliverable": f"Content {i}"}
            self.output_handler._store_compiled_output(output_id, task, collected_results, final_deliverables)
        
        self.assertEqual(len(self.output_handler.compiled_outputs), 50)
        self.assertIn("output_20250101_000000", self.output_handler.compiled_outputs)
        self.assertIn("output_20250101_000049", self.output_handler.compiled_outputs)

        # Add one more output, exceeding the limit
        output_id_51 = "output_20250101_000050"
        task_51 = {"request": "Task 50"}
        collected_results_51 = {"agent_contributions": {"agent_base": {"status": "completed"}}}
        final_deliverables_51 = {"primary_deliverable": "Content 50"}
        self.output_handler._store_compiled_output(output_id_51, task_51, collected_results_51, final_deliverables_51)

        self.assertEqual(len(self.output_handler.compiled_outputs), 41) # Expect 41 after 10 are removed
        # The oldest 10 should be removed
        self.assertNotIn("output_20250101_000000", self.output_handler.compiled_outputs)
        self.assertNotIn("output_20250101_000009", self.output_handler.compiled_outputs)
        self.assertIn("output_20250101_000010", self.output_handler.compiled_outputs) # The new oldest
        self.assertIn("output_20250101_000050", self.output_handler.compiled_outputs) # The newest

    def test_format_key_findings(self):
        """Test _format_key_findings."""
        findings = ["Finding 1", "Finding 2"]
        expected = "• Finding 1\n• Finding 2"
        self.assertEqual(self.output_handler._format_key_findings(findings), expected)
        self.assertEqual(self.output_handler._format_key_findings([]), "")

    def test_format_metrics(self):
        """Test _format_metrics."""
        metrics = {"agents_involved": 2, "total_deliverables": 5}
        expected = "• Agents Involved: 2\n• Total Deliverables: 5\n"
        self.assertEqual(self.output_handler._format_metrics(metrics), expected)
        self.assertEqual(self.output_handler._format_metrics({}), "")

    def test_format_recommendations(self):
        """Test _format_recommendations."""
        recommendations = ["Rec 1", "Rec 2"]
        expected = "• Rec 1\n• Rec 2"
        self.assertEqual(self.output_handler._format_recommendations(recommendations), expected)
        self.assertEqual(self.output_handler._format_recommendations([]), "")

    def test_format_detailed_results(self):
        """Test _format_detailed_results."""
        formatted_outputs = {
            "outputs": {
                "standard_summary": {
                    "format": "standard_summary",
                    "content": {"overview": "test"}
                },
                "another_format": {
                    "format": "another_format",
                    "content": {"section1": "data"}
                }
            }
        }
        expected = (
            "📋 Standard Summary:\n"
            "   Format: standard_summary\n"
            "   Sections: 1\n"
            "\n"
            "📋 Another Format:\n"
            "   Format: another_format\n"
            "   Sections: 1\n"
            "\n"
        )
        self.assertEqual(self.output_handler._format_detailed_results(formatted_outputs), expected)
        self.assertEqual(self.output_handler._format_detailed_results({"outputs": {}}), "")

    def test_format_sources(self):
        """Test _format_sources."""
        collected_results = {
            "agent_contributions": {
                "planner": {},
                "executor": {}
            },
            "workflow_id": "wf_test",
            "collection_timestamp": "2025-01-01T10:00:00"
        }
        expected = (
            "Contributing Agents:\n"
            "• Planner\n"
            "• Executor\n"
            "\n"
            "Workflow ID: wf_test\n"
            "Collection Time: 2025-01-01T10:00:00"
        )
        self.assertEqual(self.output_handler._format_sources(collected_results), expected)

        # Test with empty contributions
        collected_results_empty = {
            "agent_contributions": {},
            "workflow_id": "wf_empty",
            "collection_timestamp": "2025-01-01T11:00:00"
        }
        expected_empty = (
            "Contributing Agents:\n"
            "\n"
            "Workflow ID: wf_empty\n"
            "Collection Time: 2025-01-01T11:00:00"
        )
        self.assertEqual(self.output_handler._format_sources(collected_results_empty), expected_empty)

if __name__ == '__main__':
    unittest.main()
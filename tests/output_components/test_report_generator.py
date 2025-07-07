import unittest
import os
from unittest.mock import patch, MagicMock
from datetime import datetime

# Ensure the src directory is in the Python path
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from src.agents.output_components.report_generator import ReportGenerator

class TestReportGenerator(unittest.TestCase):
    """Test suite for the ReportGenerator component."""

    def setUp(self):
        """Set up the test environment before each test."""
        self.generator = ReportGenerator()
        self.mock_resolved_results = {
            "unified_results": {
                "planner": {
                    "agent_id": "planner",
                    "deliverables": ["Project Plan", "Timeline"],
                    "key_output": "Strategic plan outlined"
                },
                "executor": {
                    "agent_id": "executor",
                    "deliverables": ["Codebase", "Deployment Script"],
                    "key_output": "Features implemented"
                },
                "agent_base": {
                    "agent_id": "agent_base",
                    "deliverables": [],
                    "key_output": "Workflow coordinated"
                }
            }
        }
        self.mock_task = {"request": "Develop a new feature for the platform"}
        self.mock_summary_insights = {
            "executive_summary": "Project successfully completed.",
            "key_findings": ["Finding 1", "Finding 2"],
            "metrics": {"total_deliverables": 4, "completion_rate": "100%"},
            "recommendations": ["Recommendation A", "Recommendation B"],
            "next_steps": ["Next Step X", "Next Step Y"]
        }
        self.mock_formatted_outputs = {
            "standard_summary": {
                "format": "standard_summary",
                "content": {"overview": "summary content"}
            },
            "detailed_report": {
                "format": "detailed_report",
                "content": {"sections": 5}
            }
        }
        self.mock_collected_results = {
            "agent_contributions": {
                "planner": {},
                "executor": {}
            },
            "workflow_id": "wf_test",
            "collection_timestamp": "2025-01-01T10:00:00"
        }
        self.mock_validation_report = {
            "completion_status": "complete_high_quality"
        }

    @patch('src.agents.output_components.report_generator.datetime')
    def test_generate_final_deliverables(self, mock_datetime):
        """Test generation of final deliverables package."""
        mock_datetime.now.return_value.isoformat.return_value = "2025-01-01T12:00:00"
        
        # Mock internal calls
        with patch.object(self.generator, 'format_outputs', return_value=self.mock_formatted_outputs) as mock_format_outputs:
            deliverables = self.generator.generate_final_deliverables(
                self.mock_resolved_results, self.mock_summary_insights, self.mock_task
            )
            mock_format_outputs.assert_called_once_with(self.mock_resolved_results, self.mock_task)

            self.assertIn("primary_deliverable", deliverables)
            self.assertEqual(deliverables["primary_deliverable"], self.mock_formatted_outputs["standard_summary"])
            self.assertIn("alternative_formats", deliverables)
            self.assertEqual(deliverables["alternative_formats"]["detailed_report"], self.mock_formatted_outputs["detailed_report"])
            self.assertIn("supporting_documents", deliverables)
            self.assertEqual(deliverables["supporting_documents"]["executive_summary"], self.mock_summary_insights["executive_summary"])
            self.assertIn("delivery_metadata", deliverables)
            self.assertEqual(deliverables["delivery_metadata"]["created_at"], "2025-01-01T12:00:00")
            self.assertTrue(deliverables["delivery_metadata"]["quality_assured"])

    def test_format_outputs(self):
        """Test formatting of outputs."""
        with patch.object(self.generator, '_create_standard_summary', return_value={"summary_content": "mocked"}) as mock_create_summary:
            formatted = self.generator.format_outputs(self.mock_resolved_results, self.mock_task)
            mock_create_summary.assert_called_once_with(self.mock_resolved_results, self.mock_task)
            self.assertIn("standard_summary", formatted)
            self.assertEqual(formatted["standard_summary"], {"summary_content": "mocked"})

    def test_generate_summary_insights(self):
        """Test generation of summary and insights."""
        insights = self.generator.generate_summary_insights(self.mock_resolved_results, self.mock_task)
        self.assertIn("executive_summary", insights)
        self.assertIn("key_findings", insights)
        self.assertIn("metrics", insights)
        self.assertIn("recommendations", insights)
        self.assertIn("next_steps", insights)
        self.assertIsInstance(insights["executive_summary"], str)
        self.assertIsInstance(insights["key_findings"], list)
        self.assertIsInstance(insights["metrics"], dict)

    def test_generate_response_text(self):
        """Test generation of the final user-facing response text."""
        response_text = self.generator.generate_response_text(
            self.mock_summary_insights, self.mock_formatted_outputs, self.mock_collected_results, self.mock_validation_report
        )
        self.assertIn("EXECUTIVE SUMMARY: Project successfully completed.", response_text)
        self.assertIn("KEY FINDINGS:", response_text)
        self.assertIn("METRICS:", response_text)
        self.assertIn("RECOMMENDATIONS:", response_text)
        self.assertIn("DETAILED RESULTS:", response_text)
        self.assertIn("SOURCES:", response_text)
        self.assertIn("COMPLETION STATUS: complete_high_quality", response_text)
        self.assertIn("📋 Standard Summary:", response_text)
        self.assertIn("📋 Detailed Report:", response_text)
        self.assertIn("Contributing Agents:", response_text)

    def test_create_standard_summary(self):
        """Test _create_standard_summary method."""
        summary = self.generator._create_standard_summary(self.mock_resolved_results, self.mock_task)
        self.assertEqual(summary["format"], "standard_summary")
        self.assertIn(self.mock_task["request"][:200], summary["request_summary"])
        self.assertIn("planner", summary["agents_involved"])
        self.assertIn("executor", summary["agents_involved"])
        self.assertEqual(summary["completion_status"], "Completed successfully")
        self.assertIn("Project Plan", summary["key_deliverables"])
        self.assertIn("Codebase", summary["key_deliverables"])
        self.assertIn("Multi-agent system successfully processed request", summary["summary"])

    def test_create_executive_summary_text(self):
        """Test _create_executive_summary_text method."""
        summary_text = self.generator._create_executive_summary_text(
            self.mock_task["request"], self.mock_resolved_results["unified_results"]
        )
        self.assertIn("Successfully completed multi-agent workflow involving 3 specialized agents.", summary_text)
        self.assertIn("Generated 4 key deliverables", summary_text)
        self.assertIn(self.mock_task["request"][:100], summary_text)

    def test_extract_key_findings(self):
        """Test _extract_key_findings method."""
        findings = self.generator._extract_key_findings(self.mock_resolved_results["unified_results"])
        self.assertIn("Planner: Strategic plan outlined", findings)
        self.assertIn("Executor: Features implemented", findings)
        self.assertIn("Agent_base: Workflow coordinated", findings)
        self.assertIn("Multi-agent coordination achieved 3 successful collaborations.", findings)
        self.assertIn("All planned deliverables completed within scope.", findings)
        self.assertEqual(len(findings), 5) # Max 5 findings

        # Test with empty unified_results
        empty_findings = self.generator._extract_key_findings({})
        self.assertEqual(len(empty_findings), 2) # Only general findings
        self.assertIn("Multi-agent coordination achieved 0 successful collaborations.", empty_findings)

    def test_calculate_metrics(self):
        """Test _calculate_metrics method."""
        metrics = self.generator._calculate_metrics(self.mock_resolved_results["unified_results"])
        self.assertEqual(metrics["agents_involved"], 3)
        self.assertEqual(metrics["total_deliverables"], 4)
        self.assertEqual(metrics["completion_rate"], "100.0%")
        self.assertEqual(metrics["average_deliverables_per_agent"], "1.3")
        self.assertEqual(metrics["overall_success_rate"], "95%")

        # Test with empty unified_results
        empty_metrics = self.generator._calculate_metrics({})
        self.assertEqual(empty_metrics, {})

    def test_consolidate_recommendations(self):
        """Test _consolidate_recommendations method."""
        recs = self.generator._consolidate_recommendations(self.mock_resolved_results["unified_results"])
        self.assertIn("Continue monitoring implementation progress.", recs)
        self.assertIn("Schedule regular review meetings with stakeholders.", recs)
        self.assertEqual(len(recs), 2) # Only default recommendations as no agent-specific recs in mock

        # Add agent with recommendations
        mock_resolved_with_recs = {
            "unified_results": {
                "specialist": {"agent_id": "specialist", "recommendations": ["Security review"]},
                "agent_base": {"agent_id": "agent_base"}
            }
        }
        recs_with_agent = self.generator._consolidate_recommendations(mock_resolved_with_recs["unified_results"])
        self.assertIn("Follow specialist specific recommendations for optimal results.", recs_with_agent)
        self.assertEqual(len(recs_with_agent), 3)

    def test_identify_next_steps(self):
        """Test _identify_next_steps method."""
        steps = self.generator._identify_next_steps(self.mock_resolved_results["unified_results"])
        self.assertIn("Review all deliverables with stakeholders.", steps)
        self.assertIn("Begin implementation of recommended actions.", steps)
        self.assertIn("Execute project plan according to timeline.", steps) # Because planner is involved
        self.assertIn("Deploy and monitor implemented solutions.", steps) # Because executor is involved
        self.assertEqual(len(steps), 4)

        # Test with no planner/executor
        mock_resolved_no_specific = {"unified_results": {"agent_base": {"agent_id": "agent_base"}}}
        steps_no_specific = self.generator._identify_next_steps(mock_resolved_no_specific["unified_results"])
        self.assertEqual(len(steps_no_specific), 2) # Only default steps

    def test_extract_all_deliverables(self):
        """Test _extract_all_deliverables method."""
        all_deliverables = self.generator._extract_all_deliverables(self.mock_resolved_results["unified_results"])
        self.assertIn("Project Plan", all_deliverables)
        self.assertIn("Timeline", all_deliverables)
        self.assertIn("Codebase", all_deliverables)
        self.assertIn("Deployment Script", all_deliverables)
        self.assertEqual(len(all_deliverables), 4)

        # Test with empty unified_results
        self.assertEqual(self.generator._extract_all_deliverables({}), [])

        # Test with agents having no deliverables
        mock_resolved_no_deliverables = {
            "unified_results": {
                "agent_base": {"agent_id": "agent_base", "deliverables": []},
                "empty_agent": {"agent_id": "empty_agent"}
            }
        }
        self.assertEqual(self.generator._extract_all_deliverables(mock_resolved_no_deliverables["unified_results"]), [])

    def test_create_overall_summary(self):
        """Test _create_overall_summary method."""
        overall_summary = self.generator._create_overall_summary(
            self.mock_resolved_results["unified_results"], self.mock_task
        )
        self.assertIn("Multi-agent system successfully processed request", overall_summary)
        self.assertIn(self.mock_task["request"][:50], overall_summary)
        self.assertIn("using 3 specialized agents", overall_summary)
        self.assertIn("generating 4 deliverables", overall_summary)

        # Test with empty unified_results
        empty_summary = self.generator._create_overall_summary({}, self.mock_task)
        self.assertIn("using 0 specialized agents", empty_summary)
        self.assertIn("generating 0 deliverables", empty_summary)

    def test_format_list(self):
        """Test _format_list method."""
        self.assertEqual(self.generator._format_list(["Item 1", "Item 2"]), "• Item 1\n• Item 2")
        self.assertEqual(self.generator._format_list([]), "N/A")

    def test_format_dict(self):
        """Test _format_dict method."""
        self.assertEqual(self.generator._format_dict({"key_one": "value1", "key_two": 2}), "• Key One: value1\n• Key Two: 2")
        self.assertEqual(self.generator._format_dict({}), "N/A")

    def test_format_detailed_results(self):
        """Test _format_detailed_results method."""
        expected_output = (
            "📋 Standard Summary:\n"
            "   Format: standard_summary\n"
            "   Sections: 1\n"
            "\n"
            "📋 Detailed Report:\n"
            "   Format: detailed_report\n"
            "   Sections: N/A\n" # content is {"sections": 5}, not {"content": {"sections": 5}}
            "\n"
        )
        self.assertEqual(self.generator._format_detailed_results(self.mock_formatted_outputs), expected_output)
        self.assertEqual(self.generator._format_detailed_results({}), "No detailed results generated.")

        # Test with content key missing in formatted output
        mock_formatted_no_content = {
            "summary": {"format": "summary_format"}
        }
        expected_no_content = (
            "📋 Summary:\n"
            "   Format: summary_format\n"
            "   Sections: N/A\n"
            "\n"
        )
        self.assertEqual(self.generator._format_detailed_results(mock_formatted_no_content), expected_no_content)


    def test_format_sources(self):
        """Test _format_sources method."""
        expected_output = (
            "Contributing Agents:\n"
            "• Planner\n"
            "• Executor\n"
            "\n"
            "Workflow ID: wf_test\n"
            "Collection Time: 2025-01-01T10:00:00"
        )
        self.assertEqual(self.generator._format_sources(self.mock_collected_results), expected_output)

        # Test with empty contributions
        empty_collected_results = {
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
        self.assertEqual(self.generator._format_sources(empty_collected_results), expected_empty)


if __name__ == '__main__':
    unittest.main()
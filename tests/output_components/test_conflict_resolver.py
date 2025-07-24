import os

# Ensure the src directory is in the Python path
import sys
import unittest
from datetime import datetime
from unittest.mock import MagicMock, patch

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from colony.agents.output_components.conflict_resolver import ConflictResolver


class TestConflictResolver(unittest.TestCase):
    """Test suite for the ConflictResolver component."""

    def setUp(self):
        """Set up the test environment before each test."""
        self.resolver = ConflictResolver()

    @patch("colony.agents.output_components.conflict_resolver.datetime")
    def test_resolve_conflicts_no_conflicts(self, mock_datetime):
        """Test conflict resolution when no conflicts are present."""
        mock_datetime.now.return_value.isoformat.return_value = "2025-01-01T12:00:00"
        collected_results = {
            "original_request": "test request",
            "agent_contributions": {
                "planner": {"deliverables": ["plan"]},
                "executor": {"deliverables": ["code"]},
            },
        }
        resolved = self.resolver.resolve_conflicts(collected_results)
        self.assertEqual(resolved["conflict_resolutions"], [])
        self.assertIn("planner", resolved["unified_results"])
        self.assertIn("executor", resolved["unified_results"])
        self.assertEqual(resolved["resolution_timestamp"], "2025-01-01T12:00:00")

    @patch("colony.agents.output_components.conflict_resolver.datetime")
    def test_resolve_conflicts_timeline_conflict(self, mock_datetime):
        """Test conflict resolution with timeline conflicts."""
        mock_datetime.now.return_value.isoformat.return_value = "2025-01-01T12:00:00"
        collected_results = {
            "original_request": "test request with timeline",
            "agent_contributions": {
                "planner": {"deliverables": ["plan"], "timeline": "6 weeks"},
                "executor": {"deliverables": ["code"], "timeline": "8 weeks"},
            },
        }
        resolved = self.resolver.resolve_conflicts(collected_results)
        self.assertEqual(len(resolved["conflict_resolutions"]), 1)
        self.assertEqual(
            resolved["conflict_resolutions"][0]["type"], "timeline_conflict"
        )
        self.assertIn("planner", resolved["conflict_resolutions"][0]["affected_agents"])
        self.assertIn(
            "executor", resolved["conflict_resolutions"][0]["affected_agents"]
        )

    @patch("colony.agents.output_components.conflict_resolver.datetime")
    def test_resolve_conflicts_resource_conflict(self, mock_datetime):
        """Test conflict resolution with resource conflicts."""
        mock_datetime.now.return_value.isoformat.return_value = "2025-01-01T12:00:00"
        collected_results = {
            "original_request": "test request with resources",
            "agent_contributions": {
                "planner": {"deliverables": ["plan"], "resources": ["devs"]},
                "executor": {"deliverables": ["code"], "resources": ["servers"]},
            },
        }
        resolved = self.resolver.resolve_conflicts(collected_results)
        self.assertEqual(len(resolved["conflict_resolutions"]), 1)
        self.assertEqual(
            resolved["conflict_resolutions"][0]["type"], "resource_conflict"
        )
        self.assertIn("planner", resolved["conflict_resolutions"][0]["affected_agents"])
        self.assertIn(
            "executor", resolved["conflict_resolutions"][0]["affected_agents"]
        )

    @patch("colony.agents.output_components.conflict_resolver.datetime")
    def test_resolve_conflicts_both_conflicts(self, mock_datetime):
        """Test conflict resolution with both timeline and resource conflicts."""
        mock_datetime.now.return_value.isoformat.return_value = "2025-01-01T12:00:00"
        collected_results = {
            "original_request": "test request with both",
            "agent_contributions": {
                "planner": {
                    "deliverables": ["plan"],
                    "timeline": "6 weeks",
                    "resources": ["devs"],
                },
                "executor": {
                    "deliverables": ["code"],
                    "timeline": "8 weeks",
                    "resources": ["servers"],
                },
            },
        }
        resolved = self.resolver.resolve_conflicts(collected_results)
        self.assertEqual(len(resolved["conflict_resolutions"]), 2)
        conflict_types = [c["type"] for c in resolved["conflict_resolutions"]]
        self.assertIn("timeline_conflict", conflict_types)
        self.assertIn("resource_conflict", conflict_types)

    def test_detect_conflicts(self):
        """Test the _detect_conflicts helper method."""
        contributions = {
            "agent1": {"timeline": "T1"},
            "agent2": {"timeline": "T2"},
            "agent3": {"data": "D1"},
        }
        self.assertEqual(
            self.resolver._detect_conflicts(contributions, "timeline"),
            ["agent1", "agent2"],
        )
        self.assertEqual(
            self.resolver._detect_conflicts(contributions, "resources"), []
        )
        self.assertEqual(
            self.resolver._detect_conflicts({"agent1": {"timeline": "T1"}}, "timeline"),
            [],
        )  # Only one agent

    @patch("colony.agents.output_components.conflict_resolver.datetime")
    def test_process_agent_contribution(self, mock_datetime):
        """Test _process_agent_contribution method."""
        mock_datetime.now.return_value.isoformat.return_value = "2025-01-01T12:00:00"
        contribution = {
            "agent_type": "planner",
            "status": "completed",
            "deliverables": ["Project plan"],
            "key_insights": "Structured approach",
        }
        processed = self.resolver._process_agent_contribution("planner", contribution)
        self.assertEqual(processed["agent_id"], "planner")
        self.assertEqual(processed["status"], "completed")
        self.assertEqual(processed["deliverables"], ["Project plan"])
        self.assertEqual(processed["key_output"], "Structured approach")
        self.assertEqual(processed["metadata"]["processed_at"], "2025-01-01T12:00:00")

    def test_extract_key_output(self):
        """Test _extract_key_output method."""
        # Test with key_fields present
        self.assertEqual(
            self.resolver._extract_key_output({"execution_summary": "Tasks done"}),
            "Tasks done",
        )
        self.assertEqual(
            self.resolver._extract_key_output({"design_approach": "User-centric"}),
            "User-centric",
        )
        self.assertEqual(
            self.resolver._extract_key_output(
                {"coordination_summary": "Coordinated well"}
            ),
            "Coordinated well",
        )
        self.assertEqual(
            self.resolver._extract_key_output({"key_insights": "New insights"}),
            "New insights",
        )
        self.assertEqual(
            self.resolver._extract_key_output({"expert_analysis": "Deep dive"}),
            "Deep dive",
        )

        # Test with deliverables as fallback
        self.assertEqual(
            self.resolver._extract_key_output(
                {"deliverables": ["report", "presentation"]}
            ),
            "Delivered: report, presentation",
        )
        self.assertEqual(
            self.resolver._extract_key_output({"deliverables": [1, 2, "text"]}),
            "Delivered: 1, 2, text",
        )  # Test non-string deliverables

        # Test with neither key_fields nor deliverables
        self.assertEqual(
            self.resolver._extract_key_output({"status": "completed"}),
            "Contribution processed without a specific key output.",
        )
        self.assertEqual(
            self.resolver._extract_key_output({}),
            "Contribution processed without a specific key output.",
        )


if __name__ == "__main__":
    unittest.main()

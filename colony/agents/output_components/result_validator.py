"""
Component for validating the completeness and quality of collected agent results.
"""

from typing import Any, Dict, List


class ResultValidator:
    """Validates the completeness and quality of collected agent results."""

    # Defines keywords that trigger the expectation of a contribution from a specific agent.
    AGENT_KEYWORDS: Dict[str, List[str]] = {
        "planner": ["plan", "strategy"],
        "executor": ["execute", "implement", "code"],
        "designer": ["design", "visual", "ui"],
        "specialist": ["security", "legal", "compliance", "expert"],
    }

    def validate_results(self, collected_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validates the completeness and quality of the collected results.
        """
        validation = {
            "completion_status": "complete",
            "quality_score": 0.0,
            "missing_components": [],
            "quality_issues": [],
            "recommendations_for_improvement": [],
        }

        contributions = collected_results.get("agent_contributions", {})

        # 1. Check for completeness
        expected_agents = self._determine_expected_agents(
            collected_results.get("original_request", "")
        )
        for agent in expected_agents:
            if agent not in contributions:
                validation["missing_components"].append(f"Missing {agent} contribution")

        # 2. Assess quality of each contribution
        quality_scores = [
            self._assess_contribution_quality(agent_id, contribution)
            for agent_id, contribution in contributions.items()
        ]

        for agent_id, score in zip(contributions.keys(), quality_scores):
            if (
                score <= 0.7
            ):  # Changed to <= to include agents with exactly 0.7 quality as 'low quality'
                validation["quality_issues"].append(
                    f"Low quality output from {agent_id}"
                )

        # 3. Calculate overall quality score
        validation["quality_score"] = (
            sum(quality_scores) / len(quality_scores) if quality_scores else 0.0
        )

        # 4. Determine final completion status
        if validation["missing_components"]:
            validation["completion_status"] = "incomplete"
        elif validation["quality_score"] < 0.7:
            validation["completion_status"] = "complete_with_issues"
        else:
            validation["completion_status"] = "complete_high_quality"

        # 5. Generate improvement recommendations if needed
        if validation["quality_score"] < 0.8:
            validation["recommendations_for_improvement"] = [
                "Review and enhance agent outputs",
                "Ensure all requirements are addressed",
                "Improve consistency across deliverables",
            ]

        return validation

    def _determine_expected_agents(self, original_request: str) -> List[str]:
        """Determines which agents were expected based on the request text."""
        request_lower = original_request.lower()
        expected = ["agent_base"]
        for agent, keywords in self.AGENT_KEYWORDS.items():
            if any(word in request_lower for word in keywords):
                expected.append(agent)
        return expected

    def _assess_contribution_quality(
        self, agent_id: str, contribution: Dict[str, Any]
    ) -> float:
        """
        Assesses the quality of an individual agent's contribution.
        Returns a score between 0.0 and 1.0.
        """
        quality_score = 1.0

        # Check for required fields
        required_fields = ["agent_type", "status", "deliverables"]
        missing_fields = [
            field for field in required_fields if field not in contribution
        ]
        quality_score -= 0.2 * len(missing_fields)

        # Check completion status
        if contribution.get("status") != "completed":
            quality_score -= 0.3

        # Check for deliverables
        deliverables = contribution.get("deliverables", [])
        if not deliverables:
            quality_score -= 0.3
        elif len(deliverables) < 2:
            quality_score -= 0.1

        # Agent-specific quality checks
        if agent_id == "planner" and "timeline" not in contribution:
            quality_score -= 0.2
        if agent_id == "executor" and "execution_summary" not in contribution:
            quality_score -= 0.2

        return max(0.0, quality_score)

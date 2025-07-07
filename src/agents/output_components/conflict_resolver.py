"""
Component for resolving conflicts and inconsistencies among agent results.
"""

from typing import Dict, Any, List
from datetime import datetime

class ConflictResolver:
    """Resolves conflicts and inconsistencies in collected agent results."""

    def resolve_conflicts(self, collected_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Identifies and resolves conflicts in the contributions from different agents.
        """
        contributions = collected_results.get('agent_contributions', {})
        resolved = {
            'original_request': collected_results.get('original_request'),
            'unified_results': {},
            'conflict_resolutions': [],
            'resolution_timestamp': datetime.now().isoformat()
        }

        # Detect and log potential conflicts
        timeline_conflicts = self._detect_conflicts(contributions, 'timeline')
        if timeline_conflicts:
            resolved['conflict_resolutions'].append({
                'type': 'timeline_conflict',
                'resolution': 'Used most detailed timeline from planner (simulated resolution)',
                'affected_agents': timeline_conflicts
            })

        resource_conflicts = self._detect_conflicts(contributions, 'resources')
        if resource_conflicts:
            resolved['conflict_resolutions'].append({
                'type': 'resource_conflict',
                'resolution': 'Consolidated resource requirements (simulated resolution)',
                'affected_agents': resource_conflicts
            })

        # Unify results by processing each contribution
        for agent_id, contribution in contributions.items():
            resolved['unified_results'][agent_id] = self._process_agent_contribution(agent_id, contribution)
            
        return resolved

    def _detect_conflicts(self, contributions: Dict[str, Any], keyword: str) -> List[str]:
        """Generic function to detect agents contributing items with a specific keyword."""
        conflicting_agents = [
            agent_id for agent_id, contribution in contributions.items()
            if keyword in str(contribution)
        ]
        return conflicting_agents if len(conflicting_agents) > 1 else []

    def _process_agent_contribution(self, agent_id: str, contribution: Dict[str, Any]) -> Dict[str, Any]:
        """
        Processes and standardizes a single agent's contribution for unification.
        """
        return {
            'agent_id': agent_id,
            'contribution_type': contribution.get('agent_type', agent_id),
            'status': contribution.get('status', 'unknown'),
            'deliverables': contribution.get('deliverables', []),
            'key_output': self._extract_key_output(contribution),
            'metadata': {
                'processed_at': datetime.now().isoformat()
            }
        }

    def _extract_key_output(self, contribution: Dict[str, Any]) -> str:
        """
        Extracts the most significant piece of information from a contribution.
        """
        # Prioritize fields that are likely to contain summary information
        key_fields = [
            'execution_summary', 'design_approach', 'coordination_summary', 
            'key_insights', 'expert_analysis'
        ]
        
        for field in key_fields:
            if field in contribution:
                return str(contribution[field])
        
        # Fallback to a summary of deliverables
        deliverables = contribution.get('deliverables', [])
        if deliverables:
            return f"Delivered: {', '.join(map(str, deliverables))}"
            
        return "Contribution processed without a specific key output."
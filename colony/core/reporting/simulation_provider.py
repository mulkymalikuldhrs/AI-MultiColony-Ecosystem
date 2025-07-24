"""
Component for providing simulated agent results for testing and development.
"""

from typing import Dict, Any

class SimulationProvider:
    """Generates simulated results from different specialized agents."""

    @staticmethod
    def get_simulation_for(agent_type: str, task: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Factory method to get simulated results for a specific agent type.
        """
        if agent_type == 'planner':
            return SimulationProvider._simulate_planner_results()
        if agent_type == 'executor':
            return SimulationProvider._simulate_executor_results()
        if agent_type == 'designer':
            return SimulationProvider._simulate_designer_results()
        if agent_type == 'specialist':
            return SimulationProvider._simulate_specialist_results()
        if agent_type == 'agent_base':
            return SimulationProvider._simulate_base_results(task or {})
        return {}

    @staticmethod
    def _simulate_planner_results() -> Dict[str, Any]:
        """Simulate planner results."""
        return {
            'agent_type': 'planner',
            'status': 'completed',
            'deliverables': ['Project plan', 'Timeline', 'Resource allocation'],
            'timeline': '4-6 weeks estimated',
            'key_insights': 'Structured approach with clear milestones identified'
        }

    @staticmethod
    def _simulate_executor_results() -> Dict[str, Any]:
        """Simulate executor results."""
        return {
            'agent_type': 'executor',
            'status': 'completed',
            'deliverables': ['Executed scripts', 'API integrations', 'Data processing'],
            'execution_summary': 'All technical tasks completed successfully',
            'performance_metrics': {'success_rate': '95%', 'execution_time': '45 minutes'}
        }

    @staticmethod
    def _simulate_designer_results() -> Dict[str, Any]:
        """Simulate designer results."""
        return {
            'agent_type': 'designer',
            'status': 'completed',
            'deliverables': ['UI mockups', 'Design system', 'Visual assets'],
            'design_approach': 'Modern, user-centered design',
            'assets_created': 8
        }

    @staticmethod
    def _simulate_specialist_results() -> Dict[str, Any]:
        """Simulate specialist results."""
        return {
            'agent_type': 'specialist',
            'status': 'completed',
            'deliverables': ['Expert analysis', 'Recommendations', 'Risk assessment'],
            'domain_expertise': 'Security and compliance',
            'risk_level': 'Medium',
            'recommendations_count': 6
        }

    @staticmethod
    def _simulate_base_results(task: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate agent base coordination results."""
        # In a real scenario, this might reflect the actual agents involved
        # based on the task context.
        agents_involved = ['planner', 'executor', 'designer', 'specialist']
        
        return {
            'agent_type': 'agent_base',
            'status': 'completed',
            'coordination_summary': 'Successfully coordinated multi-agent workflow',
            'agents_involved': agents_involved,
            'workflow_efficiency': '92%'
        }
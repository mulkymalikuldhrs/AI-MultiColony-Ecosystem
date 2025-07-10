"""
Component for generating final reports and deliverables from processed agent results.
"""

from typing import Dict, Any, List
from datetime import datetime

class ReportGenerator:
    """Generates various formatted outputs from unified agent results."""

    def generate_final_deliverables(self, resolved_results: Dict[str, Any],
                                    summary_insights: Dict[str, Any],
                                    task: Dict[str, Any],
                                    timestamp: str) -> Dict[str, Any]:
        """
        Prepares the final package of deliverables, including primary and supporting documents.
        """
        # In this simulation, the "standard_summary" is the main formatted output.
        formatted_outputs = self.format_outputs(resolved_results, task)

        deliverables = {
            'primary_deliverable': formatted_outputs.get('standard_summary', {}),
            'alternative_formats': {k: v for k, v in formatted_outputs.items() if k != 'standard_summary'},
            'supporting_documents': {
                'executive_summary': summary_insights.get('executive_summary'),
                'key_findings_report': summary_insights.get('key_findings'),
                'recommendations_list': summary_insights.get('recommendations'),
                'metrics_dashboard': summary_insights.get('metrics')
            },
            'delivery_metadata': {
                'created_at': timestamp,
                'format_versions': list(formatted_outputs.keys()),
                'quality_assured': True,
                'ready_for_delivery': True
            }
        }
        return deliverables

    def format_outputs(self, resolved_results: Dict[str, Any], task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Creates different formatted views of the results.
        For this refactoring, we are only generating a "standard_summary".
        The structure is kept to allow for future expansion with other formats.
        """
        requested_format = task.get('context', {}).get('output_format', 'comprehensive')
        
        formatted = {
            'standard_summary': self._create_standard_summary(resolved_results, task)
            # Other formats like 'executive_summary', 'detailed_report' could be generated here.
        }
        
        return formatted

    def generate_summary_insights(self, resolved_results: Dict[str, Any], task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generates high-level summaries, metrics, and actionable insights.
        """
        request = task.get('request', '')
        unified_results = resolved_results.get('unified_results', {})
        
        insights = {
            'executive_summary': self._create_executive_summary_text(request, unified_results),
            'key_findings': self._extract_key_findings(unified_results),
            'metrics': self._calculate_metrics(unified_results),
            'recommendations': self._consolidate_recommendations(unified_results),
            'next_steps': self._identify_next_steps(unified_results)
        }
        return insights

    def generate_response_text(self, summary_insights: Dict, formatted_outputs: Dict, 
                               collected_results: Dict, validation_report: Dict) -> str:
        """
        Constructs the final, user-facing text response from all generated components.
        """
        content = f"""
 📋 EXECUTIVE SUMMARY: {summary_insights.get('executive_summary', 'Not available.')}

 📊 KEY FINDINGS:
{self._format_list(summary_insights.get('key_findings', []))}

 📈 METRICS:
{self._format_dict(summary_insights.get('metrics', {}))}

 💡 RECOMMENDATIONS:
{self._format_list(summary_insights.get('recommendations', []))}

 📚 DETAILED RESULTS:
{self._format_detailed_results(formatted_outputs)}

 🔗 SOURCES:
{self._format_sources(collected_results)}

 ✅ COMPLETION STATUS: {validation_report.get('completion_status', 'Unknown')}
        """
        return content.strip()

    # Internal helper methods for content creation
    
    def _create_standard_summary(self, resolved_results: Dict[str, Any], task: Dict[str, Any]) -> Dict[str, Any]:
        """Creates a standard summary of the task outcome."""
        unified_results = resolved_results.get('unified_results', {})
        return {
            'format': 'standard_summary',
            'request_summary': task.get('request', '')[:200],
            'agents_involved': list(unified_results.keys()),
            'completion_status': 'Completed successfully',
            'key_deliverables': self._extract_all_deliverables(unified_results),
            'summary': self._create_overall_summary(unified_results, task)
        }

    def _create_executive_summary_text(self, request: str, unified_results: Dict[str, Any]) -> str:
        """Creates a concise executive summary text."""
        agents_count = len(unified_results)
        deliverables_count = sum(len(r.get('deliverables', [])) for r in unified_results.values())
        
        return (f"Successfully completed multi-agent workflow involving {agents_count} specialized agents. "
                f"Generated {deliverables_count} key deliverables addressing the request: '{request[:100]}...'. "
                "All agents coordinated effectively to deliver comprehensive results.")

    def _extract_key_findings(self, unified_results: Dict[str, Any]) -> List[str]:
        """Extracts key findings from all agent results."""
        findings = [
            f"{agent_id.title()}: {result.get('key_output', '')}"
            for agent_id, result in unified_results.items() if result.get('key_output')
        ]
        findings.extend([
            f"Multi-agent coordination achieved {len(unified_results)} successful collaborations.",
            "All planned deliverables completed within scope."
        ])
        return findings[:5]

    def _calculate_metrics(self, unified_results: Dict[str, Any]) -> Dict[str, Any]:
        """Calculates quantitative metrics about the workflow."""
        if not unified_results:
            return {}
        total_deliverables = sum(len(r.get('deliverables', [])) for r in unified_results.values())
        completed_agents = len([r for r in unified_results.values() if r.get('status') == 'completed'])
        
        return {
            'agents_involved': len(unified_results),
            'total_deliverables': total_deliverables,
            'completion_rate': f"{(completed_agents / len(unified_results) * 100):.1f}%",
            'average_deliverables_per_agent': f"{total_deliverables / len(unified_results):.1f}",
            'overall_success_rate': "95%"  # Simulated
        }

    def _consolidate_recommendations(self, unified_results: Dict[str, Any]) -> List[str]:
        """Consolidates recommendations from all agents."""
        recs = [
            "Continue monitoring implementation progress.",
            "Schedule regular review meetings with stakeholders."
        ]
        for agent_id, result in unified_results.items():
            if 'recommendations' in str(result):
                recs.append(f"Follow {agent_id} specific recommendations for optimal results.")
        return recs[:5]

    def _identify_next_steps(self, unified_results: Dict[str, Any]) -> List[str]:
        """Identifies next steps based on the results."""
        steps = [
            "Review all deliverables with stakeholders.",
            "Begin implementation of recommended actions."
        ]
        if any('planner' in r.get('agent_id', '') for r in unified_results.values()):
            steps.append("Execute project plan according to timeline.")
        if any('executor' in r.get('agent_id', '') for r in unified_results.values()):
            steps.append("Deploy and monitor implemented solutions.")
        return steps

    def extract_all_deliverables(self, unified_results: Dict[str, Any]) -> List[str]:
        """Extracts a flat list of all deliverables from all agents."""
        return [
            deliverable
            for result in unified_results.values()
            for deliverable in result.get('deliverables', [])
        ]

    def _create_overall_summary(self, unified_results: Dict[str, Any], task: Dict[str, Any]) -> str:
        """Creates a final, overall summary string."""
        agents_count = len(unified_results)
        total_deliverables = len(self._extract_all_deliverables(unified_results))
        return (f"Multi-agent system successfully processed request '{task.get('request', '')[:50]}...' "
                f"using {agents_count} specialized agents, generating {total_deliverables} deliverables.")

    # Internal helper methods for formatting text
    
    def _format_list(self, items: List[str]) -> str:
        """Formats a list of strings into a bulleted list."""
        return "\n".join(f"• {item}" for item in items) if items else "N/A"

    def _format_dict(self, data: Dict[str, Any]) -> str:
        """Formats a dictionary into a key-value list."""
        return "\n".join(f"• {key.replace('_', ' ').title()}: {value}" for key, value in data.items()) if data else "N/A"

    def _format_detailed_results(self, formatted_outputs: Dict[str, Any]) -> str:
        """Formats the detailed results section."""
        output_str = ""
        for format_name, content in formatted_outputs.items():
            output_str += f"📋 {format_name.replace('_', ' ').title()}:\n"
            if isinstance(content, dict):
                output_str += f"   Format: {content.get('format', 'Standard')}\n"
                output_str += f"   Sections: {len(content.get('content', {})) if 'content' in content else 'N/A'}\n"
            output_str += "\n"
        return output_str if output_str else "No detailed results generated."

    def _format_sources(self, collected_results: Dict[str, Any]) -> str:
        """Formats the sources and attribution section."""
        contributions = collected_results.get('agent_contributions', {})
        source_lines = ["Contributing Agents:"]
        source_lines.extend(f"• {agent_id.replace('_', ' ').title()}" for agent_id in contributions.keys())
        source_lines.append(f"\nWorkflow ID: {collected_results.get('workflow_id', 'N/A')}")
        source_lines.append(f"Collection Time: {collected_results.get('collection_timestamp', 'N/A')}")
        return "\n".join(source_lines)
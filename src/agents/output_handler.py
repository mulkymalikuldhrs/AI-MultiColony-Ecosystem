"""
Output Handler - Orchestrates the final compilation and delivery of agent results.
"""

from typing import Dict, List, Any, Optional
from datetime import datetime

from ..core.base_agent import BaseAgent
from .output_components.result_collector import ResultCollector
from .output_components.result_validator import ResultValidator
from .output_components.conflict_resolver import ConflictResolver
from .output_components.report_generator import ReportGenerator
from .output_components.output_store import OutputStore

class OutputHandler(BaseAgent):
    """
    Orchestrates the final compilation and delivery of agent results
    by coordinating a set of specialized components.
    """
    
    def __init__(self, config_path: str = "config/prompts.yaml"):
        """Initializes the OutputHandler and its components."""
        super().__init__("output_handler", config_path)
        
        # Instantiate the components
        self.result_collector = ResultCollector(use_simulation=True)
        self.result_validator = ResultValidator()
        self.conflict_resolver = ConflictResolver()
        self.report_generator = ReportGenerator()
        self.output_store = OutputStore(max_size=50)
        
    def validate_input(self, task: Dict[str, Any]) -> bool:
        """Validates that the task is a dictionary and contains a 'request' key."""
        return isinstance(task, dict) and 'request' in task
        
    def process_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Processes a task by orchestrating the collection, validation,
        resolution, and generation of the final output.
        """
        if not self.validate_input(task):
            return self.format_error("Invalid task format: Missing 'request' key.")

        try:
            # Step 1: Collect results from all contributors
            self.update_status("collecting", task)
            collected_results = self.result_collector.collect_agent_results(task)
            
            # Step 2: Validate completeness and quality
            self.update_status("validating")
            validation_report = self.result_validator.validate_results(collected_results)
            
            # Step 3: Resolve conflicts and inconsistencies
            self.update_status("resolving")
            resolved_results = self.conflict_resolver.resolve_conflicts(collected_results)
            
            # Step 4: Generate summary and insights
            self.update_status("generating_insights")
            summary_insights = self.report_generator.generate_summary_insights(resolved_results, task)
            
            # Step 5: Format final outputs
            self.update_status("formatting")
            formatted_outputs = self.report_generator.format_outputs(resolved_results, task)

            # Step 6: Prepare final deliverables package
            self.update_status("finalizing")
            final_deliverables = self.report_generator.generate_final_deliverables(
                resolved_results, summary_insights, task
            )
            
            # Step 7: Generate the user-facing response text
            response_content = self.report_generator.generate_response_text(
                summary_insights, formatted_outputs, collected_results, validation_report
            )
            
            # Step 8: Store the compiled output for auditing and retrieval
            self._store_compiled_output(task, collected_results, final_deliverables, resolved_results)
            
            self.update_status("ready")
            
            # Step 9: Format and return the final response
            response = self.format_response(response_content, "final_deliverable")
            response['status'] = 'success'
            return response
            
        except Exception as e:
            self.log_error(f"An unexpected error occurred during task processing: {e}")
            return self.format_error(f"Internal error: {e}")

    def _store_compiled_output(self, task: Dict[str, Any], 
                               collected_results: Dict[str, Any], 
                               final_deliverables: Dict[str, Any],
                               resolved_results: Dict[str, Any]):
        """Stores the fully compiled output using the OutputStore component."""
        output_id = self.output_store.generate_output_id()
        
        unified_results = resolved_results.get('unified_results', {})

        compiled_output = {
            'output_id': output_id,
            'created_at': datetime.now().isoformat(),
            'original_task': task,
            'collected_results': collected_results,
            'final_deliverables': final_deliverables,
            'compilation_metadata': {
                'agents_involved': len(collected_results.get('agent_contributions', {})),
                'total_deliverables': len(self.report_generator._extract_all_deliverables(unified_results)),
                'quality_assured': True,
                'ready_for_delivery': True
            }
        }
        self.output_store.store_output(output_id, compiled_output)

    def get_compiled_output(self, output_id: str) -> Optional[Dict[str, Any]]:
        """Retrieves a compiled output from the store."""
        return self.output_store.get_output(output_id)
    
    def list_compiled_outputs(self) -> List[Dict[str, Any]]:
        """Lists all compiled outputs from the store."""
        return self.output_store.list_outputs()

    def format_error(self, message: str) -> Dict[str, str]:
        """Creates a standardized error response."""
        return {
            "status": "error",
            "type": "error",
            "content": message
        }

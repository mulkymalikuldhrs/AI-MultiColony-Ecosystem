"""
Component for storing and retrieving compiled agent outputs.
"""

from typing import Dict, List, Any, Optional
from datetime import datetime

class OutputStore:
    """Manages the persistence of compiled outputs."""

    def __init__(self, max_size: int = 50):
        """Initializes the output store."""
        self.compiled_outputs: Dict[str, Dict[str, Any]] = {}
        self.max_size = max_size

    def store_output(self, output_id: str, output_data: Dict[str, Any]):
        """
        Stores a compiled output and enforces size limits on the store.
        """
        self.compiled_outputs[output_id] = output_data
        self._enforce_max_size()

    def get_output(self, output_id: str) -> Optional[Dict[str, Any]]:
        """Retrieves a compiled output by its ID."""
        return self.compiled_outputs.get(output_id)

    def list_outputs(self) -> List[Dict[str, Any]]:
        """Lists metadata for all stored compiled outputs."""
        output_list = []
        for output_id, output in self.compiled_outputs.items():
            metadata = output.get('compilation_metadata', {})
            output_list.append({
                'output_id': output_id,
                'created_at': output.get('created_at', 'N/A'),
                'agents_involved': metadata.get('agents_involved', 0),
                'deliverables_count': metadata.get('total_deliverables', 0)
            })
        return output_list

    def _enforce_max_size(self):
        """Removes the oldest outputs if the store exceeds its maximum size."""
        if len(self.compiled_outputs) > self.max_size:
            # Sort by creation date to find the oldest ones
            try:
                sorted_ids = sorted(
                    self.compiled_outputs.keys(),
                    key=lambda k: self.compiled_outputs[k].get('created_at', '')
                )
                
                # Number of items to delete
                num_to_delete = len(self.compiled_outputs) - self.max_size
                ids_to_delete = sorted_ids[:num_to_delete]
                
                for output_id in ids_to_delete:
                    if output_id in self.compiled_outputs:
                        del self.compiled_outputs[output_id]
            except TypeError:
                # Fallback in case created_at is missing or not comparable
                keys_to_delete = list(self.compiled_outputs.keys())
                num_to_delete = len(keys_to_delete) - self.max_size
                for i in range(num_to_delete):
                    del self.compiled_outputs[keys_to_delete[i]]


    @staticmethod
    def generate_output_id() -> str:
        """Generates a unique output ID based on the current timestamp."""
        return f"output_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
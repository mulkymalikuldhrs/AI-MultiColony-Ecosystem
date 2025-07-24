# colony/core/base_agent.py
"""
Base Agent - Foundation class for all agents in the system
Made with ❤️ by Mulky Malikul Dhaher in Indonesia 🇮🇩
"""

import json
import logging
import os
import time
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Dict, List, Optional, Union


class BaseAgent(ABC):
    """
    Abstract base class for all agents in the system.
    All specialized agents must inherit from this class.
    """

    def __init__(
        self, name: str, config: Optional[Dict[str, Any]] = None, memory_manager=None
    ):
        """
        Initialize the base agent.

        Args:
            name: Unique identifier for the agent.
            config: Configuration dictionary for the agent.
            memory_manager: Instance of a memory manager for state persistence.
        """
        self.name = name
        self.agent_id = name  # For backward compatibility
        self.config = config if config is not None else {}
        self.memory = memory_manager

        self.status = "initialized"
        self.start_time = time.time()
        self.last_activity = self.start_time
        self.task_history = []
        self.current_task = None

        # Setup logging
        self.logger = logging.getLogger(f"agent.{self.name}")

        # Create output directory if it doesn't exist
        os.makedirs("agent_output", exist_ok=True)

        self.logger.info(f"Agent '{self.name}' initialized")

    @abstractmethod
    def run(self):
        """
        Run the agent's main functionality.
        This method must be overridden by subclasses.
        """
        pass

    async def process_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a task asynchronously.
        This method should be overridden by subclasses.

        Args:
            task: Task data dictionary

        Returns:
            Result dictionary
        """
        raise NotImplementedError("Subclasses must implement process_task()")

    def update_status(self, status: str, task: Optional[Dict[str, Any]] = None):
        """
        Update the agent's status.

        Args:
            status: New status
            task: Current task (optional)
        """
        self.status = status
        self.last_activity = time.time()

        if task:
            self.current_task = task

        self.logger.info(f"Status updated to: {status}")

        # Try to update status in agent registry if available
        try:
            from colony.core.agent_registry import update_agent_status

            update_agent_status(self.agent_id, status)
        except ImportError:
            pass

    def validate_input(self, task: Dict[str, Any]) -> bool:
        """
        Validate input task data.

        Args:
            task: Task data to validate

        Returns:
            True if valid, False otherwise
        """
        # Basic validation - subclasses should override for specific validation
        return isinstance(task, dict)

    def handle_error(
        self, error: Exception, task: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Handle an error during task processing.

        Args:
            error: Exception that occurred
            task: Task that caused the error (optional)

        Returns:
            Error response dictionary
        """
        error_message = str(error)
        self.logger.error(f"Error processing task: {error_message}")

        # Update status to error
        self.update_status("error")

        # Create error response
        return {
            "success": False,
            "error": error_message,
            "agent_id": self.agent_id,
            "timestamp": datetime.now().isoformat(),
        }

    def format_response(
        self, content: str, response_type: str = "text"
    ) -> Dict[str, Any]:
        """
        Format a successful response.

        Args:
            content: Response content
            response_type: Type of response (text, json, etc.)

        Returns:
            Formatted response dictionary
        """
        # Update status to completed
        self.update_status("completed")

        # Create response
        return {
            "success": True,
            "content": content,
            "type": response_type,
            "agent_id": self.agent_id,
            "timestamp": datetime.now().isoformat(),
            "processing_time": time.time() - self.last_activity,
        }

    def save_output(
        self, content: Union[str, Dict[str, Any]], filename: Optional[str] = None
    ) -> str:
        """
        Save output to a file.

        Args:
            content: Content to save
            filename: Filename to use (optional)

        Returns:
            Path to the saved file
        """
        # Generate filename if not provided
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{self.agent_id}_{timestamp}.json"

        # Ensure the filename has an extension
        if not filename.endswith(".json") and not filename.endswith(".txt"):
            filename += ".json" if isinstance(content, dict) else ".txt"

        # Create full path
        output_path = os.path.join("agent_output", filename)

        # Save content
        try:
            if isinstance(content, dict):
                with open(output_path, "w") as f:
                    json.dump(content, f, indent=2)
            else:
                with open(output_path, "w") as f:
                    f.write(str(content))

            self.logger.info(f"Output saved to {output_path}")
            return output_path
        except Exception as e:
            self.logger.error(f"Error saving output: {e}")
            return ""

    def get_status(self) -> Dict[str, Any]:
        """
        Get the agent's current status.

        Returns:
            Status dictionary
        """
        return {
            "agent_id": self.agent_id,
            "status": self.status,
            "uptime": time.time() - self.start_time,
            "last_activity": time.time() - self.last_activity,
            "task_count": len(self.task_history),
            "current_task": self.current_task,
        }

    def stop(self):
        """
        Stop the agent.
        """
        self.update_status("stopped")
        self.logger.info(f"Agent {self.agent_id} stopped")

    def restart(self):
        """
        Restart the agent.
        """
        self.update_status("restarting")
        self.logger.info(f"Agent {self.agent_id} restarting")

        # Reset agent state
        self.start_time = time.time()
        self.last_activity = self.start_time
        self.current_task = None

        # Update status to running
        self.update_status("running")
        self.logger.info(f"Agent {self.agent_id} restarted")

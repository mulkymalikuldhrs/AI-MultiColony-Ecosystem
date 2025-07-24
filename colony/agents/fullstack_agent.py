"""
FullstackAgent - Autonomous agent for fullstack development
Handles both frontend and backend development tasks
"""

import asyncio
import json
import logging
import os
import sys
import uuid
from typing import Any, Dict, List, Optional

from colony.core.base_agent import BaseAgent


class FullstackAgent(BaseAgent):
    """
    Autonomous agent for fullstack development.

    This agent can handle both frontend and backend development tasks,
    including API development, UI implementation, and integration.
    """

    def __init__(self, name=None, config=None, memory=None):
        """Initialize the agent."""
        super().__init__(name or "FullstackAgent", config, memory)

        # Set up logger
        self.logger = logging.getLogger(f"agents.{self.__class__.__name__}")

        # Default configuration
        self.default_config = {
            "model": "gpt-4",
            "temperature": 0.7,
            "max_tokens": 2000,
            "frontend_frameworks": ["react", "vue", "angular"],
            "backend_frameworks": ["fastapi", "flask", "express"],
            "database_technologies": ["postgresql", "mongodb", "sqlite"],
        }

        # Merge with provided config
        self.config = {**self.default_config, **(config or {})}

        # Initialize memory if not provided
        self.memory = memory or {}

        # Initialize state
        self.state = {"status": "idle", "current_task": None, "task_history": []}

    async def run(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Run the agent on a task.

        Args:
            task: Task to run

        Returns:
            Task result
        """
        try:
            self.logger.info(
                f"Running {self.__class__.__name__} on task: {task.get('task_id', 'unknown')}"
            )

            # Update state
            self.state["status"] = "running"
            self.state["current_task"] = task

            # Get task details
            task_id = task.get("task_id", str(uuid.uuid4()))
            task_type = task.get("type", "unknown")
            task_description = task.get("description", "")

            # Process task based on type
            if task_type == "frontend_development":
                result = await self._handle_frontend_task(task)
            elif task_type == "backend_development":
                result = await self._handle_backend_task(task)
            elif task_type == "fullstack_development":
                result = await self._handle_fullstack_task(task)
            else:
                result = await self._handle_generic_task(task)

            # Update state
            self.state["status"] = "idle"
            self.state["current_task"] = None
            self.state["task_history"].append(
                {
                    "task_id": task_id,
                    "type": task_type,
                    "description": task_description,
                    "status": "completed",
                }
            )

            return result

        except Exception as e:
            self.logger.error(f"Error in {self.__class__.__name__}: {str(e)}")

            # Update state
            self.state["status"] = "error"
            self.state["task_history"].append(
                {
                    "task_id": task.get("task_id", str(uuid.uuid4())),
                    "type": task.get("type", "unknown"),
                    "description": task.get("description", ""),
                    "status": "failed",
                    "error": str(e),
                }
            )

            return self.handle_error(e, task)

    async def _handle_frontend_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle a frontend development task.

        Args:
            task: Task to handle

        Returns:
            Task result
        """
        self.logger.info(f"Handling frontend task: {task.get('description', '')}")

        # Extract task details
        framework = task.get("framework", "react")
        components = task.get("components", [])

        # Validate framework
        if framework not in self.config["frontend_frameworks"]:
            return {
                "status": "error",
                "message": f"Unsupported frontend framework: {framework}",
                "supported_frameworks": self.config["frontend_frameworks"],
            }

        # TODO: Implement actual frontend development logic
        # This would typically involve generating code, updating files, etc.

        return {
            "status": "success",
            "type": "frontend_development",
            "framework": framework,
            "components": components,
            "message": f"Frontend task completed with {framework}",
        }

    async def _handle_backend_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle a backend development task.

        Args:
            task: Task to handle

        Returns:
            Task result
        """
        self.logger.info(f"Handling backend task: {task.get('description', '')}")

        # Extract task details
        framework = task.get("framework", "fastapi")
        endpoints = task.get("endpoints", [])
        database = task.get("database", "postgresql")

        # Validate framework and database
        if framework not in self.config["backend_frameworks"]:
            return {
                "status": "error",
                "message": f"Unsupported backend framework: {framework}",
                "supported_frameworks": self.config["backend_frameworks"],
            }

        if database not in self.config["database_technologies"]:
            return {
                "status": "error",
                "message": f"Unsupported database technology: {database}",
                "supported_databases": self.config["database_technologies"],
            }

        # TODO: Implement actual backend development logic
        # This would typically involve generating code, updating files, etc.

        return {
            "status": "success",
            "type": "backend_development",
            "framework": framework,
            "endpoints": endpoints,
            "database": database,
            "message": f"Backend task completed with {framework} and {database}",
        }

    async def _handle_fullstack_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle a fullstack development task.

        Args:
            task: Task to handle

        Returns:
            Task result
        """
        self.logger.info(f"Handling fullstack task: {task.get('description', '')}")

        # Split task into frontend and backend tasks
        frontend_task = {
            "type": "frontend_development",
            "framework": task.get("frontend_framework", "react"),
            "components": task.get("frontend_components", []),
            "description": f"Frontend part of: {task.get('description', '')}",
        }

        backend_task = {
            "type": "backend_development",
            "framework": task.get("backend_framework", "fastapi"),
            "endpoints": task.get("backend_endpoints", []),
            "database": task.get("database", "postgresql"),
            "description": f"Backend part of: {task.get('description', '')}",
        }

        # Handle frontend and backend tasks
        frontend_result = await self._handle_frontend_task(frontend_task)
        backend_result = await self._handle_backend_task(backend_task)

        # Combine results
        return {
            "status": (
                "success"
                if frontend_result["status"] == "success"
                and backend_result["status"] == "success"
                else "error"
            ),
            "type": "fullstack_development",
            "frontend": frontend_result,
            "backend": backend_result,
            "message": "Fullstack task completed",
        }

    async def _handle_generic_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle a generic task.

        Args:
            task: Task to handle

        Returns:
            Task result
        """
        self.logger.info(f"Handling generic task: {task.get('description', '')}")

        # TODO: Implement actual generic task handling logic
        # This would typically involve analyzing the task and determining the appropriate action

        return {
            "status": "success",
            "type": "generic_task",
            "message": f"Generic task completed: {task.get('description', '')}",
        }

    def handle_error(self, error: Exception, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle an error.

        Args:
            error: Error to handle
            task: Task that caused the error

        Returns:
            Error result
        """
        return {
            "status": "error",
            "type": "error",
            "message": f"Error in {self.__class__.__name__}: {str(error)}",
            "task": task,
        }

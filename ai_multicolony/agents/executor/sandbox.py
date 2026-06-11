"""Sandbox configuration and handle classes for the Executor agent."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, Optional


class SandboxConfig:
    """Configuration for a sandbox environment.

    Parameters
    ----------
    sandbox_type:
        ``"docker"`` or ``"wasm"``.
    image:
        Docker image or WASM module reference.
    cpu_limit:
        CPU core limit.
    memory_mb:
        Memory limit in megabytes.
    timeout_ms:
        Execution timeout in milliseconds.
    network:
        Whether network access is allowed.
    env:
        Environment variables to inject.
    """

    def __init__(
        self,
        sandbox_type: str = "docker",
        image: str = "python:3.12-slim",
        cpu_limit: float = 1.0,
        memory_mb: int = 512,
        timeout_ms: int = 60000,
        network: bool = False,
        env: Optional[Dict[str, str]] = None,
    ):
        self.sandbox_type = sandbox_type
        self.image = image
        self.cpu_limit = cpu_limit
        self.memory_mb = memory_mb
        self.timeout_ms = timeout_ms
        self.network = network
        self.env = env or {}


class SandboxHandle:
    """Represents a running or completed sandbox instance.

    Stores the sandbox ID, status, output, and resource usage so that
    executors can track and manage multiple sandboxes.
    """

    def __init__(self, sandbox_id: str, config: SandboxConfig):
        self.sandbox_id = sandbox_id
        self.config = config
        self.status: str = "created"  # created | running | completed | failed | timed_out
        self.exit_code: Optional[int] = None
        self.stdout: str = ""
        self.stderr: str = ""
        self.started_at: Optional[datetime] = None
        self.completed_at: Optional[datetime] = None
        self.cpu_usage: float = 0.0
        self.memory_usage_mb: float = 0.0

    @property
    def execution_time_ms(self) -> float:
        """Wall-clock execution time in milliseconds."""
        if self.started_at is None:
            return 0.0
        end = self.completed_at or datetime.utcnow()
        return (end - self.started_at).total_seconds() * 1000

    def to_dict(self) -> Dict[str, Any]:
        """Serialize handle state to a dict."""
        return {
            "sandbox_id": self.sandbox_id,
            "status": self.status,
            "exit_code": self.exit_code,
            "stdout": self.stdout[:4096],
            "stderr": self.stderr[:4096],
            "execution_time_ms": self.execution_time_ms,
            "cpu_usage": self.cpu_usage,
            "memory_usage_mb": self.memory_usage_mb,
        }

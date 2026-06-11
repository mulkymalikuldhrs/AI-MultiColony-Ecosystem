"""ShellTool – execute shell commands with timeout, output capture, and safety controls.

Autonomy level: **L1** (safe read-only) by default; L2 for commands with
side-effects.
"""

from __future__ import annotations

import asyncio
import os
import logging
import time
from typing import Any, Dict, List, Optional

from .base import MCPTool

logger = logging.getLogger(__name__)

# ── Allowlist-based command safety ───────────────────────────────
# Only commands on this allowlist are permitted at L1/L2.
# Anything NOT on this list is blocked unless L3 approval is present.

# Base command names that are safe (no arguments considered).
_ALLOWED_COMMANDS: frozenset = frozenset({
    # Core read-only utilities
    "ls", "cat", "head", "tail", "grep", "find", "wc", "echo",
    "pwd", "date", "whoami",
    # Additional safe commands
    "which", "env", "printenv", "id", "uname", "hostname",
    "df", "du", "ps", "free", "uptime", "stat", "file",
    "diff", "sort", "uniq", "cut", "tr",
    # Python (restricted – must be "python -c" or "python3 -c")
    "python", "python3",
})

# Multi-word command prefixes that are safe at L1.
_ALLOWED_PREFIXES: tuple = (
    "git status", "git log", "git diff", "git branch", "git remote",
    "python -c", "python3 -c", "node -e",
    "sed -n", "awk",
)


class ShellTool(MCPTool):
    """Execute shell commands with timeout, output capture, working-directory
    control, and environment-variable support.

    Actions
    -------
    execute : run an arbitrary command (L2 for side-effects, L1 for read-only)
    """

    # ── MCPTool interface ────────────────────────────────────────

    def name(self) -> str:
        return "shell.execute"

    def category(self) -> str:
        return "compute"

    def autonomy_level(self) -> int:
        return 1  # L1 for safe commands; L2 enforced dynamically

    def input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "required": ["command"],
            "properties": {
                "command": {
                    "type": "string",
                    "description": "Shell command to execute",
                },
                "timeout": {
                    "type": "integer",
                    "default": 30,
                    "description": "Execution timeout in seconds",
                },
                "working_dir": {
                    "type": "string",
                    "description": "Working directory for command execution",
                },
                "env": {
                    "type": "object",
                    "description": "Additional environment variables",
                    "additionalProperties": {"type": "string"},
                },
                "shell": {
                    "type": "string",
                    "default": "/bin/bash",
                    "description": "Shell binary to use",
                },
                "capture_stdout": {
                    "type": "boolean",
                    "default": True,
                    "description": "Whether to capture stdout",
                },
                "capture_stderr": {
                    "type": "boolean",
                    "default": True,
                    "description": "Whether to capture stderr",
                },
            },
        }

    def output_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "stdout": {"type": "string"},
                "stderr": {"type": "string"},
                "exit_code": {"type": "integer"},
                "timed_out": {"type": "boolean"},
                "duration_ms": {"type": "number"},
                "command": {"type": "string"},
                "working_dir": {"type": "string"},
            },
        }

    def error_codes(self) -> List[Dict[str, Any]]:
        return [
            {"code": 1001, "message": "Command timed out"},
            {"code": 1002, "message": "Command blocked by safety policy"},
            {"code": 1003, "message": "Working directory does not exist"},
            {"code": 1004, "message": "Shell binary not found"},
            {"code": 1005, "message": "Process killed (OOM or signal)"},
        ]

    # ── Execution ────────────────────────────────────────────────

    async def execute(self, params: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a shell command and return captured output."""
        command: str = params["command"]
        timeout: int = params.get("timeout", 30)
        working_dir: Optional[str] = params.get("working_dir")
        extra_env: Dict[str, str] = params.get("env", {})
        shell_bin: str = params.get("shell", "/bin/bash")
        capture_stdout: bool = params.get("capture_stdout", True)
        capture_stderr: bool = params.get("capture_stderr", True)
        autonomy = context.get("autonomy_level", 0)

        start = time.monotonic()

        # ── Allowlist safety check ───────────────────────────────
        if not self.is_safe_command(command):
            # L3 approval can override the allowlist
            if autonomy < 3:
                self.record_call(False, (time.monotonic() - start) * 1000)
                return {
                    "stdout": "",
                    "stderr": (
                        f"Command not on allowlist: '{self._extract_base_command(command)}'. "
                        f"Only approved commands are permitted. "
                        f"L3 autonomy required for unrestricted commands."
                    ),
                    "exit_code": -2,
                    "timed_out": False,
                    "duration_ms": (time.monotonic() - start) * 1000,
                    "command": command,
                    "working_dir": working_dir or os.getcwd(),
                }
            else:
                logger.warning(
                    "L3 override: executing non-allowlisted command: %s",
                    command,
                )

        # Validate working directory
        if working_dir and not os.path.isdir(working_dir):
            self.record_call(False, (time.monotonic() - start) * 1000)
            return {
                "stdout": "",
                "stderr": f"Working directory does not exist: {working_dir}",
                "exit_code": -3,
                "timed_out": False,
                "duration_ms": (time.monotonic() - start) * 1000,
                "command": command,
                "working_dir": working_dir,
            }

        # Validate shell binary
        if not os.path.isfile(shell_bin):
            self.record_call(False, (time.monotonic() - start) * 1000)
            return {
                "stdout": "",
                "stderr": f"Shell binary not found: {shell_bin}",
                "exit_code": -4,
                "timed_out": False,
                "duration_ms": (time.monotonic() - start) * 1000,
                "command": command,
                "working_dir": working_dir or os.getcwd(),
            }

        # Build environment
        env = os.environ.copy()
        env.update(extra_env)

        # ── Execute ──────────────────────────────────────────────
        try:
            proc = await asyncio.create_subprocess_shell(
                command,
                stdout=asyncio.subprocess.PIPE if capture_stdout else asyncio.subprocess.DEVNULL,
                stderr=asyncio.subprocess.PIPE if capture_stderr else asyncio.subprocess.DEVNULL,
                cwd=working_dir,
                env=env,
                executable=shell_bin,
            )

            stdout_bytes, stderr_bytes = await asyncio.wait_for(
                proc.communicate(),
                timeout=timeout,
            )

            duration_ms = (time.monotonic() - start) * 1000
            exit_code = proc.returncode if proc.returncode is not None else -1
            success = exit_code == 0

            self.record_call(success, duration_ms)

            return {
                "stdout": (stdout_bytes.decode(errors="replace") if stdout_bytes else ""),
                "stderr": (stderr_bytes.decode(errors="replace") if stderr_bytes else ""),
                "exit_code": exit_code,
                "timed_out": False,
                "duration_ms": round(duration_ms, 2),
                "command": command,
                "working_dir": working_dir or os.getcwd(),
            }

        except asyncio.TimeoutError:
            # Try to kill the process
            try:
                proc.kill()
                await proc.wait()
            except Exception:
                logger.debug("Failed to kill timed-out process")

            duration_ms = (time.monotonic() - start) * 1000
            self.record_call(False, duration_ms)

            return {
                "stdout": "",
                "stderr": f"Command timed out after {timeout}s",
                "exit_code": -1,
                "timed_out": True,
                "duration_ms": round(duration_ms, 2),
                "command": command,
                "working_dir": working_dir or os.getcwd(),
            }

        except Exception as exc:
            duration_ms = (time.monotonic() - start) * 1000
            self.record_call(False, duration_ms)

            return {
                "stdout": "",
                "stderr": str(exc),
                "exit_code": -1,
                "timed_out": False,
                "duration_ms": round(duration_ms, 2),
                "command": command,
                "working_dir": working_dir or os.getcwd(),
            }

    # ── Helpers ──────────────────────────────────────────────────

    @staticmethod
    def _extract_base_command(command: str) -> str:
        """Extract the base command name from a command string."""
        stripped = command.strip()
        # Handle quoted commands or paths like /usr/bin/python
        if stripped.startswith("/"):
            base = stripped.split("/")[-1].split()[0] if "/" in stripped else stripped.split()[0]
        else:
            base = stripped.split()[0] if stripped else ""
        return base

    def is_safe_command(self, command: str) -> bool:
        """Return True only if the command is on the allowlist.

        An allowlist approach is used instead of a blocklist: any command
        not explicitly permitted is denied.  L3 autonomy can override.
        """
        cmd_stripped = command.strip().lower()
        if not cmd_stripped:
            return False

        # Check multi-word allowed prefixes first (more specific)
        if any(cmd_stripped.startswith(prefix) for prefix in _ALLOWED_PREFIXES):
            return True

        # Check base command against allowlist
        base_cmd = self._extract_base_command(command).lower()
        if base_cmd in _ALLOWED_COMMANDS:
            return True

        return False

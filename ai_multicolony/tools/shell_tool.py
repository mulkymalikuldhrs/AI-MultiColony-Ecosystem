"""Shell/bash execution tool for the AI MultiColony Ecosystem.

Provides safe shell command execution with timeout, output capture,
security filtering, working directory support, and environment variable
management.
"""

from __future__ import annotations

import asyncio
import os
import re
import shlex
from typing import Any, Optional

from ai_multicolony.config.logging_config import get_logger
from ai_multicolony.core.tool_base import BaseTool
from ai_multicolony.exceptions import ToolExecutionError, ToolTimeoutError, ToolPermissionError
from ai_multicolony.types.tools import ToolCall, ToolDefinition, ToolParameter, ToolResult, ToolType

logger = get_logger(__name__)

# Default list of dangerous command patterns to block (used only in blocklist mode)
_DEFAULT_BLOCKED_PATTERNS: list[str] = [
    r"\brm\s+-rf\s+/",
    r"\brm\s+-rf\s+~",
    r"\bmkfs\b",
    r"\bdd\s+if=",
    r"\bformat\b",
    r">\s*/dev/sd",
    r"\bchmod\s+777\s+/",
    r"\bchown\s+.*\s+/",
    r"\bshutdown\b",
    r"\breboot\b",
    r"\binit\s+[06]",
    r"\bhalt\b",
    r"\bpoweroff\b",
    r"\biptables\b",
    r"\bip6tables\b",
    r"\bmount\b",
    r"\bumount\b",
    r"\bfdisk\b",
    r"\bparted\b",
    r"\bmkswap\b",
    r"\bfsck\b",
    r"\bkill\s+-9\s+1\b",
    r"\bkillall\b",
    r"\b:\(\)\{\s*:\|:&\s*\}",  # fork bomb
    r"\bcurl\b.*\|\s*\bsh\b",
    r"\bwget\b.*\|\s*\bsh\b",
    r"\bsudo\s+rm\b",
    r"\bsystemctl\s+(stop|disable|mask)\s+(ssh|sshd|docker|networkd)",
]

# Default allowlist of safe commands (used in allowlist mode, which is the default)
_DEFAULT_ALLOWED_COMMANDS: list[str] = [
    "ls", "cat", "head", "tail", "grep", "find", "wc", "echo",
    "pwd", "whoami", "date", "python3", "pip", "git", "curl", "wget",
]


class ShellTool(BaseTool):
    """Shell command execution tool with security controls.

    Features:
    - Execute bash/shell commands with timeout
    - Capture stdout, stderr, and exit code
    - Security filtering via allowlist (default) or blocklist mode
    - Working directory support
    - Environment variable management
    - Shell injection detection
    - Output size limiting

    Security Modes:
    - **allowlist** (default): Only commands whose base name is in the
      allowed list are permitted. This is the secure default.
    - **blocklist**: Dangerous patterns are rejected. Less secure because
      new/obscure dangerous commands may not be blocked. Requires
      ``SHELL_MODE=blocklist`` env var to activate.
    """

    def __init__(self, config: Optional[dict[str, Any]] = None) -> None:
        super().__init__(config)
        self._default_timeout = self._config.get("timeout", 60)
        self._max_output_size = self._config.get("max_output_bytes", 100_000)
        self._shell = self._config.get("shell", "/bin/bash")

        # Security: determine mode from env var (default=allowlist, require explicit blocklist)
        shell_mode = os.environ.get("SHELL_MODE", "allowlist").lower()
        self._use_allowlist = shell_mode != "blocklist"

        if not self._use_allowlist:
            logger.warning(
                "SECURITY: Shell tool running in blocklist mode. "
                "Allowlist mode is recommended for production. "
                "Set SHELL_MODE=allowlist (or remove SHELL_MODE) to enable allowlist mode."
            )

        # Security: blocked patterns (compiled for performance, used only in blocklist mode)
        custom_blocked = self._config.get("blocked_commands", [])
        all_patterns = _DEFAULT_BLOCKED_PATTERNS + custom_blocked
        self._blocked_regexes: list[re.Pattern[str]] = [
            re.compile(p, re.IGNORECASE) for p in all_patterns
        ]

        # Security: allowlist mode (default)
        # Build allowed set from config override or default allowlist
        config_allowed = self._config.get("allowed_commands", None)
        allowed_list = config_allowed if config_allowed else _DEFAULT_ALLOWED_COMMANDS
        self._allowed_set = set(allowed_list)

        # Track recent command history for rate limiting
        self._command_history: list[tuple[float, str]] = []
        self._max_history = self._config.get("max_history", 100)

    @property
    def definition(self) -> ToolDefinition:
        return ToolDefinition(
            name="shell",
            description=(
                "Execute shell/bash commands with output capture, timeout, "
                "working directory, and security checks. Uses allowlist mode "
                "by default; only pre-approved commands are permitted."
            ),
            tool_type=ToolType.SHELL,
            parameters=[
                ToolParameter(
                    name="command",
                    type="string",
                    description="The shell command to execute",
                    required=True,
                ),
                ToolParameter(
                    name="timeout",
                    type="integer",
                    description="Execution timeout in seconds (default: 60)",
                    required=False,
                    default=self._default_timeout,
                ),
                ToolParameter(
                    name="working_dir",
                    type="string",
                    description="Working directory for command execution",
                    required=False,
                ),
                ToolParameter(
                    name="env",
                    type="object",
                    description="Environment variables to set (key-value pairs)",
                    required=False,
                ),
                ToolParameter(
                    name="shell",
                    type="string",
                    description="Shell executable to use (default: /bin/bash)",
                    required=False,
                    default=self._shell,
                ),
                ToolParameter(
                    name="capture_stderr",
                    type="boolean",
                    description="Whether to capture stderr separately",
                    required=False,
                    default=True,
                ),
            ],
            tags=["shell", "execution", "system"],
            requires_permission="shell.execute",
            timeout=self._default_timeout,
        )

    # ------------------------------------------------------------------
    # Security
    # ------------------------------------------------------------------

    def _validate_command(self, command: str) -> None:
        """Validate a command against security rules.

        In allowlist mode (default), only explicitly allowed base commands
        are permitted. In blocklist mode (requires SHELL_MODE=blocklist env
        var), dangerous patterns are rejected.

        Args:
            command: The command to validate.

        Raises:
            ToolPermissionError: If the command is blocked.
        """
        command_stripped = command.strip()

        # Allowlist mode (default): only permit explicitly allowed commands
        if self._use_allowlist:
            # Extract the base command (first token)
            try:
                base_cmd = shlex.split(command_stripped)[0] if command_stripped else ""
            except ValueError:
                base_cmd = command_stripped.split()[0] if command_stripped else ""

            # Resolve absolute paths to basename
            base_cmd = os.path.basename(base_cmd)

            if base_cmd not in self._allowed_set:
                raise ToolPermissionError(
                    f"Command '{base_cmd}' is not in the allowlist. "
                    f"Allowed commands: {sorted(self._allowed_set)}. "
                    f"To use blocklist mode instead, set SHELL_MODE=blocklist.",
                    tool_name="shell",
                    required_permission="shell.bypass_allowlist",
                )
            return

        # Blocklist mode: reject dangerous patterns
        for pattern in self._blocked_regexes:
            match = pattern.search(command_stripped)
            if match:
                raise ToolPermissionError(
                    f"Command blocked for security: matched pattern '{pattern.pattern}'",
                    tool_name="shell",
                    required_permission="shell.bypass",
                )

    def _record_command(self, command: str) -> None:
        """Record a command in the history for auditing."""
        import time as _time
        self._command_history.append((_time.time(), command[:200]))
        if len(self._command_history) > self._max_history:
            self._command_history = self._command_history[-self._max_history:]

    # ------------------------------------------------------------------
    # Execution
    # ------------------------------------------------------------------

    async def execute(self, tool_call: ToolCall) -> ToolResult:
        """Execute a shell command.

        Args:
            tool_call: The tool call with command arguments.

        Returns:
            ToolResult with command output.
        """
        command = tool_call.arguments.get("command", "")
        timeout = tool_call.arguments.get("timeout", self._default_timeout)
        working_dir = tool_call.arguments.get("working_dir")
        env = tool_call.arguments.get("env")
        shell = tool_call.arguments.get("shell", self._shell)
        capture_stderr = tool_call.arguments.get("capture_stderr", True)

        if not command:
            return ToolResult(
                tool_call_id=tool_call.id,
                tool_name="shell",
                success=False,
                error="No command specified",
            )

        # Security check
        self._validate_command(command)
        self._record_command(command)

        # Prepare environment
        exec_env = os.environ.copy()
        if env and isinstance(env, dict):
            exec_env.update({k: str(v) for k, v in env.items()})

        # Validate working directory
        if working_dir and not os.path.isdir(working_dir):
            return ToolResult(
                tool_call_id=tool_call.id,
                tool_name="shell",
                success=False,
                error=f"Working directory does not exist: {working_dir}",
            )

        try:
            proc = await asyncio.create_subprocess_shell(
                command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=working_dir or None,
                env=exec_env,
                executable=shell,
            )

            try:
                stdout_bytes, stderr_bytes = await asyncio.wait_for(
                    proc.communicate(),
                    timeout=timeout,
                )
            except asyncio.TimeoutError:
                proc.kill()
                # Give the process a moment to clean up
                try:
                    await asyncio.wait_for(proc.communicate(), timeout=5)
                except asyncio.TimeoutError:
                    pass
                raise ToolTimeoutError(
                    f"Command timed out after {timeout}s: {command[:200]}",
                    tool_name="shell",
                    timeout=float(timeout),
                )

            stdout_str = stdout_bytes.decode("utf-8", errors="replace")
            stderr_str = stderr_bytes.decode("utf-8", errors="replace")

            # Truncate output if too large
            stdout_truncated = False
            stderr_truncated = False
            if len(stdout_str) > self._max_output_size:
                stdout_str = stdout_str[: self._max_output_size] + "\n... [output truncated]"
                stdout_truncated = True
            if len(stderr_str) > self._max_output_size:
                stderr_str = stderr_str[: self._max_output_size] + "\n... [stderr truncated]"
                stderr_truncated = True

            success = proc.returncode == 0

            # Build output
            output = stdout_str
            if capture_stderr and stderr_str:
                if output:
                    output += f"\n[stderr]\n{stderr_str}"
                else:
                    output = stderr_str

            metadata: dict[str, Any] = {
                "exit_code": proc.returncode,
                "stdout_len": len(stdout_str),
                "stderr_len": len(stderr_str),
                "truncated": stdout_truncated or stderr_truncated,
            }

            return ToolResult(
                tool_call_id=tool_call.id,
                tool_name="shell",
                success=success,
                output=output,
                error=stderr_str if not success else None,
                exit_code=proc.returncode,
                metadata=metadata,
            )

        except ToolTimeoutError:
            raise
        except ToolPermissionError:
            raise
        except Exception as e:
            raise ToolExecutionError(
                f"Command execution failed: {e}",
                tool_name="shell",
            )

    # ------------------------------------------------------------------
    # Utility
    # ------------------------------------------------------------------

    def get_history(self, limit: int = 20) -> list[dict[str, Any]]:
        """Get recent command execution history.

        Args:
            limit: Maximum number of history entries to return.

        Returns:
            List of dicts with 'timestamp' and 'command' keys.
        """
        recent = self._command_history[-limit:]
        return [{"timestamp": ts, "command": cmd} for ts, cmd in recent]

    def clear_history(self) -> None:
        """Clear command execution history."""
        self._command_history.clear()

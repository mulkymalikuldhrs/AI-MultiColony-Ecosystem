"""Permission engine for access control.

Manages permissions with autonomy levels (L0-L4), RBAC,
and rate limiting per agent/tool.
"""

from __future__ import annotations

import time
from collections import defaultdict
from enum import Enum
from typing import Any, Optional

from ai_multicolony.config.logging_config import get_logger
from ai_multicolony.exceptions import PermissionDeniedError

logger = get_logger(__name__)


class AutonomyLevel(str, Enum):
    """Agent autonomy levels (L0-L4).

    Defines what actions an agent can take without human approval:
    - L0: No autonomy, all actions require approval
    - L1: Read-only autonomy, can read but not modify
    - L2: Constrained autonomy, can perform safe operations
    - L3: Standard autonomy, can perform most operations
    - L4: Full autonomy, can perform all operations including dangerous ones
    """

    L0_NONE = "L0"
    L1_READONLY = "L1"
    L2_CONSTRAINED = "L2"
    L3_STANDARD = "L3"
    L4_FULL = "L4"

    @property
    def level(self) -> int:
        """Numeric level for comparison."""
        return {
            AutonomyLevel.L0_NONE: 0,
            AutonomyLevel.L1_READONLY: 1,
            AutonomyLevel.L2_CONSTRAINED: 2,
            AutonomyLevel.L3_STANDARD: 3,
            AutonomyLevel.L4_FULL: 4,
        }[self]

    def gte(self, other: AutonomyLevel) -> bool:
        """Check if this level is >= another."""
        return self.level >= other.level


class Permission(str, Enum):
    """System permissions."""

    SHELL_EXECUTE = "shell.execute"
    SHELL_BYPASS = "shell.bypass"
    FILE_READ = "file.read"
    FILE_WRITE = "file.write"
    FILE_DELETE = "file.delete"
    FILE_BYPASS_SANDBOX = "file.bypass_sandbox"
    BROWSER_USE = "browser.use"
    SEARCH_USE = "search.use"
    CODE_EXECUTE = "code.execute"
    DOCKER_MANAGE = "docker.manage"
    VOICE_USE = "voice.use"
    MCP_USE = "mcp.use"
    CHANNEL_SEND = "channel.send"
    AGENT_SPAWN = "agent.spawn"
    AGENT_TERMINATE = "agent.terminate"
    COLONY_MANAGE = "colony.manage"
    ADMIN = "admin"


# Autonomy level to permissions mapping
AUTONOMY_PERMISSIONS: dict[AutonomyLevel, set[Permission]] = {
    AutonomyLevel.L0_NONE: set(),
    AutonomyLevel.L1_READONLY: {
        Permission.FILE_READ, Permission.SEARCH_USE, Permission.BROWSER_USE,
    },
    AutonomyLevel.L2_CONSTRAINED: {
        Permission.FILE_READ, Permission.FILE_WRITE, Permission.SEARCH_USE,
        Permission.BROWSER_USE, Permission.CODE_EXECUTE, Permission.MCP_USE,
    },
    AutonomyLevel.L3_STANDARD: {
        Permission.SHELL_EXECUTE, Permission.FILE_READ, Permission.FILE_WRITE,
        Permission.BROWSER_USE, Permission.SEARCH_USE, Permission.CODE_EXECUTE,
        Permission.VOICE_USE, Permission.MCP_USE, Permission.CHANNEL_SEND,
        Permission.DOCKER_MANAGE,
    },
    AutonomyLevel.L4_FULL: set(Permission),  # All permissions
}


class RateLimitEntry:
    """Rate limit tracking for an agent/tool combination."""

    def __init__(self, window_seconds: int = 60) -> None:
        self.window_seconds = window_seconds
        self.request_count = 0
        self.window_start = time.time()

    def check(self, limit: int) -> bool:
        """Check if request is within rate limit."""
        now = time.time()
        if now - self.window_start >= self.window_seconds:
            self.request_count = 1
            self.window_start = now
            return True
        if self.request_count >= limit:
            return False
        self.request_count += 1
        return True

    @property
    def remaining(self) -> int:
        """Get remaining requests in current window."""
        return max(0, self.window_seconds - self.request_count)


class PermissionEngine:
    """Permission engine with autonomy levels, RBAC, and rate limiting.

    Features:
    - Autonomy levels L0-L4 with permission mapping
    - Role-based access control (RBAC)
    - Per-agent permission grants and revocations
    - Rate limiting per agent/tool
    - Audit logging of permission decisions
    - Permission checks and enforcement
    """

    # Default role permissions
    ROLE_PERMISSIONS: dict[str, set[Permission]] = {
        "admin": set(Permission),
        "manus": {
            Permission.SHELL_EXECUTE, Permission.FILE_READ, Permission.FILE_WRITE,
            Permission.BROWSER_USE, Permission.SEARCH_USE, Permission.CODE_EXECUTE,
            Permission.VOICE_USE, Permission.MCP_USE, Permission.CHANNEL_SEND,
        },
        "planner": {
            Permission.SEARCH_USE, Permission.MCP_USE,
        },
        "executor": {
            Permission.SHELL_EXECUTE, Permission.FILE_READ, Permission.FILE_WRITE,
            Permission.CODE_EXECUTE, Permission.DOCKER_MANAGE,
        },
        "coder": {
            Permission.SHELL_EXECUTE, Permission.FILE_READ, Permission.FILE_WRITE,
            Permission.CODE_EXECUTE, Permission.SEARCH_USE, Permission.MCP_USE,
        },
        "browser": {
            Permission.BROWSER_USE, Permission.SEARCH_USE, Permission.FILE_READ,
            Permission.FILE_WRITE, Permission.MCP_USE,
        },
        "security": {
            Permission.SHELL_EXECUTE, Permission.FILE_READ, Permission.CODE_EXECUTE,
            Permission.MCP_USE,
        },
        "researcher": {
            Permission.SEARCH_USE, Permission.BROWSER_USE, Permission.FILE_READ,
            Permission.FILE_WRITE, Permission.MCP_USE,
        },
        "voice": {
            Permission.VOICE_USE, Permission.CHANNEL_SEND, Permission.MCP_USE,
        },
        "colony": {
            Permission.AGENT_SPAWN, Permission.AGENT_TERMINATE, Permission.COLONY_MANAGE,
            Permission.SEARCH_USE, Permission.MCP_USE, Permission.CHANNEL_SEND,
        },
        "viewer": {
            Permission.FILE_READ, Permission.SEARCH_USE,
        },
    }

    def __init__(
        self,
        default_autonomy: AutonomyLevel = AutonomyLevel.L2_CONSTRAINED,
        default_rate_limit: int = 60,
    ) -> None:
        self._agent_permissions: dict[str, set[Permission]] = {}
        self._agent_autonomy: dict[str, AutonomyLevel] = {}
        self._denied_log: list[dict[str, Any]] = []
        self._rate_limits: dict[str, dict[str, RateLimitEntry]] = defaultdict(dict)
        self._default_autonomy = default_autonomy
        self._default_rate_limit = default_rate_limit

    def set_autonomy(self, agent_id: str, level: AutonomyLevel) -> None:
        """Set the autonomy level for an agent.

        This also grants the permissions associated with that level.

        Args:
            agent_id: The agent ID.
            level: The autonomy level.
        """
        self._agent_autonomy[agent_id] = level

        # Grant level-appropriate permissions
        level_perms = AUTONOMY_PERMISSIONS.get(level, set())
        if agent_id not in self._agent_permissions:
            self._agent_permissions[agent_id] = set()
        self._agent_permissions[agent_id].update(level_perms)

        logger.info("autonomy_set", agent_id=agent_id, level=level.value)

    def get_autonomy(self, agent_id: str) -> AutonomyLevel:
        """Get the autonomy level for an agent."""
        return self._agent_autonomy.get(agent_id, self._default_autonomy)

    def grant_role(self, agent_id: str, role: str) -> None:
        """Grant a role's permissions to an agent.

        Args:
            agent_id: The agent ID.
            role: The role name.
        """
        permissions = self.ROLE_PERMISSIONS.get(role, set())
        if agent_id not in self._agent_permissions:
            self._agent_permissions[agent_id] = set()
        self._agent_permissions[agent_id].update(permissions)

    def grant_permission(self, agent_id: str, permission: Permission) -> None:
        """Grant a specific permission to an agent."""
        if agent_id not in self._agent_permissions:
            self._agent_permissions[agent_id] = set()
        self._agent_permissions[agent_id].add(permission)

    def revoke_permission(self, agent_id: str, permission: Permission) -> None:
        """Revoke a permission from an agent."""
        if agent_id in self._agent_permissions:
            self._agent_permissions[agent_id].discard(permission)

    def check_permission(self, agent_id: str, permission: Permission) -> bool:
        """Check if an agent has a specific permission.

        Args:
            agent_id: The agent ID.
            permission: The permission to check.

        Returns:
            True if the agent has the permission.
        """
        agent_perms = self._agent_permissions.get(agent_id, set())
        has_perm = permission in agent_perms or Permission.ADMIN in agent_perms

        if not has_perm:
            self._denied_log.append({
                "agent_id": agent_id,
                "permission": permission.value,
                "timestamp": time.time(),
            })

        return has_perm

    def enforce_permission(self, agent_id: str, permission: Permission) -> None:
        """Enforce that an agent has a permission, raising an error if not.

        Args:
            agent_id: The agent ID.
            permission: The required permission.

        Raises:
            PermissionDeniedError: If the agent doesn't have the permission.
        """
        if not self.check_permission(agent_id, permission):
            raise PermissionDeniedError(
                f"Agent '{agent_id}' does not have permission: {permission.value}",
                permission=permission.value,
                subject=agent_id,
            )

    def check_rate_limit(self, agent_id: str, tool_name: str, limit: Optional[int] = None) -> bool:
        """Check if an agent is within rate limits for a tool.

        Args:
            agent_id: The agent ID.
            tool_name: The tool name.
            limit: Custom rate limit (requests per minute).

        Returns:
            True if the request is allowed.
        """
        rpm = limit or self._default_rate_limit

        if tool_name not in self._rate_limits[agent_id]:
            self._rate_limits[agent_id][tool_name] = RateLimitEntry(window_seconds=60)

        entry = self._rate_limits[agent_id][tool_name]
        return entry.check(rpm)

    def get_rate_limit_usage(self, agent_id: str, tool_name: str) -> dict[str, Any]:
        """Get rate limit usage for an agent/tool combination."""
        entry = self._rate_limits.get(agent_id, {}).get(tool_name)
        if not entry:
            return {"used": 0, "remaining": self._default_rate_limit}
        return {"used": entry.request_count, "remaining": entry.remaining}

    def get_permissions(self, agent_id: str) -> set[Permission]:
        """Get all permissions for an agent."""
        return self._agent_permissions.get(agent_id, set())

    def get_denied_log(self, limit: int = 100) -> list[dict[str, Any]]:
        """Get the log of denied permission checks."""
        return self._denied_log[-limit:]

    def get_agent_info(self, agent_id: str) -> dict[str, Any]:
        """Get full permission info for an agent."""
        return {
            "agent_id": agent_id,
            "autonomy_level": self.get_autonomy(agent_id).value,
            "permissions": [p.value for p in self.get_permissions(agent_id)],
            "rate_limited_tools": list(self._rate_limits.get(agent_id, {}).keys()),
        }

"""MCP client for connecting to external MCP servers.

Provides a client for the Model Context Protocol with connection management,
tool discovery, tool execution, and resource access.
"""

from __future__ import annotations

import asyncio
import time
from typing import Any, Optional

from ai_multicolony.config.logging_config import get_logger
from ai_multicolony.mcp.protocol import (
    MCPErrorCode,
    MCPRequest,
    MCPResponse,
    MCPServerInfo,
    PermissionLevel,
    PromptDefinition,
    ResourceDefinition,
    ToolDefinition,
)

logger = get_logger(__name__)


class MCPConnectionError(Exception):
    """Error connecting to MCP server."""

    pass


class MCPClient:
    """MCP client for connecting to external servers.

    Features:
    - Connect to MCP servers via HTTP or stdio
    - Discover available tools, resources, and prompts
    - Execute tools with automatic retry
    - Read resources and subscribe to updates
    - Connection lifecycle management
    - Request/response correlation
    """

    def __init__(
        self,
        server_url: str,
        timeout: float = 30.0,
        max_retries: int = 3,
        retry_delay: float = 1.0,
        agent_id: str = "",
        permission_level: PermissionLevel = PermissionLevel.EXECUTE,
    ) -> None:
        self._server_url = server_url.rstrip("/")
        self._timeout = timeout
        self._max_retries = max_retries
        self._retry_delay = retry_delay
        self._agent_id = agent_id
        self._permission_level = permission_level
        self._server_info: Optional[dict[str, Any]] = None
        self._tools: dict[str, ToolDefinition] = {}
        self._resources: dict[str, ResourceDefinition] = {}
        self._prompts: dict[str, PromptDefinition] = {}
        self._connected = False
        self._last_ping: Optional[float] = None
        self._request_count = 0
        self._error_count = 0

    # === Connection Management ===

    async def connect(self) -> dict[str, Any]:
        """Initialize the connection to the MCP server.

        Performs the MCP handshake (initialize) and discovers
        available tools, resources, and prompts.

        Returns:
            Server information.

        Raises:
            MCPConnectionError: If connection fails.
        """
        try:
            response = await self._send_request(MCPRequest(
                method="initialize",
                params={
                    "protocolVersion": "2024-11-05",
                    "capabilities": {
                        "tools": {},
                        "resources": {"subscribe": True},
                        "prompts": {},
                    },
                    "clientInfo": {
                        "name": "ai-multicolony-client",
                        "version": "0.1.0",
                    },
                    "_agent_id": self._agent_id,
                },
            ))

            if response.is_error:
                raise MCPConnectionError(f"MCP initialization failed: {response.error}")

            self._server_info = response.result
            self._connected = True
            self._last_ping = time.time()

            # Discover capabilities
            await self.discover_tools()
            await self.discover_resources()
            await self.discover_prompts()

            logger.info(
                "mcp_client_connected",
                server=self._server_url,
                tools=len(self._tools),
                resources=len(self._resources),
                prompts=len(self._prompts),
            )
            return self._server_info or {}

        except MCPConnectionError:
            raise
        except Exception as e:
            raise MCPConnectionError(f"Connection failed: {e}")

    async def disconnect(self) -> None:
        """Disconnect from the MCP server."""
        self._connected = False
        self._tools.clear()
        self._resources.clear()
        self._prompts.clear()
        self._server_info = None
        logger.info("mcp_client_disconnected", server=self._server_url)

    async def ping(self) -> bool:
        """Ping the MCP server to check connectivity.

        Returns:
            True if server is responsive.
        """
        try:
            response = await self._send_request(MCPRequest(method="initialize"))
            if not response.is_error:
                self._last_ping = time.time()
                return True
            return False
        except Exception:
            return False

    @property
    def is_connected(self) -> bool:
        """Check if the client is connected."""
        return self._connected

    # === Tool Discovery & Execution ===

    async def discover_tools(self) -> list[ToolDefinition]:
        """Discover available tools on the MCP server.

        Returns:
            List of tool definitions.
        """
        response = await self._send_request(MCPRequest(
            method="tools/list",
            params={"_agent_id": self._agent_id},
        ))

        if response.is_error:
            logger.warning("mcp_discover_tools_error", error=response.error)
            return []

        tools = []
        for tool_data in response.result.get("tools", []):
            tool = ToolDefinition(**tool_data)
            tools.append(tool)
            self._tools[tool.name] = tool

        return tools

    async def list_tools(self) -> list[ToolDefinition]:
        """List available tools (from cache or discover).

        Returns:
            List of tool definitions.
        """
        if not self._tools:
            return await self.discover_tools()
        return list(self._tools.values())

    async def call_tool(self, name: str, arguments: dict[str, Any]) -> Any:
        """Call a tool on the MCP server with automatic retry.

        Args:
            name: Tool name.
            arguments: Tool arguments.

        Returns:
            Tool execution result.

        Raises:
            RuntimeError: If tool call fails after retries.
        """
        last_error = None

        for attempt in range(self._max_retries):
            try:
                response = await self._send_request(MCPRequest(
                    method="tools/call",
                    params={
                        "name": name,
                        "arguments": arguments,
                        "_agent_id": self._agent_id,
                    },
                ))

                if response.is_error:
                    error_code = response.error.get("code", 0)
                    # Don't retry on permission or not-found errors
                    if error_code in (
                        MCPErrorCode.PERMISSION_DENIED.value,
                        MCPErrorCode.UNKNOWN_TOOL.value,
                        MCPErrorCode.RATE_LIMITED.value,
                    ):
                        raise RuntimeError(f"Tool call failed: {response.error}")

                    last_error = response.error
                    if attempt < self._max_retries - 1:
                        await asyncio.sleep(self._retry_delay * (attempt + 1))
                    continue

                content = response.result.get("content", [])
                if content and isinstance(content, list):
                    return content[0].get("text", "")
                return response.result

            except RuntimeError:
                raise
            except Exception as e:
                last_error = str(e)
                if attempt < self._max_retries - 1:
                    await asyncio.sleep(self._retry_delay * (attempt + 1))

        raise RuntimeError(f"Tool call failed after {self._max_retries} retries: {last_error}")

    # === Resource Access ===

    async def discover_resources(self) -> list[ResourceDefinition]:
        """Discover available resources on the MCP server.

        Returns:
            List of resource definitions.
        """
        response = await self._send_request(MCPRequest(
            method="resources/list",
            params={"_agent_id": self._agent_id},
        ))

        if response.is_error:
            return []

        resources = []
        for res_data in response.result.get("resources", []):
            resource = ResourceDefinition(**res_data)
            resources.append(resource)
            self._resources[resource.uri] = resource

        return resources

    async def list_resources(self) -> list[dict[str, Any]]:
        """List available resources (from cache or discover)."""
        if not self._resources:
            await self.discover_resources()
        return [r.model_dump() for r in self._resources.values()]

    async def read_resource(self, uri: str) -> str:
        """Read a resource from the MCP server.

        Args:
            uri: Resource URI.

        Returns:
            Resource content.
        """
        response = await self._send_request(MCPRequest(
            method="resources/read",
            params={"uri": uri, "_agent_id": self._agent_id},
        ))

        if response.is_error:
            raise RuntimeError(f"Failed to read resource: {response.error}")

        contents = response.result.get("contents", [])
        if contents and isinstance(contents, list):
            return contents[0].get("text", "")
        return ""

    async def subscribe_resource(self, uri: str) -> bool:
        """Subscribe to resource updates.

        Args:
            uri: Resource URI.

        Returns:
            True if subscribed successfully.
        """
        response = await self._send_request(MCPRequest(
            method="resources/subscribe",
            params={"uri": uri, "_agent_id": self._agent_id},
        ))
        return not response.is_error

    async def unsubscribe_resource(self, uri: str) -> bool:
        """Unsubscribe from resource updates.

        Args:
            uri: Resource URI.

        Returns:
            True if unsubscribed successfully.
        """
        response = await self._send_request(MCPRequest(
            method="resources/unsubscribe",
            params={"uri": uri, "_agent_id": self._agent_id},
        ))
        return not response.is_error

    # === Prompt Access ===

    async def discover_prompts(self) -> list[PromptDefinition]:
        """Discover available prompts on the MCP server.

        Returns:
            List of prompt definitions.
        """
        response = await self._send_request(MCPRequest(
            method="prompts/list",
            params={"_agent_id": self._agent_id},
        ))

        if response.is_error:
            return []

        prompts = []
        for p_data in response.result.get("prompts", []):
            prompt = PromptDefinition(**p_data)
            prompts.append(prompt)
            self._prompts[prompt.name] = prompt

        return prompts

    async def get_prompt(self, name: str, arguments: Optional[dict[str, Any]] = None) -> dict[str, Any]:
        """Get a rendered prompt from the MCP server.

        Args:
            name: Prompt name.
            arguments: Optional arguments for the prompt.

        Returns:
            Rendered prompt result.
        """
        params: dict[str, Any] = {"name": name, "_agent_id": self._agent_id}
        if arguments:
            params["arguments"] = arguments

        response = await self._send_request(MCPRequest(method="prompts/get", params=params))

        if response.is_error:
            raise RuntimeError(f"Failed to get prompt: {response.error}")

        return response.result or {}

    # === Transport ===

    async def _send_request(self, request: MCPRequest) -> MCPResponse:
        """Send a request to the MCP server via HTTP.

        Args:
            request: The MCP request.

        Returns:
            The MCP response.
        """
        self._request_count += 1

        try:
            import httpx

            async with httpx.AsyncClient(timeout=self._timeout) as client:
                http_response = await client.post(
                    f"{self._server_url}/mcp",
                    json=request.model_dump(),
                    headers={"Content-Type": "application/json"},
                )
                return MCPResponse(**http_response.json())

        except ImportError:
            raise MCPConnectionError("httpx not installed. Install with: pip install httpx")
        except Exception as e:
            self._error_count += 1
            return MCPResponse(
                id=request.id,
                error={"code": -32603, "message": f"Connection error: {e}"},
            )

    # === Properties ===

    @property
    def server_info(self) -> Optional[dict[str, Any]]:
        """Get server information."""
        return self._server_info

    @property
    def available_tools(self) -> list[str]:
        """Get names of available tools."""
        return list(self._tools.keys())

    @property
    def available_resources(self) -> list[str]:
        """Get URIs of available resources."""
        return list(self._resources.keys())

    @property
    def available_prompts(self) -> list[str]:
        """Get names of available prompts."""
        return list(self._prompts.keys())

    def get_tool(self, name: str) -> Optional[ToolDefinition]:
        """Get a specific tool definition."""
        return self._tools.get(name)

    def get_stats(self) -> dict[str, Any]:
        """Get client statistics."""
        return {
            "server_url": self._server_url,
            "connected": self._connected,
            "agent_id": self._agent_id,
            "tools": len(self._tools),
            "resources": len(self._resources),
            "prompts": len(self._prompts),
            "request_count": self._request_count,
            "error_count": self._error_count,
            "last_ping": self._last_ping,
        }

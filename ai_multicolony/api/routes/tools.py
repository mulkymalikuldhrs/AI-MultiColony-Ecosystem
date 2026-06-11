"""Tool management API routes."""

from __future__ import annotations

from typing import Any

from ai_multicolony.api.schemas import ToolCallRequest, ToolCallResponse


def create_router() -> Any:
    """Create the tools router."""
    from fastapi import APIRouter, HTTPException

    router = APIRouter(prefix="/tools", tags=["tools"])

    @router.get("/", response_model=list[dict[str, Any]])
    async def list_tools() -> list[dict[str, Any]]:
        """List available tools."""
        from ai_multicolony.core.tool_registry import ToolRegistry
        registry = ToolRegistry()
        return [{"name": k, **v} for k, v in registry.list_all().items()]

    @router.post("/call", response_model=ToolCallResponse)
    async def call_tool(request: ToolCallRequest) -> ToolCallResponse:
        """Call a tool."""
        from ai_multicolony.core.tool_registry import ToolRegistry
        registry = ToolRegistry()
        try:
            result = await registry.execute(request.tool_name, request.arguments)
            return ToolCallResponse(
                success=result.success,
                output=result.output[:1000],
                error=result.error,
            )
        except Exception as e:
            return ToolCallResponse(success=False, error=str(e))

    @router.get("/{tool_name}/schema")
    async def get_tool_schema(tool_name: str) -> dict[str, Any]:
        """Get a tool's OpenAI schema."""
        from ai_multicolony.core.tool_registry import ToolRegistry
        registry = ToolRegistry()
        try:
            tool = registry.get(tool_name)
            return tool.get_openai_schema()
        except KeyError:
            raise HTTPException(status_code=404, detail=f"Tool not found: {tool_name}")

    @router.get("/mcp/list")
    async def list_mcp_tools() -> list[dict[str, Any]]:
        """List tools from MCP servers."""
        # Placeholder for MCP tool discovery
        return []

    return router

"""Tools module for the AI MultiColony Ecosystem.

Provides a comprehensive set of tools for agent interaction with
the outside world: shell execution, file operations, browser automation,
web search, code execution, MCP protocol, Docker sandboxing, voice I/O,
memory operations, and multi-channel messaging.

All tools extend BaseTool from ai_multicolony.core.tool_base and
return ToolResult instances.
"""

from ai_multicolony.tools.shell_tool import ShellTool
from ai_multicolony.tools.file_tool import FileTool
from ai_multicolony.tools.browser_tool import BrowserTool
from ai_multicolony.tools.search_tool import SearchTool
from ai_multicolony.tools.code_tool import CodeTool
from ai_multicolony.tools.mcp_tool import MCPTool
from ai_multicolony.tools.docker_tool import DockerTool
from ai_multicolony.tools.voice_tool import VoiceTool
from ai_multicolony.tools.memory_tool import MemoryTool
from ai_multicolony.tools.channel_tool import ChannelTool

__all__ = [
    "ShellTool",
    "FileTool",
    "BrowserTool",
    "SearchTool",
    "CodeTool",
    "MCPTool",
    "DockerTool",
    "VoiceTool",
    "MemoryTool",
    "ChannelTool",
]

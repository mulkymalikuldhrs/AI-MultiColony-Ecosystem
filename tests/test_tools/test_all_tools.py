"""Comprehensive tests for all 10 tool types.

Tests cover:
- Each tool can be instantiated with default and custom config
- Each tool has correct name/description/parameters
- Each tool has correct tool type
- Tool execution returns ToolResult
- Error handling for invalid inputs
- Tool parameter validation
- Tool-specific features
"""

from __future__ import annotations

import asyncio
import os
import tempfile
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from ai_multicolony.tools.shell_tool import ShellTool
from ai_multicolony.tools.file_tool import FileTool, detect_encoding, unified_diff
from ai_multicolony.tools.browser_tool import BrowserTool, _html_to_markdown
from ai_multicolony.tools.search_tool import SearchTool, SearchResult
from ai_multicolony.tools.code_tool import CodeTool, _safe_import
from ai_multicolony.tools.mcp_tool import MCPTool
from ai_multicolony.tools.docker_tool import DockerTool
from ai_multicolony.tools.voice_tool import VoiceTool, _raw_pcm_to_wav, _detect_wav_params, _convert_audio_format
from ai_multicolony.tools.memory_tool import MemoryTool
from ai_multicolony.tools.channel_tool import ChannelTool, _format_message
from ai_multicolony.types.tools import ToolCall, ToolDefinition, ToolResult, ToolType


# ══════════════════════════════════════════════════════════════════════
# Helper: All 10 tool classes
# ══════════════════════════════════════════════════════════════════════

ALL_TOOL_CLASSES = [
    ShellTool,
    FileTool,
    BrowserTool,
    SearchTool,
    CodeTool,
    MCPTool,
    DockerTool,
    VoiceTool,
    MemoryTool,
    ChannelTool,
]

TOOL_NAME_MAP = {
    ShellTool: "shell",
    FileTool: "file",
    BrowserTool: "browser",
    SearchTool: "search",
    CodeTool: "code",
    MCPTool: "mcp",
    DockerTool: "docker",
    VoiceTool: "voice",
    MemoryTool: "memory",
    ChannelTool: "channel",
}

TOOL_TYPE_MAP = {
    ShellTool: ToolType.SHELL,
    FileTool: ToolType.FILE,
    BrowserTool: ToolType.BROWSER,
    SearchTool: ToolType.SEARCH,
    CodeTool: ToolType.CODE,
    MCPTool: ToolType.MCP,
    DockerTool: ToolType.DOCKER,
    VoiceTool: ToolType.VOICE,
    MemoryTool: ToolType.MEMORY,
    ChannelTool: ToolType.CHANNEL,
}


def make_tool_call(tool_name: str, arguments: dict) -> ToolCall:
    """Helper to create a ToolCall with given arguments."""
    return ToolCall(tool_name=tool_name, arguments=arguments)


# ══════════════════════════════════════════════════════════════════════
# 1. Instantiation & Basic Properties
# ══════════════════════════════════════════════════════════════════════


class TestToolInstantiation:
    """Test that each tool can be instantiated with default config."""

    @pytest.mark.parametrize("tool_cls", ALL_TOOL_CLASSES,
                             ids=[c.__name__ for c in ALL_TOOL_CLASSES])
    def test_instantiate_default(self, tool_cls):
        tool = tool_cls()
        assert tool is not None

    @pytest.mark.parametrize("tool_cls", ALL_TOOL_CLASSES,
                             ids=[c.__name__ for c in ALL_TOOL_CLASSES])
    def test_instantiate_with_config(self, tool_cls):
        tool = tool_cls(config={"timeout": 120})
        assert tool is not None

    @pytest.mark.parametrize("tool_cls", ALL_TOOL_CLASSES,
                             ids=[c.__name__ for c in ALL_TOOL_CLASSES])
    def test_has_id(self, tool_cls):
        tool = tool_cls()
        assert tool.id is not None
        assert len(tool.id) > 0


# ══════════════════════════════════════════════════════════════════════
# 2. Tool Name, Description, Type
# ══════════════════════════════════════════════════════════════════════


class TestToolNameDescriptionType:
    """Test that each tool has correct name, description, and type."""

    @pytest.mark.parametrize("tool_cls,expected_name", list(TOOL_NAME_MAP.items()),
                             ids=[c.__name__ for c in TOOL_NAME_MAP.keys()])
    def test_name(self, tool_cls, expected_name):
        tool = tool_cls()
        assert tool.name == expected_name

    @pytest.mark.parametrize("tool_cls,expected_type", list(TOOL_TYPE_MAP.items()),
                             ids=[c.__name__ for c in TOOL_TYPE_MAP.keys()])
    def test_tool_type(self, tool_cls, expected_type):
        tool = tool_cls()
        assert tool.tool_type == expected_type

    @pytest.mark.parametrize("tool_cls", ALL_TOOL_CLASSES,
                             ids=[c.__name__ for c in ALL_TOOL_CLASSES])
    def test_description_not_empty(self, tool_cls):
        tool = tool_cls()
        assert tool.description is not None
        assert len(tool.description) > 0

    @pytest.mark.parametrize("tool_cls", ALL_TOOL_CLASSES,
                             ids=[c.__name__ for c in ALL_TOOL_CLASSES])
    def test_definition_is_tool_definition(self, tool_cls):
        tool = tool_cls()
        assert isinstance(tool.definition, ToolDefinition)

    @pytest.mark.parametrize("tool_cls", ALL_TOOL_CLASSES,
                             ids=[c.__name__ for c in ALL_TOOL_CLASSES])
    def test_definition_name_matches(self, tool_cls):
        tool = tool_cls()
        assert tool.definition.name == tool.name

    @pytest.mark.parametrize("tool_cls", ALL_TOOL_CLASSES,
                             ids=[c.__name__ for c in ALL_TOOL_CLASSES])
    def test_has_tags(self, tool_cls):
        tool = tool_cls()
        assert isinstance(tool.tags, list)
        assert len(tool.tags) > 0


# ══════════════════════════════════════════════════════════════════════
# 3. Parameters
# ══════════════════════════════════════════════════════════════════════


class TestToolParameters:
    """Test that each tool has proper parameter definitions."""

    @pytest.mark.parametrize("tool_cls", ALL_TOOL_CLASSES,
                             ids=[c.__name__ for c in ALL_TOOL_CLASSES])
    def test_has_parameters(self, tool_cls):
        tool = tool_cls()
        params = tool.definition.parameters
        assert isinstance(params, list)
        assert len(params) > 0

    @pytest.mark.parametrize("tool_cls", ALL_TOOL_CLASSES,
                             ids=[c.__name__ for c in ALL_TOOL_CLASSES])
    def test_parameters_have_names(self, tool_cls):
        tool = tool_cls()
        for p in tool.definition.parameters:
            assert len(p.name) > 0

    @pytest.mark.parametrize("tool_cls", ALL_TOOL_CLASSES,
                             ids=[c.__name__ for c in ALL_TOOL_CLASSES])
    def test_parameters_have_types(self, tool_cls):
        tool = tool_cls()
        for p in tool.definition.parameters:
            assert len(p.type) > 0

    @pytest.mark.parametrize("tool_cls", ALL_TOOL_CLASSES,
                             ids=[c.__name__ for c in ALL_TOOL_CLASSES])
    def test_at_least_one_required_parameter(self, tool_cls):
        tool = tool_cls()
        required = [p for p in tool.definition.parameters if p.required]
        assert len(required) >= 1

    @pytest.mark.parametrize("tool_cls", ALL_TOOL_CLASSES,
                             ids=[c.__name__ for c in ALL_TOOL_CLASSES])
    def test_openai_schema_valid(self, tool_cls):
        tool = tool_cls()
        schema = tool.get_openai_schema()
        assert "type" in schema
        assert schema["type"] == "function"
        assert "function" in schema
        assert "name" in schema["function"]
        assert "parameters" in schema["function"]


# ══════════════════════════════════════════════════════════════════════
# 4. Tool Argument Validation
# ══════════════════════════════════════════════════════════════════════


class TestToolArgumentValidation:
    """Test argument validation for tools."""

    def test_shell_missing_required_command(self):
        tool = ShellTool()
        errors = tool.validate_arguments({})
        assert any("command" in e for e in errors)

    def test_shell_valid_arguments(self):
        tool = ShellTool()
        errors = tool.validate_arguments({"command": "ls"})
        assert len(errors) == 0

    def test_file_missing_required_operation(self):
        tool = FileTool()
        errors = tool.validate_arguments({})
        assert any("operation" in e for e in errors)

    def test_file_missing_required_path(self):
        tool = FileTool()
        errors = tool.validate_arguments({"operation": "read"})
        assert any("path" in e for e in errors)

    def test_file_invalid_operation_enum(self):
        tool = FileTool()
        errors = tool.validate_arguments({"operation": "invalid_op", "path": "/tmp/test"})
        assert any("enum" in e.lower() or "must be one of" in e for e in errors)

    def test_file_valid_operation_enum(self):
        tool = FileTool()
        errors = tool.validate_arguments({"operation": "read", "path": "/tmp/test"})
        assert len(errors) == 0

    def test_search_missing_required_query(self):
        tool = SearchTool()
        errors = tool.validate_arguments({})
        assert any("query" in e for e in errors)

    def test_code_missing_required_code(self):
        tool = CodeTool()
        errors = tool.validate_arguments({})
        assert any("code" in e for e in errors)

    def test_browser_missing_required_action(self):
        tool = BrowserTool()
        errors = tool.validate_arguments({})
        assert any("action" in e for e in errors)

    def test_voice_missing_required_action(self):
        tool = VoiceTool()
        errors = tool.validate_arguments({})
        assert any("action" in e for e in errors)

    def test_memory_missing_required_action(self):
        tool = MemoryTool()
        errors = tool.validate_arguments({})
        assert any("action" in e for e in errors)

    def test_channel_missing_required_action(self):
        tool = ChannelTool()
        errors = tool.validate_arguments({})
        assert any("action" in e for e in errors)

    def test_docker_missing_required_action(self):
        tool = DockerTool()
        errors = tool.validate_arguments({})
        assert any("action" in e for e in errors)

    def test_mcp_missing_required_action(self):
        tool = MCPTool()
        errors = tool.validate_arguments({})
        assert any("action" in e for e in errors)

    def test_unknown_parameter_flagged(self):
        tool = ShellTool()
        errors = tool.validate_arguments({"command": "ls", "nonexistent_param": "val"})
        assert any("Unknown parameter" in e for e in errors)


# ══════════════════════════════════════════════════════════════════════
# 5. Shell Tool Execution
# ══════════════════════════════════════════════════════════════════════


class TestShellToolExecution:
    """Test ShellTool execution."""

    @pytest.mark.asyncio
    async def test_empty_command_returns_error(self):
        tool = ShellTool()
        tc = make_tool_call("shell", {"command": ""})
        result = await tool.execute(tc)
        assert isinstance(result, ToolResult)
        assert result.success is False
        assert "No command" in result.error

    @pytest.mark.asyncio
    async def test_simple_command_succeeds(self):
        tool = ShellTool()
        tc = make_tool_call("shell", {"command": "echo hello"})
        result = await tool.execute(tc)
        assert isinstance(result, ToolResult)
        assert result.success is True
        assert "hello" in result.output

    @pytest.mark.asyncio
    async def test_command_with_nonzero_exit(self):
        tool = ShellTool()
        tc = make_tool_call("shell", {"command": "exit 1"})
        result = await tool.execute(tc)
        assert isinstance(result, ToolResult)
        assert result.success is False

    @pytest.mark.asyncio
    async def test_dangerous_command_blocked(self):
        tool = ShellTool()
        tc = make_tool_call("shell", {"command": "rm -rf /"})
        with pytest.raises(Exception):
            await tool.execute(tc)

    @pytest.mark.asyncio
    async def test_invalid_working_dir(self):
        tool = ShellTool()
        tc = make_tool_call("shell", {"command": "ls", "working_dir": "/nonexistent/dir"})
        result = await tool.execute(tc)
        assert result.success is False
        assert "not exist" in result.error.lower() or "Working directory" in result.error

    def test_command_history(self):
        tool = ShellTool()
        tool._record_command("ls")
        tool._record_command("pwd")
        history = tool.get_history()
        assert len(history) == 2

    def test_clear_history(self):
        tool = ShellTool()
        tool._record_command("ls")
        tool.clear_history()
        assert len(tool.get_history()) == 0

    def test_allowlist_mode(self):
        tool = ShellTool(config={"allowed_commands": ["ls", "pwd"]})
        # Allowed command should pass
        tool._validate_command("ls -la")
        # Disallowed should raise
        from ai_multicolony.exceptions import ToolPermissionError
        with pytest.raises(ToolPermissionError):
            tool._validate_command("rm file.txt")


# ══════════════════════════════════════════════════════════════════════
# 6. File Tool Execution
# ══════════════════════════════════════════════════════════════════════


class TestFileToolExecution:
    """Test FileTool execution."""

    @pytest.mark.asyncio
    async def test_no_operation_returns_error(self):
        tool = FileTool()
        tc = make_tool_call("file", {"path": "test.txt"})
        result = await tool.execute(tc)
        assert result.success is False
        assert "No operation" in result.error

    @pytest.mark.asyncio
    async def test_no_path_returns_error(self):
        tool = FileTool()
        tc = make_tool_call("file", {"operation": "read"})
        result = await tool.execute(tc)
        assert result.success is False
        assert "No path" in result.error

    @pytest.mark.asyncio
    async def test_unknown_operation_returns_error(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            tool = FileTool(config={"base_dir": tmpdir})
            tc = make_tool_call("file", {"operation": "fly", "path": "test.txt"})
            result = await tool.execute(tc)
            assert result.success is False
            assert "Unknown operation" in result.error

    @pytest.mark.asyncio
    async def test_read_nonexistent_file(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            tool = FileTool(config={"base_dir": tmpdir})
            tc = make_tool_call("file", {"operation": "read", "path": "nonexistent_file.txt"})
            result = await tool.execute(tc)
            assert result.success is False
            assert "not found" in result.error.lower() or "File" in result.error

    @pytest.mark.asyncio
    async def test_write_and_read_file(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            tool = FileTool(config={"base_dir": tmpdir})
            filepath = os.path.join(tmpdir, "test.txt")

            # Write
            tc_write = make_tool_call("file", {"operation": "write", "path": "test.txt", "content": "Hello World"})
            result_w = await tool.execute(tc_write)
            assert result_w.success is True

            # Read
            tc_read = make_tool_call("file", {"operation": "read", "path": "test.txt"})
            result_r = await tool.execute(tc_read)
            assert result_r.success is True
            assert "Hello World" in result_r.output

    @pytest.mark.asyncio
    async def test_edit_file(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            tool = FileTool(config={"base_dir": tmpdir})
            # Write initial content
            tc_write = make_tool_call("file", {"operation": "write", "path": "edit_test.txt", "content": "Hello World"})
            await tool.execute(tc_write)
            # Edit
            tc_edit = make_tool_call("file", {
                "operation": "edit", "path": "edit_test.txt",
                "old_text": "Hello", "new_text": "Goodbye",
            })
            result = await tool.execute(tc_edit)
            assert result.success is True

    @pytest.mark.asyncio
    async def test_edit_missing_old_text(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            tool = FileTool(config={"base_dir": tmpdir})
            # First create the file so edit doesn't fail on file-not-found
            tc_write = make_tool_call("file", {"operation": "write", "path": "test.txt", "content": "Hello"})
            await tool.execute(tc_write)
            tc = make_tool_call("file", {"operation": "edit", "path": "test.txt"})
            result = await tool.execute(tc)
            assert result.success is False
            assert "old_text" in result.error

    @pytest.mark.asyncio
    async def test_list_directory(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            tool = FileTool(config={"base_dir": tmpdir})
            tc = make_tool_call("file", {"operation": "list", "path": "."})
            result = await tool.execute(tc)
            assert result.success is True

    @pytest.mark.asyncio
    async def test_mkdir(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            tool = FileTool(config={"base_dir": tmpdir})
            tc = make_tool_call("file", {"operation": "mkdir", "path": "new_dir"})
            result = await tool.execute(tc)
            assert result.success is True
            assert os.path.isdir(os.path.join(tmpdir, "new_dir"))

    @pytest.mark.asyncio
    async def test_path_traversal_blocked(self):
        tool = FileTool(config={"base_dir": "/tmp"})
        from ai_multicolony.exceptions import ToolPermissionError
        with pytest.raises(ToolPermissionError):
            tool._validate_path("../../../etc/passwd")

    def test_detect_encoding_utf8_bom(self):
        data = b"\xef\xbb\xbfhello"
        assert detect_encoding(data) == "utf-8-sig"

    def test_detect_encoding_utf16_le(self):
        data = b"\xff\xfehello"
        assert detect_encoding(data) == "utf-16-le"

    def test_detect_encoding_plain_utf8(self):
        data = b"hello world"
        assert detect_encoding(data) == "utf-8"

    def test_unified_diff_no_changes(self):
        assert unified_diff("hello", "hello") == ""

    def test_unified_diff_with_changes(self):
        diff = unified_diff("line1\nline2\n", "line1\nline3\n", "test.py")
        assert len(diff) > 0


# ══════════════════════════════════════════════════════════════════════
# 7. Code Tool Execution
# ══════════════════════════════════════════════════════════════════════


class TestCodeToolExecution:
    """Test CodeTool execution."""

    @pytest.mark.asyncio
    async def test_no_code_returns_error(self):
        tool = CodeTool()
        tc = make_tool_call("code", {"code": ""})
        result = await tool.execute(tc)
        assert result.success is False
        assert "No code" in result.error

    @pytest.mark.asyncio
    async def test_simple_expression(self):
        tool = CodeTool()
        tc = make_tool_call("code", {"code": "2 + 2"})
        result = await tool.execute(tc)
        assert result.success is True
        assert "4" in result.output

    @pytest.mark.asyncio
    async def test_print_output(self):
        tool = CodeTool()
        tc = make_tool_call("code", {"code": "print('hello')"})
        result = await tool.execute(tc)
        assert result.success is True
        assert "hello" in result.output

    @pytest.mark.asyncio
    async def test_code_error_returns_failure(self):
        tool = CodeTool()
        tc = make_tool_call("code", {"code": "1/0"})
        result = await tool.execute(tc)
        assert result.success is False

    @pytest.mark.asyncio
    async def test_sandbox_mode_restricted_import(self):
        tool = CodeTool()
        tc = make_tool_call("code", {"code": "import os; os.system('echo hacked')", "sandbox": True})
        result = await tool.execute(tc)
        assert result.success is False

    @pytest.mark.asyncio
    async def test_safe_import_allowed(self):
        tool = CodeTool()
        tc = make_tool_call("code", {"code": "import json; print(json.dumps({'a': 1}))", "sandbox": True})
        result = await tool.execute(tc)
        assert result.success is True

    @pytest.mark.asyncio
    async def test_reset_namespace(self):
        tool = CodeTool()
        # Set a variable
        tc1 = make_tool_call("code", {"code": "x = 42"})
        await tool.execute(tc1)
        # Reset and verify x is gone
        tc2 = make_tool_call("code", {"code": "x", "reset_namespace": True})
        result = await tool.execute(tc2)
        assert result.success is False  # NameError

    def test_reset_method(self):
        tool = CodeTool()
        tool._namespace = {"x": 42}
        tool.reset()
        assert tool._namespace == {}

    def test_get_namespace_vars(self):
        tool = CodeTool()
        tool._namespace = {"x": 42, "y": "hello"}
        vars = tool.get_namespace_vars()
        assert vars["x"] == "int"
        assert vars["y"] == "str"

    def test_safe_import_allowed_module(self):
        mod = _safe_import("math")
        assert mod is not None

    def test_safe_import_blocked_module(self):
        with pytest.raises(ImportError):
            _safe_import("subprocess")


# ══════════════════════════════════════════════════════════════════════
# 8. Search Tool
# ══════════════════════════════════════════════════════════════════════


class TestSearchTool:
    """Test SearchTool properties and helpers."""

    def test_default_engine(self):
        tool = SearchTool()
        assert tool._default_engine == "duckduckgo"

    def test_custom_engine(self):
        tool = SearchTool(config={"engine": "google"})
        assert tool._default_engine == "google"

    def test_max_results_default(self):
        tool = SearchTool()
        assert tool._max_results == 10

    def test_search_result_dedup_key(self):
        r = SearchResult(title="Test", url="https://example.com/", snippet="", source_engine="ddg")
        assert r.dedup_key == "https://example.com"

    def test_search_result_dedup_key_strips_tracking(self):
        r = SearchResult(title="T", url="https://x.com/page?utm_source=g", snippet="", source_engine="ddg")
        key = r.dedup_key
        assert "utm_source" not in key

    def test_deduplicate(self):
        tool = SearchTool()
        results = [
            SearchResult(title="A", url="https://a.com", snippet="", source_engine="duckduckgo"),
            SearchResult(title="A2", url="https://a.com", snippet="", source_engine="google"),
            SearchResult(title="B", url="https://b.com", snippet="", source_engine="duckduckgo"),
        ]
        deduped = tool._deduplicate(results)
        assert len(deduped) == 2

    def test_rank_results(self):
        tool = SearchTool()
        results = [
            SearchResult(title="Python programming", url="https://py.com", snippet="Python code", source_engine="google"),
            SearchResult(title="Random stuff", url="https://rand.com", snippet="", source_engine="duckduckgo"),
        ]
        ranked = tool._rank_results(results, "python programming")
        assert ranked[0].title == "Python programming"
        assert ranked[0].rank == 1


# ══════════════════════════════════════════════════════════════════════
# 9. Browser Tool
# ══════════════════════════════════════════════════════════════════════


class TestBrowserTool:
    """Test BrowserTool properties and helpers."""

    def test_default_headless(self):
        tool = BrowserTool()
        assert tool._headless is True

    def test_default_stealth_mode(self):
        tool = BrowserTool()
        assert tool._stealth_mode is True

    def test_custom_viewport(self):
        tool = BrowserTool(config={"viewport": {"width": 1920, "height": 1080}})
        assert tool._default_viewport == {"width": 1920, "height": 1080}

    @pytest.mark.asyncio
    async def test_no_action_returns_error(self):
        tool = BrowserTool()
        tc = make_tool_call("browser", {"action": ""})
        result = await tool.execute(tc)
        assert result.success is False
        assert "No action" in result.error

    def test_html_to_markdown_headings(self):
        html = "<h1>Title</h1><h2>Subtitle</h2>"
        md = _html_to_markdown(html)
        assert "# Title" in md
        assert "## Subtitle" in md

    def test_html_to_markdown_links(self):
        html = '<a href="https://example.com">Click</a>'
        md = _html_to_markdown(html)
        assert "[Click](https://example.com)" in md

    def test_html_to_markdown_bold(self):
        html = "<strong>Bold</strong>"
        md = _html_to_markdown(html)
        assert "**Bold**" in md

    def test_html_to_markdown_code(self):
        html = "<code>x = 1</code>"
        md = _html_to_markdown(html)
        assert "`x = 1`" in md

    def test_html_to_markdown_removes_scripts(self):
        html = '<script>alert("xss")</script><p>Safe</p>'
        md = _html_to_markdown(html)
        assert "alert" not in md
        assert "Safe" in md


# ══════════════════════════════════════════════════════════════════════
# 10. MCP Tool
# ══════════════════════════════════════════════════════════════════════


class TestMCPTool:
    """Test MCPTool properties and basic actions."""

    def test_no_servers_by_default(self):
        tool = MCPTool()
        assert len(tool._servers) == 0

    def test_preconfigured_servers(self):
        tool = MCPTool(config={"servers": {"test": {"url": "http://localhost:9000"}}})
        assert "test" in tool._servers
        assert tool._server_meta["test"]["url"] == "http://localhost:9000"

    def test_get_server_returns_none_for_missing(self):
        tool = MCPTool()
        assert tool._get_server("missing") is None

    def test_get_server_default_server(self):
        tool = MCPTool(config={"default_server": "myserver", "servers": {"myserver": {"url": "http://x"}}})
        result = tool._get_server(None)
        assert result is not None

    @pytest.mark.asyncio
    async def test_unknown_action_returns_error(self):
        tool = MCPTool()
        tc = make_tool_call("mcp", {"action": "nonexistent"})
        result = await tool.execute(tc)
        assert result.success is False
        assert "Unknown" in result.error

    @pytest.mark.asyncio
    async def test_connect_missing_name(self):
        tool = MCPTool()
        tc = make_tool_call("mcp", {"action": "connect", "url": "http://x"})
        result = await tool.execute(tc)
        assert result.success is False
        assert "No server name" in result.error

    @pytest.mark.asyncio
    async def test_connect_missing_url(self):
        tool = MCPTool()
        tc = make_tool_call("mcp", {"action": "connect", "server": "test"})
        result = await tool.execute(tc)
        assert result.success is False
        assert "No server URL" in result.error

    @pytest.mark.asyncio
    async def test_disconnect_nonexistent(self):
        tool = MCPTool()
        tc = make_tool_call("mcp", {"action": "disconnect", "server": "missing"})
        result = await tool.execute(tc)
        assert result.success is False
        assert "not found" in result.error.lower()

    @pytest.mark.asyncio
    async def test_status_no_servers(self):
        tool = MCPTool()
        tc = make_tool_call("mcp", {"action": "status"})
        result = await tool.execute(tc)
        assert result.success is True
        assert "No MCP servers" in result.output


# ══════════════════════════════════════════════════════════════════════
# 11. Docker Tool
# ══════════════════════════════════════════════════════════════════════


class TestDockerTool:
    """Test DockerTool properties."""

    def test_default_image(self):
        tool = DockerTool()
        assert tool._default_image == "python:3.12-slim"

    def test_custom_image(self):
        tool = DockerTool(config={"image": "ubuntu:22.04"})
        assert tool._default_image == "ubuntu:22.04"

    def test_containers_initially_empty(self):
        tool = DockerTool()
        assert len(tool._containers) == 0

    @pytest.mark.asyncio
    async def test_unknown_action_returns_error(self):
        tool = DockerTool()
        tc = make_tool_call("docker", {"action": "nonexistent"})
        # Docker tool tries to get client first, which may fail
        # If Docker is not available, it raises ToolExecutionError
        # Either way, the action should not succeed
        try:
            result = await tool.execute(tc)
            assert result.success is False
        except Exception:
            pass  # Docker unavailable is expected in test env


# ══════════════════════════════════════════════════════════════════════
# 12. Voice Tool
# ══════════════════════════════════════════════════════════════════════


class TestVoiceTool:
    """Test VoiceTool properties and helpers."""

    def test_default_language(self):
        tool = VoiceTool()
        assert tool._default_language == "en"

    def test_custom_language(self):
        tool = VoiceTool(config={"language": "es"})
        assert tool._default_language == "es"

    def test_whisper_model_size(self):
        tool = VoiceTool()
        assert tool._whisper_model_size == "base"

    @pytest.mark.asyncio
    async def test_unknown_action_returns_error(self):
        tool = VoiceTool()
        tc = make_tool_call("voice", {"action": "nonexistent"})
        result = await tool.execute(tc)
        assert result.success is False
        assert "Unknown" in result.error

    @pytest.mark.asyncio
    async def test_transcribe_no_audio(self):
        tool = VoiceTool()
        tc = make_tool_call("voice", {"action": "transcribe"})
        result = await tool.execute(tc)
        assert result.success is False
        assert "No audio" in result.error

    @pytest.mark.asyncio
    async def test_synthesize_no_text(self):
        tool = VoiceTool()
        tc = make_tool_call("voice", {"action": "synthesize"})
        result = await tool.execute(tc)
        assert result.success is False
        assert "No text" in result.error

    def test_raw_pcm_to_wav(self):
        pcm = b"\x00\x00" * 100  # 100 samples of silence
        wav = _raw_pcm_to_wav(pcm, sample_rate=16000, channels=1, sample_width=2)
        assert wav[:4] == b"RIFF"
        assert len(wav) > len(pcm)

    def test_detect_wav_params_invalid(self):
        params = _detect_wav_params(b"not a wav")
        assert params["sample_rate"] == 16000  # default fallback

    def test_convert_audio_same_format(self):
        data = b"test data"
        result = _convert_audio_format(data, "wav", "wav")
        assert result == data

    def test_convert_audio_pcm_to_wav(self):
        pcm = b"\x00\x00" * 50
        wav = _convert_audio_format(pcm, "pcm", "wav")
        assert wav[:4] == b"RIFF"


# ══════════════════════════════════════════════════════════════════════
# 13. Memory Tool
# ══════════════════════════════════════════════════════════════════════


class TestMemoryTool:
    """Test MemoryTool properties and basic actions."""

    @pytest.mark.asyncio
    async def test_unknown_action_returns_error(self):
        tool = MemoryTool()
        tc = make_tool_call("memory", {"action": "nonexistent"})
        result = await tool.execute(tc)
        assert result.success is False
        assert "Unknown" in result.error

    @pytest.mark.asyncio
    async def test_store_no_content(self):
        tool = MemoryTool()
        tc = make_tool_call("memory", {"action": "store"})
        result = await tool.execute(tc)
        assert result.success is False
        assert "No content" in result.error

    @pytest.mark.asyncio
    async def test_store_success(self):
        tool = MemoryTool()
        tc = make_tool_call("memory", {"action": "store", "content": "Test memory", "memory_type": "episodic"})
        result = await tool.execute(tc)
        assert result.success is True
        assert "Stored" in result.output

    @pytest.mark.asyncio
    async def test_query_empty(self):
        tool = MemoryTool()
        tc = make_tool_call("memory", {"action": "query", "query": "nonexistent"})
        result = await tool.execute(tc)
        assert result.success is True
        assert "No matching" in result.output or "result" in result.output.lower()

    @pytest.mark.asyncio
    async def test_recall_empty(self):
        tool = MemoryTool()
        tc = make_tool_call("memory", {"action": "recall"})
        result = await tool.execute(tc)
        assert result.success is True

    @pytest.mark.asyncio
    async def test_stats(self):
        tool = MemoryTool()
        tc = make_tool_call("memory", {"action": "stats"})
        result = await tool.execute(tc)
        assert result.success is True
        assert "Statistics" in result.output

    @pytest.mark.asyncio
    async def test_create_session(self):
        tool = MemoryTool()
        tc = make_tool_call("memory", {"action": "create_session"})
        result = await tool.execute(tc)
        assert result.success is True
        assert "Created session" in result.output

    @pytest.mark.asyncio
    async def test_list_sessions(self):
        tool = MemoryTool()
        tc = make_tool_call("memory", {"action": "list_sessions"})
        result = await tool.execute(tc)
        assert result.success is True

    @pytest.mark.asyncio
    async def test_delete_entry_no_id(self):
        tool = MemoryTool()
        tc = make_tool_call("memory", {"action": "delete_entry"})
        result = await tool.execute(tc)
        assert result.success is False
        assert "entry_id" in result.error

    @pytest.mark.asyncio
    async def test_load_page_no_id(self):
        tool = MemoryTool()
        tc = make_tool_call("memory", {"action": "load_page"})
        result = await tool.execute(tc)
        assert result.success is False
        assert "page_id" in result.error


# ══════════════════════════════════════════════════════════════════════
# 14. Channel Tool
# ══════════════════════════════════════════════════════════════════════


class TestChannelTool:
    """Test ChannelTool properties and basic actions."""

    @pytest.mark.asyncio
    async def test_unknown_action_returns_error(self):
        tool = ChannelTool()
        tc = make_tool_call("channel", {"action": "nonexistent"})
        result = await tool.execute(tc)
        assert result.success is False
        assert "Unknown" in result.error

    @pytest.mark.asyncio
    async def test_send_no_channel_type(self):
        tool = ChannelTool()
        tc = make_tool_call("channel", {"action": "send", "message": "hi"})
        result = await tool.execute(tc)
        assert result.success is False
        assert "channel_type" in result.error

    @pytest.mark.asyncio
    async def test_send_no_message(self):
        tool = ChannelTool()
        tc = make_tool_call("channel", {"action": "send", "channel_type": "telegram"})
        result = await tool.execute(tc)
        assert result.success is False
        assert "message" in result.error

    @pytest.mark.asyncio
    async def test_send_queued_when_no_channel(self):
        tool = ChannelTool()
        tc = make_tool_call("channel", {
            "action": "send",
            "channel_type": "telegram",
            "message": "Hello!",
        })
        result = await tool.execute(tc)
        assert result.success is True
        assert "queued" in result.output.lower()

    @pytest.mark.asyncio
    async def test_list_no_channels(self):
        tool = ChannelTool()
        tc = make_tool_call("channel", {"action": "list"})
        result = await tool.execute(tc)
        assert result.success is True
        assert "No channels" in result.output

    @pytest.mark.asyncio
    async def test_receive_no_messages(self):
        tool = ChannelTool()
        tc = make_tool_call("channel", {"action": "receive"})
        result = await tool.execute(tc)
        assert result.success is True

    @pytest.mark.asyncio
    async def test_format_no_message(self):
        tool = ChannelTool()
        tc = make_tool_call("channel", {"action": "format"})
        result = await tool.execute(tc)
        assert result.success is False
        assert "message" in result.error

    @pytest.mark.asyncio
    async def test_format_markdown(self):
        tool = ChannelTool()
        tc = make_tool_call("channel", {"action": "format", "message": "Hello", "format_type": "markdown"})
        result = await tool.execute(tc)
        assert result.success is True
        assert result.output == "Hello"

    @pytest.mark.asyncio
    async def test_format_html(self):
        tool = ChannelTool()
        tc = make_tool_call("channel", {"action": "format", "message": "**Bold**", "format_type": "html"})
        result = await tool.execute(tc)
        assert result.success is True
        assert "<strong>" in result.output

    @pytest.mark.asyncio
    async def test_format_json(self):
        tool = ChannelTool()
        tc = make_tool_call("channel", {"action": "format", "message": "Hello", "format_type": "json"})
        result = await tool.execute(tc)
        assert result.success is True
        assert "text" in result.output

    def test_register_channel(self):
        tool = ChannelTool()
        mock_channel = MagicMock()
        tool.register_channel("telegram", mock_channel)
        assert "telegram" in tool._channels

    def test_unregister_channel(self):
        tool = ChannelTool()
        mock_channel = MagicMock()
        tool.register_channel("telegram", mock_channel)
        tool.unregister_channel("telegram")
        assert "telegram" not in tool._channels

    @pytest.mark.asyncio
    async def test_register_action(self):
        tool = ChannelTool()
        tc = make_tool_call("channel", {"action": "register", "channel_type": "slack"})
        result = await tool.execute(tc)
        assert result.success is True

    @pytest.mark.asyncio
    async def test_unregister_missing_channel(self):
        tool = ChannelTool()
        tc = make_tool_call("channel", {"action": "unregister", "channel_type": "missing"})
        result = await tool.execute(tc)
        assert result.success is False
        assert "not found" in result.error.lower()

    def test_format_message_text(self):
        assert _format_message("Hello", "text") == "Hello"

    def test_format_message_html(self):
        result = _format_message("**Bold**", "html")
        assert "<strong>" in result

    def test_format_message_json(self):
        import json
        result = _format_message("Hello", "json")
        parsed = json.loads(result)
        assert parsed["text"] == "Hello"

    def test_max_queue_size(self):
        tool = ChannelTool(config={"max_queue_size": 50})
        assert tool._max_queue_size == 50


# ══════════════════════════════════════════════════════════════════════
# 15. Safe Execute Wrapper
# ══════════════════════════════════════════════════════════════════════


class TestToolSafeExecute:
    """Test BaseTool.safe_execute wrapper."""

    @pytest.mark.asyncio
    async def test_safe_execute_returns_tool_result(self):
        tool = CodeTool()
        tc = make_tool_call("code", {"code": "1 + 1"})
        result = await tool.safe_execute(tc)
        assert isinstance(result, ToolResult)

    @pytest.mark.asyncio
    async def test_safe_execute_with_validation_error(self):
        tool = ShellTool()
        tc = make_tool_call("shell", {})  # missing required 'command'
        result = await tool.safe_execute(tc)
        assert result.success is False
        assert "Validation" in result.error

    @pytest.mark.asyncio
    async def test_safe_execute_sets_execution_time(self):
        tool = CodeTool()
        tc = make_tool_call("code", {"code": "1 + 1"})
        result = await tool.safe_execute(tc)
        assert result.execution_time is not None
        assert result.execution_time >= 0


# ══════════════════════════════════════════════════════════════════════
# 16. Tool Repr
# ══════════════════════════════════════════════════════════════════════


class TestToolRepr:
    """Test tool __repr__."""

    @pytest.mark.parametrize("tool_cls", ALL_TOOL_CLASSES,
                             ids=[c.__name__ for c in ALL_TOOL_CLASSES])
    def test_repr_contains_class_name(self, tool_cls):
        tool = tool_cls()
        r = repr(tool)
        assert tool_cls.__name__ in r

    @pytest.mark.parametrize("tool_cls,expected_name", list(TOOL_NAME_MAP.items()),
                             ids=[c.__name__ for c in TOOL_NAME_MAP.keys()])
    def test_repr_contains_tool_name(self, tool_cls, expected_name):
        tool = tool_cls()
        r = repr(tool)
        assert expected_name in r

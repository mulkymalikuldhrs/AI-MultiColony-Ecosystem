"""Comprehensive tests for Sandbox module (DockerSandbox).

Covers container lifecycle, command execution, file operations,
resource limits, and stats with mocked Docker SDK.
"""

from __future__ import annotations

import sys
import time
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from ai_multicolony.sandbox.docker import DockerSandbox
from ai_multicolony.exceptions import SandboxError


@pytest.fixture(autouse=True)
def mock_docker_module():
    """Ensure docker module is mocked for all tests in this module."""
    mock_docker = MagicMock()
    # Store original
    original = sys.modules.get("docker")
    sys.modules["docker"] = mock_docker
    yield mock_docker
    # Restore
    if original is not None:
        sys.modules["docker"] = original
    else:
        sys.modules.pop("docker", None)


def _make_client(containers=None):
    """Create a mock Docker client."""
    client = MagicMock()
    client.containers = containers or MagicMock()
    return client


# ============================================================
# DockerSandbox Init Tests
# ============================================================


class TestDockerSandboxInit:
    """Test DockerSandbox initialization."""

    def test_default_init(self):
        sb = DockerSandbox()
        assert sb._image == "python:3.12-slim"
        assert sb._memory_limit == "512m"
        assert sb._cpu_limit == 1.0
        assert sb._timeout == 300
        assert sb._network_disabled is True
        assert sb._work_dir == "/workspace"
        assert sb._container_id is None
        assert sb._created_at is None

    def test_custom_init(self):
        sb = DockerSandbox(
            image="node:18",
            memory_limit="1g",
            cpu_limit=2.0,
            timeout=600,
            network_disabled=False,
            work_dir="/app",
            env_vars={"NODE_ENV": "test"},
        )
        assert sb._image == "node:18"
        assert sb._memory_limit == "1g"
        assert sb._cpu_limit == 2.0
        assert sb._timeout == 600
        assert sb._network_disabled is False
        assert sb._work_dir == "/app"
        assert sb._env_vars["NODE_ENV"] == "test"

    def test_is_running_false_initially(self):
        sb = DockerSandbox()
        assert sb.is_running is False

    def test_container_id_none_initially(self):
        sb = DockerSandbox()
        assert sb.container_id is None


# ============================================================
# DockerSandbox Create Tests
# ============================================================


class TestDockerSandboxCreate:
    """Test DockerSandbox container creation."""

    async def test_create_success(self, mock_docker_module):
        sb = DockerSandbox()
        mock_container = MagicMock()
        mock_container.id = "abc123def456"
        mock_client = _make_client()
        mock_client.containers.run.return_value = mock_container
        mock_docker_module.from_env.return_value = mock_client

        container_id = await sb.create()
        assert container_id == "abc123def456"
        assert sb._container_id == "abc123def456"
        assert sb._created_at is not None

    async def test_create_sets_running(self, mock_docker_module):
        sb = DockerSandbox()
        mock_container = MagicMock()
        mock_container.id = "abc123def456"
        mock_client = _make_client()
        mock_client.containers.run.return_value = mock_container
        mock_docker_module.from_env.return_value = mock_client

        await sb.create()
        assert sb.is_running is True

    async def test_create_with_network_disabled(self, mock_docker_module):
        sb = DockerSandbox(network_disabled=True)
        mock_container = MagicMock()
        mock_container.id = "abc123"
        mock_client = _make_client()
        mock_client.containers.run.return_value = mock_container
        mock_docker_module.from_env.return_value = mock_client

        await sb.create()
        call_kwargs = mock_client.containers.run.call_args[1]
        assert call_kwargs["network_mode"] == "none"

    async def test_create_with_network_enabled(self, mock_docker_module):
        sb = DockerSandbox(network_disabled=False)
        mock_container = MagicMock()
        mock_container.id = "abc123"
        mock_client = _make_client()
        mock_client.containers.run.return_value = mock_container
        mock_docker_module.from_env.return_value = mock_client

        await sb.create()
        call_kwargs = mock_client.containers.run.call_args[1]
        assert call_kwargs["network_mode"] == "bridge"

    async def test_create_with_memory_limit(self, mock_docker_module):
        sb = DockerSandbox(memory_limit="1g")
        mock_container = MagicMock()
        mock_container.id = "abc123"
        mock_client = _make_client()
        mock_client.containers.run.return_value = mock_container
        mock_docker_module.from_env.return_value = mock_client

        await sb.create()
        call_kwargs = mock_client.containers.run.call_args[1]
        assert call_kwargs["mem_limit"] == "1g"

    async def test_create_with_env_vars(self, mock_docker_module):
        sb = DockerSandbox(env_vars={"KEY": "VALUE"})
        mock_container = MagicMock()
        mock_container.id = "abc123"
        mock_client = _make_client()
        mock_client.containers.run.return_value = mock_container
        mock_docker_module.from_env.return_value = mock_client

        await sb.create()
        call_kwargs = mock_client.containers.run.call_args[1]
        assert call_kwargs["environment"]["KEY"] == "VALUE"

    async def test_create_docker_error(self, mock_docker_module):
        sb = DockerSandbox()
        mock_client = _make_client()
        mock_client.containers.run.side_effect = Exception("Cannot start container")
        mock_docker_module.from_env.return_value = mock_client

        with pytest.raises(SandboxError, match="Failed to create sandbox"):
            await sb.create()

    async def test_create_container_id_truncated(self, mock_docker_module):
        sb = DockerSandbox()
        mock_container = MagicMock()
        mock_container.id = "verylongcontaineridthatshouldbetruncated"
        mock_client = _make_client()
        mock_client.containers.run.return_value = mock_container
        mock_docker_module.from_env.return_value = mock_client

        container_id = await sb.create()
        assert len(container_id) == 12

    async def test_create_labels_set(self, mock_docker_module):
        sb = DockerSandbox()
        mock_container = MagicMock()
        mock_container.id = "abc123def456"
        mock_client = _make_client()
        mock_client.containers.run.return_value = mock_container
        mock_docker_module.from_env.return_value = mock_client

        await sb.create()
        call_kwargs = mock_client.containers.run.call_args[1]
        assert "ai_multicolony_sandbox" in call_kwargs["labels"]

    async def test_create_with_cpu_limit(self, mock_docker_module):
        sb = DockerSandbox(cpu_limit=2.0)
        mock_container = MagicMock()
        mock_container.id = "abc123"
        mock_client = _make_client()
        mock_client.containers.run.return_value = mock_container
        mock_docker_module.from_env.return_value = mock_client

        await sb.create()
        call_kwargs = mock_client.containers.run.call_args[1]
        assert call_kwargs["nano_cpus"] == int(2.0 * 1e9)


# ============================================================
# DockerSandbox Execute Tests
# ============================================================


class TestDockerSandboxExecute:
    """Test DockerSandbox command execution."""

    async def test_execute_not_created_raises(self):
        sb = DockerSandbox()
        with pytest.raises(SandboxError, match="not created"):
            await sb.execute("ls")

    async def test_execute_success(self, mock_docker_module):
        sb = DockerSandbox()
        sb._container_id = "test123"
        mock_container = MagicMock()
        exec_result = MagicMock()
        exec_result.output = (b"hello\n", b"")
        exec_result.exit_code = 0
        mock_container.exec_run.return_value = exec_result
        mock_client = _make_client()
        mock_client.containers.get.return_value = mock_container
        mock_docker_module.from_env.return_value = mock_client

        result = await sb.execute("echo hello")
        assert result["stdout"] == "hello\n"
        assert result["exit_code"] == 0
        assert result["command"] == "echo hello"
        assert "duration" in result

    async def test_execute_with_stderr(self, mock_docker_module):
        sb = DockerSandbox()
        sb._container_id = "test123"
        mock_container = MagicMock()
        exec_result = MagicMock()
        exec_result.output = (b"", b"error message\n")
        exec_result.exit_code = 1
        mock_container.exec_run.return_value = exec_result
        mock_client = _make_client()
        mock_client.containers.get.return_value = mock_container
        mock_docker_module.from_env.return_value = mock_client

        result = await sb.execute("bad_command")
        assert result["stderr"] == "error message\n"
        assert result["exit_code"] == 1

    async def test_execute_with_workdir(self, mock_docker_module):
        sb = DockerSandbox()
        sb._container_id = "test123"
        mock_container = MagicMock()
        exec_result = MagicMock()
        exec_result.output = (b"ok", b"")
        exec_result.exit_code = 0
        mock_container.exec_run.return_value = exec_result
        mock_client = _make_client()
        mock_client.containers.get.return_value = mock_container
        mock_docker_module.from_env.return_value = mock_client

        await sb.execute("ls", work_dir="/tmp")
        call_kwargs = mock_container.exec_run.call_args[1]
        assert call_kwargs["workdir"] == "/tmp"

    async def test_execute_with_env_vars(self, mock_docker_module):
        sb = DockerSandbox()
        sb._container_id = "test123"
        mock_container = MagicMock()
        exec_result = MagicMock()
        exec_result.output = (b"ok", b"")
        exec_result.exit_code = 0
        mock_container.exec_run.return_value = exec_result
        mock_client = _make_client()
        mock_client.containers.get.return_value = mock_container
        mock_docker_module.from_env.return_value = mock_client

        await sb.execute("env", env_vars={"FOO": "bar"})
        call_kwargs = mock_container.exec_run.call_args[1]
        assert call_kwargs["environment"]["FOO"] == "bar"

    async def test_execute_error(self, mock_docker_module):
        sb = DockerSandbox()
        sb._container_id = "test123"
        mock_client = _make_client()
        mock_client.containers.get.side_effect = Exception("Container not found")
        mock_docker_module.from_env.return_value = mock_client

        with pytest.raises(SandboxError, match="Execution failed"):
            await sb.execute("ls")

    async def test_execute_null_stdout(self, mock_docker_module):
        sb = DockerSandbox()
        sb._container_id = "test123"
        mock_container = MagicMock()
        exec_result = MagicMock()
        exec_result.output = (None, b"")
        exec_result.exit_code = 0
        mock_container.exec_run.return_value = exec_result
        mock_client = _make_client()
        mock_client.containers.get.return_value = mock_container
        mock_docker_module.from_env.return_value = mock_client

        result = await sb.execute("ls")
        assert result["stdout"] == ""

    async def test_execute_null_stderr(self, mock_docker_module):
        sb = DockerSandbox()
        sb._container_id = "test123"
        mock_container = MagicMock()
        exec_result = MagicMock()
        exec_result.output = (b"out", None)
        exec_result.exit_code = 0
        mock_container.exec_run.return_value = exec_result
        mock_client = _make_client()
        mock_client.containers.get.return_value = mock_container
        mock_docker_module.from_env.return_value = mock_client

        result = await sb.execute("ls")
        assert result["stderr"] == ""

    async def test_execute_tracks_duration(self, mock_docker_module):
        sb = DockerSandbox()
        sb._container_id = "test123"
        mock_container = MagicMock()
        exec_result = MagicMock()
        exec_result.output = (b"ok", b"")
        exec_result.exit_code = 0
        mock_container.exec_run.return_value = exec_result
        mock_client = _make_client()
        mock_client.containers.get.return_value = mock_container
        mock_docker_module.from_env.return_value = mock_client

        result = await sb.execute("sleep 1")
        assert result["duration"] >= 0

    async def test_execute_demux_true(self, mock_docker_module):
        sb = DockerSandbox()
        sb._container_id = "test123"
        mock_container = MagicMock()
        exec_result = MagicMock()
        exec_result.output = (b"out", b"")
        exec_result.exit_code = 0
        mock_container.exec_run.return_value = exec_result
        mock_client = _make_client()
        mock_client.containers.get.return_value = mock_container
        mock_docker_module.from_env.return_value = mock_client

        await sb.execute("cmd")
        call_kwargs = mock_container.exec_run.call_args[1]
        assert call_kwargs["demux"] is True


# ============================================================
# DockerSandbox Python Execution Tests
# ============================================================


class TestDockerSandboxPython:
    """Test DockerSandbox Python code execution."""

    async def test_execute_python_not_created_raises(self):
        sb = DockerSandbox()
        with pytest.raises(SandboxError, match="not created"):
            await sb.execute_python("print('hello')")

    async def test_execute_python_writes_and_executes(self):
        sb = DockerSandbox()
        sb._container_id = "test123"

        with patch.object(sb, "write_file", new_callable=AsyncMock) as mock_write, \
             patch.object(sb, "execute", new_callable=AsyncMock) as mock_exec:
            mock_exec.return_value = {"stdout": "hello", "exit_code": 0}
            result = await sb.execute_python("print('hello')")
            mock_write.assert_called_once_with("/tmp/_exec.py", "print('hello')")
            mock_exec.assert_called_once_with("python /tmp/_exec.py", timeout=None)

    async def test_execute_python_with_timeout(self):
        sb = DockerSandbox()
        sb._container_id = "test123"

        with patch.object(sb, "write_file", new_callable=AsyncMock), \
             patch.object(sb, "execute", new_callable=AsyncMock) as mock_exec:
            mock_exec.return_value = {"stdout": "ok", "exit_code": 0}
            await sb.execute_python("print('hello')", timeout=10)
            mock_exec.assert_called_once_with("python /tmp/_exec.py", timeout=10)


# ============================================================
# DockerSandbox File Operations Tests
# ============================================================


class TestDockerSandboxFileOps:
    """Test DockerSandbox file operations."""

    async def test_write_file_not_created_raises(self):
        sb = DockerSandbox()
        with pytest.raises(SandboxError, match="not created"):
            await sb.write_file("/tmp/test.py", "print(1)")

    async def test_write_file_success(self, mock_docker_module):
        sb = DockerSandbox()
        sb._container_id = "test123"
        mock_container = MagicMock()
        mock_container.put_archive = MagicMock()
        mock_client = _make_client()
        mock_client.containers.get.return_value = mock_container
        mock_docker_module.from_env.return_value = mock_client

        await sb.write_file("/workspace/test.py", "print('hello')")
        mock_container.put_archive.assert_called_once()

    async def test_write_file_error(self, mock_docker_module):
        sb = DockerSandbox()
        sb._container_id = "test123"
        mock_client = _make_client()
        mock_client.containers.get.side_effect = Exception("Not found")
        mock_docker_module.from_env.return_value = mock_client

        with pytest.raises(SandboxError, match="Write failed"):
            await sb.write_file("/test.py", "code")

    async def test_read_file_not_created_raises(self):
        sb = DockerSandbox()
        with pytest.raises(SandboxError, match="not created"):
            await sb.read_file("/tmp/test.py")

    async def test_copy_file_not_created_raises(self):
        sb = DockerSandbox()
        with pytest.raises(SandboxError, match="not created"):
            await sb.copy_file("/host/file.txt", "/container/file.txt")

    async def test_copy_file_error(self, mock_docker_module):
        sb = DockerSandbox()
        sb._container_id = "test123"
        mock_client = _make_client()
        mock_client.containers.get.side_effect = Exception("Not found")
        mock_docker_module.from_env.return_value = mock_client

        with pytest.raises(SandboxError, match="Copy failed"):
            await sb.copy_file("/host/f.txt", "/container/f.txt")

    async def test_write_file_empty_content(self, mock_docker_module):
        sb = DockerSandbox()
        sb._container_id = "test123"
        mock_container = MagicMock()
        mock_container.put_archive = MagicMock()
        mock_client = _make_client()
        mock_client.containers.get.return_value = mock_container
        mock_docker_module.from_env.return_value = mock_client

        await sb.write_file("/workspace/empty.txt", "")
        mock_container.put_archive.assert_called_once()

    async def test_write_file_deep_path(self, mock_docker_module):
        sb = DockerSandbox()
        sb._container_id = "test123"
        mock_container = MagicMock()
        mock_container.put_archive = MagicMock()
        mock_client = _make_client()
        mock_client.containers.get.return_value = mock_container
        mock_docker_module.from_env.return_value = mock_client

        await sb.write_file("/a/b/c/file.txt", "content")
        # Verify parent directory was used in put_archive
        call_args = mock_container.put_archive.call_args
        assert call_args is not None


# ============================================================
# DockerSandbox Stats Tests
# ============================================================


class TestDockerSandboxStats:
    """Test DockerSandbox stats."""

    async def test_stats_not_created(self):
        sb = DockerSandbox()
        result = await sb.get_stats()
        assert result["status"] == "not_created"

    async def test_stats_with_container(self, mock_docker_module):
        sb = DockerSandbox()
        sb._container_id = "test123"
        mock_container = MagicMock()
        mock_container.status = "running"
        mock_container.stats.return_value = {
            "cpu_stats": {
                "cpu_usage": {"total_usage": 1000000},
                "system_cpu_usage": 10000000,
                "online_cpus": 2,
            },
            "precpu_stats": {
                "cpu_usage": {"total_usage": 500000},
                "system_cpu_usage": 9000000,
            },
            "memory_stats": {"usage": 52428800, "limit": 536870912},
            "networks": {"eth0": {"rx_bytes": 1000, "tx_bytes": 500}},
        }
        mock_client = _make_client()
        mock_client.containers.get.return_value = mock_container
        mock_docker_module.from_env.return_value = mock_client

        result = await sb.get_stats()
        assert result["container_id"] == "test123"
        assert result["status"] == "running"
        assert result["memory_usage"] == 52428800
        assert result["memory_limit"] == 536870912
        assert result["network_rx"] == 1000
        assert result["network_tx"] == 500

    async def test_stats_error(self, mock_docker_module):
        sb = DockerSandbox()
        sb._container_id = "test123"
        mock_client = _make_client()
        mock_client.containers.get.side_effect = Exception("Cannot connect")
        mock_docker_module.from_env.return_value = mock_client

        result = await sb.get_stats()
        assert "error" in result


class TestDockerSandboxCPU:
    """Test CPU percent calculation."""

    def test_calculate_cpu_percent(self):
        sb = DockerSandbox()
        stats = {
            "cpu_stats": {
                "cpu_usage": {"total_usage": 2000000},
                "system_cpu_usage": 20000000,
                "online_cpus": 2,
            },
            "precpu_stats": {
                "cpu_usage": {"total_usage": 1000000},
                "system_cpu_usage": 10000000,
            },
        }
        result = sb._calculate_cpu_percent(stats)
        assert result > 0

    def test_calculate_cpu_percent_missing_data(self):
        sb = DockerSandbox()
        stats = {}
        result = sb._calculate_cpu_percent(stats)
        assert result == 0.0

    def test_calculate_cpu_percent_zero_delta(self):
        sb = DockerSandbox()
        stats = {
            "cpu_stats": {
                "cpu_usage": {"total_usage": 0},
                "system_cpu_usage": 0,
                "online_cpus": 1,
            },
            "precpu_stats": {
                "cpu_usage": {"total_usage": 0},
                "system_cpu_usage": 0,
            },
        }
        result = sb._calculate_cpu_percent(stats)
        assert result == 0.0

    def test_calculate_cpu_percent_high_usage(self):
        sb = DockerSandbox()
        stats = {
            "cpu_stats": {
                "cpu_usage": {"total_usage": 9000000},
                "system_cpu_usage": 10000000,
                "online_cpus": 4,
            },
            "precpu_stats": {
                "cpu_usage": {"total_usage": 1000000},
                "system_cpu_usage": 9000000,
            },
        }
        result = sb._calculate_cpu_percent(stats)
        # (8M / 1M) * 4 * 100 = 3200% (4 CPUs fully utilized)
        assert result > 0


# ============================================================
# DockerSandbox Destroy Tests
# ============================================================


class TestDockerSandboxDestroy:
    """Test DockerSandbox destroy."""

    async def test_destroy_not_created(self):
        sb = DockerSandbox()
        await sb.destroy()  # Should not raise
        assert sb._container_id is None

    async def test_destroy_success(self, mock_docker_module):
        sb = DockerSandbox()
        sb._container_id = "test123"
        mock_container = MagicMock()
        mock_client = _make_client()
        mock_client.containers.get.return_value = mock_container
        mock_docker_module.from_env.return_value = mock_client

        await sb.destroy()
        mock_container.remove.assert_called_once_with(force=True)
        assert sb._container_id is None

    async def test_destroy_container_error(self, mock_docker_module):
        sb = DockerSandbox()
        sb._container_id = "test123"
        mock_client = _make_client()
        mock_client.containers.get.side_effect = Exception("Not found")
        mock_docker_module.from_env.return_value = mock_client

        await sb.destroy()  # Should not raise
        assert sb._container_id is None

    async def test_destroy_sets_not_running(self, mock_docker_module):
        sb = DockerSandbox()
        sb._container_id = "test123"
        mock_container = MagicMock()
        mock_client = _make_client()
        mock_client.containers.get.return_value = mock_container
        mock_docker_module.from_env.return_value = mock_client

        await sb.destroy()
        assert sb.is_running is False


# ============================================================
# DockerSandbox Properties Tests
# ============================================================


class TestDockerSandboxProperties:
    """Test DockerSandbox properties."""

    def test_is_running_true(self):
        sb = DockerSandbox()
        sb._container_id = "test123"
        assert sb.is_running is True

    def test_is_running_false(self):
        sb = DockerSandbox()
        assert sb.is_running is False

    def test_container_id_set(self):
        sb = DockerSandbox()
        sb._container_id = "abc123"
        assert sb.container_id == "abc123"

    def test_container_id_unset(self):
        sb = DockerSandbox()
        assert sb.container_id is None

    def test_default_work_dir(self):
        sb = DockerSandbox()
        assert sb._work_dir == "/workspace"

    def test_default_image(self):
        sb = DockerSandbox()
        assert sb._image == "python:3.12-slim"

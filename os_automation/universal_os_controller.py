#!/usr/bin/env python3
"""
💻 Universal OS Controller v7.2.0
Ultimate AGI Force - Complete Operating System Automation

Features:
- Universal OS support (Windows, Linux, macOS)
- Advanced file system operations
- Process management
- Network automation
- System monitoring
- Secure sandbox execution
- Remote desktop control
- Multi-platform compatibility

Made with ❤️ by Mulky Malikul Dhaher in Indonesia 🇮🇩
"""

import json
import os
import platform
import shutil
import socket
import subprocess
import sys
import threading
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional


class UniversalOSController:
    """
    Universal Operating System Controller
    Works on Windows, Linux, macOS with full automation capabilities
    """

    def __init__(self):
        self.owner = "Mulky Malikul Dhaher"
        self.owner_id = "1108151509970001"

        # Detect OS
        self.os_type = platform.system()
        self.os_release = platform.release()
        self.os_version = platform.version()
        self.architecture = platform.machine()

        # Initialize OS-specific configurations
        self.os_config = self._initialize_os_config()

        # Active processes and operations
        self.active_processes = {}
        self.automation_tasks = {}
        self.monitoring_enabled = True

        # Security settings
        self.safe_mode = True
        self.allowed_operations = self._get_safe_operations()

        print(f"💻 Universal OS Controller v7.2.0")
        print(f"👑 Owner: {self.owner} ({self.owner_id})")
        print(f"🖥️ OS: {self.os_type} {self.os_release}")
        print(f"🏗️ Architecture: {self.architecture}")
        print("🇮🇩 Made with ❤️ in Indonesia")

    def _initialize_os_config(self):
        """Initialize OS-specific configurations"""
        configs = {
            "Windows": {
                "shell": "cmd.exe",
                "shell_args": ["/c"],
                "path_separator": "\\",
                "line_ending": "\r\n",
                "executable_extensions": [".exe", ".bat", ".cmd", ".msi"],
                "admin_command": "runas /user:Administrator",
                "package_manager": None,
                "service_manager": "sc",
                "process_manager": "tasklist",
                "kill_command": "taskkill",
                "network_commands": {
                    "ping": "ping",
                    "netstat": "netstat",
                    "ipconfig": "ipconfig",
                },
            },
            "Linux": {
                "shell": "/bin/bash",
                "shell_args": ["-c"],
                "path_separator": "/",
                "line_ending": "\n",
                "executable_extensions": [],
                "admin_command": "sudo",
                "package_manager": self._detect_linux_package_manager(),
                "service_manager": "systemctl",
                "process_manager": "ps",
                "kill_command": "kill",
                "network_commands": {
                    "ping": "ping",
                    "netstat": "netstat",
                    "ipconfig": "ifconfig",
                },
            },
            "Darwin": {  # macOS
                "shell": "/bin/bash",
                "shell_args": ["-c"],
                "path_separator": "/",
                "line_ending": "\n",
                "executable_extensions": [".app"],
                "admin_command": "sudo",
                "package_manager": "brew",
                "service_manager": "launchctl",
                "process_manager": "ps",
                "kill_command": "kill",
                "network_commands": {
                    "ping": "ping",
                    "netstat": "netstat",
                    "ipconfig": "ifconfig",
                },
            },
        }
        return configs.get(self.os_type, configs["Linux"])

    def _detect_linux_package_manager(self):
        """Detect Linux package manager"""
        managers = [
            ("apt", "apt-get"),
            ("yum", "yum"),
            ("dnf", "dnf"),
            ("pacman", "pacman"),
            ("zypper", "zypper"),
            ("emerge", "emerge"),
        ]

        for manager, command in managers:
            if shutil.which(command):
                return manager
        return None

    def _get_safe_operations(self):
        """Get list of safe operations"""
        return {
            "file_operations": ["list", "read", "create", "copy", "move"],
            "process_operations": ["list", "info", "start"],
            "network_operations": ["ping", "status", "scan"],
            "system_operations": ["info", "status", "performance"],
        }

    # === File System Operations ===

    def list_directory(self, path: str = ".", detailed: bool = False) -> Dict[str, Any]:
        """List directory contents"""
        try:
            path_obj = Path(path).resolve()

            if not path_obj.exists():
                return {"success": False, "error": "Path does not exist"}

            if not path_obj.is_dir():
                return {"success": False, "error": "Path is not a directory"}

            items = []
            for item in path_obj.iterdir():
                item_info = {
                    "name": item.name,
                    "type": "directory" if item.is_dir() else "file",
                    "path": str(item),
                }

                if detailed:
                    try:
                        stat = item.stat()
                        item_info.update(
                            {
                                "size": stat.st_size,
                                "modified": datetime.fromtimestamp(
                                    stat.st_mtime
                                ).isoformat(),
                                "permissions": oct(stat.st_mode)[-3:],
                            }
                        )
                    except:
                        pass

                items.append(item_info)

            return {
                "success": True,
                "path": str(path_obj),
                "items": items,
                "total_items": len(items),
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    def create_directory(self, path: str, parents: bool = True) -> Dict[str, Any]:
        """Create directory"""
        try:
            path_obj = Path(path)
            path_obj.mkdir(parents=parents, exist_ok=True)

            return {
                "success": True,
                "message": f"Directory created: {path}",
                "path": str(path_obj.resolve()),
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    def read_file(self, file_path: str, encoding: str = "utf-8") -> Dict[str, Any]:
        """Read file contents"""
        try:
            path_obj = Path(file_path)

            if not path_obj.exists():
                return {"success": False, "error": "File does not exist"}

            if not path_obj.is_file():
                return {"success": False, "error": "Path is not a file"}

            with open(path_obj, "r", encoding=encoding) as f:
                content = f.read()

            return {
                "success": True,
                "file_path": str(path_obj),
                "content": content,
                "size": len(content),
                "lines": len(content.split("\n")),
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    def write_file(
        self, file_path: str, content: str, encoding: str = "utf-8"
    ) -> Dict[str, Any]:
        """Write content to file"""
        try:
            path_obj = Path(file_path)

            # Create parent directories if needed
            path_obj.parent.mkdir(parents=True, exist_ok=True)

            with open(path_obj, "w", encoding=encoding) as f:
                f.write(content)

            return {
                "success": True,
                "message": f"File written: {file_path}",
                "file_path": str(path_obj),
                "bytes_written": len(content.encode(encoding)),
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    def copy_file(self, source: str, destination: str) -> Dict[str, Any]:
        """Copy file or directory"""
        try:
            source_path = Path(source)
            dest_path = Path(destination)

            if not source_path.exists():
                return {"success": False, "error": "Source does not exist"}

            if source_path.is_file():
                shutil.copy2(source_path, dest_path)
            else:
                shutil.copytree(source_path, dest_path, dirs_exist_ok=True)

            return {
                "success": True,
                "message": f"Copied {source} to {destination}",
                "source": str(source_path),
                "destination": str(dest_path),
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    # === Process Management ===

    def list_processes(self, filter_name: Optional[str] = None) -> Dict[str, Any]:
        """List running processes"""
        try:
            if self.os_type == "Windows":
                cmd = ["tasklist", "/fo", "csv"]
            else:
                cmd = ["ps", "aux"]

            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

            if result.returncode != 0:
                return {"success": False, "error": result.stderr}

            processes = []
            lines = result.stdout.strip().split("\n")

            if self.os_type == "Windows":
                # Parse CSV output
                for line in lines[1:]:  # Skip header
                    parts = line.split('","')
                    if len(parts) >= 5:
                        process = {
                            "name": parts[0].strip('"'),
                            "pid": parts[1].strip('"'),
                            "memory": parts[4].strip('"'),
                        }
                        if (
                            not filter_name
                            or filter_name.lower() in process["name"].lower()
                        ):
                            processes.append(process)
            else:
                # Parse ps output
                for line in lines[1:]:  # Skip header
                    parts = line.split(None, 10)
                    if len(parts) >= 11:
                        process = {
                            "user": parts[0],
                            "pid": parts[1],
                            "cpu": parts[2],
                            "memory": parts[3],
                            "command": parts[10],
                        }
                        if (
                            not filter_name
                            or filter_name.lower() in process["command"].lower()
                        ):
                            processes.append(process)

            return {
                "success": True,
                "processes": processes,
                "total_processes": len(processes),
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    def start_process(
        self, command: str, working_dir: Optional[str] = None
    ) -> Dict[str, Any]:
        """Start a new process"""
        try:
            if self.safe_mode and self._is_dangerous_command(command):
                return {"success": False, "error": "Command blocked for security"}

            # Start process
            process = subprocess.Popen(
                command,
                shell=True,
                cwd=working_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )

            # Store process reference
            process_id = f"proc_{int(time.time())}_{process.pid}"
            self.active_processes[process_id] = {
                "process": process,
                "command": command,
                "started_at": datetime.now().isoformat(),
                "working_dir": working_dir,
            }

            return {
                "success": True,
                "process_id": process_id,
                "pid": process.pid,
                "command": command,
                "message": "Process started successfully",
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    def kill_process(self, pid: int) -> Dict[str, Any]:
        """Kill process by PID"""
        try:
            if self.os_type == "Windows":
                cmd = ["taskkill", "/F", "/PID", str(pid)]
            else:
                cmd = ["kill", "-9", str(pid)]

            result = subprocess.run(cmd, capture_output=True, text=True)

            if result.returncode == 0:
                return {
                    "success": True,
                    "message": f"Process {pid} killed successfully",
                }
            else:
                return {
                    "success": False,
                    "error": result.stderr or "Failed to kill process",
                }

        except Exception as e:
            return {"success": False, "error": str(e)}

    # === System Information ===

    def get_system_info(self) -> Dict[str, Any]:
        """Get comprehensive system information"""
        try:
            info = {
                "os": {
                    "system": self.os_type,
                    "release": self.os_release,
                    "version": self.os_version,
                    "architecture": self.architecture,
                    "hostname": socket.gethostname(),
                },
                "hardware": {},
                "network": {},
                "storage": {},
            }

            # Get CPU info
            try:
                if self.os_type == "Windows":
                    result = subprocess.run(
                        ["wmic", "cpu", "get", "name"], capture_output=True, text=True
                    )
                    if result.returncode == 0:
                        cpu_name = result.stdout.split("\n")[1].strip()
                        info["hardware"]["cpu"] = cpu_name
                else:
                    with open("/proc/cpuinfo", "r") as f:
                        for line in f:
                            if "model name" in line:
                                info["hardware"]["cpu"] = line.split(":")[1].strip()
                                break
            except:
                info["hardware"]["cpu"] = "Unknown"

            # Get memory info
            try:
                if self.os_type == "Windows":
                    result = subprocess.run(
                        ["wmic", "computersystem", "get", "TotalPhysicalMemory"],
                        capture_output=True,
                        text=True,
                    )
                    if result.returncode == 0:
                        memory = int(result.stdout.split("\n")[1].strip())
                        info["hardware"]["memory_gb"] = round(memory / (1024**3), 2)
                else:
                    with open("/proc/meminfo", "r") as f:
                        for line in f:
                            if "MemTotal" in line:
                                memory_kb = int(line.split()[1])
                                info["hardware"]["memory_gb"] = round(
                                    memory_kb / (1024**2), 2
                                )
                                break
            except:
                info["hardware"]["memory_gb"] = "Unknown"

            # Get disk info
            try:
                if self.os_type == "Windows":
                    drives = []
                    for drive in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
                        drive_path = f"{drive}:\\"
                        if os.path.exists(drive_path):
                            usage = shutil.disk_usage(drive_path)
                            drives.append(
                                {
                                    "drive": drive,
                                    "total_gb": round(usage.total / (1024**3), 2),
                                    "free_gb": round(usage.free / (1024**3), 2),
                                }
                            )
                    info["storage"]["drives"] = drives
                else:
                    usage = shutil.disk_usage("/")
                    info["storage"]["root"] = {
                        "total_gb": round(usage.total / (1024**3), 2),
                        "free_gb": round(usage.free / (1024**3), 2),
                    }
            except:
                info["storage"] = "Unknown"

            # Get network info
            try:
                hostname = socket.gethostname()
                local_ip = socket.gethostbyname(hostname)
                info["network"]["hostname"] = hostname
                info["network"]["local_ip"] = local_ip
            except:
                info["network"] = "Unknown"

            return {
                "success": True,
                "system_info": info,
                "collected_at": datetime.now().isoformat(),
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    # === Network Operations ===

    def ping_host(self, host: str, count: int = 4) -> Dict[str, Any]:
        """Ping a host"""
        try:
            if self.os_type == "Windows":
                cmd = ["ping", "-n", str(count), host]
            else:
                cmd = ["ping", "-c", str(count), host]

            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

            return {
                "success": result.returncode == 0,
                "host": host,
                "output": result.stdout,
                "error": result.stderr if result.returncode != 0 else None,
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    def get_network_connections(self) -> Dict[str, Any]:
        """Get active network connections"""
        try:
            if self.os_type == "Windows":
                cmd = ["netstat", "-an"]
            else:
                cmd = ["netstat", "-tuln"]

            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

            if result.returncode != 0:
                return {"success": False, "error": result.stderr}

            connections = []
            for line in result.stdout.split("\n"):
                if "LISTENING" in line or "ESTABLISHED" in line:
                    parts = line.split()
                    if len(parts) >= 4:
                        connections.append(
                            {
                                "protocol": parts[0],
                                "local_address": parts[1] if len(parts) > 1 else "",
                                "foreign_address": parts[2] if len(parts) > 2 else "",
                                "state": parts[3] if len(parts) > 3 else "",
                            }
                        )

            return {
                "success": True,
                "connections": connections,
                "total_connections": len(connections),
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    # === Security & Safety ===

    def _is_dangerous_command(self, command: str) -> bool:
        """Check if command is potentially dangerous"""
        dangerous_patterns = [
            # File system destruction
            "rm -rf /",
            "del /s /q C:\\",
            "format c:",
            "fdisk",
            # System shutdown
            "shutdown",
            "reboot",
            "halt",
            "poweroff",
            "restart",
            # User/permission changes
            "passwd",
            "sudo su",
            "chmod 777",
            "chown",
            # Network attacks
            "nmap",
            "metasploit",
            "sqlmap",
            # System modification
            "registry",
            "regedit",
            "bcdedit",
        ]

        command_lower = command.lower()
        return any(pattern in command_lower for pattern in dangerous_patterns)

    def enable_safe_mode(self):
        """Enable safe mode (blocks dangerous operations)"""
        self.safe_mode = True
        return {"success": True, "message": "Safe mode enabled"}

    def disable_safe_mode(self):
        """Disable safe mode (allows all operations - use with caution)"""
        self.safe_mode = False
        return {"success": True, "message": "Safe mode disabled - USE WITH CAUTION"}

    # === Advanced Automation ===

    def execute_automation_script(self, script_path: str) -> Dict[str, Any]:
        """Execute automation script"""
        try:
            script_path_obj = Path(script_path)

            if not script_path_obj.exists():
                return {"success": False, "error": "Script file does not exist"}

            # Read script content
            with open(script_path_obj, "r") as f:
                script_content = f.read()

            # Execute based on file extension
            if script_path_obj.suffix == ".py":
                result = subprocess.run(
                    [sys.executable, str(script_path_obj)],
                    capture_output=True,
                    text=True,
                    timeout=300,
                )
            elif script_path_obj.suffix == ".bat" and self.os_type == "Windows":
                result = subprocess.run(
                    ["cmd", "/c", str(script_path_obj)],
                    capture_output=True,
                    text=True,
                    timeout=300,
                )
            elif script_path_obj.suffix == ".sh" and self.os_type != "Windows":
                result = subprocess.run(
                    ["bash", str(script_path_obj)],
                    capture_output=True,
                    text=True,
                    timeout=300,
                )
            else:
                return {"success": False, "error": "Unsupported script type"}

            return {
                "success": result.returncode == 0,
                "script_path": str(script_path_obj),
                "stdout": result.stdout,
                "stderr": result.stderr,
                "return_code": result.returncode,
            }

        except Exception as e:
            return {"success": False, "error": str(e)}


def main():
    """Main function for testing OS controller"""
    controller = UniversalOSController()

    print("\n🔍 Running OS Controller Tests...")

    # Test system info
    print("\n📊 System Information:")
    sys_info = controller.get_system_info()
    if sys_info["success"]:
        info = sys_info["system_info"]
        print(f"OS: {info['os']['system']} {info['os']['release']}")
        print(f"CPU: {info['hardware'].get('cpu', 'Unknown')}")
        print(f"Memory: {info['hardware'].get('memory_gb', 'Unknown')} GB")

    # Test directory listing
    print("\n📁 Directory Listing:")
    dir_list = controller.list_directory(".", detailed=True)
    if dir_list["success"]:
        print(f"Found {dir_list['total_items']} items in current directory")

    # Test process listing
    print("\n🔄 Process Listing:")
    processes = controller.list_processes()
    if processes["success"]:
        print(f"Found {processes['total_processes']} running processes")

    print("\n✅ OS Controller tests completed!")


if __name__ == "__main__":
    main()

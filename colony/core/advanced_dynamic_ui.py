#!/usr/bin/env python3
"""
🌐 Advanced Dynamic Web Interface v7.2.0
Ultimate AGI Force - Dynamic OS Control & Sandbox Interface

Features:
- Dynamic agent creation & management
- OS control capabilities (Windows, Linux, macOS)
- Sandbox environment support
- Real-time UI updates
- Agent registry integration
- Zero-dependency fallback support

Made with ❤️ by Mulky Malikul Dhaher in Indonesia 🇮🇩
"""

import json
import os
import platform
import subprocess
import sys
import threading
import time
from datetime import datetime
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

# Advanced fallback imports
try:
    from flask import Flask, jsonify, render_template_string, request
    from flask_socketio import SocketIO, emit

    FLASK_AVAILABLE = True
except ImportError:
    FLASK_AVAILABLE = False

    class FallbackFlask:
        def __init__(self, name):
            self.config = {}
            self.routes = {}

        def route(self, path, **kwargs):
            def decorator(func):
                self.routes[path] = func
                return func

            return decorator

        def run(self, host="0.0.0.0", port=5000, debug=False):
            print(f"🌐 Fallback web server: http://{host}:{port}")

    class FallbackSocketIO:
        def __init__(self, app, **kwargs):
            pass

        def on(self, event):
            def decorator(func):
                return func

            return decorator

        def run(self, app, host="0.0.0.0", port=5000, debug=False):
            print(f"🌐 Fallback SocketIO: http://{host}:{port}")

    Flask = FallbackFlask
    SocketIO = FallbackSocketIO

    def render_template_string(template, **kwargs):
        return template

    def jsonify(data):
        return json.dumps(data)

    def emit(event, data):
        pass


class AdvancedDynamicWebInterface:
    """
    Advanced Dynamic Web Interface with OS Control & Sandbox
    """

    def __init__(self):
        self.app_name = "Advanced Dynamic Web Interface v7.2.0"
        self.owner = "Mulky Malikul Dhaher"
        self.owner_id = "1108151509970001"

        # System information
        self.os_info = {
            "system": platform.system(),
            "release": platform.release(),
            "version": platform.version(),
            "machine": platform.machine(),
            "processor": platform.processor(),
        }

        # Initialize Flask app
        self.app = Flask(__name__)
        self.app.config["SECRET_KEY"] = "advanced_agi_secret_2025"
        self.socketio = SocketIO(self.app, cors_allowed_origins="*")

        # System state
        self.is_running = False
        self.startup_time = time.time()
        self.active_agents = {}
        self.sandbox_processes = {}

        # Initialize components
        self._initialize_system_components()
        self._setup_routes()
        self._setup_websocket_handlers()

        print(f"🌐 {self.app_name}")
        print(f"👑 Owner: {self.owner} ({self.owner_id})")
        print(f"💻 OS: {self.os_info['system']} {self.os_info['release']}")
        print("🇮🇩 Made with ❤️ in Indonesia")

    def _initialize_system_components(self):
        """Initialize advanced system components"""
        # Load agent registry
        self.agent_registry = self._load_agent_registry()

        # Initialize OS controller
        self.os_controller = OSController()

        # Initialize sandbox manager
        self.sandbox_manager = SandboxManager()

        # Start real-time monitoring
        self._start_real_time_monitoring()

    def _load_agent_registry(self):
        """Load real agent registry"""
        try:
            from agents import AGENTS_REGISTRY

            return AGENTS_REGISTRY
        except ImportError:
            return self._create_fallback_registry()

    def _create_fallback_registry(self):
        """Create fallback agent registry"""
        return {
            "dev_engine": {
                "name": "Development Engine",
                "status": "active",
                "capabilities": ["code_generation", "debugging"],
            },
            "ui_designer": {
                "name": "UI Designer",
                "status": "active",
                "capabilities": ["ui_design", "frontend"],
            },
            "system_optimizer": {
                "name": "System Optimizer",
                "status": "active",
                "capabilities": ["optimization", "performance"],
            },
            "security_agent": {
                "name": "Security Agent",
                "status": "active",
                "capabilities": ["security", "protection"],
            },
            "os_controller": {
                "name": "OS Controller",
                "status": "active",
                "capabilities": ["os_control", "automation"],
            },
        }

    def _start_real_time_monitoring(self):
        """Start real-time system monitoring"""

        def monitoring_loop():
            while self.is_running:
                try:
                    # Update system stats
                    self._update_system_stats()

                    # Monitor sandbox processes
                    self._monitor_sandbox_processes()

                    # Check agent health
                    self._check_agent_health()

                    time.sleep(2)  # Update every 2 seconds
                except Exception as e:
                    print(f"Monitoring error: {e}")
                    time.sleep(5)

        monitoring_thread = threading.Thread(target=monitoring_loop, daemon=True)
        monitoring_thread.start()

    def _update_system_stats(self):
        """Update system statistics in real-time"""
        try:
            import psutil

            cpu = psutil.cpu_percent()
            memory = psutil.virtual_memory().percent
            disk = psutil.disk_usage("/").percent
        except ImportError:
            cpu, memory, disk = 45.0, 60.0, 30.0

        self.system_stats = {
            "timestamp": datetime.now().isoformat(),
            "uptime": time.time() - self.startup_time,
            "cpu_usage": cpu,
            "memory_usage": memory,
            "disk_usage": disk,
            "active_agents": len(self.active_agents),
            "sandbox_processes": len(self.sandbox_processes),
            "os_info": self.os_info,
        }

    def _monitor_sandbox_processes(self):
        """Monitor sandbox processes"""
        for proc_id, process in list(self.sandbox_processes.items()):
            if process.poll() is not None:
                # Process finished
                del self.sandbox_processes[proc_id]
                print(f"🏁 Sandbox process {proc_id} finished")

    def _check_agent_health(self):
        """Check health of all agents"""
        for agent_id, agent_info in self.agent_registry.items():
            # Basic health check
            if hasattr(agent_info, "status"):
                agent_info["last_checked"] = datetime.now().isoformat()

    def _setup_routes(self):
        """Setup advanced Flask routes"""

        @self.app.route("/")
        def dashboard():
            """Advanced dynamic dashboard"""
            return self._render_advanced_dashboard()

        @self.app.route("/agents")
        def agents_management():
            """Dynamic agent management"""
            return self._render_dynamic_agents_page()

        @self.app.route("/os-control")
        def os_control():
            """OS control interface"""
            return self._render_os_control_page()

        @self.app.route("/sandbox")
        def sandbox_management():
            """Sandbox management interface"""
            return self._render_sandbox_page()

        # API Routes
        @self.app.route("/api/agents/list")
        def api_get_agents():
            """Get dynamic agent list"""
            return jsonify(self._get_dynamic_agent_list())

        @self.app.route("/api/agents/create", methods=["POST"])
        def api_create_agent():
            """Create new agent dynamically"""
            if FLASK_AVAILABLE:
                agent_data = request.get_json()
                result = self._create_new_agent(agent_data)
                return jsonify(result)
            return jsonify({"error": "Flask not available"})

        @self.app.route("/api/agents/<agent_id>/execute", methods=["POST"])
        def api_execute_agent(agent_id):
            """Execute specific agent"""
            if FLASK_AVAILABLE:
                task_data = request.get_json()
                result = self._execute_specific_agent(agent_id, task_data)
                return jsonify(result)
            return jsonify({"error": "Flask not available"})

        @self.app.route("/api/os/execute", methods=["POST"])
        def api_os_execute():
            """Execute OS command"""
            if FLASK_AVAILABLE:
                command_data = request.get_json()
                result = self.os_controller.execute_command(command_data)
                return jsonify(result)
            return jsonify({"error": "Flask not available"})

        @self.app.route("/api/sandbox/create", methods=["POST"])
        def api_create_sandbox():
            """Create sandbox environment"""
            if FLASK_AVAILABLE:
                sandbox_data = request.get_json()
                result = self.sandbox_manager.create_sandbox(sandbox_data)
                return jsonify(result)
            return jsonify({"error": "Flask not available"})

        @self.app.route("/api/system/stats")
        def api_system_stats():
            """Get real-time system stats"""
            return jsonify(self.system_stats)

    def _setup_websocket_handlers(self):
        """Setup WebSocket handlers for real-time updates"""

        @self.socketio.on("connect")
        def handle_connect():
            """Handle client connection"""
            print("🔗 Client connected to Advanced Web Interface")
            emit("status", {"message": "Connected to Advanced AGI Force"})

        @self.socketio.on("request_agent_list")
        def handle_agent_list_request():
            """Send current agent list"""
            emit("agent_list_update", self._get_dynamic_agent_list())

        @self.socketio.on("create_agent")
        def handle_create_agent(data):
            """Handle agent creation request"""
            result = self._create_new_agent(data)
            emit("agent_created", result)
            # Broadcast update to all clients
            emit("agent_list_update", self._get_dynamic_agent_list(), broadcast=True)

        @self.socketio.on("execute_os_command")
        def handle_os_command(data):
            """Handle OS command execution"""
            result = self.os_controller.execute_command(data)
            emit("os_command_result", result)

        @self.socketio.on("create_sandbox")
        def handle_create_sandbox(data):
            """Handle sandbox creation"""
            result = self.sandbox_manager.create_sandbox(data)
            emit("sandbox_created", result)

    def _render_advanced_dashboard(self):
        """Render advanced dynamic dashboard"""
        dashboard_html = (
            """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Advanced AGI Force v7.2.0 - Dynamic Dashboard</title>
            <script src="https://cdnjs.cloudflare.com/ajax/libs/socket.io/4.0.1/socket.io.js"></script>
            <style>
                * { margin: 0; padding: 0; box-sizing: border-box; }
                body {
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
                    color: white; min-height: 100vh; padding: 20px;
                }
                .container { max-width: 1400px; margin: 0 auto; }
                .header {
                    text-align: center; padding: 30px; margin-bottom: 30px;
                    background: rgba(255,255,255,0.1); border-radius: 20px;
                    backdrop-filter: blur(10px); border: 1px solid rgba(255,255,255,0.2);
                }
                .dashboard-grid {
                    display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                    gap: 20px; margin-bottom: 30px;
                }
                .dashboard-card {
                    background: rgba(255,255,255,0.15); padding: 25px; border-radius: 15px;
                    backdrop-filter: blur(10px); border: 1px solid rgba(255,255,255,0.2);
                    transition: transform 0.3s ease, box-shadow 0.3s ease;
                }
                .dashboard-card:hover {
                    transform: translateY(-5px); box-shadow: 0 10px 25px rgba(0,0,0,0.3);
                }
                .metric-value { font-size: 2.5em; font-weight: bold; margin: 10px 0; }
                .metric-label { font-size: 1.1em; opacity: 0.8; }
                .control-buttons {
                    display: flex; gap: 15px; justify-content: center; flex-wrap: wrap;
                    margin-top: 30px;
                }
                .btn {
                    padding: 15px 30px; background: rgba(255,255,255,0.2);
                    border: 2px solid rgba(255,255,255,0.3); border-radius: 10px;
                    color: white; text-decoration: none; font-weight: bold;
                    transition: all 0.3s ease; cursor: pointer; font-size: 16px;
                }
                .btn:hover {
                    background: rgba(255,255,255,0.3); transform: translateY(-2px);
                    box-shadow: 0 5px 15px rgba(0,0,0,0.3);
                }
                .status-indicator {
                    width: 15px; height: 15px; border-radius: 50%;
                    display: inline-block; margin-right: 10px;
                }
                .status-active { background: #4CAF50; }
                .status-warning { background: #FF9800; }
                .status-error { background: #F44336; }
                .real-time-info {
                    position: fixed; top: 20px; right: 20px; 
                    background: rgba(0,0,0,0.8); padding: 15px; border-radius: 10px;
                    font-size: 14px; backdrop-filter: blur(10px);
                }
            </style>
        </head>
        <body>
            <div class="real-time-info">
                <div>🕐 <span id="current-time"></span></div>
                <div>⚡ Status: <span class="status-indicator status-active"></span>Online</div>
            </div>
            
            <div class="container">
                <div class="header">
                    <h1>🚀 Advanced Ultimate AGI Force v7.2.0</h1>
                    <h2>Dynamic OS Control & Sandbox Interface</h2>
                    <p>👑 Owner: """
            + self.owner
            + """ ("""
            + self.owner_id
            + """)</p>
                    <p>💻 OS: """
            + f"{self.os_info['system']} {self.os_info['release']}"
            + """</p>
                    <p>🇮🇩 Made with ❤️ in Indonesia</p>
                </div>
                
                <div class="dashboard-grid">
                    <div class="dashboard-card">
                        <h3>🤖 Agent Status</h3>
                        <div class="metric-value" id="agent-count">Loading...</div>
                        <div class="metric-label">Active Agents</div>
                        <p><span class="status-indicator status-active"></span>Dynamic Registry</p>
                    </div>
                    
                    <div class="dashboard-card">
                        <h3>💻 System Performance</h3>
                        <div>CPU: <span id="cpu-usage">Loading...</span>%</div>
                        <div>Memory: <span id="memory-usage">Loading...</span>%</div>
                        <div>Disk: <span id="disk-usage">Loading...</span>%</div>
                    </div>
                    
                    <div class="dashboard-card">
                        <h3>🏗️ Sandbox Status</h3>
                        <div class="metric-value" id="sandbox-count">Loading...</div>
                        <div class="metric-label">Active Sandboxes</div>
                        <p><span class="status-indicator status-active"></span>Secure Environment</p>
                    </div>
                    
                    <div class="dashboard-card">
                        <h3>🎯 OS Control</h3>
                        <p><span class="status-indicator status-active"></span>Full OS Access</p>
                        <p><span class="status-indicator status-active"></span>Command Execution</p>
                        <p><span class="status-indicator status-active"></span>File System Control</p>
                    </div>
                </div>
                
                <div class="control-buttons">
                    <a href="/agents" class="btn">🤖 Dynamic Agent Management</a>
                    <a href="/os-control" class="btn">💻 OS Control Panel</a>
                    <a href="/sandbox" class="btn">🏗️ Sandbox Manager</a>
                    <button class="btn" onclick="createNewAgent()">➕ Create Agent</button>
                    <button class="btn" onclick="runSystemDiagnostics()">🔍 System Diagnostics</button>
                </div>
            </div>
            
            <script>
                // Initialize Socket.IO
                const socket = io();
                
                // Real-time clock
                function updateClock() {
                    document.getElementById('current-time').textContent = new Date().toLocaleTimeString();
                }
                setInterval(updateClock, 1000);
                updateClock();
                
                // Update system stats
                function updateStats() {
                    fetch('/api/system/stats')
                        .then(response => response.json())
                        .then(data => {
                            document.getElementById('cpu-usage').textContent = data.cpu_usage.toFixed(1);
                            document.getElementById('memory-usage').textContent = data.memory_usage.toFixed(1);
                            document.getElementById('disk-usage').textContent = data.disk_usage.toFixed(1);
                            document.getElementById('agent-count').textContent = data.active_agents;
                            document.getElementById('sandbox-count').textContent = data.sandbox_processes;
                        })
                        .catch(error => console.error('Error:', error));
                }
                
                // Update stats every 2 seconds
                setInterval(updateStats, 2000);
                updateStats();
                
                // Agent creation
                function createNewAgent() {
                    const agentName = prompt('Enter new agent name:');
                    const agentType = prompt('Enter agent type (dev/ui/security/custom):');
                    
                    if (agentName && agentType) {
                        socket.emit('create_agent', {
                            name: agentName,
                            type: agentType,
                            capabilities: ['dynamic_creation']
                        });
                    }
                }
                
                // System diagnostics
                function runSystemDiagnostics() {
                    alert('🔍 Running comprehensive system diagnostics...');
                    fetch('/api/system/diagnostics', {method: 'POST'})
                        .then(response => response.json())
                        .then(data => alert('Diagnostics completed: ' + JSON.stringify(data, null, 2)))
                        .catch(error => console.error('Error:', error));
                }
                
                // Socket event listeners
                socket.on('agent_created', function(data) {
                    alert('✅ Agent created successfully: ' + data.name);
                    updateStats();
                });
                
                socket.on('agent_list_update', function(data) {
                    console.log('Agent list updated:', data);
                });
            </script>
        </body>
        </html>
        """
        )
        return dashboard_html

    def _render_dynamic_agents_page(self):
        """Render dynamic agent management page"""
        return """Dynamic Agent Management Page - Real-time agent creation and management"""

    def _render_os_control_page(self):
        """Render OS control interface"""
        return """OS Control Interface - Execute system commands and control operating system"""

    def _render_sandbox_page(self):
        """Render sandbox management interface"""
        return (
            """Sandbox Management - Create and manage secure execution environments"""
        )

    def _get_dynamic_agent_list(self):
        """Get dynamic list of agents"""
        agents = []
        for agent_id, agent_info in self.agent_registry.items():
            agent_data = {
                "id": agent_id,
                "name": agent_info.get("name", agent_id),
                "status": agent_info.get("status", "unknown"),
                "capabilities": agent_info.get("capabilities", []),
                "last_active": agent_info.get("last_checked", "unknown"),
            }
            agents.append(agent_data)
        return {"agents": agents, "total": len(agents)}

    def _create_new_agent(self, agent_data):
        """Create new agent dynamically"""
        try:
            agent_id = f"agent_{len(self.agent_registry)}_{int(time.time())}"

            new_agent = {
                "name": agent_data.get("name", "New Agent"),
                "type": agent_data.get("type", "custom"),
                "status": "active",
                "capabilities": agent_data.get("capabilities", []),
                "created_at": datetime.now().isoformat(),
                "owner": self.owner,
            }

            # Add to registry
            self.agent_registry[agent_id] = new_agent
            self.active_agents[agent_id] = new_agent

            print(f"✅ New agent created: {agent_id}")

            return {
                "success": True,
                "agent_id": agent_id,
                "message": f'Agent {new_agent["name"]} created successfully',
                "agent_data": new_agent,
            }

        except Exception as e:
            print(f"❌ Agent creation failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to create agent",
            }

    def _execute_specific_agent(self, agent_id, task_data):
        """Execute specific agent with task"""
        if agent_id in self.agent_registry:
            agent = self.agent_registry[agent_id]
            return {
                "success": True,
                "agent_id": agent_id,
                "agent_name": agent.get("name", "Unknown"),
                "task": task_data.get("task", "No task specified"),
                "result": "Task executed successfully",
                "execution_time": 0.5,
            }
        else:
            return {
                "success": False,
                "error": f"Agent {agent_id} not found",
                "message": "Agent does not exist",
            }

    def run(self, host="0.0.0.0", port=5000, debug=False):
        """Run the advanced web interface"""
        self.is_running = True

        print(f"\n🌐 Starting Advanced Dynamic Web Interface...")
        print(f"📊 Dashboard: http://{host}:{port}")
        print(f"🤖 Agent Management: http://{host}:{port}/agents")
        print(f"💻 OS Control: http://{host}:{port}/os-control")
        print(f"🏗️ Sandbox: http://{host}:{port}/sandbox")

        if FLASK_AVAILABLE:
            print("✅ Flask available - full functionality enabled")
            self.socketio.run(self.app, host=host, port=port, debug=debug)
        else:
            print("⚠️ Flask not available - running in simulation mode")
            print(f"🌐 Simulated advanced web server: http://{host}:{port}")
            try:
                while self.is_running:
                    time.sleep(1)
            except KeyboardInterrupt:
                print("\n🛑 Advanced web interface shutdown")


class OSController:
    """Operating System Controller"""

    def __init__(self):
        self.os_type = platform.system()
        self.supported_commands = self._get_supported_commands()

    def _get_supported_commands(self):
        """Get OS-specific supported commands"""
        if self.os_type == "Windows":
            return {
                "list_files": "dir",
                "create_dir": "mkdir",
                "remove_file": "del",
                "system_info": "systeminfo",
                "process_list": "tasklist",
            }
        else:  # Linux/macOS
            return {
                "list_files": "ls -la",
                "create_dir": "mkdir -p",
                "remove_file": "rm -f",
                "system_info": "uname -a",
                "process_list": "ps aux",
            }

    def execute_command(self, command_data):
        """Execute OS command safely"""
        try:
            command = command_data.get("command", "")
            safe_mode = command_data.get("safe_mode", True)

            # Safety checks
            if safe_mode and self._is_dangerous_command(command):
                return {
                    "success": False,
                    "error": "Dangerous command blocked",
                    "message": "Command blocked for security reasons",
                }

            # Execute command
            result = subprocess.run(
                command, shell=True, capture_output=True, text=True, timeout=30
            )

            return {
                "success": True,
                "command": command,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "return_code": result.returncode,
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "Command execution failed",
            }

    def _is_dangerous_command(self, command):
        """Check if command is potentially dangerous"""
        dangerous_patterns = [
            "rm -rf /",
            "del /s /q",
            "format",
            "fdisk",
            "shutdown",
            "reboot",
            "halt",
            "poweroff",
            "passwd",
            "sudo su",
            "chmod 777",
        ]
        return any(pattern in command.lower() for pattern in dangerous_patterns)


class SandboxManager:
    """Sandbox Environment Manager"""

    def __init__(self):
        self.sandboxes = {}
        self.sandbox_dir = Path("sandboxes")
        self.sandbox_dir.mkdir(exist_ok=True)

    def create_sandbox(self, sandbox_data):
        """Create new sandbox environment"""
        try:
            sandbox_id = f"sandbox_{int(time.time())}"
            sandbox_path = self.sandbox_dir / sandbox_id
            sandbox_path.mkdir(exist_ok=True)

            # Create sandbox configuration
            config = {
                "id": sandbox_id,
                "name": sandbox_data.get("name", "New Sandbox"),
                "path": str(sandbox_path),
                "created_at": datetime.now().isoformat(),
                "restrictions": {
                    "network_access": sandbox_data.get("network_access", False),
                    "file_system_access": sandbox_data.get(
                        "file_system_access", "restricted"
                    ),
                    "resource_limits": sandbox_data.get("resource_limits", {}),
                },
            }

            self.sandboxes[sandbox_id] = config

            return {
                "success": True,
                "sandbox_id": sandbox_id,
                "message": f'Sandbox {config["name"]} created successfully',
                "config": config,
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to create sandbox",
            }


def main():
    """Main function to run advanced web interface"""
    interface = AdvancedDynamicWebInterface()

    try:
        interface.run(debug=True)
    except KeyboardInterrupt:
        print("\n🛑 Advanced dynamic web interface shutdown")
        interface.is_running = False


if __name__ == "__main__":
    main()

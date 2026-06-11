"""
🧠 Agentic AI System - Main Entry Point
Autonomous Multi-Agent Intelligence System

v0.4.0 — Major integration fix: EcosystemOrchestrator now drives all
initialization.  Old zombie agent paths and disconnected Flask/gateway
code have been replaced with the unified integration layer.

Made with ❤️ by Mulky Malikul Dhaher in Indonesia 🇮🇩
"""

import asyncio
import sys
import os
import signal
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, List

# Ensure project root is importable
sys.path.append(str(Path(__file__).parent))

logger = logging.getLogger("agentic_ai.main")


# ---------------------------------------------------------------------------
# Banner
# ---------------------------------------------------------------------------

def print_banner():
    """Print system banner"""
    banner = """
╔══════════════════════════════════════════════════════════════════════════════╗
║                        🧠 AGENTIC AI SYSTEM 🧠                               ║
║                                                                              ║
║                    Autonomous Multi-Agent Intelligence                       ║
║                                                                              ║
║               🤖 20+ Specialized Agents | 🔄 Auto-Schedule                   ║
║               🌐 Multi-Platform | 🚀 Self-Expanding                         ║
║               📊 Real-time Sync | 🎯 Intelligent Selection                  ║
║                                                                              ║
║                Made with ❤️ by Mulky Malikul Dhaher 🇮🇩                     ║
╚══════════════════════════════════════════════════════════════════════════════╝
    """
    print(banner)


# ---------------------------------------------------------------------------
# Agent registry — maps logical IDs to actual src.agents classes
# ---------------------------------------------------------------------------

# Each entry: (module_path, class_name, display_name)
DEER_FLOW_AGENTS: Dict[str, Dict[str, str]] = {
    "meta_spawner": {
        "module": "src.agents.agent_02_meta_spawner",
        "class": "Agent02MetaSpawner",
        "display": "Meta Spawner",
    },
    "planner": {
        "module": "src.agents.agent_03_planner",
        "class": "Agent03Planner",
        "display": "Planner",
    },
    "executor": {
        "module": "src.agents.agent_04_executor",
        "class": "Agent04Executor",
        "display": "Executor",
    },
    "designer": {
        "module": "src.agents.agent_05_designer",
        "class": "Agent05Designer",
        "display": "Designer",
    },
    "specialist": {
        "module": "src.agents.agent_06_specialist",
        "class": "Agent06Specialist",
        "display": "Specialist",
    },
    "dynamic_factory": {
        "module": "src.agents.dynamic_agent_factory",
        "class": "DynamicAgentFactory",
        "display": "Dynamic Agent Factory",
    },
    "advanced_creator": {
        "module": "src.agents.advanced_agent_creator",
        "class": "AdvancedAgentCreator",
        "display": "Advanced Agent Creator",
    },
    "web_automation": {
        "module": "src.agents.web_automation_agent",
        "class": "WebAutomationAgent",
        "display": "Web Automation",
    },
    "launcher": {
        "module": "src.agents.launcher_agent",
        "class": "LauncherAgent",
        "display": "Launcher",
    },
    "output_handler": {
        "module": "src.agents.output_handler",
        "class": "OutputHandler",
        "display": "Output Handler",
    },
    "deployment": {
        "module": "src.agents.deployment_agent",
        "class": "DeploymentAgent",
        "display": "Deployment",
    },
    "agent_base": {
        "module": "src.agents.agent_base",
        "class": "AgentBase",
        "display": "Agent Base (Coordinator)",
    },
}


# ---------------------------------------------------------------------------
# Main system class
# ---------------------------------------------------------------------------

class AgenticAISystem:
    """
    Main Agentic AI System orchestrator.

    v0.4.0: All initialisation flows through ``EcosystemOrchestrator`` from
    ``src.integration``.  The quant, organism, gateway, and backend adapters
    are created and wired by the orchestrator.  Deer-flow agents from
    ``src.agents`` are loaded separately and registered with the ecosystem bus.
    """

    def __init__(self, data_dir: Optional[str] = None):
        self.system_id = "agentic_ai_system"
        self.version = "0.4.0"
        self.status = "initializing"
        self.start_time = datetime.now()

        # Core ecosystem — the single source of truth
        self.orchestrator: Optional[Any] = None
        self.bus: Optional[Any] = None          # EcosystemBus
        self.quant: Optional[Any] = None        # QuantAdapter
        self.organism: Optional[Any] = None     # OrganismAdapter
        self.gateway: Optional[Any] = None      # GatewayAdapter
        self.backend: Optional[Any] = None      # BackendAdapter

        # Deer-flow agent instances (keyed by logical ID)
        self.agents: Dict[str, Any] = {}
        self.active_agents: Dict[str, Any] = {}

        # Web interface handle
        self._web_process = None

        # System configuration (backward-compatible)
        self.config = self._load_system_config()
        if data_dir:
            self.config["data_dir"] = data_dir

        # Shutdown flag
        self.shutdown_requested = False

        # Setup signal handlers
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

    # ------------------------------------------------------------------
    # Config
    # ------------------------------------------------------------------

    def _load_system_config(self) -> Dict[str, Any]:
        """Load system configuration"""
        default_config = {
            "auto_start_agents": [
                "meta_spawner",
                "planner",
                "executor",
                "designer",
                "specialist",
                "deployment",
                "output_handler",
            ],
            "enable_scheduler": True,
            "enable_sync_engine": True,
            "enable_web_interface": True,
            "enable_gateway": True,
            "web_interface_port": 5000,
            "log_level": "INFO",
            "max_concurrent_tasks": 10,
            "auto_backup_interval": 3600,   # 1 hour
            "health_check_interval": 300,    # 5 minutes
        }

        config_file = Path("data/system_config.json")
        if config_file.exists():
            try:
                with open(config_file, "r") as f:
                    user_config = json.load(f)
                    default_config.update(user_config)
            except Exception as e:
                print(f"⚠️  Failed to load config: {e}")

        return default_config

    # ------------------------------------------------------------------
    # Initialisation
    # ------------------------------------------------------------------

    async def initialize(self):
        """Initialise the system through EcosystemOrchestrator."""
        print("🚀 Initializing Agentic AI System v0.4.0 …")

        try:
            # 1. Ensure data directories
            self._ensure_directories()

            # 2. Initialise EcosystemOrchestrator (quant + organism + gateway + backend)
            await self._initialize_orchestrator()

            # 3. Load deer-flow agents from src.agents
            await self._initialize_agents()

            # 4. Start organism scheduler
            if self.config["enable_scheduler"] and self.organism:
                await self._start_scheduler()

            # 5. Start sync engine
            if self.config["enable_sync_engine"]:
                await self._start_sync_engine()

            # 6. Start gateway + web interface
            if self.config.get("enable_gateway") and self.gateway:
                self._start_gateway()

            if self.config["enable_web_interface"]:
                await self._start_web_interface()

            self.status = "running"
            print("✅ Agentic AI System initialized successfully!")

            # 7. Print status
            await self._print_system_status()

        except Exception as e:
            print(f"❌ System initialization failed: {e}")
            logger.exception("Initialization failure")
            self.status = "failed"
            raise

    # ---- Orchestrator ----

    async def _initialize_orchestrator(self):
        """Create the EcosystemOrchestrator — the single entry-point for
        all ecosystem modules (quant, organism, gateway, backend)."""
        print("🔧 Initializing EcosystemOrchestrator …")

        try:
            from src.integration import EcosystemOrchestrator

            data_dir = self.config.get("data_dir", "data")
            self.orchestrator = EcosystemOrchestrator(data_dir=data_dir)

            # Pull out adapter references for convenience
            self.bus = self.orchestrator.bus
            self.quant = self.orchestrator.quant
            self.organism = self.orchestrator.organism
            self.gateway = self.orchestrator.gateway
            self.backend = self.orchestrator.backend

            print("  ✅ EcosystemOrchestrator  (bus → quant → organism → gateway → backend)")

        except Exception as e:
            print(f"  ❌ EcosystemOrchestrator failed: {e}")
            logger.exception("Orchestrator init failed")
            # Fall back — try to at least get individual pieces
            await self._initialize_orchestrator_fallback()

    async def _initialize_orchestrator_fallback(self):
        """Fallback: try to load individual adapters when full orchestrator fails."""
        print("  ⚠️  Falling back to individual adapter initialization …")

        # Bus
        try:
            from src.integration import EcosystemBus
            self.bus = EcosystemBus()
            print("  ✅ EcosystemBus")
        except Exception as e:
            print(f"  ❌ EcosystemBus: {e}")

        # Quant
        try:
            from src.integration import QuantAdapter
            self.quant = QuantAdapter(bus=self.bus)
            print("  ✅ QuantAdapter")
        except Exception as e:
            print(f"  ❌ QuantAdapter: {e}")

        # Organism
        try:
            from src.integration import OrganismAdapter
            self.organism = OrganismAdapter(bus=self.bus)
            print("  ✅ OrganismAdapter")
        except Exception as e:
            print(f"  ❌ OrganismAdapter: {e}")

        # Gateway
        try:
            from src.integration import GatewayAdapter
            self.gateway = GatewayAdapter(bus=self.bus)
            self.gateway.setup_default_routes()
            self.gateway.setup_default_middleware()
            self.gateway.setup_default_localization()
            print("  ✅ GatewayAdapter")
        except Exception as e:
            print(f"  ❌ GatewayAdapter: {e}")

        # Backend
        try:
            from src.integration import BackendAdapter
            data_dir = self.config.get("data_dir", "data")
            self.backend = BackendAdapter(bus=self.bus, data_dir=data_dir)
            self.backend.register_default_skills()
            print("  ✅ BackendAdapter")
        except Exception as e:
            print(f"  ❌ BackendAdapter: {e}")

    # ---- Deer-flow agents ----

    async def _initialize_agents(self):
        """Load and register deer-flow agents from ``src.agents``."""
        print("🤖 Initializing deer-flow agents …")

        for agent_id, spec in DEER_FLOW_AGENTS.items():
            try:
                module = __import__(spec["module"], fromlist=[spec["class"]])
                cls = getattr(module, spec["class"])
                instance = cls()
                self.agents[agent_id] = instance

                if agent_id in self.config["auto_start_agents"]:
                    self.active_agents[agent_id] = instance

                print(f"  ✅ {spec['display']} ({agent_id})")

            except Exception as e:
                print(f"  ❌ {spec['display']} ({agent_id}): {e}")

        print(f"🤖 Initialized {len(self.agents)} agents, {len(self.active_agents)} active")

    # ---- Scheduler ----

    async def _start_scheduler(self):
        """Start the organism scheduler."""
        try:
            # OrganismAdapter already created the scheduler; just confirm it
            status = self.organism.scheduler.get_status()
            print(f"  ✅ Organism Scheduler ready — cycles: {list(status.get('cycles', {}).keys())}")
        except Exception as e:
            print(f"  ❌ Organism Scheduler: {e}")

    # ---- Sync engine ----

    async def _start_sync_engine(self):
        """Start the sync engine."""
        try:
            from src.integrations.langgraph_integration import LangGraphIntegration
            self.sync_engine = LangGraphIntegration()
            print("  ✅ Sync Engine (LangGraph)")
        except Exception as e:
            print(f"  ❌ Sync Engine: {e}")

    # ---- Gateway ----

    def _start_gateway(self):
        """Confirm the gateway adapter is wired (routes, middleware, i18n)."""
        try:
            routes = self.gateway.router.list_routes()
            print(f"  ✅ Gateway — {len(routes)} routes, middleware + i18n ready")
        except Exception as e:
            print(f"  ❌ Gateway: {e}")

    # ---- Web interface ----

    async def _start_web_interface(self):
        """Start the Flask web interface in a background process."""
        try:
            asyncio.create_task(self._run_web_interface())
            print(f"  ✅ Web Interface starting on port {self.config['web_interface_port']}")
        except Exception as e:
            print(f"  ❌ Web Interface: {e}")

    async def _run_web_interface(self) -> None:
        """Run the web interface server as a subprocess."""
        try:
            import subprocess
            self._web_process = subprocess.Popen(
                [
                    sys.executable, "-m", "flask", "--app", "web_interface.app",
                    "run",
                    "--host", "0.0.0.0",
                    "--port", str(self.config["web_interface_port"]),
                ],
            )
        except Exception as e:
            print(f"Web interface error: {e}")

    # ------------------------------------------------------------------
    # Directories
    # ------------------------------------------------------------------

    def _ensure_directories(self):
        """Ensure required directories exist."""
        directories = [
            "data", "data/backups", "data/logs", "data/cache",
            "projects", "ui/generated", "reports",
        ]
        for directory in directories:
            Path(directory).mkdir(parents=True, exist_ok=True)

    # ------------------------------------------------------------------
    # Status / display
    # ------------------------------------------------------------------

    async def _print_system_status(self):
        """Print current system status."""
        orch_status = {}
        if self.orchestrator:
            try:
                orch_status = self.orchestrator.get_system_status()
            except Exception:
                pass

        status_info = f"""
┌─ SYSTEM STATUS ─────────────────────────────────────────────────────────────┐
│ Status: {self.status.upper()}
│ Version: {self.version}
│ Started: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}
│
│ 🧠 Ecosystem Orchestrator: {'✅' if self.orchestrator else '❌'}
│   • Bus:       {'✅' if self.bus else '❌'}
│   • Quant:     {'✅' if self.quant else '❌'}
│   • Organism:  {'✅' if self.organism else '❌'}
│   • Gateway:   {'✅' if self.gateway else '❌'}
│   • Backend:   {'✅' if self.backend else '❌'}
│
│ 🤖 Active Agents: {len(self.active_agents)}
{self._format_agents_status()}
│
│ 🌐 Interfaces:
│   • Web UI: http://localhost:{self.config['web_interface_port']}
│   • API:    http://localhost:{self.config['web_interface_port']}/api
│
│ 🇮🇩 Made with ❤️ by Mulky Malikul Dhaher in Indonesia
└─────────────────────────────────────────────────────────────────────────────┘
        """
        print(status_info)

    def _format_agents_status(self) -> str:
        """Format agents status for display"""
        lines = []
        for agent_id, agent in self.active_agents.items():
            status = getattr(agent, 'status', 'unknown')
            name = getattr(agent, 'name', agent_id)
            lines.append(f"│   • {name}: {status}")
        return '\n'.join(lines) if lines else "│   • No active agents"

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    async def process_user_input(
        self,
        user_input: str,
        input_type: str = "text",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Process user input through the system.

        Routes through the agent_base coordinator if available,
        otherwise falls back to the first active agent.
        """
        # Prefer the AgentBase coordinator (it knows how to delegate)
        coordinator = self.agents.get("agent_base") or self.agents.get("executor")
        if coordinator and hasattr(coordinator, "process_task"):
            try:
                task = {
                    "task_id": f"user_{datetime.now().strftime('%Y%m%d%H%M%S')}",
                    "request": user_input,
                    "context": metadata or {},
                }
                result = coordinator.process_task(task)
                return {"success": True, "result": result}
            except Exception as e:
                return {"success": False, "error": str(e)}

        # Fallback: try any active agent
        for agent_id, agent in self.active_agents.items():
            if hasattr(agent, "process_task"):
                try:
                    task = {
                        "task_id": f"user_{datetime.now().strftime('%Y%m%d%H%M%S')}",
                        "request": user_input,
                        "context": metadata or {},
                    }
                    result = agent.process_task(task)
                    return {"success": True, "result": result}
                except Exception:
                    continue

        return {"success": False, "error": "No available agent to process input"}

    async def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status."""
        uptime = (datetime.now() - self.start_time).total_seconds()

        status: Dict[str, Any] = {
            "system_id": self.system_id,
            "version": self.version,
            "status": self.status,
            "uptime_seconds": uptime,
            "started_at": self.start_time.isoformat(),
            "ecosystem": {
                "orchestrator": self.orchestrator is not None,
                "bus": self.bus is not None,
                "quant": self.quant is not None,
                "organism": self.organism is not None,
                "gateway": self.gateway is not None,
                "backend": self.backend is not None,
            },
            "agents": {
                "total": len(self.agents),
                "active": len(self.active_agents),
                "list": list(self.active_agents.keys()),
            },
            "config": self.config,
        }

        # Add orchestrator-level details if available
        if self.orchestrator:
            try:
                status["ecosystem_details"] = self.orchestrator.get_system_status()
            except Exception:
                pass

        return status

    # ------------------------------------------------------------------
    # Interactive mode
    # ------------------------------------------------------------------

    async def run_interactive_mode(self) -> None:
        """Run in interactive mode — accepts text commands from stdin."""
        print("\n🎯 Entering interactive mode. Type 'help' for commands, 'exit' to quit.")

        while not self.shutdown_requested:
            try:
                user_input = input("\n🧠 Agentic AI > ").strip()

                if not user_input:
                    continue

                cmd = user_input.lower()

                if cmd in ("exit", "quit"):
                    break
                elif cmd == "help":
                    self._print_help()
                    continue
                elif cmd == "status":
                    status = await self.get_system_status()
                    print(json.dumps(status, indent=2, default=str))
                    continue
                elif cmd == "agents":
                    print(f"Active agents: {', '.join(self.active_agents.keys())}")
                    continue
                elif cmd == "orchestrator":
                    if self.orchestrator:
                        orch_status = self.orchestrator.get_system_status()
                        print(json.dumps(orch_status, indent=2, default=str))
                    else:
                        print("❌ Orchestrator not initialized")
                    continue
                elif cmd == "bus":
                    if self.bus:
                        print(f"Bus history: {len(self.bus._history)} messages")
                        for msg in self.bus._history[-5:]:
                            print(f"  [{msg.type.value}] {msg.source}: {msg.payload}")
                    else:
                        print("❌ Bus not initialized")
                    continue

                # Process as regular prompt
                print("🔄 Processing…")
                result = await self.process_user_input(user_input)

                if result.get("success"):
                    print("✅ Task completed successfully!")
                    if "result" in result:
                        print(f"📊 Result: {result['result']}")
                else:
                    print(f"❌ Error: {result.get('error', 'Unknown error')}")

            except KeyboardInterrupt:
                print("\n\n👋 Goodbye!")
                break
            except EOFError:
                break
            except Exception as e:
                print(f"❌ Unexpected error: {e}")

    def _print_help(self):
        """Print help information."""
        help_text = """
🆘 AGENTIC AI SYSTEM HELP

Commands:
  help              - Show this help
  status            - Show system status
  agents            - List active agents
  orchestrator      - Show EcosystemOrchestrator status
  bus               - Show recent bus messages
  exit/quit         - Exit the system

Natural Language Commands:
  "Create a web app called TaskManager"
  "Build a React component for user login"
  "Set up a FastAPI backend with authentication"
  "Generate a landing page for my startup"
  "Deploy my app to production"
  "Create an agent that monitors system health"

Ecosystem Modules (v0.4.0):
  🧠 EcosystemOrchestrator — top-level wiring
  📊 QuantAdapter — risk officer, kill switch, pressure engine, decisions
  🦠 OrganismAdapter — scheduler, immune, decision, memory
  🌐 GatewayAdapter — API routes, middleware, localization
  💾 BackendAdapter — conversation memory, persistence, skills

For detailed documentation: http://localhost:5000/docs
        """
        print(help_text)

    # ------------------------------------------------------------------
    # Shutdown
    # ------------------------------------------------------------------

    def _signal_handler(self, signum: int, frame) -> None:
        """Handle shutdown signals gracefully."""
        print(f"\n🛑 Received signal {signum}, initiating shutdown…")
        self.shutdown_requested = True

    async def shutdown(self) -> None:
        """Gracefully shutdown the system."""
        print("🛑 Shutting down Agentic AI System…")

        try:
            # Terminate web process
            if self._web_process and self._web_process.poll() is None:
                self._web_process.terminate()
                try:
                    self._web_process.wait(timeout=5)
                except Exception:
                    self._web_process.kill()
                print("  ✅ Web process terminated")

            # Organism scheduler cleanup
            if self.organism and hasattr(self.organism.scheduler, "stop"):
                try:
                    self.organism.scheduler.stop()
                except Exception:
                    pass
                print("  ✅ Organism scheduler stopped")

            # Backend memory cleanup
            if self.backend and hasattr(self.backend.memory, "summarize"):
                try:
                    self.backend.memory.summarize()
                except Exception:
                    pass
                print("  ✅ Backend memory summarized")

            # Save system state
            await self._save_system_state()

            self.status = "stopped"
            print("✅ System shutdown complete")

        except Exception as e:
            print(f"❌ Shutdown error: {e}")

    async def _save_system_state(self):
        """Save current system state."""
        try:
            state = {
                "shutdown_time": datetime.now().isoformat(),
                "uptime_seconds": (datetime.now() - self.start_time).total_seconds(),
                "active_agents": list(self.active_agents.keys()),
                "status": self.status,
                "version": self.version,
            }

            Path("data").mkdir(parents=True, exist_ok=True)
            with open("data/last_session.json", "w") as f:
                json.dump(state, f, indent=2)

        except Exception as e:
            print(f"Failed to save system state: {e}")


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

async def main():
    """Main entry point"""
    print_banner()

    # Create and initialise the system
    system = AgenticAISystem()

    try:
        await system.initialize()

        # Check command line arguments
        if len(sys.argv) > 1:
            command = " ".join(sys.argv[1:])
            print(f"🎯 Executing command: {command}")

            result = await system.process_user_input(command)

            if result.get("success"):
                print("✅ Command executed successfully!")
                if "result" in result:
                    print(json.dumps(result["result"], indent=2, default=str))
            else:
                print(f"❌ Command failed: {result.get('error')}")
        else:
            # Run in interactive mode
            await system.run_interactive_mode()

    except KeyboardInterrupt:
        print("\n👋 Goodbye!")

    except Exception as e:
        print(f"❌ System error: {e}")
        logger.exception("Fatal system error")

    finally:
        # Shutdown gracefully
        await system.shutdown()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 System interrupted")
    except Exception as e:
        print(f"❌ Fatal error: {e}")

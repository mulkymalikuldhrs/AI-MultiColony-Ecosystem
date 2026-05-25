#!/usr/bin/env python3
"""
AI-MultiColony-Ecosystem v8.1.0 - Unified Multi-Agent Colony Launcher
A multi-agent colony coordination platform for orchestrating specialized AI agents.

Features:
- Multi-agent colony coordination framework
- Agent registry and discovery system
- Unified web interface with FastAPI backend
- Integration with CAMEL AI, AutoGen, CrewAI, LangGraph
- Dynamic agent creation and management
- Shared memory bus for inter-agent communication
- Task scheduling and daemon management

Made with ❤️ by Mulky Malikul Dhaher in Indonesia 🇮🇩
For Education Purpose
"""

import argparse
import asyncio
import json
import logging
import os
import sys
import time
import threading
import subprocess
import importlib.util
import webbrowser
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional

# ASCII Art Banner
BANNER = """
============================================================
    AI-MULTICOLONY-ECOSYSTEM v8.1.0
    Multi-Agent Colony Coordination Platform
============================================================
    Made with ❤️ by Mulky Malikul Dhaher 🇮🇩
    For Education Purpose
============================================================
"""

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Add colony directory to path
sys.path.append(str(Path(__file__).parent))
sys.path.append(str(Path(__file__).parent / "colony"))


class EcosystemLauncher:
    """
    Unified Ecosystem Launcher v8.1.0
    Launcher for managing multi-agent colony ecosystem
    """

    def __init__(self):
        self.version = "8.1.0"
        self.status = "initializing"
        self.agents_count = 0

        # Initialize components
        self._initialize_components()

    def _initialize_components(self):
        """Initialize all core components"""
        try:
            # Import unified agent registry
            from colony.core.unified_agent_registry import (
                get_agent_by_name, list_all_agents, unified_registry, create_agent
            )
            from colony.core.system_bootstrap import bootstrap_systems

            self.get_agent_by_name = get_agent_by_name
            self.list_all_agents = list_all_agents
            self.unified_registry = unified_registry
            self.create_agent = create_agent
            self.bootstrap_systems = bootstrap_systems

            logger.info("Unified Agent Registry imported successfully.")

        except ImportError as e:
            logger.warning(f"Error importing unified registry: {e}")
            self._setup_fallback_functions()

        # Import additional components
        try:
            from colony.integrations.camel_ai_integration import CamelAIAgent, CamelAIColonyIntegration
            self.camel_ai_available = True
            logger.info("Camel AI integration available")
        except ImportError:
            self.camel_ai_available = False
            logger.info("Camel AI integration not available")

    def _setup_fallback_functions(self):
        """Setup fallback functions if imports fail"""
        def get_agent_by_name(name):
            return None
        def list_all_agents():
            return []
        def bootstrap_systems():
            pass
        def create_agent(name, config=None, instance_name=None):
            return None

        self.get_agent_by_name = get_agent_by_name
        self.list_all_agents = list_all_agents
        self.bootstrap_systems = bootstrap_systems
        self.create_agent = create_agent
        self.unified_registry = None

        logger.info("Fallback functions initialized")

    def print_banner(self):
        """Print system banner"""
        print(BANNER)
        print(f"System Version: v{self.version}")

        # List registered agents if available
        try:
            agents = self.list_all_agents()
            print(f"Registered Agents: {len(agents)}")
        except Exception:
            print("Registered Agents: 0 (registry not loaded)")

        print("=" * 60)

    def start_web_interface(self, host="0.0.0.0", port=8080):
        """Start unified web interface"""
        try:
            logger.info("Starting Web Interface...")

            # Change to web-interface directory
            web_dir = Path(__file__).parent / "web-interface"
            if web_dir.exists():
                os.chdir(web_dir)

                # Start Flask backend
                backend_thread = threading.Thread(
                    target=self._start_flask_backend,
                    args=(host, port),
                    daemon=True
                )
                backend_thread.start()

                # Wait for services to start
                time.sleep(3)

                url = f"http://localhost:{port}"
                print(f"Web Interface: {url}")
                return True
            else:
                logger.error("Web interface directory not found")
                return False

        except Exception as e:
            logger.error(f"Failed to start web interface: {e}")
            return False

    def _start_flask_backend(self, host="0.0.0.0", port=8080):
        """Start Flask backend server"""
        try:
            from web_interface.app import app
            app.run(host=host, port=port, debug=False, threaded=True)
        except ImportError:
            try:
                sys.path.append("web-interface")
                from app import app
                app.run(host=host, port=port, debug=False, threaded=True)
            except Exception as e:
                logger.error(f"Failed to start Flask backend: {e}")

    def start_ecosystem(self, mode="standard"):
        """Start the ecosystem"""
        self.print_banner()

        logger.info("Initializing AI MultiColony Ecosystem...")

        # Bootstrap core systems
        try:
            self.bootstrap_systems()
            logger.info("Core systems bootstrapped")
        except Exception as e:
            logger.warning(f"Bootstrap warning: {e}")

        # Update status
        self.status = "operational"
        logger.info("AI MultiColony Ecosystem is OPERATIONAL")

        return True

    def get_system_status(self):
        """Get system status"""
        agents = self.list_all_agents() if callable(self.list_all_agents) else []
        status = {
            "version": self.version,
            "status": self.status,
            "timestamp": datetime.now().isoformat(),
            "agents": {
                "registered": len(agents),
                "available": len(agents) if isinstance(agents, list) else 0
            },
        }
        return status

    def list_agents(self):
        """List all available agents"""
        try:
            agents = self.list_all_agents()
            print(f"\nAgent Registry v{self.version}")
            print(f"Total Agents: {len(agents)}")
            print("=" * 50)

            if agents:
                for i, agent in enumerate(agents, 1):
                    print(f"  {i}. {agent}")
            else:
                print("No agents currently registered. Configure agents in colony/ directory.")

        except Exception as e:
            logger.error(f"Error listing agents: {e}")


def main():
    """Main function for ecosystem launcher"""
    parser = argparse.ArgumentParser(
        description="AI-MultiColony-Ecosystem v8.1.0 Launcher",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Modes:
  --mode standard       Start standard ecosystem
  --mode web            Start with web interface

Examples:
  python main.py --start-all
  python main.py --web-ui
  python main.py --status
        """
    )

    # Core modes
    parser.add_argument("--mode", choices=["standard", "web"],
                       default="standard", help="System mode")
    parser.add_argument("--start-all", action="store_true", help="Start all components")
    parser.add_argument("--web-ui", action="store_true", help="Start web interface")

    # Status and monitoring
    parser.add_argument("--status", action="store_true", help="Show system status")
    parser.add_argument("--list-agents", action="store_true", help="List all agents")

    # Interface options
    parser.add_argument("--host", default="0.0.0.0", help="Web interface host")
    parser.add_argument("--port", type=int, default=8080, help="Web interface port")

    args = parser.parse_args()

    # Initialize launcher
    launcher = EcosystemLauncher()

    try:
        if args.status:
            status = launcher.get_system_status()
            print(f"\nSystem Status v{status['version']}")
            print("=" * 50)
            print(f"Version: {status['version']}")
            print(f"Status: {status['status']}")
            print(f"Timestamp: {status['timestamp']}")
            print(f"Agents: {status['agents']['registered']} registered")
            print("=" * 50)

        elif args.list_agents:
            launcher.list_agents()

        elif args.web_ui or args.start_all or args.mode == "web":
            launcher.start_ecosystem(mode=args.mode)
            launcher.start_web_interface(host=args.host, port=args.port)

            try:
                print("\nEcosystem running. Press Ctrl+C to stop.")
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                print("\nShutting down AI MultiColony Ecosystem...")

        else:
            # Default: start ecosystem
            launcher.start_ecosystem(mode=args.mode)

            try:
                print("\nEcosystem running. Press Ctrl+C to stop.")
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                print("\nShutting down AI MultiColony Ecosystem...")

    except Exception as e:
        logger.error(f"Error in main execution: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

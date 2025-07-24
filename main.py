# main.py - Unified Launcher for AI MultiColony Ecosystem
# Made with ❤️ by Mulky Malikul Dhaher in Indonesia 🇮🇩

import argparse
import importlib.util
import os
import subprocess
import sys
import threading
import time
from pathlib import Path

# Add colony directory to path
sys.path.append(str(Path(__file__).parent))

# Import core components
try:
    from colony.core.agent_registry import get_agent_by_name, list_all_agents
    from colony.core.system_bootstrap import bootstrap_systems
    print("Core components imported successfully.")
except ImportError as e:
    print(f"Error importing core components: {e}")
    # Attempt to add the project root to the path and retry, as this script might be run from a different CWD.
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    try:
        from colony.core.agent_registry import (get_agent_by_name,
                                                list_all_agents)
        from colony.core.system_bootstrap import bootstrap_systems
        print("Core components imported successfully after path correction.")
    except ImportError as e2:
        print(f"Failed to import core components even after path correction: {e2}")
        sys.exit(1)

# ANSI color codes for terminal output
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def print_banner():
    """Print the system banner"""
    banner = f"""
{Colors.BLUE}╔══════════════════════════════════════════════════════════════╗{Colors.ENDC}
{Colors.BLUE}║                {Colors.YELLOW}🚀 AI-MultiColony-Ecosystem v7.2.0{Colors.BLUE}            ║{Colors.ENDC}
{Colors.BLUE}║                     {Colors.GREEN}Unified Launcher System{Colors.BLUE}                  ║{Colors.ENDC}
{Colors.BLUE}║          {Colors.YELLOW}🇮🇩 Made with ❤️ by Mulky Malikul Dhaher 🇮🇩{Colors.BLUE}        ║{Colors.ENDC}
{Colors.BLUE}╚══════════════════════════════════════════════════════════════╝{Colors.ENDC}
"""
    print(banner)

def print_menu():
    """Print the launcher mode selection menu"""
    menu = f"""
{Colors.GREEN}🎯 Available Launcher Modes:{Colors.ENDC}
{Colors.BLUE}1. {Colors.YELLOW}🌐 Web UI Only{Colors.ENDC} - Modern web interface (RECOMMENDED)
{Colors.BLUE}2. {Colors.YELLOW}🔄 Web UI + Background{Colors.ENDC} - Web interface with autonomous engines  
{Colors.BLUE}3. {Colors.YELLOW}🖥️ CLI Mode{Colors.ENDC} - Interactive command line interface
{Colors.BLUE}4. {Colors.YELLOW}📱 Termux Shell{Colors.ENDC} - Compatible with Android Termux
{Colors.BLUE}5. {Colors.YELLOW}❌ Exit{Colors.ENDC} - Shutdown launcher
"""
    print(menu)
    return input(f"{Colors.GREEN}🎯 Select mode (1-5): {Colors.ENDC}")

def run_web_ui(with_background=False):
    """Run the web UI interface"""
    print(f"{Colors.GREEN}🌐 Starting Web UI...{Colors.ENDC}")
    
    # Create necessary directories if they don't exist
    os.makedirs("logs", exist_ok=True)
    os.makedirs("data", exist_ok=True)
    os.makedirs("agent_output", exist_ok=True)
    
    # Set environment variables (only if not already set)
    if "WEB_INTERFACE_PORT" not in os.environ:
        os.environ["WEB_INTERFACE_PORT"] = "8080"
    if "WEB_INTERFACE_HOST" not in os.environ:
        os.environ["WEB_INTERFACE_HOST"] = "0.0.0.0"
    
    # Bootstrap the system
    try:
        bootstrap_systems()
        print(f"{Colors.GREEN}✅ System bootstrapped successfully{Colors.ENDC}")
    except Exception as e:
        print(f"{Colors.RED}❌ Error bootstrapping system: {e}{Colors.ENDC}")
    
    # Start background processes if requested
    if with_background:
        print(f"{Colors.YELLOW}🔄 Starting background processes...{Colors.ENDC}")
        try:
            # Start autonomous engines in background threads
            threading.Thread(target=start_autonomous_engines, daemon=True).start()
            print(f"{Colors.GREEN}✅ Background processes started{Colors.ENDC}")
        except Exception as e:
            print(f"{Colors.RED}❌ Error starting background processes: {e}{Colors.ENDC}")
    
    # Start the web UI
    try:
        port = int(os.getenv('WEB_INTERFACE_PORT', 8080))
        host = os.getenv('WEB_INTERFACE_HOST', '0.0.0.0')
        
        print(f"{Colors.GREEN}🌐 Web UI will be available at:{Colors.ENDC}")
        print(f"{Colors.YELLOW}   http://localhost:{port}{Colors.ENDC}")
        print(f"{Colors.YELLOW}   http://YOUR_IP:{port}{Colors.ENDC}")
        
        # Import and run the Flask app
        from colony.api.app import app, socketio
        socketio.run(app, host=host, port=port, debug=False, allow_unsafe_werkzeug=True)
    except Exception as e:
        print(f"{Colors.RED}❌ Error starting web UI: {e}{Colors.ENDC}")
        print(f"{Colors.YELLOW}⚠️ Attempting to start web UI with subprocess...{Colors.ENDC}")
        try:
            subprocess.run([sys.executable, "-m", "colony.api.app"], check=True)
        except Exception as sub_e:
            print(f"{Colors.RED}❌ Failed to start web UI with subprocess: {sub_e}{Colors.ENDC}")

def start_autonomous_engines():
    """Start the autonomous engines in the background"""
    print(f"{Colors.YELLOW}🔄 Starting autonomous engines...{Colors.ENDC}")
    
    # List of engines to start
    engines = [
        "AUTONOMOUS_DEVELOPMENT_ENGINE",
        "AUTONOMOUS_EXECUTION_ENGINE",
        "AUTONOMOUS_IMPROVEMENT_ENGINE",
        "CONTINUOUS_IMPROVEMENT_CYCLE"
    ]
    
    for engine in engines:
        try:
            # Try to import and start each engine
            module_path = f"colony.core.{engine}"
            if importlib.util.find_spec(module_path):
                module = importlib.import_module(module_path)
                if hasattr(module, "start_engine"):
                    threading.Thread(target=module.start_engine, daemon=True).start()
                    print(f"{Colors.GREEN}✅ Started {engine}{Colors.ENDC}")
                else:
                    print(f"{Colors.YELLOW}⚠️ {engine} has no start_engine function{Colors.ENDC}")
            else:
                print(f"{Colors.YELLOW}⚠️ {engine} module not found{Colors.ENDC}")
        except Exception as e:
            print(f"{Colors.RED}❌ Error starting {engine}: {e}{Colors.ENDC}")

def run_cli_mode():
    """Run the interactive CLI mode"""
    print(f"{Colors.GREEN}🖥️ Starting CLI Mode...{Colors.ENDC}")
    
    # Bootstrap the system
    try:
        bootstrap_systems()
        print(f"{Colors.GREEN}✅ System bootstrapped successfully{Colors.ENDC}")
    except Exception as e:
        print(f"{Colors.RED}❌ Error bootstrapping system: {e}{Colors.ENDC}")
    
    # Start CLI loop
    print(f"{Colors.GREEN}🖥️ CLI Mode ready. Type 'help' for available commands.{Colors.ENDC}")
    while True:
        try:
            command = input(f"{Colors.BLUE}colony> {Colors.ENDC}")
            if command.lower() == "exit":
                print(f"{Colors.YELLOW}👋 Exiting CLI Mode...{Colors.ENDC}")
                break
            elif command.lower() == "help":
                print_cli_help()
            elif command.lower() == "status":
                print_system_status()
            elif command.lower() == "agents":
                list_available_agents()
            elif command.lower() == "logs":
                show_recent_logs()
            elif command.lower() == "web":
                print(f"{Colors.YELLOW}🌐 Starting Web UI in background...{Colors.ENDC}")
                threading.Thread(target=run_web_ui, daemon=True).start()
                print(f"{Colors.GREEN}✅ Web UI started at http://localhost:8080{Colors.ENDC}")
            elif command.lower().startswith("run "):
                agent_name = command.split(" ")[1]
                run_specific_agent(agent_name)
            else:
                print(f"{Colors.RED}❌ Unknown command. Type 'help' for available commands.{Colors.ENDC}")
        except KeyboardInterrupt:
            print(f"\n{Colors.YELLOW}👋 Exiting CLI Mode...{Colors.ENDC}")
            break
        except Exception as e:
            print(f"{Colors.RED}❌ Error: {e}{Colors.ENDC}")

def print_cli_help():
    """Print available CLI commands"""
    help_text = f"""
{Colors.GREEN}📋 Available Commands:{Colors.ENDC}
{Colors.BLUE}help{Colors.ENDC}      - Show this help message
{Colors.BLUE}status{Colors.ENDC}    - Show system status
{Colors.BLUE}agents{Colors.ENDC}    - List all available agents
{Colors.BLUE}logs{Colors.ENDC}      - Show recent system logs
{Colors.BLUE}web{Colors.ENDC}       - Start web UI in background
{Colors.BLUE}run <agent>{Colors.ENDC} - Run a specific agent
{Colors.BLUE}exit{Colors.ENDC}      - Exit CLI mode
"""
    print(help_text)

def print_system_status():
    """Print current system status"""
    print(f"{Colors.GREEN}📊 System Status:{Colors.ENDC}")
    print(f"{Colors.BLUE}Version:{Colors.ENDC} 7.2.0")
    print(f"{Colors.BLUE}Status:{Colors.ENDC} Running")
    
    # Count agents
    try:
        agent_count = len(list_all_agents())
        print(f"{Colors.BLUE}Agents:{Colors.ENDC} {agent_count} registered")
    except Exception:
        print(f"{Colors.BLUE}Agents:{Colors.ENDC} Unknown")
    
    # Check log file
    log_file = "logs/colony_activity.log"
    if os.path.exists(log_file):
        log_size = os.path.getsize(log_file) / 1024  # KB
        print(f"{Colors.BLUE}Log Size:{Colors.ENDC} {log_size:.2f} KB")
    else:
        print(f"{Colors.BLUE}Log Size:{Colors.ENDC} No log file found")

def list_available_agents():
    """List all available agents"""
    print(f"{Colors.GREEN}🤖 Available Agents:{Colors.ENDC}")
    try:
        agents = list_all_agents()
        if not agents:
            print(f"{Colors.YELLOW}⚠️ No agents found{Colors.ENDC}")
            return
        
        for i, agent_name in enumerate(agents, 1):
            print(f"{Colors.BLUE}{i}. {agent_name}{Colors.ENDC}")
    except Exception as e:
        print(f"{Colors.RED}❌ Error listing agents: {e}{Colors.ENDC}")

def show_recent_logs():
    """Show recent system logs"""
    log_file = "logs/colony_activity.log"
    print(f"{Colors.GREEN}📄 Recent Logs:{Colors.ENDC}")
    
    if not os.path.exists(log_file):
        print(f"{Colors.YELLOW}⚠️ No log file found at {log_file}{Colors.ENDC}")
        return
    
    try:
        # Show last 10 lines of log file
        with open(log_file, "r") as f:
            lines = f.readlines()
            for line in lines[-10:]:
                print(line.strip())
    except Exception as e:
        print(f"{Colors.RED}❌ Error reading log file: {e}{Colors.ENDC}")

def run_specific_agent(agent_name):
    """Run a specific agent"""
    print(f"{Colors.GREEN}🤖 Running agent: {agent_name}{Colors.ENDC}")
    try:
        agent_cls = get_agent_by_name(agent_name)
        if agent_cls:
            # Pass a default config and no memory manager for now
            agent = agent_cls(name=agent_name, config={}, memory_manager=None)
            agent.run()
            print(f"{Colors.GREEN}✅ Agent {agent_name} completed{Colors.ENDC}")
        else:
            print(f"{Colors.RED}❌ Agent '{agent_name}' not found in registry.{Colors.ENDC}")
    except Exception as e:
        print(f"{Colors.RED}❌ Error running agent {agent_name}: {e}{Colors.ENDC}")

def run_termux_mode():
    """Run the Termux-compatible mode"""
    print(f"{Colors.GREEN}📱 Starting Termux Mode...{Colors.ENDC}")
    print(f"{Colors.YELLOW}⚠️ Termux mode is optimized for Android environment{Colors.ENDC}")
    
    # Similar to CLI mode but with Termux-specific adjustments
    run_cli_mode()

def main():
    """Main entry point for the unified launcher"""
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="AI MultiColony Ecosystem - Unified Launcher")
    parser.add_argument("--agent", help="Run a specific agent")
    parser.add_argument("--all", action="store_true", help="Run all agents")
    parser.add_argument("--monitor", action="store_true", help="Enable monitoring")
    parser.add_argument("--web-ui", action="store_true", help="Launch web UI")
    parser.add_argument("--mode", type=int, choices=[1, 2, 3, 4, 5], help="Launch mode (1-5)")
    args = parser.parse_args()
    
    # Print banner
    print_banner()
    
    # Handle direct command line arguments
    if args.agent:
        run_specific_agent(args.agent)
        return
    elif args.all:
        print(f"{Colors.GREEN}🤖 Running all agents...{Colors.ENDC}")
        try:
            for agent_name in list_all_agents():
                agent_cls = get_agent_by_name(agent_name)
                agent = agent_cls()
                agent.run()
            print(f"{Colors.GREEN}✅ All agents completed{Colors.ENDC}")
        except Exception as e:
            print(f"{Colors.RED}❌ Error running all agents: {e}{Colors.ENDC}")
        return
    elif args.web_ui:
        run_web_ui(with_background=args.monitor)
        return
    elif args.monitor:
        print(f"{Colors.GREEN}📊 Starting monitoring...{Colors.ENDC}")
        # Start monitoring in a separate thread
        threading.Thread(target=start_autonomous_engines, daemon=True).start()
        print(f"{Colors.GREEN}✅ Monitoring started{Colors.ENDC}")
        return
    
    # If mode is specified via command line, use it
    if args.mode:
        mode = args.mode
    else:
        # Otherwise show interactive menu
        mode_input = print_menu()
        try:
            mode = int(mode_input)
        except ValueError:
            print(f"{Colors.RED}❌ Invalid input. Please enter a number between 1 and 5.{Colors.ENDC}")
            return
    
    # Process selected mode
    if mode == 1:
        run_web_ui(with_background=False)
    elif mode == 2:
        run_web_ui(with_background=True)
    elif mode == 3:
        run_cli_mode()
    elif mode == 4:
        run_termux_mode()
    elif mode == 5:
        print(f"{Colors.YELLOW}👋 Exiting launcher...{Colors.ENDC}")
    else:
        print(f"{Colors.RED}❌ Invalid mode. Please select a number between 1 and 5.{Colors.ENDC}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}👋 Exiting launcher...{Colors.ENDC}")
    except Exception as e:
        print(f"{Colors.RED}❌ Unhandled error: {e}{Colors.ENDC}")
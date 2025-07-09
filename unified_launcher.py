import argparse
import asyncio
import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.append(str(project_root))

def print_header(text: str):
    """Print colored header"""
    print(f"\n\033[95m\033[1m🧠 {text}\033[0m")
    print(f"\033[96m{'=' * (len(text) + 3)}\033[0m")

def print_success(text: str):
    """Print success message"""
    print(f"\033[92m✅ {text}\033[0m")

def print_error(text: str):
    """Print error message"""
    print(f"\033[91m❌ {text}\033[0m")

def print_info(text: str):
    """Print info message"""
    print(f"\033[94mℹ️  {text}\033[0m")

async def run_web_interface():
    """Run the web interface"""
    print_header("Starting Web Interface")
    try:
        from web_interface.app import socketio, app
        port = int(os.getenv('WEB_INTERFACE_PORT', 5000))
        host = os.getenv('WEB_INTERFACE_HOST', '0.0.0.0')
        print_info(f"Dashboard will be available at: http://localhost:{port}")
        socketio.run(app, host=host, port=port, debug=False, allow_unsafe_werkzeug=True)
    except ImportError as e:
        print_error(f"Web interface modules not found: {e}")
        sys.exit(1)
    except Exception as e:
        print_error(f"Failed to start web interface: {e}")
        sys.exit(1)

async def run_cli_interface():
    """Run the CLI interface (placeholder for now, will integrate cli.py logic)"""
    print_header("Starting CLI Interface")
    print_info("CLI mode selected. All CLI commands will be integrated here.")
    # In a real scenario, you would integrate the click commands from cli.py here
    # For now, we'll just print a message and exit or run a basic loop
    print_info("This is a placeholder for the integrated CLI functionality.")
    print_info("Please run specific commands using 'python unified_launcher.py --mode cli <command>'")
    # Example:
    # from cli import cli as original_cli
    # original_cli() # This would run the click CLI directly
    sys.exit(0) # Exit after showing message for now

async def run_headless_mode():
    """Run the system in headless mode"""
    print_header("Starting Headless Mode")
    print_info("Headless mode selected. Running core engine...")
    try:
        # Assuming core.engine_core exists or will be created
        # from core.engine_core import start_engine
        # await start_engine()
        print_success("Core engine started in headless mode (placeholder).")
        # Keep the event loop running for background tasks
        while True:
            await asyncio.sleep(3600) # Sleep for an hour, or until interrupted
    except ImportError as e:
        print_error(f"Core engine module not found: {e}")
        sys.exit(1)
    except Exception as e:
        print_error(f"Failed to start headless mode: {e}")
        sys.exit(1)

async def run_termux_mode():
    """Run the system in Termux mode (similar to headless but optimized for mobile)"""
    print_header("Starting Termux Mode")
    print_info("Termux mode selected. Running optimized core engine for mobile...")
    try:
        # from core.engine_core import start_engine_termux_optimized
        # await start_engine_termux_optimized()
        print_success("Core engine started in Termux mode (placeholder).")
        while True:
            await asyncio.sleep(3600) # Sleep for an hour, or until interrupted
    except ImportError as e:
        print_error(f"Termux optimized engine module not found: {e}")
        sys.exit(1)
    except Exception as e:
        print_error(f"Failed to start Termux mode: {e}")
        sys.exit(1)

async def main():
    parser = argparse.ArgumentParser(description="🚀 AI-MultiColony-Ecosystem Unified Launcher")
    parser.add_argument('--mode', type=str, default='web', 
                        choices=['web', 'cli', 'headless', 'termux'],
                        help='Mode to run the system in (web, cli, headless, termux)')
    
    args = parser.parse_args()

    print("🚀 AI-MultiColony-Ecosystem v7.0.0")
    print("🇮🇩 Made with ❤️ by Mulky Malikul Dhaher")
    print("📂 Starting Unified Launcher System...")
    print("="*60)

    if args.mode == 'web':
        await run_web_interface()
    elif args.mode == 'cli':
        await run_cli_interface()
    elif args.mode == 'headless':
        await run_headless_mode()
    elif args.mode == 'termux':
        await run_termux_mode()
    else:
        print_error(f"Invalid mode: {args.mode}")
        sys.exit(1)

if __name__ == "__main__":
    # Ensure LLM7 public endpoint and key are always set for all agents
    os.environ["LLM7_API_KEY"] = "unused"
    os.environ["LLM7_API_BASE_URL"] = "https://api.llm7.io/v1"
    os.environ["OPENAI_API_KEY"] = "unused"
    os.environ["OPENAI_API_BASE_URL"] = "https://api.llm7.io/v1"
    asyncio.run(main())
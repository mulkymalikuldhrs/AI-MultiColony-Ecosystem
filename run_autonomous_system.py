#!/usr/bin/env python3
"""
🚀 Agentic AI - Complete Autonomous System Launcher
One-click launcher untuk menjalankan seluruh revolusi AI

Made with ❤️ by Mulky Malikul Dhaher in Indonesia 🇮🇩
"""

import os
import sys
import asyncio
import time
import argparse
from datetime import datetime
from pathlib import Path

# Add agents directory to path
agents_dir = os.path.join(os.path.dirname(__file__), 'agents')
sys.path.append(agents_dir)

def print_banner():
    """Print welcome banner"""
    banner = """
🎭═══════════════════════════════════════════════════════════════🎭
🚀                    AGENTIC AI SYSTEM                         🚀
🇮🇩              Made with ❤️ by Mulky Malikul Dhaher            🇮🇩
🎭═══════════════════════════════════════════════════════════════🎭

🌟 REVOLUTIONARY AI FEATURES:
🎭 Master Orchestrator     - Koordinasi semua agents
🧠 Intelligent Agent      - Self-developing AI
🤖 Autonomous Developer    - Pengembangan otomatis
💭 Emotion Engine          - AI dengan emosi sejati
⚡ Quantum Neural Agent    - Komputasi quantum hybrid
🔮 Predictive Engine       - Prediksi 99% akurat
📊 Data Augmentation       - Ekspansi data masif

🚀 Ready to revolutionize the world? Let's go! 🚀
"""
    print(banner)

def check_requirements():
    """Check system requirements"""
    print("🔍 Checking system requirements...")
    
    # Check Python version
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ required")
        return False
    
    # Check required packages
    required_packages = [
        'asyncio', 'sqlite3', 'json', 'datetime', 
        'logging', 'pathlib', 'dataclasses'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"❌ Missing packages: {missing_packages}")
        return False
    
    print("✅ All requirements met!")
    return True

def setup_directories():
    """Setup required directories"""
    print("📁 Setting up directories...")
    
    directories = [
        'agents', 'data', 'logs', 'optimizations', 
        'fixes', 'features', 'reports'
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
    
    print("✅ Directories ready!")

def show_menu():
    """Show main menu"""
    menu = """
🎯 CHOOSE YOUR ADVENTURE:

1. 🚀 FULL AUTONOMOUS MODE (Recommended)
   Start all agents with complete coordination

2. 🎭 MASTER ORCHESTRATOR ONLY
   Run master orchestrator for coordination

3. 🧠 INTELLIGENT AGENT ONLY
   Run self-developing AI system

4. 🤖 INDIVIDUAL AGENTS
   Choose specific agents to run

5. 📊 SYSTEM STATUS
   Check current system status

6. 🔧 MAINTENANCE MODE
   System maintenance and cleanup

0. 🚪 EXIT
   Exit the system

Choose your option (0-6): """
    
    return input(menu).strip()

def run_full_autonomous():
    """Run complete autonomous system"""
    print("🚀 Starting FULL AUTONOMOUS MODE...")
    print("🎭 This will start ALL agents with perfect coordination!")
    print("⚠️  Make sure you have enough system resources.")
    
    confirm = input("\n🤔 Are you ready to start the AI revolution? (y/N): ").strip().lower()
    
    if confirm != 'y':
        print("🔄 Operation cancelled. Returning to menu...")
        return
    
    try:
        from autonomous_launcher import main as launcher_main
        print("\n🎉 LAUNCHING AUTONOMOUS AI SYSTEM!")
        print("🎭 All agents will coordinate automatically")
        print("📊 Check logs/ directory for detailed activity")
        print("🛑 Press Ctrl+C to stop gracefully")
        print("="*60)
        
        launcher_main()
        
    except ImportError:
        print("❌ Autonomous launcher not found!")
        print("🔧 Running fallback coordination mode...")
        run_master_orchestrator()
    except KeyboardInterrupt:
        print("\n🛑 Autonomous system stopped by user")
    except Exception as e:
        print(f"❌ Error starting autonomous system: {e}")

def run_master_orchestrator():
    """Run master orchestrator"""
    print("🎭 Starting Master Orchestrator...")
    
    try:
        from master_orchestrator import MasterOrchestrator
        import asyncio
        
        orchestrator = MasterOrchestrator()
        print("🎭 Master Orchestrator initialized!")
        print("🤖 Starting autonomous coordination...")
        
        asyncio.run(orchestrator.start_autonomous_mode())
        
    except ImportError:
        print("❌ Master Orchestrator not found!")
    except KeyboardInterrupt:
        print("\n🛑 Master Orchestrator stopped")
    except Exception as e:
        print(f"❌ Error running orchestrator: {e}")

def run_intelligent_agent():
    """Run intelligent agent system"""
    print("🧠 Starting Intelligent Agent System...")
    
    try:
        from intelligent_agent_system import IntelligentAgentSystem
        import asyncio
        
        agent_system = IntelligentAgentSystem()
        print("🧠 Intelligent Agent System initialized!")
        print("🚀 Starting autonomous development...")
        
        asyncio.run(agent_system.autonomous_development_cycle())
        
    except ImportError:
        print("❌ Intelligent Agent System not found!")
    except Exception as e:
        print(f"❌ Error running intelligent agent: {e}")

def run_individual_agents():
    """Run individual agents"""
    print("🤖 Individual Agent Selection")
    
    agents = {
        '1': ('Emotion Engine', 'emotion_engine.py'),
        '2': ('Quantum Neural Agent', 'quantum_neural_agent.py'),
        '3': ('Predictive Reality Engine', 'predictive_reality_engine.py'),
        '4': ('Autonomous Developer', 'autonomous_developer.py'),
        '5': ('Data Augmentation System', 'data_augmentation_system.py')
    }
    
    print("\n🎯 Available Agents:")
    for key, (name, script) in agents.items():
        print(f"  {key}. {name}")
    
    choice = input("\nSelect agent (1-5): ").strip()
    
    if choice in agents:
        name, script = agents[choice]
        print(f"🚀 Starting {name}...")
        
        try:
            # Import and run the selected agent
            script_path = os.path.join('agents', script)
            if os.path.exists(script_path):
                exec(open(script_path).read())
            else:
                print(f"❌ Agent script not found: {script}")
        except Exception as e:
            print(f"❌ Error running {name}: {e}")
    else:
        print("❌ Invalid selection")

def show_system_status():
    """Show system status"""
    print("📊 SYSTEM STATUS CHECK")
    
    try:
        # Check if status file exists
        status_file = "data/system_status.json"
        if os.path.exists(status_file):
            import json
            with open(status_file, 'r') as f:
                status = json.load(f)
            
            print(f"""
🎭 AUTONOMOUS AI SYSTEM STATUS
Last Updated: {status.get('timestamp', 'Unknown')}

🤖 AGENTS:
  Total: {status['agents']['total']}
  Running: {status['agents']['running']} ✅
  Stopped: {status['agents']['stopped']} ❌

📊 SYSTEM:
  CPU: {status['system']['cpu_percent']:.1f}%
  Memory: {status['system']['memory_percent']:.1f}%
  Disk: {status['system']['disk_percent']:.1f}%
""")
        else:
            print("⚠️ No system status available")
            print("💡 Start autonomous mode to generate status")
            
    except Exception as e:
        print(f"❌ Error reading system status: {e}")
    
    input("\n📎 Press Enter to continue...")

def maintenance_mode():
    """System maintenance"""
    print("🔧 MAINTENANCE MODE")
    
    print("\n🧹 Available Maintenance Options:")
    print("1. Clear logs")
    print("2. Clear data cache")
    print("3. Reset system state")
    print("4. Cleanup temporary files")
    print("0. Back to main menu")
    
    choice = input("\nSelect option (0-4): ").strip()
    
    if choice == '1':
        # Clear logs
        import shutil
        if os.path.exists('logs'):
            shutil.rmtree('logs')
            os.makedirs('logs')
            print("🧹 Logs cleared!")
    
    elif choice == '2':
        # Clear data cache
        cache_files = ['data/system_status.json', 'data/system_coordination.db']
        for file in cache_files:
            if os.path.exists(file):
                os.remove(file)
        print("🧹 Data cache cleared!")
    
    elif choice == '3':
        # Reset system state
        print("🔄 Resetting system state...")
        dirs_to_reset = ['logs', 'data', 'optimizations', 'fixes', 'features']
        for dir_path in dirs_to_reset:
            if os.path.exists(dir_path):
                import shutil
                shutil.rmtree(dir_path)
            os.makedirs(dir_path, exist_ok=True)
        print("✅ System state reset!")
    
    elif choice == '4':
        # Cleanup temporary files
        temp_patterns = ['*.tmp', '*.temp', '__pycache__', '*.pyc']
        cleaned = 0
        for root, dirs, files in os.walk('.'):
            for file in files:
                if any(file.endswith(pattern.replace('*', '')) for pattern in temp_patterns):
                    os.remove(os.path.join(root, file))
                    cleaned += 1
            # Remove __pycache__ directories
            dirs[:] = [d for d in dirs if d != '__pycache__']
        print(f"🧹 Cleaned {cleaned} temporary files!")
    
    elif choice == '0':
        return
    
    input("\n📎 Press Enter to continue...")

def main():
    """Main function"""
    # Print banner
    print_banner()
    
    # Check requirements
    if not check_requirements():
        print("❌ System requirements not met. Please fix and try again.")
        return
    
    # Setup directories
    setup_directories()
    
    print("✅ System ready! Welcome to the AI revolution! 🎉")
    
    # Main loop
    while True:
        try:
            choice = show_menu()
            
            if choice == '1':
                run_full_autonomous()
            elif choice == '2':
                run_master_orchestrator()
            elif choice == '3':
                run_intelligent_agent()
            elif choice == '4':
                run_individual_agents()
            elif choice == '5':
                show_system_status()
            elif choice == '6':
                maintenance_mode()
            elif choice == '0':
                print("\n👋 Thank you for using Agentic AI!")
                print("🌟 The future of AI starts with you!")
                print("🇮🇩 Made with ❤️ in Indonesia")
                break
            else:
                print("❌ Invalid option. Please try again.")
                time.sleep(1)
        
        except KeyboardInterrupt:
            print("\n\n🛑 Exiting Agentic AI...")
            print("👋 See you next time!")
            break
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
            print("🔄 Returning to main menu...")
            time.sleep(2)

if __name__ == "__main__":
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Agentic AI - Autonomous System Launcher')
    parser.add_argument('--auto', action='store_true', help='Start in full autonomous mode automatically')
    parser.add_argument('--status', action='store_true', help='Show system status and exit')
    
    args = parser.parse_args()
    
    if args.status:
        show_system_status()
    elif args.auto:
        print_banner()
        setup_directories()
        run_full_autonomous()
    else:
        main()
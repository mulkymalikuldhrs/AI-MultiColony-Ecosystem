# 🚀 AI-MultiColony-Ecosystem Unified Launcher

## Overview

The Unified Launcher is a central entry point for the AI-MultiColony-Ecosystem, providing a seamless way to access all system components through a single interface. It connects all agents, core components, and the web UI into a cohesive system.

## Features

- 🌐 **Web UI Interface**: Modern web-based control panel for managing the entire ecosystem
- 🖥️ **CLI Mode**: Interactive command-line interface for direct system control
- 📱 **Termux Compatibility**: Special mode optimized for Android Termux environment
- 🔄 **Background Processing**: Run autonomous engines in the background
- 🤖 **Agent Management**: Run specific agents or all agents with simple commands

## Usage

### Basic Usage

```bash
# Launch with interactive menu
python main.py

# Launch web UI directly
python main.py --web-ui

# Launch web UI with background processing
python main.py --web-ui --monitor

# Run a specific agent
python main.py --agent agent_name

# Run all agents
python main.py --all

# Enable monitoring only
python main.py --monitor

# Launch specific mode directly
python main.py --mode 1  # Web UI Only
python main.py --mode 2  # Web UI + Background
python main.py --mode 3  # CLI Mode
python main.py --mode 4  # Termux Shell
python main.py --mode 5  # Exit
```

### Web UI Mode

The Web UI provides a modern interface for managing the entire ecosystem. It includes:

- Dashboard with system metrics
- Agent management interface
- Task submission and monitoring
- System configuration
- Interactive terminal
- Visualization tools

### CLI Mode

The CLI mode provides an interactive command-line interface with the following commands:

- `help`: Show available commands
- `status`: Show system status
- `agents`: List all available agents
- `logs`: Show recent system logs
- `web`: Start web UI in background
- `run <agent>`: Run a specific agent
- `exit`: Exit CLI mode

## Architecture

The Unified Launcher connects all system components:

1. **Core Components**:
   - Agent Registry
   - Memory Manager
   - System Bootstrap
   - Scheduler
   - Memory Bus

2. **Agent System**:
   - All registered agents
   - Agent communication channels
   - Task delegation system

3. **Web Interface**:
   - Modern web UI
   - API endpoints
   - Real-time updates via WebSockets

4. **Autonomous Engines**:
   - Continuous improvement cycle
   - Autonomous development engine
   - Autonomous execution engine
   - Autonomous improvement engine

## Implementation Details

The Unified Launcher is implemented in `main.py` with a symbolic link to `unified_launcher.py` for backward compatibility. It uses a modular architecture that allows for easy extension and customization.

Key implementation features:

- Colorful terminal output for better user experience
- Error handling and graceful degradation
- Dynamic component discovery and loading
- Asynchronous processing for background tasks
- Comprehensive logging system

## Future Enhancements

- Docker containerization for easy deployment
- Cloud deployment options
- Mobile app integration
- Enhanced security features
- Plugin system for third-party extensions

## Made with ❤️ by Mulky Malikul Dhaher in Indonesia 🇮🇩
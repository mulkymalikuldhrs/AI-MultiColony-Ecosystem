#!/usr/bin/env python3
"""
🚀 Autonomous Agent Colony - Main Launcher
Entry point for the entire system
"""

import asyncio
import sys
import os
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Import all main components
from src.main_controller import AutonomousColonyController
from src.utils.logger import setup_logger
from src.utils.config_manager import ConfigManager

async def main():
    """Main entry point for Autonomous Agent Colony"""
    try:
        print("""
🐫 Autonomous Agent Colony System Starting...
=============================================
        """)
        
        # Setup logging
        logger = setup_logger()
        logger.info("Starting Autonomous Agent Colony System")
        
        # Load configuration
        config_manager = ConfigManager()
        config = config_manager.load_config()
        
        # Initialize main controller
        controller = AutonomousColonyController(config)
        
        # Start the system
        await controller.start()
        
        print("✅ System started successfully!")
        print("🌐 Web interface: http://localhost:8000")
        print("📚 API docs: http://localhost:8000/docs")
        print("🔧 Admin panel: http://localhost:8000/admin")
        
        # Keep running
        await controller.run_forever()
        
    except KeyboardInterrupt:
        print("\n🛑 Shutting down gracefully...")
        await controller.shutdown()
    except Exception as e:
        print(f"❌ Error starting system: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())

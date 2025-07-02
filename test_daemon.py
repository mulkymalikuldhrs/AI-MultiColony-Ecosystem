#!/usr/bin/env python3
"""
🛡️ Test daemon functionality without forking
"""

import sys
import os
from pathlib import Path

# Add current directory to path
sys.path.append(str(Path(__file__).parent))

from daemon_manager import DaemonManager

def test_daemon():
    """Test daemon without forking"""
    print("🛡️ Testing Ultimate AGI Force Daemon v7.0.0")
    print("🇮🇩 Made with ❤️ by Mulky Malikul Dhaher in Indonesia")
    
    daemon = DaemonManager()
    
    # Create directories
    daemon.daemon_dir.mkdir(parents=True, exist_ok=True)
    daemon.log_dir.mkdir(parents=True, exist_ok=True)
    
    # Test agent loading
    print("\n🔧 Testing agent initialization...")
    daemon._start_all_agents()
    
    print(f"\n📊 Started {len(daemon.running_agents)} agents:")
    for agent_id, agent_data in daemon.running_agents.items():
        print(f"  ✅ {agent_id}: {agent_data['status']}")
    
    # Test web interface
    print("\n🌐 Starting web interface...")
    daemon._start_web_interface()
    
    print("\n✅ Test completed successfully!")
    print("🌐 Web interface should be available at: http://localhost:5000")
    
    return daemon

if __name__ == "__main__":
    daemon = test_daemon()
    
    # Keep running for testing
    try:
        print("\n🔄 Running in test mode... Press Ctrl+C to stop")
        while True:
            import time
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 Stopping test daemon...")
        daemon._stop_all_agents()

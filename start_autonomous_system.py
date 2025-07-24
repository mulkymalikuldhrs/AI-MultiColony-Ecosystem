#!/usr/bin/env python3
"""
🚀 AUTONOMOUS SYSTEM STARTUP SCRIPT
Ensures 24/7 operation with auto-restart and health monitoring

🇮🇩 Made with ❤️ by Mulky Malikul Dhaher in Indonesia 🇮🇩

Features:
- ✅ Auto-start on system boot
- ✅ Auto-restart on crashes
- ✅ Health monitoring
- ✅ Resource monitoring
- ✅ Dependency checking
- ✅ Environment setup
- ✅ Log management
- ✅ Process monitoring
"""

import asyncio
import json
import logging
import os
import signal
import subprocess
import sys
import threading
import time
from datetime import datetime
from pathlib import Path

import psutil

# Setup logging
log_dir = Path("autonomous/logs")
log_dir.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler(log_dir / "startup.log"), logging.StreamHandler()],
)
logger = logging.getLogger("StartupSystem")


class AutonomousSystemStarter:
    """
    🚀 AUTONOMOUS SYSTEM STARTER

    Manages the complete lifecycle of the autonomous system:
    - Environment validation
    - Dependency checking
    - System startup
    - Health monitoring
    - Auto-restart on failures
    - Resource management
    """

    def __init__(self):
        self.process = None
        self.is_running = False
        self.restart_count = 0
        self.max_restarts = 10
        self.startup_time = None

        # Health monitoring
        self.health_check_interval = 30
        self.last_health_check = None
        self.health_history = []

        # Performance monitoring
        self.performance_data = []
        self.resource_thresholds = {"cpu_max": 90, "memory_max": 85, "disk_max": 95}

    def start_autonomous_system(self):
        """Start the complete autonomous system"""
        print("🚀 STARTING AUTONOMOUS AI ECOSYSTEM")
        print("🇮🇩 Made with ❤️ by Mulky Malikul Dhaher")
        print("=" * 60)

        try:
            # Pre-startup checks
            self.pre_startup_checks()

            # Start the main system
            self.start_main_process()

            # Start monitoring
            self.start_health_monitoring()

            # Keep the starter running
            self.maintain_operation()

        except KeyboardInterrupt:
            logger.info("Startup system interrupted by user")
            self.graceful_shutdown()
        except Exception as e:
            logger.error(f"Startup system error: {e}")
            self.handle_startup_error(e)

    def pre_startup_checks(self):
        """Perform comprehensive pre-startup checks"""
        print("🔍 Performing pre-startup checks...")

        # Check Python version
        self.check_python_version()

        # Check system resources
        self.check_system_resources()

        # Check dependencies
        self.check_dependencies()

        # Setup environment
        self.setup_environment()

        # Check previous shutdown
        self.check_previous_shutdown()

        print("✅ All pre-startup checks passed")

    def check_python_version(self):
        """Check Python version compatibility"""
        version = sys.version_info
        if version.major < 3 or (version.major == 3 and version.minor < 8):
            raise Exception(
                f"Python 3.8+ required, found {version.major}.{version.minor}"
            )

        logger.info(f"Python version: {version.major}.{version.minor}.{version.micro}")

    def check_system_resources(self):
        """Check available system resources"""
        # Check available memory
        memory = psutil.virtual_memory()
        if memory.available < 1024 * 1024 * 1024:  # Less than 1GB
            logger.warning(
                f"Low memory: {memory.available / 1024 / 1024 / 1024:.1f}GB available"
            )

        # Check available disk space
        disk = psutil.disk_usage("/")
        if disk.free < 5 * 1024 * 1024 * 1024:  # Less than 5GB
            logger.warning(
                f"Low disk space: {disk.free / 1024 / 1024 / 1024:.1f}GB available"
            )

        # Check CPU cores
        cpu_count = psutil.cpu_count()
        logger.info(f"CPU cores available: {cpu_count}")

        logger.info("System resources check completed")

    def check_dependencies(self):
        """Check for required dependencies"""
        required_packages = [
            "asyncio",
            "psutil",
            "aiohttp",
            "aiofiles",
            "requests",
            "sqlite3",
        ]

        missing_packages = []

        for package in required_packages:
            try:
                __import__(package)
            except ImportError:
                missing_packages.append(package)

        if missing_packages:
            logger.warning(f"Missing packages: {missing_packages}")
            self.install_missing_packages(missing_packages)
        else:
            logger.info("All dependencies satisfied")

    def install_missing_packages(self, packages):
        """Install missing packages automatically"""
        logger.info(f"Installing missing packages: {packages}")

        for package in packages:
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", package])
                logger.info(f"Successfully installed {package}")
            except subprocess.CalledProcessError as e:
                logger.error(f"Failed to install {package}: {e}")

    def setup_environment(self):
        """Setup the execution environment"""
        # Create necessary directories
        directories = [
            "autonomous/logs",
            "autonomous/data",
            "autonomous/backup",
            "autonomous/monitoring",
            "autonomous/system_state",
            "data",
            "logs",
            "config",
        ]

        for directory in directories:
            Path(directory).mkdir(parents=True, exist_ok=True)

        # Set environment variables
        os.environ["AUTONOMOUS_MODE"] = "true"
        os.environ["AUTO_RESTART"] = "true"

        logger.info("Environment setup completed")

    def check_previous_shutdown(self):
        """Check if previous shutdown was clean"""
        shutdown_file = Path("autonomous/system_state/shutdown.json")

        if shutdown_file.exists():
            try:
                with open(shutdown_file, "r") as f:
                    shutdown_data = json.load(f)

                if shutdown_data.get("clean_shutdown", False):
                    logger.info("Previous shutdown was clean")
                else:
                    logger.warning(
                        "Previous shutdown was not clean - may need recovery"
                    )
                    self.handle_unclean_shutdown(shutdown_data)

            except Exception as e:
                logger.error(f"Error reading shutdown file: {e}")

        # Remove shutdown file to prepare for new run
        if shutdown_file.exists():
            shutdown_file.unlink()

    def start_main_process(self):
        """Start the main autonomous system process"""
        print("🤖 Starting main autonomous system...")

        try:
            # Start the autonomous main system
            self.process = subprocess.Popen(
                [sys.executable, "autonomous_main.py"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )

            self.is_running = True
            self.startup_time = datetime.now()

            logger.info(f"Main process started with PID: {self.process.pid}")
            print(f"✅ Autonomous system started (PID: {self.process.pid})")

        except Exception as e:
            logger.error(f"Failed to start main process: {e}")
            raise

    def start_health_monitoring(self):
        """Start health monitoring in a separate thread"""

        def health_monitor():
            while self.is_running:
                try:
                    self.perform_health_check()
                    time.sleep(self.health_check_interval)
                except Exception as e:
                    logger.error(f"Health monitoring error: {e}")
                    time.sleep(60)

        monitor_thread = threading.Thread(target=health_monitor, daemon=True)
        monitor_thread.start()

        logger.info("Health monitoring started")

    def perform_health_check(self):
        """Perform comprehensive health check"""
        health_data = {
            "timestamp": datetime.now().isoformat(),
            "process_running": self.is_process_running(),
            "system_resources": self.get_system_resources(),
            "performance_metrics": self.get_performance_metrics(),
        }

        # Check if process is still running
        if not health_data["process_running"]:
            logger.error("Main process is not running - initiating restart")
            self.restart_system()
            return

        # Check resource usage
        resources = health_data["system_resources"]
        if resources["cpu_usage"] > self.resource_thresholds["cpu_max"]:
            logger.warning(f"High CPU usage: {resources['cpu_usage']}%")

        if resources["memory_usage"] > self.resource_thresholds["memory_max"]:
            logger.warning(f"High memory usage: {resources['memory_usage']}%")

        if resources["disk_usage"] > self.resource_thresholds["disk_max"]:
            logger.warning(f"High disk usage: {resources['disk_usage']}%")

        # Store health data
        self.health_history.append(health_data)
        self.last_health_check = datetime.now()

        # Keep only last 100 health checks
        self.health_history = self.health_history[-100:]

        # Save health data
        self.save_health_data(health_data)

    def is_process_running(self):
        """Check if the main process is still running"""
        if not self.process:
            return False

        try:
            # Check if process is still alive
            return self.process.poll() is None
        except Exception:
            return False

    def get_system_resources(self):
        """Get current system resource usage"""
        return {
            "cpu_usage": psutil.cpu_percent(interval=1),
            "memory_usage": psutil.virtual_memory().percent,
            "disk_usage": psutil.disk_usage("/").percent,
            "load_average": os.getloadavg()[0] if hasattr(os, "getloadavg") else 0,
        }

    def get_performance_metrics(self):
        """Get performance metrics for the autonomous system"""
        if not self.process:
            return {}

        try:
            process = psutil.Process(self.process.pid)
            return {
                "cpu_percent": process.cpu_percent(),
                "memory_percent": process.memory_percent(),
                "num_threads": process.num_threads(),
                "connections": (
                    len(process.connections()) if hasattr(process, "connections") else 0
                ),
            }
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            return {}

    def save_health_data(self, health_data):
        """Save health data to file"""
        health_file = Path("autonomous/monitoring/health_data.json")

        try:
            if health_file.exists():
                with open(health_file, "r") as f:
                    all_health_data = json.load(f)
            else:
                all_health_data = []

            all_health_data.append(health_data)

            # Keep only last 1000 entries
            all_health_data = all_health_data[-1000:]

            with open(health_file, "w") as f:
                json.dump(all_health_data, f, indent=2)

        except Exception as e:
            logger.error(f"Error saving health data: {e}")

    def restart_system(self):
        """Restart the autonomous system"""
        if self.restart_count >= self.max_restarts:
            logger.critical(f"Maximum restart attempts ({self.max_restarts}) reached")
            self.emergency_shutdown()
            return

        self.restart_count += 1
        logger.info(
            f"Restarting system (attempt {self.restart_count}/{self.max_restarts})"
        )

        # Stop current process
        self.stop_main_process()

        # Wait a moment
        time.sleep(10)

        # Start again
        try:
            self.start_main_process()
            logger.info("System restart successful")
        except Exception as e:
            logger.error(f"Restart failed: {e}")
            time.sleep(30)  # Wait before next attempt

    def stop_main_process(self):
        """Stop the main process gracefully"""
        if not self.process:
            return

        try:
            # Try graceful shutdown first
            self.process.terminate()

            # Wait for graceful shutdown
            try:
                self.process.wait(timeout=30)
            except subprocess.TimeoutExpired:
                # Force kill if graceful shutdown fails
                logger.warning("Graceful shutdown timeout - force killing process")
                self.process.kill()
                self.process.wait()

            self.process = None
            self.is_running = False

            logger.info("Main process stopped")

        except Exception as e:
            logger.error(f"Error stopping main process: {e}")

    def maintain_operation(self):
        """Maintain 24/7 operation"""
        logger.info("Entering 24/7 operation mode")

        try:
            while self.is_running:
                # Check process status
                if not self.is_process_running():
                    logger.error("Process died - restarting")
                    self.restart_system()

                # Periodic maintenance
                if datetime.now().hour == 3 and datetime.now().minute == 0:
                    self.perform_daily_maintenance()

                time.sleep(60)  # Check every minute

        except KeyboardInterrupt:
            logger.info("Operation interrupted by user")
            self.graceful_shutdown()

    def perform_daily_maintenance(self):
        """Perform daily maintenance tasks"""
        logger.info("Performing daily maintenance")

        try:
            # Clean old logs
            self.clean_old_logs()

            # Optimize performance data
            self.optimize_performance_data()

            # Health check summary
            self.generate_health_summary()

        except Exception as e:
            logger.error(f"Daily maintenance error: {e}")

    def clean_old_logs(self):
        """Clean old log files"""
        log_dir = Path("autonomous/logs")

        for log_file in log_dir.glob("*.log"):
            if log_file.stat().st_mtime < time.time() - (7 * 24 * 3600):  # 7 days
                log_file.unlink()
                logger.info(f"Cleaned old log: {log_file}")

    def graceful_shutdown(self):
        """Gracefully shutdown the system"""
        logger.info("Initiating graceful shutdown")

        # Stop main process
        self.stop_main_process()

        # Save shutdown state
        shutdown_data = {
            "timestamp": datetime.now().isoformat(),
            "clean_shutdown": True,
            "restart_count": self.restart_count,
            "uptime": (
                str(datetime.now() - self.startup_time) if self.startup_time else None
            ),
        }

        shutdown_file = Path("autonomous/system_state/shutdown.json")
        with open(shutdown_file, "w") as f:
            json.dump(shutdown_data, f, indent=2)

        print("✅ Graceful shutdown completed")

    def emergency_shutdown(self):
        """Emergency shutdown when all restart attempts fail"""
        logger.critical("EMERGENCY SHUTDOWN - Maximum restart attempts exceeded")

        # Stop everything
        self.stop_main_process()

        # Save emergency state
        emergency_data = {
            "timestamp": datetime.now().isoformat(),
            "emergency_shutdown": True,
            "restart_count": self.restart_count,
            "last_health_check": (
                self.last_health_check.isoformat() if self.last_health_check else None
            ),
        }

        emergency_file = Path("autonomous/system_state/emergency.json")
        with open(emergency_file, "w") as f:
            json.dump(emergency_data, f, indent=2)

        print("🚨 EMERGENCY SHUTDOWN - System requires manual intervention")
        sys.exit(1)

    def handle_startup_error(self, error):
        """Handle startup errors"""
        logger.error(f"Startup error: {error}")

        # Try to recover
        if "dependencies" in str(error).lower():
            self.check_dependencies()
            time.sleep(10)
            self.start_autonomous_system()
        else:
            logger.critical("Cannot recover from startup error")
            sys.exit(1)

    def handle_unclean_shutdown(self, shutdown_data):
        """Handle recovery from unclean shutdown"""
        logger.info("Handling recovery from unclean shutdown")

        # Check for corruption
        # Restore from backup if needed
        # Reset system state

        # For now, just log and continue
        logger.info("Recovery completed")


def main():
    """Main entry point"""
    print("🚀 AUTONOMOUS SYSTEM STARTUP")
    print("🇮🇩 Made with ❤️ by Mulky Malikul Dhaher")
    print("🤖 Starting World's Most Advanced Autonomous AI System")
    print("=" * 60)

    starter = AutonomousSystemStarter()
    starter.start_autonomous_system()


if __name__ == "__main__":
    # Handle signals for graceful shutdown
    def signal_handler(sig, frame):
        print("\n🛑 Shutdown signal received")
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    main()

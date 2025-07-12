"""
Web UI Connector - Bridge between the unified launcher and web interface
Made with ❤️ by Mulky Malikul Dhaher in Indonesia 🇮🇩
"""

import os
import sys
import logging
import threading
import importlib.util
import subprocess
from pathlib import Path

# Setup logger
logger = logging.getLogger("web_ui_connector")

class WebUIConnector:
    """
    Connector class to bridge the unified launcher with the web interface.
    Handles starting, stopping, and communicating with the web UI.
    """
    
    def __init__(self, port=8080, host="0.0.0.0", debug=False):
        """
        Initialize the Web UI connector.
        
        Args:
            port: Port to run the web UI on
            host: Host to bind to
            debug: Whether to run in debug mode
        """
        self.port = port
        self.host = host
        self.debug = debug
        self.process = None
        self.thread = None
        self.running = False
        
        # Set environment variables
        os.environ["WEB_INTERFACE_PORT"] = str(port)
        os.environ["WEB_INTERFACE_HOST"] = host
        
        logger.info(f"Web UI connector initialized (port: {port}, host: {host})")
    
    def start_web_ui(self, background=True):
        """
        Start the web UI.
        
        Args:
            background: Whether to run in the background
            
        Returns:
            True if started successfully, False otherwise
        """
        if self.running:
            logger.warning("Web UI is already running")
            return True
        
        logger.info("Starting web UI...")
        
        try:
            # Try to import the Flask app
            try:
                from colony.api.app import app, socketio
                
                # Start in a separate thread if background is True
                if background:
                    self.thread = threading.Thread(
                        target=self._run_web_ui,
                        args=(app, socketio),
                        daemon=True
                    )
                    self.thread.start()
                    self.running = True
                    logger.info(f"Web UI started in background at http://{self.host}:{self.port}")
                    return True
                else:
                    # Run directly (blocking)
                    self._run_web_ui(app, socketio)
                    return True
            
            except ImportError as e:
                logger.warning(f"Could not import Flask app: {e}")
                logger.info("Attempting to start web UI with subprocess...")
                
                # Try to start with subprocess
                try:
                    if background:
                        # Start in background
                        self.process = subprocess.Popen(
                            [sys.executable, "-m", "colony.api.app"],
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE
                        )
                        self.running = True
                        logger.info(f"Web UI started in background with subprocess at http://{self.host}:{self.port}")
                        return True
                    else:
                        # Start blocking
                        subprocess.run([sys.executable, "-m", "colony.api.app"], check=True)
                        return True
                
                except Exception as sub_e:
                    logger.error(f"Failed to start web UI with subprocess: {sub_e}")
                    return False
        
        except Exception as e:
            logger.error(f"Error starting web UI: {e}")
            return False
    
    def _run_web_ui(self, app, socketio):
        """
        Run the web UI (internal method).
        
        Args:
            app: Flask app
            socketio: SocketIO instance
        """
        try:
            socketio.run(
                app,
                host=self.host,
                port=self.port,
                debug=self.debug,
                allow_unsafe_werkzeug=True
            )
        except Exception as e:
            logger.error(f"Error running web UI: {e}")
            self.running = False
    
    def stop_web_ui(self):
        """
        Stop the web UI.
        
        Returns:
            True if stopped successfully, False otherwise
        """
        if not self.running:
            logger.warning("Web UI is not running")
            return True
        
        logger.info("Stopping web UI...")
        
        try:
            if self.process:
                # Stop subprocess
                self.process.terminate()
                self.process.wait(timeout=5)
                self.process = None
            
            # Set running flag to False
            self.running = False
            logger.info("Web UI stopped")
            return True
        
        except Exception as e:
            logger.error(f"Error stopping web UI: {e}")
            return False
    
    def restart_web_ui(self, background=True):
        """
        Restart the web UI.
        
        Args:
            background: Whether to run in the background
            
        Returns:
            True if restarted successfully, False otherwise
        """
        logger.info("Restarting web UI...")
        
        # Stop if running
        if self.running:
            if not self.stop_web_ui():
                logger.error("Failed to stop web UI for restart")
                return False
        
        # Start again
        return self.start_web_ui(background)
    
    def get_status(self):
        """
        Get the status of the web UI.
        
        Returns:
            Status dictionary
        """
        return {
            "running": self.running,
            "port": self.port,
            "host": self.host,
            "url": f"http://{self.host}:{self.port}" if self.running else None,
            "process_id": self.process.pid if self.process else None
        }

# Global instance
web_ui_connector = WebUIConnector()

def start_web_ui(background=True, port=None, host=None):
    """
    Start the web UI using the global connector.
    
    Args:
        background: Whether to run in the background
        port: Port to run on (optional)
        host: Host to bind to (optional)
        
    Returns:
        True if started successfully, False otherwise
    """
    global web_ui_connector
    
    # Update port and host if provided
    if port is not None:
        web_ui_connector.port = port
        os.environ["WEB_INTERFACE_PORT"] = str(port)
    
    if host is not None:
        web_ui_connector.host = host
        os.environ["WEB_INTERFACE_HOST"] = host
    
    return web_ui_connector.start_web_ui(background)

def stop_web_ui():
    """
    Stop the web UI using the global connector.
    
    Returns:
        True if stopped successfully, False otherwise
    """
    global web_ui_connector
    return web_ui_connector.stop_web_ui()

def restart_web_ui(background=True):
    """
    Restart the web UI using the global connector.
    
    Args:
        background: Whether to run in the background
        
    Returns:
        True if restarted successfully, False otherwise
    """
    global web_ui_connector
    return web_ui_connector.restart_web_ui(background)

def get_web_ui_status():
    """
    Get the status of the web UI using the global connector.
    
    Returns:
        Status dictionary
    """
    global web_ui_connector
    return web_ui_connector.get_status()
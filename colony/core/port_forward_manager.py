#!/usr/bin/env python3
"""
🌐 Port Forward Manager - Automatic Port Forwarding System
Ensures AGI colonies are accessible from anywhere in the world

Made with ❤️ by Mulky Malikul Dhaher in Indonesia 🇮🇩
"""

import asyncio
import json
import os
import socket
import subprocess
import threading
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import psutil
import requests


class PortForwardManager:
    """
    Automatic port forwarding manager for AGI colony accessibility
    Ensures all colonies can communicate regardless of network topology
    """

    def __init__(self):
        self.manager_id = "port_forward_manager"
        self.name = "Port Forward Manager"
        self.version = "7.0.0-ultimate"
        self.status = "ready"

        # Owner loyalty
        self.owner_identity = "1108151509970001"  # Mulky Malikul Dhaher
        self.owner_name = "Mulky Malikul Dhaher"

        # Port forwarding configuration
        self.forwarded_ports = {
            "main_dashboard": 5000,
            "agent_communication": 8080,
            "colony_discovery": 7777,
            "secure_tunnel": 9999,
            "ssh_backup": 2222,
            "http_backup": 8000,
            "websocket": 9000,
            "api_gateway": 3000,
        }

        # Port forwarding methods
        self.forwarding_methods = {
            "upnp": UPnPForwarder(self),
            "ssh_tunnel": SSHTunnelForwarder(self),
            "ngrok": NgrokForwarder(self),
            "cloudflare": CloudflareForwarder(self),
            "reverse_proxy": ReverseProxyForwarder(self),
        }

        # Active forwarding status
        self.active_forwards = {}
        self.external_addresses = {}

        # Data storage
        self.data_dir = Path("data/port_forwarding")
        self.data_dir.mkdir(parents=True, exist_ok=True)

        print(f"🌐 {self.name} initialized for global accessibility")
        print(f"👑 Serving: {self.owner_name} ({self.owner_identity})")

    async def start(self):
        """Start automatic port forwarding system"""
        print(f"🚀 Starting {self.name} v{self.version}")
        self.status = "active"

        # Initialize all forwarding methods
        await self._initialize_forwarding_methods()

        # Setup automatic port forwarding
        await self._setup_automatic_forwarding()

        # Start monitoring and maintenance
        await self._start_monitoring()

        # Start external address discovery
        await self._start_address_discovery()

        print(f"✅ {self.name} fully operational - global access enabled")

        # Log successful startup
        self._log_startup_success()

    async def _initialize_forwarding_methods(self):
        """Initialize all port forwarding methods"""
        for method_name, forwarder in self.forwarding_methods.items():
            try:
                await forwarder.initialize()
                print(f"🔧 {method_name} forwarder ready")
            except Exception as e:
                print(f"⚠️ {method_name} forwarder warning: {e}")

    async def _setup_automatic_forwarding(self):
        """Setup automatic port forwarding for all required ports"""
        print("🔀 Setting up automatic port forwarding...")

        for port_name, port_number in self.forwarded_ports.items():
            await self._forward_port(port_name, port_number)

        print(f"✅ {len(self.active_forwards)} ports forwarded successfully")

    async def _forward_port(self, port_name: str, port_number: int):
        """Forward a specific port using best available method"""
        try:
            # Try forwarding methods in priority order
            methods_priority = [
                "upnp",
                "ngrok",
                "cloudflare",
                "ssh_tunnel",
                "reverse_proxy",
            ]

            for method_name in methods_priority:
                forwarder = self.forwarding_methods.get(method_name)

                if forwarder and await forwarder.is_available():
                    result = await forwarder.forward_port(port_number, port_name)

                    if result.get("success"):
                        self.active_forwards[port_name] = {
                            "port": port_number,
                            "method": method_name,
                            "external_address": result.get("external_address"),
                            "status": "active",
                            "started_at": datetime.now().isoformat(),
                        }

                        print(
                            f"✅ {port_name}:{port_number} forwarded via {method_name}"
                        )
                        print(f"🌐 External access: {result.get('external_address')}")
                        break
            else:
                print(f"❌ Failed to forward {port_name}:{port_number}")

        except Exception as e:
            print(f"🔀 Port forwarding error for {port_name}: {e}")

    async def _start_monitoring(self):
        """Start monitoring of forwarded ports"""
        monitoring_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        monitoring_thread.start()

        print("📊 Port forwarding monitoring started")

    def _monitoring_loop(self):
        """Continuous monitoring of port forwards"""
        while self.status == "active":
            try:
                # Check each forwarded port
                for port_name, forward_info in self.active_forwards.items():
                    if not self._check_forward_health(forward_info):
                        print(f"⚠️ {port_name} forward unhealthy, attempting repair")
                        self._repair_forward(port_name, forward_info)

                # Update external addresses
                self._update_external_addresses()

                # Save current status
                self._save_forwarding_status()

                # Wait before next check
                time.sleep(60)  # Check every minute

            except Exception as e:
                print(f"📊 Monitoring error: {e}")
                time.sleep(120)  # Wait longer on error

    def _check_forward_health(self, forward_info: Dict) -> bool:
        """Check if port forward is healthy"""
        try:
            port = forward_info["port"]
            external_address = forward_info.get("external_address")

            # Check local port is listening
            if not self._is_port_listening(port):
                return False

            # Check external accessibility if address available
            if external_address:
                return self._check_external_accessibility(external_address)

            return True

        except:
            return False

    def _is_port_listening(self, port: int) -> bool:
        """Check if port is listening locally"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            result = sock.connect_ex(("localhost", port))
            sock.close()
            return result == 0
        except:
            return False

    def _check_external_accessibility(self, address: str) -> bool:
        """Check if external address is accessible"""
        try:
            response = requests.get(f"http://{address}", timeout=5)
            return response.status_code in [200, 302, 401]  # Any response is good
        except:
            return False

    def _repair_forward(self, port_name: str, forward_info: Dict):
        """Attempt to repair a broken port forward"""
        try:
            port = forward_info["port"]
            method_name = forward_info["method"]

            # Try to re-establish forward
            forwarder = self.forwarding_methods.get(method_name)
            if forwarder:
                asyncio.create_task(self._forward_port(port_name, port))
        except Exception as e:
            print(f"🔧 Repair failed for {port_name}: {e}")

    async def _start_address_discovery(self):
        """Start discovery of external addresses"""
        discovery_thread = threading.Thread(
            target=self._address_discovery_loop, daemon=True
        )
        discovery_thread.start()

        print("🔍 External address discovery started")

    def _address_discovery_loop(self):
        """Continuously discover and update external addresses"""
        while self.status == "active":
            try:
                # Discover public IP
                public_ip = self._get_public_ip()
                if public_ip:
                    self.external_addresses["public_ip"] = public_ip

                # Update DNS records if configured
                self._update_dns_records()

                # Wait before next discovery
                time.sleep(300)  # Check every 5 minutes

            except Exception as e:
                print(f"🔍 Address discovery error: {e}")
                time.sleep(600)  # Wait longer on error

    def _get_public_ip(self) -> Optional[str]:
        """Get public IP address"""
        try:
            services = [
                "https://api.ipify.org",
                "https://icanhazip.com",
                "https://ident.me",
            ]

            for service in services:
                try:
                    response = requests.get(service, timeout=5)
                    if response.status_code == 200:
                        return response.text.strip()
                except:
                    continue

            return None

        except:
            return None

    def _update_external_addresses(self):
        """Update external addresses for all forwards"""
        for port_name, forward_info in self.active_forwards.items():
            if forward_info.get("external_address"):
                self.external_addresses[port_name] = forward_info["external_address"]

    def _update_dns_records(self):
        """Update DNS records for dynamic addressing"""
        # This would update DNS records if dynamic DNS is configured
        pass

    def _save_forwarding_status(self):
        """Save current forwarding status"""
        try:
            status_data = {
                "active_forwards": self.active_forwards,
                "external_addresses": self.external_addresses,
                "last_update": datetime.now().isoformat(),
                "status": self.status,
            }

            with open(self.data_dir / "forwarding_status.json", "w") as f:
                json.dump(status_data, f, indent=2)

        except Exception as e:
            print(f"💾 Failed to save status: {e}")

    def _log_startup_success(self):
        """Log successful startup with access information"""
        try:
            access_log = {
                "startup_time": datetime.now().isoformat(),
                "owner": self.owner_name,
                "owner_id": self.owner_identity,
                "forwarded_ports": self.forwarded_ports,
                "active_forwards": self.active_forwards,
                "external_addresses": self.external_addresses,
                "global_access": "enabled",
            }

            with open(self.data_dir / "access_log.json", "w") as f:
                json.dump(access_log, f, indent=2)

            print("📝 Access log saved successfully")

        except Exception as e:
            print(f"📝 Failed to save access log: {e}")

    def get_access_info(self) -> Dict:
        """Get current access information"""
        return {
            "status": self.status,
            "forwarded_ports": self.forwarded_ports,
            "active_forwards": self.active_forwards,
            "external_addresses": self.external_addresses,
            "global_access": len(self.active_forwards) > 0,
        }

    async def health_check(self) -> bool:
        """Perform health check"""
        try:
            return (
                self.status == "active"
                and len(self.active_forwards) > 0
                and any(
                    self._check_forward_health(info)
                    for info in self.active_forwards.values()
                )
            )
        except:
            return False

    async def stop(self):
        """Stop port forwarding manager"""
        print(f"🛑 Stopping {self.name}")
        self.status = "stopping"

        # Stop all forwards
        for port_name, forward_info in self.active_forwards.items():
            method_name = forward_info["method"]
            forwarder = self.forwarding_methods.get(method_name)

            if forwarder:
                try:
                    await forwarder.stop_forward(forward_info["port"])
                except Exception as e:
                    print(f"⚠️ Failed to stop {port_name}: {e}")

        self.status = "stopped"
        print(f"✅ {self.name} stopped")


# Base class for forwarding methods
class BaseForwarder:
    def __init__(self, parent_manager):
        self.parent = parent_manager
        self.available = False

    async def initialize(self):
        pass

    async def is_available(self) -> bool:
        return self.available

    async def forward_port(self, port: int, name: str) -> Dict:
        return {"success": False, "error": "Not implemented"}

    async def stop_forward(self, port: int):
        pass


class UPnPForwarder(BaseForwarder):
    """UPnP automatic port forwarding"""

    async def initialize(self):
        try:
            import miniupnpc

            self.upnp = miniupnpc.UPnP()
            self.upnp.discoverdelay = 200

            if self.upnp.discover() > 0:
                self.upnp.selectigd()
                self.available = True
                print("🔧 UPnP gateway discovered")
            else:
                print("⚠️ No UPnP gateway found")
        except ImportError:
            print("📦 UPnP library not available")
        except Exception as e:
            print(f"🔧 UPnP initialization error: {e}")

    async def forward_port(self, port: int, name: str) -> Dict:
        try:
            if not self.available:
                return {"success": False, "error": "UPnP not available"}

            # Add port mapping
            result = self.upnp.addportmapping(
                port, "TCP", self.upnp.lanaddr, port, f"AGI Colony {name}", ""
            )

            if result:
                external_ip = self.upnp.externalipaddress()
                return {
                    "success": True,
                    "external_address": f"{external_ip}:{port}",
                    "method": "upnp",
                }
            else:
                return {"success": False, "error": "UPnP mapping failed"}

        except Exception as e:
            return {"success": False, "error": str(e)}


class NgrokForwarder(BaseForwarder):
    """Ngrok tunnel forwarding"""

    async def initialize(self):
        try:
            # Check if ngrok is available
            result = subprocess.run(
                ["ngrok", "version"], capture_output=True, text=True, timeout=5
            )
            if result.returncode == 0:
                self.available = True
                print("🔧 Ngrok available")
            else:
                print("⚠️ Ngrok not found")
        except:
            print("⚠️ Ngrok not available")

    async def forward_port(self, port: int, name: str) -> Dict:
        try:
            if not self.available:
                return {"success": False, "error": "Ngrok not available"}

            # Start ngrok tunnel
            process = subprocess.Popen(
                ["ngrok", "http", str(port), "--log=stdout"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )

            # Wait a bit for tunnel to establish
            time.sleep(3)

            # Get tunnel URL from ngrok API
            try:
                response = requests.get("http://localhost:4040/api/tunnels", timeout=5)
                if response.status_code == 200:
                    tunnels = response.json().get("tunnels", [])
                    for tunnel in tunnels:
                        if (
                            tunnel.get("config", {}).get("addr")
                            == f"http://localhost:{port}"
                        ):
                            public_url = (
                                tunnel.get("public_url", "")
                                .replace("https://", "")
                                .replace("http://", "")
                            )
                            return {
                                "success": True,
                                "external_address": public_url,
                                "method": "ngrok",
                                "process": process,
                            }
            except:
                pass

            return {"success": False, "error": "Failed to get ngrok tunnel URL"}

        except Exception as e:
            return {"success": False, "error": str(e)}


class SSHTunnelForwarder(BaseForwarder):
    """SSH tunnel forwarding"""

    async def initialize(self):
        # SSH tunnel would require configuration
        print("🔧 SSH tunnel forwarder initialized (requires configuration)")

    async def forward_port(self, port: int, name: str) -> Dict:
        # SSH tunnel implementation would go here
        return {"success": False, "error": "SSH tunnel requires configuration"}


class CloudflareForwarder(BaseForwarder):
    """Cloudflare tunnel forwarding"""

    async def initialize(self):
        try:
            # Check if cloudflared is available
            result = subprocess.run(
                ["cloudflared", "version"], capture_output=True, text=True, timeout=5
            )
            if result.returncode == 0:
                self.available = True
                print("🔧 Cloudflared available")
            else:
                print("⚠️ Cloudflared not found")
        except:
            print("⚠️ Cloudflared not available")

    async def forward_port(self, port: int, name: str) -> Dict:
        # Cloudflare tunnel implementation would go here
        return {"success": False, "error": "Cloudflare tunnel requires configuration"}


class ReverseProxyForwarder(BaseForwarder):
    """Reverse proxy forwarding"""

    async def initialize(self):
        print("🔧 Reverse proxy forwarder initialized")
        self.available = True

    async def forward_port(self, port: int, name: str) -> Dict:
        # Simple reverse proxy implementation
        return {"success": False, "error": "Reverse proxy requires setup"}


# Global instance
port_forward_manager = PortForwardManager()

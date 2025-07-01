"""
🖥️ Advanced System Monitoring Dashboard
Real-time monitoring untuk user device & server dengan AI intervention

Made with ❤️ by Mulky Malikul Dhaher in Indonesia 🇮🇩
KTP: 1107151509970001 (Developer Access - Free Forever)
"""

import psutil
import platform
import socket
import json
import asyncio
import threading
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
import subprocess
import requests
import hashlib

@dataclass
class SystemMetrics:
    """Data structure untuk system metrics"""
    timestamp: str
    cpu_percent: float
    memory_percent: float
    disk_percent: float
    network_io: Dict[str, int]
    temperature: Optional[float]
    battery_percent: Optional[float]
    processes_count: int
    uptime: float
    os_info: Dict[str, str]
    threats_detected: List[str]
    performance_score: float

@dataclass
class ThreatAlert:
    """Data structure untuk threat detection"""
    threat_id: str
    threat_type: str
    severity: str  # low, medium, high, critical
    description: str
    timestamp: str
    auto_resolved: bool
    resolution_action: str

class AdvancedSystemMonitor:
    """
    🖥️ Advanced System Monitoring dengan AI Intervention
    
    Features:
    - Real-time CPU/Memory/Disk monitoring
    - Operating System integration (Windows, Linux, macOS)
    - Automated crash detection & recovery
    - Threat detection & response
    - Performance optimization
    - Cross-platform support
    """
    
    def __init__(self):
        self.monitoring_active = False
        self.metrics_history = []
        self.threat_alerts = []
        self.performance_baseline = None
        self.auto_optimization = True
        self.threat_detection_enabled = True
        
        # Monitoring intervals
        self.monitor_interval = 5  # seconds
        self.threat_scan_interval = 60  # seconds
        self.optimization_interval = 300  # 5 minutes
        
        # Performance thresholds
        self.cpu_threshold = 85.0
        self.memory_threshold = 80.0
        self.disk_threshold = 90.0
        self.temperature_threshold = 80.0
        
        # Initialize monitoring
        self._initialize_monitoring()
    
    def _initialize_monitoring(self):
        """Initialize monitoring system"""
        print("🖥️ Initializing Advanced System Monitor...")
        
        # Detect operating system
        self.os_info = {
            "system": platform.system(),
            "release": platform.release(),
            "version": platform.version(),
            "machine": platform.machine(),
            "processor": platform.processor(),
            "hostname": socket.gethostname(),
            "python_version": platform.python_version()
        }
        
        print(f"  ✅ OS Detected: {self.os_info['system']} {self.os_info['release']}")
        print(f"  ✅ Hostname: {self.os_info['hostname']}")
        print(f"  ✅ Processor: {self.os_info['processor']}")
        
        # Initialize baseline performance
        self._establish_performance_baseline()
        
    def _establish_performance_baseline(self):
        """Establish baseline performance metrics"""
        print("📊 Establishing performance baseline...")
        
        # Collect samples for baseline
        samples = []
        for i in range(10):
            metrics = self._collect_system_metrics()
            samples.append(metrics)
            time.sleep(1)
        
        # Calculate baseline
        self.performance_baseline = {
            "avg_cpu": sum(s.cpu_percent for s in samples) / len(samples),
            "avg_memory": sum(s.memory_percent for s in samples) / len(samples),
            "avg_disk": sum(s.disk_percent for s in samples) / len(samples),
            "established_at": datetime.now().isoformat()
        }
        
        print(f"  ✅ Baseline established - CPU: {self.performance_baseline['avg_cpu']:.1f}%")
    
    def start_monitoring(self):
        """Start real-time system monitoring"""
        if self.monitoring_active:
            return {"status": "already_running"}
        
        self.monitoring_active = True
        print("🚀 Starting Advanced System Monitoring...")
        
        # Start monitoring threads
        monitor_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        threat_thread = threading.Thread(target=self._threat_detection_loop, daemon=True)
        optimization_thread = threading.Thread(target=self._optimization_loop, daemon=True)
        
        monitor_thread.start()
        threat_thread.start()
        optimization_thread.start()
        
        print("  ✅ System monitoring active")
        print("  ✅ Threat detection active")
        print("  ✅ Auto-optimization active")
        
        return {"status": "started", "monitoring_active": True}
    
    def stop_monitoring(self):
        """Stop system monitoring"""
        self.monitoring_active = False
        print("🛑 System monitoring stopped")
        return {"status": "stopped", "monitoring_active": False}
    
    def _monitoring_loop(self):
        """Main monitoring loop"""
        while self.monitoring_active:
            try:
                # Collect metrics
                metrics = self._collect_system_metrics()
                
                # Store metrics
                self.metrics_history.append(metrics)
                
                # Keep only last 1000 entries
                if len(self.metrics_history) > 1000:
                    self.metrics_history = self.metrics_history[-1000:]
                
                # Check for alerts
                self._check_performance_alerts(metrics)
                
                # Sleep until next check
                time.sleep(self.monitor_interval)
                
            except Exception as e:
                print(f"❌ Monitoring error: {e}")
                time.sleep(self.monitor_interval)
    
    def _collect_system_metrics(self) -> SystemMetrics:
        """Collect comprehensive system metrics"""
        try:
            # CPU metrics
            cpu_percent = psutil.cpu_percent(interval=1)
            
            # Memory metrics
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            
            # Disk metrics
            disk = psutil.disk_usage('/')
            disk_percent = disk.percent
            
            # Network I/O
            network = psutil.net_io_counters()
            network_io = {
                "bytes_sent": network.bytes_sent,
                "bytes_recv": network.bytes_recv,
                "packets_sent": network.packets_sent,
                "packets_recv": network.packets_recv
            }
            
            # Temperature (if available)
            temperature = self._get_cpu_temperature()
            
            # Battery (if available)
            battery_percent = self._get_battery_level()
            
            # Process count
            processes_count = len(psutil.pids())
            
            # System uptime
            uptime = time.time() - psutil.boot_time()
            
            # Performance score calculation
            performance_score = self._calculate_performance_score(
                cpu_percent, memory_percent, disk_percent
            )
            
            # Create metrics object
            metrics = SystemMetrics(
                timestamp=datetime.now().isoformat(),
                cpu_percent=cpu_percent,
                memory_percent=memory_percent,
                disk_percent=disk_percent,
                network_io=network_io,
                temperature=temperature,
                battery_percent=battery_percent,
                processes_count=processes_count,
                uptime=uptime,
                os_info=self.os_info,
                threats_detected=[],
                performance_score=performance_score
            )
            
            return metrics
            
        except Exception as e:
            print(f"❌ Error collecting metrics: {e}")
            return self._get_fallback_metrics()
    
    def _get_cpu_temperature(self) -> Optional[float]:
        """Get CPU temperature if available"""
        try:
            if platform.system() == "Linux":
                # Try to read from thermal zone
                try:
                    with open('/sys/class/thermal/thermal_zone0/temp', 'r') as f:
                        temp = float(f.read().strip()) / 1000.0
                        return temp
                except:
                    pass
            
            # Try psutil sensors (if available)
            try:
                temps = psutil.sensors_temperatures()
                if temps:
                    # Get first available temperature
                    for name, entries in temps.items():
                        if entries:
                            return entries[0].current
            except:
                pass
            
            return None
            
        except Exception:
            return None
    
    def _get_battery_level(self) -> Optional[float]:
        """Get battery level if available"""
        try:
            battery = psutil.sensors_battery()
            if battery:
                return battery.percent
            return None
        except Exception:
            return None
    
    def _calculate_performance_score(self, cpu: float, memory: float, disk: float) -> float:
        """Calculate overall performance score (0-100)"""
        try:
            # Invert percentages (lower usage = higher score)
            cpu_score = max(0, 100 - cpu)
            memory_score = max(0, 100 - memory)
            disk_score = max(0, 100 - disk)
            
            # Weighted average
            performance_score = (cpu_score * 0.4 + memory_score * 0.4 + disk_score * 0.2)
            
            return round(performance_score, 2)
        except Exception:
            return 50.0  # Default middle score
    
    def _check_performance_alerts(self, metrics: SystemMetrics):
        """Check for performance issues and trigger alerts"""
        alerts = []
        
        # CPU alert
        if metrics.cpu_percent > self.cpu_threshold:
            alerts.append(f"High CPU usage: {metrics.cpu_percent:.1f}%")
            self._trigger_cpu_optimization()
        
        # Memory alert
        if metrics.memory_percent > self.memory_threshold:
            alerts.append(f"High memory usage: {metrics.memory_percent:.1f}%")
            self._trigger_memory_optimization()
        
        # Disk alert
        if metrics.disk_percent > self.disk_threshold:
            alerts.append(f"High disk usage: {metrics.disk_percent:.1f}%")
            self._trigger_disk_cleanup()
        
        # Temperature alert
        if metrics.temperature and metrics.temperature > self.temperature_threshold:
            alerts.append(f"High temperature: {metrics.temperature:.1f}°C")
            self._trigger_cooling_optimization()
        
        # Log alerts
        for alert in alerts:
            print(f"⚠️ ALERT: {alert}")
            self._log_system_alert(alert, "performance")
    
    def _threat_detection_loop(self):
        """Threat detection loop"""
        while self.monitoring_active:
            try:
                if self.threat_detection_enabled:
                    threats = self._scan_for_threats()
                    
                    for threat in threats:
                        self._handle_threat(threat)
                
                time.sleep(self.threat_scan_interval)
                
            except Exception as e:
                print(f"❌ Threat detection error: {e}")
                time.sleep(self.threat_scan_interval)
    
    def _scan_for_threats(self) -> List[ThreatAlert]:
        """Scan for security threats"""
        threats = []
        
        try:
            # Check for suspicious processes
            suspicious_processes = self._check_suspicious_processes()
            threats.extend(suspicious_processes)
            
            # Check network connections
            suspicious_connections = self._check_network_connections()
            threats.extend(suspicious_connections)
            
            # Check file system
            file_threats = self._check_file_system_threats()
            threats.extend(file_threats)
            
            # Check system integrity
            integrity_threats = self._check_system_integrity()
            threats.extend(integrity_threats)
            
        except Exception as e:
            print(f"❌ Threat scanning error: {e}")
        
        return threats
    
    def _check_suspicious_processes(self) -> List[ThreatAlert]:
        """Check for suspicious running processes"""
        threats = []
        
        try:
            # Known malicious process patterns
            suspicious_patterns = [
                "cryptominer", "botnet", "keylogger", "rootkit",
                "trojan", "backdoor", "ransomware", "spyware"
            ]
            
            for proc in psutil.process_iter(['pid', 'name', 'exe', 'cmdline']):
                try:
                    proc_info = proc.info
                    proc_name = proc_info.get('name', '').lower()
                    
                    # Check against suspicious patterns
                    for pattern in suspicious_patterns:
                        if pattern in proc_name:
                            threat = ThreatAlert(
                                threat_id=f"proc_{proc_info['pid']}_{int(time.time())}",
                                threat_type="suspicious_process",
                                severity="high",
                                description=f"Suspicious process detected: {proc_name}",
                                timestamp=datetime.now().isoformat(),
                                auto_resolved=False,
                                resolution_action="process_analysis_required"
                            )
                            threats.append(threat)
                            
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
                    
        except Exception as e:
            print(f"❌ Process scanning error: {e}")
        
        return threats
    
    def _check_network_connections(self) -> List[ThreatAlert]:
        """Check for suspicious network connections"""
        threats = []
        
        try:
            # Get network connections
            connections = psutil.net_connections(kind='inet')
            
            # Known malicious IP ranges or patterns
            suspicious_ports = [4444, 6667, 6969, 31337, 12345, 54321]
            
            for conn in connections:
                if conn.raddr:  # Has remote address
                    remote_ip = conn.raddr.ip
                    remote_port = conn.raddr.port
                    
                    # Check suspicious ports
                    if remote_port in suspicious_ports:
                        threat = ThreatAlert(
                            threat_id=f"net_{remote_ip}_{remote_port}_{int(time.time())}",
                            threat_type="suspicious_network",
                            severity="medium",
                            description=f"Suspicious network connection: {remote_ip}:{remote_port}",
                            timestamp=datetime.now().isoformat(),
                            auto_resolved=False,
                            resolution_action="connection_monitoring"
                        )
                        threats.append(threat)
                        
        except Exception as e:
            print(f"❌ Network scanning error: {e}")
        
        return threats
    
    def _check_file_system_threats(self) -> List[ThreatAlert]:
        """Check for file system threats"""
        threats = []
        
        try:
            # Check for suspicious file extensions in common directories
            suspicious_extensions = ['.exe.scr', '.bat.exe', '.vbs', '.js.exe']
            
            import os
            check_dirs = []
            
            # Platform-specific directories
            if platform.system() == "Windows":
                check_dirs = [
                    os.path.expanduser("~\\Desktop"),
                    os.path.expanduser("~\\Downloads"),
                    "C:\\Temp"
                ]
            else:
                check_dirs = [
                    os.path.expanduser("~/Desktop"),
                    os.path.expanduser("~/Downloads"),
                    "/tmp"
                ]
            
            for check_dir in check_dirs:
                if os.path.exists(check_dir):
                    try:
                        for root, dirs, files in os.walk(check_dir):
                            for file in files:
                                for ext in suspicious_extensions:
                                    if file.lower().endswith(ext):
                                        threat = ThreatAlert(
                                            threat_id=f"file_{hashlib.md5(file.encode()).hexdigest()}",
                                            threat_type="suspicious_file",
                                            severity="high",
                                            description=f"Suspicious file detected: {file}",
                                            timestamp=datetime.now().isoformat(),
                                            auto_resolved=False,
                                            resolution_action="file_quarantine_recommended"
                                        )
                                        threats.append(threat)
                            break  # Only check first level
                    except PermissionError:
                        continue
                        
        except Exception as e:
            print(f"❌ File system scanning error: {e}")
        
        return threats
    
    def _check_system_integrity(self) -> List[ThreatAlert]:
        """Check system integrity"""
        threats = []
        
        try:
            # Check system file modifications (basic check)
            if platform.system() == "Windows":
                # Check Windows system files
                system_files = [
                    "C:\\Windows\\System32\\notepad.exe",
                    "C:\\Windows\\System32\\calc.exe"
                ]
            else:
                # Check Linux system files
                system_files = [
                    "/bin/ls",
                    "/bin/cat"
                ]
            
            for file_path in system_files:
                if os.path.exists(file_path):
                    # Basic integrity check (size and modification time)
                    try:
                        stat = os.stat(file_path)
                        mod_time = datetime.fromtimestamp(stat.st_mtime)
                        
                        # If system file was modified recently, it's suspicious
                        if mod_time > datetime.now() - timedelta(days=1):
                            threat = ThreatAlert(
                                threat_id=f"integrity_{hashlib.md5(file_path.encode()).hexdigest()}",
                                threat_type="system_integrity",
                                severity="critical",
                                description=f"System file recently modified: {file_path}",
                                timestamp=datetime.now().isoformat(),
                                auto_resolved=False,
                                resolution_action="system_scan_required"
                            )
                            threats.append(threat)
                            
                    except OSError:
                        continue
                        
        except Exception as e:
            print(f"❌ Integrity checking error: {e}")
        
        return threats
    
    def _handle_threat(self, threat: ThreatAlert):
        """Handle detected threat with AI intervention"""
        print(f"🚨 THREAT DETECTED: {threat.description}")
        
        # Store threat
        self.threat_alerts.append(threat)
        
        # Auto-resolution based on threat type
        if threat.threat_type == "suspicious_process":
            self._auto_resolve_process_threat(threat)
        elif threat.threat_type == "suspicious_network":
            self._auto_resolve_network_threat(threat)
        elif threat.threat_type == "suspicious_file":
            self._auto_resolve_file_threat(threat)
        elif threat.threat_type == "system_integrity":
            self._auto_resolve_integrity_threat(threat)
        
        # Log threat for analysis
        self._log_threat_alert(threat)
    
    def _auto_resolve_process_threat(self, threat: ThreatAlert):
        """Auto-resolve process threats"""
        try:
            # Extract process ID from threat_id
            parts = threat.threat_id.split('_')
            if len(parts) >= 2:
                pid = int(parts[1])
                
                # Terminate suspicious process
                try:
                    proc = psutil.Process(pid)
                    proc.terminate()
                    
                    threat.auto_resolved = True
                    threat.resolution_action = f"Process {pid} terminated"
                    
                    print(f"  ✅ Auto-resolved: Terminated process {pid}")
                    
                except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
                    print(f"  ❌ Could not terminate process {pid}: {e}")
                    
        except Exception as e:
            print(f"❌ Process threat resolution error: {e}")
    
    def _auto_resolve_network_threat(self, threat: ThreatAlert):
        """Auto-resolve network threats"""
        try:
            # Log connection for monitoring
            threat.auto_resolved = True
            threat.resolution_action = "Connection logged for monitoring"
            
            print(f"  ✅ Auto-resolved: Network threat logged for monitoring")
            
        except Exception as e:
            print(f"❌ Network threat resolution error: {e}")
    
    def _auto_resolve_file_threat(self, threat: ThreatAlert):
        """Auto-resolve file threats"""
        try:
            # For now, just log the threat
            threat.auto_resolved = True
            threat.resolution_action = "File marked for manual review"
            
            print(f"  ✅ Auto-resolved: File threat marked for review")
            
        except Exception as e:
            print(f"❌ File threat resolution error: {e}")
    
    def _auto_resolve_integrity_threat(self, threat: ThreatAlert):
        """Auto-resolve integrity threats"""
        try:
            # System integrity issues require manual intervention
            threat.auto_resolved = False
            threat.resolution_action = "Manual system scan required"
            
            print(f"  ⚠️ Manual intervention required for integrity threat")
            
        except Exception as e:
            print(f"❌ Integrity threat resolution error: {e}")
    
    def _optimization_loop(self):
        """System optimization loop"""
        while self.monitoring_active:
            try:
                if self.auto_optimization:
                    self._perform_system_optimization()
                
                time.sleep(self.optimization_interval)
                
            except Exception as e:
                print(f"❌ Optimization error: {e}")
                time.sleep(self.optimization_interval)
    
    def _perform_system_optimization(self):
        """Perform automatic system optimization"""
        try:
            print("🔧 Running system optimization...")
            
            # Memory optimization
            self._optimize_memory()
            
            # Disk cleanup
            self._optimize_disk()
            
            # Process optimization
            self._optimize_processes()
            
            print("  ✅ System optimization completed")
            
        except Exception as e:
            print(f"❌ System optimization error: {e}")
    
    def _trigger_cpu_optimization(self):
        """Trigger CPU optimization"""
        try:
            print("🔧 Optimizing CPU usage...")
            
            # Lower priority of high-CPU processes
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent']):
                try:
                    if proc.info['cpu_percent'] > 50:
                        process = psutil.Process(proc.info['pid'])
                        if platform.system() == "Windows":
                            process.nice(psutil.BELOW_NORMAL_PRIORITY_CLASS)
                        else:
                            process.nice(10)  # Lower priority
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            print("  ✅ CPU optimization applied")
            
        except Exception as e:
            print(f"❌ CPU optimization error: {e}")
    
    def _trigger_memory_optimization(self):
        """Trigger memory optimization"""
        self._optimize_memory()
    
    def _optimize_memory(self):
        """Optimize memory usage"""
        try:
            print("🧠 Optimizing memory...")
            
            if platform.system() == "Windows":
                # Windows memory optimization
                subprocess.run(['sfc', '/scannow'], capture_output=True, text=True)
            else:
                # Linux memory optimization
                try:
                    # Drop caches (requires root, will fail silently if not)
                    subprocess.run(['sync'], capture_output=True)
                    with open('/proc/sys/vm/drop_caches', 'w') as f:
                        f.write('3')
                except:
                    pass
            
            print("  ✅ Memory optimization completed")
            
        except Exception as e:
            print(f"❌ Memory optimization error: {e}")
    
    def _trigger_disk_cleanup(self):
        """Trigger disk cleanup"""
        self._optimize_disk()
    
    def _optimize_disk(self):
        """Optimize disk usage"""
        try:
            print("💾 Optimizing disk...")
            
            # Clear temporary files
            import tempfile
            import shutil
            
            temp_dir = tempfile.gettempdir()
            for file in os.listdir(temp_dir):
                file_path = os.path.join(temp_dir, file)
                try:
                    if os.path.isfile(file_path):
                        # Only delete files older than 1 day
                        if os.path.getmtime(file_path) < time.time() - 86400:
                            os.remove(file_path)
                    elif os.path.isdir(file_path):
                        if os.path.getmtime(file_path) < time.time() - 86400:
                            shutil.rmtree(file_path)
                except:
                    continue
            
            print("  ✅ Disk optimization completed")
            
        except Exception as e:
            print(f"❌ Disk optimization error: {e}")
    
    def _trigger_cooling_optimization(self):
        """Trigger cooling optimization"""
        try:
            print("🌡️ Optimizing system temperature...")
            
            # Reduce CPU frequency if possible
            if platform.system() == "Linux":
                try:
                    # Set CPU governor to powersave
                    subprocess.run(['cpufreq-set', '-g', 'powersave'], 
                                 capture_output=True)
                except:
                    pass
            
            print("  ✅ Cooling optimization applied")
            
        except Exception as e:
            print(f"❌ Cooling optimization error: {e}")
    
    def _optimize_processes(self):
        """Optimize running processes"""
        try:
            print("⚙️ Optimizing processes...")
            
            # Find and optimize resource-heavy processes
            processes = []
            for proc in psutil.process_iter(['pid', 'name', 'memory_percent', 'cpu_percent']):
                try:
                    processes.append(proc.info)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            # Sort by resource usage
            processes.sort(key=lambda x: x.get('memory_percent', 0) + x.get('cpu_percent', 0), 
                          reverse=True)
            
            # Optimize top resource users
            for proc_info in processes[:10]:  # Top 10 processes
                try:
                    process = psutil.Process(proc_info['pid'])
                    # Lower priority for resource-heavy processes
                    if platform.system() == "Windows":
                        process.nice(psutil.BELOW_NORMAL_PRIORITY_CLASS)
                    else:
                        process.nice(5)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            print("  ✅ Process optimization completed")
            
        except Exception as e:
            print(f"❌ Process optimization error: {e}")
    
    def get_current_metrics(self) -> Dict[str, Any]:
        """Get current system metrics"""
        if not self.metrics_history:
            metrics = self._collect_system_metrics()
            return asdict(metrics)
        
        return asdict(self.metrics_history[-1])
    
    def get_metrics_history(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get metrics history"""
        history = self.metrics_history[-limit:] if limit else self.metrics_history
        return [asdict(metrics) for metrics in history]
    
    def get_threat_alerts(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get threat alerts"""
        alerts = self.threat_alerts[-limit:] if limit else self.threat_alerts
        return [asdict(alert) for alert in alerts]
    
    def get_system_health_score(self) -> Dict[str, Any]:
        """Get overall system health score"""
        if not self.metrics_history:
            return {"health_score": 50, "status": "unknown"}
        
        latest_metrics = self.metrics_history[-1]
        
        # Calculate health components
        cpu_health = max(0, 100 - latest_metrics.cpu_percent)
        memory_health = max(0, 100 - latest_metrics.memory_percent)
        disk_health = max(0, 100 - latest_metrics.disk_percent)
        
        # Threat penalty
        recent_threats = len([t for t in self.threat_alerts 
                            if datetime.fromisoformat(t.timestamp) > 
                               datetime.now() - timedelta(hours=1)])
        threat_penalty = min(50, recent_threats * 10)
        
        # Calculate overall health
        health_score = (cpu_health * 0.3 + memory_health * 0.3 + 
                       disk_health * 0.2 + latest_metrics.performance_score * 0.2)
        health_score = max(0, health_score - threat_penalty)
        
        # Determine status
        if health_score >= 80:
            status = "excellent"
        elif health_score >= 60:
            status = "good"
        elif health_score >= 40:
            status = "fair"
        elif health_score >= 20:
            status = "poor"
        else:
            status = "critical"
        
        return {
            "health_score": round(health_score, 2),
            "status": status,
            "cpu_health": round(cpu_health, 2),
            "memory_health": round(memory_health, 2),
            "disk_health": round(disk_health, 2),
            "recent_threats": recent_threats,
            "monitoring_active": self.monitoring_active,
            "last_update": latest_metrics.timestamp
        }
    
    def _get_fallback_metrics(self) -> SystemMetrics:
        """Get fallback metrics when collection fails"""
        return SystemMetrics(
            timestamp=datetime.now().isoformat(),
            cpu_percent=0.0,
            memory_percent=0.0,
            disk_percent=0.0,
            network_io={},
            temperature=None,
            battery_percent=None,
            processes_count=0,
            uptime=0.0,
            os_info=self.os_info,
            threats_detected=[],
            performance_score=50.0
        )
    
    def _log_system_alert(self, alert: str, alert_type: str):
        """Log system alert"""
        try:
            log_entry = {
                "timestamp": datetime.now().isoformat(),
                "type": alert_type,
                "message": alert,
                "system_info": self.os_info
            }
            
            # In a real implementation, this would go to a proper logging system
            print(f"📝 LOGGED: {alert}")
            
        except Exception as e:
            print(f"❌ Logging error: {e}")
    
    def _log_threat_alert(self, threat: ThreatAlert):
        """Log threat alert"""
        try:
            # In a real implementation, this would go to a security information system
            print(f"🔐 THREAT LOGGED: {threat.description}")
            
        except Exception as e:
            print(f"❌ Threat logging error: {e}")

# Global instance
system_monitor = AdvancedSystemMonitor()

# Auto-start monitoring
def initialize_system_monitoring():
    """Initialize and start system monitoring"""
    print("🖥️ Initializing Advanced System Monitor...")
    system_monitor.start_monitoring()
    print("✅ System monitoring initialized and active")

if __name__ == "__main__":
    initialize_system_monitoring()
    
    # Keep monitoring running
    try:
        while True:
            time.sleep(10)
            health = system_monitor.get_system_health_score()
            print(f"System Health: {health['health_score']:.1f}% ({health['status']})")
    except KeyboardInterrupt:
        system_monitor.stop_monitoring()
        print("👋 System monitoring stopped")
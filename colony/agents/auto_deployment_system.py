"""
🚀 AUTONOMOUS DEPLOYMENT & UPDATE SYSTEM
Handles all deployments, updates, downloads, and installations automatically

🇮🇩 Made with ❤️ by Mulky Malikul Dhaher in Indonesia 🇮🇩
"""

import asyncio
import json
import os
import sys
import time
import threading
import requests
import subprocess
import shutil
import git
import zipfile
import tarfile
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional
import hashlib
import aiohttp
import aiofiles
import tempfile

from colony.core.base_agent import BaseAgent
from colony.core.agent_registry import register_agent

@register_agent(name="auto_deployment_system")
class AutoDeploymentSystem(BaseAgent):
    """
    🚀 AUTONOMOUS DEPLOYMENT SYSTEM
    
    Capabilities:
    - 📦 Auto-download updates from any source
    - 🔧 Install system and dependency updates
    - 🌐 Deploy to multiple environments automatically
    - 🔄 Self-updating without downtime
    - 📊 Monitor deployment health
    - 🛡️ Automatic rollback on failures
    - 🔍 Discover and install new features
    """

    def __init__(self, name: str, config: Dict[str, Any], memory_manager: Any):
        super().__init__(name, config, memory_manager)
        self.update_manager = UpdateManager()
        self.deployment_manager = DeploymentManager()
        self.download_manager = DownloadManager()
        self.installer = AutoInstaller()
        self.health_monitor = DeploymentHealthMonitor()
        
        # Background tasks
        self.is_running = False
        self.deployment_queue = []
        self.active_deployments = {}
        
        # Metrics
        self.deployment_metrics = {
            "total_deployments": 0,
            "successful_deployments": 0,
            "failed_deployments": 0,
            "rollbacks_performed": 0,
            "updates_installed": 0
        }
        
        self.initialize()

    def run(self, **kwargs):
        """The main entry point for the agent's execution."""
        self.update_status("running")
        # This agent is designed to be called with specific tasks,
        # so the run method will just keep the agent alive.
        while self.status == "running":
            time.sleep(1)

    def initialize(self):
        """Initialize deployment system"""
        print("🚀 Initializing Autonomous Deployment System...")
        
        # Create necessary directories
        self.setup_deployment_workspace()
        
        # Start background services
        self.start_background_services()
        
        self.status = "running"
        print("✅ Autonomous Deployment System is ACTIVE!")
    
    def setup_deployment_workspace(self):
        """Setup deployment workspace"""
        workspaces = [
            "deployments/downloads",
            "deployments/staging", 
            "deployments/production",
            "deployments/backup",
            "deployments/cache",
            "deployments/logs",
            "deployments/temp",
            "deployments/rollback",
            "deployments/updates"
        ]
        
        for workspace in workspaces:
            Path(workspace).mkdir(parents=True, exist_ok=True)
    
    def start_background_services(self):
        """Start all background deployment services"""
        self.is_running = True
        
        # Update checker
        update_thread = threading.Thread(target=self.continuous_update_checking, daemon=True)
        update_thread.start()
        
        # Deployment processor
        deploy_thread = threading.Thread(target=self.continuous_deployment_processing, daemon=True)
        deploy_thread.start()
        
        # Health monitoring
        health_thread = threading.Thread(target=self.continuous_health_monitoring, daemon=True)
        health_thread.start()
        
        # Self-improvement
        improvement_thread = threading.Thread(target=self.continuous_self_improvement, daemon=True)
        improvement_thread.start()
        
        print("🔄 All deployment services started - running 24/7!")
    
    def continuous_update_checking(self):
        """Continuous checking for updates"""
        while self.is_running:
            try:
                print("📦 Checking for updates...")
                
                # Check system updates
                system_updates = self.update_manager.check_system_updates()
                
                # Check dependency updates
                dependency_updates = self.update_manager.check_dependency_updates()
                
                # Check application updates
                app_updates = self.update_manager.check_application_updates()
                
                # Check for new features/modules
                feature_updates = self.update_manager.discover_new_features()
                
                all_updates = system_updates + dependency_updates + app_updates + feature_updates
                
                if all_updates:
                    print(f"🔄 Found {len(all_updates)} updates - processing...")
                    asyncio.run(self.process_updates(all_updates))
                
                time.sleep(900)  # Check every 15 minutes
                
            except Exception as e:
                print(f"❌ Update checking error: {e}")
                time.sleep(300)
    
    def continuous_deployment_processing(self):
        """Continuous deployment processing"""
        while self.is_running:
            try:
                if self.deployment_queue:
                    deployment = self.deployment_queue.pop(0)
                    print(f"🚀 Processing deployment: {deployment['name']}")
                    
                    asyncio.run(self.execute_deployment(deployment))
                
                time.sleep(30)  # Process queue every 30 seconds
                
            except Exception as e:
                print(f"❌ Deployment processing error: {e}")
                time.sleep(60)
    
    def continuous_health_monitoring(self):
        """Continuous deployment health monitoring"""
        while self.is_running:
            try:
                # Monitor active deployments
                for deployment_id, deployment in self.active_deployments.items():
                    health = self.health_monitor.check_deployment_health(deployment)
                    
                    if health["status"] == "failed":
                        print(f"🚨 Deployment {deployment_id} failed - initiating rollback")
                        asyncio.run(self.rollback_deployment(deployment_id))
                    elif health["status"] == "degraded":
                        print(f"⚠️ Deployment {deployment_id} degraded - attempting fix")
                        asyncio.run(self.fix_deployment_issues(deployment_id, health))
                
                time.sleep(120)  # Monitor every 2 minutes
                
            except Exception as e:
                print(f"❌ Health monitoring error: {e}")
                time.sleep(300)
    
    def continuous_self_improvement(self):
        """Continuous self-improvement and feature discovery"""
        while self.is_running:
            try:
                # Analyze deployment patterns
                patterns = self.analyze_deployment_patterns()
                
                # Identify improvement opportunities
                improvements = self.identify_deployment_improvements(patterns)
                
                if improvements:
                    print(f"🧬 Found {len(improvements)} improvement opportunities")
                    asyncio.run(self.implement_improvements(improvements))
                
                # Auto-discovery of new deployment strategies
                new_strategies = self.discover_new_deployment_strategies()
                
                if new_strategies:
                    print(f"🔍 Discovered {len(new_strategies)} new deployment strategies")
                    asyncio.run(self.implement_new_strategies(new_strategies))
                
                time.sleep(3600)  # Self-improve every hour
                
            except Exception as e:
                print(f"❌ Self-improvement error: {e}")
                time.sleep(1800)
    
    async def process_updates(self, updates: List[Dict]):
        """Process all discovered updates"""
        for update in updates:
            try:
                update_type = update["type"]
                
                print(f"📦 Processing {update_type}: {update['name']}")
                
                if update_type == "system_update":
                    await self.install_system_update(update)
                elif update_type == "dependency_update":
                    await self.install_dependency_update(update)
                elif update_type == "application_update":
                    await self.install_application_update(update)
                elif update_type == "feature_update":
                    await self.install_new_feature(update)
                elif update_type == "security_patch":
                    await self.install_security_patch(update)
                
                self.deployment_metrics["updates_installed"] += 1
                print(f"✅ Installed {update['name']}")
                
            except Exception as e:
                print(f"❌ Failed to install {update['name']}: {e}")
                # Create recovery deployment
                await self.create_recovery_deployment(update, str(e))
    
    async def install_system_update(self, update: Dict):
        """Install system-level updates"""
        print(f"🔧 Installing system update: {update['name']}")
        
        # Download update
        download_path = await self.download_manager.download_update(update)
        
        # Create system backup
        backup_id = await self.create_system_backup()
        
        try:
            # Apply update
            await self.installer.install_system_update(download_path, update)
            
            # Verify installation
            if await self.verify_system_update(update):
                print(f"✅ System update successful: {update['name']}")
                await self.cleanup_update_files(download_path)
            else:
                raise Exception("System update verification failed")
                
        except Exception as e:
            print(f"❌ System update failed: {e}")
            await self.rollback_to_backup(backup_id)
            raise
    
    async def install_dependency_update(self, update: Dict):
        """Install dependency updates"""
        print(f"📚 Installing dependency: {update['name']}")
        
        try:
            # Install using appropriate package manager
            if update.get("package_manager") == "pip":
                await self.installer.install_pip_package(update)
            elif update.get("package_manager") == "npm":
                await self.installer.install_npm_package(update)
            elif update.get("package_manager") == "conda":
                await self.installer.install_conda_package(update)
            else:
                await self.installer.install_generic_package(update)
            
            # Test dependency
            if await self.test_dependency(update):
                print(f"✅ Dependency installed: {update['name']}")
            else:
                raise Exception("Dependency test failed")
                
        except Exception as e:
            print(f"❌ Dependency installation failed: {e}")
            await self.rollback_dependency(update)
            raise
    
    async def install_application_update(self, update: Dict):
        """Install application updates"""
        print(f"🚀 Installing application update: {update['name']}")
        
        # Download application files
        download_path = await self.download_manager.download_application_update(update)
        
        # Create application backup
        backup_id = await self.create_application_backup()
        
        try:
            # Deploy to staging first
            staging_deployment = await self.deploy_to_staging(download_path, update)
            
            # Test staging deployment
            if await self.test_staging_deployment(staging_deployment):
                # Deploy to production
                await self.deploy_to_production(staging_deployment)
                print(f"✅ Application update deployed: {update['name']}")
            else:
                raise Exception("Staging deployment test failed")
                
        except Exception as e:
            print(f"❌ Application update failed: {e}")
            await self.rollback_to_backup(backup_id)
            raise
    
    async def install_new_feature(self, feature: Dict):
        """Install newly discovered features"""
        print(f"🌟 Installing new feature: {feature['name']}")
        
        try:
            # Download feature
            feature_path = await self.download_manager.download_feature(feature)
            
            # Analyze feature requirements
            requirements = await self.analyze_feature_requirements(feature_path)
            
            # Install requirements first
            for req in requirements:
                await self.install_dependency_update(req)
            
            # Install feature
            await self.installer.install_feature(feature_path, feature)
            
            # Test feature
            if await self.test_new_feature(feature):
                print(f"✅ New feature installed: {feature['name']}")
                await self.enable_feature(feature)
            else:
                raise Exception("Feature test failed")
                
        except Exception as e:
            print(f"❌ Feature installation failed: {e}")
            await self.disable_feature(feature)
            raise
    
    async def execute_deployment(self, deployment: Dict):
        """Execute a complete deployment"""
        deployment_id = deployment["id"]
        self.active_deployments[deployment_id] = deployment
        
        try:
            print(f"🚀 Starting deployment: {deployment['name']}")
            
            # Pre-deployment checks
            await self.pre_deployment_checks(deployment)
            
            # Execute deployment steps
            for step in deployment["steps"]:
                await self.execute_deployment_step(deployment_id, step)
            
            # Post-deployment verification
            await self.post_deployment_verification(deployment)
            
            # Mark as successful
            deployment["status"] = "completed"
            deployment["completed_at"] = datetime.now().isoformat()
            
            self.deployment_metrics["successful_deployments"] += 1
            print(f"✅ Deployment completed: {deployment['name']}")
            
        except Exception as e:
            print(f"❌ Deployment failed: {deployment['name']} - {e}")
            deployment["status"] = "failed"
            deployment["error"] = str(e)
            
            self.deployment_metrics["failed_deployments"] += 1
            
            # Attempt automatic rollback
            await self.rollback_deployment(deployment_id)
        
        finally:
            # Clean up
            if deployment_id in self.active_deployments:
                del self.active_deployments[deployment_id]
    
    async def rollback_deployment(self, deployment_id: str):
        """Rollback a failed deployment"""
        print(f"🔄 Rolling back deployment: {deployment_id}")
        
        try:
            deployment = self.active_deployments.get(deployment_id)
            if not deployment:
                return
            
            # Execute rollback steps
            rollback_steps = deployment.get("rollback_steps", [])
            
            for step in reversed(rollback_steps):
                await self.execute_rollback_step(deployment_id, step)
            
            # Restore from backup if available
            backup_id = deployment.get("backup_id")
            if backup_id:
                await self.restore_from_backup(backup_id)
            
            self.deployment_metrics["rollbacks_performed"] += 1
            print(f"✅ Rollback completed: {deployment_id}")
            
        except Exception as e:
            print(f"❌ Rollback failed: {deployment_id} - {e}")
            # Escalate to emergency recovery
            await self.emergency_recovery(deployment_id)
    
    def load_configuration(self) -> Dict:
        """Load deployment configuration"""
        config_file = "config/deployment_config.json"
        
        default_config = {
            "update_sources": [
                "https://api.github.com/repos",
                "https://pypi.org/pypi",
                "https://registry.npmjs.org",
                "https://conda.anaconda.org"
            ],
            "deployment_environments": [
                "development",
                "staging", 
                "production"
            ],
            "auto_deploy_enabled": True,
            "rollback_enabled": True,
            "health_check_interval": 120,
            "backup_retention_days": 30
        }
        
        if Path(config_file).exists():
            try:
                with open(config_file, 'r') as f:
                    return json.load(f)
            except:
                pass
        
        # Save default config
        Path(config_file).parent.mkdir(parents=True, exist_ok=True)
        with open(config_file, 'w') as f:
            json.dump(default_config, f, indent=2)
        
        return default_config

class UpdateManager:
    """Manages discovery and validation of updates"""
    
    def __init__(self):
        self.update_sources = []
        self.update_cache = {}
    
    def check_system_updates(self) -> List[Dict]:
        """Check for system-level updates"""
        updates = []
        
        try:
            # Check Git repository for updates
            if self.check_git_updates():
                updates.append({
                    "type": "system_update",
                    "name": "System Core Update",
                    "source": "git",
                    "version": "latest",
                    "download_url": self.get_git_update_url(),
                    "priority": "high"
                })
            
            # Check for Python environment updates
            python_updates = self.check_python_updates()
            updates.extend(python_updates)
            
        except Exception as e:
            print(f"❌ System update check error: {e}")
        
        return updates
    
    def check_dependency_updates(self) -> List[Dict]:
        """Check for dependency updates"""
        updates = []
        
        try:
            # Check pip packages
            pip_updates = self.check_pip_updates()
            updates.extend(pip_updates)
            
            # Check npm packages if available
            if Path("package.json").exists():
                npm_updates = self.check_npm_updates()
                updates.extend(npm_updates)
            
            # Check conda packages if available
            if self.is_conda_environment():
                conda_updates = self.check_conda_updates()
                updates.extend(conda_updates)
                
        except Exception as e:
            print(f"❌ Dependency update check error: {e}")
        
        return updates
    
    def check_application_updates(self) -> List[Dict]:
        """Check for application updates"""
        updates = []
        
        try:
            # Check main application version
            current_version = self.get_current_app_version()
            latest_version = self.get_latest_app_version()
            
            if self.is_newer_version(latest_version, current_version):
                updates.append({
                    "type": "application_update",
                    "name": "Main Application",
                    "current_version": current_version,
                    "latest_version": latest_version,
                    "download_url": self.get_app_download_url(latest_version),
                    "priority": "medium"
                })
                
        except Exception as e:
            print(f"❌ Application update check error: {e}")
        
        return updates
    
    def discover_new_features(self) -> List[Dict]:
        """Discover new features and modules"""
        features = []
        
        try:
            # Check feature repositories
            feature_repos = [
                "https://api.github.com/repos/username/ai-features",
                "https://api.github.com/repos/username/agent-plugins"
            ]
            
            for repo_url in feature_repos:
                repo_features = self.scan_feature_repository(repo_url)
                features.extend(repo_features)
                
        except Exception as e:
            print(f"❌ Feature discovery error: {e}")
        
        return features
    
    def check_git_updates(self) -> bool:
        """Check if Git repository has updates"""
        try:
            repo = git.Repo(".")
            origin = repo.remotes.origin
            origin.fetch()
            
            commits_behind = list(repo.iter_commits('HEAD..origin/main'))
            return len(commits_behind) > 0
            
        except:
            return False
    
    def check_pip_updates(self) -> List[Dict]:
        """Check for pip package updates"""
        updates = []
        
        try:
            # Get outdated packages
            result = subprocess.run(
                [sys.executable, "-m", "pip", "list", "--outdated", "--format=json"],
                capture_output=True, text=True
            )
            
            if result.returncode == 0:
                outdated = json.loads(result.stdout)
                
                for package in outdated:
                    updates.append({
                        "type": "dependency_update",
                        "name": package["name"],
                        "current_version": package["version"],
                        "latest_version": package["latest_version"],
                        "package_manager": "pip",
                        "priority": "low"
                    })
                    
        except Exception as e:
            print(f"❌ Pip update check error: {e}")
        
        return updates

class DeploymentManager:
    """Manages deployment processes"""
    
    def __init__(self):
        self.deployment_strategies = {
            "blue_green": self.blue_green_deployment,
            "rolling": self.rolling_deployment,
            "canary": self.canary_deployment,
            "immediate": self.immediate_deployment
        }
    
    async def blue_green_deployment(self, deployment: Dict):
        """Blue-Green deployment strategy"""
        print("🔵🟢 Executing Blue-Green deployment...")
        
        # Deploy to green environment
        green_env = await self.deploy_to_green_environment(deployment)
        
        # Test green environment
        if await self.test_environment(green_env):
            # Switch traffic to green
            await self.switch_traffic_to_green(green_env)
            
            # Cleanup blue environment
            await self.cleanup_blue_environment()
        else:
            # Keep blue active, cleanup green
            await self.cleanup_green_environment(green_env)
            raise Exception("Green environment test failed")
    
    async def rolling_deployment(self, deployment: Dict):
        """Rolling deployment strategy"""
        print("🔄 Executing Rolling deployment...")
        
        instances = await self.get_application_instances()
        
        for instance in instances:
            # Update instance
            await self.update_instance(instance, deployment)
            
            # Test instance
            if not await self.test_instance(instance):
                # Rollback instance
                await self.rollback_instance(instance)
                raise Exception(f"Instance {instance} update failed")
            
            # Wait before next instance
            await asyncio.sleep(30)
    
    async def canary_deployment(self, deployment: Dict):
        """Canary deployment strategy"""
        print("🐤 Executing Canary deployment...")
        
        # Deploy to small subset (5%)
        canary_instances = await self.deploy_to_canary(deployment, percentage=5)
        
        # Monitor canary for issues
        await asyncio.sleep(300)  # 5 minutes
        
        if await self.canary_health_check(canary_instances):
            # Gradually increase traffic
            await self.increase_canary_traffic(canary_instances, 25)
            await asyncio.sleep(300)
            
            if await self.canary_health_check(canary_instances):
                # Full deployment
                await self.complete_canary_deployment(canary_instances)
            else:
                await self.rollback_canary(canary_instances)
        else:
            await self.rollback_canary(canary_instances)

class DownloadManager:
    """Manages all download operations"""
    
    def __init__(self):
        self.download_cache = {}
        self.concurrent_downloads = 5
    
    async def download_update(self, update: Dict) -> str:
        """Download update files"""
        download_url = update["download_url"]
        filename = self.get_filename_from_url(download_url)
        download_path = f"deployments/downloads/{filename}"
        
        # Check cache first
        if self.is_cached(download_url):
            cached_path = self.get_cached_path(download_url)
            if await self.verify_download(cached_path, update):
                return cached_path
        
        print(f"📥 Downloading: {filename}")
        
        async with aiohttp.ClientSession() as session:
            async with session.get(download_url) as response:
                if response.status == 200:
                    async with aiofiles.open(download_path, 'wb') as f:
                        async for chunk in response.content.iter_chunked(8192):
                            await f.write(chunk)
                    
                    # Verify download
                    if await self.verify_download(download_path, update):
                        # Cache the download
                        self.cache_download(download_url, download_path)
                        print(f"✅ Downloaded: {filename}")
                        return download_path
                    else:
                        raise Exception("Download verification failed")
                else:
                    raise Exception(f"Download failed: HTTP {response.status}")
    
    async def download_application_update(self, update: Dict) -> str:
        """Download application update"""
        return await self.download_update(update)
    
    async def download_feature(self, feature: Dict) -> str:
        """Download new feature"""
        return await self.download_update(feature)
    
    def get_filename_from_url(self, url: str) -> str:
        """Extract filename from URL"""
        return url.split("/")[-1] or f"download_{int(time.time())}"
    
    async def verify_download(self, file_path: str, update: Dict) -> bool:
        """Verify downloaded file integrity"""
        if not Path(file_path).exists():
            return False
        
        # Check file size
        expected_size = update.get("file_size")
        if expected_size:
            actual_size = Path(file_path).stat().st_size
            if actual_size != expected_size:
                return False
        
        # Check checksum
        expected_hash = update.get("checksum")
        if expected_hash:
            actual_hash = await self.calculate_file_hash(file_path)
            if actual_hash != expected_hash:
                return False
        
        return True
    
    async def calculate_file_hash(self, file_path: str) -> str:
        """Calculate file SHA256 hash"""
        sha256_hash = hashlib.sha256()
        
        async with aiofiles.open(file_path, 'rb') as f:
            async for chunk in f:
                sha256_hash.update(chunk)
        
        return sha256_hash.hexdigest()

class AutoInstaller:
    """Handles automatic installation of updates"""
    
    def __init__(self):
        self.installation_strategies = {}
    
    async def install_system_update(self, update_path: str, update: Dict):
        """Install system update"""
        print(f"🔧 Installing system update from: {update_path}")
        
        # Extract update if compressed
        extracted_path = await self.extract_if_compressed(update_path)
        
        # Apply update based on type
        update_type = update.get("update_type", "files")
        
        if update_type == "files":
            await self.install_file_update(extracted_path, update)
        elif update_type == "script":
            await self.run_update_script(extracted_path, update)
        elif update_type == "binary":
            await self.install_binary_update(extracted_path, update)
    
    async def install_pip_package(self, package: Dict):
        """Install pip package"""
        package_name = package["name"]
        version = package.get("latest_version", "")
        
        cmd = [sys.executable, "-m", "pip", "install", "--upgrade"]
        
        if version:
            cmd.append(f"{package_name}=={version}")
        else:
            cmd.append(package_name)
        
        result = await self.run_command(cmd)
        
        if result.returncode != 0:
            raise Exception(f"Pip installation failed: {result.stderr}")
    
    async def install_npm_package(self, package: Dict):
        """Install npm package"""
        package_name = package["name"]
        version = package.get("latest_version", "latest")
        
        cmd = ["npm", "install", f"{package_name}@{version}"]
        
        result = await self.run_command(cmd)
        
        if result.returncode != 0:
            raise Exception(f"NPM installation failed: {result.stderr}")
    
    async def install_feature(self, feature_path: str, feature: Dict):
        """Install new feature"""
        print(f"🌟 Installing feature: {feature['name']}")
        
        # Extract feature files
        extracted_path = await self.extract_if_compressed(feature_path)
        
        # Install feature files
        feature_dir = f"features/{feature['name']}"
        Path(feature_dir).mkdir(parents=True, exist_ok=True)
        
        # Copy feature files
        if Path(extracted_path).is_dir():
            shutil.copytree(extracted_path, feature_dir, dirs_exist_ok=True)
        else:
            shutil.copy2(extracted_path, feature_dir)
        
        # Run feature installation script if available
        install_script = Path(feature_dir) / "install.py"
        if install_script.exists():
            await self.run_feature_install_script(install_script, feature)
    
    async def run_command(self, cmd: List[str]) -> subprocess.CompletedProcess:
        """Run system command asynchronously"""
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        stdout, stderr = await process.communicate()
        
        return subprocess.CompletedProcess(
            cmd, process.returncode, stdout, stderr
        )

class DeploymentHealthMonitor:
    """Monitors deployment health and performance"""
    
    def __init__(self):
        self.health_checks = {}
        self.performance_baselines = {}
    
    def check_deployment_health(self, deployment: Dict) -> Dict:
        """Check deployment health"""
        health_status = {
            "status": "healthy",
            "issues": [],
            "performance": {},
            "timestamp": datetime.now().isoformat()
        }
        
        try:
            # Check system resources
            resource_health = self.check_resource_health()
            if resource_health["status"] != "healthy":
                health_status["status"] = "degraded"
                health_status["issues"].extend(resource_health["issues"])
            
            # Check application endpoints
            endpoint_health = self.check_endpoint_health(deployment)
            if endpoint_health["status"] != "healthy":
                health_status["status"] = "degraded"
                health_status["issues"].extend(endpoint_health["issues"])
            
            # Check error rates
            error_health = self.check_error_rates(deployment)
            if error_health["status"] != "healthy":
                health_status["status"] = "failed" if error_health["critical"] else "degraded"
                health_status["issues"].extend(error_health["issues"])
            
        except Exception as e:
            health_status["status"] = "failed"
            health_status["issues"].append(f"Health check error: {e}")
        
        return health_status
    
    def check_resource_health(self) -> Dict:
        """Check system resource health"""
        import psutil
        
        cpu_usage = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        issues = []
        status = "healthy"
        
        if cpu_usage > 90:
            issues.append(f"High CPU usage: {cpu_usage}%")
            status = "degraded"
        
        if memory.percent > 90:
            issues.append(f"High memory usage: {memory.percent}%")
            status = "degraded"
        
        if disk.percent > 95:
            issues.append(f"High disk usage: {disk.percent}%")
            status = "degraded"
        
        return {
            "status": status,
            "issues": issues,
            "metrics": {
                "cpu_usage": cpu_usage,
                "memory_usage": memory.percent,
                "disk_usage": disk.percent
            }
        }
    
    def check_endpoint_health(self, deployment: Dict) -> Dict:
        """Check application endpoint health"""
        # Placeholder for endpoint health checking
        return {
            "status": "healthy",
            "issues": []
        }
    
    def check_error_rates(self, deployment: Dict) -> Dict:
        """Check application error rates"""
        # Placeholder for error rate checking
        return {
            "status": "healthy",
            "issues": [],
            "critical": False
        }

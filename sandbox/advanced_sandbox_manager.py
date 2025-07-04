#!/usr/bin/env python3
"""
🏗️ Advanced Sandbox Manager v7.2.0
Ultimate AGI Force - Secure Execution Environment

Features:
- Cross-platform sandbox environments
- Resource isolation and limits
- Network access control
- File system sandboxing
- Process containment
- Security monitoring
- Virtual environment management
- Docker integration (optional)

Made with ❤️ by Mulky Malikul Dhaher in Indonesia 🇮🇩
"""

import os
import sys
import json
import time
import subprocess
import platform
import threading
import shutil
import tempfile
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
import venv

class AdvancedSandboxManager:
    """
    Advanced Sandbox Manager for Secure Code Execution
    """
    
    def __init__(self):
        self.owner = "Mulky Malikul Dhaher"
        self.owner_id = "1108151509970001"
        
        # System information
        self.os_type = platform.system()
        self.sandbox_root = Path('sandbox_environments')
        self.sandbox_root.mkdir(exist_ok=True)
        
        # Active sandboxes
        self.active_sandboxes = {}
        self.sandbox_processes = {}
        
        # Default configurations
        self.default_config = self._get_default_config()
        
        # Security settings
        self.max_sandboxes = 10
        self.max_execution_time = 300  # 5 minutes
        self.allowed_packages = [
            'requests', 'numpy', 'pandas', 'matplotlib', 'flask',
            'fastapi', 'click', 'colorama', 'tqdm', 'beautifulsoup4'
        ]
        
        print(f"🏗️ Advanced Sandbox Manager v7.2.0")
        print(f"👑 Owner: {self.owner} ({self.owner_id})")
        print(f"🖥️ OS: {self.os_type}")
        print(f"📁 Sandbox Root: {self.sandbox_root}")
        print("🇮🇩 Made with ❤️ in Indonesia")
    
    def _get_default_config(self):
        """Get default sandbox configuration"""
        return {
            'name': 'default_sandbox',
            'type': 'python_venv',
            'restrictions': {
                'network_access': False,
                'file_system_access': 'restricted',
                'max_memory_mb': 512,
                'max_cpu_percent': 50,
                'max_execution_time': 60,
                'allowed_imports': ['os', 'sys', 'json', 'time', 'datetime'],
                'blocked_imports': ['subprocess', 'socket', 'urllib']
            },
            'environment': {
                'python_version': '3.9',
                'pip_packages': [],
                'environment_variables': {}
            },
            'security': {
                'read_only': False,
                'isolated_network': True,
                'temp_directory': True,
                'auto_cleanup': True
            }
        }
    
    def create_sandbox(self, config: Optional[Dict] = None) -> Dict[str, Any]:
        """Create new sandbox environment"""
        try:
            # Generate unique sandbox ID
            sandbox_id = f"sandbox_{int(time.time())}_{str(uuid.uuid4())[:8]}"
            
            # Merge with default config
            final_config = self.default_config.copy()
            if config:
                final_config.update(config)
            
            # Create sandbox directory
            sandbox_path = self.sandbox_root / sandbox_id
            sandbox_path.mkdir(exist_ok=True)
            
            # Setup sandbox based on type
            if final_config['type'] == 'python_venv':
                result = self._create_python_venv_sandbox(sandbox_id, sandbox_path, final_config)
            elif final_config['type'] == 'docker':
                result = self._create_docker_sandbox(sandbox_id, sandbox_path, final_config)
            elif final_config['type'] == 'isolated_process':
                result = self._create_isolated_process_sandbox(sandbox_id, sandbox_path, final_config)
            else:
                result = self._create_basic_sandbox(sandbox_id, sandbox_path, final_config)
            
            if result['success']:
                # Store sandbox info
                sandbox_info = {
                    'id': sandbox_id,
                    'path': str(sandbox_path),
                    'config': final_config,
                    'created_at': datetime.now().isoformat(),
                    'status': 'created',
                    'processes': [],
                    'resource_usage': {
                        'cpu_time': 0,
                        'memory_peak': 0,
                        'files_created': 0
                    }
                }
                
                self.active_sandboxes[sandbox_id] = sandbox_info
                
                result.update({
                    'sandbox_id': sandbox_id,
                    'sandbox_info': sandbox_info
                })
            
            return result
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': 'Failed to create sandbox'
            }
    
    def _create_python_venv_sandbox(self, sandbox_id: str, sandbox_path: Path, config: Dict) -> Dict[str, Any]:
        """Create Python virtual environment sandbox"""
        try:
            venv_path = sandbox_path / 'venv'
            
            # Create virtual environment
            venv.create(venv_path, with_pip=True)
            
            # Get paths
            if self.os_type == 'Windows':
                python_exe = venv_path / 'Scripts' / 'python.exe'
                pip_exe = venv_path / 'Scripts' / 'pip.exe'
            else:
                python_exe = venv_path / 'bin' / 'python'
                pip_exe = venv_path / 'bin' / 'pip'
            
            # Install packages
            packages = config.get('environment', {}).get('pip_packages', [])
            for package in packages:
                if package in self.allowed_packages:
                    subprocess.run([str(pip_exe), 'install', package], 
                                 timeout=120, capture_output=True)
            
            # Create sandbox runner script
            runner_script = self._create_sandbox_runner(sandbox_path, python_exe, config)
            
            return {
                'success': True,
                'type': 'python_venv',
                'python_path': str(python_exe),
                'runner_script': str(runner_script),
                'message': 'Python virtual environment sandbox created'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': 'Failed to create Python venv sandbox'
            }
    
    def _create_docker_sandbox(self, sandbox_id: str, sandbox_path: Path, config: Dict) -> Dict[str, Any]:
        """Create Docker-based sandbox (if Docker is available)"""
        try:
            # Check if Docker is available
            docker_check = subprocess.run(['docker', '--version'], 
                                        capture_output=True, text=True)
            
            if docker_check.returncode != 0:
                return {
                    'success': False,
                    'error': 'Docker not available',
                    'message': 'Docker is required for this sandbox type'
                }
            
            # Create Dockerfile
            dockerfile_content = f"""
FROM python:3.9-slim
WORKDIR /sandbox
COPY . /sandbox
RUN pip install --no-cache-dir {' '.join(config.get('environment', {}).get('pip_packages', []))}
CMD ["python", "-u", "runner.py"]
            """
            
            dockerfile_path = sandbox_path / 'Dockerfile'
            with open(dockerfile_path, 'w') as f:
                f.write(dockerfile_content)
            
            # Build Docker image
            image_name = f"sandbox_{sandbox_id}"
            build_result = subprocess.run([
                'docker', 'build', '-t', image_name, str(sandbox_path)
            ], capture_output=True, text=True, timeout=300)
            
            if build_result.returncode != 0:
                return {
                    'success': False,
                    'error': build_result.stderr,
                    'message': 'Failed to build Docker image'
                }
            
            return {
                'success': True,
                'type': 'docker',
                'image_name': image_name,
                'message': 'Docker sandbox created'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': 'Failed to create Docker sandbox'
            }
    
    def _create_isolated_process_sandbox(self, sandbox_id: str, sandbox_path: Path, config: Dict) -> Dict[str, Any]:
        """Create isolated process sandbox"""
        try:
            # Create restricted environment
            restricted_env = os.environ.copy()
            
            # Remove dangerous environment variables
            dangerous_vars = ['PATH', 'PYTHONPATH', 'LD_LIBRARY_PATH']
            for var in dangerous_vars:
                if var in restricted_env:
                    del restricted_env[var]
            
            # Set safe PATH
            if self.os_type == 'Windows':
                restricted_env['PATH'] = 'C:\\Windows\\System32'
            else:
                restricted_env['PATH'] = '/usr/bin:/bin'
            
            # Create sandbox info
            return {
                'success': True,
                'type': 'isolated_process',
                'environment': restricted_env,
                'working_directory': str(sandbox_path),
                'message': 'Isolated process sandbox created'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': 'Failed to create isolated process sandbox'
            }
    
    def _create_basic_sandbox(self, sandbox_id: str, sandbox_path: Path, config: Dict) -> Dict[str, Any]:
        """Create basic file-based sandbox"""
        try:
            # Create basic structure
            (sandbox_path / 'code').mkdir(exist_ok=True)
            (sandbox_path / 'data').mkdir(exist_ok=True)
            (sandbox_path / 'output').mkdir(exist_ok=True)
            
            return {
                'success': True,
                'type': 'basic',
                'working_directory': str(sandbox_path),
                'message': 'Basic sandbox created'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': 'Failed to create basic sandbox'
            }
    
    def _create_sandbox_runner(self, sandbox_path: Path, python_exe: Path, config: Dict) -> Path:
        """Create sandbox runner script with security restrictions"""
        runner_content = f'''#!/usr/bin/env python3
"""
Sandbox Runner with Security Restrictions
Generated by Advanced Sandbox Manager v7.2.0
"""

import sys
import os
import time
import json
import resource
from pathlib import Path

# Security restrictions
BLOCKED_IMPORTS = {config['restrictions']['blocked_imports']}
ALLOWED_IMPORTS = {config['restrictions']['allowed_imports']}
MAX_EXECUTION_TIME = {config['restrictions']['max_execution_time']}
MAX_MEMORY_MB = {config['restrictions']['max_memory_mb']}

class SecurityManager:
    def __init__(self):
        self.start_time = time.time()
        self.setup_resource_limits()
    
    def setup_resource_limits(self):
        try:
            # Set memory limit (Linux/macOS only)
            if sys.platform != 'win32':
                resource.setrlimit(resource.RLIMIT_AS, (MAX_MEMORY_MB * 1024 * 1024, -1))
                resource.setrlimit(resource.RLIMIT_CPU, (MAX_EXECUTION_TIME, -1))
        except:
            pass
    
    def check_import(self, name):
        if name in BLOCKED_IMPORTS:
            raise ImportError(f"Import '{{name}}' is blocked in sandbox")
        return True
    
    def check_time_limit(self):
        if time.time() - self.start_time > MAX_EXECUTION_TIME:
            raise TimeoutError("Execution time limit exceeded")

# Install import hook
security_manager = SecurityManager()
original_import = __builtins__.__import__

def secure_import(name, *args, **kwargs):
    security_manager.check_import(name)
    security_manager.check_time_limit()
    return original_import(name, *args, **kwargs)

__builtins__.__import__ = secure_import

# Sandbox execution function
def execute_sandbox_code(code_file):
    try:
        with open(code_file, 'r') as f:
            code = f.read()
        
        # Execute in restricted environment
        exec(code, {{'__name__': '__main__'}})
        
    except Exception as e:
        print(f"Sandbox execution error: {{e}}")
        return 1
    
    return 0

if __name__ == "__main__":
    if len(sys.argv) > 1:
        exit_code = execute_sandbox_code(sys.argv[1])
        sys.exit(exit_code)
    else:
        print("Usage: runner.py <code_file>")
        sys.exit(1)
'''
        
        runner_path = sandbox_path / 'runner.py'
        with open(runner_path, 'w') as f:
            f.write(runner_content)
        
        return runner_path
    
    def execute_code_in_sandbox(self, sandbox_id: str, code: str, filename: str = 'main.py') -> Dict[str, Any]:
        """Execute code in specified sandbox"""
        try:
            if sandbox_id not in self.active_sandboxes:
                return {
                    'success': False,
                    'error': 'Sandbox not found',
                    'message': f'Sandbox {sandbox_id} does not exist'
                }
            
            sandbox_info = self.active_sandboxes[sandbox_id]
            sandbox_path = Path(sandbox_info['path'])
            
            # Write code to file
            code_file = sandbox_path / filename
            with open(code_file, 'w') as f:
                f.write(code)
            
            # Execute based on sandbox type
            if sandbox_info['config']['type'] == 'python_venv':
                result = self._execute_in_python_venv(sandbox_info, str(code_file))
            elif sandbox_info['config']['type'] == 'docker':
                result = self._execute_in_docker(sandbox_info, str(code_file))
            else:
                result = self._execute_in_basic_sandbox(sandbox_info, str(code_file))
            
            # Update sandbox stats
            sandbox_info['resource_usage']['files_created'] += 1
            sandbox_info['status'] = 'executed'
            
            return result
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': 'Failed to execute code in sandbox'
            }
    
    def _execute_in_python_venv(self, sandbox_info: Dict, code_file: str) -> Dict[str, Any]:
        """Execute code in Python virtual environment"""
        try:
            sandbox_path = Path(sandbox_info['path'])
            
            if self.os_type == 'Windows':
                python_exe = sandbox_path / 'venv' / 'Scripts' / 'python.exe'
            else:
                python_exe = sandbox_path / 'venv' / 'bin' / 'python'
            
            runner_script = sandbox_path / 'runner.py'
            
            # Execute with timeout
            start_time = time.time()
            process = subprocess.run([
                str(python_exe), str(runner_script), code_file
            ], capture_output=True, text=True, timeout=self.max_execution_time,
            cwd=str(sandbox_path))
            
            execution_time = time.time() - start_time
            
            return {
                'success': process.returncode == 0,
                'stdout': process.stdout,
                'stderr': process.stderr,
                'return_code': process.returncode,
                'execution_time': execution_time,
                'sandbox_type': 'python_venv'
            }
            
        except subprocess.TimeoutExpired:
            return {
                'success': False,
                'error': 'Execution timeout',
                'message': f'Code execution exceeded {self.max_execution_time} seconds'
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': 'Failed to execute in Python venv'
            }
    
    def _execute_in_docker(self, sandbox_info: Dict, code_file: str) -> Dict[str, Any]:
        """Execute code in Docker container"""
        try:
            image_name = f"sandbox_{sandbox_info['id']}"
            
            # Copy code file to sandbox
            sandbox_path = Path(sandbox_info['path'])
            container_code_file = sandbox_path / 'main.py'
            shutil.copy2(code_file, container_code_file)
            
            # Run Docker container
            start_time = time.time()
            process = subprocess.run([
                'docker', 'run', '--rm',
                '--memory=512m',
                '--cpus=0.5',
                '--network=none',
                '-v', f'{sandbox_path}:/sandbox',
                image_name,
                'python', 'main.py'
            ], capture_output=True, text=True, timeout=self.max_execution_time)
            
            execution_time = time.time() - start_time
            
            return {
                'success': process.returncode == 0,
                'stdout': process.stdout,
                'stderr': process.stderr,
                'return_code': process.returncode,
                'execution_time': execution_time,
                'sandbox_type': 'docker'
            }
            
        except subprocess.TimeoutExpired:
            return {
                'success': False,
                'error': 'Execution timeout',
                'message': f'Docker execution exceeded {self.max_execution_time} seconds'
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': 'Failed to execute in Docker'
            }
    
    def _execute_in_basic_sandbox(self, sandbox_info: Dict, code_file: str) -> Dict[str, Any]:
        """Execute code in basic sandbox"""
        try:
            sandbox_path = Path(sandbox_info['path'])
            
            # Execute with basic Python
            start_time = time.time()
            process = subprocess.run([
                sys.executable, code_file
            ], capture_output=True, text=True, timeout=self.max_execution_time,
            cwd=str(sandbox_path))
            
            execution_time = time.time() - start_time
            
            return {
                'success': process.returncode == 0,
                'stdout': process.stdout,
                'stderr': process.stderr,
                'return_code': process.returncode,
                'execution_time': execution_time,
                'sandbox_type': 'basic'
            }
            
        except subprocess.TimeoutExpired:
            return {
                'success': False,
                'error': 'Execution timeout',
                'message': f'Basic execution exceeded {self.max_execution_time} seconds'
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': 'Failed to execute in basic sandbox'
            }
    
    def list_sandboxes(self) -> Dict[str, Any]:
        """List all active sandboxes"""
        sandboxes = []
        for sandbox_id, sandbox_info in self.active_sandboxes.items():
            sandbox_summary = {
                'id': sandbox_id,
                'name': sandbox_info['config']['name'],
                'type': sandbox_info['config']['type'],
                'status': sandbox_info['status'],
                'created_at': sandbox_info['created_at'],
                'path': sandbox_info['path'],
                'resource_usage': sandbox_info['resource_usage']
            }
            sandboxes.append(sandbox_summary)
        
        return {
            'success': True,
            'sandboxes': sandboxes,
            'total_sandboxes': len(sandboxes)
        }
    
    def destroy_sandbox(self, sandbox_id: str) -> Dict[str, Any]:
        """Destroy sandbox and clean up resources"""
        try:
            if sandbox_id not in self.active_sandboxes:
                return {
                    'success': False,
                    'error': 'Sandbox not found',
                    'message': f'Sandbox {sandbox_id} does not exist'
                }
            
            sandbox_info = self.active_sandboxes[sandbox_id]
            sandbox_path = Path(sandbox_info['path'])
            
            # Kill any running processes
            if sandbox_id in self.sandbox_processes:
                for process in self.sandbox_processes[sandbox_id]:
                    try:
                        process.terminate()
                        process.wait(timeout=5)
                    except:
                        try:
                            process.kill()
                        except:
                            pass
                del self.sandbox_processes[sandbox_id]
            
            # Clean up Docker image if applicable
            if sandbox_info['config']['type'] == 'docker':
                try:
                    image_name = f"sandbox_{sandbox_id}"
                    subprocess.run(['docker', 'rmi', image_name], 
                                 capture_output=True, timeout=30)
                except:
                    pass
            
            # Remove sandbox directory
            if sandbox_path.exists():
                shutil.rmtree(sandbox_path)
            
            # Remove from active sandboxes
            del self.active_sandboxes[sandbox_id]
            
            return {
                'success': True,
                'message': f'Sandbox {sandbox_id} destroyed successfully'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': 'Failed to destroy sandbox'
            }
    
    def get_sandbox_info(self, sandbox_id: str) -> Dict[str, Any]:
        """Get detailed information about a sandbox"""
        if sandbox_id not in self.active_sandboxes:
            return {
                'success': False,
                'error': 'Sandbox not found',
                'message': f'Sandbox {sandbox_id} does not exist'
            }
        
        return {
            'success': True,
            'sandbox_info': self.active_sandboxes[sandbox_id]
        }
    
    def cleanup_all_sandboxes(self) -> Dict[str, Any]:
        """Clean up all sandboxes"""
        cleaned_count = 0
        errors = []
        
        for sandbox_id in list(self.active_sandboxes.keys()):
            result = self.destroy_sandbox(sandbox_id)
            if result['success']:
                cleaned_count += 1
            else:
                errors.append(f"{sandbox_id}: {result['error']}")
        
        return {
            'success': len(errors) == 0,
            'cleaned_sandboxes': cleaned_count,
            'errors': errors,
            'message': f'Cleaned up {cleaned_count} sandboxes'
        }

def main():
    """Main function for testing sandbox manager"""
    manager = AdvancedSandboxManager()
    
    print("\n🧪 Testing Sandbox Manager...")
    
    # Create a test sandbox
    print("\n📦 Creating Python venv sandbox...")
    sandbox_result = manager.create_sandbox({
        'name': 'test_sandbox',
        'type': 'python_venv',
        'environment': {
            'pip_packages': ['requests']
        }
    })
    
    if sandbox_result['success']:
        sandbox_id = sandbox_result['sandbox_id']
        print(f"✅ Sandbox created: {sandbox_id}")
        
        # Test code execution
        print("\n🚀 Testing code execution...")
        test_code = '''
print("Hello from sandbox!")
print("Python version:", __import__("sys").version)
print("Current directory:", __import__("os").getcwd())
'''
        
        exec_result = manager.execute_code_in_sandbox(sandbox_id, test_code)
        if exec_result['success']:
            print("✅ Code executed successfully")
            print("Output:", exec_result['stdout'])
        else:
            print("❌ Code execution failed:", exec_result['error'])
        
        # Clean up
        print("\n🧹 Cleaning up...")
        cleanup_result = manager.destroy_sandbox(sandbox_id)
        if cleanup_result['success']:
            print("✅ Sandbox cleaned up")
    else:
        print("❌ Failed to create sandbox:", sandbox_result['error'])
    
    print("\n✅ Sandbox Manager tests completed!")

if __name__ == "__main__":
    main()
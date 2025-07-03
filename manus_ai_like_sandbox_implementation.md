# Implementasi AI Agent Seperti Manus AI dengan Sandbox Environment

## Arsitektur Sistem

### 1. Container Sandbox Architecture
```yaml
# docker-compose.yml
version: '3.8'
services:
  ai-agent:
    build: ./ai-agent
    volumes:
      - ./workspace:/workspace
      - ./logs:/logs
    environment:
      - DISPLAY=:99
      - VNC_PASSWD=password123
    ports:
      - "5900:5900"  # VNC
      - "6080:6080"  # noVNC web interface
      - "8000:8000"  # Agent API
    networks:
      - agent-network
    cap_drop:
      - ALL
    cap_add:
      - SYS_PTRACE  # Untuk debugging jika diperlukan
    security_opt:
      - no-new-privileges:true
    user: "1000:1000"

  agent-browser:
    build: ./browser-env
    volumes:
      - ./downloads:/downloads
    environment:
      - DISPLAY=:99
    networks:
      - agent-network
    depends_on:
      - ai-agent

networks:
  agent-network:
    driver: bridge
    ipam:
      config:
        - subnet: 172.20.0.0/16
```

### 2. AI Agent Core Implementation

#### Agent Controller
```python
# agent_controller.py
import asyncio
import docker
import subprocess
from typing import Dict, List, Any
import logging
from dataclasses import dataclass
from enum import Enum

class AgentStatus(Enum):
    IDLE = "idle"
    WORKING = "working"
    ERROR = "error"
    STOPPED = "stopped"

@dataclass
class Task:
    id: str
    type: str
    description: str
    parameters: Dict[str, Any]
    priority: int = 1

class ManusAIAgent:
    def __init__(self, agent_id: str, container_name: str):
        self.agent_id = agent_id
        self.container_name = container_name
        self.status = AgentStatus.IDLE
        self.current_task = None
        self.task_queue = asyncio.Queue()
        self.docker_client = docker.from_env()
        self.container = None
        self.logger = logging.getLogger(f"agent_{agent_id}")
        
        # Capabilities yang dimiliki agent
        self.capabilities = {
            "web_browsing": True,
            "file_operations": True,
            "code_execution": True,
            "image_processing": True,
            "data_analysis": True,
            "api_calls": True,
            "screen_capture": True,
            "keyboard_mouse_control": True
        }
        
    async def start_sandbox(self):
        """Memulai container sandbox untuk agent"""
        try:
            # Buat dan jalankan container
            self.container = self.docker_client.containers.run(
                "manus-ai-agent:latest",
                name=self.container_name,
                detach=True,
                volumes={
                    f'/workspace/{self.agent_id}': {'bind': '/workspace', 'mode': 'rw'},
                    '/tmp/.X11-unix': {'bind': '/tmp/.X11-unix', 'mode': 'rw'}
                },
                environment={
                    'DISPLAY': ':99',
                    'AGENT_ID': self.agent_id,
                    'PYTHONPATH': '/app'
                },
                ports={'5900/tcp': None, '8000/tcp': None},
                network='agent-network',
                user='1000:1000'
            )
            
            # Tunggu container siap
            await asyncio.sleep(5)
            
            # Setup virtual display
            await self.setup_virtual_display()
            
            self.logger.info(f"Sandbox started for agent {self.agent_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to start sandbox: {e}")
            return False
    
    async def setup_virtual_display(self):
        """Setup virtual display untuk GUI applications"""
        commands = [
            "Xvfb :99 -screen 0 1920x1080x24 &",
            "x11vnc -display :99 -nopw -listen localhost -xkb -ncache 10 -ncache_cr -forever &",
            "fluxbox -display :99 &"
        ]
        
        for cmd in commands:
            result = self.container.exec_run(cmd, detach=True)
            if result.exit_code != 0:
                self.logger.warning(f"Command failed: {cmd}")

    async def execute_task(self, task: Task):
        """Eksekusi task dalam sandbox"""
        self.status = AgentStatus.WORKING
        self.current_task = task
        
        try:
            result = await self._route_task(task)
            self.logger.info(f"Task {task.id} completed successfully")
            return result
            
        except Exception as e:
            self.logger.error(f"Task {task.id} failed: {e}")
            self.status = AgentStatus.ERROR
            raise
            
        finally:
            self.current_task = None
            self.status = AgentStatus.IDLE
    
    async def _route_task(self, task: Task):
        """Route task ke handler yang sesuai"""
        handlers = {
            "web_browse": self._handle_web_browsing,
            "file_operation": self._handle_file_operation,
            "code_execution": self._handle_code_execution,
            "data_analysis": self._handle_data_analysis,
            "screen_interaction": self._handle_screen_interaction,
            "api_call": self._handle_api_call
        }
        
        handler = handlers.get(task.type)
        if handler:
            return await handler(task)
        else:
            raise ValueError(f"Unknown task type: {task.type}")

    async def _handle_web_browsing(self, task: Task):
        """Handle web browsing tasks"""
        script = f"""
import asyncio
from playwright.async_api import async_playwright

async def browse_web():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        
        url = "{task.parameters.get('url', '')}"
        action = "{task.parameters.get('action', 'navigate')}"
        
        if action == "navigate":
            await page.goto(url)
            await page.wait_for_load_state('networkidle')
            
        elif action == "click":
            selector = "{task.parameters.get('selector', '')}"
            await page.click(selector)
            
        elif action == "type":
            selector = "{task.parameters.get('selector', '')}"
            text = "{task.parameters.get('text', '')}"
            await page.fill(selector, text)
            
        elif action == "extract":
            selector = "{task.parameters.get('selector', '')}"
            elements = await page.query_selector_all(selector)
            data = []
            for element in elements:
                text = await element.text_content()
                data.append(text)
            print(data)
            
        # Screenshot untuk monitoring
        await page.screenshot(path="/workspace/screenshots/latest.png")
        
        await browser.close()

asyncio.run(browse_web())
"""
        
        result = self.container.exec_run(
            f"python3 -c '{script}'",
            workdir="/workspace"
        )
        
        return {"status": "completed", "output": result.output.decode()}

    async def _handle_file_operation(self, task: Task):
        """Handle file operations"""
        operation = task.parameters.get('operation')
        file_path = task.parameters.get('file_path')
        
        if operation == "read":
            result = self.container.exec_run(f"cat {file_path}")
            return {"content": result.output.decode()}
            
        elif operation == "write":
            content = task.parameters.get('content', '')
            cmd = f"echo '{content}' > {file_path}"
            result = self.container.exec_run(cmd)
            return {"status": "written"}
            
        elif operation == "list":
            result = self.container.exec_run(f"ls -la {file_path}")
            return {"listing": result.output.decode()}

    async def _handle_code_execution(self, task: Task):
        """Handle code execution"""
        code = task.parameters.get('code', '')
        language = task.parameters.get('language', 'python')
        
        if language == "python":
            # Simpan code ke file sementara
            temp_file = f"/tmp/code_{task.id}.py"
            self.container.exec_run(f"echo '{code}' > {temp_file}")
            
            # Eksekusi dengan timeout
            result = self.container.exec_run(
                f"timeout 30s python3 {temp_file}",
                workdir="/workspace"
            )
            
            # Cleanup
            self.container.exec_run(f"rm {temp_file}")
            
            return {
                "exit_code": result.exit_code,
                "output": result.output.decode()
            }

    async def _handle_screen_interaction(self, task: Task):
        """Handle screen interactions (click, type, etc.)"""
        action = task.parameters.get('action')
        
        if action == "screenshot":
            result = self.container.exec_run(
                "scrot /workspace/screenshots/current.png"
            )
            return {"screenshot_path": "/workspace/screenshots/current.png"}
            
        elif action == "click":
            x = task.parameters.get('x', 0)
            y = task.parameters.get('y', 0)
            result = self.container.exec_run(
                f"xdotool mousemove {x} {y} click 1"
            )
            return {"status": "clicked", "coordinates": [x, y]}
            
        elif action == "type":
            text = task.parameters.get('text', '')
            result = self.container.exec_run(
                f"xdotool type '{text}'"
            )
            return {"status": "typed", "text": text}

    async def _handle_api_call(self, task: Task):
        """Handle API calls"""
        script = f"""
import requests
import json

url = "{task.parameters.get('url', '')}"
method = "{task.parameters.get('method', 'GET')}"
headers = {task.parameters.get('headers', {})}
data = {task.parameters.get('data', {})}

if method == "GET":
    response = requests.get(url, headers=headers)
elif method == "POST":
    response = requests.post(url, headers=headers, json=data)
elif method == "PUT":
    response = requests.put(url, headers=headers, json=data)

print(json.dumps({{
    "status_code": response.status_code,
    "headers": dict(response.headers),
    "content": response.text
}}))
"""
        
        result = self.container.exec_run(f"python3 -c '{script}'")
        return {"response": result.output.decode()}

    async def stop_sandbox(self):
        """Hentikan dan bersihkan container"""
        if self.container:
            self.container.stop()
            self.container.remove()
            self.logger.info(f"Sandbox stopped for agent {self.agent_id}")
```

### 3. Dockerfile untuk Agent Environment

```dockerfile
# Dockerfile untuk AI Agent
FROM ubuntu:22.04

# Install dependencies
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    xvfb \
    x11vnc \
    fluxbox \
    chromium-browser \
    firefox \
    scrot \
    xdotool \
    curl \
    wget \
    git \
    vim \
    nano \
    && rm -rf /var/lib/apt/lists/*

# Setup user
RUN useradd -m -u 1000 agent && \
    echo "agent:password" | chpasswd

# Install Python packages
COPY requirements.txt /tmp/
RUN pip3 install -r /tmp/requirements.txt

# Setup workspace
RUN mkdir -p /workspace /logs /screenshots
RUN chown -R agent:agent /workspace /logs /screenshots

# Copy agent code
COPY agent_code/ /app/
RUN chown -R agent:agent /app

# Environment variables
ENV DISPLAY=:99
ENV PYTHONPATH=/app

USER agent
WORKDIR /workspace

# Start script
COPY start.sh /start.sh
USER root
RUN chmod +x /start.sh
USER agent

CMD ["/start.sh"]
```

### 4. Requirements dan Dependencies

```txt
# requirements.txt
fastapi==0.104.1
uvicorn==0.24.0
playwright==1.40.0
selenium==4.15.2
requests==2.31.0
aiohttp==3.9.1
asyncio-mqtt==0.11.1
docker==6.1.3
numpy==1.24.3
pandas==2.0.3
opencv-python==4.8.1.78
pillow==10.1.0
beautifulsoup4==4.12.2
lxml==4.9.3
python-multipart==0.0.6
websockets==12.0
pynput==1.7.6
psutil==5.9.6
schedule==1.2.0
python-dotenv==1.0.0
jsonschema==4.19.2
pydantic==2.5.0
redis==5.0.1
celery==5.3.4
```

### 5. Agent Management System

```python
# agent_manager.py
import asyncio
from typing import Dict, List
import uuid
from agent_controller import ManusAIAgent, Task

class AgentManager:
    def __init__(self):
        self.agents: Dict[str, ManusAIAgent] = {}
        self.agent_pool_size = 5
        
    async def create_agent(self, capabilities: List[str] = None) -> str:
        """Buat agent baru dengan sandbox"""
        agent_id = str(uuid.uuid4())
        container_name = f"agent_{agent_id[:8]}"
        
        agent = ManusAIAgent(agent_id, container_name)
        
        # Filter capabilities jika dispesifikasikan
        if capabilities:
            for cap in list(agent.capabilities.keys()):
                if cap not in capabilities:
                    agent.capabilities[cap] = False
        
        # Start sandbox
        success = await agent.start_sandbox()
        if success:
            self.agents[agent_id] = agent
            return agent_id
        else:
            raise Exception(f"Failed to create agent {agent_id}")
    
    async def assign_task(self, agent_id: str, task: Task):
        """Assign task ke agent tertentu"""
        if agent_id not in self.agents:
            raise ValueError(f"Agent {agent_id} not found")
            
        agent = self.agents[agent_id]
        await agent.task_queue.put(task)
        
    async def get_available_agent(self, required_capabilities: List[str] = None):
        """Dapatkan agent yang tersedia dengan capabilities yang dibutuhkan"""
        for agent in self.agents.values():
            if agent.status.value == "idle":
                if required_capabilities:
                    if all(agent.capabilities.get(cap, False) for cap in required_capabilities):
                        return agent.agent_id
                else:
                    return agent.agent_id
        return None
    
    async def scale_agents(self, target_count: int):
        """Scale jumlah agent"""
        current_count = len(self.agents)
        
        if target_count > current_count:
            # Tambah agent
            for _ in range(target_count - current_count):
                await self.create_agent()
                
        elif target_count < current_count:
            # Kurangi agent (stop yang idle)
            agents_to_stop = []
            for agent_id, agent in self.agents.items():
                if len(agents_to_stop) >= (current_count - target_count):
                    break
                if agent.status.value == "idle":
                    agents_to_stop.append(agent_id)
            
            for agent_id in agents_to_stop:
                await self.stop_agent(agent_id)
    
    async def stop_agent(self, agent_id: str):
        """Stop dan remove agent"""
        if agent_id in self.agents:
            agent = self.agents[agent_id]
            await agent.stop_sandbox()
            del self.agents[agent_id]
    
    async def get_agent_status(self, agent_id: str = None):
        """Get status agent"""
        if agent_id:
            if agent_id in self.agents:
                agent = self.agents[agent_id]
                return {
                    "agent_id": agent_id,
                    "status": agent.status.value,
                    "current_task": agent.current_task.id if agent.current_task else None,
                    "capabilities": agent.capabilities
                }
            else:
                return None
        else:
            # Return status semua agent
            return {
                agent_id: {
                    "status": agent.status.value,
                    "current_task": agent.current_task.id if agent.current_task else None,
                    "capabilities": agent.capabilities
                }
                for agent_id, agent in self.agents.items()
            }
```

### 6. API Endpoints

```python
# api_server.py
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
import asyncio
import json
from agent_manager import AgentManager, Task
from typing import List, Dict, Any

app = FastAPI(title="Manus AI Agent API")
agent_manager = AgentManager()

@app.on_event("startup")
async def startup_event():
    # Buat pool agent awal
    for _ in range(3):
        await agent_manager.create_agent()

@app.post("/agents/create")
async def create_agent(capabilities: List[str] = None):
    """Buat agent baru"""
    try:
        agent_id = await agent_manager.create_agent(capabilities)
        return {"agent_id": agent_id, "status": "created"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/agents/{agent_id}/tasks")
async def assign_task(agent_id: str, task_data: Dict[str, Any]):
    """Assign task ke agent"""
    try:
        task = Task(
            id=task_data.get("id", str(uuid.uuid4())),
            type=task_data["type"],
            description=task_data["description"],
            parameters=task_data.get("parameters", {}),
            priority=task_data.get("priority", 1)
        )
        
        await agent_manager.assign_task(agent_id, task)
        return {"status": "task_assigned", "task_id": task.id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/tasks/auto-assign")
async def auto_assign_task(task_data: Dict[str, Any]):
    """Auto-assign task ke agent yang tersedia"""
    try:
        required_capabilities = task_data.get("required_capabilities", [])
        agent_id = await agent_manager.get_available_agent(required_capabilities)
        
        if not agent_id:
            # Buat agent baru jika tidak ada yang tersedia
            agent_id = await agent_manager.create_agent(required_capabilities)
        
        task = Task(
            id=task_data.get("id", str(uuid.uuid4())),
            type=task_data["type"],
            description=task_data["description"],
            parameters=task_data.get("parameters", {}),
            priority=task_data.get("priority", 1)
        )
        
        await agent_manager.assign_task(agent_id, task)
        return {
            "status": "task_assigned", 
            "task_id": task.id,
            "agent_id": agent_id
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/agents/{agent_id}/status")
async def get_agent_status(agent_id: str):
    """Get status agent"""
    status = await agent_manager.get_agent_status(agent_id)
    if status:
        return status
    else:
        raise HTTPException(status_code=404, detail="Agent not found")

@app.get("/agents/status")
async def get_all_agents_status():
    """Get status semua agent"""
    return await agent_manager.get_agent_status()

@app.post("/agents/scale")
async def scale_agents(target_count: int):
    """Scale jumlah agent"""
    try:
        await agent_manager.scale_agents(target_count)
        return {"status": "scaled", "target_count": target_count}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/agents/{agent_id}")
async def stop_agent(agent_id: str):
    """Stop agent"""
    try:
        await agent_manager.stop_agent(agent_id)
        return {"status": "stopped", "agent_id": agent_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/agents/{agent_id}/vnc")
async def get_vnc_url(agent_id: str):
    """Get VNC URL untuk monitoring agent"""
    if agent_id not in agent_manager.agents:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    agent = agent_manager.agents[agent_id]
    container_ports = agent.container.attrs['NetworkSettings']['Ports']
    vnc_port = container_ports['5900/tcp'][0]['HostPort']
    
    return {
        "vnc_url": f"vnc://localhost:{vnc_port}",
        "web_vnc_url": f"http://localhost:6080/vnc.html?host=localhost&port={vnc_port}"
    }

@app.get("/agents/{agent_id}/screenshot")
async def get_screenshot(agent_id: str):
    """Get screenshot dari agent"""
    if agent_id not in agent_manager.agents:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    agent = agent_manager.agents[agent_id]
    
    # Ambil screenshot
    screenshot_task = Task(
        id="screenshot_" + str(uuid.uuid4()),
        type="screen_interaction",
        description="Take screenshot",
        parameters={"action": "screenshot"}
    )
    
    result = await agent.execute_task(screenshot_task)
    
    # Return image file
    screenshot_path = result["screenshot_path"]
    result = agent.container.exec_run(f"cat {screenshot_path}")
    
    return StreamingResponse(
        io.BytesIO(result.output),
        media_type="image/png"
    )
```

### 7. Monitoring dan Logging

```python
# monitoring.py
import asyncio
import time
import psutil
import json
from typing import Dict, Any
import docker

class AgentMonitor:
    def __init__(self, agent_manager):
        self.agent_manager = agent_manager
        self.metrics = {}
        self.docker_client = docker.from_env()
        
    async def start_monitoring(self):
        """Start monitoring loop"""
        while True:
            await self.collect_metrics()
            await asyncio.sleep(10)  # Collect metrics every 10 seconds
            
    async def collect_metrics(self):
        """Collect metrics dari semua agent"""
        timestamp = time.time()
        
        for agent_id, agent in self.agent_manager.agents.items():
            try:
                # Container stats
                container_stats = agent.container.stats(stream=False)
                
                # CPU usage
                cpu_percent = self.calculate_cpu_percent(container_stats)
                
                # Memory usage
                memory_usage = container_stats['memory_stats']['usage']
                memory_limit = container_stats['memory_stats']['limit']
                memory_percent = (memory_usage / memory_limit) * 100
                
                # Network I/O
                network_rx = container_stats['networks']['eth0']['rx_bytes']
                network_tx = container_stats['networks']['eth0']['tx_bytes']
                
                # Store metrics
                self.metrics[agent_id] = {
                    'timestamp': timestamp,
                    'cpu_percent': cpu_percent,
                    'memory_usage_mb': memory_usage / 1024 / 1024,
                    'memory_percent': memory_percent,
                    'network_rx_mb': network_rx / 1024 / 1024,
                    'network_tx_mb': network_tx / 1024 / 1024,
                    'status': agent.status.value,
                    'current_task': agent.current_task.id if agent.current_task else None
                }
                
            except Exception as e:
                print(f"Error collecting metrics for agent {agent_id}: {e}")
    
    def calculate_cpu_percent(self, stats):
        """Calculate CPU percentage"""
        cpu_delta = stats['cpu_stats']['cpu_usage']['total_usage'] - \
                   stats['precpu_stats']['cpu_usage']['total_usage']
        system_delta = stats['cpu_stats']['system_cpu_usage'] - \
                      stats['precpu_stats']['system_cpu_usage']
        
        if system_delta > 0 and cpu_delta > 0:
            return (cpu_delta / system_delta) * len(stats['cpu_stats']['cpu_usage']['percpu_usage']) * 100
        return 0.0
    
    def get_metrics(self, agent_id: str = None):
        """Get metrics for specific agent or all agents"""
        if agent_id:
            return self.metrics.get(agent_id)
        return self.metrics
```

### 8. Deployment Script

```bash
#!/bin/bash
# deploy.sh

echo "Building Manus AI Agent Environment..."

# Build Docker image
docker build -t manus-ai-agent:latest .

# Create network
docker network create agent-network 2>/dev/null || true

# Create volumes
docker volume create agent-workspace
docker volume create agent-logs

# Start services
docker-compose up -d

echo "Deployment completed!"
echo "API available at: http://localhost:8000"
echo "VNC monitoring at: http://localhost:6080"

# Health check
sleep 10
curl -f http://localhost:8000/agents/status || echo "API not ready yet"
```

### 9. Usage Examples

```python
# example_usage.py
import asyncio
import aiohttp
import json

async def create_web_scraping_agent():
    """Contoh penggunaan untuk web scraping"""
    
    # Buat agent baru
    async with aiohttp.ClientSession() as session:
        # Create agent
        async with session.post('http://localhost:8000/agents/create', 
                               json={"capabilities": ["web_browsing", "file_operations"]}) as resp:
            agent_data = await resp.json()
            agent_id = agent_data['agent_id']
        
        # Assign web browsing task
        task_data = {
            "type": "web_browse",
            "description": "Scrape product prices from e-commerce site",
            "parameters": {
                "url": "https://example-shop.com/products",
                "action": "extract",
                "selector": ".price-tag"
            }
        }
        
        async with session.post(f'http://localhost:8000/agents/{agent_id}/tasks',
                               json=task_data) as resp:
            result = await resp.json()
            print(f"Task assigned: {result}")
        
        # Monitor agent status
        async with session.get(f'http://localhost:8000/agents/{agent_id}/status') as resp:
            status = await resp.json()
            print(f"Agent status: {status}")

async def create_data_analysis_agent():
    """Contoh untuk data analysis"""
    
    async with aiohttp.ClientSession() as session:
        # Auto-assign task
        task_data = {
            "type": "code_execution",
            "description": "Analyze sales data and generate report",
            "required_capabilities": ["code_execution", "data_analysis"],
            "parameters": {
                "language": "python",
                "code": """
import pandas as pd
import matplotlib.pyplot as plt

# Load data
data = pd.read_csv('/workspace/sales_data.csv')

# Analysis
monthly_sales = data.groupby('month')['sales'].sum()
print("Monthly Sales Summary:")
print(monthly_sales)

# Create chart
plt.figure(figsize=(10, 6))
monthly_sales.plot(kind='bar')
plt.title('Monthly Sales')
plt.savefig('/workspace/sales_chart.png')
plt.close()

print("Analysis completed. Chart saved to sales_chart.png")
"""
            }
        }
        
        async with session.post('http://localhost:8000/tasks/auto-assign',
                               json=task_data) as resp:
            result = await resp.json()
            print(f"Task auto-assigned: {result}")

# Run examples
if __name__ == "__main__":
    asyncio.run(create_web_scraping_agent())
    asyncio.run(create_data_analysis_agent())
```

### 10. Security Considerations

```python
# security.py
import os
import subprocess
from typing import List

class SecurityManager:
    def __init__(self):
        self.allowed_commands = [
            'python3', 'pip3', 'curl', 'wget', 'git',
            'chromium-browser', 'firefox', 'scrot', 'xdotool'
        ]
        
        self.blocked_paths = [
            '/etc/passwd', '/etc/shadow', '/root', '/var/log',
            '/proc', '/sys', '/dev'
        ]
    
    def validate_command(self, command: str) -> bool:
        """Validate if command is safe to execute"""
        cmd_parts = command.split()
        if not cmd_parts:
            return False
            
        base_cmd = cmd_parts[0]
        
        # Check if command is in allowed list
        if base_cmd not in self.allowed_commands:
            return False
            
        # Check for dangerous patterns
        dangerous_patterns = [
            'sudo', 'su', 'chmod', 'chown', 'rm -rf /',
            '../../', '/etc/', '/root/', 'passwd'
        ]
        
        for pattern in dangerous_patterns:
            if pattern in command:
                return False
                
        return True
    
    def validate_file_path(self, file_path: str) -> bool:
        """Validate if file path is safe to access"""
        abs_path = os.path.abspath(file_path)
        
        # Check if path is in blocked list
        for blocked in self.blocked_paths:
            if abs_path.startswith(blocked):
                return False
                
        # Must be within workspace
        if not abs_path.startswith('/workspace'):
            return False
            
        return True
    
    def sanitize_input(self, user_input: str) -> str:
        """Sanitize user input"""
        # Remove dangerous characters
        dangerous_chars = [';', '|', '&', '$', '`', '(', ')']
        sanitized = user_input
        
        for char in dangerous_chars:
            sanitized = sanitized.replace(char, '')
            
        return sanitized.strip()
```

## Kesimpulan

Implementasi ini memberikan Anda framework lengkap untuk membangun AI agent seperti Manus AI yang dapat:

1. **Berjalan dalam sandbox Docker** dengan isolasi keamanan penuh
2. **Memiliki virtual desktop** dengan VNC untuk monitoring
3. **Menjalankan berbagai tasks** seperti web browsing, file operations, code execution
4. **Auto-scaling** berdasarkan workload
5. **Monitoring dan logging** yang komprehensif
6. **API yang lengkap** untuk integrasi
7. **Security yang robust** dengan validasi command dan path

Framework ini dapat diadaptasi sesuai kebutuhan spesifik Anda dan dikembangkan lebih lanjut dengan capabilities tambahan seperti machine learning inference, computer vision, atau integrasi dengan services external lainnya.
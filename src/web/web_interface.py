"""
Web Interface for Autonomous Agent Colony
Provides HTML dashboard for monitoring and control
"""

import asyncio
from typing import Dict, Any
from datetime import datetime
from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi import Request

from ..utils.logger import get_logger

logger = get_logger(__name__)

class WebInterface:
    """Web interface for the autonomous agent colony"""
    
    def __init__(self, controller):
        self.controller = controller
        self.app = None
        self.templates = None
        self._setup_interface()
    
    def _setup_interface(self):
        """Setup web interface"""
        # Create templates directory if it doesn't exist
        templates_dir = Path(__file__).parent / "templates"
        templates_dir.mkdir(exist_ok=True)
        
        static_dir = Path(__file__).parent / "static"
        static_dir.mkdir(exist_ok=True)
        
        # Create basic HTML templates
        self._create_templates(templates_dir)
        self._create_static_files(static_dir)
        
        self.templates = Jinja2Templates(directory=str(templates_dir))
    
    def _create_templates(self, templates_dir: Path):
        """Create HTML templates"""
        
        # Main dashboard template
        dashboard_html = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Autonomous Agent Colony Dashboard</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <link href="/static/dashboard.css" rel="stylesheet">
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-dark bg-dark">
        <div class="container-fluid">
            <a class="navbar-brand" href="#">
                <i class="fas fa-robot"></i> Autonomous Agent Colony
            </a>
            <div class="navbar-nav ms-auto">
                <span class="navbar-text">
                    <i class="fas fa-circle text-success"></i> System Operational
                </span>
            </div>
        </div>
    </nav>

    <div class="container-fluid mt-3">
        <div class="row">
            <!-- Sidebar -->
            <div class="col-md-3">
                <div class="card">
                    <div class="card-header">
                        <h5><i class="fas fa-tachometer-alt"></i> Quick Actions</h5>
                    </div>
                    <div class="card-body">
                        <div class="d-grid gap-2">
                            <button class="btn btn-primary" onclick="createAgent()">
                                <i class="fas fa-plus"></i> Create Agent
                            </button>
                            <button class="btn btn-success" onclick="submitTask()">
                                <i class="fas fa-tasks"></i> Submit Task
                            </button>
                            <button class="btn btn-info" onclick="testCodeCompletion()">
                                <i class="fas fa-code"></i> Test Code Completion
                            </button>
                            <button class="btn btn-warning" onclick="refreshDashboard()">
                                <i class="fas fa-sync"></i> Refresh
                            </button>
                        </div>
                    </div>
                </div>

                <div class="card mt-3">
                    <div class="card-header">
                        <h5><i class="fas fa-chart-line"></i> System Stats</h5>
                    </div>
                    <div class="card-body">
                        <div class="stat-item">
                            <small class="text-muted">Total Agents</small>
                            <div class="h4" id="totalAgents">0</div>
                        </div>
                        <div class="stat-item">
                            <small class="text-muted">Active Tasks</small>
                            <div class="h4" id="activeTasks">0</div>
                        </div>
                        <div class="stat-item">
                            <small class="text-muted">Models Available</small>
                            <div class="h4" id="totalModels">0</div>
                        </div>
                        <div class="stat-item">
                            <small class="text-muted">Uptime</small>
                            <div class="h6" id="systemUptime">--:--:--</div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Main Content -->
            <div class="col-md-9">
                <!-- Status Cards -->
                <div class="row mb-3">
                    <div class="col-md-3">
                        <div class="card bg-primary text-white">
                            <div class="card-body">
                                <div class="d-flex justify-content-between">
                                    <div>
                                        <h6 class="card-title">Agents</h6>
                                        <h4 id="agentCount">0</h4>
                                    </div>
                                    <div class="align-self-center">
                                        <i class="fas fa-robot fa-2x"></i>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-3">
                        <div class="card bg-success text-white">
                            <div class="card-body">
                                <div class="d-flex justify-content-between">
                                    <div>
                                        <h6 class="card-title">Tasks</h6>
                                        <h4 id="taskCount">0</h4>
                                    </div>
                                    <div class="align-self-center">
                                        <i class="fas fa-tasks fa-2x"></i>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-3">
                        <div class="card bg-info text-white">
                            <div class="card-body">
                                <div class="d-flex justify-content-between">
                                    <div>
                                        <h6 class="card-title">Models</h6>
                                        <h4 id="modelCount">0</h4>
                                    </div>
                                    <div class="align-self-center">
                                        <i class="fas fa-brain fa-2x"></i>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-3">
                        <div class="card bg-warning text-white">
                            <div class="card-body">
                                <div class="d-flex justify-content-between">
                                    <div>
                                        <h6 class="card-title">Queue</h6>
                                        <h4 id="queueSize">0</h4>
                                    </div>
                                    <div class="align-self-center">
                                        <i class="fas fa-clock fa-2x"></i>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Tabs -->
                <ul class="nav nav-tabs" id="mainTabs" role="tablist">
                    <li class="nav-item" role="presentation">
                        <button class="nav-link active" id="agents-tab" data-bs-toggle="tab" data-bs-target="#agents" type="button" role="tab">
                            <i class="fas fa-robot"></i> Agents
                        </button>
                    </li>
                    <li class="nav-item" role="presentation">
                        <button class="nav-link" id="tasks-tab" data-bs-toggle="tab" data-bs-target="#tasks" type="button" role="tab">
                            <i class="fas fa-tasks"></i> Tasks
                        </button>
                    </li>
                    <li class="nav-item" role="presentation">
                        <button class="nav-link" id="models-tab" data-bs-toggle="tab" data-bs-target="#models" type="button" role="tab">
                            <i class="fas fa-brain"></i> Models
                        </button>
                    </li>
                    <li class="nav-item" role="presentation">
                        <button class="nav-link" id="logs-tab" data-bs-toggle="tab" data-bs-target="#logs" type="button" role="tab">
                            <i class="fas fa-list"></i> Logs
                        </button>
                    </li>
                </ul>

                <!-- Tab Content -->
                <div class="tab-content" id="mainTabContent">
                    <!-- Agents Tab -->
                    <div class="tab-pane fade show active" id="agents" role="tabpanel">
                        <div class="card">
                            <div class="card-header d-flex justify-content-between">
                                <h5>Active Agents</h5>
                                <button class="btn btn-sm btn-primary" onclick="createAgent()">Add Agent</button>
                            </div>
                            <div class="card-body">
                                <div class="table-responsive">
                                    <table class="table table-striped" id="agentsTable">
                                        <thead>
                                            <tr>
                                                <th>Agent ID</th>
                                                <th>Role</th>
                                                <th>Status</th>
                                                <th>Tasks Completed</th>
                                                <th>Last Activity</th>
                                                <th>Actions</th>
                                            </tr>
                                        </thead>
                                        <tbody id="agentsTableBody">
                                            <!-- Dynamic content -->
                                        </tbody>
                                    </table>
                                </div>
                            </div>
                        </div>
                    </div>

                    <!-- Tasks Tab -->
                    <div class="tab-pane fade" id="tasks" role="tabpanel">
                        <div class="card">
                            <div class="card-header d-flex justify-content-between">
                                <h5>Task Queue</h5>
                                <button class="btn btn-sm btn-success" onclick="submitTask()">Submit Task</button>
                            </div>
                            <div class="card-body">
                                <div id="tasksContent">
                                    <p class="text-muted">Task management interface coming soon...</p>
                                </div>
                            </div>
                        </div>
                    </div>

                    <!-- Models Tab -->
                    <div class="tab-pane fade" id="models" role="tabpanel">
                        <div class="card">
                            <div class="card-header">
                                <h5>Available Models</h5>
                            </div>
                            <div class="card-body">
                                <div id="modelsContent">
                                    <!-- Dynamic content -->
                                </div>
                            </div>
                        </div>
                    </div>

                    <!-- Logs Tab -->
                    <div class="tab-pane fade" id="logs" role="tabpanel">
                        <div class="card">
                            <div class="card-header">
                                <h5>System Logs</h5>
                            </div>
                            <div class="card-body">
                                <div class="log-container" id="logsContainer">
                                    <div class="log-entry">
                                        <span class="log-time">{{ current_time }}</span>
                                        <span class="log-level log-info">INFO</span>
                                        <span class="log-message">System started successfully</span>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <!-- Modals -->
    <!-- Create Agent Modal -->
    <div class="modal fade" id="createAgentModal" tabindex="-1">
        <div class="modal-dialog">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title">Create New Agent</h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                </div>
                <div class="modal-body">
                    <form id="createAgentForm">
                        <div class="mb-3">
                            <label for="agentRole" class="form-label">Agent Role</label>
                            <select class="form-select" id="agentRole" required>
                                <option value="">Select a role...</option>
                                <option value="developer">Developer</option>
                                <option value="analyst">Analyst</option>
                                <option value="researcher">Researcher</option>
                                <option value="critic">Critic</option>
                                <option value="coordinator">Coordinator</option>
                            </select>
                        </div>
                        <div class="mb-3">
                            <label for="agentConfig" class="form-label">Configuration (JSON)</label>
                            <textarea class="form-control" id="agentConfig" rows="3" placeholder='{"task_type": "general"}'></textarea>
                        </div>
                    </form>
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                    <button type="button" class="btn btn-primary" onclick="submitCreateAgent()">Create Agent</button>
                </div>
            </div>
        </div>
    </div>

    <!-- Submit Task Modal -->
    <div class="modal fade" id="submitTaskModal" tabindex="-1">
        <div class="modal-dialog modal-lg">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title">Submit New Task</h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                </div>
                <div class="modal-body">
                    <form id="submitTaskForm">
                        <div class="mb-3">
                            <label for="taskType" class="form-label">Task Type</label>
                            <select class="form-select" id="taskType" required>
                                <option value="">Select task type...</option>
                                <option value="coding">Coding</option>
                                <option value="analysis">Analysis</option>
                                <option value="research">Research</option>
                                <option value="general">General</option>
                            </select>
                        </div>
                        <div class="mb-3">
                            <label for="taskContent" class="form-label">Task Description</label>
                            <textarea class="form-control" id="taskContent" rows="4" required placeholder="Describe the task you want the agents to perform..."></textarea>
                        </div>
                        <div class="mb-3">
                            <label for="preferredRole" class="form-label">Preferred Agent Role (Optional)</label>
                            <select class="form-select" id="preferredRole">
                                <option value="">Any available agent</option>
                                <option value="developer">Developer</option>
                                <option value="analyst">Analyst</option>
                                <option value="researcher">Researcher</option>
                                <option value="critic">Critic</option>
                            </select>
                        </div>
                        <div class="mb-3">
                            <label for="taskPriority" class="form-label">Priority</label>
                            <select class="form-select" id="taskPriority">
                                <option value="5">Normal</option>
                                <option value="3">Low</option>
                                <option value="7">High</option>
                                <option value="9">Critical</option>
                            </select>
                        </div>
                    </form>
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                    <button type="button" class="btn btn-success" onclick="submitNewTask()">Submit Task</button>
                </div>
            </div>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
    <script src="/static/dashboard.js"></script>
</body>
</html>'''
        
        with open(templates_dir / "dashboard.html", 'w') as f:
            f.write(dashboard_html)
    
    def _create_static_files(self, static_dir: Path):
        """Create static CSS and JS files"""
        
        # CSS file
        css_content = '''
.stat-item {
    margin-bottom: 1rem;
    padding-bottom: 0.5rem;
    border-bottom: 1px solid #eee;
}

.log-container {
    background-color: #f8f9fa;
    border: 1px solid #dee2e6;
    border-radius: 0.375rem;
    padding: 1rem;
    height: 400px;
    overflow-y: auto;
    font-family: 'Courier New', monospace;
    font-size: 0.875rem;
}

.log-entry {
    margin-bottom: 0.5rem;
}

.log-time {
    color: #6c757d;
    margin-right: 0.5rem;
}

.log-level {
    padding: 0.25rem 0.5rem;
    border-radius: 0.25rem;
    margin-right: 0.5rem;
    font-weight: bold;
    font-size: 0.75rem;
}

.log-info {
    background-color: #d1ecf1;
    color: #0c5460;
}

.log-warning {
    background-color: #fff3cd;
    color: #856404;
}

.log-error {
    background-color: #f8d7da;
    color: #721c24;
}

.log-success {
    background-color: #d4edda;
    color: #155724;
}

.log-message {
    color: #212529;
}

.card {
    box-shadow: 0 0.125rem 0.25rem rgba(0, 0, 0, 0.075);
    border: 1px solid rgba(0, 0, 0, 0.125);
}

.navbar-brand {
    font-weight: bold;
}

.tab-content {
    margin-top: 1rem;
}

.status-badge {
    font-size: 0.75rem;
}

.agent-actions {
    white-space: nowrap;
}

.websocket-status {
    position: fixed;
    top: 70px;
    right: 20px;
    z-index: 1000;
}
'''
        
        with open(static_dir / "dashboard.css", 'w') as f:
            f.write(css_content)
        
        # JavaScript file
        js_content = '''
class DashboardApp {
    constructor() {
        this.websocket = null;
        this.init();
    }

    init() {
        this.connectWebSocket();
        this.loadInitialData();
        this.setupEventListeners();
        
        // Refresh data every 30 seconds
        setInterval(() => this.refreshDashboard(), 30000);
    }

    connectWebSocket() {
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const wsUrl = `${protocol}//${window.location.host}/ws`;
        
        this.websocket = new WebSocket(wsUrl);
        
        this.websocket.onopen = () => {
            console.log('WebSocket connected');
            this.showWebSocketStatus('connected');
        };
        
        this.websocket.onmessage = (event) => {
            const message = JSON.parse(event.data);
            this.handleWebSocketMessage(message);
        };
        
        this.websocket.onclose = () => {
            console.log('WebSocket disconnected');
            this.showWebSocketStatus('disconnected');
            // Attempt to reconnect after 5 seconds
            setTimeout(() => this.connectWebSocket(), 5000);
        };
        
        this.websocket.onerror = (error) => {
            console.error('WebSocket error:', error);
            this.showWebSocketStatus('error');
        };
    }

    showWebSocketStatus(status) {
        let statusElement = document.getElementById('websocketStatus');
        if (!statusElement) {
            statusElement = document.createElement('div');
            statusElement.id = 'websocketStatus';
            statusElement.className = 'websocket-status';
            document.body.appendChild(statusElement);
        }
        
        const statusConfig = {
            connected: { class: 'alert-success', icon: 'fas fa-wifi', text: 'Connected' },
            disconnected: { class: 'alert-warning', icon: 'fas fa-wifi', text: 'Disconnected' },
            error: { class: 'alert-danger', icon: 'fas fa-exclamation-triangle', text: 'Connection Error' }
        };
        
        const config = statusConfig[status];
        statusElement.innerHTML = `
            <div class="alert ${config.class} alert-dismissible fade show" role="alert">
                <i class="${config.icon}"></i> WebSocket ${config.text}
                <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
            </div>
        `;
    }

    handleWebSocketMessage(message) {
        console.log('WebSocket message:', message);
        
        switch (message.type) {
            case 'agent_created':
                this.addLogEntry('info', `Agent ${message.agent_id} (${message.role}) created`);
                this.refreshAgents();
                break;
            case 'agent_removed':
                this.addLogEntry('warning', `Agent ${message.agent_id} removed`);
                this.refreshAgents();
                break;
            case 'task_submitted':
                this.addLogEntry('info', `Task ${message.task_id} (${message.task_type}) submitted`);
                this.refreshStats();
                break;
            case 'system_shutdown':
                this.addLogEntry('error', 'System shutdown initiated');
                break;
        }
    }

    setupEventListeners() {
        // Modal event listeners are handled by Bootstrap
    }

    async loadInitialData() {
        await this.refreshDashboard();
    }

    async refreshDashboard() {
        await Promise.all([
            this.refreshStats(),
            this.refreshAgents(),
            this.refreshModels()
        ]);
    }

    async refreshStats() {
        try {
            const response = await fetch('/system/status');
            const data = await response.json();
            
            if (data.success) {
                const agents = data.agents;
                const models = data.models;
                
                document.getElementById('totalAgents').textContent = agents.total_agents || 0;
                document.getElementById('agentCount').textContent = agents.total_agents || 0;
                document.getElementById('activeTasks').textContent = agents.queue_size || 0;
                document.getElementById('taskCount').textContent = agents.queue_size || 0;
                document.getElementById('totalModels').textContent = models.total_models || 0;
                document.getElementById('modelCount').textContent = models.total_models || 0;
                document.getElementById('queueSize').textContent = agents.queue_size || 0;
            }
        } catch (error) {
            console.error('Failed to refresh stats:', error);
        }
    }

    async refreshAgents() {
        try {
            const response = await fetch('/agents');
            const data = await response.json();
            
            if (data.success) {
                this.updateAgentsTable(data.agents);
            }
        } catch (error) {
            console.error('Failed to refresh agents:', error);
        }
    }

    updateAgentsTable(agents) {
        const tbody = document.getElementById('agentsTableBody');
        tbody.innerHTML = '';
        
        Object.entries(agents).forEach(([agentId, agent]) => {
            const row = document.createElement('tr');
            
            const statusBadge = this.getStatusBadge(agent.status);
            const lastActivity = new Date(agent.last_activity).toLocaleString();
            
            row.innerHTML = `
                <td><code>${agentId}</code></td>
                <td><span class="badge bg-secondary">${agent.role}</span></td>
                <td>${statusBadge}</td>
                <td>${agent.task_count}</td>
                <td><small>${lastActivity}</small></td>
                <td class="agent-actions">
                    <button class="btn btn-sm btn-outline-danger" onclick="dashboard.removeAgent('${agentId}')">
                        <i class="fas fa-trash"></i>
                    </button>
                </td>
            `;
            
            tbody.appendChild(row);
        });
    }

    getStatusBadge(status) {
        const statusConfig = {
            ready: { class: 'bg-success', text: 'Ready' },
            working: { class: 'bg-primary', text: 'Working' },
            error: { class: 'bg-danger', text: 'Error' },
            initializing: { class: 'bg-warning', text: 'Initializing' }
        };
        
        const config = statusConfig[status] || { class: 'bg-secondary', text: status };
        return `<span class="badge ${config.class}">${config.text}</span>`;
    }

    async refreshModels() {
        try {
            const response = await fetch('/models');
            const data = await response.json();
            
            if (data.success) {
                this.updateModelsContent(data.models);
            }
        } catch (error) {
            console.error('Failed to refresh models:', error);
        }
    }

    updateModelsContent(models) {
        const content = document.getElementById('modelsContent');
        content.innerHTML = `
            <div class="row">
                <div class="col-md-6">
                    <h6>Total Models: ${models.total_models}</h6>
                    <h6>Healthy Models: ${models.healthy_models}</h6>
                    <h6>Providers: ${models.providers.join(', ')}</h6>
                </div>
                <div class="col-md-6">
                    <h6>Request Count:</h6>
                    <pre>${JSON.stringify(models.request_count, null, 2)}</pre>
                </div>
            </div>
        `;
    }

    async createAgent() {
        const modal = new bootstrap.Modal(document.getElementById('createAgentModal'));
        modal.show();
    }

    async submitCreateAgent() {
        const role = document.getElementById('agentRole').value;
        const configText = document.getElementById('agentConfig').value;
        
        if (!role) {
            alert('Please select an agent role');
            return;
        }
        
        let config = {};
        if (configText.trim()) {
            try {
                config = JSON.parse(configText);
            } catch (error) {
                alert('Invalid JSON configuration');
                return;
            }
        }
        
        try {
            const response = await fetch('/agents', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ role, config }),
            });
            
            const result = await response.json();
            
            if (result.success) {
                this.addLogEntry('success', `Agent ${result.agent_id} created successfully`);
                bootstrap.Modal.getInstance(document.getElementById('createAgentModal')).hide();
                document.getElementById('createAgentForm').reset();
                await this.refreshAgents();
            } else {
                alert('Failed to create agent: ' + result.error);
            }
        } catch (error) {
            console.error('Failed to create agent:', error);
            alert('Failed to create agent: ' + error.message);
        }
    }

    async removeAgent(agentId) {
        if (!confirm(`Are you sure you want to remove agent ${agentId}?`)) {
            return;
        }
        
        try {
            const response = await fetch(`/agents/${agentId}`, {
                method: 'DELETE',
            });
            
            const result = await response.json();
            
            if (result.success) {
                this.addLogEntry('warning', `Agent ${agentId} removed`);
                await this.refreshAgents();
            } else {
                alert('Failed to remove agent: ' + result.error);
            }
        } catch (error) {
            console.error('Failed to remove agent:', error);
            alert('Failed to remove agent: ' + error.message);
        }
    }

    async submitTask() {
        const modal = new bootstrap.Modal(document.getElementById('submitTaskModal'));
        modal.show();
    }

    async submitNewTask() {
        const type = document.getElementById('taskType').value;
        const content = document.getElementById('taskContent').value;
        const preferred_role = document.getElementById('preferredRole').value;
        const priority = parseInt(document.getElementById('taskPriority').value);
        
        if (!type || !content) {
            alert('Please fill in task type and description');
            return;
        }
        
        try {
            const response = await fetch('/tasks', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    type,
                    content,
                    context: {},
                    preferred_role: preferred_role || null,
                    priority
                }),
            });
            
            const result = await response.json();
            
            if (result.success) {
                this.addLogEntry('success', `Task ${result.task_id} submitted successfully`);
                bootstrap.Modal.getInstance(document.getElementById('submitTaskModal')).hide();
                document.getElementById('submitTaskForm').reset();
                await this.refreshStats();
            } else {
                alert('Failed to submit task: ' + result.error);
            }
        } catch (error) {
            console.error('Failed to submit task:', error);
            alert('Failed to submit task: ' + error.message);
        }
    }

    async testCodeCompletion() {
        const testCode = `def hello_world():
    print("Hello, ");`;
        
        try {
            const response = await fetch('/code/completion', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    file_path: 'test.py',
                    code_context: testCode,
                    cursor_position: testCode.length,
                    language: 'python'
                }),
            });
            
            const result = await response.json();
            
            if (result.success) {
                this.addLogEntry('info', `Code completion test successful: ${result.completions.length} suggestions`);
                console.log('Completions:', result.completions);
            } else {
                alert('Code completion test failed: ' + result.error);
            }
        } catch (error) {
            console.error('Code completion test failed:', error);
            alert('Code completion test failed: ' + error.message);
        }
    }

    addLogEntry(level, message) {
        const container = document.getElementById('logsContainer');
        const entry = document.createElement('div');
        entry.className = 'log-entry';
        
        const timestamp = new Date().toLocaleTimeString();
        entry.innerHTML = `
            <span class="log-time">${timestamp}</span>
            <span class="log-level log-${level}">${level.toUpperCase()}</span>
            <span class="log-message">${message}</span>
        `;
        
        container.appendChild(entry);
        container.scrollTop = container.scrollHeight;
    }
}

// Global functions for HTML event handlers
let dashboard;

window.onload = function() {
    dashboard = new DashboardApp();
};

function refreshDashboard() {
    dashboard.refreshDashboard();
}

function createAgent() {
    dashboard.createAgent();
}

function submitCreateAgent() {
    dashboard.submitCreateAgent();
}

function submitTask() {
    dashboard.submitTask();
}

function submitNewTask() {
    dashboard.submitNewTask();
}

function testCodeCompletion() {
    dashboard.testCodeCompletion();
}
'''
        
        with open(static_dir / "dashboard.js", 'w') as f:
            f.write(js_content)
    
    def setup_routes(self, app: FastAPI):
        """Setup web interface routes"""
        
        # Serve static files
        static_dir = Path(__file__).parent / "static"
        app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")
        
        @app.get("/admin", response_class=HTMLResponse)
        async def admin_dashboard(request: Request):
            """Main admin dashboard"""
            return self.templates.TemplateResponse("dashboard.html", {
                "request": request,
                "current_time": datetime.now().isoformat()
            })
    
    async def start(self):
        """Start web interface"""
        try:
            # Setup routes in the main app
            if hasattr(self.controller, 'api_server') and self.controller.api_server:
                self.setup_routes(self.controller.api_server.app)
            
            logger.info("✅ Web Interface started")
            
        except Exception as e:
            logger.error(f"Failed to start web interface: {e}")
            raise
    
    async def stop(self):
        """Stop web interface"""
        logger.info("✅ Web Interface stopped")
    
    def is_healthy(self) -> bool:
        """Check if web interface is healthy"""
        return True
// Socket.IO connection
const socket = io();

// Global state
let systemStatus = {};
let agents = [];
let realTimeData = {};

// Initialize dashboard
async function initializeDashboard() {
    console.log('🚀 Initializing Ultimate AGI Force Dashboard');
    
    // Load initial data
    await loadSystemStatus();
    await loadAgents();
    
    // Setup real-time updates
    setupSocketListeners();
    
    // Start periodic updates
    setInterval(updateMetrics, 5000); // Update every 5 seconds
    setInterval(loadSystemStatus, 30000); // Full refresh every 30 seconds
}

// Load system status from API
async function loadSystemStatus() {
    try {
        const response = await fetch('/api/system/status');
        const data = await response.json();
        
        if (data.success) {
            systemStatus = data.data;
            updateSystemMetrics();
            updateSystemHealth();
        } else {
            console.error('Failed to load system status:', data.error);
        }
    } catch (error) {
        console.error('Error loading system status:', error);
    }
}

// Load agents from API
async function loadAgents() {
    try {
        const response = await fetch('/api/agents/list');
        const data = await response.json();
        
        if (data.success) {
            agents = data.data;
            updateAgentsList();
            updateAgentMetrics();
        } else {
            console.error('Failed to load agents:', data.error);
        }
    } catch (error) {
        console.error('Error loading agents:', error);
    }
}

// Update system metrics display
function updateSystemMetrics() {
    document.getElementById('active-agents').textContent = systemStatus.agents_active || 0;
    document.getElementById('total-tasks').textContent = systemStatus.llm_requests || 0;
    document.getElementById('revenue-generated').textContent = '$' + (systemStatus.revenue || 0);
    document.getElementById('threats-detected').textContent = systemStatus.threats || 0;
    document.getElementById('backups-created').textContent = systemStatus.backups || 0;
    document.getElementById('campaigns-active').textContent = systemStatus.campaigns || 0;
}

// Update system health display
function updateSystemHealth() {
    // Update CPU usage (mock calculation based on active agents)
    const cpuUsage = Math.min(95, (systemStatus.agents_active || 0) * 2 + 20);
    document.querySelector('#cpu-usage-bar').style.width = cpuUsage + '%';
    document.querySelector('#cpu-usage-text').textContent = cpuUsage + '%';

    // Update memory usage
    const memoryUsage = Math.min(90, (systemStatus.total_agents || 0) * 1.5 + 30);
    document.querySelector('#memory-usage-bar').style.width = memoryUsage + '%';
    document.querySelector('#memory-usage-text').textContent = memoryUsage + '%';

    // Update network I/O
    const networkUsage = Math.min(80, (systemStatus.llm_requests || 0) / 10 + 10);
    document.querySelector('#network-usage-bar').style.width = networkUsage + '%';
    document.querySelector('#network-usage-text').textContent = networkUsage + '%';
}

// Update agents list display
function updateAgentsList() {
    agents.forEach(agent => {
        const agentElement = document.querySelector(`[data-agent="${agent.id}"]`);
        if (agentElement) {
            // Update status indicator
            const statusDot = agentElement.querySelector('.status-dot');
            if (statusDot) {
                statusDot.className = `status-dot w-3 h-3 rounded-full mr-3 ${getStatusColor(agent.status)}`;
            }
            
            // Update agent info
            const nameElement = agentElement.querySelector('.font-medium');
            const descElement = agentElement.querySelector('.text-xs.text-gray-400');
            if (nameElement) nameElement.textContent = agent.name;
            if (descElement) descElement.textContent = agent.capabilities.join(', ').substring(0, 50) + '...';
        }
    });
}

// Update agent metrics
function updateAgentMetrics() {
    const activeCount = agents.filter(a => a.status === 'active').length;
    document.getElementById('active-agents').textContent = activeCount;
}

// Setup Socket.IO listeners
function setupSocketListeners() {
    socket.on('connect', () => {
        console.log('🔗 Connected to server');
        socket.emit('subscribe_updates');
    });

    socket.on('disconnect', () => {
        console.log('🔌 Disconnected from server');
    });

    socket.on('system_update', (data) => {
        systemStatus = { ...systemStatus, ...data };
        updateSystemMetrics();
        updateSystemHealth();
    });

    socket.on('agent_update', (data) => {
        const agentIndex = agents.findIndex(a => a.id === data.agent_id);
        if (agentIndex !== -1) {
            agents[agentIndex] = { ...agents[agentIndex], ...data };
            updateAgentsList();
            updateAgentMetrics();
        }
    });

    socket.on('activity_log', (data) => {
        addActivityLog(data);
    });

    socket.on('agent_status_update', (data) => {
        updateAgentStatus(data.agent_id, data.status);
    });

    socket.on('system_metrics', (data) => {
        updateSystemMetrics(data);
    });

    socket.on('new_log_entry', (data) => {
        addLogEntry(data);
    });
}

// Add activity log entry
function addActivityLog(activity) {
    const container = document.getElementById('recent-activities');
    const activityElement = document.createElement('div');
    activityElement.className = 'flex items-center space-x-3 p-3 bg-slate-700 rounded-lg';
    
    const statusColor = activity.type === 'success' ? 'bg-green-500' : 
                      activity.type === 'warning' ? 'bg-yellow-500' : 'bg-blue-500';
    
    activityElement.innerHTML = `
        <div class="w-3 h-3 ${statusColor} rounded-full"></div>
        <div class="flex-1">
            <div class="text-sm font-medium">${activity.message}</div>
            <div class="text-xs text-gray-400">${activity.timestamp}</div>
        </div>
    `;
    
    container.prepend(activityElement);
    
    // Keep only last 10 activities
    while (container.children.length > 10) {
        container.removeChild(container.lastChild);
    }
}

// Handle agent actions
async function handleAgentAction(agentId, action) {
    try {
        const response = await fetch(`/api/agents/${agentId}/${action}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' }
        });
        
        const data = await response.json();
        if (data.success) {
            console.log(`Agent ${agentId} ${action} successful`);
            // Refresh agent data
            await loadAgents();
        } else {
            console.error(`Agent ${agentId} ${action} failed:`, data.error);
        }
    } catch (error) {
        console.error(`Error with agent ${agentId} ${action}:`, error);
    }
}

// Handle emergency stop
async function handleEmergencyStop() {
    if (confirm('Are you sure you want to stop all agents?')) {
        try {
            const response = await fetch('/api/system/emergency-stop', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' }
            });
            
            const data = await response.json();
            if (data.success) {
                alert('Emergency stop initiated');
            } else {
                alert('Emergency stop failed: ' + data.error);
            }
        } catch (error) {
            alert('Emergency stop error: ' + error.message);
        }
    }
}

// Handle restart all
async function handleRestartAll() {
    if (confirm('Are you sure you want to restart all agents?')) {
        try {
            const response = await fetch('/api/system/restart-all', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' }
            });
            
            const data = await response.json();
            if (data.success) {
                alert('System restart initiated');
            } else {
                alert('System restart failed: ' + data.error);
            }
        } catch (error) {
            alert('System restart error: ' + error.message);
        }
    }
}

// Update metrics periodically
function updateMetrics() {
    // Update timestamps
    const now = new Date();
    document.querySelectorAll('.text-xs.text-gray-400').forEach(el => {
        if (el.textContent.includes('ago')) {
            // Update relative timestamps
            const match = el.textContent.match(/(\d+) minutes ago/);
            if (match) {
                const minutes = parseInt(match[1]) + 1;
                el.textContent = `${minutes} minutes ago`;
            }
        }
    });
}

function getStatusColor(status) {
    switch (status) {
        case 'active': return 'bg-green-500';
        case 'running': return 'bg-blue-500';
        case 'error': return 'bg-red-500';
        case 'paused': return 'bg-yellow-500';
        default: return 'bg-gray-500';
    }
}

function addLogEntry(logData) {
    const logContainer = document.getElementById('log-container');
    if (!logContainer) return;
    const logEntry = document.createElement('div');
    logEntry.className = `text-${logData.level === 'ERROR' ? 'red' : logData.level === 'WARN' ? 'yellow' : 'green'}-400`;
    logEntry.textContent = `[${logData.timestamp}] [${logData.level}] ${logData.message}`;
    
    logContainer.appendChild(logEntry);
    logContainer.scrollTop = logContainer.scrollHeight;
}

function loadAgentDetails(agentId) {
    socket.emit('get_agent_details', { agent_id: agentId });
}

function updateAgentStatus(agentId, status) {
    const agentItem = document.querySelector(`[data-agent="${agentId}"]`);
    if (agentItem) {
        const statusDot = agentItem.querySelector('.status-dot');
        if(statusDot) {
            statusDot.className = `status-dot w-3 h-3 rounded-full mr-3 ${getStatusColor(status)}`;
        }
    }
}

// Initialize dashboard when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    initializeDashboard();
    
    // Bind event handlers for control buttons
    document.getElementById('emergency-stop')?.addEventListener('click', handleEmergencyStop);
    document.getElementById('restart-all')?.addEventListener('click', handleRestartAll);
    
    // Bind agent action buttons
    document.querySelectorAll('.agent-action').forEach(button => {
        button.addEventListener('click', (e) => {
            e.stopPropagation();
            const action = button.dataset.action;
            const agentItem = button.closest('.agent-item');
            const agentId = agentItem.dataset.agent;
            
            handleAgentAction(agentId, action);
            
            // Visual feedback
            button.classList.add('animate-pulse');
            setTimeout(() => button.classList.remove('animate-pulse'), 1000);
        });
    });

    // Group toggle functionality
    document.querySelectorAll('.group-toggle').forEach(toggle => {
        toggle.addEventListener('click', () => {
            const content = toggle.nextElementSibling;
            const icon = toggle.querySelector('i.fa-chevron-down');
            
            content.classList.toggle('hidden');
            icon.classList.toggle('rotate-180');
        });
    });

    // Tab switching
    document.querySelectorAll('.tab-button').forEach(button => {
        button.addEventListener('click', () => {
            const targetTab = button.dataset.tab;
            
            // Update button states
            document.querySelectorAll('.tab-button').forEach(btn => {
                btn.classList.remove('active', 'bg-blue-600', 'text-white');
                btn.classList.add('bg-slate-700', 'hover:bg-slate-600');
            });
            button.classList.add('active', 'bg-blue-600', 'text-white');
            button.classList.remove('bg-slate-700', 'hover:bg-slate-600');
            
            // Show target tab content
            document.querySelectorAll('.tab-content').forEach(content => {
                content.classList.add('hidden');
            });
            document.getElementById(targetTab + '-tab').classList.remove('hidden');
        });
    });

    // Agent selection
    document.querySelectorAll('.agent-item').forEach(item => {
        item.addEventListener('click', () => {
            // Remove previous selection
            document.querySelectorAll('.agent-item > div').forEach(div => {
                div.classList.remove('ring-2', 'ring-blue-500');
            });
            
            // Add selection to clicked item
            item.querySelector('div').classList.add('ring-2', 'ring-blue-500');
            
            const agentId = item.dataset.agent;
            loadAgentDetails(agentId);
        });
    });
});
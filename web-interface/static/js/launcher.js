/**
 * Unified Launcher Integration - JavaScript for interacting with the unified launcher
 * Made with ❤️ by Mulky Malikul Dhaher in Indonesia 🇮🇩
 */

// Launcher API base URL
const LAUNCHER_API_BASE = '/api/launcher';

/**
 * Get the system status from the launcher
 * @returns {Promise<Object>} System status
 */
async function getLauncherStatus() {
    try {
        const response = await fetch(`${LAUNCHER_API_BASE}/status`);
        const data = await response.json();
        
        if (data.success) {
            return data.data;
        } else {
            console.error('Error getting launcher status:', data.error);
            return null;
        }
    } catch (error) {
        console.error('Error fetching launcher status:', error);
        return null;
    }
}

/**
 * Start the web UI
 * @param {boolean} background Whether to run in the background
 * @returns {Promise<Object>} Result
 */
async function startWebUI(background = true) {
    try {
        const response = await fetch(`${LAUNCHER_API_BASE}/web-ui/start`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ background })
        });
        
        return await response.json();
    } catch (error) {
        console.error('Error starting web UI:', error);
        return { success: false, error: error.message };
    }
}

/**
 * Stop the web UI
 * @returns {Promise<Object>} Result
 */
async function stopWebUI() {
    try {
        const response = await fetch(`${LAUNCHER_API_BASE}/web-ui/stop`, {
            method: 'POST'
        });
        
        return await response.json();
    } catch (error) {
        console.error('Error stopping web UI:', error);
        return { success: false, error: error.message };
    }
}

/**
 * Start an agent
 * @param {string} agentName Name of the agent to start
 * @param {boolean} background Whether to run in the background
 * @returns {Promise<Object>} Result
 */
async function startAgent(agentName, background = true) {
    try {
        const response = await fetch(`${LAUNCHER_API_BASE}/agents/start`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ agent_name: agentName, background })
        });
        
        return await response.json();
    } catch (error) {
        console.error(`Error starting agent ${agentName}:`, error);
        return { success: false, error: error.message };
    }
}

/**
 * Stop an agent
 * @param {string} agentName Name of the agent to stop
 * @returns {Promise<Object>} Result
 */
async function stopAgent(agentName) {
    try {
        const response = await fetch(`${LAUNCHER_API_BASE}/agents/stop`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ agent_name: agentName })
        });
        
        return await response.json();
    } catch (error) {
        console.error(`Error stopping agent ${agentName}:`, error);
        return { success: false, error: error.message };
    }
}

/**
 * Start all agents
 * @param {boolean} background Whether to run in the background
 * @returns {Promise<Object>} Result
 */
async function startAllAgents(background = true) {
    try {
        const response = await fetch(`${LAUNCHER_API_BASE}/agents/start-all`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ background })
        });
        
        return await response.json();
    } catch (error) {
        console.error('Error starting all agents:', error);
        return { success: false, error: error.message };
    }
}

/**
 * Stop all agents
 * @returns {Promise<Object>} Result
 */
async function stopAllAgents() {
    try {
        const response = await fetch(`${LAUNCHER_API_BASE}/agents/stop-all`, {
            method: 'POST'
        });
        
        return await response.json();
    } catch (error) {
        console.error('Error stopping all agents:', error);
        return { success: false, error: error.message };
    }
}

/**
 * Start an engine
 * @param {string} engineName Name of the engine to start
 * @returns {Promise<Object>} Result
 */
async function startEngine(engineName) {
    try {
        const response = await fetch(`${LAUNCHER_API_BASE}/engines/start`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ engine_name: engineName })
        });
        
        return await response.json();
    } catch (error) {
        console.error(`Error starting engine ${engineName}:`, error);
        return { success: false, error: error.message };
    }
}

/**
 * Stop an engine
 * @param {string} engineName Name of the engine to stop
 * @returns {Promise<Object>} Result
 */
async function stopEngine(engineName) {
    try {
        const response = await fetch(`${LAUNCHER_API_BASE}/engines/stop`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ engine_name: engineName })
        });
        
        return await response.json();
    } catch (error) {
        console.error(`Error stopping engine ${engineName}:`, error);
        return { success: false, error: error.message };
    }
}

/**
 * Start all engines
 * @returns {Promise<Object>} Result
 */
async function startAllEngines() {
    try {
        const response = await fetch(`${LAUNCHER_API_BASE}/engines/start-all`, {
            method: 'POST'
        });
        
        return await response.json();
    } catch (error) {
        console.error('Error starting all engines:', error);
        return { success: false, error: error.message };
    }
}

/**
 * Stop all engines
 * @returns {Promise<Object>} Result
 */
async function stopAllEngines() {
    try {
        const response = await fetch(`${LAUNCHER_API_BASE}/engines/stop-all`, {
            method: 'POST'
        });
        
        return await response.json();
    } catch (error) {
        console.error('Error stopping all engines:', error);
        return { success: false, error: error.message };
    }
}

/**
 * Start all components (web UI, agents, engines)
 * @param {boolean} background Whether to run in the background
 * @returns {Promise<Object>} Result
 */
async function startAll(background = true) {
    try {
        const response = await fetch(`${LAUNCHER_API_BASE}/start-all`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ background })
        });
        
        return await response.json();
    } catch (error) {
        console.error('Error starting all components:', error);
        return { success: false, error: error.message };
    }
}

/**
 * Stop all components (web UI, agents, engines)
 * @returns {Promise<Object>} Result
 */
async function stopAll() {
    try {
        const response = await fetch(`${LAUNCHER_API_BASE}/stop-all`, {
            method: 'POST'
        });
        
        return await response.json();
    } catch (error) {
        console.error('Error stopping all components:', error);
        return { success: false, error: error.message };
    }
}

/**
 * Update the UI with launcher status
 * @param {Object} status Launcher status
 */
function updateLauncherUI(status) {
    if (!status) return;
    
    // Update system info
    const systemInfo = status.system || {};
    document.querySelectorAll('.system-name').forEach(el => {
        el.textContent = systemInfo.name || 'AI MultiColony Ecosystem';
    });
    
    document.querySelectorAll('.system-version').forEach(el => {
        el.textContent = systemInfo.version || '7.2.0';
    });
    
    document.querySelectorAll('.system-status').forEach(el => {
        el.textContent = systemInfo.status || 'Unknown';
        
        // Update status indicator color
        const indicator = el.closest('.status-container')?.querySelector('.status-indicator');
        if (indicator) {
            indicator.className = 'status-indicator';
            if (systemInfo.status === 'running') {
                indicator.classList.add('bg-green-500');
            } else if (systemInfo.status === 'stopped') {
                indicator.classList.add('bg-red-500');
            } else {
                indicator.classList.add('bg-yellow-500');
            }
        }
    });
    
    // Update component counts
    const components = status.components || {};
    
    // Update agent counts
    const agents = components.agents || {};
    document.querySelectorAll('.active-agents-count').forEach(el => {
        el.textContent = agents.running || 0;
    });
    
    document.querySelectorAll('.total-agents-count').forEach(el => {
        el.textContent = agents.total || 0;
    });
    
    // Update engine counts
    const engines = components.engines || {};
    document.querySelectorAll('.active-engines-count').forEach(el => {
        el.textContent = engines.running || 0;
    });
    
    document.querySelectorAll('.total-engines-count').forEach(el => {
        el.textContent = engines.total || 0;
    });
    
    // Update web UI status
    const webUI = components.web_ui || {};
    document.querySelectorAll('.web-ui-status').forEach(el => {
        el.textContent = webUI.running ? 'Running' : 'Stopped';
        
        // Update status indicator color
        const indicator = el.closest('.status-container')?.querySelector('.status-indicator');
        if (indicator) {
            indicator.className = 'status-indicator';
            if (webUI.running) {
                indicator.classList.add('bg-green-500');
            } else {
                indicator.classList.add('bg-red-500');
            }
        }
    });
    
    // Update agent list if available
    const agentList = document.getElementById('agent-list');
    if (agentList && agents.statuses) {
        agentList.innerHTML = '';
        
        Object.entries(agents.statuses).forEach(([agentName, agentStatus]) => {
            const agentItem = document.createElement('div');
            agentItem.className = 'bg-slate-700 rounded-lg p-4 mb-2';
            
            const statusColor = agentStatus.running ? 'bg-green-500' : 'bg-red-500';
            
            agentItem.innerHTML = `
                <div class="flex items-center justify-between">
                    <div class="flex items-center">
                        <div class="w-3 h-3 ${statusColor} rounded-full mr-2"></div>
                        <span class="font-semibold">${agentName}</span>
                    </div>
                    <div class="flex space-x-2">
                        <button class="start-agent-btn bg-green-600 hover:bg-green-700 text-white px-2 py-1 rounded text-xs" data-agent="${agentName}">
                            <i class="fas fa-play mr-1"></i>Start
                        </button>
                        <button class="stop-agent-btn bg-red-600 hover:bg-red-700 text-white px-2 py-1 rounded text-xs" data-agent="${agentName}">
                            <i class="fas fa-stop mr-1"></i>Stop
                        </button>
                    </div>
                </div>
                <div class="text-xs text-gray-400 mt-1">${agentStatus.description || ''}</div>
            `;
            
            agentList.appendChild(agentItem);
        });
        
        // Add event listeners to buttons
        document.querySelectorAll('.start-agent-btn').forEach(btn => {
            btn.addEventListener('click', async () => {
                const agentName = btn.dataset.agent;
                const result = await startAgent(agentName);
                
                if (result.success) {
                    showNotification(`Started agent ${agentName}`, 'success');
                } else {
                    showNotification(`Failed to start agent ${agentName}: ${result.error}`, 'error');
                }
                
                // Refresh status after a short delay
                setTimeout(refreshLauncherStatus, 1000);
            });
        });
        
        document.querySelectorAll('.stop-agent-btn').forEach(btn => {
            btn.addEventListener('click', async () => {
                const agentName = btn.dataset.agent;
                const result = await stopAgent(agentName);
                
                if (result.success) {
                    showNotification(`Stopped agent ${agentName}`, 'success');
                } else {
                    showNotification(`Failed to stop agent ${agentName}: ${result.error}`, 'error');
                }
                
                // Refresh status after a short delay
                setTimeout(refreshLauncherStatus, 1000);
            });
        });
    }
    
    // Update engine list if available
    const engineList = document.getElementById('engine-list');
    if (engineList && engines.statuses) {
        engineList.innerHTML = '';
        
        Object.entries(engines.statuses).forEach(([engineName, engineStatus]) => {
            const engineItem = document.createElement('div');
            engineItem.className = 'bg-slate-700 rounded-lg p-4 mb-2';
            
            const statusColor = engineStatus.running ? 'bg-green-500' : 'bg-red-500';
            const enabledClass = engineStatus.enabled ? '' : 'opacity-50';
            
            engineItem.innerHTML = `
                <div class="flex items-center justify-between ${enabledClass}">
                    <div class="flex items-center">
                        <div class="w-3 h-3 ${statusColor} rounded-full mr-2"></div>
                        <span class="font-semibold">${engineName}</span>
                    </div>
                    <div class="flex space-x-2">
                        <button class="start-engine-btn bg-green-600 hover:bg-green-700 text-white px-2 py-1 rounded text-xs" data-engine="${engineName}" ${!engineStatus.enabled ? 'disabled' : ''}>
                            <i class="fas fa-play mr-1"></i>Start
                        </button>
                        <button class="stop-engine-btn bg-red-600 hover:bg-red-700 text-white px-2 py-1 rounded text-xs" data-engine="${engineName}" ${!engineStatus.running ? 'disabled' : ''}>
                            <i class="fas fa-stop mr-1"></i>Stop
                        </button>
                    </div>
                </div>
                <div class="text-xs text-gray-400 mt-1">${engineStatus.description || ''}</div>
                <div class="text-xs text-gray-400 mt-1">Interval: ${engineStatus.interval || 0}s</div>
            `;
            
            engineList.appendChild(engineItem);
        });
        
        // Add event listeners to buttons
        document.querySelectorAll('.start-engine-btn').forEach(btn => {
            btn.addEventListener('click', async () => {
                const engineName = btn.dataset.engine;
                const result = await startEngine(engineName);
                
                if (result.success) {
                    showNotification(`Started engine ${engineName}`, 'success');
                } else {
                    showNotification(`Failed to start engine ${engineName}: ${result.error}`, 'error');
                }
                
                // Refresh status after a short delay
                setTimeout(refreshLauncherStatus, 1000);
            });
        });
        
        document.querySelectorAll('.stop-engine-btn').forEach(btn => {
            btn.addEventListener('click', async () => {
                const engineName = btn.dataset.engine;
                const result = await stopEngine(engineName);
                
                if (result.success) {
                    showNotification(`Stopped engine ${engineName}`, 'success');
                } else {
                    showNotification(`Failed to stop engine ${engineName}: ${result.error}`, 'error');
                }
                
                // Refresh status after a short delay
                setTimeout(refreshLauncherStatus, 1000);
            });
        });
    }
}

/**
 * Show a notification
 * @param {string} message Notification message
 * @param {string} type Notification type (success, error, warning, info)
 */
function showNotification(message, type = 'info') {
    // Check if notification container exists
    let container = document.getElementById('notification-container');
    
    // Create container if it doesn't exist
    if (!container) {
        container = document.createElement('div');
        container.id = 'notification-container';
        container.className = 'fixed top-4 right-4 z-50 flex flex-col space-y-2';
        document.body.appendChild(container);
    }
    
    // Create notification element
    const notification = document.createElement('div');
    notification.className = 'rounded-lg p-4 flex items-center shadow-lg transform transition-all duration-300 ease-in-out';
    
    // Set background color based on type
    switch (type) {
        case 'success':
            notification.classList.add('bg-green-600', 'text-white');
            break;
        case 'error':
            notification.classList.add('bg-red-600', 'text-white');
            break;
        case 'warning':
            notification.classList.add('bg-yellow-600', 'text-white');
            break;
        case 'info':
        default:
            notification.classList.add('bg-blue-600', 'text-white');
            break;
    }
    
    // Set icon based on type
    let icon;
    switch (type) {
        case 'success':
            icon = 'fa-check-circle';
            break;
        case 'error':
            icon = 'fa-exclamation-circle';
            break;
        case 'warning':
            icon = 'fa-exclamation-triangle';
            break;
        case 'info':
        default:
            icon = 'fa-info-circle';
            break;
    }
    
    // Set content
    notification.innerHTML = `
        <i class="fas ${icon} mr-2"></i>
        <span>${message}</span>
        <button class="ml-4 text-white hover:text-gray-200">
            <i class="fas fa-times"></i>
        </button>
    `;
    
    // Add to container
    container.appendChild(notification);
    
    // Add animation
    setTimeout(() => {
        notification.classList.add('translate-x-0', 'opacity-100');
    }, 10);
    
    // Add close button event listener
    const closeButton = notification.querySelector('button');
    closeButton.addEventListener('click', () => {
        notification.classList.add('opacity-0', 'translate-x-full');
        setTimeout(() => {
            notification.remove();
        }, 300);
    });
    
    // Auto-remove after 5 seconds
    setTimeout(() => {
        notification.classList.add('opacity-0', 'translate-x-full');
        setTimeout(() => {
            notification.remove();
        }, 300);
    }, 5000);
}

/**
 * Refresh the launcher status
 */
async function refreshLauncherStatus() {
    const status = await getLauncherStatus();
    updateLauncherUI(status);
}

/**
 * Initialize the launcher integration
 */
function initLauncherIntegration() {
    // Initial status refresh
    refreshLauncherStatus();
    
    // Set up periodic refresh (every 10 seconds)
    setInterval(refreshLauncherStatus, 10000);
    
    // Set up event listeners for global control buttons
    document.getElementById('emergency-stop')?.addEventListener('click', async () => {
        const result = await stopAll();
        
        if (result.success) {
            showNotification('Emergency stop initiated for all components', 'success');
        } else {
            showNotification(`Emergency stop failed: ${result.error}`, 'error');
        }
        
        // Refresh status after a short delay
        setTimeout(refreshLauncherStatus, 1000);
    });
    
    document.getElementById('restart-all')?.addEventListener('click', async () => {
        // Stop all components
        await stopAll();
        
        // Wait a moment
        await new Promise(resolve => setTimeout(resolve, 1000));
        
        // Start all components
        const result = await startAll();
        
        if (result.success) {
            showNotification('Restart initiated for all components', 'success');
        } else {
            showNotification(`Restart failed: ${result.error}`, 'error');
        }
        
        // Refresh status after a short delay
        setTimeout(refreshLauncherStatus, 1000);
    });
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', initLauncherIntegration);
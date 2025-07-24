/**
 * Dynamic Dashboard JavaScript
 * Main controller for the AI MultiColony Ecosystem interface
 */

class DynamicDashboard {
    constructor() {
        this.socket = null;
        this.agents = new Map();
        this.currentView = 'dashboard';
        this.notifications = [];
        this.isLoading = true;
        
        this.init();
    }
    
    async init() {
        try {
            // Initialize Socket.IO connection
            await this.initSocket();
            
            // Setup event listeners
            this.setupEventListeners();
            
            // Load initial data
            await this.loadInitialData();
            
            // Hide loading screen
            this.hideLoadingScreen();
            
            // Start real-time updates
            this.startRealTimeUpdates();
            
            console.log('🚀 Dynamic Dashboard initialized successfully');
        } catch (error) {
            console.error('❌ Error initializing dashboard:', error);
            this.showNotification('Error initializing dashboard', 'error');
        }
    }
    
    async initSocket() {
        return new Promise((resolve, reject) => {
            try {
                this.socket = io();
                
                this.socket.on('connect', () => {
                    console.log('✅ Socket.IO connected');
                    this.updateSystemStatus('online');
                    resolve();
                });
                
                this.socket.on('disconnect', () => {
                    console.log('❌ Socket.IO disconnected');
                    this.updateSystemStatus('offline');
                });
                
                this.socket.on('agent_update', (data) => {
                    this.handleAgentUpdate(data);
                });
                
                this.socket.on('system_log', (data) => {
                    this.handleSystemLog(data);
                });
                
                this.socket.on('notification', (data) => {
                    this.showNotification(data.message, data.type);
                });
                
                // Connection timeout
                setTimeout(() => {
                    if (!this.socket.connected) {
                        reject(new Error('Socket connection timeout'));
                    }
                }, 5000);
                
            } catch (error) {
                reject(error);
            }
        });
    }
    
    setupEventListeners() {
        // Sidebar toggle
        document.getElementById('sidebar-toggle').addEventListener('click', () => {
            this.toggleSidebar();
        });
        
        // Navigation
        document.querySelectorAll('.nav-item').forEach(item => {
            item.addEventListener('click', (e) => {
                e.preventDefault();
                const view = item.dataset.view;
                if (view) {
                    this.switchView(view);
                }
            });
        });
        
        // Global search
        const globalSearch = document.getElementById('global-search');
        globalSearch.addEventListener('input', (e) => {
            this.handleGlobalSearch(e.target.value);
        });
        
        globalSearch.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                this.executeSearch(e.target.value);
            }
        });
        
        // Voice search
        document.getElementById('voice-search').addEventListener('click', () => {
            this.startVoiceSearch();
        });
        
        // Refresh dashboard
        document.getElementById('refresh-dashboard').addEventListener('click', () => {
            this.refreshDashboard();
        });
        
        // Quick actions
        document.getElementById('emergency-stop').addEventListener('click', () => {
            this.emergencyStop();
        });
        
        document.getElementById('system-optimize').addEventListener('click', () => {
            this.optimizeSystem();
        });
        
        // Add agent button
        document.getElementById('add-agent-btn').addEventListener('click', () => {
            this.switchView('agent-creator');
        });
        
        // Clear activity
        document.getElementById('clear-activity').addEventListener('click', () => {
            this.clearActivity();
        });
        
        // Notifications
        document.getElementById('notifications-btn').addEventListener('click', () => {
            this.toggleNotifications();
        });
        
        // Modal close
        document.querySelectorAll('.modal-close').forEach(btn => {
            btn.addEventListener('click', () => {
                this.closeModal();
            });
        });
        
        // Window resize
        window.addEventListener('resize', () => {
            this.handleResize();
        });
        
        // Keyboard shortcuts
        document.addEventListener('keydown', (e) => {
            this.handleKeyboardShortcuts(e);
        });
    }
    
    async loadInitialData() {
        try {
            // Load agents
            await this.loadAgents();
            
            // Load system status
            await this.loadSystemStatus();
            
            // Load activity feed
            await this.loadActivityFeed();
            
            // Update UI
            this.updateDashboard();
            
        } catch (error) {
            console.error('❌ Error loading initial data:', error);
            throw error;
        }
    }
    
    async loadAgents() {
        try {
            const response = await fetch('/api/agents/list');
            const data = await response.json();
            
            if (data.success) {
                this.agents.clear();
                data.agents.forEach(agent => {
                    this.agents.set(agent.id, agent);
                });
                
                this.updateAgentsDisplay();
                this.updateAgentsCount();
                
                console.log(`✅ Loaded ${this.agents.size} agents`);
            } else {
                throw new Error(data.error || 'Failed to load agents');
            }
        } catch (error) {
            console.error('❌ Error loading agents:', error);
            this.showNotification('Failed to load agents', 'error');
        }
    }
    
    async loadSystemStatus() {
        try {
            const response = await fetch('/api/system/status');
            const data = await response.json();
            
            if (data.success) {
                this.updateSystemStats(data.status);
                console.log('✅ System status loaded');
            } else {
                throw new Error(data.error || 'Failed to load system status');
            }
        } catch (error) {
            console.error('❌ Error loading system status:', error);
            this.showNotification('Failed to load system status', 'error');
        }
    }
    
    async loadActivityFeed() {
        try {
            // Simulate activity feed for now
            const activities = [
                {
                    id: 1,
                    type: 'success',
                    title: 'Agent Started',
                    description: 'Chatbot Agent started successfully',
                    timestamp: new Date().toISOString()
                },
                {
                    id: 2,
                    type: 'info',
                    title: 'System Update',
                    description: 'Dynamic dashboard initialized',
                    timestamp: new Date().toISOString()
                }
            ];
            
            this.updateActivityFeed(activities);
            console.log('✅ Activity feed loaded');
        } catch (error) {
            console.error('❌ Error loading activity feed:', error);
        }
    }
    
    hideLoadingScreen() {
        const loadingScreen = document.getElementById('loading-screen');
        const app = document.getElementById('app');
        
        setTimeout(() => {
            loadingScreen.style.display = 'none';
            app.style.display = 'grid';
            this.isLoading = false;
        }, 1000);
    }
    
    toggleSidebar() {
        const sidebar = document.getElementById('sidebar');
        sidebar.classList.toggle('open');
    }
    
    switchView(viewName) {
        // Hide all views
        document.querySelectorAll('.view').forEach(view => {
            view.classList.remove('active');
        });
        
        // Show target view
        const targetView = document.getElementById(`${viewName}-view`);
        if (targetView) {
            targetView.classList.add('active');
            this.currentView = viewName;
            
            // Update navigation
            document.querySelectorAll('.nav-item').forEach(item => {
                item.classList.remove('active');
            });
            
            const navItem = document.querySelector(`[data-view="${viewName}"]`);
            if (navItem) {
                navItem.classList.add('active');
            }
            
            // Load view-specific data
            this.loadViewData(viewName);
            
            console.log(`📄 Switched to ${viewName} view`);
        }
    }
    
    async loadViewData(viewName) {
        switch (viewName) {
            case 'agents':
                await this.loadAgentsView();
                break;
            case 'chat':
                this.initChatView();
                break;
            case 'agent-creator':
                this.initAgentCreator();
                break;
            case 'monitoring':
                await this.loadMonitoringView();
                break;
            default:
                break;
        }
    }
    
    async loadAgentsView() {
        // This will be implemented in agent-manager.js
        if (window.AgentManager) {
            window.AgentManager.loadAgentsView();
        }
    }
    
    initChatView() {
        // This will be implemented in chat-interface.js
        if (window.ChatInterface) {
            window.ChatInterface.init();
        }
    }
    
    initAgentCreator() {
        // This will be implemented in agent-creator.js
        if (window.AgentCreator) {
            window.AgentCreator.init();
        }
    }
    
    async loadMonitoringView() {
        // Load monitoring data
        console.log('📊 Loading monitoring view');
    }
    
    updateAgentsDisplay() {
        const agentsGrid = document.getElementById('agents-grid');
        agentsGrid.innerHTML = '';
        
        this.agents.forEach(agent => {
            const agentCard = this.createAgentCard(agent);
            agentsGrid.appendChild(agentCard);
        });
    }
    
    createAgentCard(agent) {
        const card = document.createElement('div');
        card.className = 'agent-card';
        card.dataset.agentId = agent.id;
        
        const statusClass = agent.status === 'active' ? 'active' : 'inactive';
        const statusIcon = agent.status === 'active' ? '✅' : '❌';
        
        card.innerHTML = `
            <div class="agent-header">
                <div class="agent-info">
                    <div class="agent-avatar">
                        <i class="fas fa-robot"></i>
                    </div>
                    <div class="agent-details">
                        <h3>${agent.name}</h3>
                        <p>${agent.id}</p>
                    </div>
                </div>
                <div class="agent-status ${statusClass}">
                    ${statusIcon} ${agent.status}
                </div>
            </div>
            <div class="agent-description">
                ${agent.description || 'No description available'}
            </div>
            <div class="agent-capabilities">
                ${(agent.capabilities || []).slice(0, 3).map(cap => 
                    `<span class="capability-tag">${cap}</span>`
                ).join('')}
                ${agent.capabilities && agent.capabilities.length > 3 ? 
                    `<span class="capability-tag">+${agent.capabilities.length - 3} more</span>` : ''
                }
            </div>
            <div class="agent-actions">
                <button class="btn btn-primary btn-sm" onclick="dashboard.viewAgent('${agent.id}')">
                    <i class="fas fa-eye"></i> View
                </button>
                <button class="btn btn-secondary btn-sm" onclick="dashboard.configureAgent('${agent.id}')">
                    <i class="fas fa-cog"></i> Configure
                </button>
            </div>
        `;
        
        return card;
    }
    
    updateAgentsCount() {
        const activeAgents = Array.from(this.agents.values()).filter(agent => agent.status === 'active').length;
        
        document.getElementById('agents-count').textContent = this.agents.size;
        document.getElementById('active-agents-count').textContent = activeAgents;
    }
    
    updateSystemStats(stats) {
        if (stats) {
            document.getElementById('running-tasks-count').textContent = stats.running_tasks || 0;
            document.getElementById('system-performance').textContent = stats.performance || '98%';
            document.getElementById('system-uptime').textContent = stats.uptime || '0h 0m';
        }
    }
    
    updateActivityFeed(activities) {
        const activityFeed = document.getElementById('activity-feed');
        activityFeed.innerHTML = '';
        
        activities.forEach(activity => {
            const activityItem = this.createActivityItem(activity);
            activityFeed.appendChild(activityItem);
        });
    }
    
    createActivityItem(activity) {
        const item = document.createElement('div');
        item.className = 'activity-item';
        
        const timeAgo = this.getTimeAgo(new Date(activity.timestamp));
        
        item.innerHTML = `
            <div class="activity-icon ${activity.type}">
                <i class="fas fa-${this.getActivityIcon(activity.type)}"></i>
            </div>
            <div class="activity-content">
                <h4>${activity.title}</h4>
                <p>${activity.description}</p>
            </div>
            <div class="activity-time">${timeAgo}</div>
        `;
        
        return item;
    }
    
    getActivityIcon(type) {
        const icons = {
            success: 'check',
            warning: 'exclamation-triangle',
            error: 'times',
            info: 'info'
        };
        return icons[type] || 'info';
    }
    
    getTimeAgo(date) {
        const now = new Date();
        const diff = now - date;
        const minutes = Math.floor(diff / 60000);
        
        if (minutes < 1) return 'Just now';
        if (minutes < 60) return `${minutes}m ago`;
        
        const hours = Math.floor(minutes / 60);
        if (hours < 24) return `${hours}h ago`;
        
        const days = Math.floor(hours / 24);
        return `${days}d ago`;
    }
    
    updateSystemStatus(status) {
        const statusIndicator = document.querySelector('.status-indicator');
        const statusText = statusIndicator.nextElementSibling;
        
        if (status === 'online') {
            statusIndicator.classList.add('online');
            statusText.textContent = 'Online';
        } else {
            statusIndicator.classList.remove('online');
            statusText.textContent = 'Offline';
        }
    }
    
    handleAgentUpdate(data) {
        if (data.agent_id && this.agents.has(data.agent_id)) {
            const agent = this.agents.get(data.agent_id);
            Object.assign(agent, data);
            this.updateAgentsDisplay();
            this.updateAgentsCount();
        }
    }
    
    handleSystemLog(data) {
        // Add to activity feed
        const activity = {
            id: Date.now(),
            type: 'info',
            title: 'System Log',
            description: data.message,
            timestamp: new Date().toISOString()
        };
        
        const activityFeed = document.getElementById('activity-feed');
        const activityItem = this.createActivityItem(activity);
        activityFeed.insertBefore(activityItem, activityFeed.firstChild);
        
        // Keep only last 50 items
        while (activityFeed.children.length > 50) {
            activityFeed.removeChild(activityFeed.lastChild);
        }
    }
    
    handleGlobalSearch(query) {
        // Implement search suggestions
        console.log('🔍 Search query:', query);
    }
    
    executeSearch(query) {
        if (!query.trim()) return;
        
        // Check if it's a command
        if (query.startsWith('/')) {
            this.executeCommand(query.slice(1));
        } else {
            // Regular search
            this.performSearch(query);
        }
    }
    
    executeCommand(command) {
        const [cmd, ...args] = command.split(' ');
        
        switch (cmd.toLowerCase()) {
            case 'agents':
                this.switchView('agents');
                break;
            case 'chat':
                this.switchView('chat');
                break;
            case 'create':
                this.switchView('agent-creator');
                break;
            case 'status':
                this.showSystemStatus();
                break;
            default:
                this.showNotification(`Unknown command: ${cmd}`, 'warning');
        }
    }
    
    performSearch(query) {
        // Implement search functionality
        console.log('🔍 Performing search:', query);
        this.showNotification(`Searching for: ${query}`, 'info');
    }
    
    startVoiceSearch() {
        if (window.VoiceInterface) {
            window.VoiceInterface.startListening();
        } else {
            this.showNotification('Voice interface not available', 'warning');
        }
    }
    
    async refreshDashboard() {
        this.showNotification('Refreshing dashboard...', 'info');
        
        try {
            await this.loadInitialData();
            this.showNotification('Dashboard refreshed successfully', 'success');
        } catch (error) {
            this.showNotification('Failed to refresh dashboard', 'error');
        }
    }
    
    async emergencyStop() {
        if (confirm('Are you sure you want to perform an emergency stop? This will stop all agents.')) {
            try {
                const response = await fetch('/api/system/emergency-stop', {
                    method: 'POST'
                });
                
                const data = await response.json();
                
                if (data.success) {
                    this.showNotification('Emergency stop executed', 'warning');
                } else {
                    throw new Error(data.error);
                }
            } catch (error) {
                this.showNotification('Failed to execute emergency stop', 'error');
            }
        }
    }
    
    async optimizeSystem() {
        this.showNotification('Starting system optimization...', 'info');
        
        try {
            // Simulate optimization
            setTimeout(() => {
                this.showNotification('System optimization completed', 'success');
            }, 3000);
        } catch (error) {
            this.showNotification('System optimization failed', 'error');
        }
    }
    
    clearActivity() {
        const activityFeed = document.getElementById('activity-feed');
        activityFeed.innerHTML = '<div class="activity-item"><div class="activity-content"><p>No recent activity</p></div></div>';
    }
    
    toggleNotifications() {
        // Implement notifications panel
        console.log('📢 Toggle notifications');
    }
    
    showModal(title, content, actions = []) {
        const modal = document.getElementById('agent-modal');
        const modalTitle = document.getElementById('modal-title');
        const modalBody = document.getElementById('modal-body');
        const modalAction = document.getElementById('modal-action');
        
        modalTitle.textContent = title;
        modalBody.innerHTML = content;
        
        if (actions.length > 0) {
            modalAction.textContent = actions[0].text;
            modalAction.onclick = actions[0].handler;
            modalAction.style.display = 'block';
        } else {
            modalAction.style.display = 'none';
        }
        
        modal.classList.add('active');
    }
    
    closeModal() {
        const modal = document.getElementById('agent-modal');
        modal.classList.remove('active');
    }
    
    showNotification(message, type = 'info', duration = 5000) {
        const container = document.getElementById('notifications');
        const notification = document.createElement('div');
        notification.className = `notification ${type}`;
        
        const icon = this.getNotificationIcon(type);
        
        notification.innerHTML = `
            <div class="notification-icon">
                <i class="fas fa-${icon}"></i>
            </div>
            <div class="notification-content">
                <p>${message}</p>
            </div>
            <button class="notification-close" onclick="this.parentElement.remove()">
                <i class="fas fa-times"></i>
            </button>
        `;
        
        container.appendChild(notification);
        
        // Auto remove
        if (duration > 0) {
            setTimeout(() => {
                if (notification.parentElement) {
                    notification.remove();
                }
            }, duration);
        }
        
        // Update notification count
        this.updateNotificationCount();
    }
    
    getNotificationIcon(type) {
        const icons = {
            success: 'check-circle',
            warning: 'exclamation-triangle',
            error: 'times-circle',
            info: 'info-circle'
        };
        return icons[type] || 'info-circle';
    }
    
    updateNotificationCount() {
        const count = document.querySelectorAll('.notification').length;
        document.querySelector('.notification-count').textContent = count;
    }
    
    handleResize() {
        // Handle responsive behavior
        const width = window.innerWidth;
        const sidebar = document.getElementById('sidebar');
        
        if (width <= 768) {
            sidebar.classList.remove('open');
        }
    }
    
    handleKeyboardShortcuts(e) {
        // Ctrl/Cmd + K for search
        if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
            e.preventDefault();
            document.getElementById('global-search').focus();
        }
        
        // Escape to close modal
        if (e.key === 'Escape') {
            this.closeModal();
        }
    }
    
    startRealTimeUpdates() {
        // Update system uptime every minute
        setInterval(() => {
            this.updateUptime();
        }, 60000);
        
        // Refresh agents every 30 seconds
        setInterval(() => {
            this.loadAgents();
        }, 30000);
    }
    
    updateUptime() {
        // Calculate uptime since page load
        const startTime = window.performance.timing.navigationStart;
        const now = Date.now();
        const uptime = now - startTime;
        
        const hours = Math.floor(uptime / 3600000);
        const minutes = Math.floor((uptime % 3600000) / 60000);
        
        document.getElementById('system-uptime').textContent = `${hours}h ${minutes}m`;
    }
    
    updateDashboard() {
        this.updateAgentsDisplay();
        this.updateAgentsCount();
    }
    
    // Public methods for external access
    viewAgent(agentId) {
        const agent = this.agents.get(agentId);
        if (agent) {
            const content = `
                <div class="agent-details">
                    <h4>${agent.name}</h4>
                    <p><strong>ID:</strong> ${agent.id}</p>
                    <p><strong>Status:</strong> ${agent.status}</p>
                    <p><strong>Description:</strong> ${agent.description || 'No description'}</p>
                    <h5>Capabilities:</h5>
                    <ul>
                        ${(agent.capabilities || []).map(cap => `<li>${cap}</li>`).join('')}
                    </ul>
                </div>
            `;
            
            this.showModal(`Agent: ${agent.name}`, content, [
                {
                    text: 'Configure',
                    handler: () => this.configureAgent(agentId)
                }
            ]);
        }
    }
    
    configureAgent(agentId) {
        console.log('⚙️ Configure agent:', agentId);
        this.closeModal();
        // Implement agent configuration
    }
    
    showSystemStatus() {
        const content = `
            <div class="system-status-details">
                <h4>System Information</h4>
                <p><strong>Active Agents:</strong> ${Array.from(this.agents.values()).filter(a => a.status === 'active').length}</p>
                <p><strong>Total Agents:</strong> ${this.agents.size}</p>
                <p><strong>Connection:</strong> ${this.socket?.connected ? 'Connected' : 'Disconnected'}</p>
                <p><strong>Version:</strong> 7.2.1</p>
            </div>
        `;
        
        this.showModal('System Status', content);
    }
}

// Initialize dashboard when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.dashboard = new DynamicDashboard();
});

// Export for module usage
if (typeof module !== 'undefined' && module.exports) {
    module.exports = DynamicDashboard;
}
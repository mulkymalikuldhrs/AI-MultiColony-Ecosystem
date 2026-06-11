export const mockAgents = [
  { id: 'browser-01', name: 'Browser Agent', type: 'browser', status: 'active', cpu: 45, memory: 62, task: 'Scraping financial data', lastAction: '2m ago' },
  { id: 'coder-01', name: 'Coder Agent', type: 'coder', status: 'idle', cpu: 12, memory: 34, task: null, lastAction: '5m ago' },
  { id: 'colony-01', name: 'Colony Agent', type: 'colony', status: 'active', cpu: 78, memory: 85, task: 'Coordinating 5 agents', lastAction: '1m ago' },
  { id: 'executor-01', name: 'Executor Agent', type: 'executor', status: 'active', cpu: 56, memory: 45, task: 'Running shell commands', lastAction: '30s ago' },
  { id: 'manus-01', name: 'Manus Agent', type: 'manus', status: 'error', cpu: 0, memory: 12, task: null, lastAction: '15m ago' },
  { id: 'planner-01', name: 'Planner Agent', type: 'planner', status: 'active', cpu: 34, memory: 28, task: 'Planning deployment pipeline', lastAction: '1m ago' },
  { id: 'researcher-01', name: 'Researcher Agent', type: 'researcher', status: 'active', cpu: 67, memory: 72, task: 'Analyzing market trends', lastAction: '45s ago' },
  { id: 'security-01', name: 'Security Agent', type: 'security', status: 'active', cpu: 23, memory: 18, task: 'Monitoring access logs', lastAction: '3m ago' },
  { id: 'voice-01', name: 'Voice Agent', type: 'voice', status: 'idle', cpu: 5, memory: 15, task: null, lastAction: '10m ago' },
  { id: 'registry-01', name: 'Agent Registry', type: 'registry', status: 'active', cpu: 8, memory: 22, task: 'Managing 10 agents', lastAction: '1m ago' },
];

export const mockColonies = [
  { id: 'colony-alpha', name: 'Alpha Colony', health: 92, agents: 5, capacity: 10, status: 'active', created: '2025-06-01', schedule: 'Round-Robin' },
  { id: 'colony-beta', name: 'Beta Colony', health: 78, agents: 3, capacity: 8, status: 'active', created: '2025-06-05', schedule: 'Priority-Based' },
  { id: 'colony-gamma', name: 'Gamma Colony', health: 45, agents: 2, capacity: 6, status: 'degraded', created: '2025-06-08', schedule: 'FIFO' },
];

export const mockTools = [
  { id: 'browser', name: 'Browser Tool', category: 'web', description: 'Web browsing and scraping', executions: 156, lastUsed: '2m ago' },
  { id: 'code', name: 'Code Tool', category: 'dev', description: 'Code execution and analysis', executions: 234, lastUsed: '5m ago' },
  { id: 'docker', name: 'Docker Tool', category: 'infra', description: 'Container management', executions: 89, lastUsed: '15m ago' },
  { id: 'file', name: 'File Tool', category: 'system', description: 'File system operations', executions: 312, lastUsed: '1m ago' },
  { id: 'mcp', name: 'MCP Tool', category: 'protocol', description: 'Model Context Protocol', executions: 67, lastUsed: '8m ago' },
  { id: 'memory', name: 'Memory Tool', category: 'cognitive', description: 'Memory retrieval and storage', executions: 198, lastUsed: '3m ago' },
  { id: 'search', name: 'Search Tool', category: 'web', description: 'Web and code search', executions: 278, lastUsed: '30s ago' },
  { id: 'shell', name: 'Shell Tool', category: 'system', description: 'Shell command execution', executions: 445, lastUsed: '10s ago' },
  { id: 'voice', name: 'Voice Tool', category: 'media', description: 'Speech synthesis and recognition', executions: 23, lastUsed: '1h ago' },
  { id: 'channel', name: 'Channel Tool', category: 'comms', description: 'Multi-channel messaging', executions: 145, lastUsed: '4m ago' },
];

export const mockMemoryEntries = [
  { id: 'mem-01', key: 'market-analysis-btc', type: 'knowledge', content: 'Bitcoin showing bullish divergence on 4H timeframe...', timestamp: '2025-06-11T08:30:00Z', relevance: 0.95 },
  { id: 'mem-02', key: 'session-2025-06-10', type: 'session', content: 'Previous session: 5 trades, 3 profitable, 2 losses', timestamp: '2025-06-10T23:59:00Z', relevance: 0.82 },
  { id: 'mem-03', key: 'vector-pattern-01', type: 'vector', content: 'Pattern detected: Head and shoulders on ETH/USDT', timestamp: '2025-06-11T07:15:00Z', relevance: 0.88 },
  { id: 'mem-04', key: 'condensed-news', type: 'condenser', content: 'Fed rate decision expected next week, market cautious', timestamp: '2025-06-11T06:00:00Z', relevance: 0.76 },
  { id: 'mem-05', key: 'deploy-config-v2', type: 'knowledge', content: 'Docker compose configuration for production deployment', timestamp: '2025-06-09T14:20:00Z', relevance: 0.65 },
];

export const mockChannels = [
  { id: 'discord', name: 'Discord', status: 'connected', messages: 1245, config: { webhook: '***', channel: '#trading-alerts' } },
  { id: 'slack', name: 'Slack', status: 'connected', messages: 876, config: { webhook: '***', channel: '#ai-colony' } },
  { id: 'telegram', name: 'Telegram', status: 'disconnected', messages: 432, config: { botToken: '***', chatId: '***' } },
  { id: 'whatsapp', name: 'WhatsApp', status: 'error', messages: 0, config: { bridgeUrl: '***' } },
];

export const mockSecurityEvents = [
  { id: 'sec-01', timestamp: '2025-06-11T08:45:00Z', type: 'auth_success', severity: 'info', agent: 'researcher-01', detail: 'Agent authenticated successfully' },
  { id: 'sec-02', timestamp: '2025-06-11T08:30:00Z', type: 'permission_denied', severity: 'warning', agent: 'browser-01', detail: 'Access denied to /etc/shadow' },
  { id: 'sec-03', timestamp: '2025-06-11T07:15:00Z', type: 'sandbox_escape_attempt', severity: 'critical', agent: 'executor-01', detail: 'Attempted to escape Docker sandbox' },
  { id: 'sec-04', timestamp: '2025-06-11T06:00:00Z', type: 'tool_execution', severity: 'info', agent: 'coder-01', detail: 'Shell command executed: npm test' },
  { id: 'sec-05', timestamp: '2025-06-10T23:00:00Z', type: 'rate_limit', severity: 'warning', agent: 'voice-01', detail: 'Rate limit exceeded for TTS API' },
];

export const mockEvents = [
  { id: 'evt-01', timestamp: '08:45:12', type: 'agent_start', message: 'Researcher Agent started market analysis', severity: 'info' },
  { id: 'evt-02', timestamp: '08:44:58', type: 'tool_exec', message: 'Browser Tool completed scraping', severity: 'success' },
  { id: 'evt-03', timestamp: '08:43:30', type: 'colony_update', message: 'Alpha Colony added new agent', severity: 'info' },
  { id: 'evt-04', timestamp: '08:42:15', type: 'security', message: 'Permission denied for shell access', severity: 'warning' },
  { id: 'evt-05', timestamp: '08:41:00', type: 'memory', message: 'New pattern stored in knowledge base', severity: 'success' },
  { id: 'evt-06', timestamp: '08:40:22', type: 'error', message: 'Manus Agent encountered LLM timeout', severity: 'error' },
];

export const statusColors: Record<string, string> = {
  active: 'bg-emerald-500',
  idle: 'bg-amber-500',
  error: 'bg-red-500',
  disconnected: 'bg-gray-500',
  degraded: 'bg-orange-500',
  connected: 'bg-emerald-500',
};

export const severityColors: Record<string, string> = {
  info: 'text-cyan-400',
  warning: 'text-amber-400',
  critical: 'text-red-400',
  success: 'text-emerald-400',
  error: 'text-red-500',
};

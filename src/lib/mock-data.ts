// Mock data for the AI-MultiColony-Ecosystem Dashboard
// Used as fallback when the backend API is not available

export interface Agent {
  id: string;
  name: string;
  type: string;
  status: "active" | "idle" | "error" | "offline";
  colony: string;
  lastActive: string;
  tasksCompleted: number;
  tasksRunning: number;
  cpu: number;
  memory: number;
  description: string;
}

export interface Colony {
  id: string;
  name: string;
  status: "active" | "idle" | "scaling" | "error";
  agents: number;
  maxAgents: number;
  coordinator: string;
  schedule: string;
  uptime: string;
  health: number;
}

export interface Tool {
  id: string;
  name: string;
  category: string;
  status: "available" | "busy" | "error" | "disabled";
  description: string;
  executions: number;
  avgLatency: number;
  version: string;
}

export interface MemoryEntry {
  id: string;
  key: string;
  value: string;
  category: string;
  timestamp: string;
  size: number;
  accessCount: number;
}

export interface Channel {
  id: string;
  name: string;
  type: "discord" | "slack" | "telegram" | "whatsapp";
  status: "connected" | "disconnected" | "error";
  messages: number;
  lastMessage: string;
  config: Record<string, string>;
}

export interface SecurityEvent {
  id: string;
  type: "audit" | "permission" | "sandbox" | "alert";
  severity: "low" | "medium" | "high" | "critical";
  message: string;
  timestamp: string;
  source: string;
  resolved: boolean;
}

export interface SystemEvent {
  id: string;
  type: "agent" | "colony" | "tool" | "system" | "security";
  message: string;
  timestamp: string;
  severity: "info" | "warning" | "error" | "success";
}

export const AGENT_TYPES = [
  "Browser", "Coder", "Colony", "Executor", "Manus",
  "Planner", "Researcher", "Security", "Voice", "Registry"
];

export const TOOL_CATEGORIES = [
  "browser", "channel", "code", "docker", "file",
  "mcp", "memory", "search", "shell", "voice", "registry"
];

export const MEMORY_TYPES = [
  "condenser", "knowledge", "paging", "session", "vector"
];

export const CHANNEL_TYPES = ["discord", "slack", "telegram", "whatsapp"] as const;

export const mockAgents: Agent[] = [
  {
    id: "agt-001",
    name: "Browser-Alpha",
    type: "Browser",
    status: "active",
    colony: "Colony-Alpha",
    lastActive: "2s ago",
    tasksCompleted: 147,
    tasksRunning: 3,
    cpu: 45,
    memory: 62,
    description: "Web browsing and scraping agent"
  },
  {
    id: "agt-002",
    name: "Coder-Beta",
    type: "Coder",
    status: "active",
    colony: "Colony-Alpha",
    lastActive: "5s ago",
    tasksCompleted: 89,
    tasksRunning: 2,
    cpu: 78,
    memory: 45,
    description: "Code generation and review agent"
  },
  {
    id: "agt-003",
    name: "Colony-Master",
    type: "Colony",
    status: "active",
    colony: "Colony-Alpha",
    lastActive: "1s ago",
    tasksCompleted: 234,
    tasksRunning: 5,
    cpu: 32,
    memory: 28,
    description: "Colony coordination and management"
  },
  {
    id: "agt-004",
    name: "Executor-Gamma",
    type: "Executor",
    status: "idle",
    colony: "Colony-Beta",
    lastActive: "30s ago",
    tasksCompleted: 56,
    tasksRunning: 0,
    cpu: 5,
    memory: 12,
    description: "Task execution and orchestration"
  },
  {
    id: "agt-005",
    name: "Manus-Delta",
    type: "Manus",
    status: "active",
    colony: "Colony-Beta",
    lastActive: "3s ago",
    tasksCompleted: 312,
    tasksRunning: 4,
    cpu: 56,
    memory: 71,
    description: "General-purpose autonomous agent"
  },
  {
    id: "agt-006",
    name: "Planner-Epsilon",
    type: "Planner",
    status: "active",
    colony: "Colony-Alpha",
    lastActive: "1s ago",
    tasksCompleted: 198,
    tasksRunning: 2,
    cpu: 38,
    memory: 33,
    description: "Strategic planning and task decomposition"
  },
  {
    id: "agt-007",
    name: "Researcher-Zeta",
    type: "Researcher",
    status: "idle",
    colony: "Colony-Gamma",
    lastActive: "45s ago",
    tasksCompleted: 67,
    tasksRunning: 0,
    cpu: 8,
    memory: 15,
    description: "Information gathering and analysis"
  },
  {
    id: "agt-008",
    name: "Security-Eta",
    type: "Security",
    status: "active",
    colony: "Colony-Alpha",
    lastActive: "0s ago",
    tasksCompleted: 445,
    tasksRunning: 1,
    cpu: 22,
    memory: 19,
    description: "Security monitoring and threat detection"
  },
  {
    id: "agt-009",
    name: "Voice-Theta",
    type: "Voice",
    status: "offline",
    colony: "Colony-Gamma",
    lastActive: "5m ago",
    tasksCompleted: 23,
    tasksRunning: 0,
    cpu: 0,
    memory: 0,
    description: "Voice interface and speech processing"
  },
  {
    id: "agt-010",
    name: "Registry-Iota",
    type: "Registry",
    status: "active",
    colony: "Colony-Alpha",
    lastActive: "0s ago",
    tasksCompleted: 1203,
    tasksRunning: 0,
    cpu: 12,
    memory: 8,
    description: "Agent and tool registry management"
  }
];

export const mockColonies: Colony[] = [
  {
    id: "col-001",
    name: "Colony-Alpha",
    status: "active",
    agents: 6,
    maxAgents: 10,
    coordinator: "Colony-Master",
    schedule: "Round-Robin",
    uptime: "3d 14h 22m",
    health: 98
  },
  {
    id: "col-002",
    name: "Colony-Beta",
    status: "active",
    agents: 2,
    maxAgents: 8,
    coordinator: "Executor-Gamma",
    schedule: "Priority-Based",
    uptime: "1d 8h 15m",
    health: 87
  },
  {
    id: "col-003",
    name: "Colony-Gamma",
    status: "idle",
    agents: 2,
    maxAgents: 6,
    coordinator: "Researcher-Zeta",
    schedule: "On-Demand",
    uptime: "12h 45m",
    health: 65
  }
];

export const mockTools: Tool[] = [
  { id: "tool-001", name: "Browser Tool", category: "browser", status: "available", description: "Web browsing, scraping, and automation", executions: 1247, avgLatency: 340, version: "2.1.0" },
  { id: "tool-002", name: "Channel Tool", category: "channel", status: "available", description: "Multi-platform messaging integration", executions: 893, avgLatency: 120, version: "1.5.2" },
  { id: "tool-003", name: "Code Tool", category: "code", status: "busy", description: "Code execution, analysis, and generation", executions: 2156, avgLatency: 890, version: "3.0.1" },
  { id: "tool-004", name: "Docker Tool", category: "docker", status: "available", description: "Container management and sandboxing", executions: 567, avgLatency: 1200, version: "2.3.0" },
  { id: "tool-005", name: "File Tool", category: "file", status: "available", description: "File system operations and management", executions: 3421, avgLatency: 45, version: "1.8.0" },
  { id: "tool-006", name: "MCP Tool", category: "mcp", status: "available", description: "Model Context Protocol integration", executions: 234, avgLatency: 200, version: "1.0.0" },
  { id: "tool-007", name: "Memory Tool", category: "memory", status: "available", description: "Memory storage, retrieval, and search", executions: 4567, avgLatency: 30, version: "2.5.0" },
  { id: "tool-008", name: "Search Tool", category: "search", status: "available", description: "Web and knowledge base search", executions: 1890, avgLatency: 560, version: "2.2.0" },
  { id: "tool-009", name: "Shell Tool", category: "shell", status: "error", description: "Shell command execution", executions: 789, avgLatency: 150, version: "1.9.0" },
  { id: "tool-010", name: "Voice Tool", category: "voice", status: "disabled", description: "Voice synthesis and recognition", executions: 45, avgLatency: 800, version: "0.5.0" },
  { id: "tool-011", name: "Registry Tool", category: "registry", status: "available", description: "Agent and tool registry", executions: 8912, avgLatency: 10, version: "2.0.0" },
  { id: "tool-012", name: "Container Tool", category: "docker", status: "available", description: "WASM and container runtime", executions: 345, avgLatency: 450, version: "1.2.0" }
];

export const mockMemory: MemoryEntry[] = [
  { id: "mem-001", key: "project_context", value: "AI-MultiColony-Ecosystem: Autonomous Agent Operating System with colony-based architecture", category: "knowledge", timestamp: "2025-01-15T10:30:00Z", size: 256, accessCount: 45 },
  { id: "mem-002", key: "session_browser_alpha", value: "Active browsing session: Research on microservice patterns", category: "session", timestamp: "2025-01-15T11:15:00Z", size: 1024, accessCount: 12 },
  { id: "mem-003", key: "code_review_template", value: "Standard code review checklist for Python projects...", category: "knowledge", timestamp: "2025-01-14T09:00:00Z", size: 512, accessCount: 89 },
  { id: "mem-004", key: "security_audit_001", value: "Permission denied for shell access from agent Voice-Theta", category: "session", timestamp: "2025-01-15T12:00:00Z", size: 128, accessCount: 3 },
  { id: "mem-005", key: "colony_alpha_state", value: "6 active agents, Round-Robin scheduling, 98% health", category: "vector", timestamp: "2025-01-15T12:30:00Z", size: 2048, accessCount: 156 },
  { id: "mem-006", key: "mcp_config_openai", value: "OpenAI GPT-4 configuration with function calling enabled", category: "knowledge", timestamp: "2025-01-13T15:00:00Z", size: 384, accessCount: 234 },
  { id: "mem-007", key: "condensed_daily_0115", value: "Summary: 3 colonies active, 10 agents deployed, 892 tasks completed, 2 security alerts", category: "condenser", timestamp: "2025-01-15T23:59:00Z", size: 512, accessCount: 7 },
  { id: "mem-008", key: "vector_embedding_model", value: "text-embedding-3-small, 1536 dimensions, cosine similarity", category: "vector", timestamp: "2025-01-10T08:00:00Z", size: 64, accessCount: 567 },
  { id: "mem-009", key: "pager_cache_lru", value: "LRU cache with 1000 entries, 64MB max, eviction policy: least recently used", category: "paging", timestamp: "2025-01-15T00:00:00Z", size: 128, accessCount: 3421 },
  { id: "mem-010", key: "research_topic_quantum", value: "Quantum computing applications in portfolio optimization", category: "knowledge", timestamp: "2025-01-15T14:20:00Z", size: 768, accessCount: 15 }
];

export const mockChannels: Channel[] = [
  {
    id: "ch-001",
    name: "Discord-Primary",
    type: "discord",
    status: "connected",
    messages: 1247,
    lastMessage: "2m ago",
    config: { webhook: "active", channel: "#agent-ops", guild: "AI-Colony" }
  },
  {
    id: "ch-002",
    name: "Slack-Workspace",
    type: "slack",
    status: "connected",
    messages: 893,
    lastMessage: "5m ago",
    config: { workspace: "multicolony", channel: "#alerts", bot: "ColonyBot" }
  },
  {
    id: "ch-003",
    name: "Telegram-Bot",
    type: "telegram",
    status: "disconnected",
    messages: 456,
    lastMessage: "1h ago",
    config: { bot_token: "***", chat_id: "-1001", mode: "polling" }
  },
  {
    id: "ch-004",
    name: "WhatsApp-Gateway",
    type: "whatsapp",
    status: "error",
    messages: 123,
    lastMessage: "3h ago",
    config: { phone: "+1-555-0199", api: "twilio", webhook: "active" }
  }
];

export const mockSecurityEvents: SecurityEvent[] = [
  { id: "sec-001", type: "audit", severity: "low", message: "Agent Browser-Alpha accessed memory store", timestamp: "2025-01-15T12:30:00Z", source: "audit-logger", resolved: true },
  { id: "sec-002", type: "permission", severity: "medium", message: "Permission escalation attempt by Voice-Theta for shell access", timestamp: "2025-01-15T12:15:00Z", source: "permission-manager", resolved: true },
  { id: "sec-003", type: "sandbox", severity: "low", message: "Docker container sandbox restarted for Executor-Gamma", timestamp: "2025-01-15T11:45:00Z", source: "docker-sandbox", resolved: true },
  { id: "sec-004", type: "alert", severity: "high", message: "Unauthorized API access attempt from external IP", timestamp: "2025-01-15T11:00:00Z", source: "network-monitor", resolved: false },
  { id: "sec-005", type: "audit", severity: "low", message: "Config update by Planner-Epsilon: scheduling algorithm changed", timestamp: "2025-01-15T10:30:00Z", source: "audit-logger", resolved: true },
  { id: "sec-006", type: "permission", severity: "critical", message: "Root access request denied for unknown agent", timestamp: "2025-01-15T09:15:00Z", source: "permission-manager", resolved: false },
  { id: "sec-007", type: "sandbox", severity: "medium", message: "WASM sandbox memory limit exceeded by Coder-Beta", timestamp: "2025-01-15T08:50:00Z", source: "wasm-sandbox", resolved: true },
  { id: "sec-008", type: "audit", severity: "low", message: "New agent registration: Voice-Theta", timestamp: "2025-01-15T08:00:00Z", source: "registry", resolved: true },
  { id: "sec-009", type: "alert", severity: "high", message: "Rate limit exceeded on API endpoint /agents/run", timestamp: "2025-01-15T07:30:00Z", source: "rate-limiter", resolved: false },
  { id: "sec-010", type: "sandbox", severity: "low", message: "Container health check passed for all active containers", timestamp: "2025-01-15T07:00:00Z", source: "docker-sandbox", resolved: true }
];

export const mockSystemEvents: SystemEvent[] = [
  { id: "evt-001", type: "agent", message: "Browser-Alpha completed web scraping task #147", timestamp: "12:30:15", severity: "success" },
  { id: "evt-002", type: "colony", message: "Colony-Alpha scaled up: added Manus-Delta", timestamp: "12:29:45", severity: "info" },
  { id: "evt-003", type: "tool", message: "Code Tool execution completed (2.1s)", timestamp: "12:28:30", severity: "success" },
  { id: "evt-004", type: "system", message: "Memory usage at 78% - consider cleanup", timestamp: "12:27:00", severity: "warning" },
  { id: "evt-005", type: "security", message: "Rate limit warning on /api/agents/run", timestamp: "12:25:30", severity: "warning" },
  { id: "evt-006", type: "agent", message: "Researcher-Zeta entering idle mode", timestamp: "12:24:00", severity: "info" },
  { id: "evt-007", type: "tool", message: "Shell Tool encountered error: timeout", timestamp: "12:22:45", severity: "error" },
  { id: "evt-008", type: "colony", message: "Colony-Gamma coordinator handoff complete", timestamp: "12:20:00", severity: "success" },
  { id: "evt-009", type: "agent", message: "Security-Eta detected anomalous access pattern", timestamp: "12:18:30", severity: "warning" },
  { id: "evt-010", type: "system", message: "WebSocket connection established with 3 clients", timestamp: "12:15:00", severity: "info" },
  { id: "evt-011", type: "agent", message: "Coder-Beta pushed code changes to repository", timestamp: "12:13:00", severity: "success" },
  { id: "evt-012", type: "tool", message: "Docker Tool: Container restarted for health check", timestamp: "12:10:00", severity: "info" }
];

export const resourceUsageHistory = [
  { time: "10:00", cpu: 35, memory: 45, agents: 8, tasks: 12 },
  { time: "10:30", cpu: 42, memory: 52, agents: 9, tasks: 15 },
  { time: "11:00", cpu: 55, memory: 58, agents: 10, tasks: 18 },
  { time: "11:30", cpu: 48, memory: 62, agents: 10, tasks: 14 },
  { time: "12:00", cpu: 62, memory: 68, agents: 10, tasks: 22 },
  { time: "12:30", cpu: 58, memory: 72, agents: 10, tasks: 19 },
  { time: "13:00", cpu: 45, memory: 65, agents: 9, tasks: 16 },
  { time: "13:30", cpu: 52, memory: 60, agents: 10, tasks: 20 },
  { time: "14:00", cpu: 68, memory: 75, agents: 10, tasks: 25 },
  { time: "14:30", cpu: 55, memory: 70, agents: 10, tasks: 18 },
];

export const colonyHealthHistory = [
  { time: "10:00", alpha: 95, beta: 82, gamma: 70 },
  { time: "10:30", alpha: 96, beta: 85, gamma: 72 },
  { time: "11:00", alpha: 97, beta: 88, gamma: 68 },
  { time: "11:30", alpha: 98, beta: 86, gamma: 65 },
  { time: "12:00", alpha: 97, beta: 87, gamma: 63 },
  { time: "12:30", alpha: 98, beta: 85, gamma: 60 },
  { time: "13:00", alpha: 96, beta: 89, gamma: 62 },
  { time: "13:30", alpha: 97, beta: 90, gamma: 65 },
  { time: "14:00", alpha: 98, beta: 87, gamma: 68 },
  { time: "14:30", alpha: 99, beta: 88, gamma: 65 },
];

export const toolExecutionHistory = [
  { time: "10:00", executions: 45, errors: 2 },
  { time: "10:30", executions: 52, errors: 1 },
  { time: "11:00", executions: 68, errors: 3 },
  { time: "11:30", executions: 55, errors: 1 },
  { time: "12:00", executions: 72, errors: 2 },
  { time: "12:30", executions: 65, errors: 0 },
  { time: "13:00", executions: 48, errors: 1 },
  { time: "13:30", executions: 58, errors: 2 },
  { time: "14:00", executions: 75, errors: 1 },
  { time: "14:30", executions: 62, errors: 0 },
];

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export class ApiClient {
  private baseUrl: string;

  constructor(baseUrl: string = API_BASE) {
    this.baseUrl = baseUrl;
  }

  private async request<T>(path: string, options?: RequestInit): Promise<T> {
    try {
      const res = await fetch(`${this.baseUrl}${path}`, {
        headers: { 'Content-Type': 'application/json', ...options?.headers },
        ...options,
      });
      if (!res.ok) throw new Error(`API Error: ${res.status}`);
      return res.json();
    } catch {
      return null as T;
    }
  }

  // Agents
  async listAgents() { return this.request<any[]>('/api/agents/list'); }
  async runAgent(agentId: string, task: string) {
    return this.request<any>('/api/agents/run', {
      method: 'POST', body: JSON.stringify({ agent_id: agentId, task }),
    });
  }
  async getAgentStatus(agentId: string) { return this.request<any>(`/api/agents/status/${agentId}`); }

  // Colony
  async getColonyStatus() { return this.request<any>('/api/colony/status'); }
  async createColony(name: string, agentIds: string[]) {
    return this.request<any>('/api/colony/create', {
      method: 'POST', body: JSON.stringify({ name, agent_ids: agentIds }),
    });
  }
  async getColonyAgents() { return this.request<any[]>('/api/colony/agents'); }

  // Tools
  async listTools() { return this.request<any[]>('/api/tools/list'); }
  async executeTool(toolId: string, params: any) {
    return this.request<any>('/api/tools/execute', {
      method: 'POST', body: JSON.stringify({ tool_id: toolId, params }),
    });
  }

  // Memory
  async searchMemory(query: string) { return this.request<any[]>(`/api/memory/search?q=${query}`); }
  async storeMemory(key: string, value: any) {
    return this.request<any>('/api/memory/store', {
      method: 'POST', body: JSON.stringify({ key, value }),
    });
  }
}

export const api = new ApiClient();

const API_BASE_URL = "/api";
const BACKEND_PORT = "8000";

interface RequestOptions {
  method?: string;
  body?: unknown;
  headers?: Record<string, string>;
}

class ApiClient {
  private async request<T>(endpoint: string, options: RequestOptions = {}): Promise<T> {
    const { method = "GET", body, headers = {} } = options;
    const url = `${API_BASE_URL}${endpoint}?XTransformPort=${BACKEND_PORT}`;

    const config: RequestInit = {
      method,
      headers: {
        "Content-Type": "application/json",
        ...headers,
      },
    };

    if (body) {
      config.body = JSON.stringify(body);
    }

    try {
      const response = await fetch(url, config);
      if (!response.ok) {
        throw new Error(`API Error: ${response.status} ${response.statusText}`);
      }
      return response.json();
    } catch (error) {
      console.error(`API request failed: ${endpoint}`, error);
      throw error;
    }
  }

  // Agents
  async listAgents() {
    return this.request("/agents/list");
  }

  async runAgent(data: { agent_type: string; task: string }) {
    return this.request("/agents/run", { method: "POST", body: data });
  }

  async getAgentStatus(id: string) {
    return this.request(`/agents/status/${id}`);
  }

  // Colony
  async getColonyStatus() {
    return this.request("/colony/status");
  }

  async createColony(data: { name: string; agents: string[] }) {
    return this.request("/colony/create", { method: "POST", body: data });
  }

  async listColonyAgents() {
    return this.request("/colony/agents");
  }

  // Tools
  async listTools() {
    return this.request("/tools/list");
  }

  async executeTool(data: { tool_name: string; params: Record<string, unknown> }) {
    return this.request("/tools/execute", { method: "POST", body: data });
  }

  // Memory
  async searchMemory(query: string) {
    return this.request(`/memory/search?q=${encodeURIComponent(query)}`);
  }

  async storeMemory(data: { key: string; value: string; category?: string }) {
    return this.request("/memory/store", { method: "POST", body: data });
  }
}

export const apiClient = new ApiClient();

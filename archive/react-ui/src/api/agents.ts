import axios from 'axios'

const API_URL = '/api'

export interface Agent {
  id: string
  name: string
  description: string
  status: string
  route?: string
}

export interface AgentResponse {
  status: string
  agents: Agent[]
}

export interface AgentStatusResponse {
  status: string
  agent: Agent
}

export interface AgentRunResponse {
  status: string
  message: string
  task_id: string
  task_description: string
}

export interface AgentLogsResponse {
  status: string
  agent: string
  logs: {
    timestamp: string
    level: string
    message: string
  }[]
}

// Get all agents
export const getAgents = async (): Promise<Agent[]> => {
  try {
    const response = await axios.get<AgentResponse>(`${API_URL}/agents/`)
    return response.data.agents
  } catch (error) {
    console.error('Error fetching agents:', error)
    throw error
  }
}

// Get agent status
export const getAgentStatus = async (name: string): Promise<Agent> => {
  try {
    const response = await axios.get<AgentStatusResponse>(`${API_URL}/agents/${name}/status`)
    return response.data.agent
  } catch (error) {
    console.error(`Error fetching agent ${name} status:`, error)
    throw error
  }
}

// Run agent
export const runAgent = async (name: string, taskDescription: string): Promise<AgentRunResponse> => {
  try {
    const response = await axios.post<AgentRunResponse>(`${API_URL}/agents/${name}/run`, {
      agent_name: name,
      task_description: taskDescription
    })
    return response.data
  } catch (error) {
    console.error(`Error running agent ${name}:`, error)
    throw error
  }
}

// Stop agent
export const stopAgent = async (name: string): Promise<{ status: string; message: string }> => {
  try {
    const response = await axios.post<{ status: string; message: string }>(`${API_URL}/agents/${name}/stop`)
    return response.data
  } catch (error) {
    console.error(`Error stopping agent ${name}:`, error)
    throw error
  }
}

// Get agent logs
export const getAgentLogs = async (name: string, limit: number = 10): Promise<AgentLogsResponse> => {
  try {
    const response = await axios.get<AgentLogsResponse>(`${API_URL}/agents/${name}/logs?limit=${limit}`)
    return response.data
  } catch (error) {
    console.error(`Error fetching agent ${name} logs:`, error)
    throw error
  }
}
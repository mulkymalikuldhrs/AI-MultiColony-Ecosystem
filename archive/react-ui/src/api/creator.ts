import axios from 'axios'

const API_URL = '/api'

export interface AgentCreateRequest {
  name: string
  prompt_template: string
  config?: Record<string, any>
  description?: string
  dependencies?: string[]
}

export interface AgentCreateResponse {
  status: string
  message: string
  agent: {
    name: string
    file_path: string
    config: Record<string, any>
  }
}

// Create a new agent
export const createAgent = async (agentData: AgentCreateRequest): Promise<AgentCreateResponse> => {
  try {
    const response = await axios.post<AgentCreateResponse>(`${API_URL}/agent-creator/create`, agentData)
    return response.data
  } catch (error) {
    console.error('Error creating agent:', error)
    throw error
  }
}
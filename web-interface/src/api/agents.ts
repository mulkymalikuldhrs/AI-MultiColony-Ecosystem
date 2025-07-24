import axios from 'axios';

const API_URL = '/api';

export const getAgents = async () => {
  const response = await axios.get(`${API_URL}/agents`);
  return response.data;
};

export const getAgentStatus = async (name: string) => {
  const response = await axios.get(`${API_URL}/agents/${name}/status`);
  return response.data;
};

export const runAgent = async (name: string, taskDescription: string) => {
  const response = await axios.post(`${API_URL}/agents/${name}/run`, {
    agent_name: name,
    task_description: taskDescription,
  });
  return response.data;
};

export const stopAgent = async (name: string) => {
  const response = await axios.post(`${API_URL}/agents/${name}/stop`);
  return response.data;
};

export const getAgentLogs = async (name: string) => {
  const response = await axios.get(`${API_URL}/agents/${name}/logs`);
  return response.data;
};

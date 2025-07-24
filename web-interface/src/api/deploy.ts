import axios from 'axios';

const API_URL = '/api';

export const deployAgent = async (agentName: string, environment: string) => {
  const response = await axios.post(`${API_URL}/deploy`, {
    agent_name: agentName,
    environment,
  });
  return response.data;
};

import axios from 'axios';

const API_URL = '/api';

export const createAgent = async (agentData: any) => {
  const response = await axios.post(`${API_URL}/agent-creator/create`, agentData);
  return response.data;
};

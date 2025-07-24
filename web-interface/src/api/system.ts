import axios from 'axios';

const API_URL = '/api';

export const getSystemStatus = async () => {
  const response = await axios.get(`${API_URL}/system/status`);
  return response.data;
};

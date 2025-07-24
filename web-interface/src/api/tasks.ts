import axios from 'axios';

const API_URL = '/api';

export const getTaskStatus = async (taskId: string) => {
  const response = await axios.get(`${API_URL}/task-status/${taskId}`);
  return response.data;
};

export const streamTaskLogs = (taskId: string) => {
  return new EventSource(`${API_URL}/log-stream/${taskId}`);
};

import axios from 'axios';

// Use environment variable or default to Render URL
const API_BASE_URL = process.env.REACT_APP_API_URL || 'https://speech-sentiment-pipeline.onrender.com/api/v1';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Audio endpoints
export const uploadAudio = async (file: File) => {
  const formData = new FormData();
  formData.append('file', file);
  const response = await api.post('/audio/upload', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
  return response.data;
};

export const processAudio = async (audioId: string) => {
  const response = await api.post(`/audio/${audioId}/process`);
  return response.data;
};

export const listAudioFiles = async () => {
  const response = await api.get('/audio/');
  return response.data;
};

export const getAudioFile = async (audioId: string) => {
  const response = await api.get(`/audio/${audioId}`);
  return response.data;
};

export const deleteAudioFile = async (audioId: string) => {
  const response = await api.delete(`/audio/${audioId}`);
  return response.data;
};

// Analysis endpoints
export const getFullAnalysis = async (audioId: string) => {
  const response = await api.get(`/analysis/${audioId}/full`);
  return response.data;
};

export const getTranscript = async (audioId: string) => {
  const response = await api.get(`/analysis/${audioId}/transcript`);
  return response.data;
};

export const getSentiment = async (audioId: string) => {
  const response = await api.get(`/analysis/${audioId}/sentiment`);
  return response.data;
};

export const getEntities = async (audioId: string) => {
  const response = await api.get(`/analysis/${audioId}/entities`);
  return response.data;
};

export const getSummary = async (audioId: string) => {
  const response = await api.get(`/analysis/${audioId}/summary`);
  return response.data;
};

// Health check
export const healthCheck = async () => {
  const response = await api.get('/health/');
  return response.data;
};

export default api;

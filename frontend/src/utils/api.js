import axios from 'axios';

const api = axios.create({
  baseURL: '/api',
});

export const uploadFile = (file) => {
  const formData = new FormData();
  formData.append('file', file);
  return api.post('/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
};

export const getDocuments = () => api.get('/documents');
export const getDatasets = () => api.get('/datasets');
export const mergeDatasets = () => api.post('/datasets/merge');
export const startTraining = (config) => api.post('/train', config);
export const stopTraining = () => api.post('/train/stop');
export const getTrainingStatus = () => api.get('/train/status');
export const chat = (prompt, maxTokens = 4096) =>
  api.post('/chat', { prompt, max_tokens: maxTokens });

export const createTrainWebSocket = () => {
  const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
  return new WebSocket(`${protocol}//${window.location.host}/ws/train`);
};

// RAG endpoints
export const ragStatus = () => api.get('/rag/status');
export const ragQuery = (question, topK = 4) =>
  api.post('/rag/query', { question, top_k: topK });
export const ragReindex = () => api.post('/rag/reindex');
export const ragClear = () => api.delete('/rag/index');

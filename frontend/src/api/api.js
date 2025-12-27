import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const subjectsAPI = {
  getAll: () => api.get('/subjects'),
  getById: (id) => api.get(`/subjects/${id}`),
  create: (data) => api.post('/subjects', data),
  getTopics: (subjectId) => api.get(`/subjects/${subjectId}/topics`),
  createTopic: (subjectId, data) => api.post(`/subjects/${subjectId}/topics`, data),
  uploadMaterial: (subjectId, topicId, file) => {
    const formData = new FormData();
    formData.append('file', file);
    return api.post(`/subjects/${subjectId}/topics/${topicId}/upload`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
  },
};

export const sessionAPI = {
  generate: (data) => api.post('/session/generate', data),
  complete: (data) => api.post('/session/complete', data),
};

export const historyAPI = {
  get: (subjectId) => api.get(`/history/${subjectId}`),
  getRecommendations: (subjectId) => api.get(`/recommendations/${subjectId}`),
};

export default api;

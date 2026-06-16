import axios from 'axios';

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000',
  timeout: 10000,
  headers: { 'Content-Type': 'application/json' },
});

export const getHealth = () => api.get('/health').then(r => r.data);
export const getFacilities = () => api.get('/facilities').then(r => r.data);
export const getFacility = (id) => api.get(`/facilities/${id}`).then(r => r.data);
export const getAnomalies = () => api.get('/anomalies').then(r => r.data);
export const getAnomaly = (id) => api.get(`/anomalies/${id}`).then(r => r.data);
export const assignAnomaly = (id, tech_name) =>
  api.post(`/anomalies/${id}/assign`, { tech_name }).then(r => r.data);
export const getImpact = () => api.get('/impact/projection').then(r => r.data);
export const getStats = () => api.get('/stats').then(r => r.data);

export default api;

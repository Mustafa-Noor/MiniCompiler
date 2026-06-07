import axios from 'axios';

const API_BASE = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000';

const api = axios.create({
  baseURL: API_BASE,
  timeout: 120000,
  headers: { 'Content-Type': 'application/json' },
});

export const uploadFile = async (file) => {
  const formData = new FormData();
  formData.append('file', file);
  const { data } = await api.post('/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
  return data;
};

export const saveSource = async (sourceCode, filename = 'editor.pas') => {
  const { data } = await api.post('/source', { source_code: sourceCode, filename });
  return data;
};

export const getSource = async () => {
  const { data } = await api.get('/source');
  return data;
};

export const getStatus = async () => {
  const { data } = await api.get('/status');
  return data;
};

export const runLexer = async () => {
  const { data } = await api.post('/run/lexer');
  return data;
};

export const runRDParser = async () => {
  const { data } = await api.post('/run/rd');
  return data;
};

export const runLL1Parser = async () => {
  const { data } = await api.post('/run/ll1');
  return data;
};

export const runLRParser = async () => {
  const { data } = await api.post('/run/lr');
  return data;
};

export const runAST = async () => {
  const { data } = await api.post('/run/ast');
  return data;
};

export const runAll = async () => {
  const { data } = await api.post('/run/all');
  return data;
};

export const getSymbolTable = async () => {
  const { data } = await api.get('/symbol-table');
  return data;
};

export const getErrors = async () => {
  const { data } = await api.get('/errors');
  return data;
};

export const getReports = async () => {
  const { data } = await api.get('/reports');
  return data;
};

export const getReportDownloadUrl = (filename) => {
  return `${API_BASE}/reports/download/${filename}`;
};

export default api;

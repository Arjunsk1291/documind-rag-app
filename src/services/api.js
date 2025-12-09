import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 60000,
});

// ============= DOCUMENT MANAGEMENT =============

export const uploadDocument = async (file) => {
  const formData = new FormData();
  formData.append('file', file);
  
  const response = await api.post('/documents/upload', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
  
  return response.data;
};

export const getDocuments = async () => {
  const response = await api.get('/documents');
  return response.data;
};

export const deleteDocument = async (documentId) => {
  const response = await api.delete(`/documents/${documentId}`);
  return response.data;
};

// ============= CONVERSATION MANAGEMENT =============

export const createConversation = async (documentIds = []) => {
  const response = await api.post('/conversations', {
    document_ids: documentIds
  });
  return response.data;
};

export const getConversations = async () => {
  const response = await api.get('/conversations');
  return response.data;
};

export const getConversation = async (conversationId) => {
  const response = await api.get(`/conversations/${conversationId}`);
  return response.data;
};

export const updateConversationTitle = async (conversationId, title) => {
  const response = await api.put(`/conversations/${conversationId}/title`, {
    title
  });
  return response.data;
};

export const updateConversationDocuments = async (conversationId, documentIds) => {
  const response = await api.put(`/conversations/${conversationId}/documents`, {
    document_ids: documentIds
  });
  return response.data;
};

export const deleteConversation = async (conversationId) => {
  const response = await api.delete(`/conversations/${conversationId}`);
  return response.data;
};

// ============= CHAT =============

export const sendMessage = async (conversationId, query, documentIds = []) => {
  const response = await api.post(`/conversations/${conversationId}/messages`, {
    query,
    document_ids: documentIds,
  });
  
  return response.data;
};

export const generateMindMap = async (conversationId, query, documentIds = []) => {
  const response = await api.post(`/conversations/${conversationId}/mindmap`, {
    query,
    document_ids: documentIds,
  });
  
  return response.data;
};

export default api;

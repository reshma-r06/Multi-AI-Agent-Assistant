import axios from 'axios';
import { QueryRequest, TaskResponse, FileUploadResponse } from '@/types';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const api = {
  // Health check
  healthCheck: async () => {
    const response = await apiClient.get('/health');
    return response.data;
  },

  // Process query
  processQuery: async (request: QueryRequest): Promise<TaskResponse> => {
    const response = await apiClient.post<TaskResponse>('/query', request);
    return response.data;
  },

  // Get task status
  getTask: async (taskId: string): Promise<TaskResponse> => {
    const response = await apiClient.get<TaskResponse>(`/tasks/${taskId}`);
    return response.data;
  },

  // Upload file
  uploadFile: async (file: File): Promise<FileUploadResponse> => {
    const formData = new FormData();
    formData.append('file', file);

    const response = await apiClient.post<FileUploadResponse>('/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },

  // Generate report
  generateReport: async (taskId: string, format: string = 'pdf') => {
    const response = await apiClient.post('/reports/generate', {
      task_id: taskId,
      format,
      include_sources: true,
    });
    return response.data;
  },

  // Clear documents
  clearDocuments: async () => {
    const response = await apiClient.delete('/documents/clear');
    return response.data;
  },
};

export default api;
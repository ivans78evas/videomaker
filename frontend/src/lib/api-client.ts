import { TranslationTask, WorkerStatus, TranslationRequest, BatchTaskResponse } from '../types/api';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

class ApiClient {
  private async request<T>(endpoint: string, options?: RequestInit): Promise<T> {
    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...options?.headers,
      },
    });

    if (!response.ok) {
      throw new Error(`API Error: ${response.statusText}`);
    }

    return response.json();
  }

  async getTasks(): Promise<TranslationTask[]> {
    return this.request<TranslationTask[]>('/tasks/');
  }

  async createTask(data: TranslationRequest): Promise<BatchTaskResponse> {
    return this.request<BatchTaskResponse>('/tasks/', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async getWorkers(): Promise<WorkerStatus> {
    return this.request<WorkerStatus>('/tasks/workers');
  }

  async getTask(id: string): Promise<TranslationTask> {
    return this.request<TranslationTask>(`/tasks/${id}`);
  }
}

export const apiClient = new ApiClient();

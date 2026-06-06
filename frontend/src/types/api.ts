export interface TranslationTask {
  id: string;
  source_url: string;
  target_language: string;
  status: 'pending' | 'processing' | 'completed' | 'failed' | 'blocked';
  local_final_path?: string;
  created_at: string;
}

export interface WorkerStatus {
  count: number;
  workers: string[];
  mode: string;
}

export interface TranslationRequest {
  url: string;
  target_lang: string;
}

export interface BatchTaskResponse {
  count: number;
  task_ids: string[];
  status: string;
}

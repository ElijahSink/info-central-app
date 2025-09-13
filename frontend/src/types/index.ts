export interface Block {
  id: number;
  user_prompt: string;
  title: string;
  current_version: number;
  refresh_interval: number;
  layout_data: {
    x: number;
    y: number;
    w: number;
    h: number;
  };
  status: 'active' | 'error' | 'disabled';
  created_at: string;
  updated_at: string;
}

export interface BlockVersion {
  id: number;
  version: number;
  frontend_code: string;
  ai_explanation: string;
  created_at: string;
  status: 'active' | 'deprecated' | 'failed';
}

export interface BlockData {
  data: any;
  cached: boolean;
  fetched_at?: string;
  refreshed_at?: string;
}

export interface CreateBlockRequest {
  user_prompt: string;
  title?: string;
  refresh_interval?: number;
}

export interface UpdateBlockRequest {
  user_prompt: string;
}

export interface LayoutUpdateRequest {
  layout_data: {
    x: number;
    y: number;
    w: number;
    h: number;
  };
}
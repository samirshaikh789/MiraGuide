import { apiRequest } from './queryClient';
import type { Session, Interaction, AIResponse, DecisionResult, AnalyzeResponse, ProvidersResponse } from '@/types';

const API_BASE = '/api/v1';

class ApiError extends Error {
  constructor(
    message: string,
    public status: number,
    public errorCode?: string,
    public details?: unknown
  ) {
    super(message);
    this.name = 'ApiError';
  }
}

async function handleResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    let errorData: { error?: string; error_code?: string; details?: unknown } = {};
    try {
      errorData = await response.json();
    } catch {
      // Ignore parse errors
    }
    throw new ApiError(
      errorData.error || `HTTP error ${response.status}`,
      response.status,
      errorData.error_code,
      errorData.details
    );
  }
  return response.json();
}

export const api = {
  // Sessions
  createSession: async (userId?: string): Promise<Session> => {
    const response = await apiRequest('POST', `${API_BASE}/sessions`, { user_id: userId });
    return handleResponse(response);
  },

  getSession: async (sessionId: string): Promise<Session> => {
    const response = await apiRequest('GET', `${API_BASE}/sessions/${sessionId}`);
    return handleResponse(response);
  },

  deleteSession: async (sessionId: string): Promise<void> => {
    const response = await apiRequest('DELETE', `${API_BASE}/sessions/${sessionId}`);
    return handleResponse(response);
  },

  // Analyze endpoints
  analyzeImage: async (
    file: File,
    options?: {
      sessionId?: string;
      question?: string;
      detailLevel?: 'brief' | 'standard' | 'detailed';
    }
  ): Promise<AnalyzeResponse> => {
    const formData = new FormData();
    formData.append('image', file);
    if (options?.sessionId) formData.append('session_id', options.sessionId);
    if (options?.question) formData.append('question', options.question);
    if (options?.detailLevel) formData.append('detail_level', options.detailLevel);

    const response = await apiRequest('POST', `${API_BASE}/analyze/image`, formData, {
      headers: {}, // Let browser set Content-Type with boundary
    });
    return handleResponse(response);
  },

  analyzeDocument: async (
    file: File,
    options?: {
      sessionId?: string;
      simplifyLevel?: 'simple' | 'very-simple' | 'child';
    }
  ): Promise<AnalyzeResponse> => {
    const formData = new FormData();
    formData.append('image', file);
    if (options?.sessionId) formData.append('session_id', options.sessionId);
    if (options?.simplifyLevel) formData.append('simplify_level', options.simplifyLevel);

    const response = await apiRequest('POST', `${API_BASE}/analyze/document`, formData, {
      headers: {},
    });
    return handleResponse(response);
  },

  analyzeForm: async (
    file: File,
    options?: {
      sessionId?: string;
      explainFields?: boolean;
    }
  ): Promise<AnalyzeResponse> => {
    const formData = new FormData();
    formData.append('image', file);
    if (options?.sessionId) formData.append('session_id', options.sessionId);
    if (options?.explainFields !== undefined) formData.append('explain_fields', String(options.explainFields));

    const response = await apiRequest('POST', `${API_BASE}/analyze/form`, formData, {
      headers: {},
    });
    return handleResponse(response);
  },

  askQuestion: async (
    sessionId: string,
    question: string,
    includeContext: boolean = true
  ): Promise<AnalyzeResponse> => {
    const response = await apiRequest('POST', `${API_BASE}/analyze/ask`, {
      session_id: sessionId,
      question,
      include_context: includeContext,
    });
    return handleResponse(response);
  },

  simplifyText: async (
    text: string,
    level: 'simple' | 'very-simple' | 'child' = 'simple',
    sessionId?: string
  ): Promise<AnalyzeResponse> => {
    const response = await apiRequest('POST', `${API_BASE}/analyze/simplify`, {
      text,
      level,
      session_id: sessionId,
    });
    return handleResponse(response);
  },

  summarizeText: async (
    text: string,
    sessionId?: string
  ): Promise<AnalyzeResponse> => {
    const response = await apiRequest('POST', `${API_BASE}/analyze/summarize`, {
      text,
      session_id: sessionId,
    });
    return handleResponse(response);
  },

  chat: async (
    message: string,
    sessionId?: string
  ): Promise<AnalyzeResponse> => {
    const response = await apiRequest('POST', `${API_BASE}/analyze/chat`, {
      message,
      session_id: sessionId,
    });
    return handleResponse(response);
  },

  // Voice endpoints
  transcribeAudio: async (
    file: File,
    options?: {
      sessionId?: string;
      language?: string;
    }
  ): Promise<AnalyzeResponse> => {
    const formData = new FormData();
    formData.append('audio', file);
    if (options?.sessionId) formData.append('session_id', options.sessionId);
    if (options?.language) formData.append('language', options.language);

    const response = await apiRequest('POST', `${API_BASE}/voice/transcribe`, formData, {
      headers: {},
    });
    return handleResponse(response);
  },

  synthesizeSpeech: async (
    text: string,
    options?: {
      voice?: string;
      speed?: number;
      sessionId?: string;
    }
  ): Promise<AnalyzeResponse & { audio_base64: string; audio_mime_type: string }> => {
    const response = await apiRequest('POST', `${API_BASE}/voice/synthesize`, {
      text,
      voice: options?.voice,
      speed: options?.speed ?? 1.0,
      session_id: options?.sessionId,
    });
    return handleResponse(response);
  },

  // Interactions
  getSessionInteractions: async (
    sessionId: string,
    page: number = 1,
    pageSize: number = 20
  ): Promise<{
    items: Interaction[];
    total: number;
    page: number;
    page_size: number;
    total_pages: number;
  }> => {
    const response = await apiRequest(
      'GET',
      `${API_BASE}/interactions/session/${sessionId}?page=${page}&page_size=${pageSize}`
    );
    return handleResponse(response);
  },

  getInteraction: async (interactionId: string): Promise<Interaction> => {
    const response = await apiRequest('GET', `${API_BASE}/interactions/${interactionId}`);
    return handleResponse(response);
  },

  // Providers
  getProviders: async (): Promise<ProvidersResponse> => {
    const response = await apiRequest('GET', `${API_BASE}/analyze/providers`);
    return handleResponse(response);
  },
};

export { ApiError };
export type { Session, Interaction, AIResponse, DecisionResult, AnalyzeResponse, ProvidersResponse };
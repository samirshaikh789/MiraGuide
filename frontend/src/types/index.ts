export type Route =
  | '/'
  | '/dashboard'
  | '/see'
  | '/read'
  | '/form'
  | '/ask'
  | '/voice'
  | '/chat'
  | '/settings';

export type SimplifyLevel = 'simple' | 'very-simple' | 'child';

export interface AccessibilitySettings {
  fontScale: number;
  highContrast: boolean;
  darkMode: boolean;
  reduceMotion: boolean;
  largerButtons: boolean;
  autoRead: boolean;
  speechRate: number;
  voiceNavigation: boolean;
  simplifiedInterface: boolean;
  language: string;
}

export interface AIResult { 
  text: string; 
  notice?: string; 
}

export interface Transcript { 
  id: string; 
  createdAt: string; 
  content: string; 
}

export interface SoundEvent { 
  id: string; 
  name: string; 
  detail: string; 
  time: string; 
  icon: string; 
}

// New types for MiraGuide
export interface Session {
  id: string;
  user_id: string | null;
  created_at: string;
  updated_at: string;
  context_data: string | null;
  interactions?: Interaction[];
}

export interface Interaction {
  id: string;
  session_id: string;
  input_type: string;
  intent: string;
  question: string | null;
  response: string | null;
  structured_response: string | null;
  confidence: number;
  needs_clarification: boolean;
  clarification_question: string | null;
  safety_note: string | null;
  created_at: string;
}

export interface AIResponse {
  intent: string;
  summary: string;
  details: string[];
  entities: Array<{
    type: string;
    label: string;
    value: string | null;
    confidence: number;
    bounding_box: Record<string, number> | null;
  }>;
  important_information: Array<{
    label: string;
    value: string;
    priority: number;
    source: string | null;
  }>;
  confidence: number;
  needs_clarification: boolean;
  clarification_question: string | null;
  safety_note: string | null;
  response_mode: string;
  follow_up_suggestions: string[];
  provider: string;
  model: string;
  processing_time_ms: number;
  demo_mode: boolean;
}

export interface DecisionResult {
  intent: string;
  confidence: number;
  requires_clarification: boolean;
  clarification_question: string | null;
  response_mode: string;
  safety_concerns: string[];
  recommended_workflow: string;
  context_used: boolean;
}

export interface AnalyzeResponse {
  session_id: string;
  interaction_id: string;
  ai_response: AIResponse;
  decision: DecisionResult;
}

export interface ProvidersResponse {
  vision: string[];
  text: string[];
  ocr: string[];
  stt: string[];
  tts: string[];
}

export type IntentType = 
  | 'see_understand' 
  | 'read_explain' 
  | 'form_assist' 
  | 'visual_qa' 
  | 'simplify' 
  | 'summarize' 
  | 'communicate' 
  | 'chat' 
  | 'unknown';

export type InputType = 
  | 'image' 
  | 'document' 
  | 'form' 
  | 'text' 
  | 'voice' 
  | 'question';

export type ResponseMode = 'text' | 'voice' | 'text_and_voice' | 'visual';
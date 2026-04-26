export type GradeLevel = 'K' | '1' | '2' | '3' | '4' | '5' | '6' | '7' | '8' | '9' | '10' | '11' | '12';
export type LanguageCode = 'en' | 'hi' | 'es' | 'fr' | 'de' | 'zh' | 'ja' | 'kn';

export interface QuestionRequest {
  question: string;
  student_id: string;
  grade_level: GradeLevel;
  language?: LanguageCode;
  context?: string;
}

export interface VideoRequest {
  topic: string;
  student_id: string;
  grade_level: GradeLevel;
  language?: LanguageCode;
  target_duration_minutes?: number;
  enable_tts?: boolean;
  extra_context?: string;
}

export interface BoardStep {
  step: number;
  content: string;
  type: 'title' | 'body' | 'equation' | 'highlight' | 'diagram';
  draw_duration_ms?: number;
}

export interface BoardScript {
  steps: BoardStep[];
  total_duration_ms: number;
  background_color?: string;
  text_color?: string;
}

export interface MermaidDiagram {
  title: string;
  description: string;
  mermaid_code: string;
  diagram_type: string;
}

export interface ExplanationResponse {
  explanation_text: string;
  mermaid_diagrams?: MermaidDiagram[];
  board_script: BoardScript;
  difficulty_level: string;
  key_concepts: string[];
  follow_up_questions: string[];
  confidence_score: number;
  timestamp: string;
}

export interface VideoResponse {
  video_url: string;
  video_id: string;
  topic: string;
  duration_seconds?: number;
  generation_time_seconds?: number;
  timestamp: string;
  has_audio?: boolean;
  tts_engine?: string | null;
  narration_preview?: string | null;
}

export interface LearningStats {
  total_sessions: number;
  total_questions: number;
  recent_activity: number;
  success_rate: number;
}

export interface StudentProfile {
  student_id: string;
  grade_level: GradeLevel;
  preferred_language: LanguageCode;
  total_sessions: number;
  total_questions: number;
  updated_at: string;
}

export interface APIError {
  error: string;
  message: string;
  details?: Record<string, unknown>;
  timestamp: string;
}

// Type definitions for SnapLearn AI Frontend

export type GradeLevel = 
  | 'K' | '1' | '2' | '3' | '4' | '5' | '6' 
  | '7' | '8' | '9' | '10' | '11' | '12';

export type LanguageCode = 
  | 'en' | 'hi' | 'es' | 'fr' | 'de' | 'zh' | 'ja';

export type LearningStyle = 
  | 'visual' | 'auditory' | 'kinesthetic' | 'reading_writing' | 'mixed';

export type ConfidenceLevel = 
  | 'high' | 'medium' | 'low' | 'unknown';

// API Request Types
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
  duration_preference?: string;
}

export interface AssessmentRequest {
  question: string;
  answer: string;
  student_id: string;
  expected_answer?: string;
}

// Phase 2: Multimodal Input Types
export interface MultiModalRequest {
  student_id: string;
  grade_level: GradeLevel;
  language?: LanguageCode;
  input_type: 'text' | 'image' | 'voice';
  context?: string;
}

export interface ImageUploadRequest extends MultiModalRequest {
  input_type: 'image';
  image_data: string; // Base64 encoded
  image_format: string;
}

export interface VoiceUploadRequest extends MultiModalRequest {
  input_type: 'voice';
  audio_data: string; // Base64 encoded
  audio_format: string;
}

// Animation and Board Script Types
export interface BoardStep {
  step: number;
  content: string;
  type: 'title' | 'body' | 'equation' | 'highlight' | 'diagram';
  draw_duration_ms?: number;
  position?: { x: number; y: number };
  style?: Record<string, any>;
}

export interface BoardScript {
  steps: BoardStep[];
  total_duration_ms: number;
  background_color?: string;
  text_color?: string;
}

// API Response Types
export interface ExplanationResponse {
  explanation_text: string;
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
  file_size_mb?: number;
  manim_script?: string;
  generation_time_seconds?: number;
  timestamp: string;
}

export interface AssessmentResponse {
  is_correct: boolean;
  confidence_score: number;
  feedback: string;
  mistakes_identified: string[];
  suggestions: string[];
  next_explanation_style?: string;
  timestamp: string;
}

export interface ProcessedInputResponse {
  success: boolean;
  input_type: string;
  normalized_text: string;
  detected_language: string;
  confidence_score: number;
  math_expressions: string[];
  processing_time_ms: number;
  metadata: Record<string, any>;
  original_content?: string;
  error?: string;
}

// Student Profile Types
export interface ConceptMastery {
  concept: string;
  mastery_level: number;
  last_practiced: string;
  practice_count: number;
}

export interface LearningSession {
  session_id: string;
  timestamp: string;
  questions_asked: string[];
  topics_covered: string[];
  time_spent_minutes: number;
  engagement_score: number;
}

export interface StudentProfile {
  student_id: string;
  grade_level: GradeLevel;
  preferred_language: LanguageCode;
  learning_style: LearningStyle;
  explanation_style_preference: string;
  difficulty_preference: string;
  concept_mastery: ConceptMastery[];
  learning_sessions: LearningSession[];
  confusion_patterns: Record<string, number>;
  success_patterns: Record<string, number>;
  created_at: string;
  updated_at: string;
  total_sessions: number;
  total_questions: number;
}

// UI State Types
export interface AppState {
  currentStudent: string | null;
  isLoading: boolean;
  error: string | null;
  darkMode: boolean;
}

export interface TutorState {
  currentQuestion: string;
  currentExplanation: ExplanationResponse | null;
  isGenerating: boolean;
  animationProgress: number;
  showFollowUp: boolean;
}

export interface VideoState {
  isGenerating: boolean;
  currentVideo: VideoResponse | null;
  generationProgress: number;
  error: string | null;
}

// Component Props Types
export interface BlackboardProps {
  script: BoardScript;
  isPlaying: boolean;
  onAnimationComplete?: () => void;
  className?: string;
}

export interface QuestionInputProps {
  value: string;
  onChange: (value: string) => void;
  onSubmit: () => void;
  isLoading?: boolean;
  placeholder?: string;
  className?: string;
}

export interface StudentProfileProps {
  profile: StudentProfile;
  onUpdate: (profile: Partial<StudentProfile>) => void;
  isEditing?: boolean;
}

export interface VideoPlayerProps {
  videoUrl: string;
  title: string;
  onLoadStart?: () => void;
  onLoadEnd?: () => void;
  className?: string;
}

// API Client Types
export interface APIClient {
  explain: (request: QuestionRequest) => Promise<ExplanationResponse>;
  generateVideo: (request: VideoRequest) => Promise<VideoResponse>;
  assessAnswer: (request: AssessmentRequest) => Promise<AssessmentResponse>;
  getStudentProfile: (studentId: string) => Promise<{
    student_id: string;
    profile: StudentProfile | null;
    recent_topics: string[];
    learning_stats: LearningStats;
  }>;
  getStudentVideos: (studentId: string) => Promise<{ videos: VideoResponse[] }>;
  resetStudent: (studentId: string) => Promise<{ message: string }>;
}

export interface LearningStats {
  total_sessions: number;
  total_questions: number;
  recent_activity: number;
  success_rate: number;
}

// Hook Types
export interface UseAnimatedBlackboardOptions {
  script: BoardScript;
  autoPlay?: boolean;
  loop?: boolean;
  onComplete?: () => void;
}

export interface UseAnimatedBlackboardReturn {
  currentStep: number;
  isPlaying: boolean;
  progress: number;
  play: () => void;
  pause: () => void;
  reset: () => void;
  goToStep: (step: number) => void;
}

export interface UseStudentDataOptions {
  studentId: string;
  autoRefresh?: boolean;
  refreshInterval?: number;
}

export interface UseStudentDataReturn {
  profile: StudentProfile | null;
  recentTopics: string[];
  learningStats: LearningStats;
  isLoading: boolean;
  error: string | null;
  refresh: () => Promise<void>;
  updateProfile: (updates: Partial<StudentProfile>) => Promise<void>;
}

// Utility Types
export type Theme = 'light' | 'dark' | 'auto';

export interface ToastOptions {
  type: 'success' | 'error' | 'warning' | 'info';
  duration?: number;
  position?: 'top-right' | 'top-left' | 'bottom-right' | 'bottom-left';
}

export interface ModalProps {
  isOpen: boolean;
  onClose: () => void;
  title?: string;
  children: React.ReactNode;
  size?: 'sm' | 'md' | 'lg' | 'xl';
}

// Error Types
export interface APIError {
  error: string;
  message: string;
  details?: Record<string, any>;
  timestamp: string;
}

export interface FormErrors {
  [key: string]: string[];
}

// Configuration Types
export interface AppConfig {
  apiBaseUrl: string;
  defaultLanguage: LanguageCode;
  defaultGradeLevel: GradeLevel;
  animationSpeed: number;
  theme: Theme;
  features: {
    videoGeneration: boolean;
    assessments: boolean;
    profiles: boolean;
    animations: boolean;
  };
}

// Event Types
export interface StudentInteractionEvent {
  type: 'question' | 'assessment' | 'video_request';
  timestamp: string;
  data: any;
}

export interface AnimationEvent {
  type: 'start' | 'step' | 'complete' | 'pause';
  step?: number;
  progress?: number;
}

// SDK Demo Types (for the HTML demo page)
export interface SDKDemoState {
  question: string;
  grade: GradeLevel;
  language: LanguageCode;
  studentId: string;
  response: ExplanationResponse | null;
  isLoading: boolean;
  apiCalls: APICallLog[];
}

export interface APICallLog {
  id: string;
  timestamp: string;
  method: string;
  url: string;
  request: any;
  response: any;
  duration: number;
  status: number;
}
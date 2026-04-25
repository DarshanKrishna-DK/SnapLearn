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

// Phase 3 Types - Advanced Tutoring Features

export interface ConversationRequest {
  student_id: string;
  input_text: string;
  conversation_id?: string;
  input_type?: 'question' | 'answer' | 'clarification';
  context?: string;
}

export interface ConversationResponse {
  conversation_id: string;
  response: ExplanationResponse;
  state: 'starting' | 'explaining' | 'assessing' | 'confused' | 'adapting' | 'completed' | 'paused';
  turn_count: number;
  learning_insights: Record<string, any>;
  recommendations: string[];
  next_action?: string;
}

export interface AssessmentAnalytics {
  student_id: string;
  total_assessments: number;
  accuracy_trend: number[];
  mistake_patterns: Record<string, number>;
  improvement_areas: string[];
  strengths: string[];
  intervention_recommendations: string[];
}

export interface DifficultyAdaptationRequest {
  student_id: string;
  current_difficulty: string;
  recent_performance: Record<string, any>;
  topic: string;
}

export interface DifficultyAdaptationResponse {
  recommended_difficulty: string;
  adaptation_reason: string;
  confidence: number;
  adapted_content: Record<string, any>;
  teaching_strategies: string[];
}

export interface LearningPathRequest {
  student_id: string;
  target_topics: string[];
  time_available: number;
  preferences?: Record<string, any>;
}

export interface LearningPathResponse {
  path_id: string;
  recommended_sequence: Array<{
    topic: string;
    duration_minutes: number;
    difficulty: string;
    activities: string[];
  }>;
  estimated_duration: number;
  difficulty_progression: string[];
  checkpoint_assessments: Array<{
    after_topic: string;
    assessment_type: string;
  }>;
  personalization_notes: string[];
}

export interface ConfusionDetectionRequest {
  student_id: string;
  interaction_data: Record<string, any>;
  response_time: number;
  response_text: string;
}

export interface ConfusionDetectionResponse {
  confusion_detected: boolean;
  confidence_score: number;
  confusion_indicators: string[];
  intervention_needed: boolean;
  suggested_interventions: string[];
  emotion_analysis: Record<string, number>;
}

export interface ExplanationStyleRequest {
  student_id: string;
  topic: string;
  current_style: string;
  adaptation_reason: string;
  target_style: string;
}

export interface ExplanationStyleResponse {
  adapted_explanation: ExplanationResponse;
  style_comparison: Record<string, string>;
  effectiveness_prediction: number;
}

export interface ParentDashboardData {
  student_id: string;
  learning_summary: Record<string, any>;
  recent_activities: Array<Record<string, any>>;
  progress_metrics: Record<string, number>;
  areas_of_strength: string[];
  areas_needing_support: string[];
  recommendations_for_parents: string[];
  time_spent_learning: number;
  engagement_trend: number[];
}

export interface StudyRecommendationRequest {
  student_id: string;
  available_time: number;
  subject_preferences?: string[];
  difficulty_preference?: string;
}

export interface StudyRecommendationResponse {
  recommended_activities: Array<{
    activity: string;
    duration: number;
    subject: string;
    difficulty: string;
    description?: string;
  }>;
  personalized_schedule: Record<string, any>;
  focus_areas: string[];
  estimated_improvement: Record<string, number>;
  motivational_message: string;
  reminder_suggestions: string[];
}

export interface LearningAnalytics {
  student_id: string;
  time_period: string;
  total_sessions: number;
  total_time_minutes: number;
  concepts_mastered: string[];
  accuracy_metrics: Record<string, number>;
  engagement_metrics: Record<string, number>;
  difficulty_progression: Array<Record<string, any>>;
  learning_velocity: string;
  prediction_models: Record<string, any>;
}

// Phase 3 UI Component Types
export interface ConversationState {
  conversation_id: string | null;
  messages: ConversationMessage[];
  current_state: string;
  turn_count: number;
  is_active: boolean;
}

export interface ConversationMessage {
  id: string;
  type: 'student' | 'ai';
  content: string;
  timestamp: string;
  metadata?: Record<string, any>;
}

export interface AssessmentFeedback {
  overall_score: number;
  detailed_feedback: string;
  mistake_patterns: string[];
  improvement_suggestions: string[];
  next_difficulty: string;
  confidence_level: number;
}

export interface AdaptiveComponent {
  difficulty_level: string;
  explanation_style: string;
  engagement_level: number;
  confusion_indicators: string[];
  adaptations_made: number;
}

export interface ProgressTracking {
  session_start: string;
  current_topic: string;
  questions_answered: number;
  accuracy_rate: number;
  time_spent: number;
  engagement_score: number;
  difficulty_changes: Array<{
    from: string;
    to: string;
    reason: string;
    timestamp: string;
  }>;
}

// Extended API Client for Phase 3
export interface ExtendedAPIClient extends APIClient {
  // Conversation Management
  startConversation: (request: ConversationRequest) => Promise<ConversationResponse>;
  continueConversation: (request: ConversationRequest) => Promise<ConversationResponse>;
  
  // Advanced Assessment
  comprehensiveAssessment: (request: AssessmentRequest) => Promise<any>;
  getAssessmentAnalytics: (studentId: string) => Promise<AssessmentAnalytics>;
  
  // Adaptive Difficulty
  adaptDifficulty: (request: DifficultyAdaptationRequest) => Promise<DifficultyAdaptationResponse>;
  
  // Learning Path Optimization
  optimizeLearningPath: (request: LearningPathRequest) => Promise<LearningPathResponse>;
  
  // Confusion Detection
  detectConfusion: (request: ConfusionDetectionRequest) => Promise<ConfusionDetectionResponse>;
  
  // Parent Dashboard
  getParentDashboard: (studentId: string, days?: number) => Promise<ParentDashboardData>;
  
  // Study Recommendations
  getStudyRecommendations: (request: StudyRecommendationRequest) => Promise<StudyRecommendationResponse>;
  
  // Learning Analytics
  getLearningAnalytics: (studentId: string, period?: string) => Promise<LearningAnalytics>;
}

// Phase 3 Hook Types
export interface UseConversationOptions {
  studentId: string;
  autoStart?: boolean;
  persistHistory?: boolean;
}

export interface UseConversationReturn {
  conversation: ConversationState | null;
  sendMessage: (message: string, type?: string) => Promise<void>;
  startNewConversation: (initialQuestion: string) => Promise<void>;
  pauseConversation: () => Promise<void>;
  resumeConversation: () => Promise<void>;
  isLoading: boolean;
  error: string | null;
}

export interface UseAdaptiveTutoringOptions {
  studentId: string;
  initialTopic?: string;
  adaptationThreshold?: number;
}

export interface UseAdaptiveTutoringReturn {
  currentDifficulty: string;
  explanationStyle: string;
  isAdapting: boolean;
  adaptationHistory: Array<any>;
  requestAdaptation: (reason: string) => Promise<void>;
  getRecommendations: () => Promise<string[]>;
}

export interface UseProgressTrackingReturn {
  progress: ProgressTracking | null;
  updateProgress: (update: Partial<ProgressTracking>) => void;
  getAnalytics: () => Promise<LearningAnalytics>;
  resetSession: () => void;
}

// Phase 4 Types - Enhanced Video Generation & Analytics

export interface VideoGenerationSettings {
  topic: string;
  quality: 'low' | 'medium' | 'high' | 'ultra';
  format: 'mp4' | 'mov' | 'webm';
  animationStyle: 'classic' | 'modern' | 'colorful' | 'mathematical' | 'visual' | 'kinesthetic';
  targetDuration: number;
  includeInteractiveElements: boolean;
  personalizeForStudent: boolean;
}

export interface BatchVideoSettings {
  topics: string[];
  sequenceType: 'linear_progression' | 'branched_exploration' | 'spiral_curriculum';
  totalDuration: number;
  adaptiveDifficulty: boolean;
}

export interface VideoAnalyticsData {
  sessionId: string | null;
  watchTime: number;
  totalDuration: number;
  completionPercentage: number;
  interactions: number;
  engagementLevel: 'very_low' | 'low' | 'medium' | 'high' | 'very_high';
  confusionIndicators: string[];
  learningIndicators: string[];
}

export interface BatchVideoStatus {
  batch_id: string;
  status: 'queued' | 'processing' | 'completed' | 'failed' | 'cancelled';
  progress: {
    total_videos: number;
    completed: number;
    failed: number;
    processing: number;
    queued: number;
    completion_percentage: number;
  };
  estimated_completion: string | null;
  created_at: string;
  video_jobs: Array<{
    job_id: string;
    topic: string;
    status: string;
    sequence_position: number;
    video_url: string | null;
    error_message: string | null;
  }>;
  learning_path: {
    path_id: string;
    total_duration: number;
    difficulty_progression: string[];
  };
}

export interface VideoInteractionEvent {
  session_id: string;
  interaction_type: 'play' | 'pause' | 'seek' | 'rewind' | 'skip' | 'complete' | 'bookmark' | 'rate';
  video_position: number;
  duration?: number;
  metadata?: Record<string, any>;
}

export interface VideoSessionAnalytics {
  session_id: string;
  total_session_time: number;
  active_watch_time: number;
  engagement_level: string;
  engagement_score: number;
  completion_percentage: number;
  interaction_counts: Record<string, number>;
  focused_segments_count: number;
  focused_watch_time: number;
  attention_ratio: number;
  confusion_indicators: string[];
  learning_indicators: string[];
  rewatch_segments: Array<{
    start_time: number;
    end_time: number;
    rewatch_count: number;
  }>;
  peak_attention_moments: Array<{
    start_time: number;
    end_time: number;
    attention_score: number;
  }>;
}

export interface VideoPerformanceMetrics {
  video_id: string;
  performance_metrics: {
    total_views: number;
    average_completion_rate: number;
    average_watch_time: number;
    learning_effectiveness_score: number;
  };
  engagement_analysis: {
    engagement_distribution: Record<string, number>;
    most_rewatched_segments: Array<{
      start_time: number;
      end_time: number;
      rewatch_count: number;
    }>;
    drop_off_points: Array<[number, number]>; // [timestamp, drop_count]
  };
  improvement_opportunities: string[];
  student_feedback: {
    average_rating: number;
    total_ratings: number;
  };
}

export interface EnhancedVideoResponse extends VideoResponse {
  video_variants?: Array<{
    video_id: string;
    video_url: string;
    quality: string;
    format: string;
    file_size_mb: number;
    duration_seconds: number;
  }>;
  thumbnail_url?: string;
  learning_context?: Record<string, any>;
  script_metadata?: Record<string, any>;
  animation_style?: string;
  difficulty_level?: string;
  personalization_applied?: string[];
  video_analytics?: Record<string, any>;
  conceptual_map?: string[];
  interactive_elements?: string[];
}

export interface VideoRecommendation {
  topic: string;
  reason: string;
  priority: 'low' | 'medium' | 'high';
  estimated_duration: number;
  difficulty: string;
  thumbnail_url?: string;
}

export interface VideoFeedback {
  video_id: string;
  student_id: string;
  rating: number; // 1-5 stars
  feedback_text?: string;
  improvement_suggestions?: string[];
  timestamp: string;
}

// Enhanced API Client for Phase 4 Video Features
export interface VideoAPIClient {
  // Contextual video generation
  generateContextualVideo: (params: {
    topic: string;
    student_id: string;
    grade_level: string;
    language?: string;
    conversation_context?: any;
    video_quality?: string;
    video_format?: string;
    animation_style?: string;
    target_duration?: number;
  }) => Promise<EnhancedVideoResponse>;

  // Batch video generation
  createBatchGeneration: (request: LearningPathRequest) => Promise<{
    batch_id: string;
    message: string;
    estimated_completion: string;
  }>;

  getBatchStatus: (batchId: string) => Promise<BatchVideoStatus>;
  cancelBatch: (batchId: string) => Promise<{ message: string }>;
  getBatchAnalytics: () => Promise<any>;

  // Video analytics
  startVideoSession: (videoId: string, studentId: string, metadata?: any) => Promise<{ session_id: string }>;
  trackVideoInteraction: (event: VideoInteractionEvent) => Promise<{ message: string }>;
  endVideoSession: (sessionId: string, finalPosition?: number) => Promise<VideoSessionAnalytics>;
  getVideoAnalytics: (videoId: string) => Promise<VideoPerformanceMetrics>;
  getStudentVideoAnalytics: (studentId: string, days?: number) => Promise<any>;

  // Video features
  generateStyledVideo: (params: {
    topic: string;
    student_id: string;
    style_preferences: Record<string, any>;
    quality_settings?: Record<string, any>;
  }) => Promise<EnhancedVideoResponse>;

  submitVideoFeedback: (feedback: VideoFeedback) => Promise<{ feedback_id: string }>;
  getVideoRecommendations: (studentId: string, limit?: number) => Promise<{
    recommendations: VideoRecommendation[];
    personalization_basis: Record<string, any>;
  }>;
  getVideoThumbnail: (videoId: string) => Promise<Blob>;
}

export interface UseEnhancedVideoOptions {
  studentId: string;
  conversationContext?: ConversationResponse;
  autoLoadRecommendations?: boolean;
}

export interface UseEnhancedVideoReturn {
  // Video generation
  generateVideo: (settings: VideoGenerationSettings) => Promise<EnhancedVideoResponse>;
  createBatch: (settings: BatchVideoSettings) => Promise<string>;
  
  // Current video state
  currentVideo: EnhancedVideoResponse | null;
  isGenerating: boolean;
  generationProgress: number;
  
  // Batch state
  activeBatch: string | null;
  batchProgress: BatchVideoStatus | null;
  
  // Analytics
  videoAnalytics: VideoAnalyticsData;
  startAnalytics: (videoId: string) => Promise<void>;
  trackInteraction: (type: string, position: number) => Promise<void>;
  endAnalytics: () => Promise<VideoSessionAnalytics>;
  
  // Recommendations
  recommendations: VideoRecommendation[];
  loadRecommendations: () => Promise<void>;
  
  // Feedback
  submitFeedback: (rating: number, text?: string) => Promise<void>;
}
// API Client for SnapLearn AI

import axios, { AxiosInstance, AxiosResponse } from 'axios';
import {
  QuestionRequest,
  VideoRequest,
  AssessmentRequest,
  ExplanationResponse,
  VideoResponse,
  AssessmentResponse,
  StudentProfile,
  LearningStats,
  APIError,
  ImageUploadRequest,
  VoiceUploadRequest,
  MultiModalRequest,
  ProcessedInputResponse,
  // Phase 3 types
  ConversationRequest,
  ConversationResponse,
  AssessmentAnalytics,
  DifficultyAdaptationRequest,
  DifficultyAdaptationResponse,
  LearningPathRequest,
  LearningPathResponse,
  ConfusionDetectionRequest,
  ConfusionDetectionResponse,
  ParentDashboardData,
  StudyRecommendationRequest,
  StudyRecommendationResponse,
  LearningAnalytics,
} from '@/types';

class SnapLearnAPIClient {
  private client: AxiosInstance;
  private baseURL: string;

  constructor(baseURL = 'http://localhost:8000') {
    this.baseURL = baseURL;
    
    this.client = axios.create({
      baseURL,
      timeout: 60000, // 60 second timeout for video generation
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Request interceptor
    this.client.interceptors.request.use(
      (config) => {
        // Add timestamp to all requests
        config.headers['X-Request-Time'] = new Date().toISOString();
        
        // Log request in development
        if (process.env.NODE_ENV === 'development') {
          console.log(`API Request: ${config.method?.toUpperCase()} ${config.url}`, config.data);
        }
        
        return config;
      },
      (error) => {
        console.error('Request interceptor error:', error);
        return Promise.reject(error);
      }
    );

    // Response interceptor
    this.client.interceptors.response.use(
      (response: AxiosResponse) => {
        // Log response in development
        if (process.env.NODE_ENV === 'development') {
          console.log(`API Response: ${response.status} ${response.config.url}`, response.data);
        }
        
        return response;
      },
      (error) => {
        console.error('API Error:', error);
        
        // Transform error to our APIError format
        const apiError: APIError = {
          error: error.response?.data?.error || 'NetworkError',
          message: error.response?.data?.message || error.message || 'An unexpected error occurred',
          details: error.response?.data?.details || {},
          timestamp: new Date().toISOString(),
        };
        
        return Promise.reject(apiError);
      }
    );
  }

  // Health check
  async healthCheck(): Promise<{
    status: string;
    version: string;
    services: Record<string, boolean>;
    timestamp: string;
  }> {
    const response = await this.client.get('/health');
    return response.data;
  }

  // Main tutoring endpoint
  async explain(request: QuestionRequest): Promise<ExplanationResponse> {
    const response = await this.client.post('/api/explain', request);
    return response.data;
  }

  // Video generation endpoint
  async generateVideo(request: VideoRequest): Promise<VideoResponse> {
    const response = await this.client.post('/api/generate-video', request);
    return response.data;
  }

  // Assessment endpoint
  async assessAnswer(request: AssessmentRequest): Promise<AssessmentResponse> {
    const response = await this.client.post('/api/assess', request);
    return response.data;
  }

  // Student profile endpoints
  async getStudentProfile(studentId: string): Promise<{
    student_id: string;
    profile: StudentProfile | null;
    recent_topics: string[];
    learning_stats: LearningStats;
  }> {
    const response = await this.client.get(`/api/student/${studentId}/profile`);
    return response.data;
  }

  async getStudentVideos(studentId: string): Promise<{ videos: VideoResponse[] }> {
    const response = await this.client.get(`/api/student/${studentId}/videos`);
    return response.data;
  }

  // Development endpoints
  async resetStudent(studentId: string): Promise<{ message: string }> {
    const response = await this.client.post(`/api/debug/reset/${studentId}`);
    return response.data;
  }

  async getDebugMemory(): Promise<any> {
    const response = await this.client.get('/api/debug/memory');
    return response.data;
  }

  // Phase 2: Multimodal input processing endpoints
  async processImage(request: ImageUploadRequest): Promise<ProcessedInputResponse> {
    const response = await this.client.post('/api/process-image', request);
    return response.data;
  }

  async processVoice(request: VoiceUploadRequest): Promise<ProcessedInputResponse> {
    const response = await this.client.post('/api/process-voice', request);
    return response.data;
  }

  async processText(request: MultiModalRequest): Promise<ProcessedInputResponse> {
    const response = await this.client.post('/api/process-text', request);
    return response.data;
  }

  // Phase 3: Advanced Tutoring Features

  // Conversation Management
  async startConversation(request: ConversationRequest): Promise<ConversationResponse> {
    const response = await this.client.post('/api/conversation/start', request);
    return response.data;
  }

  async continueConversation(request: ConversationRequest): Promise<ConversationResponse> {
    const response = await this.client.post('/api/conversation/continue', request);
    return response.data;
  }

  // Advanced Assessment
  async comprehensiveAssessment(request: AssessmentRequest): Promise<any> {
    const response = await this.client.post('/api/assessment/comprehensive', request);
    return response.data;
  }

  async getAssessmentAnalytics(studentId: string): Promise<AssessmentAnalytics> {
    const response = await this.client.get(`/api/assessment/analytics/${studentId}`);
    return response.data;
  }

  // Adaptive Difficulty
  async adaptDifficulty(request: DifficultyAdaptationRequest): Promise<DifficultyAdaptationResponse> {
    const response = await this.client.post('/api/difficulty/adapt', request);
    return response.data;
  }

  // Learning Path Optimization
  async optimizeLearningPath(request: LearningPathRequest): Promise<LearningPathResponse> {
    const response = await this.client.post('/api/learning-path/optimize', request);
    return response.data;
  }

  // Confusion Detection
  async detectConfusion(request: ConfusionDetectionRequest): Promise<ConfusionDetectionResponse> {
    const response = await this.client.post('/api/confusion/detect', request);
    return response.data;
  }

  // Parent/Teacher Dashboard
  async getParentDashboard(studentId: string, days: number = 7): Promise<ParentDashboardData> {
    const response = await this.client.get(`/api/dashboard/parent/${studentId}?days=${days}`);
    return response.data;
  }

  // Study Recommendations
  async getStudyRecommendations(request: StudyRecommendationRequest): Promise<StudyRecommendationResponse> {
    const response = await this.client.post('/api/recommendations/study', request);
    return response.data;
  }

  // Learning Analytics
  async getLearningAnalytics(studentId: string, period: string = 'week'): Promise<LearningAnalytics> {
    const response = await this.client.get(`/api/analytics/learning/${studentId}?period=${period}`);
    return response.data;
  }

  // Phase 4: Enhanced Video Generation & Analytics

  // Contextual Video Generation
  async generateContextualVideo(params: {
    topic: string;
    student_id: string;
    grade_level: string;
    language?: string;
    conversation_context?: any;
    video_quality?: string;
    video_format?: string;
    animation_style?: string;
    target_duration?: number;
  }): Promise<any> {
    const response = await this.client.post('/api/video/generate-contextual', null, { params });
    return response.data;
  }

  // Batch Video Generation
  async createBatchGeneration(request: LearningPathRequest): Promise<{
    batch_id: string;
    message: string;
    estimated_completion: string;
  }> {
    const response = await this.client.post('/api/video/batch-generate', request);
    return response.data;
  }

  async getBatchStatus(batchId: string): Promise<any> {
    const response = await this.client.get(`/api/video/batch-status/${batchId}`);
    return response.data;
  }

  async cancelBatch(batchId: string): Promise<{ message: string }> {
    const response = await this.client.delete(`/api/video/batch-cancel/${batchId}`);
    return response.data;
  }

  async getBatchAnalytics(): Promise<any> {
    const response = await this.client.get('/api/video/batch-analytics');
    return response.data;
  }

  // Video Analytics
  async startVideoSession(videoId: string, studentId: string, metadata?: any): Promise<{ session_id: string }> {
    const response = await this.client.post('/api/video/session/start', {
      video_id: videoId,
      student_id: studentId,
      video_metadata: metadata
    });
    return response.data;
  }

  async trackVideoInteraction(event: {
    session_id: string;
    interaction_type: string;
    video_position: number;
    duration?: number;
    metadata?: any;
  }): Promise<{ message: string }> {
    const response = await this.client.post('/api/video/session/track', event);
    return response.data;
  }

  async endVideoSession(sessionId: string, finalPosition?: number): Promise<any> {
    const response = await this.client.post(`/api/video/session/end/${sessionId}`, {
      final_position: finalPosition
    });
    return response.data;
  }

  async getVideoAnalytics(videoId: string): Promise<any> {
    const response = await this.client.get(`/api/video/analytics/${videoId}`);
    return response.data;
  }

  async getStudentVideoAnalytics(studentId: string, days: number = 30): Promise<any> {
    const response = await this.client.get(`/api/video/analytics/student/${studentId}?days=${days}`);
    return response.data;
  }

  // Advanced Video Features
  async generateStyledVideo(params: {
    topic: string;
    student_id: string;
    style_preferences: Record<string, any>;
    quality_settings?: Record<string, any>;
  }): Promise<any> {
    const response = await this.client.post('/api/video/generate-with-style', params);
    return response.data;
  }

  async submitVideoFeedback(feedback: {
    video_id: string;
    student_id: string;
    rating: number;
    feedback_text?: string;
    improvement_suggestions?: string[];
  }): Promise<{ feedback_id: string }> {
    const response = await this.client.post('/api/video/feedback', feedback);
    return response.data;
  }

  async getVideoRecommendations(studentId: string, limit: number = 10): Promise<{
    student_id: string;
    recommendations: any[];
    personalization_basis: Record<string, any>;
  }> {
    const response = await this.client.get(`/api/video/recommendations/${studentId}?limit=${limit}`);
    return response.data;
  }

  async getVideoThumbnail(videoId: string): Promise<string> {
    const response = await this.client.get(`/api/video/thumbnails/${videoId}`, {
      responseType: 'blob'
    });
    return URL.createObjectURL(response.data);
  }

  // Utility methods
  getVideoUrl(videoPath: string): string {
    if (videoPath.startsWith('http')) {
      return videoPath;
    }
    return `${this.baseURL}${videoPath}`;
  }

  getStaticUrl(staticPath: string): string {
    if (staticPath.startsWith('http')) {
      return staticPath;
    }
    return `${this.baseURL}/static${staticPath}`;
  }

  // Connection testing
  async testConnection(): Promise<boolean> {
    try {
      await this.healthCheck();
      return true;
    } catch (error) {
      console.error('Connection test failed:', error);
      return false;
    }
  }

  // Retry mechanism for failed requests
  async retryRequest<T>(
    operation: () => Promise<T>,
    maxRetries: number = 3,
    delay: number = 1000
  ): Promise<T> {
    let lastError: Error;

    for (let attempt = 1; attempt <= maxRetries; attempt++) {
      try {
        return await operation();
      } catch (error) {
        lastError = error as Error;
        
        if (attempt === maxRetries) {
          throw lastError;
        }

        // Wait before retry
        await new Promise(resolve => setTimeout(resolve, delay * attempt));
      }
    }

    throw lastError!;
  }

  // Batch operations
  async batchExplain(requests: QuestionRequest[]): Promise<ExplanationResponse[]> {
    const promises = requests.map(request => this.explain(request));
    return Promise.all(promises);
  }

  async batchAssess(requests: AssessmentRequest[]): Promise<AssessmentResponse[]> {
    const promises = requests.map(request => this.assessAnswer(request));
    return Promise.all(promises);
  }

  // Configuration
  updateBaseURL(newBaseURL: string): void {
    this.baseURL = newBaseURL;
    this.client.defaults.baseURL = newBaseURL;
  }

  updateTimeout(timeout: number): void {
    this.client.defaults.timeout = timeout;
  }

  // Request cancellation
  createCancelToken() {
    return axios.CancelToken.source();
  }
}

// Create singleton instance
export const apiClient = new SnapLearnAPIClient();

// Export the class for testing or multiple instances
export { SnapLearnAPIClient };

// Convenience functions for common operations
export const api = {
  // Quick explain function with error handling
  explain: async (
    question: string,
    studentId: string = 'demo-student',
    gradeLevel: any = '4',
    language: any = 'en'
  ): Promise<ExplanationResponse | null> => {
    try {
      return await apiClient.explain({
        question,
        student_id: studentId,
        grade_level: gradeLevel,
        language,
      });
    } catch (error) {
      console.error('Explain API error:', error);
      return null;
    }
  },

  // Quick video generation
  generateVideo: async (
    topic: string,
    studentId: string = 'demo-student',
    gradeLevel: any = '4',
    language: any = 'en'
  ): Promise<VideoResponse | null> => {
    try {
      return await apiClient.generateVideo({
        topic,
        student_id: studentId,
        grade_level: gradeLevel,
        language,
      });
    } catch (error) {
      console.error('Video generation API error:', error);
      return null;
    }
  },

  // Quick assessment
  assess: async (
    question: string,
    answer: string,
    studentId: string = 'demo-student'
  ): Promise<AssessmentResponse | null> => {
    try {
      return await apiClient.assessAnswer({
        question,
        answer,
        student_id: studentId,
      });
    } catch (error) {
      console.error('Assessment API error:', error);
      return null;
    }
  },

  // Health check with timeout
  healthCheck: async (timeout: number = 5000): Promise<boolean> => {
    try {
      const originalTimeout = apiClient['client'].defaults.timeout;
      apiClient.updateTimeout(timeout);
      
      await apiClient.healthCheck();
      
      // Restore original timeout
      apiClient.updateTimeout(originalTimeout || 60000);
      
      return true;
    } catch (error) {
      return false;
    }
  },
};

// Error handling utilities
export const handleAPIError = (error: any): string => {
  if (error?.message) {
    return error.message;
  }
  
  if (typeof error === 'string') {
    return error;
  }
  
  return 'An unexpected error occurred. Please try again.';
};

export const isNetworkError = (error: any): boolean => {
  return error?.error === 'NetworkError' || 
         error?.code === 'NETWORK_ERROR' ||
         error?.message?.includes('Network Error');
};

export const isTimeoutError = (error: any): boolean => {
  return error?.code === 'ECONNABORTED' ||
         error?.message?.includes('timeout');
};

// Default configurations
export const API_CONFIG = {
  BASE_URL: 'http://localhost:8000',
  TIMEOUT: 60000,
  RETRY_ATTEMPTS: 3,
  RETRY_DELAY: 1000,
} as const;
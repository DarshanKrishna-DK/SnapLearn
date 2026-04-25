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
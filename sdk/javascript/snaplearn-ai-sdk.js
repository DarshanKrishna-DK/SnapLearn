/**
 * SnapLearn AI JavaScript SDK - Phase 5
 * Official JavaScript SDK for SnapLearn AI Platform Integration
 * 
 * @version 5.0.0
 * @author SnapLearn AI Team
 * @license MIT
 */

class SnapLearnAIError extends Error {
  constructor(message, code = 'SNAPLEARN_ERROR', details = {}) {
    super(message);
    this.name = 'SnapLearnAIError';
    this.code = code;
    this.details = details;
  }
}

/**
 * SnapLearn AI JavaScript SDK Client
 */
class SnapLearnAI {
  constructor(config = {}) {
    this.config = {
      apiKey: config.apiKey || process.env.SNAPLEARN_API_KEY,
      baseUrl: config.baseUrl || 'https://api.snaplearn.ai',
      timeout: config.timeout || 30000,
      retries: config.retries || 3,
      debug: config.debug || false,
      ...config
    };

    if (!this.config.apiKey) {
      throw new SnapLearnAIError('API key is required', 'MISSING_API_KEY');
    }

    this.headers = {
      'Authorization': `Bearer ${this.config.apiKey}`,
      'Content-Type': 'application/json',
      'User-Agent': 'SnapLearnAI-JS-SDK/5.0.0'
    };

    // Initialize service clients
    this.tutoring = new TutoringService(this);
    this.multimodal = new MultimodalService(this);
    this.conversation = new ConversationService(this);
    this.assessment = new AssessmentService(this);
    this.video = new VideoService(this);
    this.analytics = new AnalyticsService(this);
    this.students = new StudentService(this);
    this.demo = new DemoService(this);
  }

  /**
   * Make authenticated API request
   */
  async request(method, endpoint, data = null, options = {}) {
    const url = `${this.config.baseUrl}${endpoint}`;
    const config = {
      method: method.toUpperCase(),
      headers: { ...this.headers, ...options.headers },
      ...options
    };

    if (data && ['POST', 'PUT', 'PATCH'].includes(config.method)) {
      config.body = JSON.stringify(data);
    }

    let attempt = 0;
    while (attempt < this.config.retries) {
      try {
        const response = await this._makeRequest(url, config);
        return await this._handleResponse(response);
      } catch (error) {
        attempt++;
        if (attempt === this.config.retries || !this._shouldRetry(error)) {
          throw error;
        }
        await this._delay(Math.pow(2, attempt) * 1000); // Exponential backoff
      }
    }
  }

  async _makeRequest(url, config) {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), this.config.timeout);
    
    try {
      const response = await fetch(url, {
        ...config,
        signal: controller.signal
      });
      clearTimeout(timeoutId);
      return response;
    } catch (error) {
      clearTimeout(timeoutId);
      throw error;
    }
  }

  async _handleResponse(response) {
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new SnapLearnAIError(
        errorData.detail || `HTTP ${response.status}: ${response.statusText}`,
        'API_ERROR',
        { status: response.status, ...errorData }
      );
    }

    const contentType = response.headers.get('content-type');
    if (contentType && contentType.includes('application/json')) {
      return await response.json();
    }
    return await response.text();
  }

  _shouldRetry(error) {
    return error.code === 'API_ERROR' && 
           error.details.status >= 500 ||
           error.name === 'AbortError';
  }

  _delay(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
  }

  /**
   * Health check
   */
  async health() {
    return await this.request('GET', '/health');
  }
}

/**
 * AI Tutoring Service
 */
class TutoringService {
  constructor(client) {
    this.client = client;
  }

  /**
   * Generate AI explanation for a question
   */
  async generateExplanation(question, options = {}) {
    const payload = {
      question,
      student_id: options.studentId || 'anonymous',
      grade_level: options.gradeLevel || '5',
      language: options.language || 'en',
      ...options
    };

    return await this.client.request('POST', '/api/tutor/explain', payload);
  }

  /**
   * Get follow-up questions
   */
  async getFollowUpQuestions(topic, options = {}) {
    const params = new URLSearchParams({
      topic,
      student_id: options.studentId || 'anonymous',
      grade_level: options.gradeLevel || '5',
      count: options.count || 3
    });

    return await this.client.request('GET', `/api/tutor/follow-up?${params}`);
  }

  /**
   * Assess student answer
   */
  async assessAnswer(question, answer, options = {}) {
    const payload = {
      question,
      student_answer: answer,
      student_id: options.studentId || 'anonymous',
      provide_feedback: options.provideFeedback !== false,
      ...options
    };

    return await this.client.request('POST', '/api/tutor/assess', payload);
  }
}

/**
 * Multimodal Input Service
 */
class MultimodalService {
  constructor(client) {
    this.client = client;
  }

  /**
   * Process uploaded image
   */
  async processImage(imageFile, options = {}) {
    const formData = new FormData();
    formData.append('image', imageFile);
    formData.append('student_id', options.studentId || 'anonymous');
    formData.append('extract_text', options.extractText !== false);
    formData.append('analyze_content', options.analyzeContent !== false);

    return await this.client.request('POST', '/api/process-image', formData, {
      headers: { 'Content-Type': undefined } // Let browser set multipart boundary
    });
  }

  /**
   * Process voice input
   */
  async processVoice(audioBlob, options = {}) {
    const formData = new FormData();
    formData.append('audio', audioBlob, 'recording.webm');
    formData.append('student_id', options.studentId || 'anonymous');
    formData.append('language', options.language || 'en');

    return await this.client.request('POST', '/api/process-voice', formData, {
      headers: { 'Content-Type': undefined }
    });
  }

  /**
   * Process text with enhancements
   */
  async processText(text, options = {}) {
    const payload = {
      text,
      student_id: options.studentId || 'anonymous',
      detect_language: options.detectLanguage !== false,
      extract_math: options.extractMath !== false,
      normalize_text: options.normalizeText !== false,
      ...options
    };

    return await this.client.request('POST', '/api/process-text', payload);
  }
}

/**
 * Conversation Service (Phase 3)
 */
class ConversationService {
  constructor(client) {
    this.client = client;
  }

  /**
   * Start new conversation
   */
  async startConversation(initialQuestion, options = {}) {
    const payload = {
      student_id: options.studentId || 'anonymous',
      initial_question: initialQuestion,
      grade_level: options.gradeLevel || '5',
      language: options.language || 'en',
      context: options.context,
      ...options
    };

    return await this.client.request('POST', '/api/conversation/start', payload);
  }

  /**
   * Continue existing conversation
   */
  async continueConversation(conversationId, message, options = {}) {
    const payload = {
      conversation_id: conversationId,
      student_input: message,
      input_type: options.inputType || 'question',
      ...options
    };

    return await this.client.request('POST', '/api/conversation/continue', payload);
  }

  /**
   * Get conversation summary
   */
  async getConversationSummary(conversationId) {
    return await this.client.request('GET', `/api/conversation/${conversationId}/summary`);
  }
}

/**
 * Assessment Service
 */
class AssessmentService {
  constructor(client) {
    this.client = client;
  }

  /**
   * Create new assessment
   */
  async createAssessment(templateId, studentId, options = {}) {
    const payload = {
      template_id: templateId,
      student_id: studentId,
      customizations: options.customizations,
      ...options
    };

    return await this.client.request('POST', '/api/assessment/create', payload);
  }

  /**
   * Start assessment
   */
  async startAssessment(assessmentId) {
    return await this.client.request('POST', `/api/assessment/${assessmentId}/start`);
  }

  /**
   * Submit response
   */
  async submitResponse(assessmentId, questionId, response) {
    const payload = {
      assessment_id: assessmentId,
      question_id: questionId,
      ...response
    };

    return await this.client.request('POST', `/api/assessment/${assessmentId}/submit`, payload);
  }

  /**
   * Get assessment results
   */
  async getResults(assessmentId) {
    return await this.client.request('GET', `/api/assessment/${assessmentId}/results`);
  }

  /**
   * Get available assessment templates
   */
  async getTemplates() {
    return await this.client.request('GET', '/api/assessment/templates');
  }

  /**
   * Get comprehensive assessment analytics
   */
  async getAnalytics(studentId, options = {}) {
    const params = new URLSearchParams({
      student_id: studentId,
      period: options.period || 'month',
      ...options
    });

    return await this.client.request('GET', `/api/assessment/analytics?${params}`);
  }
}

/**
 * Video Generation Service (Phase 4)
 */
class VideoService {
  constructor(client) {
    this.client = client;
  }

  /**
   * Generate contextual video
   */
  async generateVideo(topic, options = {}) {
    const payload = {
      topic,
      student_id: options.studentId || 'anonymous',
      grade_level: options.gradeLevel || '5',
      language: options.language || 'en',
      video_quality: options.quality || 'high',
      video_format: options.format || 'mp4',
      animation_style: options.animationStyle || 'modern',
      target_duration: options.duration || 180,
      conversation_context: options.conversationContext,
      ...options
    };

    return await this.client.request('POST', '/api/video/generate-contextual', payload);
  }

  /**
   * Create batch video generation
   */
  async createBatch(learningPath, options = {}) {
    const payload = {
      ...learningPath,
      video_settings: options.videoSettings || {},
      ...options
    };

    return await this.client.request('POST', '/api/video/batch-generate', payload);
  }

  /**
   * Get batch status
   */
  async getBatchStatus(batchId) {
    return await this.client.request('GET', `/api/video/batch-status/${batchId}`);
  }

  /**
   * Cancel batch
   */
  async cancelBatch(batchId) {
    return await this.client.request('DELETE', `/api/video/batch-cancel/${batchId}`);
  }

  /**
   * Start video session tracking
   */
  async startSession(videoId, studentId, metadata = {}) {
    const payload = {
      video_id: videoId,
      student_id: studentId,
      video_metadata: metadata
    };

    return await this.client.request('POST', '/api/video/session/start', payload);
  }

  /**
   * Track video interaction
   */
  async trackInteraction(sessionId, interactionType, videoPosition, options = {}) {
    const payload = {
      session_id: sessionId,
      interaction_type: interactionType,
      video_position: videoPosition,
      duration: options.duration,
      metadata: options.metadata || {}
    };

    return await this.client.request('POST', '/api/video/session/track', payload);
  }

  /**
   * End video session
   */
  async endSession(sessionId, finalPosition = null) {
    const payload = { final_position: finalPosition };
    return await this.client.request('POST', `/api/video/session/end/${sessionId}`, payload);
  }

  /**
   * Get video analytics
   */
  async getAnalytics(videoId) {
    return await this.client.request('GET', `/api/video/analytics/${videoId}`);
  }

  /**
   * Submit video feedback
   */
  async submitFeedback(videoId, studentId, rating, feedback = {}) {
    const payload = {
      video_id: videoId,
      student_id: studentId,
      rating,
      feedback_text: feedback.text,
      improvement_suggestions: feedback.suggestions || []
    };

    return await this.client.request('POST', '/api/video/feedback', payload);
  }

  /**
   * Get video recommendations
   */
  async getRecommendations(studentId, limit = 10) {
    const params = new URLSearchParams({ student_id: studentId, limit });
    return await this.client.request('GET', `/api/video/recommendations?${params}`);
  }
}

/**
 * Analytics Service
 */
class AnalyticsService {
  constructor(client) {
    this.client = client;
  }

  /**
   * Get learning analytics
   */
  async getLearningAnalytics(studentId, options = {}) {
    const params = new URLSearchParams({
      student_id: studentId,
      period: options.period || 'week',
      ...options
    });

    return await this.client.request('GET', `/api/analytics/learning?${params}`);
  }

  /**
   * Get parent dashboard data
   */
  async getParentDashboard(studentId) {
    return await this.client.request('GET', `/api/dashboard/parent/${studentId}`);
  }

  /**
   * Get study recommendations
   */
  async getStudyRecommendations(studentId, options = {}) {
    const payload = {
      student_id: studentId,
      available_time: options.availableTime || 30,
      focus_areas: options.focusAreas || [],
      ...options
    };

    return await this.client.request('POST', '/api/recommendations/study', payload);
  }
}

/**
 * Student Profile Service
 */
class StudentService {
  constructor(client) {
    this.client = client;
  }

  /**
   * Get student profile
   */
  async getProfile(studentId) {
    return await this.client.request('GET', `/api/student/${studentId}/profile`);
  }

  /**
   * Update student profile
   */
  async updateProfile(studentId, updates) {
    return await this.client.request('PUT', `/api/student/${studentId}/profile`, updates);
  }

  /**
   * Reset student profile for testing
   */
  async resetProfile(studentId) {
    return await this.client.request('POST', `/api/debug/reset/${studentId}`);
  }
}

/**
 * SDK Demo Service (Phase 5)
 */
class DemoService {
  constructor(client) {
    this.client = client;
  }

  /**
   * Get available demo scenarios
   */
  async getAvailabledemos() {
    return await this.client.request('GET', '/api/demo/available');
  }

  /**
   * Start demo session
   */
  async startSession(scenario, visitorInfo = {}) {
    const payload = {
      scenario,
      visitor_info: visitorInfo
    };

    return await this.client.request('POST', '/api/demo/start', payload);
  }

  /**
   * Execute demo step
   */
  async executeStep(sessionId, stepOverride = null) {
    const payload = stepOverride ? { step_override: stepOverride } : {};
    return await this.client.request('POST', `/api/demo/${sessionId}/execute`, payload);
  }

  /**
   * Get demo session status
   */
  async getSessionStatus(sessionId) {
    return await this.client.request('GET', `/api/demo/${sessionId}/status`);
  }

  /**
   * Complete demo session
   */
  async completeSession(sessionId, feedback = {}) {
    return await this.client.request('POST', `/api/demo/${sessionId}/complete`, { feedback });
  }
}

/**
 * Utility Functions
 */
class SnapLearnUtils {
  /**
   * Validate grade level
   */
  static isValidGradeLevel(grade) {
    const validGrades = ['K', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12'];
    return validGrades.includes(String(grade).toUpperCase());
  }

  /**
   * Validate language code
   */
  static isValidLanguageCode(lang) {
    const validLangs = ['en', 'es', 'fr', 'de', 'it', 'pt', 'zh', 'ja', 'ko'];
    return validLangs.includes(lang.toLowerCase());
  }

  /**
   * Format error for display
   */
  static formatError(error) {
    if (error instanceof SnapLearnAIError) {
      return {
        message: error.message,
        code: error.code,
        details: error.details
      };
    }
    return {
      message: error.message || 'Unknown error',
      code: 'UNKNOWN_ERROR',
      details: {}
    };
  }

  /**
   * Create student profile object
   */
  static createStudentProfile(options = {}) {
    return {
      student_id: options.studentId || `student_${Date.now()}`,
      grade_level: options.gradeLevel || '5',
      learning_style: options.learningStyle || 'balanced',
      subjects: options.subjects || ['mathematics'],
      language: options.language || 'en',
      confusion_patterns: options.confusionPatterns || {},
      success_patterns: options.successPatterns || {}
    };
  }
}

// Export for different environments
if (typeof module !== 'undefined' && module.exports) {
  // Node.js
  module.exports = {
    SnapLearnAI,
    SnapLearnAIError,
    SnapLearnUtils
  };
} else if (typeof window !== 'undefined') {
  // Browser
  window.SnapLearnAI = SnapLearnAI;
  window.SnapLearnAIError = SnapLearnAIError;
  window.SnapLearnUtils = SnapLearnUtils;
}

/**
 * Usage Examples:
 * 
 * // Initialize client
 * const snaplearn = new SnapLearnAI({
 *   apiKey: 'your-api-key',
 *   baseUrl: 'https://api.snaplearn.ai'
 * });
 * 
 * // Generate explanation
 * const explanation = await snaplearn.tutoring.generateExplanation(
 *   'What is 2 + 2?',
 *   { studentId: 'student_123', gradeLevel: '2' }
 * );
 * 
 * // Process image
 * const result = await snaplearn.multimodal.processImage(
 *   imageFile,
 *   { studentId: 'student_123', extractText: true }
 * );
 * 
 * // Start conversation
 * const conversation = await snaplearn.conversation.startConversation(
 *   'Help me with algebra',
 *   { studentId: 'student_123', gradeLevel: '8' }
 * );
 * 
 * // Generate video
 * const video = await snaplearn.video.generateVideo(
 *   'Quadratic Equations',
 *   { 
 *     studentId: 'student_123',
 *     gradeLevel: '10',
 *     animationStyle: 'mathematical',
 *     quality: 'high'
 *   }
 * );
 * 
 * // Create assessment
 * const assessment = await snaplearn.assessment.createAssessment(
 *   'high_school_algebra',
 *   'student_123'
 * );
 * 
 * // Start demo
 * const demo = await snaplearn.demo.startSession(
 *   'elementary_math',
 *   { organization: 'My School' }
 * );
 */
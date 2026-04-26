import React, { useState, useEffect, useCallback, useRef } from 'react';
import { 
  MessageCircle, 
  Brain, 
  TrendingUp, 
  Target, 
  BookOpen, 
  Clock,
  AlertCircle,
  CheckCircle,
  ArrowRight,
  Settings,
  BarChart3,
  Lightbulb,
  RefreshCw,
  Pause,
  Play
} from 'lucide-react';
import { toast } from 'react-hot-toast';

import { apiClient } from '@/utils/api';
import {
  ConversationRequest,
  ConversationResponse,
  ConversationMessage,
  AssessmentAnalytics,
  DifficultyAdaptationResponse,
  StudyRecommendationResponse,
  GradeLevel,
  LanguageCode,
  LearningAnalytics
} from '@/types';
import AnimatedBlackboard from './AnimatedBlackboard';

interface AdvancedTutorPageProps {
  studentId: string;
  gradeLevel: GradeLevel;
  language?: LanguageCode;
}

interface ConversationState {
  conversation_id: string | null;
  messages: ConversationMessage[];
  current_state: string;
  turn_count: number;
  is_active: boolean;
}

interface AdaptiveMetrics {
  current_difficulty: string;
  explanation_style: string;
  engagement_level: number;
  adaptations_made: number;
  session_time: number;
}

const AdvancedTutorPage: React.FC<AdvancedTutorPageProps> = ({
  studentId,
  gradeLevel,
  language = 'en'
}) => {
  // Conversation State
  const [conversation, setConversation] = useState<ConversationState>({
    conversation_id: null,
    messages: [],
    current_state: 'idle',
    turn_count: 0,
    is_active: false
  });

  // UI State
  const [currentInput, setCurrentInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [activeTab, setActiveTab] = useState<'conversation' | 'analytics' | 'recommendations'>('conversation');
  
  // Advanced Features State
  const [adaptiveMetrics, setAdaptiveMetrics] = useState<AdaptiveMetrics>({
    current_difficulty: 'medium',
    explanation_style: 'balanced',
    engagement_level: 0.75,
    adaptations_made: 0,
    session_time: 0
  });

  const [assessmentAnalytics, setAssessmentAnalytics] = useState<AssessmentAnalytics | null>(null);
  const [studyRecommendations, setStudyRecommendations] = useState<StudyRecommendationResponse | null>(null);
  const [learningAnalytics, setLearningAnalytics] = useState<LearningAnalytics | null>(null);
  
  // Real-time monitoring
  const [confusionDetected, setConfusionDetected] = useState(false);
  const [responseTime, setResponseTime] = useState(0);
  const responseStartTime = useRef<number>(0);
  
  // Session management
  const [sessionStartTime] = useState(Date.now());
  const sessionTimer = useRef<NodeJS.Timeout | null>(null);

  // Auto-scroll for messages
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Initialize session timer
  useEffect(() => {
    sessionTimer.current = setInterval(() => {
      setAdaptiveMetrics(prev => ({
        ...prev,
        session_time: Math.floor((Date.now() - sessionStartTime) / 1000)
      }));
    }, 1000);

    return () => {
      if (sessionTimer.current) {
        clearInterval(sessionTimer.current);
      }
    };
  }, [sessionStartTime]);

  // Load analytics on component mount
  useEffect(() => {
    loadAnalytics();
  }, [studentId]);

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [conversation.messages]);

  const loadAnalytics = async () => {
    try {
      const [assessment, learning] = await Promise.all([
        apiClient.getAssessmentAnalytics(studentId),
        apiClient.getLearningAnalytics(studentId, 'week')
      ]);

      setAssessmentAnalytics(assessment);
      setLearningAnalytics(learning);
    } catch (error) {
      console.error('Error loading analytics:', error);
    }
  };

  const startConversation = async (initialQuestion: string) => {
    setIsLoading(true);
    responseStartTime.current = Date.now();

    try {
      const request: ConversationRequest = {
        student_id: studentId,
        input_text: initialQuestion,
        input_type: 'question'
      };

      const response = await apiClient.startConversation(request);
      
      const newMessages: ConversationMessage[] = [
        {
          id: `msg-${Date.now()}-1`,
          type: 'student',
          content: initialQuestion,
          timestamp: new Date().toISOString()
        },
        {
          id: `msg-${Date.now()}-2`,
          type: 'ai',
          content: response.response.explanation_text,
          timestamp: new Date().toISOString(),
          metadata: {
            board_script: response.response.board_script,
            key_concepts: response.response.key_concepts,
            follow_up_questions: response.response.follow_up_questions,
            difficulty_level: response.response.difficulty_level
          }
        }
      ];

      setConversation({
        conversation_id: response.conversation_id,
        messages: newMessages,
        current_state: response.state,
        turn_count: response.turn_count,
        is_active: true
      });

      // Update adaptive metrics
      setAdaptiveMetrics(prev => ({
        ...prev,
        current_difficulty: response.response.difficulty_level,
        adaptations_made: prev.adaptations_made + (response.response.difficulty_level !== prev.current_difficulty ? 1 : 0)
      }));

      toast.success('Conversation started successfully!');

    } catch (error) {
      console.error('Error starting conversation:', error);
      toast.error('Failed to start conversation. Please try again.');
    } finally {
      setIsLoading(false);
      setResponseTime(Date.now() - responseStartTime.current);
    }
  };

  const continueConversation = async (message: string, inputType: string = 'question') => {
    if (!conversation.conversation_id) {
      toast.error('No active conversation');
      return;
    }

    setIsLoading(true);
    responseStartTime.current = Date.now();

    try {
      // Add user message immediately
      const userMessage: ConversationMessage = {
        id: `msg-${Date.now()}-user`,
        type: 'student',
        content: message,
        timestamp: new Date().toISOString()
      };

      setConversation(prev => ({
        ...prev,
        messages: [...prev.messages, userMessage]
      }));

      // Send to API
      const request: ConversationRequest = {
        student_id: studentId,
        input_text: message,
        conversation_id: conversation.conversation_id,
        input_type: inputType as any
      };

      const response = await apiClient.continueConversation(request);
      const currentResponseTime = Date.now() - responseStartTime.current;
      
      // Check for confusion
      await checkForConfusion(message, currentResponseTime);

      // Add AI response
      const aiMessage: ConversationMessage = {
        id: `msg-${Date.now()}-ai`,
        type: 'ai',
        content: response.response.explanation_text,
        timestamp: new Date().toISOString(),
        metadata: {
          board_script: response.response.board_script,
          key_concepts: response.response.key_concepts,
          follow_up_questions: response.response.follow_up_questions,
          difficulty_level: response.response.difficulty_level,
          learning_insights: response.learning_insights,
          recommendations: response.recommendations
        }
      };

      setConversation(prev => ({
        ...prev,
        messages: [...prev.messages, aiMessage],
        current_state: response.state,
        turn_count: response.turn_count
      }));

      // Update adaptive metrics based on response
      updateAdaptiveMetrics(response, currentResponseTime);

    } catch (error) {
      console.error('Error continuing conversation:', error);
      toast.error('Failed to send message. Please try again.');
    } finally {
      setIsLoading(false);
      setResponseTime(Date.now() - responseStartTime.current);
    }
  };

  const checkForConfusion = async (responseText: string, responseTime: number) => {
    try {
      const confusionResponse = await apiClient.detectConfusion({
        student_id: studentId,
        interaction_data: { conversation_id: conversation.conversation_id },
        response_time: responseTime / 1000, // Convert to seconds
        response_text: responseText
      });

      setConfusionDetected(confusionResponse.confusion_detected);

      if (confusionResponse.confusion_detected && confusionResponse.intervention_needed) {
        toast.warning('It seems like you might be confused. Let me help clarify!');
      }
    } catch (error) {
      console.error('Error detecting confusion:', error);
    }
  };

  const updateAdaptiveMetrics = (response: ConversationResponse, responseTime: number) => {
    setAdaptiveMetrics(prev => {
      const difficultyChanged = response.response.difficulty_level !== prev.current_difficulty;
      
      return {
        ...prev,
        current_difficulty: response.response.difficulty_level,
        engagement_level: Math.max(0, Math.min(1, prev.engagement_level + (responseTime < 15000 ? 0.1 : -0.05))),
        adaptations_made: prev.adaptations_made + (difficultyChanged ? 1 : 0)
      };
    });
  };

  const requestDifficultyAdaptation = async (reason: string) => {
    if (!conversation.conversation_id) return;

    try {
      const adaptationResponse = await apiClient.adaptDifficulty({
        student_id: studentId,
        current_difficulty: adaptiveMetrics.current_difficulty,
        recent_performance: {
          responses: conversation.messages.slice(-5),
          session: { duration_minutes: adaptiveMetrics.session_time / 60 }
        },
        topic: 'current_topic' // This could be extracted from conversation
      });

      setAdaptiveMetrics(prev => ({
        ...prev,
        current_difficulty: adaptationResponse.recommended_difficulty,
        adaptations_made: prev.adaptations_made + 1
      }));

      toast.success(`Difficulty adapted: ${adaptationResponse.adaptation_reason}`);
    } catch (error) {
      console.error('Error adapting difficulty:', error);
      toast.error('Failed to adapt difficulty');
    }
  };

  const loadStudyRecommendations = async () => {
    try {
      const recommendations = await apiClient.getStudyRecommendations({
        student_id: studentId,
        available_time: 30, // 30 minutes
        subject_preferences: ['math', 'science'],
        difficulty_preference: adaptiveMetrics.current_difficulty
      });

      setStudyRecommendations(recommendations);
    } catch (error) {
      console.error('Error loading study recommendations:', error);
    }
  };

  const handleSendMessage = () => {
    if (!currentInput.trim()) return;
    
    if (conversation.is_active) {
      continueConversation(currentInput.trim());
    } else {
      startConversation(currentInput.trim());
    }
    
    setCurrentInput('');
  };

  const formatTime = (seconds: number): string => {
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = seconds % 60;
    return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`;
  };

  const getCurrentMessage = (): ConversationMessage | null => {
    const aiMessages = conversation.messages.filter(m => m.type === 'ai');
    return aiMessages[aiMessages.length - 1] || null;
  };

  return (
    <div className="max-w-7xl mx-auto p-6 space-y-6">
      {/* Header with adaptive metrics */}
      <div className="bg-white rounded-xl shadow-lg p-6">
        <div className="flex items-center justify-between mb-4">
          <h1 className="text-3xl font-bold text-gray-800 flex items-center gap-3">
            <Brain className="text-blue-600" />
            Advanced AI Tutor
          </h1>
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-2 text-sm text-gray-600">
              <Clock className="w-4 h-4" />
              <span>{formatTime(adaptiveMetrics.session_time)}</span>
            </div>
            {confusionDetected && (
              <div className="flex items-center gap-2 text-orange-600 bg-orange-100 px-3 py-1 rounded-lg">
                <AlertCircle className="w-4 h-4" />
                <span className="text-sm">Confusion detected</span>
              </div>
            )}
          </div>
        </div>

        {/* Adaptive Metrics Dashboard */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="bg-blue-50 p-4 rounded-lg">
            <div className="flex items-center gap-2 mb-2">
              <Target className="w-5 h-5 text-blue-600" />
              <span className="font-medium text-blue-900">Difficulty</span>
            </div>
            <p className="text-2xl font-bold text-blue-700 capitalize">
              {adaptiveMetrics.current_difficulty}
            </p>
          </div>

          <div className="bg-green-50 p-4 rounded-lg">
            <div className="flex items-center gap-2 mb-2">
              <TrendingUp className="w-5 h-5 text-green-600" />
              <span className="font-medium text-green-900">Engagement</span>
            </div>
            <p className="text-2xl font-bold text-green-700">
              {Math.round(adaptiveMetrics.engagement_level * 100)}%
            </p>
          </div>

          <div className="bg-purple-50 p-4 rounded-lg">
            <div className="flex items-center gap-2 mb-2">
              <RefreshCw className="w-5 h-5 text-purple-600" />
              <span className="font-medium text-purple-900">Adaptations</span>
            </div>
            <p className="text-2xl font-bold text-purple-700">
              {adaptiveMetrics.adaptations_made}
            </p>
          </div>

          <div className="bg-orange-50 p-4 rounded-lg">
            <div className="flex items-center gap-2 mb-2">
              <MessageCircle className="w-5 h-5 text-orange-600" />
              <span className="font-medium text-orange-900">Turns</span>
            </div>
            <p className="text-2xl font-bold text-orange-700">
              {conversation.turn_count}
            </p>
          </div>
        </div>
      </div>

      {/* Main Content Tabs */}
      <div className="bg-white rounded-xl shadow-lg">
        <div className="border-b border-gray-200">
          <nav className="flex space-x-8 px-6">
            {[
              { id: 'conversation', label: 'Conversation', icon: MessageCircle },
              { id: 'analytics', label: 'Analytics', icon: BarChart3 },
              { id: 'recommendations', label: 'Recommendations', icon: Lightbulb }
            ].map(({ id, label, icon: Icon }) => (
              <button
                key={id}
                onClick={() => setActiveTab(id as any)}
                className={`flex items-center gap-2 py-4 px-2 border-b-2 font-medium text-sm ${
                  activeTab === id
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700'
                }`}
              >
                <Icon className="w-4 h-4" />
                {label}
              </button>
            ))}
          </nav>
        </div>

        <div className="p-6">
          {activeTab === 'conversation' && (
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              {/* Conversation Area */}
              <div className="lg:col-span-2 space-y-4">
                {/* Messages */}
                <div className="bg-gray-50 rounded-lg p-4 h-96 overflow-y-auto">
                  {conversation.messages.length === 0 ? (
                    <div className="text-center text-gray-500 py-8">
                      <MessageCircle className="w-12 h-12 mx-auto mb-4 text-gray-300" />
                      <p>Start a conversation by asking a question!</p>
                    </div>
                  ) : (
                    <div className="space-y-4">
                      {conversation.messages.map((message) => (
                        <div
                          key={message.id}
                          className={`flex ${message.type === 'student' ? 'justify-end' : 'justify-start'}`}
                        >
                          <div
                            className={`max-w-xs lg:max-w-md px-4 py-2 rounded-lg ${
                              message.type === 'student'
                                ? 'bg-blue-500 text-white'
                                : 'bg-white text-gray-800 shadow'
                            }`}
                          >
                            <p className="text-sm">{message.content}</p>
                            {message.metadata?.key_concepts && (
                              <div className="mt-2 pt-2 border-t border-gray-200">
                                <p className="text-xs text-gray-600 mb-1">Key concepts:</p>
                                <div className="flex flex-wrap gap-1">
                                  {message.metadata.key_concepts.map((concept: string, idx: number) => (
                                    <span
                                      key={idx}
                                      className="text-xs bg-blue-100 text-blue-800 px-2 py-1 rounded"
                                    >
                                      {concept}
                                    </span>
                                  ))}
                                </div>
                              </div>
                            )}
                          </div>
                        </div>
                      ))}
                      <div ref={messagesEndRef} />
                    </div>
                  )}
                </div>

                {/* Input Area */}
                <div className="flex gap-2">
                  <input
                    type="text"
                    value={currentInput}
                    onChange={(e) => setCurrentInput(e.target.value)}
                    onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
                    placeholder="Ask a question or respond..."
                    className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    disabled={isLoading}
                  />
                  <button
                    onClick={handleSendMessage}
                    disabled={isLoading || !currentInput.trim()}
                    className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
                  >
                    {isLoading ? (
                      <RefreshCw className="w-4 h-4 animate-spin" />
                    ) : (
                      <ArrowRight className="w-4 h-4" />
                    )}
                    Send
                  </button>
                </div>

                {/* Quick Actions */}
                <div className="flex gap-2 text-sm">
                  <button
                    onClick={() => requestDifficultyAdaptation('User requested easier content')}
                    className="px-3 py-1 bg-yellow-100 text-yellow-800 rounded-lg hover:bg-yellow-200"
                  >
                    Make it easier
                  </button>
                  <button
                    onClick={() => requestDifficultyAdaptation('User requested harder content')}
                    className="px-3 py-1 bg-red-100 text-red-800 rounded-lg hover:bg-red-200"
                  >
                    Make it harder
                  </button>
                  <button
                    onClick={() => {
                      if (conversation.current_state === 'paused') {
                        // Resume logic would go here
                      } else {
                        // Pause logic would go here
                      }
                    }}
                    className="px-3 py-1 bg-gray-100 text-gray-800 rounded-lg hover:bg-gray-200 flex items-center gap-1"
                  >
                    {conversation.current_state === 'paused' ? (
                      <>
                        <Play className="w-3 h-3" />
                        Resume
                      </>
                    ) : (
                      <>
                        <Pause className="w-3 h-3" />
                        Pause
                      </>
                    )}
                  </button>
                </div>
              </div>

              {/* Blackboard Animation */}
              <div className="bg-black rounded-lg overflow-hidden">
                {getCurrentMessage()?.metadata?.board_script && (
                  <AnimatedBlackboard
                    script={getCurrentMessage()!.metadata!.board_script}
                    isPlaying={true}
                  />
                )}
              </div>
            </div>
          )}

          {activeTab === 'analytics' && (
            <div className="space-y-6">
              {/* Assessment Analytics */}
              {assessmentAnalytics && (
                <div className="bg-gradient-to-r from-blue-50 to-purple-50 p-6 rounded-lg">
                  <h3 className="text-xl font-bold mb-4 flex items-center gap-2">
                    <BarChart3 className="text-blue-600" />
                    Assessment Analytics
                  </h3>
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div className="bg-white p-4 rounded-lg">
                      <p className="text-sm text-gray-600">Total Assessments</p>
                      <p className="text-2xl font-bold text-blue-600">
                        {assessmentAnalytics.total_assessments}
                      </p>
                    </div>
                    <div className="bg-white p-4 rounded-lg">
                      <p className="text-sm text-gray-600">Improvement Areas</p>
                      <p className="text-lg font-semibold text-orange-600">
                        {assessmentAnalytics.improvement_areas.length}
                      </p>
                    </div>
                    <div className="bg-white p-4 rounded-lg">
                      <p className="text-sm text-gray-600">Strengths</p>
                      <p className="text-lg font-semibold text-green-600">
                        {assessmentAnalytics.strengths.length}
                      </p>
                    </div>
                  </div>

                  {/* Mistake Patterns */}
                  <div className="mt-4">
                    <h4 className="font-semibold mb-2">Common Mistake Patterns</h4>
                    <div className="space-y-2">
                      {Object.entries(assessmentAnalytics.mistake_patterns).map(([pattern, count]) => (
                        <div key={pattern} className="flex justify-between items-center bg-white p-3 rounded">
                          <span className="capitalize">{pattern.replace('_', ' ')}</span>
                          <span className="font-semibold text-red-600">{count}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              )}

              {/* Learning Analytics */}
              {learningAnalytics && (
                <div className="bg-gradient-to-r from-green-50 to-blue-50 p-6 rounded-lg">
                  <h3 className="text-xl font-bold mb-4 flex items-center gap-2">
                    <TrendingUp className="text-green-600" />
                    Learning Progress
                  </h3>
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div className="bg-white p-4 rounded-lg">
                      <p className="text-sm text-gray-600">Total Sessions</p>
                      <p className="text-2xl font-bold text-green-600">
                        {learningAnalytics.total_sessions}
                      </p>
                    </div>
                    <div className="bg-white p-4 rounded-lg">
                      <p className="text-sm text-gray-600">Time Spent (hours)</p>
                      <p className="text-2xl font-bold text-blue-600">
                        {Math.round(learningAnalytics.total_time_minutes / 60)}
                      </p>
                    </div>
                    <div className="bg-white p-4 rounded-lg">
                      <p className="text-sm text-gray-600">Concepts Mastered</p>
                      <p className="text-2xl font-bold text-purple-600">
                        {learningAnalytics.concepts_mastered.length}
                      </p>
                    </div>
                  </div>

                  {/* Mastered Concepts */}
                  <div className="mt-4">
                    <h4 className="font-semibold mb-2">Mastered Concepts</h4>
                    <div className="flex flex-wrap gap-2">
                      {learningAnalytics.concepts_mastered.map((concept, idx) => (
                        <span
                          key={idx}
                          className="bg-green-100 text-green-800 px-3 py-1 rounded-full text-sm flex items-center gap-1"
                        >
                          <CheckCircle className="w-3 h-3" />
                          {concept}
                        </span>
                      ))}
                    </div>
                  </div>
                </div>
              )}
            </div>
          )}

          {activeTab === 'recommendations' && (
            <div className="space-y-6">
              <div className="flex justify-between items-center">
                <h3 className="text-xl font-bold flex items-center gap-2">
                  <Lightbulb className="text-yellow-600" />
                  Personalized Study Recommendations
                </h3>
                <button
                  onClick={loadStudyRecommendations}
                  className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 flex items-center gap-2"
                >
                  <RefreshCw className="w-4 h-4" />
                  Refresh
                </button>
              </div>

              {studyRecommendations ? (
                <div className="space-y-4">
                  {/* Motivational Message */}
                  <div className="bg-yellow-50 p-4 rounded-lg border-l-4 border-yellow-400">
                    <p className="text-yellow-800 font-medium">
                      {studyRecommendations.motivational_message}
                    </p>
                  </div>

                  {/* Recommended Activities */}
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {studyRecommendations.recommended_activities.map((activity, idx) => (
                      <div key={idx} className="bg-white p-4 border rounded-lg hover:shadow-md transition-shadow">
                        <div className="flex justify-between items-start mb-2">
                          <h4 className="font-semibold text-gray-800">{activity.activity}</h4>
                          <span className="text-sm text-gray-500">{activity.duration} min</span>
                        </div>
                        <p className="text-sm text-gray-600 mb-2">{activity.description}</p>
                        <div className="flex gap-2">
                          <span className="text-xs bg-blue-100 text-blue-800 px-2 py-1 rounded">
                            {activity.subject}
                          </span>
                          <span className="text-xs bg-purple-100 text-purple-800 px-2 py-1 rounded">
                            {activity.difficulty}
                          </span>
                        </div>
                      </div>
                    ))}
                  </div>

                  {/* Focus Areas */}
                  <div className="bg-red-50 p-4 rounded-lg">
                    <h4 className="font-semibold text-red-900 mb-2">Areas to Focus On</h4>
                    <div className="space-y-1">
                      {studyRecommendations.focus_areas.map((area, idx) => (
                        <div key={idx} className="flex items-center gap-2">
                          <Target className="w-4 h-4 text-red-600" />
                          <span className="text-red-800">{area}</span>
                        </div>
                      ))}
                    </div>
                  </div>

                  {/* Study Reminders */}
                  <div className="bg-blue-50 p-4 rounded-lg">
                    <h4 className="font-semibold text-blue-900 mb-2">Study Tips & Reminders</h4>
                    <div className="space-y-1">
                      {studyRecommendations.reminder_suggestions.map((reminder, idx) => (
                        <div key={idx} className="flex items-center gap-2">
                          <BookOpen className="w-4 h-4 text-blue-600" />
                          <span className="text-blue-800">{reminder}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              ) : (
                <div className="text-center py-8 text-gray-500">
                  <Lightbulb className="w-12 h-12 mx-auto mb-4 text-gray-300" />
                  <p>Click "Refresh" to load personalized study recommendations</p>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default AdvancedTutorPage;
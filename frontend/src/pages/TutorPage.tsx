import React, { useState, useCallback } from 'react';
import { toast } from 'react-hot-toast';
import { Send, RotateCcw, BookOpen, Lightbulb, Type, Image, Mic } from 'lucide-react';

// Components
import LoadingSpinner from '@/components/ui/LoadingSpinner';
import AnimatedBlackboard from '@/components/AnimatedBlackboard';
import QuestionInput from '@/components/QuestionInput';
import ImageUpload from '@/components/ImageUpload';
import VoiceInput from '@/components/VoiceInput';

// Utils and types
import { apiClient, handleAPIError } from '@/utils/api';
import { 
  ExplanationResponse, 
  GradeLevel, 
  LanguageCode,
  QuestionRequest 
} from '@/types';

interface TutorPageProps {
  studentId: string;
  gradeLevel: GradeLevel;
  language: LanguageCode;
}

const TutorPage: React.FC<TutorPageProps> = ({ 
  studentId, 
  gradeLevel, 
  language 
}) => {
  // State management
  const [currentQuestion, setCurrentQuestion] = useState('');
  const [explanation, setExplanation] = useState<ExplanationResponse | null>(null);
  const [isGenerating, setIsGenerating] = useState(false);
  const [showFollowUp, setShowFollowUp] = useState(false);
  
  // Phase 2: Input modality state
  const [inputMode, setInputMode] = useState<'text' | 'image' | 'voice'>('text');

  // Handle question submission
  const handleQuestionSubmit = useCallback(async (question: string) => {
    if (!question.trim()) {
      toast.error('Please enter a question');
      return;
    }

    setIsGenerating(true);
    setExplanation(null);
    setShowFollowUp(false);
    setCurrentQuestion(question);

    try {
      const request: QuestionRequest = {
        question: question.trim(),
        student_id: studentId,
        grade_level: gradeLevel,
        language: language,
      };

      const response = await apiClient.explain(request);
      
      setExplanation(response);
      toast.success('Explanation generated successfully!');
      
      // Show follow-up questions after animation completes
      setTimeout(() => {
        setShowFollowUp(true);
      }, response.board_script.total_duration_ms + 1000);

    } catch (error) {
      console.error('Error generating explanation:', error);
      toast.error(handleAPIError(error));
    } finally {
      setIsGenerating(false);
    }
  }, [studentId, gradeLevel, language]);

  // Handle follow-up question selection
  const handleFollowUpClick = (followUpQuestion: string) => {
    setCurrentQuestion(followUpQuestion);
    handleQuestionSubmit(followUpQuestion);
  };

  // Phase 2: Handle extracted text from image or voice
  const handleExtractedText = useCallback((extractedText: string) => {
    setCurrentQuestion(extractedText);
    // Automatically process the extracted text
    handleQuestionSubmit(extractedText);
  }, [handleQuestionSubmit]);

  // Reset the session
  const handleReset = () => {
    setCurrentQuestion('');
    setExplanation(null);
    setShowFollowUp(false);
  };

  // Suggested starter questions based on grade level
  const getStarterQuestions = (grade: GradeLevel): string[] => {
    const gradeNum = grade === 'K' ? 0 : parseInt(grade);
    
    if (gradeNum <= 2) {
      return [
        "What is addition?",
        "How do I count to 10?",
        "What are shapes?",
        "What is the alphabet?"
      ];
    } else if (gradeNum <= 5) {
      return [
        "How do I multiply numbers?",
        "What are fractions?",
        "How does photosynthesis work?",
        "What is the water cycle?"
      ];
    } else if (gradeNum <= 8) {
      return [
        "How do I solve algebraic equations?",
        "What is the Pythagorean theorem?",
        "How does DNA work?",
        "What causes seasons on Earth?"
      ];
    } else {
      return [
        "How do derivatives work in calculus?",
        "What is quantum physics?",
        "How do chemical bonds form?",
        "What is the theory of relativity?"
      ];
    }
  };

  const starterQuestions = getStarterQuestions(gradeLevel);

  return (
    <div className="max-w-6xl mx-auto space-y-8">
      {/* Header */}
      <div className="text-center">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">
          AI Tutor with Animated Blackboard
        </h1>
        <p className="text-gray-600 max-w-2xl mx-auto">
          Ask any question and get a personalized explanation with an animated blackboard demonstration.
          Designed for Grade {gradeLevel === 'K' ? 'K' : gradeLevel} level learning.
        </p>
      </div>

      {/* Question Input - Phase 2 Enhanced */}
      <div className="card">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center space-x-2">
            <BookOpen className="w-5 h-5 text-primary-600" />
            <h2 className="text-lg font-semibold text-gray-900">Ask Your Question</h2>
          </div>
          
          {explanation && (
            <button
              onClick={handleReset}
              className="btn-ghost flex items-center space-x-2"
            >
              <RotateCcw className="w-4 h-4" />
              <span>New Question</span>
            </button>
          )}
        </div>

        {/* Input Mode Tabs */}
        <div className="flex space-x-1 mb-4 bg-gray-100 p-1 rounded-lg">
          <button
            onClick={() => setInputMode('text')}
            className={`flex items-center space-x-2 px-4 py-2 rounded-md text-sm font-medium transition-colors ${
              inputMode === 'text'
                ? 'bg-white text-primary-600 shadow-sm'
                : 'text-gray-600 hover:text-gray-900'
            }`}
          >
            <Type className="w-4 h-4" />
            <span>Type</span>
          </button>
          
          <button
            onClick={() => setInputMode('image')}
            className={`flex items-center space-x-2 px-4 py-2 rounded-md text-sm font-medium transition-colors ${
              inputMode === 'image'
                ? 'bg-white text-primary-600 shadow-sm'
                : 'text-gray-600 hover:text-gray-900'
            }`}
          >
            <Image className="w-4 h-4" />
            <span>Image</span>
          </button>
          
          <button
            onClick={() => setInputMode('voice')}
            className={`flex items-center space-x-2 px-4 py-2 rounded-md text-sm font-medium transition-colors ${
              inputMode === 'voice'
                ? 'bg-white text-primary-600 shadow-sm'
                : 'text-gray-600 hover:text-gray-900'
            }`}
          >
            <Mic className="w-4 h-4" />
            <span>Voice</span>
          </button>
        </div>

        {/* Input Content Based on Mode */}
        {inputMode === 'text' && (
          <div>
            <p className="text-sm text-gray-600 mb-3">
              Type your question directly or copy-paste from anywhere.
            </p>
            <QuestionInput
              value={currentQuestion}
              onChange={setCurrentQuestion}
              onSubmit={() => handleQuestionSubmit(currentQuestion)}
              isLoading={isGenerating}
              placeholder="What would you like to learn about today?"
              className="mb-4"
            />

            <button
              onClick={() => handleQuestionSubmit(currentQuestion)}
              disabled={isGenerating || !currentQuestion.trim()}
              className="btn-primary flex items-center space-x-2"
            >
              {isGenerating ? (
                <>
                  <LoadingSpinner size="sm" />
                  <span>Generating explanation...</span>
                </>
              ) : (
                <>
                  <Send className="w-4 h-4" />
                  <span>Get Explanation</span>
                </>
              )}
            </button>
          </div>
        )}

        {inputMode === 'image' && (
          <div>
            <p className="text-sm text-gray-600 mb-3">
              Upload a photo of homework, textbook pages, or handwritten problems. Perfect for math equations and diagrams.
            </p>
            <ImageUpload
              studentId={studentId}
              gradeLevel={gradeLevel}
              language={language}
              onTextExtracted={handleExtractedText}
            />
          </div>
        )}

        {inputMode === 'voice' && (
          <div>
            <p className="text-sm text-gray-600 mb-3">
              Record your question by speaking. Great for complex problems that are easier to explain verbally.
            </p>
            <VoiceInput
              studentId={studentId}
              gradeLevel={gradeLevel}
              language={language}
              onTextTranscribed={handleExtractedText}
            />
          </div>
        )}
      </div>

      {/* Starter questions (shown when no explanation is active) */}
      {!explanation && !isGenerating && (
        <div className="card">
          <div className="flex items-center space-x-2 mb-4">
            <Lightbulb className="w-5 h-5 text-yellow-500" />
            <h3 className="text-lg font-semibold text-gray-900">
              Try These Questions
            </h3>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {starterQuestions.map((question, index) => (
              <button
                key={index}
                onClick={() => {
                  setCurrentQuestion(question);
                  handleQuestionSubmit(question);
                }}
                className="text-left p-3 bg-gray-50 hover:bg-gray-100 rounded-lg transition-colors text-sm"
              >
                "{question}"
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Animated Blackboard */}
      {(explanation || isGenerating) && (
        <div className="card p-0 overflow-hidden">
          <div className="p-6 border-b border-gray-200">
            <h2 className="text-lg font-semibold text-gray-900">
              {isGenerating ? 'Preparing explanation...' : currentQuestion}
            </h2>
            {explanation && (
              <div className="flex items-center space-x-4 mt-2 text-sm text-gray-600">
                <span>Difficulty: {explanation.difficulty_level}</span>
                <span>•</span>
                <span>Confidence: {Math.round(explanation.confidence_score * 100)}%</span>
              </div>
            )}
          </div>
          
          {isGenerating ? (
            <div className="flex items-center justify-center py-16">
              <div className="text-center">
                <LoadingSpinner size="lg" />
                <p className="mt-4 text-gray-600">
                  Generating personalized explanation...
                </p>
              </div>
            </div>
          ) : explanation ? (
            <AnimatedBlackboard 
              script={explanation.board_script}
              isPlaying={true}
              onAnimationComplete={() => console.log('Animation completed')}
            />
          ) : null}
        </div>
      )}

      {/* Explanation Text and Key Concepts */}
      {explanation && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Explanation Text */}
          <div className="card">
            <h3 className="text-lg font-semibold text-gray-900 mb-3">
              Detailed Explanation
            </h3>
            <div className="prose prose-sm max-w-none">
              <p className="text-gray-700 leading-relaxed">
                {explanation.explanation_text}
              </p>
            </div>
          </div>

          {/* Key Concepts */}
          <div className="card">
            <h3 className="text-lg font-semibold text-gray-900 mb-3">
              Key Concepts
            </h3>
            <div className="space-y-2">
              {explanation.key_concepts.map((concept, index) => (
                <div
                  key={index}
                  className="bg-primary-50 text-primary-700 px-3 py-2 rounded-lg text-sm"
                >
                  {concept}
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Follow-up Questions */}
      {showFollowUp && explanation && explanation.follow_up_questions.length > 0 && (
        <div className="card">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">
            Continue Learning
          </h3>
          <div className="space-y-2">
            {explanation.follow_up_questions.map((question, index) => (
              <button
                key={index}
                onClick={() => handleFollowUpClick(question)}
                className="w-full text-left p-3 bg-secondary-50 hover:bg-secondary-100 text-secondary-800 rounded-lg transition-colors"
              >
                {question}
              </button>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default TutorPage;
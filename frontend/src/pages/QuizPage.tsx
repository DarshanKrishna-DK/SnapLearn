import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { api } from '../utils/api';
import LoadingSpinner from '../components/ui/LoadingSpinner';

interface QuizQuestion {
  id: string;
  question: string;
  options: string[];
  topic: string;
  difficulty: string;
}

interface Quiz {
  quiz_id: string;
  title: string;
  topic: string;
  grade_level: string;
  difficulty: string;
  time_limit_minutes: number;
  questions: QuizQuestion[];
  personalization_notes: {
    student_weaknesses_targeted: string[];
    recommended_difficulty: string;
    quiz_accuracy_history: number;
  };
}

interface Props {
  studentId: string;
  gradeLevel: string;
}

const QuizPage: React.FC<Props> = ({ studentId, gradeLevel }) => {
  const navigate = useNavigate();
  const [currentQuiz, setCurrentQuiz] = useState<Quiz | null>(null);
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
  const [answers, setAnswers] = useState<Record<string, number>>({});
  const [timeLeft, setTimeLeft] = useState(0);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [quizComplete, setQuizComplete] = useState(false);
  const [results, setResults] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Generate quiz on component mount
  useEffect(() => {
    generateQuiz();
  }, []);

  // Timer effect
  useEffect(() => {
    if (timeLeft > 0) {
      const timer = setTimeout(() => setTimeLeft(timeLeft - 1), 1000);
      return () => clearTimeout(timer);
    } else if (timeLeft === 0 && currentQuiz && !quizComplete) {
      handleSubmitQuiz(); // Auto-submit when time runs out
    }
  }, [timeLeft]);

  const generateQuiz = async () => {
    try {
      setLoading(true);
      const response = await api.post('/api/quiz/generate', {
        student_id: studentId,
        grade_level: gradeLevel,
        topic: 'math', // Default to math - can be made dynamic
        difficulty: 'adaptive',
        num_questions: 5
      });
      
      setCurrentQuiz(response.data);
      setTimeLeft(response.data.time_limit_minutes * 60); // Convert to seconds
      setError(null);
    } catch (err) {
      console.error('Error generating quiz:', err);
      setError('Failed to generate quiz. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleAnswerSelect = (questionId: string, answerIndex: number) => {
    setAnswers(prev => ({ ...prev, [questionId]: answerIndex }));
  };

  const handleNextQuestion = () => {
    if (currentQuiz && currentQuestionIndex < currentQuiz.questions.length - 1) {
      setCurrentQuestionIndex(currentQuestionIndex + 1);
    }
  };

  const handlePreviousQuestion = () => {
    if (currentQuestionIndex > 0) {
      setCurrentQuestionIndex(currentQuestionIndex - 1);
    }
  };

  const handleSubmitQuiz = async () => {
    if (!currentQuiz) return;
    
    try {
      setIsSubmitting(true);
      
      // Convert answers to required format
      const responses = currentQuiz.questions.map(q => ({
        question_id: q.id,
        selected_answer: answers[q.id] || 0,
        is_correct: false, // Will be determined by backend
        time_taken_seconds: 60 // Estimated - could track actual time per question
      }));

      const response = await api.post('/api/quiz/submit', {
        student_id: studentId,
        grade_level: gradeLevel,
        quiz_id: currentQuiz.quiz_id,
        topic: currentQuiz.topic,
        difficulty: currentQuiz.difficulty,
        responses
      });
      
      setResults(response.data);
      setQuizComplete(true);
    } catch (err) {
      console.error('Error submitting quiz:', err);
      setError('Failed to submit quiz. Please try again.');
    } finally {
      setIsSubmitting(false);
    }
  };

  const formatTime = (seconds: number) => {
    const minutes = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${minutes}:${secs.toString().padStart(2, '0')}`;
  };

  if (loading) {
    return (
      <div className="academic-terminal min-h-screen flex items-center justify-center">
        <div className="text-center">
          <LoadingSpinner size="lg" />
          <p className="mt-4 academic-section-prefix">Generating Adaptive Quiz...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="academic-terminal min-h-screen flex items-center justify-center">
        <div className="text-center p-8">
          <h2 className="academic-section-title mb-4">Quiz Error</h2>
          <p className="text-gray-600 mb-6">{error}</p>
          <button
            onClick={generateQuiz}
            className="academic-btn-primary"
          >
            Try Again
          </button>
        </div>
      </div>
    );
  }

  if (quizComplete && results) {
    return (
      <div className="academic-terminal min-h-screen p-6">
        <div className="container mx-auto max-w-4xl">
          <div className="text-center mb-8">
            <div className="academic-section-prefix">Quiz Complete</div>
            <h1 className="academic-section-title mt-2">Results & Adaptation</h1>
          </div>

          <div className="grid md:grid-cols-2 gap-8">
            {/* Results Summary */}
            <div className="academic-card">
              <h3 className="text-xl font-bold uppercase mb-4">Your Score</h3>
              <div className="text-center mb-6">
                <div className="text-4xl font-bold text-gray-800 mb-2">
                  {results.quiz_results.score_percentage.toFixed(1)}%
                </div>
                <div className="text-gray-600">
                  {results.quiz_results.correct_answers} / {results.quiz_results.total_questions} correct
                </div>
              </div>
              
              <div className="space-y-3">
                <div className="flex justify-between">
                  <span className="font-mono text-sm">Time Taken:</span>
                  <span className="font-mono text-sm">{Math.floor(results.quiz_results.total_time_seconds / 60)}m {results.quiz_results.total_time_seconds % 60}s</span>
                </div>
                <div className="flex justify-between">
                  <span className="font-mono text-sm">New Accuracy:</span>
                  <span className="font-mono text-sm">{(results.profile_updates.new_accuracy * 100).toFixed(1)}%</span>
                </div>
                <div className="flex justify-between">
                  <span className="font-mono text-sm">Total Quizzes:</span>
                  <span className="font-mono text-sm">{results.profile_updates.total_quizzes}</span>
                </div>
              </div>
            </div>

            {/* AI Adaptation */}
            <div className="academic-card bg-gray-900 text-green-400 font-mono text-sm">
              <div className="mb-4">
                <span className="text-gray-500">// student_adaptation.json</span>
              </div>
              <div className="space-y-1">
                <div>{"{"}</div>
                <div className="ml-4">"difficulty_adjustment": "{results.adaptive_feedback.difficulty_adjustment}",</div>
                <div className="ml-4">"strengths": {JSON.stringify(results.profile_updates.strengths)},</div>
                <div className="ml-4">"focus_areas": {JSON.stringify(results.adaptive_feedback.focus_areas)},</div>
                <div className="ml-4">"next_difficulty": "{results.profile_updates.recommended_difficulty}",</div>
                <div className="ml-4">"next_topics": {JSON.stringify(results.adaptive_feedback.next_topics)}</div>
                <div>{"}"}</div>
              </div>
            </div>
          </div>

          {/* Question Review */}
          <div className="mt-8 academic-card">
            <h3 className="text-xl font-bold uppercase mb-6">Question Review</h3>
            <div className="space-y-4">
              {results.quiz_results.question_results.map((q: any, index: number) => (
                <div
                  key={q.question_id}
                  className={`p-4 border-l-4 ${
                    q.is_correct ? 'border-green-500 bg-green-50' : 'border-red-500 bg-red-50'
                  }`}
                >
                  <div className="flex items-start justify-between mb-2">
                    <h4 className="font-semibold">Question {index + 1}</h4>
                    <span className={`px-2 py-1 text-xs font-bold uppercase ${
                      q.is_correct ? 'bg-green-200 text-green-800' : 'bg-red-200 text-red-800'
                    }`}>
                      {q.is_correct ? 'Correct' : 'Incorrect'}
                    </span>
                  </div>
                  <p className="mb-2">{q.question}</p>
                  <div className="text-sm text-gray-600">
                    <p><strong>Your Answer:</strong> {q.student_answer}</p>
                    {!q.is_correct && <p><strong>Correct Answer:</strong> {q.correct_answer}</p>}
                    <p className="mt-2"><strong>Explanation:</strong> {q.explanation}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Action Buttons */}
          <div className="mt-8 text-center space-x-4">
            <button
              onClick={() => navigate('/tutor')}
              className="academic-btn-primary"
            >
              Continue Learning
            </button>
            <button
              onClick={generateQuiz}
              className="academic-btn-primary bg-transparent text-gray-800 border-2 border-gray-800"
            >
              Take Another Quiz
            </button>
          </div>
        </div>
      </div>
    );
  }

  if (!currentQuiz) return null;

  const currentQuestion = currentQuiz.questions[currentQuestionIndex];
  const progress = ((currentQuestionIndex + 1) / currentQuiz.questions.length) * 100;

  return (
    <div className="academic-terminal min-h-screen p-6">
      <div className="container mx-auto max-w-4xl">
        {/* Quiz Header */}
        <div className="flex justify-between items-center mb-8">
          <div>
            <div className="academic-section-prefix">Grade {gradeLevel} - {currentQuiz.topic.toUpperCase()}</div>
            <h1 className="academic-section-title mt-1">{currentQuiz.title}</h1>
          </div>
          <div className="text-right">
            <div className="academic-section-prefix">Time Remaining</div>
            <div className={`text-2xl font-mono font-bold mt-1 ${
              timeLeft < 60 ? 'text-red-600' : 'text-gray-800'
            }`}>
              {formatTime(timeLeft)}
            </div>
          </div>
        </div>

        {/* Progress Bar */}
        <div className="mb-8">
          <div className="flex justify-between text-sm mb-2">
            <span className="academic-section-prefix">
              Question {currentQuestionIndex + 1} of {currentQuiz.questions.length}
            </span>
            <span className="academic-section-prefix">
              {Math.round(progress)}% Complete
            </span>
          </div>
          <div className="w-full bg-gray-300 h-2">
            <div 
              className="academic-hero-gradient h-2 transition-all duration-300"
              style={{ width: `${progress}%` }}
            />
          </div>
        </div>

        {/* Question Card */}
        <div className="academic-card mb-8">
          <div className="mb-6">
            <div className="academic-section-prefix mb-2">
              {currentQuestion.topic} - {currentQuestion.difficulty}
            </div>
            <h2 className="text-2xl font-semibold mb-6">
              {currentQuestion.question}
            </h2>
          </div>

          <div className="grid gap-3">
            {currentQuestion.options.map((option, index) => (
              <button
                key={index}
                onClick={() => handleAnswerSelect(currentQuestion.id, index)}
                className={`text-left p-4 border-2 transition-all ${
                  answers[currentQuestion.id] === index
                    ? 'border-gray-800 bg-gray-100'
                    : 'border-gray-300 hover:border-gray-500'
                }`}
              >
                <div className="flex items-center space-x-3">
                  <div className={`w-4 h-4 border-2 ${
                    answers[currentQuestion.id] === index
                      ? 'bg-gray-800 border-gray-800'
                      : 'border-gray-300'
                  }`}>
                    {answers[currentQuestion.id] === index && (
                      <div className="w-full h-full bg-white transform scale-50"></div>
                    )}
                  </div>
                  <span>{option}</span>
                </div>
              </button>
            ))}
          </div>
        </div>

        {/* Navigation */}
        <div className="flex justify-between items-center">
          <button
            onClick={handlePreviousQuestion}
            disabled={currentQuestionIndex === 0}
            className="academic-btn-primary bg-transparent text-gray-800 border-2 border-gray-800 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Previous
          </button>

          <div className="text-center">
            <div className="academic-section-prefix">
              Personalized for your learning level
            </div>
            <div className="font-mono text-sm mt-1">
              Targeting: {currentQuiz.personalization_notes.student_weaknesses_targeted.join(', ') || 'General knowledge'}
            </div>
          </div>

          {currentQuestionIndex === currentQuiz.questions.length - 1 ? (
            <button
              onClick={handleSubmitQuiz}
              disabled={isSubmitting || Object.keys(answers).length !== currentQuiz.questions.length}
              className="academic-btn-primary disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isSubmitting ? (
                <>
                  <LoadingSpinner size="sm" />
                  <span className="ml-2">Submitting...</span>
                </>
              ) : (
                'Submit Quiz'
              )}
            </button>
          ) : (
            <button
              onClick={handleNextQuestion}
              disabled={answers[currentQuestion.id] === undefined}
              className="academic-btn-primary disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Next
            </button>
          )}
        </div>

        {/* Personalization Info */}
        <div className="mt-8 text-center">
          <div className="academic-section-prefix mb-2">AI Adaptation Active</div>
          <p className="text-sm text-gray-600">
            This quiz adapts to your Grade {gradeLevel} level and targets your learning needs. 
            Your performance will help personalize future content.
          </p>
        </div>
      </div>
    </div>
  );
};

export default QuizPage;
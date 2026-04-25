import React, { useState } from 'react';
import { Code, ExternalLink, Copy, Check, Play, Settings } from 'lucide-react';
import { toast } from 'react-hot-toast';

import LoadingSpinner from '@/components/ui/LoadingSpinner';
import { apiClient, handleAPIError } from '@/utils/api';
import { 
  ExplanationResponse, 
  GradeLevel, 
  LanguageCode,
  QuestionRequest 
} from '@/types';

const SDKDemoPage: React.FC = () => {
  // State
  const [question, setQuestion] = useState('How do fractions work?');
  const [gradeLevel, setGradeLevel] = useState<GradeLevel>('4');
  const [language, setLanguage] = useState<LanguageCode>('en');
  const [studentId, setStudentId] = useState('sdk-demo-student');
  const [response, setResponse] = useState<ExplanationResponse | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [apiCalls, setApiCalls] = useState<any[]>([]);
  const [copiedIndex, setCopiedIndex] = useState<number | null>(null);

  // Handle API call
  const handleApiCall = async () => {
    if (!question.trim()) {
      toast.error('Please enter a question');
      return;
    }

    setIsLoading(true);
    setResponse(null);

    const request: QuestionRequest = {
      question: question.trim(),
      student_id: studentId,
      grade_level: gradeLevel,
      language: language,
    };

    const callStart = Date.now();

    try {
      const result = await apiClient.explain(request);
      const callEnd = Date.now();

      setResponse(result);

      // Log API call
      const apiCall = {
        id: Date.now().toString(),
        timestamp: new Date().toISOString(),
        method: 'POST',
        url: '/api/explain',
        request,
        response: result,
        duration: callEnd - callStart,
        status: 200,
      };

      setApiCalls(prev => [apiCall, ...prev]);
      toast.success('API call successful!');

    } catch (error) {
      const callEnd = Date.now();
      
      // Log failed API call
      const apiCall = {
        id: Date.now().toString(),
        timestamp: new Date().toISOString(),
        method: 'POST',
        url: '/api/explain',
        request,
        response: { error: error },
        duration: callEnd - callStart,
        status: 500,
      };

      setApiCalls(prev => [apiCall, ...prev]);
      
      console.error('SDK Demo API error:', error);
      toast.error(handleAPIError(error));
    } finally {
      setIsLoading(false);
    }
  };

  // Copy to clipboard
  const copyToClipboard = async (text: string, index: number) => {
    try {
      await navigator.clipboard.writeText(text);
      setCopiedIndex(index);
      toast.success('Copied to clipboard');
      setTimeout(() => setCopiedIndex(null), 2000);
    } catch (error) {
      toast.error('Failed to copy to clipboard');
    }
  };

  // Sample code snippets
  const codeExamples = {
    javascript: `// JavaScript/TypeScript Example
import axios from 'axios';

const snapLearnAPI = {
  baseURL: 'http://localhost:8000',
  
  async explain(question, studentId = 'demo-student', gradeLevel = '4') {
    const response = await axios.post(\`\${this.baseURL}/api/explain\`, {
      question,
      student_id: studentId,
      grade_level: gradeLevel,
      language: 'en'
    });
    return response.data;
  }
};

// Usage
const explanation = await snapLearnAPI.explain('${question}');
console.log(explanation.explanation_text);`,

    python: `# Python Example
import requests

class SnapLearnAPI:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
    
    def explain(self, question, student_id="demo-student", grade_level="4"):
        response = requests.post(f"{self.base_url}/api/explain", json={
            "question": question,
            "student_id": student_id,
            "grade_level": grade_level,
            "language": "en"
        })
        return response.json()

# Usage
api = SnapLearnAPI()
explanation = api.explain('${question}')
print(explanation['explanation_text'])`,

    curl: `# cURL Example
curl -X POST http://localhost:8000/api/explain \\
  -H "Content-Type: application/json" \\
  -d '{
    "question": "${question}",
    "student_id": "${studentId}",
    "grade_level": "${gradeLevel}",
    "language": "${language}"
  }'`
  };

  return (
    <div className="max-w-7xl mx-auto space-y-8">
      {/* Header */}
      <div className="text-center">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">
          SnapLearn AI SDK Demo
        </h1>
        <p className="text-gray-600 max-w-3xl mx-auto">
          This page demonstrates how to integrate SnapLearn AI into your own applications using the REST API. 
          Make live API calls and see the JSON responses in real-time.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Left Column - API Testing */}
        <div className="space-y-6">
          {/* API Configuration */}
          <div className="card">
            <div className="flex items-center space-x-2 mb-4">
              <Settings className="w-5 h-5 text-primary-600" />
              <h2 className="text-lg font-semibold text-gray-900">API Configuration</h2>
            </div>

            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Question
                </label>
                <textarea
                  value={question}
                  onChange={(e) => setQuestion(e.target.value)}
                  className="input-primary min-h-[80px] resize-none"
                  placeholder="Enter your question here..."
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Grade Level
                  </label>
                  <select
                    value={gradeLevel}
                    onChange={(e) => setGradeLevel(e.target.value as GradeLevel)}
                    className="input-primary"
                  >
                    {['K', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12'].map(grade => (
                      <option key={grade} value={grade}>
                        {grade === 'K' ? 'Kindergarten' : `Grade ${grade}`}
                      </option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Language
                  </label>
                  <select
                    value={language}
                    onChange={(e) => setLanguage(e.target.value as LanguageCode)}
                    className="input-primary"
                  >
                    <option value="en">English</option>
                    <option value="hi">Hindi</option>
                    <option value="es">Spanish</option>
                    <option value="fr">French</option>
                  </select>
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Student ID
                </label>
                <input
                  type="text"
                  value={studentId}
                  onChange={(e) => setStudentId(e.target.value)}
                  className="input-primary"
                  placeholder="sdk-demo-student"
                />
              </div>

              <button
                onClick={handleApiCall}
                disabled={isLoading || !question.trim()}
                className="btn-primary w-full flex items-center justify-center space-x-2"
              >
                {isLoading ? (
                  <>
                    <LoadingSpinner size="sm" />
                    <span>Calling API...</span>
                  </>
                ) : (
                  <>
                    <Play className="w-4 h-4" />
                    <span>Make API Call</span>
                  </>
                )}
              </button>
            </div>
          </div>

          {/* Code Examples */}
          <div className="card">
            <div className="flex items-center space-x-2 mb-4">
              <Code className="w-5 h-5 text-primary-600" />
              <h2 className="text-lg font-semibold text-gray-900">Code Examples</h2>
            </div>

            <div className="space-y-4">
              {Object.entries(codeExamples).map(([language, code], index) => (
                <div key={language}>
                  <div className="flex items-center justify-between mb-2">
                    <h3 className="text-sm font-medium text-gray-700 capitalize">
                      {language === 'javascript' ? 'JavaScript/TypeScript' : language}
                    </h3>
                    <button
                      onClick={() => copyToClipboard(code, index)}
                      className="text-xs text-gray-500 hover:text-gray-700 flex items-center space-x-1"
                    >
                      {copiedIndex === index ? (
                        <Check className="w-3 h-3" />
                      ) : (
                        <Copy className="w-3 h-3" />
                      )}
                      <span>{copiedIndex === index ? 'Copied!' : 'Copy'}</span>
                    </button>
                  </div>
                  <pre className="text-xs bg-gray-900 text-gray-100 p-3 rounded-lg overflow-auto max-h-48">
                    {code}
                  </pre>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Right Column - API Response */}
        <div className="space-y-6">
          {/* API Response */}
          <div className="card">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-semibold text-gray-900">API Response</h2>
              {response && (
                <span className="text-xs bg-green-100 text-green-800 px-2 py-1 rounded">
                  Success
                </span>
              )}
            </div>

            {isLoading ? (
              <div className="text-center py-8">
                <LoadingSpinner size="lg" />
                <p className="mt-4 text-gray-600">Processing API request...</p>
              </div>
            ) : response ? (
              <div className="space-y-4">
                {/* Key information */}
                <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                  <h4 className="font-medium text-blue-900 mb-2">Explanation</h4>
                  <p className="text-blue-800 text-sm">{response.explanation_text}</p>
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div className="bg-gray-50 p-3 rounded-lg">
                    <div className="text-xs text-gray-600">Difficulty</div>
                    <div className="font-medium">{response.difficulty_level}</div>
                  </div>
                  <div className="bg-gray-50 p-3 rounded-lg">
                    <div className="text-xs text-gray-600">Confidence</div>
                    <div className="font-medium">{Math.round(response.confidence_score * 100)}%</div>
                  </div>
                </div>

                {/* Raw JSON Response */}
                <details>
                  <summary className="cursor-pointer text-sm font-medium text-gray-700 mb-2">
                    View Full JSON Response
                  </summary>
                  <pre className="text-xs bg-gray-900 text-gray-100 p-3 rounded-lg overflow-auto max-h-64">
                    {JSON.stringify(response, null, 2)}
                  </pre>
                </details>
              </div>
            ) : (
              <div className="text-center py-8 text-gray-500">
                <Code className="w-12 h-12 mx-auto mb-4 text-gray-300" />
                <p>Make an API call to see the response</p>
              </div>
            )}
          </div>

          {/* API Call Log */}
          <div className="card">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">API Call Log</h2>
            
            {apiCalls.length > 0 ? (
              <div className="space-y-3 max-h-96 overflow-y-auto">
                {apiCalls.map((call, index) => (
                  <div key={call.id} className="border border-gray-200 rounded-lg p-3">
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-sm font-medium">
                        {call.method} {call.url}
                      </span>
                      <div className="flex items-center space-x-2 text-xs">
                        <span className={`px-2 py-1 rounded ${
                          call.status === 200 
                            ? 'bg-green-100 text-green-800' 
                            : 'bg-red-100 text-red-800'
                        }`}>
                          {call.status}
                        </span>
                        <span className="text-gray-500">{call.duration}ms</span>
                      </div>
                    </div>
                    
                    <div className="text-xs text-gray-600">
                      {new Date(call.timestamp).toLocaleString()}
                    </div>

                    <details className="mt-2">
                      <summary className="cursor-pointer text-xs text-gray-500">
                        View Details
                      </summary>
                      <div className="mt-2 space-y-2">
                        <div>
                          <div className="text-xs font-medium text-gray-700">Request:</div>
                          <pre className="text-xs bg-gray-100 p-2 rounded max-h-24 overflow-auto">
                            {JSON.stringify(call.request, null, 2)}
                          </pre>
                        </div>
                        <div>
                          <div className="text-xs font-medium text-gray-700">Response:</div>
                          <pre className="text-xs bg-gray-100 p-2 rounded max-h-24 overflow-auto">
                            {JSON.stringify(call.response, null, 2)}
                          </pre>
                        </div>
                      </div>
                    </details>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center py-8 text-gray-500">
                <p>No API calls yet</p>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Documentation Links */}
      <div className="card bg-gray-50">
        <div className="flex items-center space-x-2 mb-4">
          <ExternalLink className="w-5 h-5 text-primary-600" />
          <h2 className="text-lg font-semibold text-gray-900">API Documentation</h2>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <a
            href="/docs"
            target="_blank"
            rel="noopener noreferrer"
            className="block p-4 bg-white rounded-lg hover:shadow-md transition-shadow"
          >
            <h3 className="font-medium text-gray-900 mb-1">Interactive API Docs</h3>
            <p className="text-sm text-gray-600">Explore all endpoints with Swagger UI</p>
          </a>
          
          <a
            href="/redoc"
            target="_blank"
            rel="noopener noreferrer"
            className="block p-4 bg-white rounded-lg hover:shadow-md transition-shadow"
          >
            <h3 className="font-medium text-gray-900 mb-1">ReDoc Documentation</h3>
            <p className="text-sm text-gray-600">Beautiful API reference documentation</p>
          </a>
          
          <div className="block p-4 bg-white rounded-lg">
            <h3 className="font-medium text-gray-900 mb-1">Base URL</h3>
            <p className="text-sm text-gray-600 font-mono">http://localhost:8000</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default SDKDemoPage;
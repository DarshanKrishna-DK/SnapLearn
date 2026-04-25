import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { Toaster } from 'react-hot-toast';

// Components
import Navbar from './components/Navbar';
import TutorPage from './pages/TutorPage';
import VideoPage from './pages/VideoPage';
import ProfilePage from './pages/ProfilePage';
import SDKDemoPage from './pages/SDKDemoPage';
import LoadingSpinner from './components/ui/LoadingSpinner';
import ErrorBoundary from './components/ErrorBoundary';

// Hooks and utilities
import { useLocalStorage } from './hooks/useLocalStorage';
import { api } from './utils/api';

// Types
import { GradeLevel, LanguageCode } from './types';

interface AppState {
  currentStudent: string;
  gradeLevel: GradeLevel;
  language: LanguageCode;
  isServerConnected: boolean;
  isCheckingConnection: boolean;
}

function App() {
  // App state
  const [appState, setAppState] = useState<AppState>({
    currentStudent: 'demo-student',
    gradeLevel: '4',
    language: 'en',
    isServerConnected: false,
    isCheckingConnection: true,
  });

  // Persistent settings
  const [savedSettings, setSavedSettings] = useLocalStorage('snaplearn-settings', {
    studentId: 'demo-student',
    gradeLevel: '4' as GradeLevel,
    language: 'en' as LanguageCode,
    darkMode: false,
  });

  // Check server connection on startup
  useEffect(() => {
    const checkConnection = async () => {
      try {
        setAppState(prev => ({ ...prev, isCheckingConnection: true }));
        
        const isConnected = await api.healthCheck(5000);
        
        setAppState(prev => ({
          ...prev,
          isServerConnected: isConnected,
          isCheckingConnection: false,
        }));

        if (!isConnected) {
          console.warn('Backend server not available');
        }
      } catch (error) {
        console.error('Connection check failed:', error);
        setAppState(prev => ({
          ...prev,
          isServerConnected: false,
          isCheckingConnection: false,
        }));
      }
    };

    checkConnection();
  }, []);

  // Initialize app state from saved settings
  useEffect(() => {
    setAppState(prev => ({
      ...prev,
      currentStudent: savedSettings.studentId,
      gradeLevel: savedSettings.gradeLevel,
      language: savedSettings.language,
    }));
  }, [savedSettings]);

  // Update student settings
  const updateSettings = (updates: Partial<typeof savedSettings>) => {
    const newSettings = { ...savedSettings, ...updates };
    setSavedSettings(newSettings);
    
    setAppState(prev => ({
      ...prev,
      currentStudent: newSettings.studentId,
      gradeLevel: newSettings.gradeLevel,
      language: newSettings.language,
    }));
  };

  // Retry connection
  const retryConnection = async () => {
    setAppState(prev => ({ ...prev, isCheckingConnection: true }));
    
    try {
      const isConnected = await api.healthCheck(10000);
      
      setAppState(prev => ({
        ...prev,
        isServerConnected: isConnected,
        isCheckingConnection: false,
      }));
    } catch (error) {
      setAppState(prev => ({
        ...prev,
        isServerConnected: false,
        isCheckingConnection: false,
      }));
    }
  };

  // Loading screen during connection check
  if (appState.isCheckingConnection) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <LoadingSpinner size="lg" />
          <p className="mt-4 text-gray-600">Connecting to SnapLearn AI...</p>
        </div>
      </div>
    );
  }

  // Connection error screen
  if (!appState.isServerConnected) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="max-w-md mx-auto text-center p-8">
          <div className="mb-6">
            <div className="w-16 h-16 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <svg className="w-8 h-8 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z" />
              </svg>
            </div>
            <h2 className="text-2xl font-bold text-gray-900 mb-2">
              Backend Server Not Available
            </h2>
            <p className="text-gray-600 mb-6">
              The SnapLearn AI backend server is not responding. Please make sure the FastAPI server is running on localhost:8000.
            </p>
            <div className="bg-gray-100 rounded-lg p-4 text-left text-sm font-mono mb-6">
              <p className="text-gray-800">To start the backend server:</p>
              <p className="text-blue-600 mt-2">cd backend</p>
              <p className="text-blue-600">python main.py</p>
            </div>
            <button
              onClick={retryConnection}
              disabled={appState.isCheckingConnection}
              className="btn-primary"
            >
              {appState.isCheckingConnection ? (
                <>
                  <LoadingSpinner size="sm" />
                  <span className="ml-2">Connecting...</span>
                </>
              ) : (
                'Try Again'
              )}
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <ErrorBoundary>
      <Router>
        <div className="min-h-screen bg-gray-50">
          <Navbar 
            currentStudent={appState.currentStudent}
            gradeLevel={appState.gradeLevel}
            language={appState.language}
            onSettingsChange={updateSettings}
          />
          
          <main className="container mx-auto px-4 py-8">
            <Routes>
              {/* Main tutoring interface */}
              <Route 
                path="/" 
                element={
                  <TutorPage 
                    studentId={appState.currentStudent}
                    gradeLevel={appState.gradeLevel}
                    language={appState.language}
                  />
                } 
              />
              
              {/* Video generation page */}
              <Route 
                path="/videos" 
                element={
                  <VideoPage 
                    studentId={appState.currentStudent}
                    gradeLevel={appState.gradeLevel}
                    language={appState.language}
                  />
                } 
              />
              
              {/* Student profile page */}
              <Route 
                path="/profile" 
                element={
                  <ProfilePage 
                    studentId={appState.currentStudent}
                    onStudentIdChange={(newId) => updateSettings({ studentId: newId })}
                  />
                } 
              />
              
              {/* SDK Demo page */}
              <Route 
                path="/sdk-demo" 
                element={<SDKDemoPage />} 
              />
              
              {/* Redirect unknown paths to home */}
              <Route path="*" element={<Navigate to="/" replace />} />
            </Routes>
          </main>
          
          {/* Toast notifications */}
          <Toaster 
            position="top-right"
            toastOptions={{
              duration: 4000,
              style: {
                background: '#363636',
                color: '#fff',
              },
              success: {
                style: {
                  background: '#22c55e',
                },
              },
              error: {
                style: {
                  background: '#ef4444',
                },
              },
            }}
          />
        </div>
      </Router>
    </ErrorBoundary>
  );
}

export default App;
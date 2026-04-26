import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate, useLocation } from 'react-router-dom';
import { Toaster } from 'react-hot-toast';

// Components
import Navbar from './components/Navbar';
import MarketingHome from './pages/MarketingHome.jsx';
import AppPage from './pages/AppPage';
import Documentation from './pages/Documentation';
import SDKPage from './pages/SDKPage';
import TutorPage from './pages/TutorPage';
import VideoPage from './pages/VideoPage';
import QuizPage from './pages/QuizPage';
import ProfilePage from './pages/ProfilePage';
import SDKDemoPage from './pages/SDKDemoPage';
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

interface AppContentProps {
  appState: AppState;
  updateSettings: (updates: Partial<{
    studentId: string;
    gradeLevel: GradeLevel;
    language: LanguageCode;
    darkMode: boolean;
  }>) => void;
  retryConnection: () => void;
}

const AppContent: React.FC<AppContentProps> = ({ appState, updateSettings, retryConnection }) => {
  const location = useLocation();
  const isFullBleed = ['/', '/docs', '/sdk', '/app'].includes(location.pathname);

  return (
    <div className={isFullBleed ? "min-h-screen" : "min-h-screen bg-[var(--sl-cream)]"}>
      {appState.isCheckingConnection && (
        <div
          className="pointer-events-none fixed top-0 left-0 right-0 z-[300] h-0.5 bg-[#3d0a18]"
          aria-hidden
        >
          <div className="h-full w-2/5 animate-pulse bg-[#c49a5c]/90" />
        </div>
      )}
      {!appState.isServerConnected && !appState.isCheckingConnection && (
        <div className="sticky top-0 z-[250] border-b border-amber-200 bg-amber-100 px-4 py-2 text-center text-sm text-amber-950">
          <span className="font-medium">API offline. </span>
          Navigation still works. Start the backend (port 8000) and use Vite so /api proxies to it.{' '}
          <button
            type="button"
            onClick={retryConnection}
            className="ml-2 font-semibold text-amber-900 underline decoration-amber-800 hover:text-amber-950"
          >
            Retry
          </button>
        </div>
      )}
      {!isFullBleed && (
        <Navbar 
          currentStudent={appState.currentStudent}
          gradeLevel={appState.gradeLevel}
          language={appState.language}
          onSettingsChange={updateSettings}
        />
      )}
      
      <main className={isFullBleed ? "" : "container mx-auto px-4 py-8"}>
          <Routes>
            {/* Landing page - Product intro */}
            <Route 
              path="/" 
              element={<MarketingHome />} 
            />
            
            {/* Documentation page */}
            <Route 
              path="/docs" 
              element={<Documentation />} 
            />
            
            {/* SDK page */}
            <Route 
              path="/sdk" 
              element={<SDKPage />} 
            />
            
            {/* Main SnapLearn App - Try SnapLearn functionality */}
            <Route 
              path="/app" 
              element={
                <AppPage 
                  studentId={appState.currentStudent}
                  gradeLevel={appState.gradeLevel}
                  language={appState.language}
                />
              } 
            />
            
            {/* Individual feature pages */}
            <Route 
              path="/tutor" 
              element={
                <TutorPage 
                  studentId={appState.currentStudent}
                  gradeLevel={appState.gradeLevel}
                  language={appState.language}
                />
              } 
            />
            
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
            
            <Route 
              path="/quiz" 
              element={
                <QuizPage 
                  studentId={appState.currentStudent}
                  gradeLevel={appState.gradeLevel}
                />
              } 
            />

            <Route
              path="/test"
              element={
                <QuizPage
                  studentId={appState.currentStudent}
                  gradeLevel={appState.gradeLevel}
                />
              }
            />
            
            <Route 
              path="/profile" 
              element={
                <ProfilePage 
                  studentId={appState.currentStudent}
                  onStudentIdChange={(newId) => updateSettings({ studentId: newId })}
                />
              } 
            />
            
            {/* Legacy SDK Demo page */}
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
  );
};

function App() {
  // App state
  const [appState, setAppState] = useState<AppState>({
    currentStudent: 'demo-student',
    gradeLevel: '4',
    language: 'en',
    isServerConnected: true,
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
        
        const isConnected = await api.healthCheck();
        
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

  // Initialize app state from saved settings and check for grade or language from landing page
  useEffect(() => {
    const selectedGrade = localStorage.getItem('selectedGrade');
    const selectedLanguage = localStorage.getItem('selectedLanguage');

    const gradeFromLanding =
      selectedGrade && ['K', '1', '2', '3', '4', '5', '6', '7', '8'].includes(selectedGrade)
        ? (selectedGrade as GradeLevel)
        : null;
    const langFromLanding =
      selectedLanguage === 'en' || selectedLanguage === 'kn'
        ? (selectedLanguage as LanguageCode)
        : null;

    setAppState(prev => {
      const nextGradeLevel = gradeFromLanding ?? savedSettings.gradeLevel;
      const nextLanguage = langFromLanding ?? savedSettings.language;
      const nextStudent = savedSettings.studentId;

      if (
        prev.currentStudent === nextStudent &&
        prev.gradeLevel === nextGradeLevel &&
        prev.language === nextLanguage
      ) {
        return prev;
      }

      return {
        ...prev,
        currentStudent: nextStudent,
        gradeLevel: nextGradeLevel,
        language: nextLanguage,
      };
    });

    if (gradeFromLanding) {
      if (gradeFromLanding !== savedSettings.gradeLevel) {
        setSavedSettings(prev => ({ ...prev, gradeLevel: gradeFromLanding }));
      }
      localStorage.removeItem('selectedGrade');
    }

    if (langFromLanding) {
      if (langFromLanding !== savedSettings.language) {
        setSavedSettings(prev => ({ ...prev, language: langFromLanding }));
      }
      localStorage.removeItem('selectedLanguage');
    }
  }, [savedSettings, setSavedSettings]);

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
      const isConnected = await api.healthCheck();
      
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

  return (
    <ErrorBoundary>
      <Router>
        <AppContent 
          appState={appState} 
          updateSettings={updateSettings} 
          retryConnection={retryConnection} 
        />
      </Router>
    </ErrorBoundary>
  );
}

export default App;
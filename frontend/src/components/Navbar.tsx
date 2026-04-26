import React, { useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { 
  BookOpen, 
  Video, 
  User, 
  Code, 
  Settings,
  Menu,
  X,
  Globe,
  GraduationCap,
  Brain,
  FileText,
  LayoutDashboard,
} from 'lucide-react';

import { GradeLevel, LanguageCode } from '@/types';

interface NavbarProps {
  currentStudent: string;
  gradeLevel: GradeLevel;
  language: LanguageCode;
  onSettingsChange: (updates: {
    studentId?: string;
    gradeLevel?: GradeLevel;
    language?: LanguageCode;
  }) => void;
}

const Navbar: React.FC<NavbarProps> = ({
  currentStudent,
  gradeLevel,
  language,
  onSettingsChange,
}) => {
  const location = useLocation();
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const [isSettingsOpen, setIsSettingsOpen] = useState(false);

  const navigationItems = [
    {
      path: '/app',
      label: 'App hub',
      icon: LayoutDashboard,
      description: 'Links to tutor, video, and quiz'
    },
    {
      path: '/tutor',
      label: 'AI Tutor',
      icon: BookOpen,
      description: 'Blackboard and explanations'
    },
    {
      path: '/videos',
      label: 'Manim video',
      icon: Video,
      description: 'Generate and view lesson video'
    },
    {
      path: '/quiz',
      label: 'Quiz',
      icon: Brain,
      description: 'Adaptive quiz flow'
    },
    {
      path: '/docs',
      label: 'Docs',
      icon: FileText,
      description: 'Documentation'
    },
    {
      path: '/sdk',
      label: 'SDK',
      icon: Code,
      description: 'API reference and ping'
    },
    {
      path: '/profile',
      label: 'Profile',
      icon: User,
      description: 'Student profile'
    },
  ];

  const gradeOptions: GradeLevel[] = [
    'K', '1', '2', '3', '4', '5', '6', '7', '8',
  ];

  const languageOptions: { code: LanguageCode; name: string }[] = [
    { code: 'en', name: 'English' },
    { code: 'kn', name: 'Kannada (ಕನ್ನಡ)' },
    { code: 'hi', name: 'हिंदी' },
    { code: 'es', name: 'Español' },
    { code: 'fr', name: 'Français' },
    { code: 'de', name: 'Deutsch' },
    { code: 'zh', name: '中文' },
    { code: 'ja', name: '日本語' },
  ];

  const handleStudentIdChange = (newId: string) => {
    onSettingsChange({ studentId: newId });
  };

  const handleGradeLevelChange = (newGrade: GradeLevel) => {
    onSettingsChange({ gradeLevel: newGrade });
  };

  const handleLanguageChange = (newLanguage: LanguageCode) => {
    onSettingsChange({ language: newLanguage });
  };

  const isActivePath = (path: string) => {
    if (path === '/quiz' && (location.pathname === '/quiz' || location.pathname === '/test')) {
      return true;
    }
    return location.pathname === path;
  };

  return (
    <>
      <nav className="border-b border-[#debfc2] bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            {/* Logo and brand */}
            <div className="flex items-center">
              <Link to="/" className="flex items-center space-x-2" title="Home">
                <div className="flex h-8 w-8 items-center justify-center rounded-md bg-[#8b1538]">
                  <BookOpen className="w-5 h-5 text-white" />
                </div>
                <span className="text-lg font-semibold text-[#1e1b14]">
                  SnapLearn
                </span>
              </Link>
            </div>

            {/* Desktop navigation */}
            <div className="hidden md:flex items-center space-x-8">
              {navigationItems.map((item) => {
                const Icon = item.icon;
                const isActive = isActivePath(item.path);
                
                return (
                  <Link
                    key={item.path}
                    to={item.path}
                    className={`flex items-center space-x-2 px-2 py-2 rounded-md text-sm font-medium transition-colors ${
                      isActive
                        ? 'bg-[#f5ebe0] text-[#8b1538]'
                        : 'text-[#3d3834] hover:bg-[#f5ebe0] hover:text-[#1e1b14]'
                    }`}
                    title={item.description}
                  >
                    <Icon className="w-4 h-4" />
                    <span>{item.label}</span>
                  </Link>
                );
              })}
            </div>

            {/* Settings and mobile menu */}
            <div className="flex items-center space-x-4">
              {/* Settings button */}
              <button
                onClick={() => setIsSettingsOpen(true)}
                className="p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-50 rounded-md transition-colors"
                title="Settings"
              >
                <Settings className="w-5 h-5" />
              </button>

              {/* Mobile menu button */}
              <button
                onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
                className="md:hidden p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-50 rounded-md transition-colors"
              >
                {isMobileMenuOpen ? (
                  <X className="w-5 h-5" />
                ) : (
                  <Menu className="w-5 h-5" />
                )}
              </button>
            </div>
          </div>
        </div>

        {/* Mobile navigation menu */}
        {isMobileMenuOpen && (
          <div className="md:hidden border-t border-gray-200 bg-white">
            <div className="px-2 pt-2 pb-3 space-y-1">
              {navigationItems.map((item) => {
                const Icon = item.icon;
                const isActive = isActivePath(item.path);
                
                return (
                  <Link
                    key={item.path}
                    to={item.path}
                    onClick={() => setIsMobileMenuOpen(false)}
                    className={`flex items-center space-x-3 px-3 py-2 rounded-md text-base font-medium ${
                      isActive
                        ? 'bg-[#f5ebe0] text-[#8b1538]'
                        : 'text-[#3d3834] hover:bg-[#f5ebe0] hover:text-[#1e1b14]'
                    }`}
                  >
                    <Icon className="w-5 h-5" />
                    <div>
                      <div>{item.label}</div>
                      <div className="text-xs text-gray-500">{item.description}</div>
                    </div>
                  </Link>
                );
              })}
            </div>
          </div>
        )}
      </nav>

      {/* Settings Modal */}
      {isSettingsOpen && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg shadow-xl max-w-md w-full max-h-[80vh] overflow-y-auto">
            {/* Modal header */}
            <div className="flex items-center justify-between p-6 border-b border-gray-200">
              <h2 className="text-lg font-semibold text-gray-900">Settings</h2>
              <button
                onClick={() => setIsSettingsOpen(false)}
                className="p-2 text-gray-400 hover:text-gray-600 rounded-md"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            {/* Modal content */}
            <div className="p-6 space-y-6">
              {/* Student ID */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  <User className="w-4 h-4 inline mr-2" />
                  Student ID
                </label>
                <input
                  type="text"
                  value={currentStudent}
                  onChange={(e) => handleStudentIdChange(e.target.value)}
                  className="input-primary"
                  placeholder="Enter student ID"
                />
                <p className="text-xs text-gray-500 mt-1">
                  Used to personalize learning and track progress
                </p>
              </div>

              {/* Grade Level */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  <GraduationCap className="w-4 h-4 inline mr-2" />
                  Grade Level
                </label>
                <select
                  value={gradeLevel}
                  onChange={(e) => handleGradeLevelChange(e.target.value as GradeLevel)}
                  className="input-primary"
                >
                  {gradeOptions.map((grade) => (
                    <option key={grade} value={grade}>
                      {grade === 'K' ? 'Kindergarten' : `Grade ${grade}`}
                    </option>
                  ))}
                </select>
                <p className="text-xs text-gray-500 mt-1">
                  Adjusts content difficulty and vocabulary
                </p>
              </div>

              {/* Language */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  <Globe className="w-4 h-4 inline mr-2" />
                  Language
                </label>
                <select
                  value={language}
                  onChange={(e) => handleLanguageChange(e.target.value as LanguageCode)}
                  className="input-primary"
                >
                  {languageOptions.map((lang) => (
                    <option key={lang.code} value={lang.code}>
                      {lang.name}
                    </option>
                  ))}
                </select>
                <p className="text-xs text-gray-500 mt-1">
                  Language for explanations and content
                </p>
              </div>
            </div>

            {/* Modal footer */}
            <div className="flex justify-end p-6 border-t border-gray-200">
              <button
                onClick={() => setIsSettingsOpen(false)}
                className="btn-primary"
              >
                Done
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
};

export default Navbar;
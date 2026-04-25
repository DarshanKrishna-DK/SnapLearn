import React, { useState, useEffect } from 'react';
import { toast } from 'react-hot-toast';
import { User, BookOpen, Trophy, Clock, TrendingUp, RotateCcw } from 'lucide-react';

import LoadingSpinner from '@/components/ui/LoadingSpinner';
import { apiClient, handleAPIError } from '@/utils/api';
import { StudentProfile, LearningStats } from '@/types';

interface ProfilePageProps {
  studentId: string;
  onStudentIdChange: (newId: string) => void;
}

const ProfilePage: React.FC<ProfilePageProps> = ({
  studentId,
  onStudentIdChange
}) => {
  const [profile, setProfile] = useState<StudentProfile | null>(null);
  const [learningStats, setLearningStats] = useState<LearningStats | null>(null);
  const [recentTopics, setRecentTopics] = useState<string[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [newStudentId, setNewStudentId] = useState(studentId);

  // Load profile data
  const loadProfileData = async () => {
    setIsLoading(true);
    try {
      const response = await apiClient.getStudentProfile(studentId);
      setProfile(response.profile);
      setLearningStats(response.learning_stats);
      setRecentTopics(response.recent_topics);
    } catch (error) {
      console.error('Error loading profile:', error);
      toast.error(handleAPIError(error));
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadProfileData();
  }, [studentId]);

  // Reset student profile
  const handleReset = async () => {
    if (!confirm('Are you sure you want to reset all learning data for this student?')) {
      return;
    }

    try {
      await apiClient.resetStudent(studentId);
      toast.success('Student profile reset successfully');
      loadProfileData();
    } catch (error) {
      console.error('Error resetting profile:', error);
      toast.error(handleAPIError(error));
    }
  };

  // Change student ID
  const handleStudentIdChange = () => {
    if (newStudentId.trim() && newStudentId !== studentId) {
      onStudentIdChange(newStudentId.trim());
      toast.success(`Switched to student: ${newStudentId}`);
    }
  };

  if (isLoading) {
    return (
      <div className="max-w-4xl mx-auto">
        <div className="card text-center py-16">
          <LoadingSpinner size="lg" />
          <p className="mt-4 text-gray-600">Loading student profile...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto space-y-8">
      {/* Header */}
      <div className="text-center">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">
          Student Learning Profile
        </h1>
        <p className="text-gray-600">
          Track learning progress and personalize the AI tutoring experience
        </p>
      </div>

      {/* Student ID Management */}
      <div className="card">
        <div className="flex items-center space-x-2 mb-4">
          <User className="w-5 h-5 text-primary-600" />
          <h2 className="text-lg font-semibold text-gray-900">Student Information</h2>
        </div>

        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Student ID
            </label>
            <div className="flex space-x-2">
              <input
                type="text"
                value={newStudentId}
                onChange={(e) => setNewStudentId(e.target.value)}
                className="input-primary flex-1"
                placeholder="Enter student ID"
              />
              <button
                onClick={handleStudentIdChange}
                disabled={!newStudentId.trim() || newStudentId === studentId}
                className="btn-primary px-6"
              >
                Switch
              </button>
            </div>
          </div>

          {profile && (
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 pt-4 border-t border-gray-200">
              <div>
                <label className="block text-sm font-medium text-gray-700">Grade Level</label>
                <p className="text-lg text-gray-900">
                  {profile.grade_level === 'K' ? 'Kindergarten' : `Grade ${profile.grade_level}`}
                </p>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700">Language</label>
                <p className="text-lg text-gray-900">{profile.preferred_language}</p>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700">Learning Style</label>
                <p className="text-lg text-gray-900 capitalize">
                  {profile.learning_style.replace('_', ' ')}
                </p>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Learning Statistics */}
      {learningStats && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <div className="card text-center">
            <div className="w-12 h-12 bg-primary-100 text-primary-600 rounded-lg flex items-center justify-center mx-auto mb-3">
              <BookOpen className="w-6 h-6" />
            </div>
            <div className="text-2xl font-bold text-gray-900">
              {learningStats.total_questions}
            </div>
            <div className="text-sm text-gray-600">Questions Asked</div>
          </div>

          <div className="card text-center">
            <div className="w-12 h-12 bg-secondary-100 text-secondary-600 rounded-lg flex items-center justify-center mx-auto mb-3">
              <Trophy className="w-6 h-6" />
            </div>
            <div className="text-2xl font-bold text-gray-900">
              {Math.round(learningStats.success_rate * 100)}%
            </div>
            <div className="text-sm text-gray-600">Success Rate</div>
          </div>

          <div className="card text-center">
            <div className="w-12 h-12 bg-accent-100 text-accent-600 rounded-lg flex items-center justify-center mx-auto mb-3">
              <Clock className="w-6 h-6" />
            </div>
            <div className="text-2xl font-bold text-gray-900">
              {learningStats.total_sessions}
            </div>
            <div className="text-sm text-gray-600">Learning Sessions</div>
          </div>

          <div className="card text-center">
            <div className="w-12 h-12 bg-orange-100 text-orange-600 rounded-lg flex items-center justify-center mx-auto mb-3">
              <TrendingUp className="w-6 h-6" />
            </div>
            <div className="text-2xl font-bold text-gray-900">
              {learningStats.recent_activity}
            </div>
            <div className="text-sm text-gray-600">Recent Activity</div>
          </div>
        </div>
      )}

      {/* Recent Topics */}
      {recentTopics.length > 0 && (
        <div className="card">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">
            Recent Topics Explored
          </h3>
          <div className="space-y-2">
            {recentTopics.map((topic, index) => (
              <div
                key={index}
                className="bg-gray-50 px-4 py-2 rounded-lg text-gray-700"
              >
                {topic}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Learning Patterns */}
      {profile && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Success Patterns */}
          <div className="card">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">
              Strengths
            </h3>
            {Object.keys(profile.success_patterns).length > 0 ? (
              <div className="space-y-2">
                {Object.entries(profile.success_patterns)
                  .sort(([, a], [, b]) => b - a)
                  .slice(0, 5)
                  .map(([pattern, count]) => (
                    <div key={pattern} className="flex justify-between items-center">
                      <span className="text-gray-700 capitalize">
                        {pattern.replace(/[_-]/g, ' ')}
                      </span>
                      <span className="bg-green-100 text-green-800 px-2 py-1 rounded text-sm">
                        {count} successes
                      </span>
                    </div>
                  ))}
              </div>
            ) : (
              <p className="text-gray-500 text-center py-8">
                No learning patterns yet. Keep exploring!
              </p>
            )}
          </div>

          {/* Confusion Patterns */}
          <div className="card">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">
              Areas to Focus On
            </h3>
            {Object.keys(profile.confusion_patterns).length > 0 ? (
              <div className="space-y-2">
                {Object.entries(profile.confusion_patterns)
                  .sort(([, a], [, b]) => b - a)
                  .slice(0, 5)
                  .map(([pattern, count]) => (
                    <div key={pattern} className="flex justify-between items-center">
                      <span className="text-gray-700 capitalize">
                        {pattern.replace(/[_-]/g, ' ')}
                      </span>
                      <span className="bg-orange-100 text-orange-800 px-2 py-1 rounded text-sm">
                        {count} questions
                      </span>
                    </div>
                  ))}
              </div>
            ) : (
              <p className="text-gray-500 text-center py-8">
                No confusion patterns identified yet.
              </p>
            )}
          </div>
        </div>
      )}

      {/* Profile Actions */}
      <div className="card">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-lg font-semibold text-gray-900">Profile Management</h3>
            <p className="text-gray-600">Reset learning data to start fresh</p>
          </div>
          
          <button
            onClick={handleReset}
            className="btn-outline text-red-600 border-red-600 hover:bg-red-50 flex items-center space-x-2"
          >
            <RotateCcw className="w-4 h-4" />
            <span>Reset Profile</span>
          </button>
        </div>
      </div>
    </div>
  );
};

export default ProfilePage;
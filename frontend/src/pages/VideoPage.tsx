import React, { useState } from 'react';
import { toast } from 'react-hot-toast';
import { Video, Play, Download, Clock } from 'lucide-react';

import LoadingSpinner from '@/components/ui/LoadingSpinner';
import { apiClient, handleAPIError } from '@/utils/api';
import { VideoResponse, GradeLevel, LanguageCode } from '@/types';

interface VideoPageProps {
  studentId: string;
  gradeLevel: GradeLevel;
  language: LanguageCode;
}

const VideoPage: React.FC<VideoPageProps> = ({
  studentId,
  gradeLevel,
  language
}) => {
  const [topic, setTopic] = useState('');
  const [isGenerating, setIsGenerating] = useState(false);
  const [generatedVideo, setGeneratedVideo] = useState<VideoResponse | null>(null);
  const [generationProgress, setGenerationProgress] = useState(0);

  const handleGenerateVideo = async () => {
    if (!topic.trim()) {
      toast.error('Please enter a topic for the video');
      return;
    }

    setIsGenerating(true);
    setGeneratedVideo(null);
    setGenerationProgress(0);

    // Simulate progress
    const progressInterval = setInterval(() => {
      setGenerationProgress(prev => {
        if (prev >= 90) {
          clearInterval(progressInterval);
          return prev;
        }
        return prev + Math.random() * 10;
      });
    }, 1000);

    try {
      const response = await apiClient.generateVideo({
        topic: topic.trim(),
        student_id: studentId,
        grade_level: gradeLevel,
        language: language,
      });

      setGeneratedVideo(response);
      setGenerationProgress(100);
      toast.success('Video generated successfully!');
      
    } catch (error) {
      console.error('Error generating video:', error);
      toast.error(handleAPIError(error));
    } finally {
      setIsGenerating(false);
      clearInterval(progressInterval);
    }
  };

  const suggestedTopics = [
    'Photosynthesis explained step by step',
    'How fractions work with visual examples',
    'The water cycle and weather patterns',
    'Basic algebra with real-world problems',
    'Introduction to geometry shapes',
    'How multiplication works visually'
  ];

  return (
    <div className="max-w-4xl mx-auto space-y-8">
      {/* Header */}
      <div className="text-center">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">
          Educational Video Generator
        </h1>
        <p className="text-gray-600 max-w-2xl mx-auto">
          Generate custom educational videos using Manim animations. 
          Perfect for visual learners and complex concepts that need step-by-step explanations.
        </p>
      </div>

      {/* Video generation form */}
      <div className="card">
        <div className="flex items-center space-x-2 mb-4">
          <Video className="w-5 h-5 text-primary-600" />
          <h2 className="text-lg font-semibold text-gray-900">Generate Video</h2>
        </div>

        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Topic for video
            </label>
            <textarea
              value={topic}
              onChange={(e) => setTopic(e.target.value)}
              placeholder="Describe what you'd like the video to explain..."
              className="input-primary min-h-[100px] resize-none"
              disabled={isGenerating}
            />
            <p className="text-xs text-gray-500 mt-1">
              Be specific about what you want to learn. The AI will create a detailed animated explanation.
            </p>
          </div>

          <button
            onClick={handleGenerateVideo}
            disabled={isGenerating || !topic.trim()}
            className="btn-primary flex items-center space-x-2"
          >
            {isGenerating ? (
              <>
                <LoadingSpinner size="sm" />
                <span>Generating video...</span>
              </>
            ) : (
              <>
                <Play className="w-4 h-4" />
                <span>Generate Video</span>
              </>
            )}
          </button>
        </div>
      </div>

      {/* Generation progress */}
      {isGenerating && (
        <div className="card">
          <div className="flex items-center space-x-3 mb-4">
            <LoadingSpinner size="md" />
            <div>
              <h3 className="font-medium text-gray-900">Generating your video</h3>
              <p className="text-sm text-gray-600">This may take 1-3 minutes...</p>
            </div>
          </div>

          <div className="space-y-2">
            <div className="flex justify-between text-sm text-gray-600">
              <span>Progress</span>
              <span>{Math.round(generationProgress)}%</span>
            </div>
            <div className="bg-gray-200 rounded-full h-2 overflow-hidden">
              <div 
                className="bg-primary-600 h-full transition-all duration-1000 ease-out"
                style={{ width: `${generationProgress}%` }}
              />
            </div>
          </div>

          <div className="mt-4 text-sm text-gray-600">
            <div className="flex items-center space-x-2">
              <Clock className="w-4 h-4" />
              <span>Creating Manim animation script...</span>
            </div>
          </div>
        </div>
      )}

      {/* Generated video */}
      {generatedVideo && (
        <div className="card">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-gray-900">
              Your Video: {generatedVideo.topic}
            </h3>
            <div className="flex items-center space-x-4 text-sm text-gray-600">
              {generatedVideo.duration_seconds && (
                <span>{Math.round(generatedVideo.duration_seconds)}s</span>
              )}
              {generatedVideo.file_size_mb && (
                <span>{generatedVideo.file_size_mb} MB</span>
              )}
            </div>
          </div>

          {/* Video player */}
          <div className="video-container mb-4">
            <video
              controls
              className="w-full h-auto max-h-96 bg-black"
              poster="/api/placeholder/800/450"
            >
              <source src={apiClient.getVideoUrl(generatedVideo.video_url)} type="video/mp4" />
              Your browser does not support the video tag.
            </video>
          </div>

          {/* Video actions */}
          <div className="flex items-center justify-between">
            <div className="text-sm text-gray-600">
              Generated in {generatedVideo.generation_time_seconds?.toFixed(1)}s
            </div>
            
            <a
              href={apiClient.getVideoUrl(generatedVideo.video_url)}
              download={`${generatedVideo.topic.replace(/[^a-zA-Z0-9]/g, '_')}.mp4`}
              className="btn-outline flex items-center space-x-2"
            >
              <Download className="w-4 h-4" />
              <span>Download</span>
            </a>
          </div>

          {/* Manim script (for development) */}
          {generatedVideo.manim_script && process.env.NODE_ENV === 'development' && (
            <details className="mt-4">
              <summary className="cursor-pointer text-sm font-medium text-gray-700 mb-2">
                View Generated Manim Script
              </summary>
              <pre className="text-xs bg-gray-100 p-3 rounded overflow-auto max-h-48">
                {generatedVideo.manim_script}
              </pre>
            </details>
          )}
        </div>
      )}

      {/* Suggested topics */}
      {!isGenerating && !generatedVideo && (
        <div className="card">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">
            Suggested Topics
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {suggestedTopics.map((suggestedTopic, index) => (
              <button
                key={index}
                onClick={() => setTopic(suggestedTopic)}
                className="text-left p-3 bg-gray-50 hover:bg-gray-100 rounded-lg transition-colors text-sm"
              >
                "{suggestedTopic}"
              </button>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default VideoPage;
import React, { useState, useEffect, useRef, useCallback } from 'react';
import { Play, Pause, RotateCcw, SkipForward, SkipBack } from 'lucide-react';

import { BoardScript, BoardStep } from '@/types';

interface AnimatedBlackboardProps {
  script: BoardScript;
  isPlaying?: boolean;
  onAnimationComplete?: () => void;
  className?: string;
  autoPlay?: boolean;
}

const AnimatedBlackboard: React.FC<AnimatedBlackboardProps> = ({
  script,
  isPlaying: externalIsPlaying,
  onAnimationComplete,
  className = "",
  autoPlay = true
}) => {
  // State
  const [currentStep, setCurrentStep] = useState(0);
  const [isPlaying, setIsPlaying] = useState(autoPlay);
  const [displayedSteps, setDisplayedSteps] = useState<BoardStep[]>([]);
  const [animatingStep, setAnimatingStep] = useState<BoardStep | null>(null);
  
  // Refs
  const timeoutRef = useRef<NodeJS.Timeout | null>(null);
  const animationRef = useRef<number | null>(null);

  // Control external playing state
  useEffect(() => {
    if (externalIsPlaying !== undefined) {
      setIsPlaying(externalIsPlaying);
    }
  }, [externalIsPlaying]);

  // Animation logic
  const playNextStep = useCallback(() => {
    if (currentStep >= script.steps.length) {
      setIsPlaying(false);
      onAnimationComplete?.();
      return;
    }

    const step = script.steps[currentStep];
    setAnimatingStep(step);

    // Simulate writing animation
    timeoutRef.current = setTimeout(() => {
      setDisplayedSteps(prev => [...prev, step]);
      setAnimatingStep(null);
      setCurrentStep(prev => prev + 1);
    }, step.draw_duration_ms || 1000);

  }, [currentStep, script.steps, onAnimationComplete]);

  // Auto-play effect
  useEffect(() => {
    if (isPlaying && currentStep < script.steps.length) {
      playNextStep();
    }

    return () => {
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current);
      }
    };
  }, [isPlaying, currentStep, playNextStep]);

  // Reset animation when script changes
  useEffect(() => {
    reset();
  }, [script]);

  // Control functions
  const play = () => setIsPlaying(true);
  const pause = () => {
    setIsPlaying(false);
    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current);
    }
  };

  const reset = () => {
    setCurrentStep(0);
    setDisplayedSteps([]);
    setAnimatingStep(null);
    setIsPlaying(autoPlay);
    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current);
    }
  };

  const stepForward = () => {
    if (currentStep < script.steps.length) {
      const step = script.steps[currentStep];
      setDisplayedSteps(prev => [...prev, step]);
      setCurrentStep(prev => prev + 1);
    }
  };

  const stepBackward = () => {
    if (displayedSteps.length > 0) {
      setDisplayedSteps(prev => prev.slice(0, -1));
      setCurrentStep(prev => prev - 1);
    }
  };

  // Render step content with proper styling
  const renderStepContent = (step: BoardStep, isAnimating: boolean = false) => {
    const baseClasses = "block transition-all duration-300";
    
    let typeClasses = "";
    switch (step.type) {
      case 'title':
        typeClasses = "text-2xl font-bold text-white mb-4";
        break;
      case 'equation':
        typeClasses = "text-xl font-mono text-blue-300 bg-blue-900/20 p-3 rounded my-3";
        break;
      case 'highlight':
        typeClasses = "text-lg text-yellow-300 font-semibold";
        break;
      case 'diagram':
        typeClasses = "text-sm text-green-300 font-mono";
        break;
      default:
        typeClasses = "text-lg text-white leading-relaxed";
    }

    const animatingClasses = isAnimating 
      ? "opacity-70 transform scale-105" 
      : "opacity-100 transform scale-100";

    return (
      <div
        key={step.step}
        className={`${baseClasses} ${typeClasses} ${animatingClasses}`}
        style={{
          animationDelay: `${step.step * 0.1}s`,
          ...step.style
        }}
      >
        {/* Add writing animation effect */}
        {isAnimating ? (
          <span className="inline-block border-r-2 border-white animate-pulse">
            {step.content}
          </span>
        ) : (
          step.content
        )}
      </div>
    );
  };

  // Calculate progress
  const progress = script.steps.length > 0 
    ? (currentStep / script.steps.length) * 100 
    : 0;

  return (
    <div className={`bg-gray-900 rounded-xl overflow-hidden ${className}`}>
      {/* Blackboard content area */}
      <div 
        className="relative min-h-[400px] p-8"
        style={{ 
          backgroundColor: script.background_color || '#1f2937',
          color: script.text_color || '#ffffff'
        }}
      >
        {/* Blackboard texture overlay */}
        <div className="absolute inset-0 opacity-10 bg-gradient-to-br from-white to-transparent pointer-events-none" />
        
        {/* Content */}
        <div className="relative z-10 space-y-4">
          {/* Render displayed steps */}
          {displayedSteps.map(step => renderStepContent(step))}
          
          {/* Render currently animating step */}
          {animatingStep && renderStepContent(animatingStep, true)}
          
          {/* Empty state */}
          {displayedSteps.length === 0 && !animatingStep && (
            <div className="text-center text-gray-400 py-16">
              <div className="text-6xl mb-4">📚</div>
              <p className="text-xl">Ready to learn something new?</p>
              <p className="text-sm mt-2">Press play to start the explanation</p>
            </div>
          )}
        </div>

        {/* Progress indicator */}
        <div className="absolute bottom-4 right-4 text-xs text-gray-300">
          Step {currentStep} of {script.steps.length}
        </div>
      </div>

      {/* Control panel */}
      <div className="bg-gray-800 px-6 py-4">
        <div className="flex items-center justify-between">
          {/* Playback controls */}
          <div className="flex items-center space-x-2">
            <button
              onClick={stepBackward}
              disabled={displayedSteps.length === 0}
              className="p-2 text-gray-400 hover:text-white disabled:opacity-50 disabled:cursor-not-allowed rounded-md hover:bg-gray-700"
              title="Previous step"
            >
              <SkipBack className="w-4 h-4" />
            </button>

            <button
              onClick={isPlaying ? pause : play}
              disabled={currentStep >= script.steps.length}
              className="p-2 bg-primary-600 text-white rounded-md hover:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed"
              title={isPlaying ? "Pause" : "Play"}
            >
              {isPlaying ? (
                <Pause className="w-4 h-4" />
              ) : (
                <Play className="w-4 h-4" />
              )}
            </button>

            <button
              onClick={stepForward}
              disabled={currentStep >= script.steps.length}
              className="p-2 text-gray-400 hover:text-white disabled:opacity-50 disabled:cursor-not-allowed rounded-md hover:bg-gray-700"
              title="Next step"
            >
              <SkipForward className="w-4 h-4" />
            </button>

            <button
              onClick={reset}
              className="p-2 text-gray-400 hover:text-white rounded-md hover:bg-gray-700"
              title="Reset"
            >
              <RotateCcw className="w-4 h-4" />
            </button>
          </div>

          {/* Progress information */}
          <div className="flex items-center space-x-4 text-sm text-gray-300">
            <span>
              {Math.round(progress)}% complete
            </span>
            
            {script.total_duration_ms && (
              <span>
                ~{Math.round(script.total_duration_ms / 1000)}s total
              </span>
            )}
          </div>
        </div>

        {/* Progress bar */}
        <div className="mt-3 bg-gray-700 rounded-full h-1.5 overflow-hidden">
          <div 
            className="h-full bg-primary-600 transition-all duration-300 ease-out"
            style={{ width: `${progress}%` }}
          />
        </div>
      </div>
    </div>
  );
};

export default AnimatedBlackboard;
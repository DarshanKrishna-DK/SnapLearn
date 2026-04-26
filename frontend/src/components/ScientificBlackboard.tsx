import React, { useState, useEffect, useRef, useCallback } from 'react';
import { Play, Pause, RotateCcw, SkipForward, SkipBack } from 'lucide-react';

import { BoardScript, BoardStep } from '@/types';

interface ScientificBlackboardProps {
  script: BoardScript;
  isPlaying?: boolean;
  onAnimationComplete?: () => void;
  className?: string;
  autoPlay?: boolean;
}

const ScientificBlackboard: React.FC<ScientificBlackboardProps> = ({
  script,
  isPlaying: externalIsPlaying,
  onAnimationComplete,
  className = "",
  autoPlay = true
}) => {
  const [currentStep, setCurrentStep] = useState(0);
  const [isPlaying, setIsPlaying] = useState(autoPlay);
  const [displayedSteps, setDisplayedSteps] = useState<BoardStep[]>([]);
  const [animatingStep, setAnimatingStep] = useState<BoardStep | null>(null);
  
  const timeoutRef = useRef<NodeJS.Timeout | null>(null);

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
    }, step.draw_duration_ms || 2000);

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

  // Convert emoji/text content to scientific notation
  const convertToScientificNotation = (content: string, type: string) => {
    let processed = content;
    
    // Remove excessive emojis and replace with scientific symbols
    processed = processed.replace(/🌊/g, '💧');
    processed = processed.replace(/⬆️|UP!/g, '↑');
    processed = processed.replace(/☁️/g, 'CLOUD');
    processed = processed.replace(/🌧️/g, 'H₂O (l)');
    processed = processed.replace(/💧/g, 'H₂O');
    processed = processed.replace(/🏞️/g, '');
    processed = processed.replace(/🔄/g, '⟲');
    
    // Add scientific formatting based on type
    if (type === 'title') {
      return processed.toUpperCase().replace(/[🎉✨]/g, '');
    }
    
    if (type === 'equation') {
      // Convert water cycle terms to chemical notation
      processed = processed.replace(/water/gi, 'H₂O');
      processed = processed.replace(/vapor/gi, 'H₂O(g)');
      processed = processed.replace(/liquid/gi, 'H₂O(l)');
      processed = processed.replace(/ice/gi, 'H₂O(s)');
    }
    
    if (type === 'diagram') {
      // Create ASCII-style diagrams
      if (processed.includes('EVAPORATION')) {
        return `
    ☀️ Solar Energy
         ↓
    🌊 H₂O(l) → H₂O(g) ↑
    
    EVAPORATION PROCESS`;
      }
      
      if (processed.includes('CONDENSATION')) {
        return `
    H₂O(g) ↑ + Cold Air
         ↓
    ☁️ H₂O(l) droplets
    
    CONDENSATION PROCESS`;
      }
      
      if (processed.includes('PRECIPITATION')) {
        return `
    ☁️ → Heavy clouds
         ↓
    🌧️ H₂O(l) falls
    
    PRECIPITATION PROCESS`;
      }
      
      if (processed.includes('COLLECTION')) {
        return `
    🌧️ → Rivers → Lakes → 🌊
          ↑_______________|
    
    COLLECTION & CYCLE`;
      }
    }
    
    // Clean up excessive punctuation and caps
    processed = processed.replace(/!/g, '.');
    processed = processed.replace(/✨/g, '');
    processed = processed.replace(/This is /g, '→ ');
    
    return processed;
  };

  // Render step content with scientific formatting
  const renderStepContent = (step: BoardStep, isAnimating: boolean = false) => {
    const processedContent = convertToScientificNotation(step.content, step.type);
    
    let typeClasses = "";
    switch (step.type) {
      case 'title':
        typeClasses = "text-3xl font-bold text-yellow-300 mb-6 text-center border-b-2 border-yellow-300 pb-2";
        break;
      case 'equation':
        typeClasses = "text-2xl font-mono text-cyan-300 bg-gray-800/50 p-4 rounded border-l-4 border-cyan-300 my-4";
        break;
      case 'highlight':
        typeClasses = "text-xl text-yellow-300 font-semibold bg-yellow-900/30 px-3 py-2 rounded";
        break;
      case 'diagram':
        typeClasses = "text-lg text-green-300 font-mono bg-green-900/20 p-4 rounded border border-green-600 my-4 whitespace-pre-line";
        break;
      default:
        typeClasses = "text-lg text-white leading-relaxed";
    }

    const animatingClasses = isAnimating 
      ? "opacity-70 transform scale-105 border-l-4 border-yellow-400 pl-4" 
      : "opacity-100 transform scale-100";

    return (
      <div
        key={step.step}
        className={`block transition-all duration-500 ${typeClasses} ${animatingClasses} mb-4`}
        style={{
          animationDelay: `${step.step * 0.1}s`,
          ...step.style
        }}
      >
        {/* Add writing animation effect */}
        {isAnimating ? (
          <span className="inline-block">
            {processedContent}
            <span className="inline-block w-2 h-6 bg-yellow-400 ml-1 animate-pulse"></span>
          </span>
        ) : (
          processedContent
        )}
      </div>
    );
  };

  const progress = script.steps.length > 0 
    ? (currentStep / script.steps.length) * 100 
    : 0;

  return (
    <div className={`bg-gray-900 rounded-xl overflow-hidden border-2 border-green-700 ${className}`}>
      {/* Blackboard content area */}
      <div 
        className="relative min-h-[400px] p-8"
        style={{ 
          backgroundColor: '#0a1a0a',
          background: `
            linear-gradient(45deg, transparent 24%, rgba(68, 68, 68, .05) 25%, rgba(68, 68, 68, .05) 26%, transparent 27%, transparent 74%, rgba(68, 68, 68, .05) 75%, rgba(68, 68, 68, .05) 76%, transparent 77%, transparent),
            linear-gradient(-45deg, transparent 24%, rgba(68, 68, 68, .05) 25%, rgba(68, 68, 68, .05) 26%, transparent 27%, transparent 74%, rgba(68, 68, 68, .05) 75%, rgba(68, 68, 68, .05) 76%, transparent 77%, transparent),
            #0a1a0a
          `,
          backgroundSize: '30px 30px'
        }}
      >
        {/* Blackboard frame */}
        <div className="absolute inset-2 border-2 border-green-600/30 rounded-lg"></div>
        
        {/* Chalk dust particles */}
        <div className="absolute inset-0 pointer-events-none">
          {[...Array(8)].map((_, i) => (
            <div 
              key={i}
              className="absolute w-1 h-1 bg-white rounded-full opacity-30 animate-bounce"
              style={{
                left: `${Math.random() * 90 + 5}%`,
                top: `${Math.random() * 90 + 5}%`,
                animationDelay: `${Math.random() * 2}s`,
                animationDuration: `${3 + Math.random() * 2}s`
              }}
            />
          ))}
        </div>
        
        {/* Content */}
        <div className="relative z-10 space-y-4">
          {/* Render displayed steps */}
          {displayedSteps.map(step => renderStepContent(step))}
          
          {/* Render currently animating step */}
          {animatingStep && renderStepContent(animatingStep, true)}
          
          {/* Empty state */}
          {displayedSteps.length === 0 && !animatingStep && (
            <div className="text-center text-green-300 py-16">
              <div className="text-6xl mb-4">🎓</div>
              <p className="text-xl font-mono">SCIENTIFIC BLACKBOARD READY</p>
              <p className="text-sm mt-2 opacity-70">Press ▶ to start the lesson</p>
            </div>
          )}
        </div>

        {/* Progress indicator */}
        <div className="absolute bottom-4 right-4 text-xs text-green-300 font-mono">
          [{currentStep}/{script.steps.length}] {Math.round(progress)}%
        </div>
      </div>

      {/* Control panel */}
      <div className="bg-gray-800 px-6 py-4 border-t border-green-700">
        <div className="flex items-center justify-between">
          {/* Playback controls */}
          <div className="flex items-center space-x-2">
            <button
              onClick={stepBackward}
              disabled={displayedSteps.length === 0}
              className="p-2 text-gray-400 hover:text-green-300 disabled:opacity-50 disabled:cursor-not-allowed rounded-md hover:bg-gray-700 transition-all"
              title="Previous step"
            >
              <SkipBack className="w-4 h-4" />
            </button>

            <button
              onClick={isPlaying ? pause : play}
              disabled={currentStep >= script.steps.length}
              className="p-2 bg-green-600 text-white rounded-md hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
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
              className="p-2 text-gray-400 hover:text-green-300 disabled:opacity-50 disabled:cursor-not-allowed rounded-md hover:bg-gray-700 transition-all"
              title="Next step"
            >
              <SkipForward className="w-4 h-4" />
            </button>

            <button
              onClick={reset}
              className="p-2 text-gray-400 hover:text-green-300 rounded-md hover:bg-gray-700 transition-all"
              title="Reset"
            >
              <RotateCcw className="w-4 h-4" />
            </button>
          </div>

          {/* Progress information */}
          <div className="flex items-center space-x-4 text-sm text-green-300 font-mono">
            <span>
              STEP {currentStep}/{script.steps.length}
            </span>
            
            {script.total_duration_ms && (
              <span>
                ~{Math.round(script.total_duration_ms / 1000)}s
              </span>
            )}
          </div>
        </div>

        {/* Progress bar */}
        <div className="mt-3 bg-gray-700 rounded-full h-1.5 overflow-hidden">
          <div 
            className="h-full bg-green-600 transition-all duration-500 ease-out"
            style={{ width: `${progress}%` }}
          />
        </div>
      </div>
    </div>
  );
};

export default ScientificBlackboard;
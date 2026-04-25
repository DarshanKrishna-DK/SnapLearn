import React, { useState, useRef, useCallback, useEffect } from 'react';
import { Mic, MicOff, Square, Play, Pause, Volume2, AlertCircle, CheckCircle } from 'lucide-react';
import { toast } from 'react-hot-toast';

import LoadingSpinner from './ui/LoadingSpinner';
import { apiClient, handleAPIError } from '@/utils/api';
import { ProcessedInputResponse, GradeLevel, LanguageCode } from '@/types';

interface VoiceInputProps {
  studentId: string;
  gradeLevel: GradeLevel;
  language: LanguageCode;
  onTextTranscribed?: (text: string) => void;
  onProcessingResult?: (result: ProcessedInputResponse) => void;
  className?: string;
}

const VoiceInput: React.FC<VoiceInputProps> = ({
  studentId,
  gradeLevel,
  language,
  onTextTranscribed,
  onProcessingResult,
  className = "",
}) => {
  const [isRecording, setIsRecording] = useState(false);
  const [isPlaying, setIsPlaying] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const [recordingDuration, setRecordingDuration] = useState(0);
  const [audioBlob, setAudioBlob] = useState<Blob | null>(null);
  const [audioUrl, setAudioUrl] = useState<string | null>(null);
  const [processingResult, setProcessingResult] = useState<ProcessedInputResponse | null>(null);
  
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioRef = useRef<HTMLAudioElement | null>(null);
  const recordingIntervalRef = useRef<NodeJS.Timeout | null>(null);
  const chunksRef = useRef<Blob[]>([]);

  // Check for browser support
  const isSupportedBrowser = typeof navigator !== 'undefined' && 
                           navigator.mediaDevices && 
                           navigator.mediaDevices.getUserMedia;

  // Start recording
  const startRecording = useCallback(async () => {
    if (!isSupportedBrowser) {
      toast.error('Voice recording is not supported in this browser');
      return;
    }

    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        audio: {
          echoCancellation: true,
          noiseSuppression: true,
          sampleRate: 44100,
        },
      });

      const mediaRecorder = new MediaRecorder(stream);
      mediaRecorderRef.current = mediaRecorder;
      chunksRef.current = [];

      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          chunksRef.current.push(event.data);
        }
      };

      mediaRecorder.onstop = () => {
        const blob = new Blob(chunksRef.current, { type: 'audio/wav' });
        setAudioBlob(blob);
        setAudioUrl(URL.createObjectURL(blob));
        
        // Stop all tracks to release microphone
        stream.getTracks().forEach(track => track.stop());
      };

      mediaRecorder.start();
      setIsRecording(true);
      setRecordingDuration(0);
      setProcessingResult(null);

      // Start duration counter
      recordingIntervalRef.current = setInterval(() => {
        setRecordingDuration(prev => prev + 1);
      }, 1000);

      toast.success('Recording started');

    } catch (error) {
      console.error('Error starting recording:', error);
      toast.error('Could not access microphone. Please check permissions.');
    }
  }, [isSupportedBrowser]);

  // Stop recording
  const stopRecording = useCallback(() => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
      
      if (recordingIntervalRef.current) {
        clearInterval(recordingIntervalRef.current);
        recordingIntervalRef.current = null;
      }

      toast.success('Recording stopped');
    }
  }, [isRecording]);

  // Play recorded audio
  const playAudio = useCallback(() => {
    if (audioRef.current && audioUrl) {
      audioRef.current.play();
      setIsPlaying(true);
    }
  }, [audioUrl]);

  // Pause audio playback
  const pauseAudio = useCallback(() => {
    if (audioRef.current) {
      audioRef.current.pause();
      setIsPlaying(false);
    }
  }, []);

  // Handle audio playback end
  const handleAudioEnd = useCallback(() => {
    setIsPlaying(false);
  }, []);

  // Convert blob to base64
  const blobToBase64 = (blob: Blob): Promise<string> => {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.readAsDataURL(blob);
      reader.onload = () => {
        const result = reader.result as string;
        // Remove the data URL prefix
        const base64 = result.split(',')[1];
        resolve(base64);
      };
      reader.onerror = reject;
    });
  };

  // Process the recorded audio
  const handleProcessAudio = useCallback(async () => {
    if (!audioBlob) {
      toast.error('No audio recording to process');
      return;
    }

    setIsProcessing(true);
    setProcessingResult(null);

    try {
      // Convert audio to base64
      const base64Data = await blobToBase64(audioBlob);

      // Process the audio
      const result = await apiClient.processVoice({
        student_id: studentId,
        grade_level: gradeLevel,
        language: language,
        input_type: 'voice',
        audio_data: base64Data,
        audio_format: 'wav',
        context: 'Student voice recording for question processing'
      });

      setProcessingResult(result);

      if (result.success && result.normalized_text) {
        onTextTranscribed?.(result.normalized_text);
        onProcessingResult?.(result);
        toast.success('Voice transcribed successfully!');
      } else if (result.error) {
        toast.error(`Failed to process voice: ${result.error}`);
      } else {
        toast.warning('No speech recognized in the recording');
      }

    } catch (error) {
      console.error('Error processing voice:', error);
      toast.error(handleAPIError(error));
    } finally {
      setIsProcessing(false);
    }
  }, [audioBlob, studentId, gradeLevel, language, onTextTranscribed, onProcessingResult]);

  // Clear recording
  const clearRecording = () => {
    setAudioBlob(null);
    setAudioUrl(null);
    setRecordingDuration(0);
    setProcessingResult(null);
    setIsPlaying(false);
  };

  // Format duration
  const formatDuration = (seconds: number): string => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (recordingIntervalRef.current) {
        clearInterval(recordingIntervalRef.current);
      }
      if (audioUrl) {
        URL.revokeObjectURL(audioUrl);
      }
    };
  }, [audioUrl]);

  if (!isSupportedBrowser) {
    return (
      <div className={`text-center py-8 ${className}`}>
        <AlertCircle className="w-12 h-12 text-red-400 mx-auto mb-4" />
        <p className="text-red-600 font-medium">Voice Recording Not Supported</p>
        <p className="text-sm text-red-500 mt-2">
          Please use a modern browser that supports audio recording
        </p>
      </div>
    );
  }

  return (
    <div className={`space-y-4 ${className}`}>
      {/* Recording Controls */}
      <div className="text-center">
        {!isRecording && !audioBlob ? (
          // Start Recording Button
          <button
            onClick={startRecording}
            className="btn-primary flex items-center space-x-2 mx-auto"
            disabled={isProcessing}
          >
            <Mic className="w-5 h-5" />
            <span>Start Recording</span>
          </button>
        ) : isRecording ? (
          // Stop Recording Button
          <div className="space-y-4">
            <div className="flex items-center justify-center space-x-4">
              <button
                onClick={stopRecording}
                className="bg-red-600 text-white px-6 py-3 rounded-lg hover:bg-red-700 flex items-center space-x-2 animate-pulse"
              >
                <Square className="w-5 h-5 fill-current" />
                <span>Stop Recording</span>
              </button>
            </div>
            
            <div className="text-center">
              <div className="inline-flex items-center space-x-2 bg-red-100 text-red-800 px-4 py-2 rounded-full">
                <div className="w-2 h-2 bg-red-600 rounded-full animate-pulse" />
                <span className="font-mono text-lg">{formatDuration(recordingDuration)}</span>
              </div>
            </div>
          </div>
        ) : null}
      </div>

      {/* Audio Player and Controls */}
      {audioBlob && audioUrl && (
        <div className="border border-gray-200 rounded-lg p-4 space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-medium text-gray-900">
              Recorded Audio ({formatDuration(recordingDuration)})
            </h3>
            <button
              onClick={clearRecording}
              className="text-sm text-red-600 hover:text-red-800"
              disabled={isProcessing}
            >
              Clear Recording
            </button>
          </div>

          {/* Audio Player */}
          <div className="flex items-center space-x-3">
            <button
              onClick={isPlaying ? pauseAudio : playAudio}
              className="btn-outline flex items-center space-x-2"
              disabled={isProcessing}
            >
              {isPlaying ? (
                <>
                  <Pause className="w-4 h-4" />
                  <span>Pause</span>
                </>
              ) : (
                <>
                  <Play className="w-4 h-4" />
                  <span>Play</span>
                </>
              )}
            </button>

            <div className="flex-1 flex items-center space-x-2">
              <Volume2 className="w-4 h-4 text-gray-500" />
              <div className="flex-1 bg-gray-200 rounded-full h-2 relative overflow-hidden">
                <div className="bg-primary-600 h-full rounded-full w-0 animate-pulse" />
              </div>
            </div>
          </div>

          {/* Process Button */}
          <div className="text-center">
            <button
              onClick={handleProcessAudio}
              disabled={isProcessing}
              className="btn-primary flex items-center space-x-2 mx-auto"
            >
              {isProcessing ? (
                <>
                  <LoadingSpinner size="sm" />
                  <span>Transcribing audio...</span>
                </>
              ) : (
                <>
                  <Mic className="w-4 h-4" />
                  <span>Convert to Text</span>
                </>
              )}
            </button>
          </div>

          {/* Hidden Audio Element */}
          <audio
            ref={audioRef}
            src={audioUrl}
            onEnded={handleAudioEnd}
            className="hidden"
          />
        </div>
      )}

      {/* Processing Result */}
      {processingResult && (
        <div className={`border rounded-lg p-4 ${
          processingResult.success 
            ? 'border-green-200 bg-green-50' 
            : 'border-red-200 bg-red-50'
        }`}>
          <div className="flex items-center space-x-2 mb-3">
            {processingResult.success ? (
              <CheckCircle className="w-5 h-5 text-green-600" />
            ) : (
              <AlertCircle className="w-5 h-5 text-red-600" />
            )}
            <h3 className={`font-medium ${
              processingResult.success ? 'text-green-900' : 'text-red-900'
            }`}>
              Transcription Result
            </h3>
          </div>

          {processingResult.success ? (
            <div className="space-y-3">
              {/* Transcribed Text */}
              {processingResult.normalized_text && (
                <div>
                  <h4 className="text-sm font-medium text-green-800 mb-1">
                    Transcribed Text:
                  </h4>
                  <p className="text-sm text-green-700 bg-white p-2 rounded border">
                    "{processingResult.normalized_text}"
                  </p>
                </div>
              )}

              {/* Math Expressions */}
              {processingResult.math_expressions && processingResult.math_expressions.length > 0 && (
                <div>
                  <h4 className="text-sm font-medium text-green-800 mb-1">
                    Mathematical Expressions Found:
                  </h4>
                  <div className="flex flex-wrap gap-1">
                    {processingResult.math_expressions.map((expr, index) => (
                      <span
                        key={index}
                        className="text-xs bg-blue-100 text-blue-800 px-2 py-1 rounded"
                      >
                        {expr}
                      </span>
                    ))}
                  </div>
                </div>
              )}

              {/* Metadata */}
              <div className="grid grid-cols-2 gap-4 text-xs text-green-700">
                <div>
                  <span className="font-medium">Language:</span> {processingResult.detected_language}
                </div>
                <div>
                  <span className="font-medium">Confidence:</span> {Math.round(processingResult.confidence_score * 100)}%
                </div>
                <div>
                  <span className="font-medium">Processing Time:</span> {processingResult.processing_time_ms.toFixed(0)}ms
                </div>
                {processingResult.metadata.audio_duration_seconds && (
                  <div>
                    <span className="font-medium">Duration:</span> {processingResult.metadata.audio_duration_seconds.toFixed(1)}s
                  </div>
                )}
              </div>
            </div>
          ) : (
            <p className="text-sm text-red-700">
              {processingResult.error || 'Failed to transcribe audio'}
            </p>
          )}
        </div>
      )}

      {/* Instructions */}
      {!audioBlob && !isRecording && (
        <div className="text-center py-8 border-2 border-dashed border-gray-300 rounded-lg">
          <Mic className="w-12 h-12 text-gray-400 mx-auto mb-4" />
          <p className="text-gray-600 mb-2">Record your voice to ask questions</p>
          <p className="text-sm text-gray-500">
            Speak clearly and include all details of your question
          </p>
          <p className="text-xs text-gray-400 mt-2">
            Perfect for complex problems that are easier to speak than type
          </p>
        </div>
      )}
    </div>
  );
};

export default VoiceInput;
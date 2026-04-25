import React, { useState, useRef, useCallback } from 'react';
import { Upload, Camera, X, Image as ImageIcon, AlertCircle, CheckCircle } from 'lucide-react';
import { toast } from 'react-hot-toast';

import LoadingSpinner from './ui/LoadingSpinner';
import { apiClient, handleAPIError } from '@/utils/api';
import { ProcessedInputResponse, GradeLevel, LanguageCode } from '@/types';

interface ImageUploadProps {
  studentId: string;
  gradeLevel: GradeLevel;
  language: LanguageCode;
  onTextExtracted?: (text: string) => void;
  onProcessingResult?: (result: ProcessedInputResponse) => void;
  className?: string;
}

const ImageUpload: React.FC<ImageUploadProps> = ({
  studentId,
  gradeLevel,
  language,
  onTextExtracted,
  onProcessingResult,
  className = "",
}) => {
  const [selectedImage, setSelectedImage] = useState<File | null>(null);
  const [imagePreview, setImagePreview] = useState<string | null>(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const [processingResult, setProcessingResult] = useState<ProcessedInputResponse | null>(null);
  
  const fileInputRef = useRef<HTMLInputElement>(null);
  const cameraInputRef = useRef<HTMLInputElement>(null);

  // Handle file selection
  const handleFileSelect = useCallback((event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    // Validate file type
    if (!file.type.startsWith('image/')) {
      toast.error('Please select a valid image file');
      return;
    }

    // Validate file size (10MB limit)
    if (file.size > 10 * 1024 * 1024) {
      toast.error('Image file must be less than 10MB');
      return;
    }

    setSelectedImage(file);
    
    // Create preview
    const reader = new FileReader();
    reader.onload = (e) => {
      setImagePreview(e.target?.result as string);
    };
    reader.readAsDataURL(file);

    setProcessingResult(null);
  }, []);

  // Convert file to base64
  const fileToBase64 = (file: File): Promise<string> => {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.readAsDataURL(file);
      reader.onload = () => {
        const result = reader.result as string;
        // Remove the data URL prefix (e.g., "data:image/jpeg;base64,")
        const base64 = result.split(',')[1];
        resolve(base64);
      };
      reader.onerror = reject;
    });
  };

  // Process the uploaded image
  const handleProcessImage = useCallback(async () => {
    if (!selectedImage) {
      toast.error('Please select an image first');
      return;
    }

    setIsProcessing(true);
    setProcessingResult(null);

    try {
      // Convert image to base64
      const base64Data = await fileToBase64(selectedImage);
      
      // Get image format
      const imageFormat = selectedImage.type.split('/')[1] || 'jpeg';

      // Process the image
      const result = await apiClient.processImage({
        student_id: studentId,
        grade_level: gradeLevel,
        language: language,
        input_type: 'image',
        image_data: base64Data,
        image_format: imageFormat,
        context: 'Student uploaded image for question processing'
      });

      setProcessingResult(result);
      
      if (result.success && result.normalized_text) {
        onTextExtracted?.(result.normalized_text);
        onProcessingResult?.(result);
        toast.success('Text extracted from image successfully!');
      } else if (result.error) {
        toast.error(`Failed to process image: ${result.error}`);
      } else {
        toast.warning('No text found in the image');
      }

    } catch (error) {
      console.error('Error processing image:', error);
      toast.error(handleAPIError(error));
    } finally {
      setIsProcessing(false);
    }
  }, [selectedImage, studentId, gradeLevel, language, onTextExtracted, onProcessingResult]);

  // Clear selected image
  const handleClearImage = () => {
    setSelectedImage(null);
    setImagePreview(null);
    setProcessingResult(null);
    if (fileInputRef.current) fileInputRef.current.value = '';
    if (cameraInputRef.current) cameraInputRef.current.value = '';
  };

  // Open file picker
  const openFilePicker = () => {
    fileInputRef.current?.click();
  };

  // Open camera
  const openCamera = () => {
    cameraInputRef.current?.click();
  };

  return (
    <div className={`space-y-4 ${className}`}>
      {/* Upload Controls */}
      <div className="flex items-center space-x-3">
        <button
          onClick={openFilePicker}
          className="btn-outline flex items-center space-x-2"
          disabled={isProcessing}
        >
          <Upload className="w-4 h-4" />
          <span>Upload Image</span>
        </button>

        <button
          onClick={openCamera}
          className="btn-outline flex items-center space-x-2"
          disabled={isProcessing}
        >
          <Camera className="w-4 h-4" />
          <span>Take Photo</span>
        </button>

        {selectedImage && (
          <button
            onClick={handleClearImage}
            className="btn-ghost text-red-600 flex items-center space-x-2"
            disabled={isProcessing}
          >
            <X className="w-4 h-4" />
            <span>Clear</span>
          </button>
        )}
      </div>

      {/* Hidden file inputs */}
      <input
        ref={fileInputRef}
        type="file"
        accept="image/*"
        onChange={handleFileSelect}
        className="hidden"
      />
      <input
        ref={cameraInputRef}
        type="file"
        accept="image/*"
        capture="environment"
        onChange={handleFileSelect}
        className="hidden"
      />

      {/* Image Preview */}
      {imagePreview && (
        <div className="border border-gray-200 rounded-lg p-4">
          <div className="flex items-center justify-between mb-3">
            <h3 className="text-sm font-medium text-gray-900">Selected Image</h3>
            {selectedImage && (
              <span className="text-xs text-gray-500">
                {selectedImage.name} ({(selectedImage.size / 1024).toFixed(1)} KB)
              </span>
            )}
          </div>
          
          <div className="relative">
            <img
              src={imagePreview}
              alt="Selected"
              className="max-w-full max-h-64 object-contain rounded-lg mx-auto border"
            />
          </div>

          {/* Process Button */}
          <div className="mt-3 text-center">
            <button
              onClick={handleProcessImage}
              disabled={isProcessing}
              className="btn-primary flex items-center space-x-2 mx-auto"
            >
              {isProcessing ? (
                <>
                  <LoadingSpinner size="sm" />
                  <span>Processing image...</span>
                </>
              ) : (
                <>
                  <ImageIcon className="w-4 h-4" />
                  <span>Extract Text from Image</span>
                </>
              )}
            </button>
          </div>
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
              Processing Result
            </h3>
          </div>

          {processingResult.success ? (
            <div className="space-y-3">
              {/* Extracted Text */}
              {processingResult.normalized_text && (
                <div>
                  <h4 className="text-sm font-medium text-green-800 mb-1">
                    Extracted Text:
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
                {processingResult.metadata.image_format && (
                  <div>
                    <span className="font-medium">Format:</span> {processingResult.metadata.image_format}
                  </div>
                )}
              </div>
            </div>
          ) : (
            <p className="text-sm text-red-700">
              {processingResult.error || 'Failed to process image'}
            </p>
          )}
        </div>
      )}

      {/* Upload Instructions */}
      {!selectedImage && (
        <div className="text-center py-8 border-2 border-dashed border-gray-300 rounded-lg">
          <ImageIcon className="w-12 h-12 text-gray-400 mx-auto mb-4" />
          <p className="text-gray-600 mb-2">Upload an image containing text or math problems</p>
          <p className="text-sm text-gray-500">
            Supports JPG, PNG, WebP, GIF formats • Max size: 10MB
          </p>
          <p className="text-xs text-gray-400 mt-2">
            Perfect for homework problems, math equations, or handwritten notes
          </p>
        </div>
      )}
    </div>
  );
};

export default ImageUpload;
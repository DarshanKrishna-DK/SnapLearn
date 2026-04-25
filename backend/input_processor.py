"""
Input Processing Module for SnapLearn AI - Phase 2
Handles multiple input modalities: text, image, voice
"""

import os
import logging
import base64
import tempfile
import io
from typing import Dict, Any, Optional, List, Union, Tuple
from pathlib import Path
import asyncio

from PIL import Image
import speech_recognition as sr
from pydub import AudioSegment
from langdetect import detect, LangDetectException

from models import LanguageCode
from utils import schedule_async_init

logger = logging.getLogger(__name__)

class InputProcessor:
    """Processes multiple input types and normalizes them to clean text"""
    
    def __init__(self):
        self.gemini_client = None
        self.speech_recognizer = sr.Recognizer()
        self.supported_image_formats = ['.jpg', '.jpeg', '.png', '.webp', '.gif', '.bmp']
        self.supported_audio_formats = ['.wav', '.mp3', '.m4a', '.ogg', '.flac']
        
        # Initialize Gemini client (works at import time and under uvicorn)
        schedule_async_init(self._init_gemini())
    
    async def _init_gemini(self):
        """Initialize Gemini client for multimodal processing"""
        try:
            from google import genai
            
            api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
            if not api_key:
                logger.error("Gemini API key not found for input processing")
                return
            
            self.gemini_client = genai.Client(api_key=api_key)
            logger.info("Input processor: Gemini client initialized")
            
        except ImportError:
            logger.error("Google GenAI library not installed for input processing")
        except Exception as e:
            logger.error(f"Error initializing Gemini for input processing: {str(e)}")
    
    async def process_input(self, 
                          input_data: Union[str, bytes], 
                          input_type: str,
                          student_id: str,
                          context: Optional[str] = None) -> Dict[str, Any]:
        """
        Main entry point for processing any input type
        
        Args:
            input_data: Raw input (text, image bytes, audio bytes)
            input_type: 'text', 'image', 'voice'
            student_id: Student identifier for context
            context: Additional context for processing
            
        Returns:
            Processed input with normalized text and metadata
        """
        try:
            logger.info(f"Processing {input_type} input for student {student_id}")
            
            if input_type == 'text':
                return await self._process_text_input(input_data, student_id, context)
            elif input_type == 'image':
                return await self._process_image_input(input_data, student_id, context)
            elif input_type == 'voice':
                return await self._process_voice_input(input_data, student_id, context)
            else:
                raise ValueError(f"Unsupported input type: {input_type}")
                
        except Exception as e:
            logger.error(f"Error processing {input_type} input: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "input_type": input_type,
                "normalized_text": "",
                "detected_language": "en",
                "confidence_score": 0.0
            }
    
    async def _process_text_input(self, 
                                text: str, 
                                student_id: str, 
                                context: Optional[str] = None) -> Dict[str, Any]:
        """Process direct text input"""
        try:
            # Clean and normalize text
            normalized_text = self._normalize_text(text)
            
            # Detect language
            detected_language = self._detect_language(normalized_text)
            
            # Extract mathematical expressions if any
            math_expressions = self._extract_math_expressions(normalized_text)
            
            return {
                "success": True,
                "input_type": "text",
                "original_text": text,
                "normalized_text": normalized_text,
                "detected_language": detected_language,
                "confidence_score": 1.0,
                "math_expressions": math_expressions,
                "processing_time_ms": 0,
                "metadata": {
                    "student_id": student_id,
                    "context": context,
                    "text_length": len(normalized_text),
                    "word_count": len(normalized_text.split())
                }
            }
            
        except Exception as e:
            logger.error(f"Error processing text input: {str(e)}")
            raise
    
    async def _process_image_input(self, 
                                 image_data: bytes, 
                                 student_id: str, 
                                 context: Optional[str] = None) -> Dict[str, Any]:
        """Process image input using Gemini Vision for OCR and understanding"""
        try:
            start_time = asyncio.get_event_loop().time()
            
            # Validate image
            image_info = self._validate_image(image_data)
            
            # Use Gemini for image understanding and text extraction
            extracted_text = await self._extract_text_from_image_gemini(image_data, context)
            
            # Normalize extracted text
            normalized_text = self._normalize_text(extracted_text)
            
            # Detect language
            detected_language = self._detect_language(normalized_text) if normalized_text else "en"
            
            # Extract mathematical expressions
            math_expressions = self._extract_math_expressions(normalized_text)
            
            processing_time = (asyncio.get_event_loop().time() - start_time) * 1000
            
            return {
                "success": True,
                "input_type": "image",
                "extracted_text": extracted_text,
                "normalized_text": normalized_text,
                "detected_language": detected_language,
                "confidence_score": 0.9,  # High confidence for Gemini Vision
                "math_expressions": math_expressions,
                "processing_time_ms": processing_time,
                "metadata": {
                    "student_id": student_id,
                    "context": context,
                    "image_format": image_info["format"],
                    "image_size": image_info["size"],
                    "text_length": len(normalized_text),
                    "has_math": len(math_expressions) > 0
                }
            }
            
        except Exception as e:
            logger.error(f"Error processing image input: {str(e)}")
            raise
    
    async def _process_voice_input(self, 
                                 audio_data: bytes, 
                                 student_id: str, 
                                 context: Optional[str] = None) -> Dict[str, Any]:
        """Process voice input using speech recognition"""
        try:
            start_time = asyncio.get_event_loop().time()
            
            # Convert audio to text using speech recognition
            transcribed_text = await self._transcribe_audio(audio_data)
            
            # Normalize text
            normalized_text = self._normalize_text(transcribed_text)
            
            # Detect language
            detected_language = self._detect_language(normalized_text) if normalized_text else "en"
            
            # Extract mathematical expressions
            math_expressions = self._extract_math_expressions(normalized_text)
            
            processing_time = (asyncio.get_event_loop().time() - start_time) * 1000
            
            return {
                "success": True,
                "input_type": "voice",
                "transcribed_text": transcribed_text,
                "normalized_text": normalized_text,
                "detected_language": detected_language,
                "confidence_score": 0.8,  # Speech recognition confidence
                "math_expressions": math_expressions,
                "processing_time_ms": processing_time,
                "metadata": {
                    "student_id": student_id,
                    "context": context,
                    "audio_duration_seconds": self._get_audio_duration(audio_data),
                    "text_length": len(normalized_text),
                    "has_math": len(math_expressions) > 0
                }
            }
            
        except Exception as e:
            logger.error(f"Error processing voice input: {str(e)}")
            raise
    
    async def _extract_text_from_image_gemini(self, 
                                            image_data: bytes, 
                                            context: Optional[str] = None) -> str:
        """Extract text from image using Gemini Vision API"""
        try:
            if not self.gemini_client:
                raise Exception("Gemini client not initialized")
            
            # Prepare the image for Gemini
            image_b64 = base64.b64encode(image_data).decode('utf-8')
            
            # Create prompt for text extraction
            prompt = self._create_image_analysis_prompt(context)
            
            # Call Gemini with multimodal input
            response = self.gemini_client.models.generate_content(
                model="gemini-2.5-flash",
                contents=[
                    {
                        "parts": [
                            {"text": prompt},
                            {
                                "inline_data": {
                                    "mime_type": "image/jpeg",  # Gemini auto-detects format
                                    "data": image_b64
                                }
                            }
                        ]
                    }
                ]
            )
            
            extracted_text = response.text.strip()
            logger.info(f"Extracted text from image: {extracted_text[:100]}...")
            
            return extracted_text
            
        except Exception as e:
            logger.error(f"Error extracting text from image with Gemini: {str(e)}")
            return ""
    
    def _create_image_analysis_prompt(self, context: Optional[str] = None) -> str:
        """Create a prompt for Gemini to analyze images and extract text"""
        base_prompt = """Please analyze this image and extract all text content. Focus on:

1. Mathematical equations, formulas, and expressions
2. Written questions or problems 
3. Handwritten or printed text
4. Diagrams with labels or annotations

Extract the text exactly as it appears, preserving mathematical notation and structure. If you see mathematical expressions, include them using standard notation.

If this appears to be a homework problem or educational content, also provide:
- The main question or problem being asked
- Any given information or constraints
- The subject area (math, science, etc.)

Extracted text:"""

        if context:
            return f"{base_prompt}\n\nContext: {context}\n\nExtracted text:"
        
        return base_prompt
    
    async def _transcribe_audio(self, audio_data: bytes) -> str:
        """Transcribe audio to text using speech recognition"""
        try:
            # Create temporary file for audio processing
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
                temp_path = temp_file.name
                
                try:
                    # Convert audio to WAV format if needed
                    audio_segment = AudioSegment.from_file(io.BytesIO(audio_data))
                    audio_segment.export(temp_path, format="wav")
                    
                    # Use speech recognition
                    with sr.AudioFile(temp_path) as source:
                        audio = self.speech_recognizer.record(source)
                        text = self.speech_recognizer.recognize_google(audio)
                        
                    logger.info(f"Transcribed audio to text: {text[:100]}...")
                    return text
                    
                finally:
                    # Clean up temporary file
                    if os.path.exists(temp_path):
                        os.unlink(temp_path)
                        
        except sr.UnknownValueError:
            logger.warning("Speech recognition could not understand audio")
            return ""
        except sr.RequestError as e:
            logger.error(f"Speech recognition service error: {str(e)}")
            return ""
        except Exception as e:
            logger.error(f"Error transcribing audio: {str(e)}")
            return ""
    
    def _normalize_text(self, text: str) -> str:
        """Clean and normalize text input"""
        if not text:
            return ""
        
        # Basic text cleaning
        normalized = text.strip()
        
        # Remove extra whitespace
        normalized = ' '.join(normalized.split())
        
        # Fix common OCR errors
        normalized = self._fix_ocr_errors(normalized)
        
        # Standardize mathematical notation
        normalized = self._standardize_math_notation(normalized)
        
        return normalized
    
    def _fix_ocr_errors(self, text: str) -> str:
        """Fix common OCR errors in text"""
        # Common OCR substitutions
        corrections = {
            '0': ['O', 'o', '°'],
            '1': ['l', 'I', '|'],
            '5': ['S', 's'],
            '6': ['G', 'b'],
            '8': ['B'],
            '+': ['±', '＋'],
            '=': ['＝', '－'],
            'x': ['×', '✕', '*'],
            '÷': ['/', '÷'],
        }
        
        # Apply corrections (simple approach - could be enhanced with ML)
        corrected = text
        for correct, errors in corrections.items():
            for error in errors:
                # Only replace if it looks like math context
                if self._is_math_context(corrected, error):
                    corrected = corrected.replace(error, correct)
        
        return corrected
    
    def _is_math_context(self, text: str, char: str) -> bool:
        """Check if a character is likely in a mathematical context"""
        math_indicators = ['=', '+', '-', '×', '÷', '(', ')', '[', ']', 'solve', 'calculate', 'find']
        return any(indicator in text.lower() for indicator in math_indicators)
    
    def _standardize_math_notation(self, text: str) -> str:
        """Standardize mathematical notation in text"""
        # Convert common math symbols
        replacements = {
            '×': '*',
            '÷': '/',
            '−': '-',
            '≈': '≈',
            '≠': '≠',
            '≤': '<=',
            '≥': '>=',
        }
        
        standardized = text
        for old, new in replacements.items():
            standardized = standardized.replace(old, new)
        
        return standardized
    
    def _extract_math_expressions(self, text: str) -> List[str]:
        """Extract mathematical expressions from text"""
        import re
        
        expressions = []
        
        # Patterns for mathematical expressions
        patterns = [
            r'\d+\s*[+\-*/÷×]\s*\d+(?:\s*[+\-*/÷×]\s*\d+)*',  # Basic arithmetic
            r'\d*x[²³⁴]?\s*[+\-]\s*\d*x?\s*[+\-]\s*\d+',     # Polynomials
            r'\d+/\d+',                                         # Fractions
            r'\d+\.\d+',                                        # Decimals
            r'\(\s*[^)]+\s*\)',                                # Expressions in parentheses
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            expressions.extend(matches)
        
        return list(set(expressions))  # Remove duplicates
    
    def _detect_language(self, text: str) -> str:
        """Detect the language of the text"""
        try:
            if not text or len(text.strip()) < 10:
                return "en"  # Default to English for short texts
            
            detected = detect(text)
            
            # Map to supported language codes
            language_mapping = {
                'en': 'en', 'hi': 'hi', 'es': 'es', 'fr': 'fr',
                'de': 'de', 'zh': 'zh', 'ja': 'ja'
            }
            
            return language_mapping.get(detected, 'en')
            
        except LangDetectException:
            logger.warning("Language detection failed, defaulting to English")
            return "en"
    
    def _validate_image(self, image_data: bytes) -> Dict[str, Any]:
        """Validate image data and extract basic info"""
        try:
            image = Image.open(io.BytesIO(image_data))
            
            return {
                "format": image.format.lower() if image.format else "unknown",
                "size": image.size,
                "mode": image.mode,
                "valid": True
            }
            
        except Exception as e:
            logger.error(f"Error validating image: {str(e)}")
            raise ValueError(f"Invalid image data: {str(e)}")
    
    def _get_audio_duration(self, audio_data: bytes) -> float:
        """Get duration of audio in seconds"""
        try:
            audio_segment = AudioSegment.from_file(io.BytesIO(audio_data))
            return len(audio_segment) / 1000.0  # Convert ms to seconds
        except Exception:
            return 0.0
    
    def is_healthy(self) -> bool:
        """Check if input processor is healthy"""
        return self.gemini_client is not None
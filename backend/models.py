"""
Pydantic models for SnapLearn AI API
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any, Union
from datetime import datetime
from enum import Enum

class LanguageCode(str, Enum):
    """Supported languages"""
    ENGLISH = "en"
    HINDI = "hi"
    SPANISH = "es"
    FRENCH = "fr"
    GERMAN = "de"
    CHINESE = "zh"
    JAPANESE = "ja"

class GradeLevel(str, Enum):
    """Grade levels supported"""
    K = "K"
    GRADE_1 = "1"
    GRADE_2 = "2"
    GRADE_3 = "3"
    GRADE_4 = "4"
    GRADE_5 = "5"
    GRADE_6 = "6"
    GRADE_7 = "7"
    GRADE_8 = "8"
    GRADE_9 = "9"
    GRADE_10 = "10"
    GRADE_11 = "11"
    GRADE_12 = "12"

class LearningStyle(str, Enum):
    """Learning style preferences"""
    VISUAL = "visual"
    AUDITORY = "auditory"
    KINESTHETIC = "kinesthetic"
    READING_WRITING = "reading_writing"
    MIXED = "mixed"

class ConfidenceLevel(str, Enum):
    """Student confidence levels"""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    UNKNOWN = "unknown"

# Request Models
class QuestionRequest(BaseModel):
    """Request model for explanation endpoint"""
    question: str = Field(..., description="Student's question")
    student_id: str = Field(..., description="Unique student identifier")
    grade_level: GradeLevel = Field(..., description="Student's grade level")
    language: LanguageCode = Field(default=LanguageCode.ENGLISH, description="Preferred language")
    context: Optional[str] = Field(None, description="Additional context for the question")

class MultiModalRequest(BaseModel):
    """Request model for multimodal input processing"""
    student_id: str = Field(..., description="Unique student identifier")
    grade_level: GradeLevel = Field(..., description="Student's grade level")
    language: LanguageCode = Field(default=LanguageCode.ENGLISH, description="Preferred language")
    input_type: str = Field(..., description="Type of input: text, image, voice")
    context: Optional[str] = Field(None, description="Additional context for processing")

class ImageUploadRequest(MultiModalRequest):
    """Request model for image upload processing"""
    input_type: str = Field(default="image", description="Input type is image")
    image_data: str = Field(..., description="Base64 encoded image data")
    image_format: str = Field(..., description="Image format (jpg, png, etc.)")

class VoiceUploadRequest(MultiModalRequest):
    """Request model for voice upload processing"""
    input_type: str = Field(default="voice", description="Input type is voice")
    audio_data: str = Field(..., description="Base64 encoded audio data")
    audio_format: str = Field(..., description="Audio format (wav, mp3, etc.)")

class VideoRequest(BaseModel):
    """Request model for video generation endpoint"""
    topic: str = Field(..., description="Topic for video generation")
    student_id: str = Field(..., description="Unique student identifier")
    grade_level: GradeLevel = Field(..., description="Student's grade level")
    language: LanguageCode = Field(default=LanguageCode.ENGLISH, description="Video language")
    duration_preference: Optional[str] = Field("medium", description="Preferred video length")

class AssessmentRequest(BaseModel):
    """Request model for answer assessment"""
    question: str = Field(..., description="Original question")
    answer: str = Field(..., description="Student's answer")
    student_id: str = Field(..., description="Unique student identifier")
    expected_answer: Optional[str] = Field(None, description="Expected correct answer")

# Animation and Board Script Models
class BoardStep(BaseModel):
    """Single step in the animated blackboard"""
    step: int = Field(..., description="Step number in sequence")
    content: str = Field(..., description="Content to display")
    type: str = Field(..., description="Type: title, body, equation, highlight, diagram")
    draw_duration_ms: int = Field(default=1000, description="Animation duration in milliseconds")
    position: Optional[Dict[str, float]] = Field(None, description="Position coordinates")
    style: Optional[Dict[str, Any]] = Field(None, description="Styling options")

class BoardScript(BaseModel):
    """Complete animated blackboard script"""
    steps: List[BoardStep] = Field(..., description="Sequence of animation steps")
    total_duration_ms: int = Field(..., description="Total animation duration")
    background_color: str = Field(default="#000000", description="Background color")
    text_color: str = Field(default="#FFFFFF", description="Text color")

# Response Models
class ExplanationResponse(BaseModel):
    """Response model for explanation endpoint"""
    explanation_text: str = Field(..., description="Main explanation text")
    board_script: BoardScript = Field(..., description="Animated blackboard script")
    difficulty_level: str = Field(..., description="Detected difficulty level")
    key_concepts: List[str] = Field(..., description="Key concepts covered")
    follow_up_questions: List[str] = Field(default_factory=list, description="Suggested follow-up questions")
    confidence_score: float = Field(..., description="AI confidence in explanation (0-1)")
    timestamp: datetime = Field(default_factory=datetime.now, description="Response timestamp")

class VideoResponse(BaseModel):
    """Response model for video generation endpoint"""
    video_url: str = Field(..., description="URL to access the generated video")
    video_id: str = Field(..., description="Unique video identifier")
    topic: str = Field(..., description="Video topic")
    duration_seconds: Optional[float] = Field(None, description="Video duration in seconds")
    file_size_mb: Optional[float] = Field(None, description="Video file size in MB")
    manim_script: Optional[str] = Field(None, description="Generated Manim script")
    generation_time_seconds: Optional[float] = Field(None, description="Time taken to generate")
    timestamp: datetime = Field(default_factory=datetime.now, description="Generation timestamp")

class AssessmentResponse(BaseModel):
    """Response model for answer assessment"""
    is_correct: bool = Field(..., description="Whether the answer is correct")
    confidence_score: float = Field(..., description="Confidence in assessment (0-1)")
    feedback: str = Field(..., description="Feedback for the student")
    mistakes_identified: List[str] = Field(default_factory=list, description="Specific mistakes found")
    suggestions: List[str] = Field(default_factory=list, description="Suggestions for improvement")
    next_explanation_style: Optional[str] = Field(None, description="Recommended explanation style")
    timestamp: datetime = Field(default_factory=datetime.now, description="Assessment timestamp")

class ProcessedInputResponse(BaseModel):
    """Response model for processed multimodal input"""
    success: bool = Field(..., description="Whether processing was successful")
    input_type: str = Field(..., description="Type of input processed")
    normalized_text: str = Field(..., description="Cleaned and normalized text")
    detected_language: str = Field(..., description="Detected language code")
    confidence_score: float = Field(..., description="Processing confidence (0-1)")
    math_expressions: List[str] = Field(default_factory=list, description="Extracted mathematical expressions")
    processing_time_ms: float = Field(..., description="Processing time in milliseconds")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    original_content: Optional[str] = Field(None, description="Original content (text/transcription)")
    error: Optional[str] = Field(None, description="Error message if processing failed")

# Student Profile and Memory Models
class ConceptMastery(BaseModel):
    """Mastery level for a specific concept"""
    concept: str = Field(..., description="Concept name")
    mastery_level: float = Field(..., ge=0.0, le=1.0, description="Mastery level (0-1)")
    last_practiced: datetime = Field(default_factory=datetime.now, description="Last practice date")
    practice_count: int = Field(default=0, description="Number of times practiced")

class LearningSession(BaseModel):
    """Record of a learning session"""
    session_id: str = Field(..., description="Unique session identifier")
    timestamp: datetime = Field(default_factory=datetime.now, description="Session timestamp")
    questions_asked: List[str] = Field(default_factory=list, description="Questions in this session")
    topics_covered: List[str] = Field(default_factory=list, description="Topics covered")
    time_spent_minutes: int = Field(default=0, description="Time spent in minutes")
    engagement_score: float = Field(default=0.5, ge=0.0, le=1.0, description="Engagement level")

class StudentProfile(BaseModel):
    """Complete student profile"""
    student_id: str = Field(..., description="Unique student identifier")
    grade_level: GradeLevel = Field(..., description="Current grade level")
    preferred_language: LanguageCode = Field(default=LanguageCode.ENGLISH)
    learning_style: LearningStyle = Field(default=LearningStyle.MIXED)
    
    # Learning preferences
    explanation_style_preference: str = Field(default="balanced", description="Preferred explanation style")
    difficulty_preference: str = Field(default="adaptive", description="Preferred difficulty level")
    
    # Performance tracking
    concept_mastery: List[ConceptMastery] = Field(default_factory=list)
    learning_sessions: List[LearningSession] = Field(default_factory=list)
    
    # Adaptive features
    confusion_patterns: Dict[str, int] = Field(default_factory=dict, description="Common confusion areas")
    success_patterns: Dict[str, int] = Field(default_factory=dict, description="Success patterns")
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    total_sessions: int = Field(default=0)
    total_questions: int = Field(default=0)

# Error Models
class ErrorResponse(BaseModel):
    """Standard error response"""
    error: str = Field(..., description="Error type")
    message: str = Field(..., description="Error message")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional error details")
    timestamp: datetime = Field(default_factory=datetime.now)

# SDK Models
class SDKHealthCheck(BaseModel):
    """SDK health check response"""
    status: str = Field(..., description="Service status")
    version: str = Field(..., description="API version")
    services: Dict[str, bool] = Field(..., description="Service availability")
    timestamp: datetime = Field(default_factory=datetime.now)

class VideoGenerationStatus(BaseModel):
    """Video generation status for async operations"""
    video_id: str = Field(..., description="Video generation ID")
    status: str = Field(..., description="Generation status: queued, processing, completed, failed")
    progress_percentage: float = Field(default=0.0, ge=0.0, le=100.0, description="Progress percentage")
    estimated_completion_seconds: Optional[int] = Field(None, description="Estimated time to completion")
    error_message: Optional[str] = Field(None, description="Error message if failed")
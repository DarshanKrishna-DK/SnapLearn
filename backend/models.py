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
    KANNADA = "kn"

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
    duration_preference: Optional[str] = Field("medium", description="Deprecated: use target_duration_minutes")
    target_duration_minutes: float = Field(
        5.0,
        ge=0.5,
        le=15.0,
        description="Target lesson length in minutes (Manim pacing + TTS). Clamped 0.5-15.",
    )
    enable_tts: bool = Field(True, description="Synthesize spoken narration and mux with ffmpeg if available")
    extra_context: Optional[str] = Field(
        None,
        description="Optional extra instructions or class context for the script and narration",
    )

class ContextualVideoRequest(BaseModel):
    """Request model for contextual video generation"""
    topic: str = Field(..., description="Topic for video generation")
    student_id: str = Field(..., description="Unique student identifier")
    grade_level: GradeLevel = Field(..., description="Student's grade level")
    language: LanguageCode = Field(default=LanguageCode.ENGLISH, description="Video language")
    conversation_context: Optional[Dict[str, Any]] = Field(None, description="Conversation context payload")
    video_quality: str = Field(default="high", description="Video quality setting")
    video_format: str = Field(default="mp4", description="Video format")
    animation_style: str = Field(default="modern", description="Animation style")
    target_duration: int = Field(default=180, description="Target video duration in seconds")

class AssessmentRequest(BaseModel):
    """Request model for answer assessment"""
    question: str = Field(..., description="Original question")
    answer: str = Field(..., description="Student's answer")
    student_id: str = Field(..., description="Unique student identifier")
    expected_answer: Optional[str] = Field(None, description="Expected correct answer")

# Animation and Board Script Models
class MermaidDiagram(BaseModel):
    """Mermaid diagram for visual representation"""
    title: str = Field(..., description="Diagram title")
    description: str = Field(..., description="What this diagram shows")
    mermaid_code: str = Field(..., description="Mermaid diagram code")
    diagram_type: str = Field(..., description="Type: flowchart, sequence, mindmap, timeline, class, state")

class BoardStep(BaseModel):
    """Single step in the animated blackboard"""
    step: int = Field(..., description="Step number in sequence")
    content: str = Field(..., description="Content to display")
    type: str = Field(..., description="Type: title, body, equation, highlight, diagram, mermaid")
    mermaid_code: Optional[str] = Field(None, description="Mermaid diagram code for this step")
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
    mermaid_diagrams: List[MermaidDiagram] = Field(default_factory=list, description="Visual Mermaid diagrams")
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
    has_audio: bool = Field(default=False, description="Whether TTS was muxed into the MP4")
    tts_engine: Optional[str] = Field(None, description="TTS engine used, e.g. edge-tts or gtts")
    narration_preview: Optional[str] = Field(
        None,
        description="Short preview of the narration that was or would be spoken",
    )

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

# Phase 3 Models - Advanced Tutoring and Adaptive Learning

class ConversationRequest(BaseModel):
    """Request to start or continue a conversation"""
    student_id: str = Field(..., description="Unique student identifier")
    input_text: str = Field(..., description="Student input text")
    conversation_id: Optional[str] = Field(None, description="Existing conversation ID to continue")
    input_type: str = Field(default="question", description="Type of input: question, answer, clarification")
    context: Optional[str] = Field(None, description="Additional context")

class ConversationResponse(BaseModel):
    """Response from conversation engine"""
    conversation_id: str = Field(..., description="Unique conversation identifier")
    response: ExplanationResponse = Field(..., description="AI tutor response")
    state: str = Field(..., description="Current conversation state")
    turn_count: int = Field(..., description="Number of turns in conversation")
    learning_insights: Dict[str, Any] = Field(..., description="Insights about learning progress")
    recommendations: List[str] = Field(default_factory=list, description="Study recommendations")
    next_action: Optional[str] = Field(None, description="Suggested next action")

class AssessmentAnalytics(BaseModel):
    """Advanced assessment analytics"""
    student_id: str = Field(..., description="Student identifier")
    total_assessments: int = Field(..., description="Total number of assessments")
    accuracy_trend: List[float] = Field(..., description="Accuracy over time")
    mistake_patterns: Dict[str, int] = Field(..., description="Frequency of mistake types")
    improvement_areas: List[str] = Field(..., description="Areas needing improvement")
    strengths: List[str] = Field(..., description="Identified strengths")
    intervention_recommendations: List[str] = Field(..., description="Recommended interventions")

class DifficultyAdaptationRequest(BaseModel):
    """Request for difficulty adaptation analysis"""
    student_id: str = Field(..., description="Student identifier")
    current_difficulty: str = Field(..., description="Current difficulty level")
    recent_performance: Dict[str, Any] = Field(..., description="Recent performance data")
    topic: str = Field(..., description="Current topic")

class DifficultyAdaptationResponse(BaseModel):
    """Response with difficulty adaptation recommendations"""
    recommended_difficulty: str = Field(..., description="Recommended difficulty level")
    adaptation_reason: str = Field(..., description="Reason for adaptation")
    confidence: float = Field(..., description="Confidence in recommendation")
    adapted_content: Dict[str, Any] = Field(..., description="Content adapted to new difficulty")
    teaching_strategies: List[str] = Field(..., description="Recommended teaching strategies")

class LearningPathRequest(BaseModel):
    """Request for learning path optimization"""
    student_id: str = Field(..., description="Student identifier")
    target_topics: List[str] = Field(..., description="Topics to learn")
    time_available: int = Field(..., description="Available time in minutes")
    preferences: Dict[str, Any] = Field(default_factory=dict, description="Learning preferences")

class LearningPathResponse(BaseModel):
    """Optimized learning path response"""
    path_id: str = Field(..., description="Learning path identifier")
    recommended_sequence: List[Dict[str, Any]] = Field(..., description="Ordered learning sequence")
    estimated_duration: int = Field(..., description="Estimated completion time in minutes")
    difficulty_progression: List[str] = Field(..., description="Difficulty level progression")
    checkpoint_assessments: List[Dict[str, Any]] = Field(..., description="Assessment checkpoints")
    personalization_notes: List[str] = Field(..., description="Personalization explanations")

class ConfusionDetectionRequest(BaseModel):
    """Request for real-time confusion detection"""
    student_id: str = Field(..., description="Student identifier")
    interaction_data: Dict[str, Any] = Field(..., description="Real-time interaction data")
    response_time: float = Field(..., description="Response time in seconds")
    response_text: str = Field(..., description="Student response text")

class ConfusionDetectionResponse(BaseModel):
    """Confusion detection analysis response"""
    confusion_detected: bool = Field(..., description="Whether confusion is detected")
    confidence_score: float = Field(..., description="Confidence in detection")
    confusion_indicators: List[str] = Field(..., description="Specific indicators of confusion")
    intervention_needed: bool = Field(..., description="Whether immediate intervention is needed")
    suggested_interventions: List[str] = Field(..., description="Suggested intervention strategies")
    emotion_analysis: Dict[str, float] = Field(default_factory=dict, description="Detected emotional states")

class ExplanationStyleRequest(BaseModel):
    """Request for explanation style adaptation"""
    student_id: str = Field(..., description="Student identifier")
    topic: str = Field(..., description="Topic to explain")
    current_style: str = Field(..., description="Current explanation style")
    adaptation_reason: str = Field(..., description="Reason for style change")
    target_style: str = Field(..., description="Target explanation style")

class ExplanationStyleResponse(BaseModel):
    """Response with adapted explanation style"""
    adapted_explanation: ExplanationResponse = Field(..., description="Explanation in new style")
    style_comparison: Dict[str, str] = Field(..., description="Comparison of styles")
    effectiveness_prediction: float = Field(..., description="Predicted effectiveness of new style")

class ParentDashboardData(BaseModel):
    """Data for parent/teacher dashboard"""
    student_id: str = Field(..., description="Student identifier")
    learning_summary: Dict[str, Any] = Field(..., description="Overall learning summary")
    recent_activities: List[Dict[str, Any]] = Field(..., description="Recent learning activities")
    progress_metrics: Dict[str, float] = Field(..., description="Progress metrics")
    areas_of_strength: List[str] = Field(..., description="Student strengths")
    areas_needing_support: List[str] = Field(..., description="Areas needing support")
    recommendations_for_parents: List[str] = Field(..., description="Recommendations for parents")
    time_spent_learning: int = Field(..., description="Total time spent learning in minutes")
    engagement_trend: List[float] = Field(..., description="Engagement levels over time")

class StudyRecommendationRequest(BaseModel):
    """Request for AI-powered study recommendations"""
    student_id: str = Field(..., description="Student identifier")
    available_time: int = Field(..., description="Available study time in minutes")
    subject_preferences: List[str] = Field(default_factory=list, description="Preferred subjects")
    difficulty_preference: str = Field(default="adaptive", description="Preferred difficulty")

class StudyRecommendationResponse(BaseModel):
    """AI-powered study recommendations"""
    recommended_activities: List[Dict[str, Any]] = Field(..., description="Recommended study activities")
    personalized_schedule: Dict[str, Any] = Field(..., description="Personalized study schedule")
    focus_areas: List[str] = Field(..., description="Areas to focus on")
    estimated_improvement: Dict[str, float] = Field(..., description="Estimated improvement predictions")
    motivational_message: str = Field(..., description="Personalized motivational message")
    reminder_suggestions: List[str] = Field(..., description="Study reminder suggestions")

# Analytics and Reporting Models
class LearningAnalytics(BaseModel):
    """Comprehensive learning analytics"""
    student_id: str = Field(..., description="Student identifier")
    time_period: str = Field(..., description="Analytics time period")
    total_sessions: int = Field(..., description="Total learning sessions")
    total_time_minutes: int = Field(..., description="Total time spent learning")
    concepts_mastered: List[str] = Field(..., description="Concepts mastered in period")
    accuracy_metrics: Dict[str, float] = Field(..., description="Accuracy metrics by topic")
    engagement_metrics: Dict[str, float] = Field(..., description="Engagement metrics")
    difficulty_progression: List[Dict[str, Any]] = Field(..., description="Difficulty level changes")
    learning_velocity: float = Field(..., description="Rate of learning progress")
    prediction_models: Dict[str, Any] = Field(..., description="Predictive analytics")

# Phase 4 Models - Enhanced Video Generation & Analytics

class LearningPathRequest(BaseModel):
    """Request for creating a learning path"""
    student_id: str = Field(..., description="Student identifier")
    target_topics: List[str] = Field(..., description="Topics to include in learning path")
    time_available: int = Field(..., description="Available time in minutes")
    preferences: Dict[str, Any] = Field(default_factory=dict, description="Learning preferences")

class LearningPathResponse(BaseModel):
    """Response containing optimized learning path"""
    path_id: str = Field(..., description="Unique path identifier")
    recommended_sequence: List[Dict[str, Any]] = Field(..., description="Recommended topic sequence")
    estimated_duration: int = Field(..., description="Estimated total duration in minutes")
    difficulty_progression: List[str] = Field(..., description="Difficulty level progression")
    checkpoint_assessments: List[Dict[str, Any]] = Field(default_factory=list, description="Assessment checkpoints")
    personalization_notes: List[str] = Field(default_factory=list, description="Personalization explanations")

class VideoGenerationRequest(BaseModel):
    """Request for contextual video generation"""
    topic: str = Field(..., description="Video topic")
    student_id: str = Field(..., description="Student identifier") 
    grade_level: str = Field(..., description="Student grade level")
    language: Optional[str] = Field(default="en", description="Video language")
    conversation_context: Optional[Dict[str, Any]] = Field(default=None, description="Conversation context")
    video_quality: Optional[str] = Field(default="high", description="Video quality setting")
    video_format: Optional[str] = Field(default="mp4", description="Video format")
    animation_style: Optional[str] = Field(default="modern", description="Animation style")
    target_duration: Optional[int] = Field(default=180, description="Target duration in seconds")

class EnhancedVideoResponse(BaseModel):
    """Enhanced video generation response with Phase 4 features"""
    video_url: str = Field(..., description="Video file URL")
    video_id: str = Field(..., description="Unique video identifier")
    topic: str = Field(..., description="Video topic")
    duration_seconds: Optional[float] = Field(None, description="Video duration in seconds")
    file_size_mb: Optional[float] = Field(None, description="Video file size in MB")
    manim_script: str = Field(..., description="Generated Manim script")
    generation_time_seconds: float = Field(..., description="Time taken to generate video")
    timestamp: Optional[datetime] = Field(default_factory=datetime.now, description="Creation timestamp")
    
    # Phase 4 Enhancements
    video_variants: Optional[List[Dict[str, Any]]] = Field(default_factory=list, description="Alternative quality/format versions")
    thumbnail_url: Optional[str] = Field(None, description="Video thumbnail URL")
    learning_context: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Learning context used")
    script_metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Script analysis metadata")
    animation_style: Optional[str] = Field(None, description="Applied animation style")
    difficulty_level: Optional[str] = Field(None, description="Content difficulty level")
    personalization_applied: Optional[List[str]] = Field(default_factory=list, description="Applied personalizations")
    video_analytics: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Initial video analytics")
    conceptual_map: Optional[List[str]] = Field(default_factory=list, description="Concepts covered in video")
    interactive_elements: Optional[List[str]] = Field(default_factory=list, description="Interactive elements included")

class VideoInteractionEvent(BaseModel):
    """Video interaction tracking event"""
    session_id: str = Field(..., description="Video session identifier")
    interaction_type: str = Field(..., description="Type of interaction (play, pause, seek, etc.)")
    video_position: float = Field(..., description="Position in video (seconds)")
    duration: Optional[float] = Field(None, description="Duration of interaction if applicable")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional interaction metadata")

class VideoSessionStart(BaseModel):
    """Start video session request"""
    video_id: str = Field(..., description="Video identifier")
    student_id: str = Field(..., description="Student identifier")
    video_metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Video metadata")

class VideoFeedback(BaseModel):
    """Video feedback submission"""
    video_id: str = Field(..., description="Video identifier")
    student_id: str = Field(..., description="Student identifier")
    rating: float = Field(..., ge=1, le=5, description="Video rating (1-5 stars)")
    feedback_text: Optional[str] = Field(None, description="Optional feedback text")
    improvement_suggestions: Optional[List[str]] = Field(default_factory=list, description="Improvement suggestions")

class VideoRecommendation(BaseModel):
    """Personalized video recommendation"""
    topic: str = Field(..., description="Recommended topic")
    reason: str = Field(..., description="Reason for recommendation")
    priority: str = Field(..., description="Recommendation priority (low, medium, high)")
    estimated_duration: int = Field(..., description="Estimated video duration in seconds")
    difficulty: str = Field(..., description="Content difficulty level")
    thumbnail_url: Optional[str] = Field(None, description="Recommendation thumbnail URL")
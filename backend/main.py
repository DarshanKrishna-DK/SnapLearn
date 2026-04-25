"""
SnapLearn AI - FastAPI Backend
Main application file for the adaptive tutoring engine
"""

from pathlib import Path

# Load backend/.env before imports that read os.environ. Uvicorn only loads dotenv when --env-file is passed.
_backend_dir = Path(__file__).resolve().parent
try:
    from dotenv import load_dotenv

    load_dotenv(_backend_dir / ".env")
except ImportError:
    pass

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import os
import logging
from datetime import datetime

# Import our modules
from models import (
    QuestionRequest, 
    ExplanationResponse, 
    VideoRequest, 
    VideoResponse,
    ContextualVideoRequest,
    StudentProfile,
    AssessmentRequest,
    AssessmentResponse,
    MultiModalRequest,
    ImageUploadRequest,
    VoiceUploadRequest,
    ProcessedInputResponse,
    # Phase 3 Models
    ConversationRequest,
    ConversationResponse,
    AssessmentAnalytics,
    DifficultyAdaptationRequest,
    DifficultyAdaptationResponse,
    LearningPathRequest,
    LearningPathResponse,
    ConfusionDetectionRequest,
    ConfusionDetectionResponse,
    ExplanationStyleRequest,
    ExplanationStyleResponse,
    ParentDashboardData,
    StudyRecommendationRequest,
    StudyRecommendationResponse,
    LearningAnalytics,
    # Phase 4 Models
    LearningPathRequest,
    LearningPathResponse
)
from memory import MemoryManager
from tutor_engine import TutorEngine
from manim_generator import ManimGenerator
from input_processor import InputProcessor
# Phase 3 Engines
from conversation_engine import ConversationEngine
from assessment_engine import AssessmentEngine
from adaptive_difficulty import AdaptiveDifficultyEngine
# Phase 4 Engines
from enhanced_manim_generator import EnhancedManimGenerator, VideoQuality, VideoFormat, AnimationStyle
from batch_video_generator import BatchVideoGenerator, VideoSequenceType
from video_analytics import VideoAnalytics, InteractionType
from utils import setup_logging, validate_environment

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="SnapLearn AI API",
    description="Adaptive AI Tutoring Engine with SDK capabilities",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
if not os.path.exists("../static"):
    os.makedirs("../static", exist_ok=True)
if not os.path.exists("../videos"):
    os.makedirs("../videos", exist_ok=True)

app.mount("/static", StaticFiles(directory="../static"), name="static")
app.mount("/videos", StaticFiles(directory="../videos"), name="videos")

# Initialize components
memory_manager = MemoryManager()
tutor_engine = TutorEngine()
manim_generator = ManimGenerator()
input_processor = InputProcessor()

# Phase 3 Components - Advanced Tutoring Engines
conversation_engine = ConversationEngine()
assessment_engine = AssessmentEngine()
adaptive_difficulty_engine = AdaptiveDifficultyEngine()

# Phase 4 Components - Enhanced Video Generation
enhanced_manim_generator = EnhancedManimGenerator()
batch_video_generator = BatchVideoGenerator()
video_analytics = VideoAnalytics()

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "3.0.0",
        "phase": "Phase 4 - Enhanced Video Generation & Analytics",
        "services": {
            "memory": memory_manager.is_healthy(),
            "tutor": tutor_engine.is_healthy(),
            "manim": manim_generator.is_healthy(),
            "input_processor": input_processor.is_healthy(),
            "conversation_engine": conversation_engine.is_healthy(),
            "assessment_engine": assessment_engine.is_healthy(),
            "adaptive_difficulty": adaptive_difficulty_engine.is_healthy(),
            "enhanced_manim": enhanced_manim_generator.is_healthy(),
            "batch_video_generator": batch_video_generator.is_healthy(),
            "video_analytics": video_analytics.is_healthy()
        }
    }

# Core API endpoints
@app.post("/api/explain", response_model=ExplanationResponse)
async def explain_topic(request: QuestionRequest):
    """
    Main tutoring endpoint - takes a question and returns personalized explanation
    with animated blackboard script
    """
    try:
        logger.info(f"Explain request: {request.question[:50]}...")
        
        # Get or create student profile
        student_profile = await memory_manager.get_student_profile(request.student_id)
        
        # Generate personalized explanation
        explanation = await tutor_engine.generate_explanation(
            question=request.question,
            student_profile=student_profile,
            grade_level=request.grade_level,
            language=request.language
        )
        
        # Update student memory
        await memory_manager.update_student_interaction(
            student_id=request.student_id,
            question=request.question,
            explanation=explanation.explanation_text,
            grade_level=request.grade_level
        )
        
        return explanation
        
    except Exception as e:
        logger.error(f"Error in explain_topic: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/generate-video", response_model=VideoResponse)
async def generate_video(request: VideoRequest, background_tasks: BackgroundTasks):
    """
    Generate Manim video for a topic - runs locally as subprocess
    """
    try:
        logger.info(f"Video generation request: {request.topic[:50]}...")
        
        # Get student profile for context
        student_profile = await memory_manager.get_student_profile(request.student_id)
        
        # Generate video
        video_result = await manim_generator.generate_video(
            topic=request.topic,
            grade_level=request.grade_level,
            student_profile=student_profile,
            language=request.language
        )
        
        # Log video generation
        await memory_manager.log_video_generation(
            student_id=request.student_id,
            topic=request.topic,
            video_path=video_result.video_url
        )
        
        return video_result
        
    except Exception as e:
        logger.error(f"Error in generate_video: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/assess", response_model=AssessmentResponse)
async def assess_answer(request: AssessmentRequest):
    """
    Assess student's answer and provide feedback
    """
    try:
        logger.info(f"Assessment request for student {request.student_id}")
        
        # Get student profile
        student_profile = await memory_manager.get_student_profile(request.student_id)
        
        # Assess the answer
        assessment = await tutor_engine.assess_answer(
            question=request.question,
            student_answer=request.answer,
            student_profile=student_profile
        )
        
        # Update student memory with assessment
        await memory_manager.update_student_assessment(
            student_id=request.student_id,
            question=request.question,
            answer=request.answer,
            assessment=assessment
        )
        
        return assessment
        
    except Exception as e:
        logger.error(f"Error in assess_answer: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/student/{student_id}/profile")
async def get_student_profile(student_id: str):
    """Get student profile and learning history"""
    try:
        profile = await memory_manager.get_student_profile(student_id)
        return {
            "student_id": student_id,
            "profile": profile.dict() if profile else None,
            "recent_topics": await memory_manager.get_recent_topics(student_id),
            "learning_stats": await memory_manager.get_learning_stats(student_id)
        }
    except Exception as e:
        logger.error(f"Error getting student profile: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/student/{student_id}/videos")
async def get_student_videos(student_id: str):
    """Get list of videos generated for this student"""
    try:
        videos = await memory_manager.get_student_videos(student_id)
        return {"videos": videos}
    except Exception as e:
        logger.error(f"Error getting student videos: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Phase 2: Multimodal Input Endpoints
@app.post("/api/process-image", response_model=ProcessedInputResponse)
async def process_image_input(request: ImageUploadRequest):
    """
    Process image input (OCR, math problem extraction, etc.)
    """
    try:
        logger.info(f"Processing image input for student {request.student_id}")
        
        # Decode base64 image data
        import base64
        image_data = base64.b64decode(request.image_data)
        
        # Process the image
        result = await input_processor.process_input(
            input_data=image_data,
            input_type="image",
            student_id=request.student_id,
            context=request.context
        )
        
        # Log the processing result
        await memory_manager.update_student_interaction(
            student_id=request.student_id,
            question=f"Image input: {result.get('normalized_text', 'No text extracted')}",
            explanation="Image processed for text extraction",
            grade_level=request.grade_level.value
        )
        
        return ProcessedInputResponse(**result)
        
    except Exception as e:
        logger.error(f"Error processing image input: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/process-voice", response_model=ProcessedInputResponse)
async def process_voice_input(request: VoiceUploadRequest):
    """
    Process voice input (speech-to-text conversion)
    """
    try:
        logger.info(f"Processing voice input for student {request.student_id}")
        
        # Decode base64 audio data
        import base64
        audio_data = base64.b64decode(request.audio_data)
        
        # Process the audio
        result = await input_processor.process_input(
            input_data=audio_data,
            input_type="voice",
            student_id=request.student_id,
            context=request.context
        )
        
        # Log the processing result
        await memory_manager.update_student_interaction(
            student_id=request.student_id,
            question=f"Voice input: {result.get('normalized_text', 'No speech recognized')}",
            explanation="Voice processed for speech-to-text",
            grade_level=request.grade_level.value
        )
        
        return ProcessedInputResponse(**result)
        
    except Exception as e:
        logger.error(f"Error processing voice input: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/process-text", response_model=ProcessedInputResponse)
async def process_text_input(request: MultiModalRequest):
    """
    Process and normalize text input (language detection, math extraction)
    """
    try:
        logger.info(f"Processing text input for student {request.student_id}")
        
        # Get text from context or create a sample
        text_content = request.context or "Sample text for processing"
        
        # Process the text
        result = await input_processor.process_input(
            input_data=text_content,
            input_type="text",
            student_id=request.student_id,
            context=request.context
        )
        
        return ProcessedInputResponse(**result)
        
    except Exception as e:
        logger.error(f"Error processing text input: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Phase 3 Endpoints - Advanced AI Tutoring Features

@app.post("/api/conversation/start", response_model=ConversationResponse)
async def start_conversation(request: ConversationRequest):
    """
    Start a new multi-turn tutoring conversation with context awareness
    """
    try:
        logger.info(f"Starting conversation for student {request.student_id}")
        
        # Get student profile
        student_profile = await memory_manager.get_student_profile(request.student_id)
        
        # Start conversation
        conversation_result = await conversation_engine.start_conversation(
            student_id=request.student_id,
            initial_question=request.input_text,
            student_profile=student_profile,
            context=request.context
        )
        
        # Create response
        conversation_response = ConversationResponse(
            conversation_id=conversation_result["conversation_id"],
            response=conversation_result["response"],
            state=conversation_result["state"],
            turn_count=conversation_result["turn_count"],
            learning_insights=conversation_result["learning_insights"],
            recommendations=[]
        )
        
        return conversation_response
        
    except Exception as e:
        logger.error(f"Error starting conversation: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/conversation/continue", response_model=ConversationResponse)
async def continue_conversation(request: ConversationRequest):
    """
    Continue an existing multi-turn conversation
    """
    try:
        logger.info(f"Continuing conversation {request.conversation_id}")
        
        if not request.conversation_id:
            raise HTTPException(status_code=400, detail="Conversation ID required to continue")
        
        # Continue conversation
        conversation_result = await conversation_engine.continue_conversation(
            conversation_id=request.conversation_id,
            student_input=request.input_text,
            input_type=request.input_type
        )
        
        # Create response
        conversation_response = ConversationResponse(
            conversation_id=conversation_result["conversation_id"],
            response=conversation_result["response"],
            state=conversation_result["state"],
            turn_count=conversation_result["turn_count"],
            learning_insights=conversation_result["learning_insights"],
            recommendations=conversation_result.get("recommendations", []),
            next_action=conversation_result.get("analysis", {}).get("next_action")
        )
        
        return conversation_response
        
    except Exception as e:
        logger.error(f"Error continuing conversation: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/assessment/comprehensive")
async def comprehensive_assessment(request: AssessmentRequest):
    """
    Advanced assessment with mistake pattern detection and adaptive feedback
    """
    try:
        logger.info(f"Comprehensive assessment for student {request.student_id}")
        
        # Get student profile
        student_profile = await memory_manager.get_student_profile(request.student_id)
        
        # Perform comprehensive assessment
        assessment_result = await assessment_engine.assess_comprehensive(
            student_id=request.student_id,
            question=request.question,
            student_answer=request.answer,
            student_profile=student_profile
        )
        
        return assessment_result
        
    except Exception as e:
        logger.error(f"Error in comprehensive assessment: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/assessment/analytics/{student_id}", response_model=AssessmentAnalytics)
async def get_assessment_analytics(student_id: str):
    """
    Get comprehensive assessment analytics and mistake patterns for a student
    """
    try:
        analytics = await assessment_engine.get_student_assessment_analytics(student_id)
        
        # Convert to response model
        assessment_analytics = AssessmentAnalytics(
            student_id=student_id,
            total_assessments=analytics.get("total_assessments", 0),
            accuracy_trend=[],  # Will be populated with historical data
            mistake_patterns=analytics.get("most_common_mistakes", {}),
            improvement_areas=analytics.get("improvement_areas", []),
            strengths=analytics.get("strengths", []),
            intervention_recommendations=analytics.get("recommendations", [])
        )
        
        return assessment_analytics
        
    except Exception as e:
        logger.error(f"Error getting assessment analytics: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/difficulty/adapt", response_model=DifficultyAdaptationResponse)
async def adapt_difficulty(request: DifficultyAdaptationRequest):
    """
    Adapt content difficulty based on student performance
    """
    try:
        logger.info(f"Adapting difficulty for student {request.student_id}")
        
        # Get student profile
        student_profile = await memory_manager.get_student_profile(request.student_id)
        
        # Assess current performance
        recent_responses = request.recent_performance.get("responses", [])
        session_data = request.recent_performance.get("session", {})
        
        performance_metrics = await adaptive_difficulty_engine.assess_current_performance(
            student_id=request.student_id,
            recent_responses=recent_responses,
            session_data=session_data
        )
        
        # Determine optimal difficulty
        new_difficulty, trigger, reason = await adaptive_difficulty_engine.determine_optimal_difficulty(
            student_id=request.student_id,
            current_difficulty=request.current_difficulty,
            performance_metrics=performance_metrics,
            student_profile=student_profile
        )
        
        # Generate adapted content if difficulty changed
        adapted_content = {}
        if new_difficulty != request.current_difficulty:
            adapted_content = await adaptive_difficulty_engine.adapt_content_difficulty(
                student_id=request.student_id,
                topic=request.topic,
                current_difficulty=request.current_difficulty,
                new_difficulty=new_difficulty,
                student_profile=student_profile
            )
        
        # Get teaching strategies
        recommendations = await adaptive_difficulty_engine.get_adaptation_recommendations(
            student_id=request.student_id,
            current_performance=performance_metrics,
            student_profile=student_profile
        )
        
        return DifficultyAdaptationResponse(
            recommended_difficulty=new_difficulty,
            adaptation_reason=reason,
            confidence=0.85,
            adapted_content=adapted_content,
            teaching_strategies=recommendations.get("teaching_strategies", [])
        )
        
    except Exception as e:
        logger.error(f"Error adapting difficulty: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/learning-path/optimize", response_model=LearningPathResponse)
async def optimize_learning_path(request: LearningPathRequest):
    """
    Generate optimized learning path based on student profile and goals
    """
    try:
        logger.info(f"Optimizing learning path for student {request.student_id}")
        
        # Get student profile
        student_profile = await memory_manager.get_student_profile(request.student_id)
        
        # Generate learning path using AI
        from google import genai
        client = genai.Client()
        
        learning_path_prompt = f"""Create an optimized learning path for this student:

STUDENT PROFILE:
- Grade Level: {student_profile.grade_level.value}
- Learning Style: {student_profile.learning_style.value}
- Strengths: {list(student_profile.success_patterns.keys())[:3]}
- Challenge Areas: {list(student_profile.confusion_patterns.keys())[:3]}

TARGET TOPICS: {', '.join(request.target_topics)}
AVAILABLE TIME: {request.time_available} minutes
PREFERENCES: {request.preferences}

Generate an optimized learning sequence in JSON format:
{{
  "recommended_sequence": [
    {{"topic": "Topic 1", "duration_minutes": 15, "difficulty": "easy", "activities": ["activity1"]}},
    {{"topic": "Topic 2", "duration_minutes": 20, "difficulty": "medium", "activities": ["activity2"]}}
  ],
  "difficulty_progression": ["easy", "medium", "hard"],
  "checkpoint_assessments": [
    {{"after_topic": "Topic 1", "assessment_type": "quick_check"}},
    {{"after_topic": "Topic 2", "assessment_type": "comprehensive"}}
  ],
  "personalization_notes": ["reason1", "reason2"]
}}"""

        from google.genai import types
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=learning_path_prompt,
            config=types.GenerateContentConfig(
                temperature=0.7,
                max_output_tokens=1024
            )
        )
        
        import json
        response_text = response.text
        
        # Parse JSON response
        try:
            if response_text.strip().startswith('{'):
                learning_path_data = json.loads(response_text)
            else:
                import re
                json_match = re.search(r'```json\s*(\{.*?\})\s*```', response_text, re.DOTALL)
                if json_match:
                    learning_path_data = json.loads(json_match.group(1))
                else:
                    raise ValueError("Could not parse JSON response")
        except:
            # Fallback path
            learning_path_data = {
                "recommended_sequence": [{"topic": topic, "duration_minutes": request.time_available // len(request.target_topics), "difficulty": "medium"} for topic in request.target_topics],
                "difficulty_progression": ["medium"] * len(request.target_topics),
                "checkpoint_assessments": [],
                "personalization_notes": ["Adaptive path generated based on student profile"]
            }
        
        # Calculate estimated duration
        estimated_duration = sum(item.get("duration_minutes", 0) for item in learning_path_data.get("recommended_sequence", []))
        
        return LearningPathResponse(
            path_id=f"path_{request.student_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            recommended_sequence=learning_path_data.get("recommended_sequence", []),
            estimated_duration=estimated_duration,
            difficulty_progression=learning_path_data.get("difficulty_progression", []),
            checkpoint_assessments=learning_path_data.get("checkpoint_assessments", []),
            personalization_notes=learning_path_data.get("personalization_notes", [])
        )
        
    except Exception as e:
        logger.error(f"Error optimizing learning path: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/confusion/detect", response_model=ConfusionDetectionResponse)
async def detect_confusion(request: ConfusionDetectionRequest):
    """
    Real-time confusion detection and intervention recommendations
    """
    try:
        logger.info(f"Detecting confusion for student {request.student_id}")
        
        # Analyze confusion indicators
        confusion_indicators = []
        confusion_detected = False
        confidence_score = 0.0
        
        # Response time analysis
        if request.response_time > 60:  # More than 1 minute
            confusion_indicators.append("Unusually long response time")
            confusion_detected = True
            confidence_score += 0.3
        
        # Text analysis
        confusion_words = ["confused", "don't understand", "help", "stuck", "lost", "unclear", "what?", "huh?"]
        if any(word in request.response_text.lower() for word in confusion_words):
            confusion_indicators.append("Explicit confusion expressions")
            confusion_detected = True
            confidence_score += 0.5
        
        # Short responses might indicate confusion
        if len(request.response_text.strip()) < 10 and request.response_time > 30:
            confusion_indicators.append("Very short response after long thinking time")
            confusion_detected = True
            confidence_score += 0.2
        
        # Generate interventions
        suggested_interventions = []
        if confusion_detected:
            suggested_interventions.extend([
                "Provide simpler explanation",
                "Break down into smaller steps",
                "Use visual aids or examples",
                "Ask guiding questions",
                "Offer alternative approach"
            ])
        
        # Emotion analysis (simplified)
        emotion_analysis = {
            "frustration": 0.3 if confusion_detected else 0.1,
            "confusion": confidence_score,
            "engagement": max(0.2, 0.8 - confidence_score)
        }
        
        return ConfusionDetectionResponse(
            confusion_detected=confusion_detected,
            confidence_score=min(1.0, confidence_score),
            confusion_indicators=confusion_indicators,
            intervention_needed=confidence_score > 0.5,
            suggested_interventions=suggested_interventions[:3],
            emotion_analysis=emotion_analysis
        )
        
    except Exception as e:
        logger.error(f"Error detecting confusion: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/dashboard/parent/{student_id}", response_model=ParentDashboardData)
async def get_parent_dashboard(student_id: str, days: int = 7):
    """
    Get parent/teacher dashboard with learning insights and progress
    """
    try:
        logger.info(f"Generating parent dashboard for student {student_id}")
        
        # Get student profile and learning data
        student_profile = await memory_manager.get_student_profile(student_id)
        learning_stats = await memory_manager.get_learning_stats(student_id)
        recent_topics = await memory_manager.get_recent_topics(student_id)
        
        # Generate dashboard data
        dashboard_data = ParentDashboardData(
            student_id=student_id,
            learning_summary={
                "total_sessions": student_profile.total_sessions,
                "total_questions": student_profile.total_questions,
                "grade_level": student_profile.grade_level.value,
                "learning_style": student_profile.learning_style.value
            },
            recent_activities=[
                {"topic": topic, "timestamp": datetime.now().isoformat()}
                for topic in recent_topics[:5]
            ],
            progress_metrics={
                "session_frequency": learning_stats.get("sessions_per_week", 0),
                "average_session_time": learning_stats.get("avg_session_minutes", 0),
                "topic_mastery_rate": learning_stats.get("mastery_rate", 0.0)
            },
            areas_of_strength=list(student_profile.success_patterns.keys())[:3],
            areas_needing_support=list(student_profile.confusion_patterns.keys())[:3],
            recommendations_for_parents=[
                "Encourage daily 15-20 minute practice sessions",
                "Review and discuss learned concepts together",
                "Celebrate progress and effort, not just correct answers"
            ],
            time_spent_learning=sum(session.time_spent_minutes for session in student_profile.learning_sessions),
            engagement_trend=[session.engagement_score for session in student_profile.learning_sessions[-7:]]
        )
        
        return dashboard_data
        
    except Exception as e:
        logger.error(f"Error generating parent dashboard: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/recommendations/study", response_model=StudyRecommendationResponse)
async def get_study_recommendations(request: StudyRecommendationRequest):
    """
    Get AI-powered personalized study recommendations
    """
    try:
        logger.info(f"Generating study recommendations for student {request.student_id}")
        
        # Get student profile
        student_profile = await memory_manager.get_student_profile(request.student_id)
        
        # Generate recommendations using AI
        from google import genai
        client = genai.Client()
        
        recommendations_prompt = f"""Generate personalized study recommendations:

STUDENT PROFILE:
- Grade Level: {student_profile.grade_level.value}
- Learning Style: {student_profile.learning_style.value}
- Strengths: {list(student_profile.success_patterns.keys())[:3]}
- Areas for Growth: {list(student_profile.confusion_patterns.keys())[:3]}

AVAILABLE TIME: {request.available_time} minutes
SUBJECT PREFERENCES: {request.subject_preferences}
DIFFICULTY PREFERENCE: {request.difficulty_preference}

Generate recommendations in JSON format:
{{
  "recommended_activities": [
    {{"activity": "Activity name", "duration": 15, "subject": "math", "difficulty": "medium", "description": "Brief description"}}
  ],
  "personalized_schedule": {{"morning": "Activity 1", "afternoon": "Activity 2"}},
  "focus_areas": ["area1", "area2"],
  "motivational_message": "Encouraging message",
  "reminder_suggestions": ["reminder1", "reminder2"]
}}"""

        from google.genai import types
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=recommendations_prompt,
            config=types.GenerateContentConfig(
                temperature=0.7,
                max_output_tokens=1024
            )
        )
        
        import json
        response_text = response.text
        
        # Parse response
        try:
            if response_text.strip().startswith('{'):
                recommendations_data = json.loads(response_text)
            else:
                import re
                json_match = re.search(r'```json\s*(\{.*?\})\s*```', response_text, re.DOTALL)
                if json_match:
                    recommendations_data = json.loads(json_match.group(1))
                else:
                    raise ValueError("Could not parse JSON")
        except:
            # Fallback recommendations
            recommendations_data = {
                "recommended_activities": [
                    {"activity": "Math Practice", "duration": request.available_time // 2, "subject": "math", "difficulty": "medium"}
                ],
                "personalized_schedule": {"study_time": "Focus on identified weak areas"},
                "focus_areas": list(student_profile.confusion_patterns.keys())[:2],
                "motivational_message": f"Great job on your learning journey! Keep up the excellent work!",
                "reminder_suggestions": ["Set a regular study time", "Take breaks every 20 minutes"]
            }
        
        return StudyRecommendationResponse(
            recommended_activities=recommendations_data.get("recommended_activities", []),
            personalized_schedule=recommendations_data.get("personalized_schedule", {}),
            focus_areas=recommendations_data.get("focus_areas", []),
            estimated_improvement={"overall": 0.15, "focus_areas": 0.25},
            motivational_message=recommendations_data.get("motivational_message", "Keep learning!"),
            reminder_suggestions=recommendations_data.get("reminder_suggestions", [])
        )
        
    except Exception as e:
        logger.error(f"Error generating study recommendations: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/analytics/learning/{student_id}", response_model=LearningAnalytics)
async def get_learning_analytics(student_id: str, period: str = "week"):
    """
    Get comprehensive learning analytics for a student
    """
    try:
        logger.info(f"Generating learning analytics for student {student_id}")
        
        # Get student data
        student_profile = await memory_manager.get_student_profile(student_id)
        assessment_analytics = await assessment_engine.get_student_assessment_analytics(student_id)
        difficulty_analytics = await adaptive_difficulty_engine.get_difficulty_analytics(student_id)
        
        # Calculate analytics
        total_time_minutes = sum(session.time_spent_minutes for session in student_profile.learning_sessions)
        concepts_mastered = [cm.concept for cm in student_profile.concept_mastery if cm.mastery_level > 0.8]
        
        # Accuracy metrics by topic (simplified)
        accuracy_metrics = {}
        for pattern, count in student_profile.success_patterns.items():
            total_attempts = count + student_profile.confusion_patterns.get(pattern, 0)
            if total_attempts > 0:
                accuracy_metrics[pattern] = count / total_attempts
        
        # Engagement metrics
        engagement_metrics = {
            "average_engagement": sum(session.engagement_score for session in student_profile.learning_sessions) / max(len(student_profile.learning_sessions), 1),
            "session_consistency": len(student_profile.learning_sessions) / max(1, (datetime.now() - student_profile.created_at).days)
        }
        
        return LearningAnalytics(
            student_id=student_id,
            time_period=period,
            total_sessions=len(student_profile.learning_sessions),
            total_time_minutes=total_time_minutes,
            concepts_mastered=concepts_mastered,
            accuracy_metrics=accuracy_metrics,
            engagement_metrics=engagement_metrics,
            difficulty_progression=[],  # Will be populated with historical data
            learning_velocity=difficulty_analytics.get("learning_trajectory", "steady"),
            prediction_models={
                "expected_improvement": 0.15,
                "mastery_timeline": "2-3 weeks",
                "risk_factors": []
            }
        )
        
    except Exception as e:
        logger.error(f"Error generating learning analytics: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Phase 4 Endpoints - Enhanced Video Generation & Analytics

@app.post("/api/video/generate-contextual")
async def generate_contextual_video(request: ContextualVideoRequest):
    """
    Generate contextual video using Phase 4 enhanced generator with conversation context
    """
    try:
        logger.info(f"Generating contextual video for topic: {request.topic}, student: {request.student_id}")
        
        # Get student profile
        student_profile = await memory_manager.get_student_profile(request.student_id)
        
        # Convert string enums to actual enums
        quality_map = {
            "low": VideoQuality.LOW.value,
            "medium": VideoQuality.MEDIUM.value,
            "high": VideoQuality.HIGH.value,
            "ultra": VideoQuality.ULTRA.value
        }
        quality_value = quality_map.get(request.video_quality, request.video_quality)
        quality_enum = VideoQuality(quality_value)
        format_enum = VideoFormat(request.video_format)
        style_enum = AnimationStyle(request.animation_style)
        
        # Generate enhanced contextual video
        video_result = await enhanced_manim_generator.generate_contextual_video(
            topic=request.topic,
            student_profile=student_profile,
            conversation_context=request.conversation_context,
            learning_analytics=None,  # Could include learning analytics
            video_quality=quality_enum,
            video_format=format_enum,
            animation_style=style_enum,
            target_duration=request.target_duration
        )
        
        # Log video generation
        await memory_manager.log_video_generation(
            student_id=request.student_id,
            topic=request.topic,
            video_path=video_result["video_url"]
        )
        
        return video_result
        
    except Exception as e:
        logger.error(f"Error generating contextual video: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/video/batch-generate")
async def create_batch_video_generation(request: LearningPathRequest):
    """
    Create batch video generation for learning paths
    """
    try:
        logger.info(f"Creating batch video generation for student {request.student_id}")
        
        # Get student profile
        student_profile = await memory_manager.get_student_profile(request.student_id)
        
        # Create batch generation
        batch_id = await batch_video_generator.create_learning_path_videos(
            request=request,
            student_profile=student_profile,
            sequence_type=VideoSequenceType.LINEAR_PROGRESSION,
            video_settings={
                "quality": "high",
                "format": "mp4", 
                "animation_style": "modern"
            }
        )
        
        return {
            "batch_id": batch_id,
            "message": "Batch video generation started successfully",
            "estimated_completion": "15-30 minutes"
        }
        
    except Exception as e:
        logger.error(f"Error creating batch video generation: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/video/batch-status/{batch_id}")
async def get_batch_video_status(batch_id: str):
    """
    Get status of batch video generation
    """
    try:
        status = await batch_video_generator.get_batch_status(batch_id)
        
        if not status:
            raise HTTPException(status_code=404, detail="Batch not found")
        
        return status
        
    except Exception as e:
        logger.error(f"Error getting batch status: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/video/batch-cancel/{batch_id}")
async def cancel_batch_video_generation(batch_id: str):
    """
    Cancel batch video generation
    """
    try:
        success = await batch_video_generator.cancel_batch(batch_id)
        
        if not success:
            raise HTTPException(status_code=404, detail="Batch not found or cannot be cancelled")
        
        return {"message": f"Batch {batch_id} cancelled successfully"}
        
    except Exception as e:
        logger.error(f"Error cancelling batch: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/video/batch-analytics")
async def get_batch_video_analytics():
    """
    Get comprehensive batch processing analytics
    """
    try:
        analytics = await batch_video_generator.get_batch_analytics()
        return analytics
        
    except Exception as e:
        logger.error(f"Error getting batch analytics: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Video Analytics Endpoints

@app.post("/api/video/session/start")
async def start_video_session(
    video_id: str,
    student_id: str,
    video_metadata: Optional[Dict[str, Any]] = None
):
    """
    Start tracking a video viewing session
    """
    try:
        session_id = await video_analytics.start_video_session(
            video_id=video_id,
            student_id=student_id,
            video_metadata=video_metadata
        )
        
        return {
            "session_id": session_id,
            "message": "Video session started successfully"
        }
        
    except Exception as e:
        logger.error(f"Error starting video session: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/video/session/track")
async def track_video_interaction(
    session_id: str,
    interaction_type: str,
    video_position: float,
    duration: Optional[float] = None,
    metadata: Optional[Dict[str, Any]] = None
):
    """
    Track video interaction event
    """
    try:
        # Convert string to enum
        interaction_enum = InteractionType(interaction_type)
        
        success = await video_analytics.track_video_interaction(
            session_id=session_id,
            interaction_type=interaction_enum,
            video_position=video_position,
            duration=duration,
            metadata=metadata
        )
        
        if not success:
            raise HTTPException(status_code=404, detail="Session not found")
        
        return {"message": "Interaction tracked successfully"}
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid interaction type: {interaction_type}")
    except Exception as e:
        logger.error(f"Error tracking video interaction: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/video/session/end/{session_id}")
async def end_video_session(
    session_id: str,
    final_position: Optional[float] = None
):
    """
    End video viewing session and get analytics
    """
    try:
        result = await video_analytics.end_video_session(
            session_id=session_id,
            final_position=final_position
        )
        
        if not result:
            raise HTTPException(status_code=404, detail="Session not found")
        
        return result
        
    except Exception as e:
        logger.error(f"Error ending video session: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/video/analytics/{video_id}")
async def get_video_analytics_data(video_id: str):
    """
    Get comprehensive analytics for a specific video
    """
    try:
        analytics = await video_analytics.get_video_analytics(video_id)
        
        if not analytics:
            raise HTTPException(status_code=404, detail="Video analytics not found")
        
        return analytics
        
    except Exception as e:
        logger.error(f"Error getting video analytics: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/video/analytics/student/{student_id}")
async def get_student_video_analytics(student_id: str, days: int = 30):
    """
    Get video analytics for a specific student
    """
    try:
        analytics = await video_analytics.get_student_analytics(student_id, days)
        return analytics
        
    except Exception as e:
        logger.error(f"Error getting student video analytics: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Advanced Video Features

@app.post("/api/video/generate-with-style")
async def generate_video_with_style(
    topic: str,
    student_id: str,
    style_preferences: Dict[str, Any],
    quality_settings: Optional[Dict[str, Any]] = None
):
    """
    Generate video with specific style and quality preferences
    """
    try:
        logger.info(f"Generating styled video for topic: {topic}")
        
        # Get student profile
        student_profile = await memory_manager.get_student_profile(student_id)
        
        # Extract preferences
        animation_style = AnimationStyle(style_preferences.get("animation_style", "modern"))
        video_quality = VideoQuality(quality_settings.get("quality", "high") if quality_settings else "high")
        video_format = VideoFormat(quality_settings.get("format", "mp4") if quality_settings else "mp4")
        target_duration = style_preferences.get("target_duration", 180)
        
        # Generate video with style preferences
        video_result = await enhanced_manim_generator.generate_contextual_video(
            topic=topic,
            student_profile=student_profile,
            video_quality=video_quality,
            video_format=video_format,
            animation_style=animation_style,
            target_duration=target_duration
        )
        
        return video_result
        
    except Exception as e:
        logger.error(f"Error generating styled video: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/video/thumbnails/{video_id}")
async def get_video_thumbnail(video_id: str):
    """
    Get smart-generated thumbnail for a video
    """
    try:
        # Check if video exists and has thumbnail
        video_path = f"../thumbnails/{video_id}.png"
        
        if os.path.exists(video_path):
            return FileResponse(video_path, media_type="image/png")
        else:
            # Generate placeholder or return default
            raise HTTPException(status_code=404, detail="Thumbnail not found")
        
    except Exception as e:
        logger.error(f"Error getting video thumbnail: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/video/feedback")
async def submit_video_feedback(
    video_id: str,
    student_id: str,
    rating: float,
    feedback_text: Optional[str] = None,
    improvement_suggestions: Optional[List[str]] = None
):
    """
    Submit feedback for a video to improve future generations
    """
    try:
        # Store feedback (could be enhanced with database)
        feedback_data = {
            "video_id": video_id,
            "student_id": student_id,
            "rating": rating,
            "feedback_text": feedback_text,
            "improvement_suggestions": improvement_suggestions or [],
            "timestamp": datetime.now().isoformat()
        }
        
        # Could be stored in video analytics or separate feedback system
        logger.info(f"Received video feedback: {video_id} - Rating: {rating}")
        
        return {
            "message": "Feedback submitted successfully",
            "feedback_id": f"feedback_{video_id}_{student_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        }
        
    except Exception as e:
        logger.error(f"Error submitting video feedback: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/video/recommendations/{student_id}")
async def get_video_recommendations(student_id: str, limit: int = 10):
    """
    Get personalized video recommendations based on learning analytics
    """
    try:
        # Get student profile and analytics
        student_profile = await memory_manager.get_student_profile(student_id)
        learning_analytics = await adaptive_difficulty_engine.get_difficulty_analytics(student_id)
        
        # Generate recommendations based on profile
        recommendations = []
        
        # Recommend based on confusion areas
        confusion_areas = list(student_profile.confusion_patterns.keys())[:3]
        for area in confusion_areas:
            recommendations.append({
                "topic": f"Review: {area}",
                "reason": "Address confusion area",
                "priority": "high",
                "estimated_duration": 240,  # 4 minutes
                "difficulty": "easy"
            })
        
        # Recommend based on success patterns
        success_areas = list(student_profile.success_patterns.keys())[:2]
        for area in success_areas:
            recommendations.append({
                "topic": f"Advanced: {area}",
                "reason": "Build on strengths", 
                "priority": "medium",
                "estimated_duration": 300,  # 5 minutes
                "difficulty": "hard"
            })
        
        # Limit results
        recommendations = recommendations[:limit]
        
        return {
            "student_id": student_id,
            "recommendations": recommendations,
            "personalization_basis": {
                "confusion_areas": confusion_areas,
                "success_areas": success_areas,
                "learning_velocity": learning_analytics.get("learning_trajectory", "steady")
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting video recommendations: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# SDK Demo endpoints
@app.get("/sdk-demo")
async def serve_sdk_demo():
    """Serve the SDK demo HTML file"""
    demo_path = "../static/sdk_demo.html"
    if os.path.exists(demo_path):
        return FileResponse(demo_path)
    else:
        raise HTTPException(status_code=404, detail="SDK demo not found")

# Development endpoints
@app.get("/api/debug/memory")
async def debug_memory():
    """Debug endpoint to inspect memory state"""
    return await memory_manager.get_debug_info()

@app.post("/api/debug/reset/{student_id}")
async def reset_student(student_id: str):
    """Reset student profile for testing"""
    await memory_manager.reset_student_profile(student_id)
    return {"message": f"Student {student_id} profile reset"}

if __name__ == "__main__":
    import uvicorn
    
    # Validate environment before starting
    validate_environment()
    
    logger.info("Starting SnapLearn AI FastAPI server...")
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
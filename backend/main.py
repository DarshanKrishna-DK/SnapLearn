"""
SnapLearn AI - FastAPI Backend
Main application file for the adaptive tutoring engine
"""

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
    StudentProfile,
    AssessmentRequest,
    AssessmentResponse
)
from memory import MemoryManager
from tutor_engine import TutorEngine
from manim_generator import ManimGenerator
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

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0",
        "services": {
            "memory": memory_manager.is_healthy(),
            "tutor": tutor_engine.is_healthy(),
            "manim": manim_generator.is_healthy()
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
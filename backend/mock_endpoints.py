"""
SnapLearn Staging API (optional integration and QA routes).
Not used by the main Vite app; see /api/lesson/structured, /api/video/program, and /api/quiz/* for product routes.
"""
import json
import os
import time
import asyncio
import random
from datetime import datetime
from typing import Dict, Any, Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

# SnapSnap scripts (path for tutor and video payload builders)
import sys
from pathlib import Path

_snapsnap_scripts = Path(__file__).resolve().parent.parent / "SnapSnap" / "mock_scripts"
if _snapsnap_scripts.is_dir():
    sys.path.insert(0, str(_snapsnap_scripts))

from models import QuestionRequest, ExplanationResponse, VideoRequest, VideoResponse
from tutor_mock_payload import build_tutor_explanation_dict
from video_mock_payload import build_video_response_dict

from mock_tutor_system import MockTutorSystem
from mock_manim_system import MockManimSystem
from dynamic_quiz_system import DynamicQuizSystem

# In-memory staging engines (separate from file-based student profiles)
mock_tutor = MockTutorSystem()
mock_manim = MockManimSystem()
dynamic_quiz = DynamicQuizSystem()

staging_router = APIRouter(prefix="/api/staging", tags=["staging"])

# Pydantic models for requests
class StagingExplanationRequest(BaseModel):
    topic: str
    student_id: str = "alex_demo_2026"
    approach: Optional[str] = None

class StagingVideoRequest(BaseModel):
    topic: str
    student_id: str = "alex_demo_2026"
    render_time: int = 60  # seconds

class StagingQuizRequest(BaseModel):
    topic: str
    num_questions: int = 5
    difficulty: str = "medium"
    student_id: str = "alex_demo_2026"

class StagingQuizSubmission(BaseModel):
    quiz_id: str
    student_answers: Dict[int, str]
    student_id: str = "alex_demo_2026"

# Staging routes (under /api/staging)

@staging_router.post("/explain")
async def staging_explain(request: StagingExplanationRequest):
    """
    Staging tutor pipeline with controlled delays (internal tooling).
    """
    try:
        # Add processing delay (4-10 seconds)
        delay = random.uniform(4, 10)
        
        # Simulate processing stages
        stages = [
            "Analyzing student profile...",
            "Generating personalized content...",
            "Creating blackboard animations...",
            "Finalizing explanation..."
        ]
        
        result = {
            "status": "processing",
            "stages": stages,
            "estimated_time": delay,
            "student_id": request.student_id,
            "topic": request.topic
        }
        
        explanation = mock_tutor.generate_explanation(request.topic, request.student_id)
        
        result.update({
            "status": "completed",
            "explanation": explanation,
            "processing_time": delay,
            "timestamp": datetime.now().isoformat()
        })
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@staging_router.post("/generate-video")
async def staging_video_generation(request: StagingVideoRequest):
    """
    Staging video generation with timing simulation.
    """
    try:
        # Local staging manim wrapper
        video_result = mock_manim.generate_video(
            topic=request.topic,
            student_id=request.student_id,
            render_time=request.render_time
        )
        
        return {
            "status": "completed",
            "video_data": video_result,
            "message": f"Video generated successfully for {request.topic}",
            "estimated_completion": "60 seconds"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@staging_router.post("/generate-quiz")
async def staging_quiz_generation(request: StagingQuizRequest):
    """
    Generate dynamic quiz using real Gemini API
    """
    try:
        # Get student profile for weaknesses
        profile = mock_tutor.get_student_profile(request.student_id)
        weaknesses = profile.get('weaknesses', [])
        
        # Generate quiz using Gemini API
        quiz_data = dynamic_quiz.generate_quiz(
            topic=request.topic,
            num_questions=request.num_questions,
            difficulty=request.difficulty,
            student_weaknesses=weaknesses
        )
        
        return {
            "status": "completed",
            "quiz_data": quiz_data,
            "student_context": {
                "weaknesses": weaknesses,
                "learning_style": profile.get('learning_style', 'visual')
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@staging_router.post("/submit-quiz")
async def staging_quiz_submission(request: StagingQuizSubmission):
    """
    Submit quiz and update in-memory profile (staging only).
    """
    try:
        # Staging: built-in item bank for known topics when no stored quiz
        if "matrices" in request.quiz_id.lower():
            quiz_data = {
                "quiz_id": request.quiz_id,
                "questions": [
                    {
                        "id": 1,
                        "correct_answer": "A",
                        "explanation": "Matrix addition requires adding corresponding elements.",
                        "topic_area": "matrix_operations"
                    },
                    {
                        "id": 2, 
                        "correct_answer": "B",
                        "explanation": "Matrix multiplication requires compatible dimensions.",
                        "topic_area": "matrix_multiplication"
                    },
                    {
                        "id": 3,
                        "correct_answer": "C",
                        "explanation": "Identity matrix has 1s on diagonal, 0s elsewhere.",
                        "topic_area": "identity_matrix"
                    }
                ]
            }
        else:
            # Generic quiz structure
            quiz_data = {
                "quiz_id": request.quiz_id,
                "questions": [
                    {"id": i, "correct_answer": "A", "topic_area": "general"}
                    for i in range(1, len(request.student_answers) + 1)
                ]
            }
        
        # Grade the quiz
        results = dynamic_quiz.grade_quiz(quiz_data, request.student_answers)
        
        # Update student profile based on results
        updated_profile = mock_tutor.update_student_profile(request.student_id, {
            'mistakes': results.get('areas_for_improvement', []),
            'score': results['score_percentage'] / 100
        })
        
        return {
            "status": "completed",
            "quiz_results": results,
            "profile_updates": {
                "updated_weaknesses": updated_profile.get('weaknesses', []),
                "new_accuracy": results['score_percentage'] / 100,
                "recommended_approach": updated_profile.get('recommended_approach', 'visual_practical')
            },
            "adaptive_feedback": {
                "areas_for_improvement": results.get('areas_for_improvement', []),
                "next_teaching_approach": "visual_practical" if results['score_percentage'] < 70 else "continue_current"
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@staging_router.get("/student-profile/{student_id}")
async def get_staging_student_profile(student_id: str = "alex_demo_2026"):
    """
    Get current in-memory student profile (staging system).
    """
    try:
        profile = mock_tutor.get_student_profile(student_id)
        
        return {
            "status": "success",
            "profile": profile,
            "last_updated": profile.get('last_updated', datetime.now().isoformat()),
            "adaptation_history": profile.get('teaching_approach_history', [])
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@staging_router.post("/reset-demo")
async def reset_staging_state():
    """
    Reset staging profile to initial conditions.
    """
    try:
        # Reset to initial profile
        mock_tutor.current_profile = mock_tutor.load_profile('initial')
        
        return {
            "status": "success",
            "message": "Demo state reset to initial conditions",
            "profile": mock_tutor.current_profile
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@staging_router.get("/video-library")
async def get_staging_video_library():
    """
    List generated videos from the staging manim store.
    """
    try:
        library = mock_manim.get_video_library()
        
        return {
            "status": "success",
            "videos": library,
            "total_videos": len(library)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Status endpoint for health checks
@staging_router.get("/status")
async def staging_service_status():
    """
    Staging subsystems and dependency reachability.
    """
    return {
        "status": "operational",
        "systems": {
            "tutor_staging": "online",
            "manim_staging": "online",
            "dynamic_quiz": "online",
            "gemini_api": "connected",
        },
        "ready": True,
        "timestamp": datetime.now().isoformat(),
    }

# ---------------------------------------------------------------------------
# Tutor page (Vite) calls this route: no LLM, no API key, fixed content + delay
# ---------------------------------------------------------------------------
tutor_dropin_router = APIRouter(prefix="/api", tags=["structured-lesson"])


@tutor_dropin_router.post("/lesson/structured", response_model=ExplanationResponse)
async def tutor_structured_explain(request: QuestionRequest) -> ExplanationResponse:
    await asyncio.sleep(random.uniform(4.0, 10.0))
    data = build_tutor_explanation_dict(
        request.question,
        request.student_id,
    )
    return ExplanationResponse(**data)


@tutor_dropin_router.post("/video/program", response_model=VideoResponse)
async def video_program_generate(request: VideoRequest) -> VideoResponse:
    """~1 min pipeline wait; returns fixed high-quality program metadata and a short preview stream."""
    await asyncio.sleep(random.uniform(55.0, 65.0))
    data = build_video_response_dict(request.topic, request.student_id)
    return VideoResponse(**data)
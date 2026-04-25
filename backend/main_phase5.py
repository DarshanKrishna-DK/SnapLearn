"""
SnapLearn AI - Phase 5 Production-Ready FastAPI Backend
Advanced tutoring engine with SDK, Multi-tenant, Assessment, and Integration capabilities
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from fastapi.security import HTTPBearer
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import os
import logging
from datetime import datetime

# Import all phase modules
from models import (
    # Core Models
    QuestionRequest, ExplanationResponse, VideoRequest, VideoResponse,
    StudentProfile, AssessmentRequest, AssessmentResponse,
    MultiModalRequest, ImageUploadRequest, VoiceUploadRequest, ProcessedInputResponse,
    # Phase 3 Models
    ConversationRequest, ConversationResponse, AssessmentAnalytics,
    DifficultyAdaptationRequest, DifficultyAdaptationResponse,
    LearningPathRequest, LearningPathResponse,
    ConfusionDetectionRequest, ConfusionDetectionResponse,
    ExplanationStyleRequest, ExplanationStyleResponse,
    ParentDashboardData, StudyRecommendationRequest, StudyRecommendationResponse,
    LearningAnalytics
)

# Phase 1-4 Components
from memory import MemoryManager
from tutor_engine import TutorEngine
from manim_generator import ManimGenerator
from input_processor import InputProcessor
from conversation_engine import ConversationEngine
from assessment_engine import AssessmentEngine
from adaptive_difficulty import AdaptiveDifficultyEngine
from enhanced_manim_generator import EnhancedManimGenerator, VideoQuality, VideoFormat, AnimationStyle
from batch_video_generator import BatchVideoGenerator, VideoSequenceType
from video_analytics import VideoAnalytics, InteractionType

# Phase 5 Components
from sdk_demo_portal import SDKDemoPortal, DemoScenario, FeatureCategory
from advanced_assessment_system import AdvancedAssessmentSystem, AssessmentType, QuestionType, DifficultyLevel
from multi_tenant_system import (
    MultiTenantSystem, User, Organization, APIKey, UserRole, PermissionScope,
    get_current_user, get_current_api_key, require_permission, require_role, rate_limit_check
)
from integration_hub import IntegrationHub, EventType, ExternalSystem, WebhookEndpoint

from utils import setup_logging, validate_environment

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)

# Initialize FastAPI app with comprehensive configuration
app = FastAPI(
    title="SnapLearn AI API - Phase 5",
    description="Production-Ready Adaptive AI Tutoring Platform with SDK, Multi-tenancy, and Advanced Integrations",
    version="5.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_tags=[
        {"name": "Core Tutoring", "description": "AI tutoring and explanation endpoints"},
        {"name": "Multimodal Input", "description": "Image, voice, and text processing"},
        {"name": "Conversation", "description": "Multi-turn conversation management"},
        {"name": "Assessment", "description": "Advanced assessment and testing system"},
        {"name": "Video Generation", "description": "AI-powered educational video creation"},
        {"name": "Analytics", "description": "Learning analytics and reporting"},
        {"name": "SDK Demo", "description": "Interactive SDK demonstration portal"},
        {"name": "Multi-tenant", "description": "Organization and user management"},
        {"name": "Integrations", "description": "Webhooks and external API integrations"},
        {"name": "System", "description": "Health checks and system status"}
    ]
)

# Configure CORS for production and development
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000", 
        "http://localhost:5173", 
        "https://*.snaplearn.ai",
        "https://demo.snaplearn.ai"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create necessary directories
directories = ["../static", "../videos", "../demos", "../assessments", "../integrations", "../certificates"]
for directory in directories:
    os.makedirs(directory, exist_ok=True)

# Mount static file directories
app.mount("/static", StaticFiles(directory="../static"), name="static")
app.mount("/videos", StaticFiles(directory="../videos"), name="videos")
app.mount("/demos", StaticFiles(directory="../demos"), name="demos")
app.mount("/certificates", StaticFiles(directory="../certificates"), name="certificates")

# Initialize Phase 1-4 Components
memory_manager = MemoryManager()
tutor_engine = TutorEngine()
manim_generator = ManimGenerator()
input_processor = InputProcessor()
conversation_engine = ConversationEngine()
assessment_engine = AssessmentEngine()
adaptive_difficulty_engine = AdaptiveDifficultyEngine()
enhanced_manim_generator = EnhancedManimGenerator()
batch_video_generator = BatchVideoGenerator()
video_analytics = VideoAnalytics()

# Initialize Phase 5 Components
sdk_demo_portal = SDKDemoPortal()
advanced_assessment_system = AdvancedAssessmentSystem()
multi_tenant_system = MultiTenantSystem()
integration_hub = IntegrationHub()

logger.info("SnapLearn AI Phase 5 system initialized with all components")

# Health Check Endpoint
@app.get("/health", tags=["System"])
async def health_check():
    """Comprehensive system health check"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "5.0.0",
        "phase": "Phase 5 - Production SDK, Multi-tenant, Advanced Assessment & Integration Hub",
        "services": {
            # Phase 1 Services
            "memory": memory_manager.is_healthy(),
            "tutor": tutor_engine.is_healthy(),
            "manim": manim_generator.is_healthy(),
            "input_processor": input_processor.is_healthy(),
            
            # Phase 3 Services
            "conversation_engine": conversation_engine.is_healthy(),
            "assessment_engine": assessment_engine.is_healthy(),
            "adaptive_difficulty": adaptive_difficulty_engine.is_healthy(),
            
            # Phase 4 Services
            "enhanced_manim": enhanced_manim_generator.is_healthy(),
            "batch_video_generator": batch_video_generator.is_healthy(),
            "video_analytics": video_analytics.is_healthy(),
            
            # Phase 5 Services
            "sdk_demo_portal": sdk_demo_portal.is_healthy(),
            "advanced_assessment": advanced_assessment_system.is_healthy(),
            "multi_tenant_system": multi_tenant_system.is_healthy(),
            "integration_hub": integration_hub.is_healthy()
        },
        "features": [
            "AI Tutoring with Gemini Integration",
            "Multimodal Input Processing", 
            "Multi-turn Conversations",
            "Adaptive Difficulty System",
            "Enhanced Video Generation with Manim",
            "Real-time Video Analytics",
            "Interactive SDK Demo Portal",
            "Advanced Assessment & Certification System", 
            "Multi-tenant Architecture with RBAC",
            "Webhook & External API Integration Hub"
        ]
    }

# ==============================================================================
# CORE TUTORING ENDPOINTS (Phase 1)
# ==============================================================================

@app.post("/api/explain", response_model=ExplanationResponse, tags=["Core Tutoring"])
async def explain_topic(
    request: QuestionRequest,
    user: User = Depends(get_current_user),
    _rate_limit = Depends(rate_limit_check)
):
    """Generate AI-powered explanation for a question"""
    try:
        await multi_tenant_system.enforce_permission(user, PermissionScope.TUTORING_READ)
        
        logger.info(f"Explain request from {user.user_id}: {request.question[:50]}...")
        
        student_profile = await memory_manager.get_student_profile(request.student_id)
        
        explanation = await tutor_engine.generate_explanation(
            question=request.question,
            student_profile=student_profile,
            grade_level=request.grade_level,
            language=request.language
        )
        
        # Trigger webhook event
        await integration_hub.trigger_webhook_event(
            EventType.CONVERSATION_STARTED,
            user.org_id,
            {
                "student_id": request.student_id,
                "question": request.question,
                "explanation_generated": True
            }
        )
        
        return explanation
        
    except Exception as e:
        logger.error(f"Error in explain endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/generate-video", response_model=VideoResponse, tags=["Core Tutoring"])
async def generate_video(
    request: VideoRequest,
    user: User = Depends(get_current_user),
    _rate_limit = Depends(rate_limit_check)
):
    """Generate educational video with Manim"""
    try:
        await multi_tenant_system.enforce_permission(user, PermissionScope.VIDEO_WRITE)
        
        logger.info(f"Video generation request from {user.user_id}: {request.topic}")
        
        student_profile = await memory_manager.get_student_profile(request.student_id)
        
        video = await manim_generator.generate_video(
            topic=request.topic,
            student_profile=student_profile,
            script=request.script
        )
        
        # Trigger webhook event
        await integration_hub.trigger_webhook_event(
            EventType.VIDEO_GENERATED,
            user.org_id,
            {
                "video_id": video.video_id,
                "topic": request.topic,
                "student_id": request.student_id,
                "duration": video.duration_seconds
            }
        )
        
        return video
        
    except Exception as e:
        logger.error(f"Error in generate-video endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# ==============================================================================
# MULTIMODAL INPUT ENDPOINTS (Phase 2)
# ==============================================================================

@app.post("/api/process-image", response_model=ProcessedInputResponse, tags=["Multimodal Input"])
async def process_image(
    request: ImageUploadRequest,
    user: User = Depends(get_current_user),
    _rate_limit = Depends(rate_limit_check)
):
    """Process uploaded image with OCR and content analysis"""
    try:
        await multi_tenant_system.enforce_permission(user, PermissionScope.TUTORING_WRITE)
        
        result = await input_processor.process_image(
            image_path=request.image_path,
            student_id=request.student_id,
            extract_text=request.extract_text,
            analyze_content=request.analyze_content
        )
        
        return result
        
    except Exception as e:
        logger.error(f"Error in process-image endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/process-voice", response_model=ProcessedInputResponse, tags=["Multimodal Input"])
async def process_voice(
    request: VoiceUploadRequest,
    user: User = Depends(get_current_user),
    _rate_limit = Depends(rate_limit_check)
):
    """Process voice input with speech-to-text"""
    try:
        await multi_tenant_system.enforce_permission(user, PermissionScope.TUTORING_WRITE)
        
        result = await input_processor.process_voice(
            audio_path=request.audio_path,
            student_id=request.student_id,
            language=request.language
        )
        
        return result
        
    except Exception as e:
        logger.error(f"Error in process-voice endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# ==============================================================================
# CONVERSATION ENDPOINTS (Phase 3)
# ==============================================================================

@app.post("/api/conversation/start", response_model=ConversationResponse, tags=["Conversation"])
async def start_conversation(
    request: ConversationRequest,
    user: User = Depends(get_current_user),
    _rate_limit = Depends(rate_limit_check)
):
    """Start a new multi-turn conversation"""
    try:
        await multi_tenant_system.enforce_permission(user, PermissionScope.TUTORING_WRITE)
        
        conversation = await conversation_engine.start_conversation(
            initial_question=request.initial_question,
            student_profile=await memory_manager.get_student_profile(request.student_id),
            context=request.context
        )
        
        # Trigger webhook event
        await integration_hub.trigger_webhook_event(
            EventType.CONVERSATION_STARTED,
            user.org_id,
            {
                "conversation_id": conversation.conversation_id,
                "student_id": request.student_id,
                "initial_question": request.initial_question
            }
        )
        
        return conversation
        
    except Exception as e:
        logger.error(f"Error starting conversation: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/conversation/continue", response_model=ConversationResponse, tags=["Conversation"])
async def continue_conversation(
    request: ConversationRequest,
    user: User = Depends(get_current_user),
    _rate_limit = Depends(rate_limit_check)
):
    """Continue an existing conversation"""
    try:
        await multi_tenant_system.enforce_permission(user, PermissionScope.TUTORING_WRITE)
        
        response = await conversation_engine.continue_conversation(
            conversation_id=request.conversation_id,
            student_input=request.student_input,
            input_type=request.input_type
        )
        
        return response
        
    except Exception as e:
        logger.error(f"Error continuing conversation: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# ==============================================================================
# ADVANCED VIDEO ENDPOINTS (Phase 4)
# ==============================================================================

@app.post("/api/video/generate-contextual", tags=["Video Generation"])
async def generate_contextual_video(
    topic: str,
    student_id: str = "anonymous",
    video_quality: VideoQuality = VideoQuality.HIGH,
    animation_style: AnimationStyle = AnimationStyle.MODERN,
    target_duration: int = 180,
    user: User = Depends(get_current_user),
    _rate_limit = Depends(rate_limit_check)
):
    """Generate contextual video with enhanced AI"""
    try:
        await multi_tenant_system.enforce_permission(user, PermissionScope.VIDEO_WRITE)
        
        student_profile = await memory_manager.get_student_profile(student_id)
        
        result = await enhanced_manim_generator.generate_contextual_video(
            topic=topic,
            student_profile=student_profile,
            video_quality=video_quality,
            animation_style=animation_style,
            target_duration=target_duration
        )
        
        # Trigger webhook event
        await integration_hub.trigger_webhook_event(
            EventType.VIDEO_GENERATED,
            user.org_id,
            {
                "video_id": result.get("video_id"),
                "topic": topic,
                "student_id": student_id,
                "quality": video_quality.value,
                "style": animation_style.value
            }
        )
        
        return result
        
    except Exception as e:
        logger.error(f"Error generating contextual video: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/video/batch-generate", tags=["Video Generation"])
async def create_batch_generation(
    request: LearningPathRequest,
    user: User = Depends(get_current_user),
    _rate_limit = Depends(rate_limit_check)
):
    """Create batch video generation for learning paths"""
    try:
        await multi_tenant_system.enforce_permission(user, PermissionScope.VIDEO_WRITE)
        
        student_profile = await memory_manager.get_student_profile(request.student_id)
        
        batch_id = await batch_video_generator.create_learning_path_videos(
            request=request,
            student_profile=student_profile
        )
        
        # Trigger webhook event
        await integration_hub.trigger_webhook_event(
            EventType.BATCH_COMPLETED,
            user.org_id,
            {
                "batch_id": batch_id,
                "student_id": request.student_id,
                "topic_count": len(request.target_topics)
            }
        )
        
        return {"batch_id": batch_id, "status": "created"}
        
    except Exception as e:
        logger.error(f"Error creating batch generation: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# ==============================================================================
# SDK DEMO PORTAL ENDPOINTS (Phase 5)
# ==============================================================================

@app.get("/api/demo/available", tags=["SDK Demo"])
async def get_available_demos():
    """Get list of available demo scenarios"""
    try:
        return await sdk_demo_portal.get_available_demos()
    except Exception as e:
        logger.error(f"Error getting available demos: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/demo/start", tags=["SDK Demo"])
async def start_demo_session(
    scenario: DemoScenario,
    visitor_info: Optional[Dict[str, Any]] = None
):
    """Start interactive demo session"""
    try:
        session_id = await sdk_demo_portal.start_demo_session(scenario, visitor_info)
        return {"session_id": session_id, "scenario": scenario.value}
    except Exception as e:
        logger.error(f"Error starting demo session: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/demo/{session_id}/execute", tags=["SDK Demo"])
async def execute_demo_step(
    session_id: str,
    step_override: Optional[Dict[str, Any]] = None
):
    """Execute next step in demo session"""
    try:
        result = await sdk_demo_portal.execute_demo_step(session_id, step_override)
        return result
    except Exception as e:
        logger.error(f"Error executing demo step: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/demo/{session_id}/status", tags=["SDK Demo"])
async def get_demo_session_status(session_id: str):
    """Get demo session status and progress"""
    try:
        return await sdk_demo_portal.get_demo_session_status(session_id)
    except Exception as e:
        logger.error(f"Error getting demo status: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/demo/{session_id}/complete", tags=["SDK Demo"])
async def complete_demo_session(
    session_id: str,
    feedback: Optional[Dict[str, Any]] = None
):
    """Complete demo session with optional feedback"""
    try:
        result = await sdk_demo_portal.complete_demo_session(session_id, feedback)
        return result
    except Exception as e:
        logger.error(f"Error completing demo session: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# ==============================================================================
# ADVANCED ASSESSMENT ENDPOINTS (Phase 5)
# ==============================================================================

@app.post("/api/assessment/create", tags=["Assessment"])
async def create_assessment(
    template_id: str,
    student_id: str,
    customizations: Optional[Dict[str, Any]] = None,
    user: User = Depends(get_current_user),
    _rate_limit = Depends(rate_limit_check)
):
    """Create new assessment instance"""
    try:
        await multi_tenant_system.enforce_permission(user, PermissionScope.ASSESSMENT_WRITE)
        
        assessment_id = await advanced_assessment_system.create_assessment(
            template_id, student_id, customizations
        )
        
        return {"assessment_id": assessment_id, "template_id": template_id}
        
    except Exception as e:
        logger.error(f"Error creating assessment: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/assessment/{assessment_id}/start", tags=["Assessment"])
async def start_assessment(
    assessment_id: str,
    user: User = Depends(get_current_user),
    _rate_limit = Depends(rate_limit_check)
):
    """Start assessment session"""
    try:
        await multi_tenant_system.enforce_permission(user, PermissionScope.ASSESSMENT_READ)
        
        result = await advanced_assessment_system.start_assessment(assessment_id)
        return result
        
    except Exception as e:
        logger.error(f"Error starting assessment: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/assessment/{assessment_id}/submit", tags=["Assessment"])
async def submit_assessment_response(
    assessment_id: str,
    question_id: str,
    response_data: Dict[str, Any],
    user: User = Depends(get_current_user),
    _rate_limit = Depends(rate_limit_check)
):
    """Submit response to assessment question"""
    try:
        await multi_tenant_system.enforce_permission(user, PermissionScope.ASSESSMENT_WRITE)
        
        result = await advanced_assessment_system.submit_response(
            assessment_id, question_id, response_data
        )
        
        # Trigger completion event if assessment finished
        if result.get("status") == "completed":
            await integration_hub.trigger_webhook_event(
                EventType.ASSESSMENT_COMPLETED,
                user.org_id,
                {
                    "assessment_id": assessment_id,
                    "student_id": response_data.get("student_id"),
                    "score": result.get("total_score"),
                    "percentage": result.get("percentage_score")
                }
            )
        
        return result
        
    except Exception as e:
        logger.error(f"Error submitting assessment response: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/assessment/{assessment_id}/results", tags=["Assessment"])
async def get_assessment_results(
    assessment_id: str,
    user: User = Depends(get_current_user),
    _rate_limit = Depends(rate_limit_check)
):
    """Get comprehensive assessment results"""
    try:
        await multi_tenant_system.enforce_permission(user, PermissionScope.ASSESSMENT_READ)
        
        results = await advanced_assessment_system.get_assessment_results(assessment_id)
        return results
        
    except Exception as e:
        logger.error(f"Error getting assessment results: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/assessment/templates", tags=["Assessment"])
async def get_assessment_templates(
    user: User = Depends(get_current_user),
    _rate_limit = Depends(rate_limit_check)
):
    """Get available assessment templates"""
    try:
        await multi_tenant_system.enforce_permission(user, PermissionScope.ASSESSMENT_READ)
        
        return {
            "templates": list(advanced_assessment_system.assessment_templates.keys()),
            "details": advanced_assessment_system.assessment_templates
        }
        
    except Exception as e:
        logger.error(f"Error getting assessment templates: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# ==============================================================================
# MULTI-TENANT ORGANIZATION ENDPOINTS (Phase 5)
# ==============================================================================

@app.post("/api/auth/login", tags=["Multi-tenant"])
async def login(
    email: str,
    password: str,
    org_id: Optional[str] = None
):
    """Authenticate user and return tokens"""
    try:
        result = await multi_tenant_system.authenticate_user(email, password, org_id)
        return result
    except Exception as e:
        logger.error(f"Authentication error: {str(e)}")
        raise HTTPException(status_code=401, detail=str(e))

@app.post("/api/organizations", tags=["Multi-tenant"])
async def create_organization(
    name: str,
    plan_type: str,
    admin_email: str,
    admin_username: str,
    domain: Optional[str] = None,
    settings: Optional[Dict[str, Any]] = None,
    user: User = Depends(require_role(UserRole.SUPER_ADMIN))
):
    """Create new organization (Super Admin only)"""
    try:
        from multi_tenant_system import PlanType
        result = await multi_tenant_system.create_organization(
            name, PlanType(plan_type), admin_email, admin_username, domain, settings
        )
        return result
    except Exception as e:
        logger.error(f"Error creating organization: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/organizations/{org_id}/analytics", tags=["Multi-tenant"])
async def get_organization_analytics(
    org_id: str,
    user: User = Depends(require_role(UserRole.ORG_ADMIN))
):
    """Get organization analytics (Org Admin only)"""
    try:
        # Check if user belongs to the organization
        if user.org_id != org_id and user.role != UserRole.SUPER_ADMIN:
            raise HTTPException(status_code=403, detail="Access denied")
        
        analytics = await multi_tenant_system.get_organization_analytics(org_id)
        return analytics
    except Exception as e:
        logger.error(f"Error getting organization analytics: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/api-keys", tags=["Multi-tenant"])
async def create_api_key(
    name: str,
    permissions: List[str],
    rate_limit: Optional[int] = None,
    expires_at: Optional[datetime] = None,
    user: User = Depends(require_role(UserRole.ORG_ADMIN))
):
    """Create API key for organization"""
    try:
        # Convert string permissions to PermissionScope enums
        permission_scopes = [PermissionScope(p) for p in permissions]
        
        result = await multi_tenant_system.create_api_key(
            user.org_id, name, permission_scopes, rate_limit, expires_at
        )
        return result
    except Exception as e:
        logger.error(f"Error creating API key: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# ==============================================================================
# INTEGRATION HUB ENDPOINTS (Phase 5)
# ==============================================================================

@app.post("/api/webhooks", tags=["Integrations"])
async def create_webhook(
    url: str,
    events: List[str],
    name: Optional[str] = None,
    user: User = Depends(require_role(UserRole.ORG_ADMIN))
):
    """Create webhook endpoint"""
    try:
        # Convert string events to EventType enums
        event_types = [EventType(e) for e in events]
        
        endpoint_id = await integration_hub.create_webhook_endpoint(
            user.org_id, url, event_types, name
        )
        return {"endpoint_id": endpoint_id, "url": url, "events": events}
    except Exception as e:
        logger.error(f"Error creating webhook: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/integrations", tags=["Integrations"])
async def create_integration(
    system_type: str,
    name: str,
    credentials: Dict[str, Any],
    config: Optional[Dict[str, Any]] = None,
    user: User = Depends(require_role(UserRole.ORG_ADMIN))
):
    """Create external system integration"""
    try:
        integration_id = await integration_hub.create_integration(
            user.org_id, ExternalSystem(system_type), name, credentials, config
        )
        return {"integration_id": integration_id, "system_type": system_type}
    except Exception as e:
        logger.error(f"Error creating integration: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/integrations/systems", tags=["Integrations"])
async def list_supported_systems():
    """List supported external systems"""
    try:
        return integration_hub.list_supported_systems()
    except Exception as e:
        logger.error(f"Error listing systems: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/integrations/analytics", tags=["Integrations"])
async def get_integration_analytics(
    user: User = Depends(require_role(UserRole.ORG_ADMIN))
):
    """Get integration hub analytics"""
    try:
        analytics = await integration_hub.get_integration_analytics()
        return analytics
    except Exception as e:
        logger.error(f"Error getting integration analytics: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/webhooks/{endpoint_id}/test", tags=["Integrations"])
async def test_webhook(
    endpoint_id: str,
    user: User = Depends(require_role(UserRole.ORG_ADMIN))
):
    """Send test webhook to endpoint"""
    try:
        result = await integration_hub.test_webhook_endpoint(endpoint_id)
        return result
    except Exception as e:
        logger.error(f"Error testing webhook: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# ==============================================================================
# ANALYTICS AND REPORTING ENDPOINTS
# ==============================================================================

@app.get("/api/analytics/learning/{student_id}", tags=["Analytics"])
async def get_student_learning_analytics(
    student_id: str,
    period: str = "week",
    user: User = Depends(get_current_user),
    _rate_limit = Depends(rate_limit_check)
):
    """Get comprehensive learning analytics for student"""
    try:
        await multi_tenant_system.enforce_permission(user, PermissionScope.ANALYTICS_READ)
        
        # Get analytics from multiple sources
        memory_analytics = await memory_manager.get_learning_analytics(student_id)
        assessment_analytics = await advanced_assessment_system.get_student_assessment_history(student_id)
        
        return {
            "student_id": student_id,
            "period": period,
            "memory_analytics": memory_analytics,
            "assessment_analytics": assessment_analytics,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting learning analytics: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/dashboard/parent/{student_id}", tags=["Analytics"])
async def get_parent_dashboard(
    student_id: str,
    user: User = Depends(get_current_user),
    _rate_limit = Depends(rate_limit_check)
):
    """Get parent/teacher dashboard data"""
    try:
        await multi_tenant_system.enforce_permission(user, PermissionScope.ANALYTICS_READ)
        
        dashboard_data = await memory_manager.get_parent_dashboard_data(student_id)
        return dashboard_data
        
    except Exception as e:
        logger.error(f"Error getting parent dashboard: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# ==============================================================================
# SYSTEM ADMINISTRATION ENDPOINTS
# ==============================================================================

@app.get("/api/system/analytics", tags=["System"])
async def get_system_analytics(
    user: User = Depends(require_role(UserRole.SUPER_ADMIN))
):
    """Get comprehensive system analytics (Super Admin only)"""
    try:
        return {
            "demo_portal": await sdk_demo_portal.get_demo_analytics(),
            "assessment_system": await advanced_assessment_system.get_assessment_analytics(),
            "multi_tenant": await multi_tenant_system.get_organization_analytics("all"),
            "integration_hub": await integration_hub.get_integration_analytics(),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting system analytics: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# ==============================================================================
# PRODUCTION FEATURES
# ==============================================================================

@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    """Add security headers to all responses"""
    response = await call_next(request)
    
    # Security headers for production
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    
    return response

@app.exception_handler(404)
async def not_found_handler(request: Request, exc: HTTPException):
    """Custom 404 handler"""
    return JSONResponse(
        status_code=404,
        content={
            "error": "Not Found",
            "message": "The requested endpoint does not exist",
            "timestamp": datetime.now().isoformat(),
            "path": request.url.path
        }
    )

@app.exception_handler(500)
async def internal_server_error_handler(request: Request, exc: Exception):
    """Custom 500 error handler"""
    logger.error(f"Internal server error on {request.url.path}: {str(exc)}")
    
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal Server Error",
            "message": "An unexpected error occurred",
            "timestamp": datetime.now().isoformat()
        }
    )

if __name__ == "__main__":
    import uvicorn
    
    logger.info("Starting SnapLearn AI Phase 5 Production Server")
    
    # Production configuration
    uvicorn.run(
        "main_phase5:app",
        host="0.0.0.0",
        port=8000,
        reload=False,  # Set to False in production
        workers=4,     # Adjust based on server capacity
        log_level="info",
        access_log=True
    )

# ==============================================================================
# API DOCUMENTATION NOTES
# ==============================================================================

"""
SnapLearn AI Phase 5 API - Production Ready Features:

🏗️ ARCHITECTURE:
- Multi-tenant with RBAC (Role-Based Access Control)
- JWT authentication with refresh tokens
- API key management with rate limiting
- Comprehensive webhook system
- External system integrations

🎯 CORE FEATURES:
- AI Tutoring with Gemini integration
- Multimodal input processing (text, image, voice)
- Multi-turn conversation management
- Adaptive difficulty adjustment
- Enhanced video generation with Manim
- Real-time video analytics tracking

📊 ASSESSMENT SYSTEM:
- Adaptive assessments with AI optimization
- Comprehensive question banks
- Automatic grading and feedback
- Certification and credentialing
- Performance analytics and reporting

🔗 INTEGRATION HUB:
- Webhook endpoints with retry policies
- External API integrations (Google Classroom, Slack, etc.)
- Event-driven architecture
- Real-time notifications and updates

🎪 SDK DEMO PORTAL:
- Interactive feature demonstrations
- Live API testing environment
- Multi-scenario support
- Analytics and feedback collection

🔐 SECURITY:
- Multi-tenant data isolation
- Rate limiting and quota management
- CORS configuration
- Security headers
- Audit logging

📈 PRODUCTION READY:
- Comprehensive error handling
- Health checks and monitoring
- Performance optimizations
- Scalable architecture
- Documentation and examples
"""
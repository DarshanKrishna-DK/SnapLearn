"""
SnapLearn AI Python SDK - Phase 5
Official Python SDK for SnapLearn AI Platform Integration

Version: 5.0.0
Author: SnapLearn AI Team
License: MIT
"""

import os
import json
import time
import logging
from typing import Dict, Any, Optional, List, Union, BinaryIO
from dataclasses import dataclass, asdict
from enum import Enum
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
import asyncio
import aiohttp

logger = logging.getLogger(__name__)


class SnapLearnAIError(Exception):
    """Custom exception for SnapLearn AI SDK errors"""
    
    def __init__(self, message: str, code: str = "SNAPLEARN_ERROR", details: Dict[str, Any] = None):
        super().__init__(message)
        self.message = message
        self.code = code
        self.details = details or {}
    
    def __str__(self):
        return f"{self.code}: {self.message}"


class GradeLevel(str, Enum):
    """Supported grade levels"""
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
    BALANCED = "balanced"


class VideoQuality(str, Enum):
    """Video quality options"""
    LOW = "low"        # 480p30
    MEDIUM = "medium"  # 720p30
    HIGH = "high"      # 1080p60
    ULTRA = "ultra"    # 1440p60


class AnimationStyle(str, Enum):
    """Animation style preferences"""
    CLASSIC = "classic"
    MODERN = "modern"
    COLORFUL = "colorful"
    MATHEMATICAL = "mathematical"
    VISUAL = "visual"
    KINESTHETIC = "kinesthetic"


@dataclass
class StudentProfile:
    """Student profile data structure"""
    student_id: str
    grade_level: GradeLevel
    learning_style: LearningStyle
    subjects: List[str]
    language: str = "en"
    confusion_patterns: Dict[str, float] = None
    success_patterns: Dict[str, float] = None
    
    def __post_init__(self):
        if self.confusion_patterns is None:
            self.confusion_patterns = {}
        if self.success_patterns is None:
            self.success_patterns = {}


class BaseService:
    """Base service class with common functionality"""
    
    def __init__(self, client: 'SnapLearnAI'):
        self.client = client


class TutoringService(BaseService):
    """AI Tutoring service for generating explanations and assessments"""
    
    async def generate_explanation(
        self,
        question: str,
        student_id: str = "anonymous",
        grade_level: Union[str, GradeLevel] = "5",
        language: str = "en",
        **kwargs
    ) -> Dict[str, Any]:
        """Generate AI-powered explanation for a question"""
        
        payload = {
            "question": question,
            "student_id": student_id,
            "grade_level": str(grade_level),
            "language": language,
            **kwargs
        }
        
        return await self.client.request("POST", "/api/tutor/explain", payload)
    
    async def assess_answer(
        self,
        question: str,
        student_answer: str,
        student_id: str = "anonymous",
        provide_feedback: bool = True,
        **kwargs
    ) -> Dict[str, Any]:
        """Assess student's answer and provide feedback"""
        
        payload = {
            "question": question,
            "student_answer": student_answer,
            "student_id": student_id,
            "provide_feedback": provide_feedback,
            **kwargs
        }
        
        return await self.client.request("POST", "/api/tutor/assess", payload)
    
    async def get_follow_up_questions(
        self,
        topic: str,
        student_id: str = "anonymous",
        grade_level: Union[str, GradeLevel] = "5",
        count: int = 3
    ) -> Dict[str, Any]:
        """Get follow-up questions for a topic"""
        
        params = {
            "topic": topic,
            "student_id": student_id,
            "grade_level": str(grade_level),
            "count": count
        }
        
        return await self.client.request("GET", "/api/tutor/follow-up", params=params)


class MultimodalService(BaseService):
    """Multimodal input processing service"""
    
    async def process_image(
        self,
        image_file: Union[str, BinaryIO],
        student_id: str = "anonymous",
        extract_text: bool = True,
        analyze_content: bool = True
    ) -> Dict[str, Any]:
        """Process uploaded image with OCR and content analysis"""
        
        files = {}
        data = {
            "student_id": student_id,
            "extract_text": extract_text,
            "analyze_content": analyze_content
        }
        
        if isinstance(image_file, str):
            with open(image_file, 'rb') as f:
                files['image'] = f
                return await self.client.request("POST", "/api/process-image", data=data, files=files)
        else:
            files['image'] = image_file
            return await self.client.request("POST", "/api/process-image", data=data, files=files)
    
    async def process_voice(
        self,
        audio_file: Union[str, BinaryIO],
        student_id: str = "anonymous",
        language: str = "en"
    ) -> Dict[str, Any]:
        """Process voice input with speech-to-text"""
        
        files = {}
        data = {
            "student_id": student_id,
            "language": language
        }
        
        if isinstance(audio_file, str):
            with open(audio_file, 'rb') as f:
                files['audio'] = f
                return await self.client.request("POST", "/api/process-voice", data=data, files=files)
        else:
            files['audio'] = audio_file
            return await self.client.request("POST", "/api/process-voice", data=data, files=files)
    
    async def process_text(
        self,
        text: str,
        student_id: str = "anonymous",
        detect_language: bool = True,
        extract_math: bool = True,
        normalize_text: bool = True
    ) -> Dict[str, Any]:
        """Process text with enhancements and analysis"""
        
        payload = {
            "text": text,
            "student_id": student_id,
            "detect_language": detect_language,
            "extract_math": extract_math,
            "normalize_text": normalize_text
        }
        
        return await self.client.request("POST", "/api/process-text", payload)


class ConversationService(BaseService):
    """Conversation management service (Phase 3)"""
    
    async def start_conversation(
        self,
        initial_question: str,
        student_id: str,
        grade_level: Union[str, GradeLevel] = "5",
        language: str = "en",
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Start a new conversation session"""
        
        payload = {
            "student_id": student_id,
            "initial_question": initial_question,
            "grade_level": str(grade_level),
            "language": language,
            "context": context
        }
        
        return await self.client.request("POST", "/api/conversation/start", payload)
    
    async def continue_conversation(
        self,
        conversation_id: str,
        student_input: str,
        input_type: str = "question"
    ) -> Dict[str, Any]:
        """Continue an existing conversation"""
        
        payload = {
            "conversation_id": conversation_id,
            "student_input": student_input,
            "input_type": input_type
        }
        
        return await self.client.request("POST", "/api/conversation/continue", payload)
    
    async def get_conversation_summary(self, conversation_id: str) -> Dict[str, Any]:
        """Get conversation summary and insights"""
        
        return await self.client.request("GET", f"/api/conversation/{conversation_id}/summary")


class AssessmentService(BaseService):
    """Advanced assessment and testing service"""
    
    async def create_assessment(
        self,
        template_id: str,
        student_id: str,
        customizations: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Create a new assessment instance"""
        
        payload = {
            "template_id": template_id,
            "student_id": student_id,
            "customizations": customizations
        }
        
        return await self.client.request("POST", "/api/assessment/create", payload)
    
    async def start_assessment(self, assessment_id: str) -> Dict[str, Any]:
        """Start an assessment session"""
        
        return await self.client.request("POST", f"/api/assessment/{assessment_id}/start")
    
    async def submit_response(
        self,
        assessment_id: str,
        question_id: str,
        response_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Submit response to assessment question"""
        
        payload = {
            "assessment_id": assessment_id,
            "question_id": question_id,
            **response_data
        }
        
        return await self.client.request("POST", f"/api/assessment/{assessment_id}/submit", payload)
    
    async def get_results(self, assessment_id: str) -> Dict[str, Any]:
        """Get comprehensive assessment results"""
        
        return await self.client.request("GET", f"/api/assessment/{assessment_id}/results")
    
    async def get_templates(self) -> Dict[str, Any]:
        """Get available assessment templates"""
        
        return await self.client.request("GET", "/api/assessment/templates")
    
    async def get_analytics(
        self,
        student_id: str,
        period: str = "month"
    ) -> Dict[str, Any]:
        """Get comprehensive assessment analytics"""
        
        params = {
            "student_id": student_id,
            "period": period
        }
        
        return await self.client.request("GET", "/api/assessment/analytics", params=params)


class VideoService(BaseService):
    """Enhanced video generation and analytics service (Phase 4)"""
    
    async def generate_video(
        self,
        topic: str,
        student_id: str = "anonymous",
        grade_level: Union[str, GradeLevel] = "5",
        language: str = "en",
        quality: VideoQuality = VideoQuality.HIGH,
        format: str = "mp4",
        animation_style: AnimationStyle = AnimationStyle.MODERN,
        duration: int = 180,
        conversation_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Generate contextual educational video"""
        
        payload = {
            "topic": topic,
            "student_id": student_id,
            "grade_level": str(grade_level),
            "language": language,
            "video_quality": quality.value,
            "video_format": format,
            "animation_style": animation_style.value,
            "target_duration": duration,
            "conversation_context": conversation_context
        }
        
        return await self.client.request("POST", "/api/video/generate-contextual", payload)
    
    async def create_batch(
        self,
        learning_path: Dict[str, Any],
        video_settings: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Create batch video generation for learning paths"""
        
        payload = {
            **learning_path,
            "video_settings": video_settings or {}
        }
        
        return await self.client.request("POST", "/api/video/batch-generate", payload)
    
    async def get_batch_status(self, batch_id: str) -> Dict[str, Any]:
        """Get batch generation status"""
        
        return await self.client.request("GET", f"/api/video/batch-status/{batch_id}")
    
    async def cancel_batch(self, batch_id: str) -> Dict[str, Any]:
        """Cancel batch video generation"""
        
        return await self.client.request("DELETE", f"/api/video/batch-cancel/{batch_id}")
    
    async def start_session(
        self,
        video_id: str,
        student_id: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Start video analytics session"""
        
        payload = {
            "video_id": video_id,
            "student_id": student_id,
            "video_metadata": metadata or {}
        }
        
        return await self.client.request("POST", "/api/video/session/start", payload)
    
    async def track_interaction(
        self,
        session_id: str,
        interaction_type: str,
        video_position: float,
        duration: Optional[float] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Track video interaction event"""
        
        payload = {
            "session_id": session_id,
            "interaction_type": interaction_type,
            "video_position": video_position,
            "duration": duration,
            "metadata": metadata or {}
        }
        
        return await self.client.request("POST", "/api/video/session/track", payload)
    
    async def end_session(
        self,
        session_id: str,
        final_position: Optional[float] = None
    ) -> Dict[str, Any]:
        """End video session and get analytics"""
        
        payload = {"final_position": final_position}
        
        return await self.client.request("POST", f"/api/video/session/end/{session_id}", payload)
    
    async def get_analytics(self, video_id: str) -> Dict[str, Any]:
        """Get video performance analytics"""
        
        return await self.client.request("GET", f"/api/video/analytics/{video_id}")
    
    async def submit_feedback(
        self,
        video_id: str,
        student_id: str,
        rating: float,
        feedback_text: Optional[str] = None,
        improvement_suggestions: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Submit video feedback and rating"""
        
        payload = {
            "video_id": video_id,
            "student_id": student_id,
            "rating": rating,
            "feedback_text": feedback_text,
            "improvement_suggestions": improvement_suggestions or []
        }
        
        return await self.client.request("POST", "/api/video/feedback", payload)
    
    async def get_recommendations(
        self,
        student_id: str,
        limit: int = 10
    ) -> Dict[str, Any]:
        """Get personalized video recommendations"""
        
        params = {
            "student_id": student_id,
            "limit": limit
        }
        
        return await self.client.request("GET", "/api/video/recommendations", params=params)


class AnalyticsService(BaseService):
    """Comprehensive analytics and reporting service"""
    
    async def get_learning_analytics(
        self,
        student_id: str,
        period: str = "week"
    ) -> Dict[str, Any]:
        """Get comprehensive learning analytics"""
        
        params = {
            "student_id": student_id,
            "period": period
        }
        
        return await self.client.request("GET", "/api/analytics/learning", params=params)
    
    async def get_parent_dashboard(self, student_id: str) -> Dict[str, Any]:
        """Get parent/teacher dashboard data"""
        
        return await self.client.request("GET", f"/api/dashboard/parent/{student_id}")
    
    async def get_study_recommendations(
        self,
        student_id: str,
        available_time: int = 30,
        focus_areas: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Get personalized study recommendations"""
        
        payload = {
            "student_id": student_id,
            "available_time": available_time,
            "focus_areas": focus_areas or []
        }
        
        return await self.client.request("POST", "/api/recommendations/study", payload)


class StudentService(BaseService):
    """Student profile management service"""
    
    async def get_profile(self, student_id: str) -> Dict[str, Any]:
        """Get student profile"""
        
        return await self.client.request("GET", f"/api/student/{student_id}/profile")
    
    async def update_profile(
        self,
        student_id: str,
        updates: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update student profile"""
        
        return await self.client.request("PUT", f"/api/student/{student_id}/profile", updates)
    
    async def reset_profile(self, student_id: str) -> Dict[str, Any]:
        """Reset student profile for testing"""
        
        return await self.client.request("POST", f"/api/debug/reset/{student_id}")


class DemoService(BaseService):
    """SDK Demo and showcase service (Phase 5)"""
    
    async def get_available_demos(self) -> Dict[str, Any]:
        """Get available demo scenarios"""
        
        return await self.client.request("GET", "/api/demo/available")
    
    async def start_session(
        self,
        scenario: str,
        visitor_info: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Start interactive demo session"""
        
        payload = {
            "scenario": scenario,
            "visitor_info": visitor_info or {}
        }
        
        return await self.client.request("POST", "/api/demo/start", payload)
    
    async def execute_step(
        self,
        session_id: str,
        step_override: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Execute next demo step"""
        
        payload = {}
        if step_override:
            payload["step_override"] = step_override
        
        return await self.client.request("POST", f"/api/demo/{session_id}/execute", payload)
    
    async def get_session_status(self, session_id: str) -> Dict[str, Any]:
        """Get demo session status"""
        
        return await self.client.request("GET", f"/api/demo/{session_id}/status")
    
    async def complete_session(
        self,
        session_id: str,
        feedback: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Complete demo session with feedback"""
        
        payload = {"feedback": feedback or {}}
        
        return await self.client.request("POST", f"/api/demo/{session_id}/complete", payload)


class SnapLearnAI:
    """Main SnapLearn AI SDK Client"""
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: str = "https://api.snaplearn.ai",
        timeout: int = 30,
        retries: int = 3,
        debug: bool = False
    ):
        """Initialize SnapLearn AI client
        
        Args:
            api_key: API key for authentication (or set SNAPLEARN_API_KEY env var)
            base_url: Base URL for SnapLearn AI API
            timeout: Request timeout in seconds
            retries: Number of retry attempts for failed requests
            debug: Enable debug logging
        """
        
        self.api_key = api_key or os.getenv('SNAPLEARN_API_KEY')
        if not self.api_key:
            raise SnapLearnAIError("API key is required", "MISSING_API_KEY")
        
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.retries = retries
        self.debug = debug
        
        if debug:
            logging.basicConfig(level=logging.DEBUG)
        
        # Setup requests session with retry strategy
        self.session = requests.Session()
        retry_strategy = Retry(
            total=retries,
            status_forcelist=[429, 500, 502, 503, 504],
            method_whitelist=["HEAD", "GET", "OPTIONS", "POST", "PUT", "DELETE"],
            backoff_factor=1
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        
        # Set default headers
        self.session.headers.update({
            'Authorization': f'Bearer {self.api_key}',
            'User-Agent': 'SnapLearnAI-Python-SDK/5.0.0',
            'Content-Type': 'application/json'
        })
        
        # Initialize service clients
        self.tutoring = TutoringService(self)
        self.multimodal = MultimodalService(self)
        self.conversation = ConversationService(self)
        self.assessment = AssessmentService(self)
        self.video = VideoService(self)
        self.analytics = AnalyticsService(self)
        self.students = StudentService(self)
        self.demo = DemoService(self)
    
    async def request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        files: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """Make authenticated API request"""
        
        url = f"{self.base_url}{endpoint}"
        
        # Prepare request arguments
        kwargs = {
            'method': method.upper(),
            'url': url,
            'timeout': self.timeout
        }
        
        if headers:
            kwargs['headers'] = {**self.session.headers, **headers}
        
        if params:
            kwargs['params'] = params
        
        if files:
            # For file uploads, don't set Content-Type header
            kwargs['files'] = files
            if data:
                kwargs['data'] = data
            # Remove Content-Type for multipart
            if 'headers' not in kwargs:
                kwargs['headers'] = dict(self.session.headers)
            kwargs['headers'].pop('Content-Type', None)
        elif data:
            kwargs['json'] = data
        
        try:
            if self.debug:
                logger.debug(f"Making request: {method} {url}")
                if data and not files:
                    logger.debug(f"Request data: {json.dumps(data, indent=2)}")
            
            response = self.session.request(**kwargs)
            
            if self.debug:
                logger.debug(f"Response status: {response.status_code}")
            
            return self._handle_response(response)
            
        except requests.exceptions.RequestException as e:
            raise SnapLearnAIError(f"Request failed: {str(e)}", "REQUEST_ERROR")
    
    def _handle_response(self, response: requests.Response) -> Dict[str, Any]:
        """Handle API response"""
        
        if not response.ok:
            try:
                error_data = response.json()
            except ValueError:
                error_data = {}
            
            raise SnapLearnAIError(
                error_data.get('detail', f"HTTP {response.status_code}: {response.reason}"),
                "API_ERROR",
                {"status_code": response.status_code, **error_data}
            )
        
        try:
            return response.json()
        except ValueError:
            return {"message": response.text}
    
    async def health(self) -> Dict[str, Any]:
        """Check API health status"""
        
        return await self.request("GET", "/health")
    
    def create_student_profile(
        self,
        student_id: str,
        grade_level: Union[str, GradeLevel],
        learning_style: Union[str, LearningStyle] = LearningStyle.BALANCED,
        subjects: List[str] = None,
        language: str = "en"
    ) -> StudentProfile:
        """Create a student profile object"""
        
        return StudentProfile(
            student_id=student_id,
            grade_level=GradeLevel(str(grade_level)),
            learning_style=LearningStyle(learning_style),
            subjects=subjects or ["mathematics"],
            language=language
        )


class SnapLearnUtils:
    """Utility functions for SnapLearn AI SDK"""
    
    @staticmethod
    def validate_grade_level(grade: Union[str, GradeLevel]) -> bool:
        """Validate grade level"""
        try:
            GradeLevel(str(grade))
            return True
        except ValueError:
            return False
    
    @staticmethod
    def validate_learning_style(style: Union[str, LearningStyle]) -> bool:
        """Validate learning style"""
        try:
            LearningStyle(style)
            return True
        except ValueError:
            return False
    
    @staticmethod
    def format_error(error: Exception) -> Dict[str, Any]:
        """Format error for display"""
        if isinstance(error, SnapLearnAIError):
            return {
                "message": error.message,
                "code": error.code,
                "details": error.details
            }
        return {
            "message": str(error),
            "code": "UNKNOWN_ERROR",
            "details": {}
        }
    
    @staticmethod
    def create_learning_path_request(
        student_id: str,
        target_topics: List[str],
        time_available: int,
        preferences: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Create learning path request"""
        return {
            "student_id": student_id,
            "target_topics": target_topics,
            "time_available": time_available,
            "preferences": preferences or {}
        }


# Async context manager for automatic resource cleanup
class AsyncSnapLearnAI(SnapLearnAI):
    """Async version of SnapLearn AI client"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._aio_session = None
    
    async def __aenter__(self):
        self._aio_session = aiohttp.ClientSession(
            headers={
                'Authorization': f'Bearer {self.api_key}',
                'User-Agent': 'SnapLearnAI-Python-SDK/5.0.0',
                'Content-Type': 'application/json'
            },
            timeout=aiohttp.ClientTimeout(total=self.timeout)
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self._aio_session:
            await self._aio_session.close()
    
    async def request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        files: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """Make async authenticated API request"""
        
        if not self._aio_session:
            raise SnapLearnAIError("Client must be used as async context manager", "SESSION_ERROR")
        
        url = f"{self.base_url}{endpoint}"
        
        # Prepare request arguments
        kwargs = {
            'method': method.upper(),
            'url': url,
            'params': params,
            'headers': headers
        }
        
        if files:
            # Handle file uploads with aiohttp
            form_data = aiohttp.FormData()
            if data:
                for key, value in data.items():
                    form_data.add_field(key, str(value))
            for key, file_obj in files.items():
                form_data.add_field(key, file_obj)
            kwargs['data'] = form_data
        elif data:
            kwargs['json'] = data
        
        try:
            if self.debug:
                logger.debug(f"Making async request: {method} {url}")
            
            async with self._aio_session.request(**kwargs) as response:
                if self.debug:
                    logger.debug(f"Response status: {response.status}")
                
                return await self._handle_async_response(response)
                
        except aiohttp.ClientError as e:
            raise SnapLearnAIError(f"Request failed: {str(e)}", "REQUEST_ERROR")
    
    async def _handle_async_response(self, response: aiohttp.ClientResponse) -> Dict[str, Any]:
        """Handle async API response"""
        
        if not response.ok:
            try:
                error_data = await response.json()
            except ValueError:
                error_data = {}
            
            raise SnapLearnAIError(
                error_data.get('detail', f"HTTP {response.status}: {response.reason}"),
                "API_ERROR",
                {"status_code": response.status, **error_data}
            )
        
        try:
            return await response.json()
        except ValueError:
            text = await response.text()
            return {"message": text}


# Export main classes
__all__ = [
    'SnapLearnAI',
    'AsyncSnapLearnAI',
    'SnapLearnAIError',
    'SnapLearnUtils',
    'StudentProfile',
    'GradeLevel',
    'LearningStyle',
    'VideoQuality',
    'AnimationStyle'
]


if __name__ == "__main__":
    # Example usage
    print("SnapLearn AI Python SDK Example Usage:\n")
    
    # Synchronous usage
    example_sync = """
# Initialize client
snaplearn = SnapLearnAI(api_key='your-api-key')

# Generate explanation
explanation = await snaplearn.tutoring.generate_explanation(
    question='What is 2 + 2?',
    student_id='student_123',
    grade_level='2'
)

# Process image
with open('math_problem.jpg', 'rb') as f:
    result = await snaplearn.multimodal.process_image(
        image_file=f,
        student_id='student_123'
    )

# Generate video
video = await snaplearn.video.generate_video(
    topic='Quadratic Equations',
    student_id='student_123',
    grade_level='10',
    animation_style=AnimationStyle.MATHEMATICAL,
    quality=VideoQuality.HIGH
)

# Create assessment
assessment = await snaplearn.assessment.create_assessment(
    template_id='high_school_algebra',
    student_id='student_123'
)
"""
    
    # Async context manager usage
    example_async = """
# Async context manager usage
async def main():
    async with AsyncSnapLearnAI(api_key='your-api-key') as snaplearn:
        # Generate explanation
        explanation = await snaplearn.tutoring.generate_explanation(
            question='Explain photosynthesis',
            student_id='student_456',
            grade_level='7'
        )
        
        # Start demo session
        demo = await snaplearn.demo.start_session(
            scenario='middle_school_science',
            visitor_info={'organization': 'My School'}
        )
        
        print(f"Demo started: {demo['session_id']}")

# Run async example
import asyncio
asyncio.run(main())
"""
    
    print("Synchronous Usage:")
    print(example_sync)
    print("\nAsync Context Manager Usage:")
    print(example_async)
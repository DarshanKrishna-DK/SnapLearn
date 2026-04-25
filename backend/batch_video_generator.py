"""
Batch Video Generation System for SnapLearn AI - Phase 4
Generates multiple interconnected videos for learning paths and curricula
"""

import os
import logging
import asyncio
import json
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from pathlib import Path
from dataclasses import dataclass
from enum import Enum
import uuid

from models import (
    StudentProfile,
    LearningPathRequest,
    LearningPathResponse,
    VideoResponse
)
from enhanced_manim_generator import EnhancedManimGenerator, VideoQuality, VideoFormat, AnimationStyle
from utils import schedule_async_init

logger = logging.getLogger(__name__)

class BatchStatus(str, Enum):
    """Batch generation status"""
    QUEUED = "queued"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class VideoSequenceType(str, Enum):
    """Types of video sequences"""
    LINEAR_PROGRESSION = "linear_progression"         # Sequential learning path
    BRANCHED_EXPLORATION = "branched_exploration"     # Multiple topic branches
    SPIRAL_CURRICULUM = "spiral_curriculum"           # Revisiting concepts with depth
    SKILL_BUILDING = "skill_building"                 # Building specific skills
    ASSESSMENT_PREP = "assessment_prep"               # Exam preparation sequence

@dataclass
class VideoJob:
    """Individual video job in a batch"""
    job_id: str
    topic: str
    sequence_position: int
    prerequisites: List[str]
    learning_objectives: List[str]
    difficulty_level: str
    estimated_duration: int
    video_quality: VideoQuality
    video_format: VideoFormat
    animation_style: AnimationStyle
    personalization_context: Dict[str, Any]
    status: BatchStatus = BatchStatus.QUEUED
    created_at: datetime = None
    completed_at: Optional[datetime] = None
    video_response: Optional[VideoResponse] = None
    error_message: Optional[str] = None

@dataclass 
class BatchVideoRequest:
    """Batch video generation request"""
    batch_id: str
    student_id: str
    learning_path: LearningPathResponse
    sequence_type: VideoSequenceType
    video_jobs: List[VideoJob]
    batch_settings: Dict[str, Any]
    priority: int = 5  # 1 (highest) to 10 (lowest)
    created_at: datetime = None
    estimated_completion: Optional[datetime] = None

class BatchVideoGenerator:
    """Manages batch generation of educational videos for learning paths"""
    
    def __init__(self):
        self.enhanced_generator = EnhancedManimGenerator()
        self.gemini_client = None
        
        # Batch management
        self.active_batches: Dict[str, BatchVideoRequest] = {}
        self.batch_queue: List[str] = []
        self.processing_batch_id: Optional[str] = None
        
        # Performance tracking
        self.batch_analytics = {}
        self.generation_metrics = {
            "total_batches": 0,
            "successful_batches": 0,
            "total_videos_generated": 0,
            "average_batch_time": 0.0,
            "error_rate": 0.0
        }
        
        # Resource management
        self.max_concurrent_jobs = 2  # Limit concurrent video generation
        self.batch_timeout_minutes = 60  # Maximum time for batch completion
        
        # Initialize Gemini for sequence planning
        schedule_async_init(self._init_gemini())
    
    async def _init_gemini(self):
        """Initialize Gemini for batch planning and script coordination"""
        try:
            from google import genai
            
            api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
            if not api_key:
                logger.error("Gemini API key not found for batch video generation")
                return
            
            self.gemini_client = genai.Client(api_key=api_key)
            logger.info("Batch video generator: Gemini client initialized")
            
        except ImportError:
            logger.error("Google GenAI library not installed for batch generation")
        except Exception as e:
            logger.error(f"Error initializing Gemini for batch generation: {str(e)}")
    
    async def create_learning_path_videos(self, 
                                        request: LearningPathRequest,
                                        student_profile: StudentProfile,
                                        sequence_type: VideoSequenceType = VideoSequenceType.LINEAR_PROGRESSION,
                                        video_settings: Optional[Dict[str, Any]] = None) -> str:
        """Create batch video generation for a learning path"""
        try:
            logger.info(f"Creating learning path videos for student {request.student_id}")
            
            # Generate optimized learning path if not provided
            if not hasattr(request, 'learning_path_response'):
                learning_path = await self._generate_learning_path(request, student_profile)
            else:
                learning_path = request.learning_path_response
            
            # Plan video sequence
            video_sequence = await self._plan_video_sequence(
                learning_path, student_profile, sequence_type
            )
            
            # Create video jobs
            video_jobs = await self._create_video_jobs(
                video_sequence, student_profile, video_settings or {}
            )
            
            # Create batch request
            batch_id = f"batch_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"
            
            batch_request = BatchVideoRequest(
                batch_id=batch_id,
                student_id=request.student_id,
                learning_path=learning_path,
                sequence_type=sequence_type,
                video_jobs=video_jobs,
                batch_settings=video_settings or {},
                created_at=datetime.now(),
                estimated_completion=self._estimate_batch_completion(video_jobs)
            )
            
            # Queue batch for processing
            self.active_batches[batch_id] = batch_request
            self.batch_queue.append(batch_id)
            
            # Start processing if not already running
            if not self.processing_batch_id:
                asyncio.create_task(self._process_batch_queue())
            
            logger.info(f"Learning path video batch created: {batch_id} with {len(video_jobs)} videos")
            
            return batch_id
            
        except Exception as e:
            logger.error(f"Error creating learning path videos: {str(e)}")
            raise Exception(f"Batch video creation failed: {str(e)}")
    
    async def _generate_learning_path(self, 
                                    request: LearningPathRequest,
                                    student_profile: StudentProfile) -> LearningPathResponse:
        """Generate optimized learning path if not provided"""
        
        if not self.gemini_client:
            return self._create_fallback_learning_path(request)
        
        try:
            learning_path_prompt = f"""Create an optimal learning path for video-based instruction:

STUDENT PROFILE:
- Grade Level: {student_profile.grade_level.value}
- Learning Style: {student_profile.learning_style.value}
- Confusion Areas: {list(student_profile.confusion_patterns.keys())[:3]}
- Success Areas: {list(student_profile.success_patterns.keys())[:3]}

LEARNING REQUEST:
- Target Topics: {', '.join(request.target_topics)}
- Available Time: {request.time_available} minutes
- Preferences: {request.preferences}

VIDEO-OPTIMIZED REQUIREMENTS:
1. Design for 3-8 minute video segments
2. Ensure each video builds on previous concepts
3. Include natural pause points for engagement
4. Plan for visual demonstrations and animations
5. Balance conceptual understanding with practical application

Create a learning sequence optimized for video-based learning with clear prerequisites and learning objectives.

RESPONSE FORMAT (JSON):
{{
  "path_id": "generated_path_id",
  "recommended_sequence": [
    {{
      "topic": "Topic 1",
      "duration_minutes": 5,
      "difficulty": "easy",
      "learning_objectives": ["objective1", "objective2"],
      "prerequisites": [],
      "video_focus": "introduction and basic concepts"
    }}
  ],
  "estimated_duration": {request.time_available},
  "difficulty_progression": ["easy", "medium", "hard"],
  "checkpoint_assessments": [],
  "personalization_notes": ["reason1", "reason2"]
}}"""

            response = self.gemini_client.models.generate_content(
                model="gemini-2.5-flash",
                contents=learning_path_prompt
            )
            
            response_text = response.text
            
            # Parse response
            try:
                if response_text.strip().startswith('{'):
                    path_data = json.loads(response_text)
                else:
                    import re
                    json_match = re.search(r'```json\s*(\{.*?\})\s*```', response_text, re.DOTALL)
                    if json_match:
                        path_data = json.loads(json_match.group(1))
                    else:
                        raise ValueError("Could not parse learning path JSON")
            except:
                return self._create_fallback_learning_path(request)
            
            # Convert to LearningPathResponse
            return LearningPathResponse(
                path_id=path_data.get("path_id", f"path_{datetime.now().strftime('%Y%m%d_%H%M%S')}"),
                recommended_sequence=path_data.get("recommended_sequence", []),
                estimated_duration=path_data.get("estimated_duration", request.time_available),
                difficulty_progression=path_data.get("difficulty_progression", ["medium"]),
                checkpoint_assessments=path_data.get("checkpoint_assessments", []),
                personalization_notes=path_data.get("personalization_notes", [])
            )
            
        except Exception as e:
            logger.error(f"Error generating learning path: {str(e)}")
            return self._create_fallback_learning_path(request)
    
    def _create_fallback_learning_path(self, request: LearningPathRequest) -> LearningPathResponse:
        """Create fallback learning path when AI generation fails"""
        
        # Simple sequential path
        sequence = []
        duration_per_topic = request.time_available // len(request.target_topics)
        
        for i, topic in enumerate(request.target_topics):
            sequence.append({
                "topic": topic,
                "duration_minutes": duration_per_topic,
                "difficulty": "medium",
                "learning_objectives": [f"understand_{topic.lower().replace(' ', '_')}"],
                "prerequisites": [request.target_topics[i-1]] if i > 0 else [],
                "video_focus": "comprehensive overview"
            })
        
        return LearningPathResponse(
            path_id=f"fallback_path_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            recommended_sequence=sequence,
            estimated_duration=request.time_available,
            difficulty_progression=["medium"] * len(request.target_topics),
            checkpoint_assessments=[],
            personalization_notes=["Generated fallback learning path"]
        )
    
    async def _plan_video_sequence(self, 
                                 learning_path: LearningPathResponse,
                                 student_profile: StudentProfile,
                                 sequence_type: VideoSequenceType) -> Dict[str, Any]:
        """Plan the video sequence with narrative flow and visual continuity"""
        
        if not self.gemini_client:
            return self._create_basic_sequence_plan(learning_path)
        
        try:
            sequence_prompt = f"""Plan a cohesive video sequence for educational content:

LEARNING PATH:
{json.dumps({
    "topics": [item["topic"] for item in learning_path.recommended_sequence],
    "difficulties": learning_path.difficulty_progression,
    "total_duration": learning_path.estimated_duration
}, indent=2)}

STUDENT CONTEXT:
- Grade Level: {student_profile.grade_level.value}
- Learning Style: {student_profile.learning_style.value}
- Sequence Type: {sequence_type.value}

VIDEO SEQUENCE PLANNING:
1. Create narrative flow connecting all videos
2. Plan visual consistency and branding
3. Design smooth conceptual transitions
4. Include engagement hooks and callbacks
5. Plan for optimal video lengths (3-8 minutes each)

RESPONSE FORMAT (JSON):
{{
  "sequence_narrative": "overall story arc description",
  "visual_consistency": {{
    "color_scheme": "color palette",
    "animation_style": "consistent style approach",
    "branding_elements": ["element1", "element2"]
  }},
  "video_connections": [
    {{
      "video_index": 0,
      "opening_callback": "reference to previous video",
      "closing_teaser": "preview of next video",
      "transition_elements": ["element1", "element2"]
    }}
  ],
  "engagement_strategy": {{
    "hooks": ["hook1", "hook2"],
    "recurring_themes": ["theme1", "theme2"],
    "interactive_moments": ["moment1", "moment2"]
  }},
  "pacing_strategy": "overall pacing approach"
}}"""

            response = self.gemini_client.models.generate_content(
                model="gemini-2.5-flash",
                contents=sequence_prompt
            )
            
            response_text = response.text
            
            # Parse sequence plan
            try:
                if response_text.strip().startswith('{'):
                    sequence_plan = json.loads(response_text)
                else:
                    import re
                    json_match = re.search(r'```json\s*(\{.*?\})\s*```', response_text, re.DOTALL)
                    if json_match:
                        sequence_plan = json.loads(json_match.group(1))
                    else:
                        raise ValueError("Could not parse sequence plan")
            except:
                return self._create_basic_sequence_plan(learning_path)
            
            # Add learning path data
            sequence_plan["learning_path"] = learning_path
            sequence_plan["sequence_type"] = sequence_type
            
            return sequence_plan
            
        except Exception as e:
            logger.error(f"Error planning video sequence: {str(e)}")
            return self._create_basic_sequence_plan(learning_path)
    
    def _create_basic_sequence_plan(self, learning_path: LearningPathResponse) -> Dict[str, Any]:
        """Create basic sequence plan when AI planning fails"""
        
        return {
            "sequence_narrative": "Progressive learning sequence covering all target topics",
            "visual_consistency": {
                "color_scheme": "blue_and_white_educational",
                "animation_style": "clean_and_modern",
                "branding_elements": ["SnapLearn logo", "consistent typography"]
            },
            "video_connections": [
                {
                    "video_index": i,
                    "opening_callback": f"Building on {learning_path.recommended_sequence[i-1]['topic']}" if i > 0 else "Welcome to our learning journey",
                    "closing_teaser": f"Next, we'll explore {learning_path.recommended_sequence[i+1]['topic']}" if i < len(learning_path.recommended_sequence)-1 else "Congratulations on completing this learning path!",
                    "transition_elements": ["progress_indicator", "concept_recap"]
                }
                for i in range(len(learning_path.recommended_sequence))
            ],
            "engagement_strategy": {
                "hooks": ["real_world_applications", "curiosity_questions"],
                "recurring_themes": ["building_understanding", "practical_application"],
                "interactive_moments": ["pause_and_think", "self_check_questions"]
            },
            "pacing_strategy": "steady_progression_with_reinforcement",
            "learning_path": learning_path,
            "sequence_type": VideoSequenceType.LINEAR_PROGRESSION
        }
    
    async def _create_video_jobs(self, 
                               sequence_plan: Dict[str, Any],
                               student_profile: StudentProfile,
                               video_settings: Dict[str, Any]) -> List[VideoJob]:
        """Create individual video jobs from sequence plan"""
        
        jobs = []
        learning_path = sequence_plan["learning_path"]
        visual_consistency = sequence_plan.get("visual_consistency", {})
        video_connections = sequence_plan.get("video_connections", [])
        
        # Default video settings
        default_quality = VideoQuality(video_settings.get("quality", VideoQuality.HIGH.value))
        default_format = VideoFormat(video_settings.get("format", VideoFormat.MP4.value))
        default_style = AnimationStyle(video_settings.get("animation_style", AnimationStyle.MODERN.value))
        
        for i, topic_item in enumerate(learning_path.recommended_sequence):
            # Get connection info for this video
            connection_info = next(
                (conn for conn in video_connections if conn["video_index"] == i),
                {"opening_callback": "", "closing_teaser": "", "transition_elements": []}
            )
            
            # Build personalization context
            personalization_context = {
                "student_profile": {
                    "grade_level": student_profile.grade_level.value,
                    "learning_style": student_profile.learning_style.value,
                    "confusion_patterns": list(student_profile.confusion_patterns.keys())[:3],
                    "success_patterns": list(student_profile.success_patterns.keys())[:3]
                },
                "sequence_context": {
                    "position": i + 1,
                    "total_videos": len(learning_path.recommended_sequence),
                    "narrative_flow": sequence_plan.get("sequence_narrative", ""),
                    "opening_callback": connection_info["opening_callback"],
                    "closing_teaser": connection_info["closing_teaser"],
                    "transition_elements": connection_info["transition_elements"]
                },
                "visual_consistency": visual_consistency,
                "engagement_strategy": sequence_plan.get("engagement_strategy", {}),
                "pacing_strategy": sequence_plan.get("pacing_strategy", "medium")
            }
            
            # Create video job
            job = VideoJob(
                job_id=f"job_{i+1:03d}_{uuid.uuid4().hex[:8]}",
                topic=topic_item["topic"],
                sequence_position=i + 1,
                prerequisites=topic_item.get("prerequisites", []),
                learning_objectives=topic_item.get("learning_objectives", []),
                difficulty_level=topic_item.get("difficulty", "medium"),
                estimated_duration=topic_item.get("duration_minutes", 5) * 60,  # Convert to seconds
                video_quality=default_quality,
                video_format=default_format,
                animation_style=default_style,
                personalization_context=personalization_context,
                created_at=datetime.now()
            )
            
            jobs.append(job)
        
        return jobs
    
    def _estimate_batch_completion(self, video_jobs: List[VideoJob]) -> datetime:
        """Estimate when batch will complete"""
        
        # Estimate generation time per video (including queue time)
        avg_generation_time_minutes = 8  # 8 minutes per video on average
        total_estimated_minutes = len(video_jobs) * avg_generation_time_minutes
        
        # Add buffer for queue processing and potential retries
        total_estimated_minutes *= 1.3
        
        return datetime.now() + timedelta(minutes=total_estimated_minutes)
    
    async def _process_batch_queue(self):
        """Process batches in the queue"""
        try:
            while self.batch_queue:
                batch_id = self.batch_queue.pop(0)
                
                if batch_id not in self.active_batches:
                    continue
                
                self.processing_batch_id = batch_id
                batch_request = self.active_batches[batch_id]
                
                logger.info(f"Processing batch: {batch_id} with {len(batch_request.video_jobs)} videos")
                
                # Process batch
                success = await self._process_single_batch(batch_request)
                
                # Update metrics
                self._update_batch_metrics(batch_request, success)
                
                self.processing_batch_id = None
                
                # Brief pause between batches
                await asyncio.sleep(2)
                
        except Exception as e:
            logger.error(f"Error processing batch queue: {str(e)}")
            self.processing_batch_id = None
    
    async def _process_single_batch(self, batch_request: BatchVideoRequest) -> bool:
        """Process a single batch of video generation jobs"""
        try:
            start_time = datetime.now()
            successful_jobs = 0
            
            # Create semaphore to limit concurrent jobs
            semaphore = asyncio.Semaphore(self.max_concurrent_jobs)
            
            # Process jobs with dependency resolution
            completed_jobs = set()
            
            async def process_job_with_semaphore(job: VideoJob):
                async with semaphore:
                    return await self._process_single_video_job(job, batch_request)
            
            # Process jobs in dependency order
            while len(completed_jobs) < len(batch_request.video_jobs):
                # Find jobs ready to process (prerequisites met)
                ready_jobs = [
                    job for job in batch_request.video_jobs
                    if job.job_id not in completed_jobs
                    and all(prereq in [completed.topic for completed in 
                           [j for j in batch_request.video_jobs if j.job_id in completed_jobs]]
                           or not prereq  # No prerequisites
                           for prereq in job.prerequisites)
                ]
                
                if not ready_jobs:
                    # No jobs ready - might be circular dependencies or all completed
                    break
                
                # Process ready jobs concurrently
                tasks = [process_job_with_semaphore(job) for job in ready_jobs[:self.max_concurrent_jobs]]
                
                if tasks:
                    results = await asyncio.gather(*tasks, return_exceptions=True)
                    
                    for i, result in enumerate(results):
                        job = ready_jobs[i]
                        if isinstance(result, Exception):
                            job.status = BatchStatus.FAILED
                            job.error_message = str(result)
                            logger.error(f"Job {job.job_id} failed: {result}")
                        else:
                            job.status = BatchStatus.COMPLETED
                            job.completed_at = datetime.now()
                            job.video_response = result
                            successful_jobs += 1
                            logger.info(f"Job {job.job_id} completed successfully")
                        
                        completed_jobs.add(job.job_id)
                
                # Check timeout
                if (datetime.now() - start_time).total_seconds() > self.batch_timeout_minutes * 60:
                    logger.warning(f"Batch {batch_request.batch_id} timed out")
                    break
            
            # Update batch status
            total_jobs = len(batch_request.video_jobs)
            success_rate = successful_jobs / total_jobs
            
            if success_rate >= 0.8:  # 80% success rate considered successful batch
                logger.info(f"Batch {batch_request.batch_id} completed successfully: {successful_jobs}/{total_jobs} videos")
                return True
            else:
                logger.warning(f"Batch {batch_request.batch_id} partially failed: {successful_jobs}/{total_jobs} videos")
                return False
                
        except Exception as e:
            logger.error(f"Error processing batch {batch_request.batch_id}: {str(e)}")
            return False
    
    async def _process_single_video_job(self, 
                                      job: VideoJob,
                                      batch_request: BatchVideoRequest) -> VideoResponse:
        """Process a single video generation job"""
        try:
            logger.info(f"Processing video job: {job.job_id} - {job.topic}")
            
            job.status = BatchStatus.PROCESSING
            
            # Get student profile
            from memory import MemoryManager
            memory_manager = MemoryManager()
            student_profile = await memory_manager.get_student_profile(batch_request.student_id)
            
            # Generate video using enhanced generator with full context
            video_result = await self.enhanced_generator.generate_contextual_video(
                topic=job.topic,
                student_profile=student_profile,
                conversation_context=None,  # Could be enhanced to include conversation
                learning_analytics=None,    # Could include learning analytics
                video_quality=job.video_quality,
                video_format=job.video_format,
                animation_style=job.animation_style,
                target_duration=job.estimated_duration
            )
            
            # Create VideoResponse from result
            video_response = VideoResponse(
                video_url=video_result["video_url"],
                video_id=video_result["video_id"],
                topic=video_result["topic"],
                duration_seconds=video_result["duration_seconds"],
                file_size_mb=video_result["file_size_mb"],
                manim_script=video_result["manim_script"],
                generation_time_seconds=video_result["generation_time_seconds"],
                timestamp=datetime.now()
            )
            
            return video_response
            
        except Exception as e:
            logger.error(f"Error processing video job {job.job_id}: {str(e)}")
            raise Exception(f"Video job processing failed: {str(e)}")
    
    def _update_batch_metrics(self, batch_request: BatchVideoRequest, success: bool):
        """Update batch processing metrics"""
        
        self.generation_metrics["total_batches"] += 1
        
        if success:
            self.generation_metrics["successful_batches"] += 1
        
        successful_videos = sum(1 for job in batch_request.video_jobs if job.status == BatchStatus.COMPLETED)
        self.generation_metrics["total_videos_generated"] += successful_videos
        
        # Update success rate
        if self.generation_metrics["total_batches"] > 0:
            success_rate = self.generation_metrics["successful_batches"] / self.generation_metrics["total_batches"]
            self.generation_metrics["error_rate"] = 1.0 - success_rate
        
        # Calculate batch duration
        if batch_request.video_jobs:
            start_time = min(job.created_at for job in batch_request.video_jobs if job.created_at)
            end_time = max(job.completed_at or datetime.now() for job in batch_request.video_jobs)
            batch_duration_minutes = (end_time - start_time).total_seconds() / 60
            
            # Update average batch time
            total_batches = self.generation_metrics["total_batches"]
            current_avg = self.generation_metrics["average_batch_time"]
            self.generation_metrics["average_batch_time"] = (
                (current_avg * (total_batches - 1) + batch_duration_minutes) / total_batches
            )
    
    async def get_batch_status(self, batch_id: str) -> Optional[Dict[str, Any]]:
        """Get status of a batch generation request"""
        
        if batch_id not in self.active_batches:
            return None
        
        batch_request = self.active_batches[batch_id]
        
        # Calculate progress
        total_jobs = len(batch_request.video_jobs)
        completed_jobs = sum(1 for job in batch_request.video_jobs if job.status == BatchStatus.COMPLETED)
        failed_jobs = sum(1 for job in batch_request.video_jobs if job.status == BatchStatus.FAILED)
        processing_jobs = sum(1 for job in batch_request.video_jobs if job.status == BatchStatus.PROCESSING)
        
        # Determine overall status
        if completed_jobs == total_jobs:
            overall_status = BatchStatus.COMPLETED
        elif failed_jobs > 0 and (completed_jobs + failed_jobs) == total_jobs:
            overall_status = BatchStatus.FAILED
        elif processing_jobs > 0 or batch_id == self.processing_batch_id:
            overall_status = BatchStatus.PROCESSING
        else:
            overall_status = BatchStatus.QUEUED
        
        return {
            "batch_id": batch_id,
            "status": overall_status.value,
            "progress": {
                "total_videos": total_jobs,
                "completed": completed_jobs,
                "failed": failed_jobs,
                "processing": processing_jobs,
                "queued": total_jobs - completed_jobs - failed_jobs - processing_jobs,
                "completion_percentage": (completed_jobs / total_jobs) * 100 if total_jobs > 0 else 0
            },
            "estimated_completion": batch_request.estimated_completion.isoformat() if batch_request.estimated_completion else None,
            "created_at": batch_request.created_at.isoformat(),
            "video_jobs": [
                {
                    "job_id": job.job_id,
                    "topic": job.topic,
                    "status": job.status.value,
                    "sequence_position": job.sequence_position,
                    "video_url": job.video_response.video_url if job.video_response else None,
                    "error_message": job.error_message
                }
                for job in batch_request.video_jobs
            ],
            "learning_path": {
                "path_id": batch_request.learning_path.path_id,
                "total_duration": batch_request.learning_path.estimated_duration,
                "difficulty_progression": batch_request.learning_path.difficulty_progression
            }
        }
    
    async def cancel_batch(self, batch_id: str) -> bool:
        """Cancel a batch generation request"""
        try:
            if batch_id not in self.active_batches:
                return False
            
            batch_request = self.active_batches[batch_id]
            
            # Mark all pending jobs as cancelled
            for job in batch_request.video_jobs:
                if job.status in [BatchStatus.QUEUED, BatchStatus.PROCESSING]:
                    job.status = BatchStatus.CANCELLED
            
            # Remove from queue if still queued
            if batch_id in self.batch_queue:
                self.batch_queue.remove(batch_id)
            
            logger.info(f"Batch {batch_id} cancelled successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error cancelling batch {batch_id}: {str(e)}")
            return False
    
    async def get_batch_analytics(self) -> Dict[str, Any]:
        """Get comprehensive batch processing analytics"""
        
        # Active batch information
        active_batch_info = []
        for batch_id, batch_request in self.active_batches.items():
            status = await self.get_batch_status(batch_id)
            if status:
                active_batch_info.append({
                    "batch_id": batch_id,
                    "student_id": batch_request.student_id,
                    "video_count": len(batch_request.video_jobs),
                    "status": status["status"],
                    "completion_percentage": status["progress"]["completion_percentage"],
                    "created_at": batch_request.created_at.isoformat()
                })
        
        return {
            "generation_metrics": self.generation_metrics,
            "active_batches": len(self.active_batches),
            "queue_length": len(self.batch_queue),
            "currently_processing": self.processing_batch_id,
            "active_batch_details": active_batch_info,
            "system_health": {
                "enhanced_generator_healthy": self.enhanced_generator.is_healthy(),
                "gemini_available": self.gemini_client is not None,
                "max_concurrent_jobs": self.max_concurrent_jobs,
                "batch_timeout_minutes": self.batch_timeout_minutes
            }
        }
    
    async def cleanup_old_batches(self, days_old: int = 7):
        """Clean up old batch data to save memory and storage"""
        try:
            cutoff_date = datetime.now() - timedelta(days=days_old)
            
            batches_to_remove = []
            
            for batch_id, batch_request in self.active_batches.items():
                if batch_request.created_at < cutoff_date:
                    # Only remove completed or failed batches
                    completed_jobs = sum(1 for job in batch_request.video_jobs if job.status in [BatchStatus.COMPLETED, BatchStatus.FAILED, BatchStatus.CANCELLED])
                    
                    if completed_jobs == len(batch_request.video_jobs):
                        batches_to_remove.append(batch_id)
            
            # Remove old batches
            for batch_id in batches_to_remove:
                del self.active_batches[batch_id]
                logger.info(f"Cleaned up old batch: {batch_id}")
                
            logger.info(f"Cleaned up {len(batches_to_remove)} old batches")
            
        except Exception as e:
            logger.error(f"Error cleaning up old batches: {str(e)}")
    
    def is_healthy(self) -> bool:
        """Check if batch video generator is healthy"""
        return (
            self.enhanced_generator.is_healthy() and
            len(self.batch_queue) < 50 and  # Not overloaded with batches
            self.generation_metrics["error_rate"] < 0.5  # Less than 50% error rate
        )
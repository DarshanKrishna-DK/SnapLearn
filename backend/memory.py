"""
Memory Manager for SnapLearn AI
Handles student profile persistence with Supabase + local JSON fallback
"""

import json
import os
import logging
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from pathlib import Path

from models import (
    StudentProfile,
    ConceptMastery,
    LearningSession,
    GradeLevel,
    LanguageCode,
    LearningStyle,
)
from utils import schedule_async_init

logger = logging.getLogger(__name__)

class MemoryManager:
    """Manages student memory with Supabase + local JSON fallback"""
    
    def __init__(self):
        self.data_dir = Path("../data")
        self.data_dir.mkdir(exist_ok=True)
        self.local_db_path = self.data_dir / "students.json"
        
        # Initialize connection states
        self.supabase_client = None
        self.use_local_mode = True
        self.connection_checked = False
        
        # Initialize local database
        self._init_local_db()
        
        # Try to connect to Supabase (works at import time and under uvicorn)
        schedule_async_init(self._init_supabase())
    
    def _init_local_db(self):
        """Initialize local JSON database if it doesn't exist"""
        if not self.local_db_path.exists():
            initial_data = {
                "students": {},
                "sessions": {},
                "videos": {},
                "metadata": {
                    "created_at": datetime.now().isoformat(),
                    "last_updated": datetime.now().isoformat(),
                    "version": "1.0.0"
                }
            }
            self._save_local_data(initial_data)
            logger.info("Initialized local database")
    
    async def _init_supabase(self):
        """Initialize Supabase connection with error handling"""
        try:
            # Check if Supabase credentials are available
            supabase_url = os.getenv("SUPABASE_URL")
            supabase_key = os.getenv("SUPABASE_ANON_KEY")
            
            if not supabase_url or not supabase_key:
                logger.info("Supabase credentials not found, using local mode")
                self.use_local_mode = True
                return
            
            # Try to import and initialize Supabase
            from supabase import create_client, Client
            
            self.supabase_client: Client = create_client(supabase_url, supabase_key)
            
            # Test connection
            response = await self._test_supabase_connection()
            if response:
                self.use_local_mode = False
                logger.info("Supabase connected successfully")
            else:
                self.use_local_mode = True
                logger.warning("Supabase connection failed, using local mode")
                
        except ImportError:
            logger.warning("Supabase client not installed, using local mode")
            self.use_local_mode = True
        except Exception as e:
            logger.error(f"Supabase initialization error: {str(e)}")
            self.use_local_mode = True
        
        self.connection_checked = True
    
    async def _test_supabase_connection(self) -> bool:
        """Test Supabase connection"""
        try:
            if not self.supabase_client:
                return False
            
            # Try a simple query to test connection
            response = self.supabase_client.table('student_profiles').select("id").limit(1).execute()
            return True
        except Exception as e:
            logger.error(f"Supabase connection test failed: {str(e)}")
            return False
    
    def _load_local_data(self) -> Dict[str, Any]:
        """Load data from local JSON file"""
        try:
            with open(self.local_db_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            self._init_local_db()
            return self._load_local_data()
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error: {str(e)}")
            # Backup corrupted file and create new one
            backup_path = self.local_db_path.with_suffix('.json.backup')
            if self.local_db_path.exists():
                self.local_db_path.rename(backup_path)
            self._init_local_db()
            return self._load_local_data()
    
    def _save_local_data(self, data: Dict[str, Any]):
        """Save data to local JSON file"""
        try:
            data["metadata"]["last_updated"] = datetime.now().isoformat()
            
            # Atomic write with temporary file
            temp_path = self.local_db_path.with_suffix('.json.tmp')
            with open(temp_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False, default=str)
            
            temp_path.replace(self.local_db_path)
            
        except Exception as e:
            logger.error(f"Error saving local data: {str(e)}")
            raise
    
    async def get_student_profile(self, student_id: str) -> Optional[StudentProfile]:
        """Get student profile from Supabase or local storage"""
        try:
            # Try Supabase first if available
            if not self.use_local_mode and self.supabase_client:
                profile_data = await self._get_supabase_profile(student_id)
                if profile_data:
                    return StudentProfile(**profile_data)
            
            # Fallback to local storage
            data = self._load_local_data()
            student_data = data["students"].get(student_id)
            
            if student_data:
                return StudentProfile(**student_data)
            
            # Create new student profile if not found
            return await self._create_new_student_profile(student_id)
            
        except Exception as e:
            logger.error(f"Error getting student profile: {str(e)}")
            return await self._create_new_student_profile(student_id)
    
    async def _get_supabase_profile(self, student_id: str) -> Optional[Dict[str, Any]]:
        """Get student profile from Supabase"""
        try:
            response = self.supabase_client.table('student_profiles').select("*").eq('student_id', student_id).execute()
            
            if response.data and len(response.data) > 0:
                return response.data[0]
            return None
            
        except Exception as e:
            logger.error(f"Supabase query error: {str(e)}")
            return None
    
    async def _create_new_student_profile(self, student_id: str) -> StudentProfile:
        """Create a new student profile with defaults"""
        new_profile = StudentProfile(
            student_id=student_id,
            grade_level=GradeLevel.GRADE_4,  # Default grade
            preferred_language=LanguageCode.ENGLISH,
            learning_style=LearningStyle.MIXED,
            explanation_style_preference="balanced",
            difficulty_preference="adaptive"
        )
        
        # Save the new profile
        await self.save_student_profile(new_profile)
        
        logger.info(f"Created new student profile for {student_id}")
        return new_profile
    
    async def save_student_profile(self, profile: StudentProfile) -> bool:
        """Save student profile to both Supabase and local storage"""
        try:
            profile.updated_at = datetime.now()
            profile_dict = profile.dict()
            
            # Try Supabase first
            if not self.use_local_mode and self.supabase_client:
                await self._save_supabase_profile(profile_dict)
            
            # Always save locally as backup
            data = self._load_local_data()
            data["students"][profile.student_id] = profile_dict
            self._save_local_data(data)
            
            return True
            
        except Exception as e:
            logger.error(f"Error saving student profile: {str(e)}")
            return False
    
    async def _save_supabase_profile(self, profile_dict: Dict[str, Any]):
        """Save profile to Supabase"""
        try:
            # Check if profile exists
            existing = await self._get_supabase_profile(profile_dict["student_id"])
            
            if existing:
                # Update existing profile
                self.supabase_client.table('student_profiles').update(profile_dict).eq('student_id', profile_dict["student_id"]).execute()
            else:
                # Insert new profile
                self.supabase_client.table('student_profiles').insert(profile_dict).execute()
                
        except Exception as e:
            logger.error(f"Supabase save error: {str(e)}")
            raise
    
    async def update_student_interaction(self, student_id: str, question: str, 
                                       explanation: str, grade_level: str):
        """Update student profile with new interaction"""
        try:
            profile = await self.get_student_profile(student_id)
            if not profile:
                return False
            
            # Update counters
            profile.total_questions += 1
            profile.updated_at = datetime.now()
            
            # Create learning session if needed
            session_id = f"{student_id}_{datetime.now().strftime('%Y%m%d_%H')}"
            
            # Save updated profile
            await self.save_student_profile(profile)
            
            # Log interaction
            await self._log_interaction(student_id, question, explanation, grade_level)
            
            return True
            
        except Exception as e:
            logger.error(f"Error updating student interaction: {str(e)}")
            return False
    
    async def update_student_assessment(self, student_id: str, question: str, 
                                      answer: str, assessment: Any):
        """Update student profile with assessment results"""
        try:
            profile = await self.get_student_profile(student_id)
            if not profile:
                return False
            
            # Update confusion/success patterns
            if hasattr(assessment, 'is_correct') and assessment.is_correct:
                # Success pattern
                key = self._extract_topic_key(question)
                if key in profile.success_patterns:
                    profile.success_patterns[key] += 1
                else:
                    profile.success_patterns[key] = 1
            else:
                # Confusion pattern
                key = self._extract_topic_key(question)
                if key in profile.confusion_patterns:
                    profile.confusion_patterns[key] += 1
                else:
                    profile.confusion_patterns[key] = 1
            
            profile.updated_at = datetime.now()
            await self.save_student_profile(profile)
            
            return True
            
        except Exception as e:
            logger.error(f"Error updating student assessment: {str(e)}")
            return False
    
    def _extract_topic_key(self, question: str) -> str:
        """Extract topic key from question for pattern tracking"""
        # Simple implementation - could be enhanced with NLP
        question_lower = question.lower()
        
        # Math topics
        math_keywords = ["add", "subtract", "multiply", "divide", "fraction", "decimal", "geometry"]
        for keyword in math_keywords:
            if keyword in question_lower:
                return f"math_{keyword}"
        
        # Science topics
        science_keywords = ["physics", "chemistry", "biology", "science"]
        for keyword in science_keywords:
            if keyword in question_lower:
                return f"science_{keyword}"
        
        # Default to general
        return "general"
    
    async def _log_interaction(self, student_id: str, question: str, 
                             explanation: str, grade_level: str):
        """Log interaction to local storage"""
        try:
            data = self._load_local_data()
            
            if "interactions" not in data:
                data["interactions"] = []
            
            interaction = {
                "timestamp": datetime.now().isoformat(),
                "student_id": student_id,
                "question": question,
                "explanation": explanation,
                "grade_level": grade_level
            }
            
            data["interactions"].append(interaction)
            
            # Keep only last 1000 interactions
            if len(data["interactions"]) > 1000:
                data["interactions"] = data["interactions"][-1000:]
            
            self._save_local_data(data)
            
        except Exception as e:
            logger.error(f"Error logging interaction: {str(e)}")
    
    async def log_video_generation(self, student_id: str, topic: str, video_path: str):
        """Log video generation event"""
        try:
            data = self._load_local_data()
            
            video_record = {
                "timestamp": datetime.now().isoformat(),
                "student_id": student_id,
                "topic": topic,
                "video_path": video_path,
                "video_id": f"video_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            }
            
            if student_id not in data["videos"]:
                data["videos"][student_id] = []
            
            data["videos"][student_id].append(video_record)
            self._save_local_data(data)
            
        except Exception as e:
            logger.error(f"Error logging video generation: {str(e)}")
    
    async def get_recent_topics(self, student_id: str, limit: int = 10) -> List[str]:
        """Get recent topics for a student"""
        try:
            data = self._load_local_data()
            interactions = data.get("interactions", [])
            
            # Filter by student and get recent topics
            student_interactions = [i for i in interactions if i.get("student_id") == student_id]
            recent_interactions = sorted(student_interactions, 
                                       key=lambda x: x.get("timestamp", ""), 
                                       reverse=True)[:limit]
            
            topics = []
            for interaction in recent_interactions:
                question = interaction.get("question", "")
                if question and question not in topics:
                    topics.append(question)
            
            return topics[:limit]
            
        except Exception as e:
            logger.error(f"Error getting recent topics: {str(e)}")
            return []
    
    async def get_learning_stats(self, student_id: str) -> Dict[str, Any]:
        """Get learning statistics for a student"""
        try:
            profile = await self.get_student_profile(student_id)
            data = self._load_local_data()
            
            # Calculate stats
            total_sessions = profile.total_sessions if profile else 0
            total_questions = profile.total_questions if profile else 0
            
            # Recent activity
            recent_interactions = len([i for i in data.get("interactions", []) 
                                     if i.get("student_id") == student_id and 
                                     datetime.fromisoformat(i.get("timestamp", datetime.now().isoformat())) > 
                                     datetime.now() - timedelta(days=7)])
            
            return {
                "total_sessions": total_sessions,
                "total_questions": total_questions,
                "recent_activity": recent_interactions,
                "success_rate": self._calculate_success_rate(profile) if profile else 0.0
            }
            
        except Exception as e:
            logger.error(f"Error getting learning stats: {str(e)}")
            return {}
    
    def _calculate_success_rate(self, profile: StudentProfile) -> float:
        """Calculate success rate from patterns"""
        try:
            total_successes = sum(profile.success_patterns.values())
            total_confusions = sum(profile.confusion_patterns.values())
            total_attempts = total_successes + total_confusions
            
            if total_attempts == 0:
                return 0.5  # Default neutral rate
            
            return total_successes / total_attempts
            
        except Exception:
            return 0.5
    
    async def get_student_videos(self, student_id: str) -> List[Dict[str, Any]]:
        """Get videos generated for a student"""
        try:
            data = self._load_local_data()
            return data.get("videos", {}).get(student_id, [])
        except Exception as e:
            logger.error(f"Error getting student videos: {str(e)}")
            return []
    
    async def reset_student_profile(self, student_id: str):
        """Reset student profile for testing"""
        try:
            data = self._load_local_data()
            if student_id in data["students"]:
                del data["students"][student_id]
            
            # Clean up related data
            data["interactions"] = [i for i in data.get("interactions", []) 
                                  if i.get("student_id") != student_id]
            if student_id in data.get("videos", {}):
                del data["videos"][student_id]
            
            self._save_local_data(data)
            
        except Exception as e:
            logger.error(f"Error resetting student profile: {str(e)}")
    
    async def get_debug_info(self) -> Dict[str, Any]:
        """Get debug information about memory state"""
        try:
            data = self._load_local_data()
            
            return {
                "connection_mode": "local" if self.use_local_mode else "supabase",
                "total_students": len(data.get("students", {})),
                "total_interactions": len(data.get("interactions", [])),
                "total_videos": sum(len(videos) for videos in data.get("videos", {}).values()),
                "database_size_kb": self.local_db_path.stat().st_size / 1024 if self.local_db_path.exists() else 0,
                "last_updated": data.get("metadata", {}).get("last_updated")
            }
            
        except Exception as e:
            logger.error(f"Error getting debug info: {str(e)}")
            return {"error": str(e)}
    
    def is_healthy(self) -> bool:
        """Check if memory manager is healthy"""
        try:
            return self.local_db_path.exists() and self.connection_checked
        except Exception:
            return False
"""
Session Management System
Unified context and state management across tutoring modes
Based on DeepTutor patterns
"""

import uuid
import json
import time
import logging
from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from enum import Enum
import asyncio
from contextlib import asynccontextmanager

logger = logging.getLogger(__name__)

class TutoringMode(Enum):
    EXPLAIN = "explain"
    VIDEO = "video" 
    ASSESSMENT = "assessment"
    CONVERSATION = "conversation"
    PRACTICE = "practice"
    ANALYTICS = "analytics"

class SessionStatus(Enum):
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    ERROR = "error"

@dataclass
class UserProfile:
    student_id: str
    grade_level: int
    language: str = "en"
    learning_style: Optional[str] = None
    strengths: List[str] = None
    areas_for_improvement: List[str] = None
    preferred_explanation_style: str = "balanced"
    
    def __post_init__(self):
        if self.strengths is None:
            self.strengths = []
        if self.areas_for_improvement is None:
            self.areas_for_improvement = []

@dataclass
class SkillState:
    skill_id: str
    name: str
    mastery_level: float = 0.0  # 0.0 to 1.0
    attempts: int = 0
    correct_attempts: int = 0
    last_practiced: Optional[datetime] = None
    needs_review: bool = False

@dataclass
class SessionContext:
    session_id: str
    user_profile: UserProfile
    mode: TutoringMode
    status: SessionStatus
    created_at: datetime
    last_activity: datetime
    
    # Context data
    conversation_history: List[Dict[str, Any]]
    current_topic: Optional[str] = None
    learning_objectives: List[str] = None
    skill_states: Dict[str, SkillState] = None
    
    # Mode-specific data
    video_requests: List[Dict[str, Any]] = None
    assessment_data: Dict[str, Any] = None
    explanation_history: List[Dict[str, Any]] = None
    
    # Metadata
    total_interactions: int = 0
    mode_switches: List[Dict[str, Any]] = None
    
    def __post_init__(self):
        if self.learning_objectives is None:
            self.learning_objectives = []
        if self.skill_states is None:
            self.skill_states = {}
        if self.video_requests is None:
            self.video_requests = []
        if self.assessment_data is None:
            self.assessment_data = {}
        if self.explanation_history is None:
            self.explanation_history = []
        if self.mode_switches is None:
            self.mode_switches = []

class SessionManager:
    def __init__(self):
        self.sessions: Dict[str, SessionContext] = {}
        self.session_locks: Dict[str, asyncio.Lock] = {}
        self.cleanup_task = None
        self.start_cleanup_task()
    
    def start_cleanup_task(self):
        """Start background task to clean up old sessions"""
        if self.cleanup_task is None:
            self.cleanup_task = asyncio.create_task(self._cleanup_loop())
    
    async def _cleanup_loop(self):
        """Background cleanup of inactive sessions"""
        while True:
            try:
                await asyncio.sleep(300)  # Check every 5 minutes
                await self.cleanup_inactive_sessions()
            except Exception as e:
                logger.error(f"Error in session cleanup: {e}")
    
    async def cleanup_inactive_sessions(self, max_age_hours: int = 24):
        """Remove sessions older than max_age_hours"""
        cutoff = datetime.now() - timedelta(hours=max_age_hours)
        to_remove = []
        
        for session_id, session in self.sessions.items():
            if session.last_activity < cutoff:
                to_remove.append(session_id)
        
        for session_id in to_remove:
            await self.end_session(session_id)
            logger.info(f"Cleaned up inactive session: {session_id}")
    
    def _get_session_lock(self, session_id: str) -> asyncio.Lock:
        """Get or create lock for session"""
        if session_id not in self.session_locks:
            self.session_locks[session_id] = asyncio.Lock()
        return self.session_locks[session_id]
    
    async def create_session(
        self,
        student_id: str,
        grade_level: int = 4,
        language: str = "en",
        mode: TutoringMode = TutoringMode.EXPLAIN
    ) -> str:
        """Create a new tutoring session"""
        session_id = str(uuid.uuid4())
        
        user_profile = UserProfile(
            student_id=student_id,
            grade_level=grade_level,
            language=language
        )
        
        session = SessionContext(
            session_id=session_id,
            user_profile=user_profile,
            mode=mode,
            status=SessionStatus.ACTIVE,
            created_at=datetime.now(),
            last_activity=datetime.now(),
            conversation_history=[]
        )
        
        self.sessions[session_id] = session
        logger.info(f"Created session {session_id} for student {student_id}")
        return session_id
    
    async def get_session(self, session_id: str) -> Optional[SessionContext]:
        """Get session by ID"""
        return self.sessions.get(session_id)
    
    async def update_session_activity(self, session_id: str):
        """Update last activity timestamp"""
        if session_id in self.sessions:
            async with self._get_session_lock(session_id):
                self.sessions[session_id].last_activity = datetime.now()
                self.sessions[session_id].total_interactions += 1
    
    async def switch_mode(
        self,
        session_id: str,
        new_mode: TutoringMode,
        context: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Switch tutoring mode for a session"""
        async with self._get_session_lock(session_id):
            session = self.sessions.get(session_id)
            if not session:
                return False
            
            old_mode = session.mode
            session.mode = new_mode
            session.last_activity = datetime.now()
            
            # Record mode switch
            switch_record = {
                "timestamp": datetime.now().isoformat(),
                "from_mode": old_mode.value,
                "to_mode": new_mode.value,
                "context": context or {}
            }
            session.mode_switches.append(switch_record)
            
            logger.info(f"Session {session_id} switched from {old_mode.value} to {new_mode.value}")
            return True
    
    async def add_interaction(
        self,
        session_id: str,
        interaction_type: str,
        data: Dict[str, Any]
    ):
        """Add interaction to session history"""
        async with self._get_session_lock(session_id):
            session = self.sessions.get(session_id)
            if not session:
                return False
            
            interaction = {
                "timestamp": datetime.now().isoformat(),
                "type": interaction_type,
                "mode": session.mode.value,
                "data": data
            }
            
            session.conversation_history.append(interaction)
            await self.update_session_activity(session_id)
            
            # Update mode-specific data
            if session.mode == TutoringMode.EXPLAIN:
                session.explanation_history.append(interaction)
            elif session.mode == TutoringMode.VIDEO:
                session.video_requests.append(interaction)
    
    async def update_skill_state(
        self,
        session_id: str,
        skill_id: str,
        skill_name: str,
        correct: bool,
        difficulty: float = 0.5
    ):
        """Update skill mastery based on performance"""
        async with self._get_session_lock(session_id):
            session = self.sessions.get(session_id)
            if not session:
                return False
            
            if skill_id not in session.skill_states:
                session.skill_states[skill_id] = SkillState(
                    skill_id=skill_id,
                    name=skill_name
                )
            
            skill = session.skill_states[skill_id]
            skill.attempts += 1
            skill.last_practiced = datetime.now()
            
            if correct:
                skill.correct_attempts += 1
            
            # Simple Bayesian Knowledge Tracing update
            old_mastery = skill.mastery_level
            
            if correct:
                # Increase mastery
                skill.mastery_level = min(1.0, old_mastery + (1 - old_mastery) * 0.3)
            else:
                # Decrease mastery
                skill.mastery_level = max(0.0, old_mastery - old_mastery * 0.2)
            
            # Mark for review if mastery drops below threshold
            skill.needs_review = skill.mastery_level < 0.6
            
            logger.debug(f"Updated skill {skill_id}: mastery {old_mastery:.2f} -> {skill.mastery_level:.2f}")
            return True
    
    async def get_session_summary(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get comprehensive session summary"""
        session = await self.get_session(session_id)
        if not session:
            return None
        
        # Calculate session stats
        duration = (session.last_activity - session.created_at).total_seconds() / 60  # minutes
        
        skill_summary = {}
        for skill_id, skill in session.skill_states.items():
            accuracy = skill.correct_attempts / skill.attempts if skill.attempts > 0 else 0
            skill_summary[skill_id] = {
                "name": skill.name,
                "mastery_level": skill.mastery_level,
                "accuracy": accuracy,
                "attempts": skill.attempts,
                "needs_review": skill.needs_review
            }
        
        mode_distribution = {}
        for switch in session.mode_switches:
            mode = switch["to_mode"]
            mode_distribution[mode] = mode_distribution.get(mode, 0) + 1
        
        return {
            "session_id": session_id,
            "student_id": session.user_profile.student_id,
            "duration_minutes": duration,
            "total_interactions": session.total_interactions,
            "current_mode": session.mode.value,
            "status": session.status.value,
            "skills": skill_summary,
            "mode_distribution": mode_distribution,
            "current_topic": session.current_topic,
            "learning_objectives": session.learning_objectives
        }
    
    async def end_session(self, session_id: str) -> bool:
        """End and cleanup session"""
        if session_id in self.sessions:
            async with self._get_session_lock(session_id):
                session = self.sessions[session_id]
                session.status = SessionStatus.COMPLETED
                session.last_activity = datetime.now()
                
                # Could save to database here
                logger.info(f"Ended session {session_id}")
                
                # Clean up
                del self.sessions[session_id]
                if session_id in self.session_locks:
                    del self.session_locks[session_id]
                
                return True
        return False
    
    @asynccontextmanager
    async def session_context(self, session_id: str):
        """Context manager for safe session access"""
        async with self._get_session_lock(session_id):
            session = self.sessions.get(session_id)
            if not session:
                raise ValueError(f"Session {session_id} not found")
            
            try:
                yield session
                await self.update_session_activity(session_id)
            except Exception as e:
                session.status = SessionStatus.ERROR
                logger.error(f"Error in session {session_id}: {e}")
                raise

# Global session manager
_session_manager = None

def get_session_manager() -> SessionManager:
    global _session_manager
    if _session_manager is None:
        _session_manager = SessionManager()
    return _session_manager

async def get_or_create_session(
    student_id: str,
    session_id: Optional[str] = None,
    grade_level: int = 4,
    language: str = "en"
) -> str:
    """Get existing session or create new one"""
    manager = get_session_manager()
    
    if session_id:
        session = await manager.get_session(session_id)
        if session:
            return session_id
    
    # Create new session
    return await manager.create_session(
        student_id=student_id,
        grade_level=grade_level,
        language=language
    )
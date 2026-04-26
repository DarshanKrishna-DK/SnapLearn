"""
Student Profile System for SnapLearn AI
Tracks learning patterns, quiz performance, and adapts content difficulty
"""

import json
import os
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from enum import Enum

class LearningStyle(str, Enum):
    VISUAL = "visual"
    AUDITORY = "auditory"
    KINESTHETIC = "kinesthetic"
    READING = "reading"

class DifficultyLevel(str, Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"
    ADAPTIVE = "adaptive"

@dataclass
class QuizResult:
    topic: str
    questions_count: int
    correct_answers: int
    time_taken_seconds: int
    difficulty: DifficultyLevel
    timestamp: str
    mistakes: List[Dict[str, Any]]

@dataclass
class LearningSession:
    session_id: str
    topic: str
    duration_minutes: int
    interactions_count: int
    completion_rate: float
    timestamp: str

@dataclass
class VideoProgress:
    video_id: str
    topic: str
    watch_time_seconds: int
    total_duration_seconds: int
    completion_rate: float
    replay_count: int
    timestamp: str

@dataclass
class StudentProfile:
    student_id: str
    grade: str
    learning_style: LearningStyle
    difficulty_preference: DifficultyLevel
    quiz_accuracy: float
    total_quizzes: int
    total_learning_time_minutes: int
    strengths: List[str]
    weaknesses: List[str]
    quiz_history: List[QuizResult]
    learning_sessions: List[LearningSession]
    video_progress: List[VideoProgress]
    created_at: str
    last_updated: str
    
    @classmethod
    def create_new(cls, student_id: str, grade: str) -> 'StudentProfile':
        """Create a new student profile with default values"""
        now = datetime.now(timezone.utc).isoformat()
        return cls(
            student_id=student_id,
            grade=grade,
            learning_style=LearningStyle.VISUAL,  # Default
            difficulty_preference=DifficultyLevel.ADAPTIVE,
            quiz_accuracy=0.0,
            total_quizzes=0,
            total_learning_time_minutes=0,
            strengths=[],
            weaknesses=[],
            quiz_history=[],
            learning_sessions=[],
            video_progress=[],
            created_at=now,
            last_updated=now
        )
    
    def update_quiz_result(self, quiz_result: QuizResult):
        """Update profile based on new quiz results"""
        self.quiz_history.append(quiz_result)
        self.total_quizzes += 1
        
        # Recalculate accuracy
        total_correct = sum(q.correct_answers for q in self.quiz_history)
        total_questions = sum(q.questions_count for q in self.quiz_history)
        self.quiz_accuracy = total_correct / total_questions if total_questions > 0 else 0.0
        
        # Analyze topic performance
        self._analyze_topic_performance()
        
        # Adjust difficulty preference
        self._adjust_difficulty_preference()
        
        self.last_updated = datetime.now(timezone.utc).isoformat()
    
    def add_learning_session(self, session: LearningSession):
        """Add a learning session record"""
        self.learning_sessions.append(session)
        self.total_learning_time_minutes += session.duration_minutes
        self.last_updated = datetime.now(timezone.utc).isoformat()
    
    def add_video_progress(self, video: VideoProgress):
        """Add or update video progress"""
        # Remove existing progress for same video
        self.video_progress = [v for v in self.video_progress if v.video_id != video.video_id]
        self.video_progress.append(video)
        self.last_updated = datetime.now(timezone.utc).isoformat()
    
    def _analyze_topic_performance(self):
        """Analyze quiz performance by topic to identify strengths/weaknesses"""
        topic_performance = {}
        
        for quiz in self.quiz_history[-10:]:  # Last 10 quizzes
            topic = quiz.topic
            if topic not in topic_performance:
                topic_performance[topic] = {'correct': 0, 'total': 0}
            
            topic_performance[topic]['correct'] += quiz.correct_answers
            topic_performance[topic]['total'] += quiz.questions_count
        
        # Identify strengths (>80% accuracy) and weaknesses (<60% accuracy)
        self.strengths = []
        self.weaknesses = []
        
        for topic, performance in topic_performance.items():
            accuracy = performance['correct'] / performance['total']
            if accuracy >= 0.8:
                self.strengths.append(topic)
            elif accuracy < 0.6:
                self.weaknesses.append(topic)
    
    def _adjust_difficulty_preference(self):
        """Adjust difficulty based on recent performance"""
        if len(self.quiz_history) < 3:
            return
        
        recent_quizzes = self.quiz_history[-5:]  # Last 5 quizzes
        recent_accuracy = sum(q.correct_answers for q in recent_quizzes) / sum(q.questions_count for q in recent_quizzes)
        
        if recent_accuracy >= 0.85:
            # Performing well, can handle harder content
            if self.difficulty_preference == DifficultyLevel.EASY:
                self.difficulty_preference = DifficultyLevel.MEDIUM
            elif self.difficulty_preference == DifficultyLevel.MEDIUM:
                self.difficulty_preference = DifficultyLevel.HARD
        elif recent_accuracy < 0.6:
            # Struggling, need easier content
            if self.difficulty_preference == DifficultyLevel.HARD:
                self.difficulty_preference = DifficultyLevel.MEDIUM
            elif self.difficulty_preference == DifficultyLevel.MEDIUM:
                self.difficulty_preference = DifficultyLevel.EASY
    
    def get_recommended_content_level(self) -> DifficultyLevel:
        """Get recommended difficulty level for new content"""
        if self.difficulty_preference == DifficultyLevel.ADAPTIVE:
            if self.quiz_accuracy >= 0.8:
                return DifficultyLevel.HARD
            elif self.quiz_accuracy >= 0.6:
                return DifficultyLevel.MEDIUM
            else:
                return DifficultyLevel.EASY
        return self.difficulty_preference

class StudentProfileManager:
    """Manages student profiles with file-based storage"""
    
    def __init__(self, profiles_dir: str = "student_profiles"):
        self.profiles_dir = profiles_dir
        os.makedirs(profiles_dir, exist_ok=True)
    
    def _get_profile_path(self, student_id: str) -> str:
        return os.path.join(self.profiles_dir, f"{student_id}.json")
    
    def get_profile(self, student_id: str, grade: str = "4") -> StudentProfile:
        """Get student profile, creating one if it doesn't exist"""
        profile_path = self._get_profile_path(student_id)
        
        if os.path.exists(profile_path):
            try:
                with open(profile_path, 'r') as f:
                    data = json.load(f)
                
                # Convert dictionaries back to dataclasses
                data['quiz_history'] = [QuizResult(**q) for q in data.get('quiz_history', [])]
                data['learning_sessions'] = [LearningSession(**s) for s in data.get('learning_sessions', [])]
                data['video_progress'] = [VideoProgress(**v) for v in data.get('video_progress', [])]
                
                return StudentProfile(**data)
            except Exception as e:
                print(f"Error loading profile for {student_id}: {e}")
                # Create new profile if loading fails
                return StudentProfile.create_new(student_id, grade)
        else:
            return StudentProfile.create_new(student_id, grade)
    
    def save_profile(self, profile: StudentProfile):
        """Save student profile to file"""
        profile_path = self._get_profile_path(profile.student_id)
        
        try:
            # Convert to dict for JSON serialization
            profile_dict = asdict(profile)
            
            with open(profile_path, 'w') as f:
                json.dump(profile_dict, f, indent=2)
        except Exception as e:
            print(f"Error saving profile for {profile.student_id}: {e}")
    
    def update_quiz_result(self, student_id: str, quiz_result: QuizResult, grade: str = "4"):
        """Update student profile with new quiz result"""
        profile = self.get_profile(student_id, grade)
        profile.update_quiz_result(quiz_result)
        self.save_profile(profile)
        return profile
    
    def add_learning_session(self, student_id: str, session: LearningSession, grade: str = "4"):
        """Add learning session to student profile"""
        profile = self.get_profile(student_id, grade)
        profile.add_learning_session(session)
        self.save_profile(profile)
        return profile
    
    def add_video_progress(self, student_id: str, video: VideoProgress, grade: str = "4"):
        """Add video progress to student profile"""
        profile = self.get_profile(student_id, grade)
        profile.add_video_progress(video)
        self.save_profile(profile)
        return profile

# Global instance
profile_manager = StudentProfileManager()
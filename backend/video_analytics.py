"""
Video Analytics and Engagement Tracking for SnapLearn AI - Phase 4
Tracks video performance, engagement metrics, and learning effectiveness
"""

import os
import logging
import json
import asyncio
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime, timedelta
from pathlib import Path
from dataclasses import dataclass
from enum import Enum
import statistics

from models import StudentProfile, VideoResponse
from utils import schedule_async_init

logger = logging.getLogger(__name__)

class EngagementLevel(str, Enum):
    """Video engagement levels"""
    VERY_LOW = "very_low"      # <20% completion
    LOW = "low"                # 20-40% completion
    MEDIUM = "medium"          # 40-70% completion
    HIGH = "high"              # 70-90% completion
    VERY_HIGH = "very_high"    # >90% completion

class InteractionType(str, Enum):
    """Types of video interactions"""
    PLAY = "play"
    PAUSE = "pause"
    SEEK = "seek"
    REWIND = "rewind"
    SKIP = "skip"
    COMPLETE = "complete"
    QUESTION = "question"
    BOOKMARK = "bookmark"
    SHARE = "share"
    RATE = "rate"

class LearningOutcome(str, Enum):
    """Learning effectiveness outcomes"""
    MASTERY_ACHIEVED = "mastery_achieved"
    GOOD_PROGRESS = "good_progress"
    SOME_PROGRESS = "some_progress"
    MINIMAL_PROGRESS = "minimal_progress"
    NO_PROGRESS = "no_progress"
    CONFUSION_INCREASED = "confusion_increased"

@dataclass
class VideoInteraction:
    """Individual video interaction event"""
    interaction_id: str
    video_id: str
    student_id: str
    interaction_type: InteractionType
    timestamp: datetime
    video_position_seconds: float
    duration_seconds: Optional[float] = None
    metadata: Optional[Dict[str, Any]] = None

@dataclass
class VideoSession:
    """Complete video viewing session"""
    session_id: str
    video_id: str
    student_id: str
    start_time: datetime
    end_time: Optional[datetime]
    total_watch_time: float
    completion_percentage: float
    interactions: List[VideoInteraction]
    engagement_level: EngagementLevel
    attention_segments: List[Tuple[float, float]]  # (start, end) in seconds
    confusion_indicators: List[str]
    learning_indicators: List[str]

@dataclass
class VideoPerformanceMetrics:
    """Aggregated performance metrics for a video"""
    video_id: str
    topic: str
    total_views: int
    unique_viewers: int
    average_completion_rate: float
    average_watch_time: float
    engagement_distribution: Dict[EngagementLevel, int]
    most_rewatched_segments: List[Tuple[float, float, int]]  # (start, end, rewatch_count)
    drop_off_points: List[Tuple[float, int]]  # (timestamp, drop_count)
    learning_effectiveness_score: float
    student_feedback_scores: List[float]
    improvement_suggestions: List[str]

class VideoAnalytics:
    """Comprehensive video analytics and engagement tracking system"""
    
    def __init__(self):
        self.analytics_dir = Path("../analytics")
        self.analytics_dir.mkdir(exist_ok=True)
        
        # In-memory storage for real-time analytics
        self.active_sessions: Dict[str, VideoSession] = {}
        self.video_metrics: Dict[str, VideoPerformanceMetrics] = {}
        self.interaction_buffer: List[VideoInteraction] = []
        
        # Analytics configuration
        self.buffer_flush_size = 100
        self.session_timeout_minutes = 30
        self.analytics_retention_days = 90
        
        # Machine learning for engagement prediction
        self.engagement_model = None
        
        # Initialize analytics data
        schedule_async_init(self._load_historical_analytics())

        # Start background tasks
        schedule_async_init(self._analytics_processor())
        schedule_async_init(self._session_monitor())
    
    async def _load_historical_analytics(self):
        """Load historical analytics data"""
        try:
            analytics_file = self.analytics_dir / "video_metrics.json"
            
            if analytics_file.exists():
                with open(analytics_file, 'r') as f:
                    data = json.load(f)
                    
                for video_id, metrics_data in data.items():
                    self.video_metrics[video_id] = VideoPerformanceMetrics(**metrics_data)
                
                logger.info(f"Loaded analytics for {len(self.video_metrics)} videos")
            
        except Exception as e:
            logger.error(f"Error loading historical analytics: {str(e)}")
    
    async def _analytics_processor(self):
        """Background task to process analytics data"""
        while True:
            try:
                await asyncio.sleep(60)  # Process every minute
                
                # Flush interaction buffer
                if len(self.interaction_buffer) >= self.buffer_flush_size:
                    await self._flush_interaction_buffer()
                
                # Update video metrics
                await self._update_video_metrics()
                
                # Clean up old sessions
                await self._cleanup_old_sessions()
                
            except Exception as e:
                logger.error(f"Error in analytics processor: {str(e)}")
    
    async def _session_monitor(self):
        """Monitor and update active sessions"""
        while True:
            try:
                await asyncio.sleep(30)  # Check every 30 seconds
                
                current_time = datetime.now()
                
                # Check for timed-out sessions
                timed_out_sessions = []
                for session_id, session in self.active_sessions.items():
                    if session.end_time is None:
                        last_interaction = max(
                            (interaction.timestamp for interaction in session.interactions),
                            default=session.start_time
                        )
                        
                        if (current_time - last_interaction).total_seconds() > self.session_timeout_minutes * 60:
                            timed_out_sessions.append(session_id)
                
                # End timed-out sessions
                for session_id in timed_out_sessions:
                    await self.end_video_session(session_id, auto_timeout=True)
                
            except Exception as e:
                logger.error(f"Error in session monitor: {str(e)}")
    
    async def start_video_session(self, 
                                video_id: str,
                                student_id: str,
                                video_metadata: Optional[Dict[str, Any]] = None) -> str:
        """Start tracking a new video viewing session"""
        try:
            session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{student_id[:8]}"
            
            session = VideoSession(
                session_id=session_id,
                video_id=video_id,
                student_id=student_id,
                start_time=datetime.now(),
                end_time=None,
                total_watch_time=0.0,
                completion_percentage=0.0,
                interactions=[],
                engagement_level=EngagementLevel.LOW,
                attention_segments=[],
                confusion_indicators=[],
                learning_indicators=[]
            )
            
            self.active_sessions[session_id] = session
            
            # Log session start
            await self.track_video_interaction(
                session_id=session_id,
                interaction_type=InteractionType.PLAY,
                video_position=0.0,
                metadata=video_metadata
            )
            
            logger.info(f"Started video session: {session_id} for video {video_id}")
            
            return session_id
            
        except Exception as e:
            logger.error(f"Error starting video session: {str(e)}")
            raise
    
    async def track_video_interaction(self,
                                    session_id: str,
                                    interaction_type: InteractionType,
                                    video_position: float,
                                    duration: Optional[float] = None,
                                    metadata: Optional[Dict[str, Any]] = None) -> bool:
        """Track a video interaction event"""
        try:
            if session_id not in self.active_sessions:
                logger.warning(f"Session {session_id} not found for interaction tracking")
                return False
            
            session = self.active_sessions[session_id]
            
            interaction = VideoInteraction(
                interaction_id=f"int_{datetime.now().strftime('%Y%m%d%H%M%S%f')}",
                video_id=session.video_id,
                student_id=session.student_id,
                interaction_type=interaction_type,
                timestamp=datetime.now(),
                video_position_seconds=video_position,
                duration_seconds=duration,
                metadata=metadata or {}
            )
            
            session.interactions.append(interaction)
            self.interaction_buffer.append(interaction)
            
            # Update session metrics in real-time
            await self._update_session_metrics(session)
            
            # Detect engagement patterns
            await self._analyze_interaction_patterns(session, interaction)
            
            return True
            
        except Exception as e:
            logger.error(f"Error tracking video interaction: {str(e)}")
            return False
    
    async def end_video_session(self, 
                              session_id: str,
                              final_position: Optional[float] = None,
                              auto_timeout: bool = False) -> Optional[Dict[str, Any]]:
        """End a video viewing session and compute final analytics"""
        try:
            if session_id not in self.active_sessions:
                return None
            
            session = self.active_sessions[session_id]
            session.end_time = datetime.now()
            
            # Add completion interaction if not auto-timeout
            if not auto_timeout and final_position is not None:
                await self.track_video_interaction(
                    session_id=session_id,
                    interaction_type=InteractionType.COMPLETE,
                    video_position=final_position
                )
            
            # Compute final session analytics
            session_analytics = await self._compute_session_analytics(session)
            
            # Update video-level metrics
            await self._update_video_level_metrics(session)
            
            # Generate learning insights
            learning_insights = await self._generate_learning_insights(session)
            
            # Remove from active sessions
            del self.active_sessions[session_id]
            
            logger.info(f"Ended video session: {session_id} - {session_analytics['engagement_level']}")
            
            return {
                "session_analytics": session_analytics,
                "learning_insights": learning_insights,
                "recommendations": await self._generate_session_recommendations(session)
            }
            
        except Exception as e:
            logger.error(f"Error ending video session: {str(e)}")
            return None
    
    async def _update_session_metrics(self, session: VideoSession):
        """Update real-time session metrics"""
        try:
            if not session.interactions:
                return
            
            # Calculate total watch time
            watch_segments = []
            current_play_start = None
            
            for interaction in session.interactions:
                if interaction.interaction_type == InteractionType.PLAY:
                    current_play_start = interaction.video_position_seconds
                elif interaction.interaction_type == InteractionType.PAUSE:
                    if current_play_start is not None:
                        watch_segments.append((
                            current_play_start,
                            interaction.video_position_seconds
                        ))
                        current_play_start = None
            
            # Add current segment if still playing
            if current_play_start is not None:
                latest_position = session.interactions[-1].video_position_seconds
                watch_segments.append((current_play_start, latest_position))
            
            # Calculate metrics
            session.total_watch_time = sum(end - start for start, end in watch_segments if end > start)
            session.attention_segments = watch_segments
            
            # Update engagement level
            if session.interactions:
                latest_position = max(interaction.video_position_seconds for interaction in session.interactions)
                video_duration = self._get_video_duration(session.video_id)
                
                if video_duration and video_duration > 0:
                    session.completion_percentage = min(100.0, (latest_position / video_duration) * 100)
                    session.engagement_level = self._classify_engagement_level(session.completion_percentage)
            
        except Exception as e:
            logger.error(f"Error updating session metrics: {str(e)}")
    
    async def _analyze_interaction_patterns(self, session: VideoSession, interaction: VideoInteraction):
        """Analyze interaction patterns for engagement and confusion indicators"""
        try:
            # Look for confusion indicators
            if interaction.interaction_type == InteractionType.REWIND:
                # Multiple rewinds in short time indicate confusion
                recent_rewinds = [
                    i for i in session.interactions[-5:]
                    if i.interaction_type == InteractionType.REWIND
                    and (interaction.timestamp - i.timestamp).total_seconds() < 60
                ]
                
                if len(recent_rewinds) >= 2:
                    session.confusion_indicators.append(f"Multiple rewinds at {interaction.video_position_seconds:.0f}s")
            
            elif interaction.interaction_type == InteractionType.PAUSE:
                # Long pauses might indicate confusion or deep thinking
                if interaction.duration_seconds and interaction.duration_seconds > 30:
                    session.confusion_indicators.append(f"Long pause ({interaction.duration_seconds:.0f}s) at {interaction.video_position_seconds:.0f}s")
            
            # Look for learning indicators
            if interaction.interaction_type == InteractionType.SEEK:
                # Forward seeking to specific sections might indicate focused learning
                if interaction.metadata and interaction.metadata.get("seek_type") == "concept_review":
                    session.learning_indicators.append(f"Concept review at {interaction.video_position_seconds:.0f}s")
            
            elif interaction.interaction_type == InteractionType.BOOKMARK:
                # Bookmarking indicates engagement
                session.learning_indicators.append(f"Bookmarked at {interaction.video_position_seconds:.0f}s")
            
        except Exception as e:
            logger.error(f"Error analyzing interaction patterns: {str(e)}")
    
    def _classify_engagement_level(self, completion_percentage: float) -> EngagementLevel:
        """Classify engagement level based on completion percentage and other factors"""
        
        if completion_percentage >= 90:
            return EngagementLevel.VERY_HIGH
        elif completion_percentage >= 70:
            return EngagementLevel.HIGH
        elif completion_percentage >= 40:
            return EngagementLevel.MEDIUM
        elif completion_percentage >= 20:
            return EngagementLevel.LOW
        else:
            return EngagementLevel.VERY_LOW
    
    def _get_video_duration(self, video_id: str) -> Optional[float]:
        """Get video duration from metadata or metrics"""
        
        if video_id in self.video_metrics:
            # Could be stored in video metadata
            return getattr(self.video_metrics[video_id], 'duration_seconds', None)
        
        # Default estimation for educational videos
        return 300.0  # 5 minutes default
    
    async def _compute_session_analytics(self, session: VideoSession) -> Dict[str, Any]:
        """Compute comprehensive analytics for a completed session"""
        
        session_duration = (session.end_time - session.start_time).total_seconds()
        video_duration = self._get_video_duration(session.video_id) or 300
        
        # Interaction analytics
        interaction_counts = {}
        for interaction_type in InteractionType:
            interaction_counts[interaction_type.value] = sum(
                1 for i in session.interactions if i.interaction_type == interaction_type
            )
        
        # Attention analysis
        focused_segments = [
            (start, end) for start, end in session.attention_segments
            if (end - start) > 10  # At least 10 seconds of continuous watching
        ]
        
        focused_watch_time = sum(end - start for start, end in focused_segments)
        
        # Engagement metrics
        engagement_score = self._calculate_engagement_score(session)
        
        return {
            "session_id": session.session_id,
            "total_session_time": session_duration,
            "active_watch_time": session.total_watch_time,
            "engagement_level": session.engagement_level.value,
            "engagement_score": engagement_score,
            "completion_percentage": session.completion_percentage,
            "interaction_counts": interaction_counts,
            "focused_segments_count": len(focused_segments),
            "focused_watch_time": focused_watch_time,
            "attention_ratio": focused_watch_time / video_duration if video_duration > 0 else 0,
            "confusion_indicators": session.confusion_indicators,
            "learning_indicators": session.learning_indicators,
            "rewatch_segments": self._identify_rewatch_segments(session),
            "peak_attention_moments": self._identify_peak_attention_moments(session)
        }
    
    def _calculate_engagement_score(self, session: VideoSession) -> float:
        """Calculate comprehensive engagement score (0-1)"""
        
        # Base score from completion
        completion_score = min(1.0, session.completion_percentage / 100.0)
        
        # Interaction diversity bonus
        unique_interactions = len(set(i.interaction_type for i in session.interactions))
        interaction_score = min(0.3, unique_interactions * 0.05)
        
        # Attention quality bonus
        video_duration = self._get_video_duration(session.video_id) or 300
        attention_score = min(0.2, session.total_watch_time / video_duration)
        
        # Learning indicator bonus
        learning_score = min(0.2, len(session.learning_indicators) * 0.05)
        
        # Confusion penalty
        confusion_penalty = min(0.3, len(session.confusion_indicators) * 0.1)
        
        engagement_score = completion_score + interaction_score + attention_score + learning_score - confusion_penalty
        
        return max(0.0, min(1.0, engagement_score))
    
    def _identify_rewatch_segments(self, session: VideoSession) -> List[Dict[str, Any]]:
        """Identify segments that were watched multiple times"""
        
        rewatch_segments = []
        
        # Group interactions by position ranges
        position_groups = {}
        
        for interaction in session.interactions:
            if interaction.interaction_type in [InteractionType.PLAY, InteractionType.SEEK]:
                # Round to 10-second intervals
                interval = int(interaction.video_position_seconds // 10) * 10
                
                if interval not in position_groups:
                    position_groups[interval] = []
                position_groups[interval].append(interaction)
        
        # Identify segments with multiple visits
        for interval, interactions in position_groups.items():
            if len(interactions) > 1:
                rewatch_segments.append({
                    "start_time": interval,
                    "end_time": interval + 10,
                    "rewatch_count": len(interactions),
                    "timestamps": [i.timestamp.isoformat() for i in interactions]
                })
        
        return sorted(rewatch_segments, key=lambda x: x["rewatch_count"], reverse=True)[:5]
    
    def _identify_peak_attention_moments(self, session: VideoSession) -> List[Dict[str, Any]]:
        """Identify moments of peak attention/engagement"""
        
        peak_moments = []
        
        # Look for segments with high interaction density
        if len(session.interactions) < 3:
            return peak_moments
        
        # Group interactions by time windows
        window_size = 30  # 30-second windows
        video_duration = self._get_video_duration(session.video_id) or 300
        
        for start_time in range(0, int(video_duration), window_size):
            end_time = start_time + window_size
            
            # Count interactions in this window
            window_interactions = [
                i for i in session.interactions
                if start_time <= i.video_position_seconds < end_time
            ]
            
            if len(window_interactions) >= 3:  # High interaction density
                interaction_types = [i.interaction_type.value for i in window_interactions]
                
                peak_moments.append({
                    "start_time": start_time,
                    "end_time": end_time,
                    "interaction_count": len(window_interactions),
                    "interaction_types": list(set(interaction_types)),
                    "attention_score": len(window_interactions) / window_size  # Interactions per second
                })
        
        return sorted(peak_moments, key=lambda x: x["attention_score"], reverse=True)[:3]
    
    async def _generate_learning_insights(self, session: VideoSession) -> Dict[str, Any]:
        """Generate learning effectiveness insights"""
        
        # Analyze learning progression
        learning_progression = "steady"
        
        if len(session.confusion_indicators) > 3:
            learning_progression = "struggling"
        elif len(session.learning_indicators) > 2 and session.completion_percentage > 80:
            learning_progression = "accelerated"
        elif session.completion_percentage < 30:
            learning_progression = "disengaged"
        
        # Determine learning outcome
        learning_outcome = LearningOutcome.SOME_PROGRESS
        
        if session.completion_percentage >= 90 and len(session.confusion_indicators) <= 1:
            learning_outcome = LearningOutcome.MASTERY_ACHIEVED
        elif session.completion_percentage >= 70 and len(session.learning_indicators) >= 2:
            learning_outcome = LearningOutcome.GOOD_PROGRESS
        elif session.completion_percentage < 30 or len(session.confusion_indicators) > 5:
            learning_outcome = LearningOutcome.MINIMAL_PROGRESS
        elif len(session.confusion_indicators) > len(session.learning_indicators) * 2:
            learning_outcome = LearningOutcome.CONFUSION_INCREASED
        
        # Engagement analysis
        engagement_analysis = {
            "primary_engagement_driver": self._identify_primary_engagement_driver(session),
            "attention_pattern": self._analyze_attention_pattern(session),
            "optimal_video_length": self._suggest_optimal_length(session),
            "content_effectiveness": self._assess_content_effectiveness(session)
        }
        
        return {
            "learning_progression": learning_progression,
            "learning_outcome": learning_outcome.value,
            "engagement_analysis": engagement_analysis,
            "personalization_opportunities": self._identify_personalization_opportunities(session),
            "content_recommendations": self._generate_content_recommendations(session)
        }
    
    def _identify_primary_engagement_driver(self, session: VideoSession) -> str:
        """Identify what drove engagement in this session"""
        
        if len(session.learning_indicators) > 2:
            return "interactive_content"
        elif session.completion_percentage > 85:
            return "compelling_narrative"
        elif len([i for i in session.interactions if i.interaction_type == InteractionType.REWIND]) > 3:
            return "complex_content_requiring_review"
        elif session.total_watch_time > self._get_video_duration(session.video_id) * 0.8:
            return "appropriate_difficulty_level"
        else:
            return "visual_animations"
    
    def _analyze_attention_pattern(self, session: VideoSession) -> str:
        """Analyze the student's attention pattern"""
        
        if len(session.attention_segments) <= 2:
            return "sustained_focus"
        elif len(session.attention_segments) > 5:
            return "fragmented_attention"
        elif any((end - start) > 120 for start, end in session.attention_segments):
            return "deep_focus_periods"
        else:
            return "moderate_focus"
    
    def _suggest_optimal_length(self, session: VideoSession) -> str:
        """Suggest optimal video length based on attention patterns"""
        
        video_duration = self._get_video_duration(session.video_id) or 300
        
        if session.completion_percentage < 50 and video_duration > 240:  # 4 minutes
            return "shorter_videos_recommended"
        elif session.completion_percentage > 90 and video_duration < 180:  # 3 minutes
            return "longer_videos_acceptable"
        else:
            return "current_length_appropriate"
    
    def _assess_content_effectiveness(self, session: VideoSession) -> float:
        """Assess how effective the content was for learning"""
        
        effectiveness_score = 0.0
        
        # Completion contributes to effectiveness
        effectiveness_score += (session.completion_percentage / 100) * 0.4
        
        # Learning indicators boost effectiveness
        effectiveness_score += min(0.3, len(session.learning_indicators) * 0.1)
        
        # Confusion reduces effectiveness
        effectiveness_score -= min(0.2, len(session.confusion_indicators) * 0.05)
        
        # Engagement level contributes
        engagement_mapping = {
            EngagementLevel.VERY_HIGH: 0.3,
            EngagementLevel.HIGH: 0.2,
            EngagementLevel.MEDIUM: 0.1,
            EngagementLevel.LOW: 0.0,
            EngagementLevel.VERY_LOW: -0.1
        }
        effectiveness_score += engagement_mapping.get(session.engagement_level, 0.0)
        
        return max(0.0, min(1.0, effectiveness_score))
    
    def _identify_personalization_opportunities(self, session: VideoSession) -> List[str]:
        """Identify opportunities for content personalization"""
        
        opportunities = []
        
        if len(session.confusion_indicators) > 2:
            opportunities.append("add_prerequisite_review")
            opportunities.append("simplify_explanations")
        
        if session.completion_percentage < 40:
            opportunities.append("increase_engagement_elements")
            opportunities.append("add_interactive_breaks")
        
        if len([i for i in session.interactions if i.interaction_type == InteractionType.REWIND]) > 3:
            opportunities.append("improve_visual_clarity")
            opportunities.append("add_step_by_step_breakdown")
        
        if session.total_watch_time < (self._get_video_duration(session.video_id) or 300) * 0.5:
            opportunities.append("adjust_difficulty_level")
            opportunities.append("add_motivation_elements")
        
        return opportunities
    
    def _generate_content_recommendations(self, session: VideoSession) -> List[str]:
        """Generate specific content improvement recommendations"""
        
        recommendations = []
        
        # Based on confusion indicators
        confusion_positions = [
            float(indicator.split("at ")[1].split("s")[0])
            for indicator in session.confusion_indicators
            if "at " in indicator and "s" in indicator
        ]
        
        if confusion_positions:
            avg_confusion_time = sum(confusion_positions) / len(confusion_positions)
            recommendations.append(f"Add clarification around {avg_confusion_time:.0f}s mark")
        
        # Based on rewatch patterns
        rewatch_segments = self._identify_rewatch_segments(session)
        if rewatch_segments:
            most_rewatched = rewatch_segments[0]
            recommendations.append(f"Improve explanation clarity at {most_rewatched['start_time']}-{most_rewatched['end_time']}s")
        
        # Based on drop-off points
        if session.completion_percentage < 70:
            video_duration = self._get_video_duration(session.video_id) or 300
            drop_off_point = (session.completion_percentage / 100) * video_duration
            recommendations.append(f"Address potential drop-off point around {drop_off_point:.0f}s")
        
        # General recommendations
        if not recommendations:
            recommendations.append("Content appears to be working well for this student")
        
        return recommendations
    
    async def _generate_session_recommendations(self, session: VideoSession) -> List[str]:
        """Generate recommendations for future learning sessions"""
        
        recommendations = []
        
        # Based on engagement level
        if session.engagement_level == EngagementLevel.VERY_LOW:
            recommendations.extend([
                "Try shorter video segments (2-3 minutes)",
                "Include more interactive elements",
                "Consider alternative learning modalities"
            ])
        elif session.engagement_level == EngagementLevel.VERY_HIGH:
            recommendations.extend([
                "Student ready for more challenging content",
                "Consider longer-form deep dives",
                "Introduce advanced concepts"
            ])
        
        # Based on confusion patterns
        if len(session.confusion_indicators) > 3:
            recommendations.extend([
                "Review prerequisite concepts before next video",
                "Consider one-on-one tutoring support",
                "Use more visual and concrete examples"
            ])
        
        # Based on learning indicators
        if len(session.learning_indicators) >= 3:
            recommendations.extend([
                "Student demonstrates strong engagement",
                "Ready for self-directed exploration",
                "Consider project-based learning opportunities"
            ])
        
        return recommendations[:5]  # Limit to top 5 recommendations
    
    async def _flush_interaction_buffer(self):
        """Flush interaction buffer to persistent storage"""
        try:
            if not self.interaction_buffer:
                return
            
            # Save interactions to file
            interactions_file = self.analytics_dir / f"interactions_{datetime.now().strftime('%Y%m%d')}.json"
            
            # Load existing data
            existing_data = []
            if interactions_file.exists():
                with open(interactions_file, 'r') as f:
                    existing_data = json.load(f)
            
            # Add new interactions
            for interaction in self.interaction_buffer:
                existing_data.append({
                    "interaction_id": interaction.interaction_id,
                    "video_id": interaction.video_id,
                    "student_id": interaction.student_id,
                    "interaction_type": interaction.interaction_type.value,
                    "timestamp": interaction.timestamp.isoformat(),
                    "video_position_seconds": interaction.video_position_seconds,
                    "duration_seconds": interaction.duration_seconds,
                    "metadata": interaction.metadata
                })
            
            # Save updated data
            with open(interactions_file, 'w') as f:
                json.dump(existing_data, f, indent=2)
            
            # Clear buffer
            self.interaction_buffer.clear()
            
            logger.info(f"Flushed {len(existing_data)} interactions to {interactions_file}")
            
        except Exception as e:
            logger.error(f"Error flushing interaction buffer: {str(e)}")
    
    async def _update_video_metrics(self):
        """Update aggregated video-level metrics"""
        try:
            # Process completed sessions
            for session_id, session in list(self.active_sessions.items()):
                if session.end_time is not None:
                    await self._update_video_level_metrics(session)
            
            # Save updated metrics
            await self._save_video_metrics()
            
        except Exception as e:
            logger.error(f"Error updating video metrics: {str(e)}")
    
    async def _update_video_level_metrics(self, session: VideoSession):
        """Update metrics for a specific video"""
        try:
            video_id = session.video_id
            
            if video_id not in self.video_metrics:
                # Initialize new video metrics
                self.video_metrics[video_id] = VideoPerformanceMetrics(
                    video_id=video_id,
                    topic="",  # Could be filled from video metadata
                    total_views=0,
                    unique_viewers=0,
                    average_completion_rate=0.0,
                    average_watch_time=0.0,
                    engagement_distribution={level: 0 for level in EngagementLevel},
                    most_rewatched_segments=[],
                    drop_off_points=[],
                    learning_effectiveness_score=0.0,
                    student_feedback_scores=[],
                    improvement_suggestions=[]
                )
            
            metrics = self.video_metrics[video_id]
            
            # Update basic metrics
            metrics.total_views += 1
            
            # Update completion rate (running average)
            old_avg_completion = metrics.average_completion_rate
            new_completion_rate = session.completion_percentage
            metrics.average_completion_rate = (
                (old_avg_completion * (metrics.total_views - 1) + new_completion_rate) / metrics.total_views
            )
            
            # Update watch time (running average)
            old_avg_watch_time = metrics.average_watch_time
            new_watch_time = session.total_watch_time
            metrics.average_watch_time = (
                (old_avg_watch_time * (metrics.total_views - 1) + new_watch_time) / metrics.total_views
            )
            
            # Update engagement distribution
            metrics.engagement_distribution[session.engagement_level] += 1
            
            # Update learning effectiveness
            content_effectiveness = self._assess_content_effectiveness(session)
            old_effectiveness = metrics.learning_effectiveness_score
            metrics.learning_effectiveness_score = (
                (old_effectiveness * (metrics.total_views - 1) + content_effectiveness) / metrics.total_views
            )
            
        except Exception as e:
            logger.error(f"Error updating video level metrics: {str(e)}")
    
    async def _save_video_metrics(self):
        """Save video metrics to persistent storage"""
        try:
            metrics_file = self.analytics_dir / "video_metrics.json"
            
            # Convert metrics to serializable format
            serializable_metrics = {}
            for video_id, metrics in self.video_metrics.items():
                serializable_metrics[video_id] = {
                    "video_id": metrics.video_id,
                    "topic": metrics.topic,
                    "total_views": metrics.total_views,
                    "unique_viewers": metrics.unique_viewers,
                    "average_completion_rate": metrics.average_completion_rate,
                    "average_watch_time": metrics.average_watch_time,
                    "engagement_distribution": {k.value: v for k, v in metrics.engagement_distribution.items()},
                    "most_rewatched_segments": metrics.most_rewatched_segments,
                    "drop_off_points": metrics.drop_off_points,
                    "learning_effectiveness_score": metrics.learning_effectiveness_score,
                    "student_feedback_scores": metrics.student_feedback_scores,
                    "improvement_suggestions": metrics.improvement_suggestions
                }
            
            with open(metrics_file, 'w') as f:
                json.dump(serializable_metrics, f, indent=2)
            
        except Exception as e:
            logger.error(f"Error saving video metrics: {str(e)}")
    
    async def _cleanup_old_sessions(self):
        """Clean up old session data"""
        try:
            cutoff_time = datetime.now() - timedelta(days=self.analytics_retention_days)
            
            # Clean up old interaction files
            for file_path in self.analytics_dir.glob("interactions_*.json"):
                if file_path.stat().st_mtime < cutoff_time.timestamp():
                    file_path.unlink()
                    logger.info(f"Cleaned up old interactions file: {file_path.name}")
            
        except Exception as e:
            logger.error(f"Error cleaning up old sessions: {str(e)}")
    
    async def get_video_analytics(self, video_id: str) -> Optional[Dict[str, Any]]:
        """Get comprehensive analytics for a specific video"""
        
        if video_id not in self.video_metrics:
            return None
        
        metrics = self.video_metrics[video_id]
        
        return {
            "video_id": video_id,
            "performance_metrics": {
                "total_views": metrics.total_views,
                "average_completion_rate": metrics.average_completion_rate,
                "average_watch_time": metrics.average_watch_time,
                "learning_effectiveness_score": metrics.learning_effectiveness_score
            },
            "engagement_analysis": {
                "engagement_distribution": {k.value: v for k, v in metrics.engagement_distribution.items()},
                "most_rewatched_segments": metrics.most_rewatched_segments,
                "drop_off_points": metrics.drop_off_points
            },
            "improvement_opportunities": metrics.improvement_suggestions,
            "student_feedback": {
                "average_rating": statistics.mean(metrics.student_feedback_scores) if metrics.student_feedback_scores else 0.0,
                "total_ratings": len(metrics.student_feedback_scores)
            }
        }
    
    async def get_student_analytics(self, student_id: str, days: int = 30) -> Dict[str, Any]:
        """Get analytics for a specific student's video viewing patterns"""
        
        # This would require loading interaction history for the student
        # For now, return analytics from active sessions
        
        student_sessions = [
            session for session in self.active_sessions.values()
            if session.student_id == student_id
        ]
        
        if not student_sessions:
            return {
                "student_id": student_id,
                "total_sessions": 0,
                "message": "No recent video sessions found"
            }
        
        # Calculate aggregated metrics
        total_watch_time = sum(session.total_watch_time for session in student_sessions)
        avg_completion = sum(session.completion_percentage for session in student_sessions) / len(student_sessions)
        
        engagement_levels = [session.engagement_level for session in student_sessions]
        most_common_engagement = max(set(engagement_levels), key=engagement_levels.count)
        
        return {
            "student_id": student_id,
            "period_days": days,
            "total_sessions": len(student_sessions),
            "total_watch_time_minutes": total_watch_time / 60,
            "average_completion_rate": avg_completion,
            "most_common_engagement_level": most_common_engagement.value,
            "learning_progress_indicators": sum(len(session.learning_indicators) for session in student_sessions),
            "confusion_indicators": sum(len(session.confusion_indicators) for session in student_sessions),
            "video_topics": list(set(session.video_id for session in student_sessions))
        }
    
    def is_healthy(self) -> bool:
        """Check if video analytics system is healthy"""
        return (
            self.analytics_dir.exists() and
            len(self.interaction_buffer) < 1000 and  # Buffer not overloaded
            len(self.active_sessions) < 100  # Not too many concurrent sessions
        )
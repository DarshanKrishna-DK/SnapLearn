"""
Adaptive Difficulty System for SnapLearn AI - Phase 3
Dynamically adjusts content difficulty based on student performance and learning patterns
"""

import os
import logging
import json
import math
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime, timedelta
from enum import Enum
from dataclasses import dataclass

from models import StudentProfile, GradeLevel
from utils import schedule_async_init

logger = logging.getLogger(__name__)

class DifficultyLevel(str, Enum):
    """Difficulty levels with numeric mappings"""
    VERY_EASY = "very_easy"      # 1
    EASY = "easy"                # 2  
    MEDIUM = "medium"            # 3
    HARD = "hard"                # 4
    VERY_HARD = "very_hard"      # 5

class PerformanceState(str, Enum):
    """Student performance states"""
    STRUGGLING = "struggling"
    LEARNING = "learning"
    MASTERING = "mastering"
    EXCELLING = "excelling"
    BORED = "bored"

class AdaptationTrigger(str, Enum):
    """Triggers for difficulty adaptation"""
    CONSECUTIVE_SUCCESS = "consecutive_success"
    CONSECUTIVE_FAILURE = "consecutive_failure"
    TIME_BASED = "time_based"
    CONFUSION_PATTERN = "confusion_pattern"
    ENGAGEMENT_DROP = "engagement_drop"
    MASTERY_ACHIEVED = "mastery_achieved"

@dataclass
class PerformanceMetrics:
    """Performance tracking metrics"""
    accuracy: float
    response_time: float
    engagement_score: float
    confusion_indicators: int
    help_requests: int
    consecutive_correct: int
    consecutive_incorrect: int
    session_duration: int

@dataclass
class AdaptationRecord:
    """Record of difficulty adaptations"""
    timestamp: datetime
    trigger: AdaptationTrigger
    old_difficulty: DifficultyLevel
    new_difficulty: DifficultyLevel
    reason: str
    performance_snapshot: PerformanceMetrics

class AdaptiveDifficultyEngine:
    """Engine for dynamically adjusting learning difficulty"""
    
    def __init__(self):
        self.gemini_client = None
        self.student_performance_db = {}  # Student performance history
        self.adaptation_history = {}      # History of adaptations
        self.difficulty_mappings = self._init_difficulty_mappings()
        
        # Adaptation thresholds
        self.adaptation_config = {
            "success_threshold": 3,      # Consecutive successes to increase
            "failure_threshold": 2,      # Consecutive failures to decrease
            "time_threshold": 300,       # 5 minutes without progress
            "engagement_threshold": 0.3, # Minimum engagement score
            "mastery_threshold": 0.85,   # Accuracy for mastery
            "struggle_threshold": 0.4    # Accuracy indicating struggle
        }
        
        # Initialize Gemini for content generation
        schedule_async_init(self._init_gemini())
    
    async def _init_gemini(self):
        """Initialize Gemini for difficulty-adaptive content generation"""
        try:
            from google import genai
            
            api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
            if not api_key:
                logger.error("Gemini API key not found for adaptive difficulty")
                return
            
            self.gemini_client = genai.Client(api_key=api_key)
            logger.info("Adaptive difficulty: Gemini client initialized")
            
        except ImportError:
            logger.error("Google GenAI library not installed for adaptive difficulty")
        except Exception as e:
            logger.error(f"Error initializing Gemini for adaptive difficulty: {str(e)}")
    
    def _init_difficulty_mappings(self) -> Dict[str, Dict]:
        """Initialize difficulty level mappings for different subjects/grades"""
        return {
            # Mathematics difficulty progressions
            "math": {
                DifficultyLevel.VERY_EASY: {
                    "description": "Basic recognition and simple operations",
                    "concepts": ["counting", "basic shapes", "single-digit addition"],
                    "complexity_score": 1.0
                },
                DifficultyLevel.EASY: {
                    "description": "Fundamental operations with guidance", 
                    "concepts": ["two-digit operations", "basic fractions", "simple geometry"],
                    "complexity_score": 2.0
                },
                DifficultyLevel.MEDIUM: {
                    "description": "Standard grade-level expectations",
                    "concepts": ["multi-step problems", "advanced operations", "word problems"],
                    "complexity_score": 3.0
                },
                DifficultyLevel.HARD: {
                    "description": "Above grade-level with multiple steps",
                    "concepts": ["complex reasoning", "multi-concept integration", "abstract thinking"],
                    "complexity_score": 4.0
                },
                DifficultyLevel.VERY_HARD: {
                    "description": "Advanced problem-solving and creative thinking",
                    "concepts": ["novel problem types", "advanced reasoning", "cross-curricular"],
                    "complexity_score": 5.0
                }
            },
            # Science difficulty progressions
            "science": {
                DifficultyLevel.VERY_EASY: {
                    "description": "Observable phenomena and basic facts",
                    "concepts": ["observation", "simple classification", "basic properties"],
                    "complexity_score": 1.0
                },
                DifficultyLevel.EASY: {
                    "description": "Simple explanations and cause-effect",
                    "concepts": ["simple systems", "basic relationships", "guided inquiry"],
                    "complexity_score": 2.0
                },
                DifficultyLevel.MEDIUM: {
                    "description": "Scientific reasoning and explanation",
                    "concepts": ["hypothesis formation", "data interpretation", "model building"],
                    "complexity_score": 3.0
                },
                DifficultyLevel.HARD: {
                    "description": "Complex systems and abstract concepts", 
                    "concepts": ["system interactions", "advanced models", "experimental design"],
                    "complexity_score": 4.0
                },
                DifficultyLevel.VERY_HARD: {
                    "description": "Advanced scientific thinking and research",
                    "concepts": ["independent research", "complex analysis", "theory development"],
                    "complexity_score": 5.0
                }
            }
        }
    
    async def assess_current_performance(self, 
                                       student_id: str,
                                       recent_responses: List[Dict[str, Any]],
                                       session_data: Dict[str, Any]) -> PerformanceMetrics:
        """Assess current student performance from recent interactions"""
        try:
            # Calculate accuracy from recent responses
            total_responses = len(recent_responses)
            if total_responses == 0:
                return self._create_baseline_metrics()
            
            correct_responses = sum(1 for r in recent_responses if r.get("is_correct", False))
            accuracy = correct_responses / total_responses
            
            # Calculate response times
            response_times = [r.get("response_time_sec", 30) for r in recent_responses]
            avg_response_time = sum(response_times) / len(response_times)
            
            # Calculate engagement score
            engagement_score = self._calculate_engagement_score(recent_responses, session_data)
            
            # Count confusion indicators
            confusion_count = sum(len(r.get("confusion_indicators", [])) for r in recent_responses)
            
            # Count help requests
            help_requests = sum(1 for r in recent_responses if r.get("help_requested", False))
            
            # Calculate consecutive patterns
            consecutive_correct = self._calculate_consecutive_correct(recent_responses)
            consecutive_incorrect = self._calculate_consecutive_incorrect(recent_responses)
            
            # Session duration
            session_duration = session_data.get("duration_minutes", 0)
            
            return PerformanceMetrics(
                accuracy=accuracy,
                response_time=avg_response_time,
                engagement_score=engagement_score,
                confusion_indicators=confusion_count,
                help_requests=help_requests,
                consecutive_correct=consecutive_correct,
                consecutive_incorrect=consecutive_incorrect,
                session_duration=session_duration
            )
            
        except Exception as e:
            logger.error(f"Error assessing performance: {str(e)}")
            return self._create_baseline_metrics()
    
    def _calculate_engagement_score(self, 
                                  recent_responses: List[Dict[str, Any]],
                                  session_data: Dict[str, Any]) -> float:
        """Calculate student engagement score"""
        
        engagement_indicators = []
        
        # Response length (longer responses indicate engagement)
        for response in recent_responses:
            response_text = response.get("student_answer", "")
            if len(response_text) > 50:
                engagement_indicators.append(0.8)
            elif len(response_text) > 20:
                engagement_indicators.append(0.5)
            else:
                engagement_indicators.append(0.2)
        
        # Question asking (students asking questions shows engagement)
        questions_asked = sum(1 for r in recent_responses if "?" in r.get("student_answer", ""))
        if questions_asked > 0:
            engagement_indicators.append(0.9)
        
        # Session duration (reasonable time indicates engagement)
        session_duration = session_data.get("duration_minutes", 0)
        if 5 <= session_duration <= 30:
            engagement_indicators.append(0.8)
        elif session_duration > 30:
            engagement_indicators.append(0.6)  # Might be struggling
        else:
            engagement_indicators.append(0.3)  # Too short
        
        # Response time consistency (consistent times indicate focus)
        response_times = [r.get("response_time_sec", 30) for r in recent_responses]
        if response_times:
            time_variance = max(response_times) - min(response_times)
            if time_variance < 20:  # Consistent response times
                engagement_indicators.append(0.7)
        
        return sum(engagement_indicators) / len(engagement_indicators) if engagement_indicators else 0.5
    
    def _calculate_consecutive_correct(self, recent_responses: List[Dict[str, Any]]) -> int:
        """Calculate consecutive correct responses from end"""
        consecutive = 0
        for response in reversed(recent_responses):
            if response.get("is_correct", False):
                consecutive += 1
            else:
                break
        return consecutive
    
    def _calculate_consecutive_incorrect(self, recent_responses: List[Dict[str, Any]]) -> int:
        """Calculate consecutive incorrect responses from end"""
        consecutive = 0
        for response in reversed(recent_responses):
            if not response.get("is_correct", False):
                consecutive += 1
            else:
                break
        return consecutive
    
    async def determine_optimal_difficulty(self, 
                                         student_id: str,
                                         current_difficulty: DifficultyLevel,
                                         performance_metrics: PerformanceMetrics,
                                         student_profile: StudentProfile,
                                         subject: str = "math") -> Tuple[DifficultyLevel, AdaptationTrigger, str]:
        """Determine optimal difficulty level based on performance"""
        try:
            # Check for adaptation triggers
            adaptation_needed, trigger, reason = self._check_adaptation_triggers(
                performance_metrics, current_difficulty
            )
            
            if not adaptation_needed:
                return current_difficulty, None, "No adaptation needed"
            
            # Determine new difficulty level
            new_difficulty = await self._calculate_new_difficulty(
                student_id, current_difficulty, performance_metrics, 
                student_profile, subject, trigger
            )
            
            return new_difficulty, trigger, reason
            
        except Exception as e:
            logger.error(f"Error determining optimal difficulty: {str(e)}")
            return current_difficulty, None, f"Error: {str(e)}"
    
    def _check_adaptation_triggers(self, 
                                 metrics: PerformanceMetrics,
                                 current_difficulty: DifficultyLevel) -> Tuple[bool, Optional[AdaptationTrigger], str]:
        """Check if difficulty adaptation is needed"""
        
        config = self.adaptation_config
        
        # Check for consecutive success (increase difficulty)
        if metrics.consecutive_correct >= config["success_threshold"] and metrics.accuracy >= config["mastery_threshold"]:
            return True, AdaptationTrigger.CONSECUTIVE_SUCCESS, f"Student showing mastery with {metrics.consecutive_correct} consecutive correct answers"
        
        # Check for consecutive failure (decrease difficulty)
        if metrics.consecutive_incorrect >= config["failure_threshold"]:
            return True, AdaptationTrigger.CONSECUTIVE_FAILURE, f"Student struggling with {metrics.consecutive_incorrect} consecutive incorrect answers"
        
        # Check for overall struggle (decrease difficulty)
        if metrics.accuracy <= config["struggle_threshold"]:
            return True, AdaptationTrigger.CONFUSION_PATTERN, f"Overall accuracy of {metrics.accuracy:.2f} indicates struggle"
        
        # Check for low engagement (adjust difficulty to re-engage)
        if metrics.engagement_score <= config["engagement_threshold"]:
            return True, AdaptationTrigger.ENGAGEMENT_DROP, f"Low engagement score of {metrics.engagement_score:.2f}"
        
        # Check for boredom (very high accuracy, increase difficulty)
        if metrics.accuracy >= 0.95 and metrics.response_time < 15:
            return True, AdaptationTrigger.MASTERY_ACHIEVED, "Student may be bored with current difficulty level"
        
        return False, None, "Performance within acceptable range"
    
    async def _calculate_new_difficulty(self, 
                                      student_id: str,
                                      current_difficulty: DifficultyLevel,
                                      metrics: PerformanceMetrics,
                                      student_profile: StudentProfile,
                                      subject: str,
                                      trigger: AdaptationTrigger) -> DifficultyLevel:
        """Calculate new difficulty level based on trigger and performance"""
        
        difficulty_values = {
            DifficultyLevel.VERY_EASY: 1,
            DifficultyLevel.EASY: 2,
            DifficultyLevel.MEDIUM: 3,
            DifficultyLevel.HARD: 4,
            DifficultyLevel.VERY_HARD: 5
        }
        
        value_to_difficulty = {v: k for k, v in difficulty_values.items()}
        current_value = difficulty_values[current_difficulty]
        
        # Determine adjustment based on trigger
        if trigger == AdaptationTrigger.CONSECUTIVE_SUCCESS or trigger == AdaptationTrigger.MASTERY_ACHIEVED:
            # Increase difficulty
            new_value = min(5, current_value + self._calculate_increase_step(metrics, student_profile))
        
        elif trigger == AdaptationTrigger.CONSECUTIVE_FAILURE or trigger == AdaptationTrigger.CONFUSION_PATTERN:
            # Decrease difficulty
            new_value = max(1, current_value - self._calculate_decrease_step(metrics, student_profile))
        
        elif trigger == AdaptationTrigger.ENGAGEMENT_DROP:
            # Adjust to optimal engagement level
            if metrics.accuracy > 0.7:
                # Probably bored, increase difficulty
                new_value = min(5, current_value + 1)
            else:
                # Probably frustrated, decrease difficulty
                new_value = max(1, current_value - 1)
        
        else:
            # Default: no change
            new_value = current_value
        
        # Apply grade-level constraints
        new_value = self._apply_grade_constraints(new_value, student_profile.grade_level)
        
        return value_to_difficulty[new_value]
    
    def _calculate_increase_step(self, 
                               metrics: PerformanceMetrics,
                               student_profile: StudentProfile) -> int:
        """Calculate how much to increase difficulty"""
        
        # Base increase
        increase_step = 1
        
        # Accelerate for very high performance
        if metrics.accuracy >= 0.95 and metrics.consecutive_correct >= 5:
            increase_step = 2
        
        # Consider response time (quick responses may indicate readiness for more challenge)
        if metrics.response_time < 20:  # Quick responses
            increase_step += 1
        
        # Consider grade level (older students can handle bigger jumps)
        grade_num = 0 if student_profile.grade_level.value == 'K' else int(student_profile.grade_level.value)
        if grade_num >= 4:
            increase_step += 1
        
        return min(increase_step, 2)  # Cap at 2 levels
    
    def _calculate_decrease_step(self, 
                                metrics: PerformanceMetrics,
                                student_profile: StudentProfile) -> int:
        """Calculate how much to decrease difficulty"""
        
        # Base decrease
        decrease_step = 1
        
        # Bigger decrease for severe struggle
        if metrics.accuracy <= 0.2:
            decrease_step = 2
        elif metrics.confusion_indicators > 3:
            decrease_step = 2
        
        # Consider engagement (low engagement might need bigger adjustment)
        if metrics.engagement_score < 0.3:
            decrease_step += 1
        
        return min(decrease_step, 2)  # Cap at 2 levels
    
    def _apply_grade_constraints(self, 
                               difficulty_value: int,
                               grade_level: GradeLevel) -> int:
        """Apply grade-level constraints to difficulty"""
        
        # Define grade-appropriate difficulty ranges
        grade_ranges = {
            "K": (1, 2),    # K: very_easy to easy
            "1": (1, 3),    # 1: very_easy to medium
            "2": (1, 3),    # 2: very_easy to medium 
            "3": (2, 4),    # 3: easy to hard
            "4": (2, 5),    # 4: easy to very_hard
            "5": (2, 5)     # 5: easy to very_hard
        }
        
        grade_min, grade_max = grade_ranges.get(grade_level.value, (1, 5))
        
        return max(grade_min, min(grade_max, difficulty_value))
    
    async def adapt_content_difficulty(self, 
                                     student_id: str,
                                     topic: str,
                                     current_difficulty: DifficultyLevel,
                                     new_difficulty: DifficultyLevel,
                                     student_profile: StudentProfile) -> Dict[str, Any]:
        """Generate content adapted to new difficulty level"""
        try:
            if not self.gemini_client:
                raise Exception("Gemini client not initialized")
            
            # Get difficulty mapping info
            subject = "math"  # Default to math, could be inferred from topic
            current_mapping = self.difficulty_mappings[subject][current_difficulty]
            new_mapping = self.difficulty_mappings[subject][new_difficulty]
            
            # Build adaptation prompt
            adaptation_prompt = f"""Generate learning content adapted from {current_difficulty.value} to {new_difficulty.value} difficulty.

TOPIC: {topic}
STUDENT: Grade {student_profile.grade_level.value}, {student_profile.learning_style.value} learner

CURRENT DIFFICULTY: {current_mapping['description']}
NEW DIFFICULTY: {new_mapping['description']}

ADAPTATION REQUIREMENTS:
1. Adjust complexity to match new difficulty level
2. Maintain connection to original topic
3. Provide appropriate scaffolding for the transition
4. Include engagement elements for the grade level
5. Generate 2-3 example problems at the new difficulty

RESPONSE FORMAT (JSON):
{{
  "adapted_content": {{
    "explanation": "Content explanation at new difficulty level",
    "key_concepts": ["concept1", "concept2"],
    "scaffolding": "Support provided for difficulty transition",
    "examples": [
      {{"problem": "Example problem 1", "solution_approach": "How to solve"}},
      {{"problem": "Example problem 2", "solution_approach": "How to solve"}}
    ]
  }},
  "difficulty_justification": "Why this difficulty level is appropriate",
  "engagement_elements": ["element1", "element2"],
  "success_indicators": ["indicator1", "indicator2"]
}}"""

            # Generate adapted content
            from google.genai import types
            response = self.gemini_client.models.generate_content(
                model="gemini-2.5-flash",
                contents=adaptation_prompt,
                config=types.GenerateContentConfig(
                    temperature=0.7,
                    max_output_tokens=1024
                )
            )
            
            response_text = response.text
            adapted_content = self._parse_json_response(response_text)
            
            # Log the adaptation
            self._log_adaptation(student_id, current_difficulty, new_difficulty, topic)
            
            return adapted_content
            
        except Exception as e:
            logger.error(f"Error adapting content difficulty: {str(e)}")
            return self._create_fallback_adaptation(topic, new_difficulty)
    
    def _log_adaptation(self, 
                       student_id: str,
                       old_difficulty: DifficultyLevel,
                       new_difficulty: DifficultyLevel,
                       topic: str):
        """Log difficulty adaptation for analysis"""
        
        if student_id not in self.adaptation_history:
            self.adaptation_history[student_id] = []
        
        adaptation_log = {
            "timestamp": datetime.now().isoformat(),
            "topic": topic,
            "old_difficulty": old_difficulty.value,
            "new_difficulty": new_difficulty.value,
            "direction": "increase" if old_difficulty.value < new_difficulty.value else "decrease"
        }
        
        self.adaptation_history[student_id].append(adaptation_log)
    
    async def get_adaptation_recommendations(self, 
                                           student_id: str,
                                           current_performance: PerformanceMetrics,
                                           student_profile: StudentProfile) -> Dict[str, Any]:
        """Get recommendations for difficulty adaptation"""
        try:
            recommendations = []
            
            # Analyze current performance
            if current_performance.accuracy > 0.85:
                recommendations.append({
                    "type": "increase_difficulty",
                    "reason": "High accuracy indicates readiness for challenge",
                    "confidence": 0.8
                })
            
            elif current_performance.accuracy < 0.5:
                recommendations.append({
                    "type": "decrease_difficulty", 
                    "reason": "Low accuracy suggests content is too challenging",
                    "confidence": 0.9
                })
            
            # Analyze engagement
            if current_performance.engagement_score < 0.4:
                if current_performance.accuracy > 0.7:
                    recommendations.append({
                        "type": "increase_engagement",
                        "reason": "Student may be bored with current level",
                        "confidence": 0.7
                    })
                else:
                    recommendations.append({
                        "type": "provide_support",
                        "reason": "Student appears frustrated with difficulty",
                        "confidence": 0.8
                    })
            
            # Analyze patterns
            if current_performance.consecutive_correct >= 3:
                recommendations.append({
                    "type": "advance_topic",
                    "reason": "Consistent success indicates mastery",
                    "confidence": 0.85
                })
            
            elif current_performance.consecutive_incorrect >= 2:
                recommendations.append({
                    "type": "review_fundamentals",
                    "reason": "Multiple errors suggest need for foundation review",
                    "confidence": 0.9
                })
            
            # Generate adaptive teaching strategies
            teaching_strategies = self._generate_adaptive_strategies(
                current_performance, student_profile
            )
            
            return {
                "performance_analysis": {
                    "accuracy": current_performance.accuracy,
                    "engagement": current_performance.engagement_score,
                    "state": self._determine_performance_state(current_performance)
                },
                "recommendations": recommendations,
                "teaching_strategies": teaching_strategies,
                "optimal_session_length": self._recommend_session_length(current_performance),
                "break_recommendation": self._recommend_break(current_performance)
            }
            
        except Exception as e:
            logger.error(f"Error generating adaptation recommendations: {str(e)}")
            return {"error": str(e)}
    
    def _determine_performance_state(self, metrics: PerformanceMetrics) -> PerformanceState:
        """Determine current performance state"""
        
        if metrics.accuracy >= 0.9 and metrics.engagement_score >= 0.8:
            return PerformanceState.EXCELLING
        elif metrics.accuracy >= 0.7 and metrics.engagement_score >= 0.6:
            return PerformanceState.MASTERING
        elif metrics.accuracy >= 0.5 and metrics.engagement_score >= 0.4:
            return PerformanceState.LEARNING
        elif metrics.engagement_score < 0.3:
            return PerformanceState.BORED if metrics.accuracy > 0.8 else PerformanceState.STRUGGLING
        else:
            return PerformanceState.STRUGGLING
    
    def _generate_adaptive_strategies(self, 
                                    metrics: PerformanceMetrics,
                                    student_profile: StudentProfile) -> List[str]:
        """Generate adaptive teaching strategies"""
        
        strategies = []
        
        # Based on performance state
        state = self._determine_performance_state(metrics)
        
        if state == PerformanceState.EXCELLING:
            strategies.extend([
                "Provide advanced challenges and extensions",
                "Encourage peer tutoring opportunities",
                "Introduce cross-curricular connections"
            ])
        
        elif state == PerformanceState.MASTERING:
            strategies.extend([
                "Gradually increase complexity",
                "Introduce real-world applications",
                "Provide choice in problem types"
            ])
        
        elif state == PerformanceState.LEARNING:
            strategies.extend([
                "Maintain current approach with minor adjustments",
                "Provide regular encouragement and feedback",
                "Use varied examples and representations"
            ])
        
        elif state == PerformanceState.STRUGGLING:
            strategies.extend([
                "Break down concepts into smaller steps",
                "Provide additional scaffolding and support",
                "Use concrete examples and manipulatives",
                "Consider one-on-one assistance"
            ])
        
        elif state == PerformanceState.BORED:
            strategies.extend([
                "Increase challenge and complexity",
                "Provide creative and open-ended problems",
                "Allow student choice in learning path"
            ])
        
        # Based on learning style
        if student_profile.learning_style.value == "visual":
            strategies.append("Emphasize visual representations and diagrams")
        elif student_profile.learning_style.value == "auditory":
            strategies.append("Include verbal explanations and discussions")
        elif student_profile.learning_style.value == "kinesthetic":
            strategies.append("Incorporate hands-on activities and movement")
        
        return strategies[:5]  # Return top 5 strategies
    
    def _recommend_session_length(self, metrics: PerformanceMetrics) -> int:
        """Recommend optimal session length in minutes"""
        
        # Base on engagement and current session performance
        if metrics.engagement_score > 0.8:
            return min(45, metrics.session_duration + 10)  # Can extend slightly
        elif metrics.engagement_score > 0.5:
            return max(15, min(30, metrics.session_duration))  # Maintain current
        else:
            return max(10, metrics.session_duration - 5)  # Shorten session
    
    def _recommend_break(self, metrics: PerformanceMetrics) -> Dict[str, Any]:
        """Recommend if a break is needed"""
        
        break_needed = False
        break_type = "none"
        reason = ""
        
        # Long session check
        if metrics.session_duration > 45:
            break_needed = True
            break_type = "long_break"
            reason = "Extended session duration"
        
        # Low engagement check
        elif metrics.engagement_score < 0.3:
            break_needed = True
            break_type = "re-energizing_break"
            reason = "Low engagement levels"
        
        # Frustration check
        elif metrics.consecutive_incorrect >= 3:
            break_needed = True
            break_type = "reset_break"
            reason = "Multiple consecutive errors"
        
        return {
            "break_needed": break_needed,
            "break_type": break_type,
            "reason": reason,
            "suggested_duration": 5 if break_type == "short_break" else 10
        }
    
    def _create_baseline_metrics(self) -> PerformanceMetrics:
        """Create baseline performance metrics"""
        return PerformanceMetrics(
            accuracy=0.5,
            response_time=30.0,
            engagement_score=0.5,
            confusion_indicators=0,
            help_requests=0,
            consecutive_correct=0,
            consecutive_incorrect=0,
            session_duration=0
        )
    
    def _parse_json_response(self, response_text: str) -> Dict[str, Any]:
        """Parse JSON response with error handling"""
        try:
            if response_text.strip().startswith('{'):
                return json.loads(response_text)
            
            import re
            json_match = re.search(r'```json\s*(\{.*?\})\s*```', response_text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group(1))
            
            return self._create_fallback_adaptation("Unknown topic", DifficultyLevel.MEDIUM)
            
        except Exception as e:
            logger.error(f"Error parsing JSON: {str(e)}")
            return self._create_fallback_adaptation("Unknown topic", DifficultyLevel.MEDIUM)
    
    def _create_fallback_adaptation(self, topic: str, difficulty: DifficultyLevel) -> Dict[str, Any]:
        """Create fallback adaptation when AI generation fails"""
        return {
            "adapted_content": {
                "explanation": f"Let's work on {topic} at {difficulty.value} level.",
                "key_concepts": [topic],
                "scaffolding": "I'll provide step-by-step guidance.",
                "examples": [
                    {"problem": f"Practice problem for {topic}", "solution_approach": "Work through it step by step"}
                ]
            },
            "difficulty_justification": f"Adjusted to {difficulty.value} level based on performance",
            "engagement_elements": ["Interactive practice", "Immediate feedback"],
            "success_indicators": ["Improved accuracy", "Increased confidence"]
        }
    
    async def get_difficulty_analytics(self, student_id: str) -> Dict[str, Any]:
        """Get analytics on difficulty adaptations for a student"""
        try:
            adaptations = self.adaptation_history.get(student_id, [])
            
            if not adaptations:
                return {
                    "total_adaptations": 0,
                    "adaptation_patterns": "No adaptation data available",
                    "recommendations": "Continue tracking performance for analysis"
                }
            
            # Analyze adaptation patterns
            increases = sum(1 for a in adaptations if a["direction"] == "increase")
            decreases = sum(1 for a in adaptations if a["direction"] == "decrease")
            
            # Recent trend
            recent_adaptations = adaptations[-5:] if len(adaptations) >= 5 else adaptations
            recent_trend = "increasing" if sum(1 for a in recent_adaptations if a["direction"] == "increase") > len(recent_adaptations) // 2 else "decreasing"
            
            return {
                "student_id": student_id,
                "total_adaptations": len(adaptations),
                "difficulty_increases": increases,
                "difficulty_decreases": decreases,
                "recent_trend": recent_trend,
                "most_recent_adaptation": adaptations[-1] if adaptations else None,
                "adaptation_frequency": len(adaptations) / max(1, len(set(a["timestamp"][:10] for a in adaptations))),  # Adaptations per day
                "learning_trajectory": "progressive" if increases > decreases else "supportive"
            }
            
        except Exception as e:
            logger.error(f"Error getting difficulty analytics: {str(e)}")
            return {"error": str(e)}
    
    def is_healthy(self) -> bool:
        """Check if adaptive difficulty engine is healthy"""
        return self.gemini_client is not None
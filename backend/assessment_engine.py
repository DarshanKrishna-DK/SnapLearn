"""
Advanced Assessment Engine for SnapLearn AI - Phase 3
Detects mistake patterns, provides detailed feedback, and adapts teaching strategies
"""

import os
import logging
import json
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime
import re
from dataclasses import dataclass
from enum import Enum

from models import (
    StudentProfile, 
    AssessmentResponse,
    GradeLevel, 
    LanguageCode
)

from utils import schedule_async_init

logger = logging.getLogger(__name__)

class MistakeType(str, Enum):
    """Categories of learning mistakes"""
    CONCEPTUAL = "conceptual"           # Misunderstanding core concepts
    PROCEDURAL = "procedural"           # Wrong steps or methods
    COMPUTATIONAL = "computational"     # Calculation errors
    NOTATION = "notation"               # Mathematical notation errors
    READING = "reading"                 # Misreading problem
    ATTENTION = "attention"             # Careless mistakes
    INCOMPLETE = "incomplete"           # Partial answers
    MISCONCEPTION = "misconception"     # Fundamental misunderstanding

class FeedbackType(str, Enum):
    """Types of feedback to provide"""
    CORRECTIVE = "corrective"           # Direct correction
    GUIDING = "guiding"                 # Leading questions
    ENCOURAGING = "encouraging"         # Positive reinforcement
    EXPLANATORY = "explanatory"         # Detailed explanation
    EXAMPLE_BASED = "example_based"     # Using examples
    VISUAL = "visual"                   # Visual demonstrations

@dataclass
class MistakePattern:
    """Represents a detected mistake pattern"""
    mistake_type: MistakeType
    description: str
    frequency: int
    confidence: float
    examples: List[str]
    suggested_intervention: str

class AssessmentEngine:
    """Advanced assessment with mistake pattern detection and adaptive feedback"""
    
    def __init__(self):
        self.gemini_client = None
        self.mistake_patterns_db = {}  # Student mistake patterns
        self.intervention_strategies = {}
        
        # Initialize assessment rubrics
        self._init_assessment_rubrics()
        
        # Initialize Gemini
        schedule_async_init(self._init_gemini())
    
    async def _init_gemini(self):
        """Initialize Gemini client for assessment"""
        try:
            from google import genai
            
            api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
            if not api_key:
                logger.error("Gemini API key not found for assessment engine")
                return
            
            self.gemini_client = genai.Client(api_key=api_key)
            logger.info("Assessment engine: Gemini client initialized")
            
        except ImportError:
            logger.error("Google GenAI library not installed for assessment")
        except Exception as e:
            logger.error(f"Error initializing Gemini for assessment: {str(e)}")
    
    def _init_assessment_rubrics(self):
        """Initialize grade-level assessment rubrics"""
        self.assessment_rubrics = {
            "K": {
                "expectations": "Basic recognition and counting",
                "key_skills": ["counting", "shapes", "colors", "patterns"],
                "common_mistakes": ["number sequence errors", "shape confusion"]
            },
            "1": {
                "expectations": "Single-digit operations, basic reading",
                "key_skills": ["addition", "subtraction", "number recognition"],
                "common_mistakes": ["counting on fingers", "number reversal"]
            },
            "2": {
                "expectations": "Two-digit operations, place value",
                "key_skills": ["place value", "regrouping", "time"],
                "common_mistakes": ["place value confusion", "regrouping errors"]
            },
            "3": {
                "expectations": "Multiplication, division basics, fractions",
                "key_skills": ["multiplication tables", "division", "basic fractions"],
                "common_mistakes": ["multiplication facts", "fraction understanding"]
            },
            "4": {
                "expectations": "Multi-digit operations, decimals, fractions",
                "key_skills": ["long division", "decimals", "equivalent fractions"],
                "common_mistakes": ["decimal placement", "fraction operations"]
            },
            "5": {
                "expectations": "Advanced fractions, geometry, measurement",
                "key_skills": ["fraction operations", "area", "volume"],
                "common_mistakes": ["fraction multiplication", "unit conversion"]
            }
            # ... can be extended for higher grades
        }
    
    async def assess_comprehensive(self, 
                                 student_id: str,
                                 question: str,
                                 student_answer: str,
                                 student_profile: StudentProfile,
                                 conversation_context: Optional[Dict] = None) -> Dict[str, Any]:
        """Comprehensive assessment with mistake pattern detection"""
        try:
            logger.info(f"Comprehensive assessment for student {student_id}")
            
            # Get assessment rubric for grade level
            rubric = self.assessment_rubrics.get(student_profile.grade_level.value, 
                                                self.assessment_rubrics["4"])
            
            # Generate AI-powered detailed assessment
            ai_assessment = await self._generate_ai_assessment(
                question, student_answer, student_profile, rubric, conversation_context
            )
            
            # Detect mistake patterns
            mistake_patterns = await self._detect_mistake_patterns(
                student_id, question, student_answer, ai_assessment
            )
            
            # Generate targeted feedback
            feedback = await self._generate_targeted_feedback(
                student_answer, mistake_patterns, student_profile
            )
            
            # Determine intervention strategy
            intervention = self._determine_intervention_strategy(mistake_patterns, student_profile)
            
            # Update student mistake patterns database
            self._update_mistake_patterns_db(student_id, mistake_patterns)
            
            # Create comprehensive assessment response
            assessment_result = {
                "is_correct": ai_assessment.get("is_correct", False),
                "confidence_score": ai_assessment.get("confidence_score", 0.0),
                "feedback": feedback["primary_feedback"],
                "detailed_feedback": feedback,
                "mistake_patterns": [pattern.__dict__ for pattern in mistake_patterns],
                "intervention_strategy": intervention,
                "learning_insights": self._generate_learning_insights(student_id, mistake_patterns),
                "next_steps": self._generate_next_steps(mistake_patterns, student_profile),
                "mastery_indicators": ai_assessment.get("mastery_indicators", []),
                "timestamp": datetime.now()
            }
            
            return assessment_result
            
        except Exception as e:
            logger.error(f"Error in comprehensive assessment: {str(e)}")
            raise
    
    async def _generate_ai_assessment(self, 
                                    question: str,
                                    student_answer: str,
                                    student_profile: StudentProfile,
                                    rubric: Dict[str, Any],
                                    conversation_context: Optional[Dict] = None) -> Dict[str, Any]:
        """Generate AI-powered assessment using Gemini"""
        try:
            if not self.gemini_client:
                raise Exception("Gemini client not initialized")
            
            # Build comprehensive assessment prompt
            assessment_prompt = f"""You are an expert educational assessor. Provide a detailed assessment of this student's answer.

QUESTION: {question}
STUDENT ANSWER: {student_answer}

STUDENT PROFILE:
- Grade Level: {student_profile.grade_level.value}
- Learning Style: {student_profile.learning_style.value}
- Previous Strengths: {list(student_profile.success_patterns.keys())[:3]}
- Previous Challenges: {list(student_profile.confusion_patterns.keys())[:3]}

GRADE-LEVEL EXPECTATIONS:
- Expected Skills: {rubric['key_skills']}
- Common Mistakes: {rubric['common_mistakes']}
- Grade Standards: {rubric['expectations']}

CONVERSATION CONTEXT:
{json.dumps(conversation_context, indent=2) if conversation_context else "No prior context"}

ASSESSMENT REQUIREMENTS:
1. Determine correctness and partial credit
2. Identify specific mistakes and their types
3. Detect misconceptions vs. careless errors
4. Assess conceptual understanding vs. procedural knowledge
5. Evaluate communication and reasoning
6. Identify mastery indicators and growth areas

RESPONSE FORMAT (JSON):
{{
  "is_correct": true/false,
  "partial_credit": 0.0-1.0,
  "confidence_score": 0.0-1.0,
  "mistake_analysis": {{
    "primary_mistakes": ["mistake1", "mistake2"],
    "mistake_types": ["conceptual", "procedural", "computational"],
    "severity": "low|medium|high",
    "patterns": ["pattern1", "pattern2"]
  }},
  "understanding_assessment": {{
    "conceptual_understanding": "strong|developing|weak",
    "procedural_fluency": "strong|developing|weak", 
    "problem_solving_approach": "systematic|partial|unclear",
    "communication_clarity": "clear|adequate|unclear"
  }},
  "mastery_indicators": ["indicator1", "indicator2"],
  "growth_areas": ["area1", "area2"],
  "suggested_next_difficulty": "easier|same|harder",
  "suggested_explanation_style": "visual|verbal|step_by_step|conceptual|practical"
}}"""

            # Use Gemini Interactions API for assessment
            from google.genai import types
            response = self.gemini_client.models.generate_content(
                model="gemini-2.5-flash",
                contents=assessment_prompt,
                config=types.GenerateContentConfig(
                    temperature=0.2,  # Lower temperature for consistent assessment
                    max_output_tokens=1024
                )
            )
            
            response_text = response.text
            return self._parse_json_response(response_text)
            
        except Exception as e:
            logger.error(f"Error generating AI assessment: {str(e)}")
            return self._create_fallback_assessment()
    
    async def _detect_mistake_patterns(self, 
                                     student_id: str,
                                     question: str,
                                     student_answer: str,
                                     ai_assessment: Dict[str, Any]) -> List[MistakePattern]:
        """Detect and categorize mistake patterns"""
        try:
            patterns = []
            mistake_analysis = ai_assessment.get("mistake_analysis", {})
            
            # Get student's historical patterns
            historical_patterns = self.mistake_patterns_db.get(student_id, {})
            
            # Analyze each identified mistake
            for mistake in mistake_analysis.get("primary_mistakes", []):
                pattern = await self._classify_mistake_pattern(
                    mistake, question, student_answer, historical_patterns
                )
                if pattern:
                    patterns.append(pattern)
            
            # Detect recurring patterns
            recurring_patterns = self._detect_recurring_patterns(student_id, patterns)
            patterns.extend(recurring_patterns)
            
            return patterns
            
        except Exception as e:
            logger.error(f"Error detecting mistake patterns: {str(e)}")
            return []
    
    async def _classify_mistake_pattern(self, 
                                      mistake: str,
                                      question: str,
                                      student_answer: str,
                                      historical: Dict[str, Any]) -> Optional[MistakePattern]:
        """Classify a specific mistake into patterns"""
        
        # Pattern classification rules
        classification_rules = [
            # Conceptual mistakes
            (["concept", "understand", "meaning", "definition"], MistakeType.CONCEPTUAL),
            
            # Procedural mistakes  
            (["step", "method", "process", "procedure", "algorithm"], MistakeType.PROCEDURAL),
            
            # Computational mistakes
            (["calculate", "arithmetic", "computation", "math", "number"], MistakeType.COMPUTATIONAL),
            
            # Notation mistakes
            (["symbol", "notation", "write", "format", "expression"], MistakeType.NOTATION),
            
            # Reading mistakes
            (["misread", "reading", "interpretation", "problem"], MistakeType.READING),
            
            # Attention mistakes
            (["careless", "rushed", "overlooked", "missed"], MistakeType.ATTENTION)
        ]
        
        mistake_lower = mistake.lower()
        
        for keywords, mistake_type in classification_rules:
            if any(keyword in mistake_lower for keyword in keywords):
                # Check frequency in historical data
                frequency = historical.get(mistake_type.value, 0) + 1
                
                return MistakePattern(
                    mistake_type=mistake_type,
                    description=mistake,
                    frequency=frequency,
                    confidence=0.8,
                    examples=[student_answer],
                    suggested_intervention=self._get_intervention_for_mistake_type(mistake_type)
                )
        
        # Default to conceptual if unclear
        return MistakePattern(
            mistake_type=MistakeType.CONCEPTUAL,
            description=mistake,
            frequency=1,
            confidence=0.6,
            examples=[student_answer],
            suggested_intervention="Review fundamental concepts"
        )
    
    def _get_intervention_for_mistake_type(self, mistake_type: MistakeType) -> str:
        """Get intervention strategy for specific mistake type"""
        interventions = {
            MistakeType.CONCEPTUAL: "Provide visual explanations and concrete examples",
            MistakeType.PROCEDURAL: "Break down steps and practice similar problems",
            MistakeType.COMPUTATIONAL: "Review basic arithmetic and use calculators when appropriate",
            MistakeType.NOTATION: "Practice proper mathematical notation and symbols",
            MistakeType.READING: "Read problems aloud and highlight key information",
            MistakeType.ATTENTION: "Slow down and check work systematically",
            MistakeType.INCOMPLETE: "Encourage complete solutions and explanations",
            MistakeType.MISCONCEPTION: "Address fundamental misunderstanding with new examples"
        }
        
        return interventions.get(mistake_type, "Provide additional practice and support")
    
    def _detect_recurring_patterns(self, 
                                 student_id: str, 
                                 current_patterns: List[MistakePattern]) -> List[MistakePattern]:
        """Detect patterns that occur frequently over time"""
        recurring = []
        historical = self.mistake_patterns_db.get(student_id, {})
        
        for pattern in current_patterns:
            if pattern.mistake_type.value in historical:
                if historical[pattern.mistake_type.value]["frequency"] >= 3:
                    # This is a recurring pattern
                    recurring_pattern = MistakePattern(
                        mistake_type=pattern.mistake_type,
                        description=f"Recurring {pattern.mistake_type.value} errors",
                        frequency=historical[pattern.mistake_type.value]["frequency"] + 1,
                        confidence=0.9,
                        examples=historical[pattern.mistake_type.value].get("examples", []),
                        suggested_intervention=f"Intensive intervention needed for {pattern.mistake_type.value} issues"
                    )
                    recurring.append(recurring_pattern)
        
        return recurring
    
    async def _generate_targeted_feedback(self, 
                                        student_answer: str,
                                        mistake_patterns: List[MistakePattern],
                                        student_profile: StudentProfile) -> Dict[str, Any]:
        """Generate personalized feedback based on mistake patterns"""
        try:
            if not mistake_patterns:
                return {
                    "primary_feedback": "Great job! Your answer demonstrates good understanding.",
                    "feedback_type": FeedbackType.ENCOURAGING,
                    "specific_feedback": [],
                    "improvement_suggestions": [],
                    "positive_reinforcement": ["Clear reasoning", "Good approach"]
                }
            
            # Categorize mistakes by severity and type
            high_priority_patterns = [p for p in mistake_patterns if p.confidence > 0.8]
            recurring_patterns = [p for p in mistake_patterns if p.frequency >= 3]
            
            # Generate different feedback for different mistake types
            feedback_components = []
            
            for pattern in high_priority_patterns:
                feedback = await self._generate_pattern_specific_feedback(
                    pattern, student_answer, student_profile
                )
                feedback_components.append(feedback)
            
            # Compile comprehensive feedback
            primary_feedback = self._compile_primary_feedback(feedback_components, student_profile)
            
            return {
                "primary_feedback": primary_feedback,
                "feedback_type": self._determine_feedback_type(mistake_patterns),
                "specific_feedback": feedback_components,
                "improvement_suggestions": [p.suggested_intervention for p in high_priority_patterns],
                "recurring_issues": [p.description for p in recurring_patterns],
                "positive_reinforcement": self._identify_positive_aspects(student_answer, student_profile)
            }
            
        except Exception as e:
            logger.error(f"Error generating targeted feedback: {str(e)}")
            return {"primary_feedback": "Let me help you improve your answer."}
    
    async def _generate_pattern_specific_feedback(self, 
                                                pattern: MistakePattern,
                                                student_answer: str,
                                                student_profile: StudentProfile) -> str:
        """Generate specific feedback for a mistake pattern"""
        
        if pattern.mistake_type == MistakeType.CONCEPTUAL:
            return f"I notice you might be unclear about the core concept. Let's revisit the fundamental idea behind this problem."
        
        elif pattern.mistake_type == MistakeType.PROCEDURAL:
            return f"Your approach shows good thinking, but let's work on the specific steps. Here's how to break it down systematically."
        
        elif pattern.mistake_type == MistakeType.COMPUTATIONAL:
            return f"Great reasoning! There's just a small calculation error. Let's double-check the arithmetic together."
        
        elif pattern.mistake_type == MistakeType.NOTATION:
            return f"Your understanding is solid - let's just clean up the mathematical notation to make it clearer."
        
        elif pattern.mistake_type == MistakeType.READING:
            return f"I think there might be a small misunderstanding of what the problem is asking. Let's read it together carefully."
        
        elif pattern.mistake_type == MistakeType.ATTENTION:
            return f"You're on the right track! Let's just slow down and double-check each step carefully."
        
        else:
            return f"Let's work together to improve this answer. I can see you understand parts of it!"
    
    def _compile_primary_feedback(self, 
                                feedback_components: List[str],
                                student_profile: StudentProfile) -> str:
        """Compile individual feedback into primary message"""
        
        if not feedback_components:
            return "Great effort! Your answer shows good thinking."
        
        # Adapt tone for grade level
        grade_num = 0 if student_profile.grade_level.value == 'K' else int(student_profile.grade_level.value)
        
        if grade_num <= 2:
            tone = "Great try! "
        elif grade_num <= 5:
            tone = "Good work! "
        else:
            tone = "I can see your reasoning. "
        
        # Combine feedback with encouraging tone
        main_feedback = feedback_components[0] if feedback_components else "Let's improve this together."
        
        return tone + main_feedback
    
    def _determine_feedback_type(self, mistake_patterns: List[MistakePattern]) -> FeedbackType:
        """Determine the most appropriate feedback approach"""
        
        if not mistake_patterns:
            return FeedbackType.ENCOURAGING
        
        # Check for recurring patterns
        if any(p.frequency >= 3 for p in mistake_patterns):
            return FeedbackType.EXPLANATORY
        
        # Check for conceptual issues
        if any(p.mistake_type == MistakeType.CONCEPTUAL for p in mistake_patterns):
            return FeedbackType.VISUAL
        
        # Check for procedural issues
        if any(p.mistake_type == MistakeType.PROCEDURAL for p in mistake_patterns):
            return FeedbackType.GUIDING
        
        # Default to corrective
        return FeedbackType.CORRECTIVE
    
    def _identify_positive_aspects(self, 
                                 student_answer: str,
                                 student_profile: StudentProfile) -> List[str]:
        """Identify positive aspects to reinforce"""
        positive_aspects = []
        
        answer_lower = student_answer.lower()
        
        # Look for positive indicators
        if len(student_answer) > 50:
            positive_aspects.append("Detailed explanation")
        
        if any(word in answer_lower for word in ["because", "therefore", "so", "since"]):
            positive_aspects.append("Shows reasoning")
        
        if any(word in answer_lower for word in ["first", "then", "next", "finally"]):
            positive_aspects.append("Organized approach")
        
        if any(char in student_answer for char in "+-*/="):
            positive_aspects.append("Uses mathematical notation")
        
        if any(word in answer_lower for word in ["example", "like", "such as"]):
            positive_aspects.append("Provides examples")
        
        return positive_aspects or ["Shows effort and engagement"]
    
    def _determine_intervention_strategy(self, 
                                       mistake_patterns: List[MistakePattern],
                                       student_profile: StudentProfile) -> Dict[str, Any]:
        """Determine the best intervention strategy"""
        
        if not mistake_patterns:
            return {
                "strategy": "advancement",
                "description": "Student is ready for more challenging content",
                "priority": "low",
                "timeline": "immediate"
            }
        
        # Analyze mistake severity and frequency
        high_frequency_patterns = [p for p in mistake_patterns if p.frequency >= 3]
        conceptual_issues = [p for p in mistake_patterns if p.mistake_type == MistakeType.CONCEPTUAL]
        
        if high_frequency_patterns:
            return {
                "strategy": "intensive_support",
                "description": "Multiple recurring issues need targeted intervention",
                "priority": "high",
                "timeline": "multiple_sessions",
                "focus_areas": [p.mistake_type.value for p in high_frequency_patterns]
            }
        
        elif conceptual_issues:
            return {
                "strategy": "conceptual_review",
                "description": "Fundamental concepts need reinforcement",
                "priority": "medium",
                "timeline": "next_session",
                "focus_areas": ["conceptual_understanding"]
            }
        
        else:
            return {
                "strategy": "skill_refinement",
                "description": "Minor adjustments and practice needed",
                "priority": "low", 
                "timeline": "ongoing_practice"
            }
    
    def _update_mistake_patterns_db(self, 
                                   student_id: str, 
                                   patterns: List[MistakePattern]):
        """Update the mistake patterns database for a student"""
        
        if student_id not in self.mistake_patterns_db:
            self.mistake_patterns_db[student_id] = {}
        
        student_db = self.mistake_patterns_db[student_id]
        
        for pattern in patterns:
            pattern_key = pattern.mistake_type.value
            
            if pattern_key in student_db:
                student_db[pattern_key]["frequency"] += 1
                student_db[pattern_key]["examples"].append(pattern.examples[0] if pattern.examples else "")
                student_db[pattern_key]["last_seen"] = datetime.now().isoformat()
            else:
                student_db[pattern_key] = {
                    "frequency": pattern.frequency,
                    "examples": pattern.examples,
                    "first_seen": datetime.now().isoformat(),
                    "last_seen": datetime.now().isoformat(),
                    "intervention_attempts": 0
                }
    
    def _generate_learning_insights(self, 
                                  student_id: str, 
                                  current_patterns: List[MistakePattern]) -> Dict[str, Any]:
        """Generate insights about student's learning patterns"""
        
        historical = self.mistake_patterns_db.get(student_id, {})
        
        # Analyze trends
        improving_areas = []
        concerning_areas = []
        stable_areas = []
        
        for pattern_type, data in historical.items():
            if data["frequency"] == 1:
                stable_areas.append(pattern_type)
            elif data["frequency"] >= 3:
                concerning_areas.append(pattern_type)
            else:
                improving_areas.append(pattern_type)
        
        return {
            "total_mistake_types": len(historical),
            "improving_areas": improving_areas,
            "concerning_areas": concerning_areas,
            "stable_areas": stable_areas,
            "most_common_mistake": max(historical.keys(), 
                                     key=lambda x: historical[x]["frequency"]) if historical else None,
            "intervention_effectiveness": self._calculate_intervention_effectiveness(student_id),
            "learning_velocity": self._calculate_learning_velocity(student_id)
        }
    
    def _calculate_intervention_effectiveness(self, student_id: str) -> float:
        """Calculate how effective interventions have been"""
        historical = self.mistake_patterns_db.get(student_id, {})
        
        if not historical:
            return 0.0
        
        total_interventions = sum(data.get("intervention_attempts", 0) for data in historical.values())
        resolved_issues = sum(1 for data in historical.values() if data["frequency"] <= 1)
        
        if total_interventions == 0:
            return 0.0
        
        return resolved_issues / len(historical)
    
    def _calculate_learning_velocity(self, student_id: str) -> str:
        """Calculate how quickly student is learning"""
        historical = self.mistake_patterns_db.get(student_id, {})
        
        if not historical:
            return "unknown"
        
        # Simple heuristic based on mistake frequency trends
        avg_frequency = sum(data["frequency"] for data in historical.values()) / len(historical)
        
        if avg_frequency <= 1.5:
            return "fast"
        elif avg_frequency <= 2.5:
            return "steady"
        else:
            return "needs_support"
    
    def _generate_next_steps(self, 
                           mistake_patterns: List[MistakePattern],
                           student_profile: StudentProfile) -> List[str]:
        """Generate specific next steps for improvement"""
        
        next_steps = []
        
        if not mistake_patterns:
            next_steps.append("Continue with more challenging problems")
            next_steps.append("Explore advanced applications of this concept")
            return next_steps
        
        # Generate steps based on mistake types
        mistake_types = [p.mistake_type for p in mistake_patterns]
        
        if MistakeType.CONCEPTUAL in mistake_types:
            next_steps.append("Review the fundamental concepts with visual aids")
            next_steps.append("Practice with simpler examples to build foundation")
        
        if MistakeType.PROCEDURAL in mistake_types:
            next_steps.append("Practice the step-by-step method with guided examples")
            next_steps.append("Create a checklist for solving similar problems")
        
        if MistakeType.COMPUTATIONAL in mistake_types:
            next_steps.append("Practice basic arithmetic facts")
            next_steps.append("Use estimation to check answer reasonableness")
        
        # Always include positive next step
        next_steps.append(f"Continue practicing - you're making good progress!")
        
        return next_steps[:5]  # Limit to 5 steps
    
    def _parse_json_response(self, response_text: str) -> Dict[str, Any]:
        """Parse JSON response with fallback handling"""
        try:
            # Try direct JSON parsing
            if response_text.strip().startswith('{'):
                return json.loads(response_text)
            
            # Extract JSON from markdown code blocks
            import re
            json_match = re.search(r'```json\s*(\{.*?\})\s*```', response_text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group(1))
            
            # Fallback parsing
            return self._create_fallback_assessment()
            
        except Exception as e:
            logger.error(f"Error parsing JSON response: {str(e)}")
            return self._create_fallback_assessment()
    
    def _create_fallback_assessment(self) -> Dict[str, Any]:
        """Create fallback assessment when AI assessment fails"""
        return {
            "is_correct": False,
            "partial_credit": 0.5,
            "confidence_score": 0.5,
            "mistake_analysis": {
                "primary_mistakes": ["Unable to analyze - technical issue"],
                "mistake_types": ["technical"],
                "severity": "low",
                "patterns": []
            },
            "understanding_assessment": {
                "conceptual_understanding": "developing",
                "procedural_fluency": "developing",
                "problem_solving_approach": "partial",
                "communication_clarity": "adequate"
            },
            "mastery_indicators": [],
            "growth_areas": ["Practice and review"],
            "suggested_next_difficulty": "same",
            "suggested_explanation_style": "visual"
        }
    
    async def get_student_assessment_analytics(self, student_id: str) -> Dict[str, Any]:
        """Get comprehensive assessment analytics for a student"""
        try:
            historical = self.mistake_patterns_db.get(student_id, {})
            
            if not historical:
                return {
                    "total_assessments": 0,
                    "mistake_patterns": [],
                    "learning_insights": "Insufficient data for analysis",
                    "recommendations": ["Continue practicing to build assessment data"]
                }
            
            # Calculate analytics
            total_mistakes = sum(data["frequency"] for data in historical.values())
            most_common_mistakes = sorted(
                historical.items(),
                key=lambda x: x[1]["frequency"],
                reverse=True
            )[:5]
            
            # Generate recommendations
            recommendations = []
            for mistake_type, data in most_common_mistakes:
                if data["frequency"] >= 3:
                    recommendations.append(f"Focus on improving {mistake_type.replace('_', ' ')} skills")
            
            return {
                "student_id": student_id,
                "total_assessments": len(historical),
                "total_mistakes_logged": total_mistakes,
                "most_common_mistakes": most_common_mistakes,
                "improvement_areas": [item[0] for item in most_common_mistakes[:3]],
                "learning_velocity": self._calculate_learning_velocity(student_id),
                "intervention_effectiveness": self._calculate_intervention_effectiveness(student_id),
                "recommendations": recommendations,
                "last_assessment": max(data.get("last_seen", "") for data in historical.values()) if historical else None
            }
            
        except Exception as e:
            logger.error(f"Error getting assessment analytics: {str(e)}")
            return {"error": str(e)}
    
    def is_healthy(self) -> bool:
        """Check if assessment engine is healthy"""
        return self.gemini_client is not None
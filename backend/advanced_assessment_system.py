"""
Advanced Assessment and Testing System for SnapLearn AI - Phase 5
Comprehensive evaluation, certification, and credentialing system
"""

import os
import logging
import json
import uuid
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime, timedelta
from pathlib import Path
from enum import Enum
from dataclasses import dataclass
import statistics

from models import (
    StudentProfile,
    ExplanationResponse,
    AssessmentAnalytics,
    LearningAnalytics
)

from utils import schedule_async_init

logger = logging.getLogger(__name__)

class AssessmentType(str, Enum):
    """Types of assessments available"""
    DIAGNOSTIC = "diagnostic"           # Initial skill assessment
    FORMATIVE = "formative"            # Ongoing progress check
    SUMMATIVE = "summative"            # Final evaluation
    ADAPTIVE = "adaptive"              # AI-driven adaptive testing
    COMPETENCY = "competency"          # Skill-based evaluation
    CERTIFICATION = "certification"    # Official credentialing
    BENCHMARK = "benchmark"            # Standardized comparison

class QuestionType(str, Enum):
    """Question types supported"""
    MULTIPLE_CHOICE = "multiple_choice"
    TRUE_FALSE = "true_false"
    SHORT_ANSWER = "short_answer"
    LONG_ANSWER = "long_answer"
    MATHEMATICAL = "mathematical"
    CODE_COMPLETION = "code_completion"
    DRAG_DROP = "drag_drop"
    DRAWING = "drawing"
    VOICE_RESPONSE = "voice_response"

class DifficultyLevel(str, Enum):
    """Question difficulty levels"""
    BEGINNER = "beginner"
    ELEMENTARY = "elementary"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"

class AssessmentStatus(str, Enum):
    """Assessment completion status"""
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    SUBMITTED = "submitted"
    GRADED = "graded"
    CERTIFIED = "certified"

@dataclass
class AssessmentQuestion:
    """Individual assessment question"""
    question_id: str
    question_type: QuestionType
    subject: str
    topic: str
    difficulty: DifficultyLevel
    question_text: str
    options: Optional[List[str]] = None
    correct_answer: Optional[str] = None
    explanation: Optional[str] = None
    points: int = 1
    time_limit_seconds: Optional[int] = None
    media_attachments: Optional[List[str]] = None
    rubric: Optional[Dict[str, Any]] = None

@dataclass
class StudentResponse:
    """Student's response to assessment question"""
    response_id: str
    question_id: str
    student_id: str
    response_text: Optional[str] = None
    selected_options: Optional[List[str]] = None
    response_time_seconds: float = 0.0
    confidence_level: Optional[float] = None
    work_shown: Optional[str] = None
    media_response: Optional[str] = None
    timestamp: datetime = None

@dataclass
class AssessmentResult:
    """Results of completed assessment"""
    result_id: str
    assessment_id: str
    student_id: str
    total_score: float
    percentage_score: float
    time_taken_minutes: float
    questions_answered: int
    questions_correct: int
    difficulty_analysis: Dict[str, Any]
    topic_breakdown: Dict[str, Any]
    learning_gaps: List[str]
    strengths: List[str]
    recommendations: List[str]
    certification_earned: Optional[str] = None

class AdvancedAssessmentSystem:
    """Comprehensive assessment and testing system with AI-powered evaluation"""
    
    def __init__(self):
        self.assessments_dir = Path("../assessments")
        self.results_dir = Path("../assessment_results")
        self.certifications_dir = Path("../certifications")
        
        # Create directories
        for directory in [self.assessments_dir, self.results_dir, self.certifications_dir]:
            directory.mkdir(exist_ok=True)
        
        # Assessment templates and question banks
        self.question_banks: Dict[str, List[AssessmentQuestion]] = {}
        self.assessment_templates: Dict[str, Dict[str, Any]] = {}
        self.certification_requirements: Dict[str, Dict[str, Any]] = {}
        
        # Active assessments and results
        self.active_assessments: Dict[str, Dict[str, Any]] = {}
        self.assessment_results: Dict[str, AssessmentResult] = {}
        
        # AI engines for intelligent assessment
        self.gemini_client = None
        self.assessment_engine = None  # From Phase 3
        self.adaptive_difficulty_engine = None  # From Phase 3
        
        # Assessment analytics
        self.assessment_analytics = {
            "total_assessments": 0,
            "completion_rates": {},
            "average_scores": {},
            "time_analytics": {},
            "certification_counts": {}
        }
        
        # Initialize system
        self._init_question_banks()
        self._init_assessment_templates()
        self._init_certification_system()
        
        # Load AI engines
        schedule_async_init(self._init_ai_engines())
        
        logger.info("Advanced Assessment System initialized with comprehensive evaluation capabilities")
    
    async def _init_ai_engines(self):
        """Initialize AI engines for intelligent assessment"""
        try:
            from google import genai
            
            api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
            if api_key:
                self.gemini_client = genai.Client(api_key=api_key, http_options={'headers': {'Referer': 'http://localhost'}})
                logger.info("Assessment System: Gemini client initialized")
            
            # Import Phase 3 engines if available
            try:
                from assessment_engine import AssessmentEngine
                from adaptive_difficulty import AdaptiveDifficultyEngine
                
                self.assessment_engine = AssessmentEngine()
                self.adaptive_difficulty_engine = AdaptiveDifficultyEngine()
                logger.info("Phase 3 assessment engines integrated")
            except ImportError:
                logger.info("Phase 3 engines not available - using fallback assessment")
            
        except Exception as e:
            logger.error(f"Error initializing AI engines: {str(e)}")
    
    def _init_question_banks(self):
        """Initialize comprehensive question banks by subject and grade level"""
        
        # Mathematics Question Bank
        math_questions = [
            AssessmentQuestion(
                question_id="math_001",
                question_type=QuestionType.MULTIPLE_CHOICE,
                subject="mathematics",
                topic="algebra",
                difficulty=DifficultyLevel.INTERMEDIATE,
                question_text="Solve for x: 2x + 5 = 17",
                options=["x = 6", "x = 8", "x = 10", "x = 12"],
                correct_answer="x = 6",
                explanation="Subtract 5 from both sides: 2x = 12, then divide by 2: x = 6",
                points=2,
                time_limit_seconds=120
            ),
            AssessmentQuestion(
                question_id="math_002",
                question_type=QuestionType.MATHEMATICAL,
                subject="mathematics", 
                topic="geometry",
                difficulty=DifficultyLevel.INTERMEDIATE,
                question_text="Calculate the area of a triangle with base 8 cm and height 12 cm.",
                correct_answer="48",
                explanation="Area = (1/2) × base × height = (1/2) × 8 × 12 = 48 cm²",
                points=3,
                time_limit_seconds=180
            ),
            AssessmentQuestion(
                question_id="math_003",
                question_type=QuestionType.SHORT_ANSWER,
                subject="mathematics",
                topic="fractions",
                difficulty=DifficultyLevel.ELEMENTARY,
                question_text="Simplify the fraction 12/16 to its lowest terms.",
                correct_answer="3/4",
                explanation="Find GCD of 12 and 16 which is 4, then divide: 12÷4 = 3, 16÷4 = 4",
                points=2,
                time_limit_seconds=90
            )
        ]
        
        # Science Question Bank
        science_questions = [
            AssessmentQuestion(
                question_id="sci_001",
                question_type=QuestionType.MULTIPLE_CHOICE,
                subject="science",
                topic="physics",
                difficulty=DifficultyLevel.ADVANCED,
                question_text="What is the acceleration due to gravity on Earth?",
                options=["8.9 m/s²", "9.8 m/s²", "10.2 m/s²", "11.1 m/s²"],
                correct_answer="9.8 m/s²",
                explanation="Standard gravity on Earth is approximately 9.8 m/s²",
                points=1
            ),
            AssessmentQuestion(
                question_id="sci_002",
                question_type=QuestionType.LONG_ANSWER,
                subject="science",
                topic="biology",
                difficulty=DifficultyLevel.INTERMEDIATE,
                question_text="Explain the process of photosynthesis and its importance to life on Earth.",
                explanation="Photosynthesis converts CO2 + H2O + sunlight → glucose + O2, providing energy for plants and oxygen for other organisms",
                points=5,
                time_limit_seconds=600,
                rubric={
                    "chemical_equation": 2,
                    "process_explanation": 2,
                    "importance_to_life": 1
                }
            )
        ]
        
        # Language Arts Question Bank
        language_questions = [
            AssessmentQuestion(
                question_id="lang_001",
                question_type=QuestionType.MULTIPLE_CHOICE,
                subject="language_arts",
                topic="grammar",
                difficulty=DifficultyLevel.ELEMENTARY,
                question_text="Which sentence uses correct punctuation?",
                options=[
                    "Hello, how are you today.",
                    "Hello how are you today?",
                    "Hello, how are you today?",
                    "Hello how are you today."
                ],
                correct_answer="Hello, how are you today?",
                explanation="Questions require question marks, and greetings need commas",
                points=1
            )
        ]
        
        self.question_banks = {
            "mathematics": math_questions,
            "science": science_questions,
            "language_arts": language_questions
        }
    
    def _init_assessment_templates(self):
        """Initialize assessment templates for different purposes"""
        
        self.assessment_templates = {
            "diagnostic_math_k5": {
                "title": "K-5 Mathematics Diagnostic Assessment",
                "description": "Comprehensive evaluation of elementary math skills",
                "assessment_type": AssessmentType.DIAGNOSTIC,
                "subject": "mathematics",
                "grade_levels": ["K", "1", "2", "3", "4", "5"],
                "duration_minutes": 30,
                "question_count": 15,
                "topics": ["counting", "addition", "subtraction", "multiplication", "fractions"],
                "adaptive": True,
                "certification_available": False
            },
            
            "formative_algebra": {
                "title": "Algebra Progress Check",
                "description": "Ongoing assessment of algebraic understanding",
                "assessment_type": AssessmentType.FORMATIVE,
                "subject": "mathematics",
                "grade_levels": ["8", "9", "10"],
                "duration_minutes": 20,
                "question_count": 10,
                "topics": ["linear_equations", "factoring", "graphing"],
                "adaptive": True,
                "certification_available": False
            },
            
            "summative_high_school_math": {
                "title": "High School Mathematics Final Assessment",
                "description": "Comprehensive final evaluation of high school math",
                "assessment_type": AssessmentType.SUMMATIVE,
                "subject": "mathematics",
                "grade_levels": ["9", "10", "11", "12"],
                "duration_minutes": 90,
                "question_count": 40,
                "topics": ["algebra", "geometry", "trigonometry", "calculus_intro"],
                "adaptive": False,
                "certification_available": True
            },
            
            "adaptive_science_assessment": {
                "title": "Adaptive Science Evaluation",
                "description": "AI-powered adaptive science assessment",
                "assessment_type": AssessmentType.ADAPTIVE,
                "subject": "science",
                "grade_levels": ["6", "7", "8", "9", "10", "11", "12"],
                "duration_minutes": 45,
                "question_count": 25,
                "topics": ["physics", "chemistry", "biology", "earth_science"],
                "adaptive": True,
                "certification_available": True
            }
        }
    
    def _init_certification_system(self):
        """Initialize certification and credentialing system"""
        
        self.certification_requirements = {
            "elementary_math_proficiency": {
                "title": "Elementary Mathematics Proficiency Certificate",
                "description": "Demonstrates mastery of K-5 mathematics concepts",
                "requirements": {
                    "min_score_percentage": 80,
                    "required_topics": ["addition", "subtraction", "multiplication", "division", "fractions"],
                    "assessment_type": AssessmentType.SUMMATIVE,
                    "validity_months": 12
                },
                "badge_image": "/certifications/badges/elementary_math.png",
                "verification_url": "/verify/{certificate_id}"
            },
            
            "high_school_algebra_mastery": {
                "title": "High School Algebra Mastery Certificate",
                "description": "Advanced proficiency in algebraic concepts and problem solving",
                "requirements": {
                    "min_score_percentage": 85,
                    "required_topics": ["linear_equations", "quadratic_equations", "systems", "graphing"],
                    "assessment_type": AssessmentType.CERTIFICATION,
                    "validity_months": 24
                },
                "badge_image": "/certifications/badges/algebra_mastery.png",
                "verification_url": "/verify/{certificate_id}"
            },
            
            "ai_tutoring_specialist": {
                "title": "AI Tutoring Platform Specialist",
                "description": "Professional certification for educators using AI tutoring systems",
                "requirements": {
                    "min_score_percentage": 90,
                    "required_topics": ["ai_tutoring_principles", "adaptive_learning", "assessment_design", "data_interpretation"],
                    "assessment_type": AssessmentType.CERTIFICATION,
                    "validity_months": 36
                },
                "badge_image": "/certifications/badges/ai_specialist.png",
                "verification_url": "/verify/{certificate_id}"
            }
        }
    
    async def create_assessment(self, 
                              template_id: str,
                              student_id: str,
                              customizations: Optional[Dict[str, Any]] = None) -> str:
        """Create a new assessment instance for a student"""
        try:
            if template_id not in self.assessment_templates:
                raise ValueError(f"Assessment template {template_id} not found")
            
            template = self.assessment_templates[template_id].copy()
            
            # Apply customizations
            if customizations:
                template.update(customizations)
            
            # Generate assessment ID
            assessment_id = f"assess_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"
            
            # Get student profile for personalization
            from memory import MemoryManager
            memory_manager = MemoryManager()
            student_profile = await memory_manager.get_student_profile(student_id)
            
            # Select appropriate questions
            if template["adaptive"]:
                questions = await self._generate_adaptive_questions(template, student_profile)
            else:
                questions = await self._select_standard_questions(template, student_profile)
            
            # Create assessment instance
            assessment_instance = {
                "assessment_id": assessment_id,
                "template_id": template_id,
                "student_id": student_id,
                "title": template["title"],
                "description": template["description"],
                "assessment_type": template["assessment_type"],
                "subject": template["subject"],
                "questions": questions,
                "status": AssessmentStatus.NOT_STARTED,
                "created_at": datetime.now(),
                "start_time": None,
                "end_time": None,
                "duration_minutes": template["duration_minutes"],
                "adaptive": template["adaptive"],
                "student_responses": {},
                "current_question": 0,
                "personalization_applied": self._get_personalization_factors(student_profile)
            }
            
            self.active_assessments[assessment_id] = assessment_instance
            
            # Update analytics
            self.assessment_analytics["total_assessments"] += 1
            
            logger.info(f"Created assessment {assessment_id} for student {student_id}")
            
            return assessment_id
            
        except Exception as e:
            logger.error(f"Error creating assessment: {str(e)}")
            raise Exception(f"Assessment creation failed: {str(e)}")
    
    async def _generate_adaptive_questions(self, 
                                         template: Dict[str, Any],
                                         student_profile: StudentProfile) -> List[AssessmentQuestion]:
        """Generate adaptive questions based on student profile and AI analysis"""
        
        subject = template["subject"]
        question_count = template["question_count"]
        topics = template["topics"]
        
        available_questions = self.question_banks.get(subject, [])
        
        if not available_questions:
            return self._generate_fallback_questions(template)
        
        # Filter questions by topics
        relevant_questions = [
            q for q in available_questions 
            if q.topic in topics
        ]
        
        if not relevant_questions:
            relevant_questions = available_questions[:question_count]
        
        # Use AI to optimize question selection
        if self.gemini_client:
            try:
                optimized_questions = await self._ai_optimize_questions(
                    relevant_questions, student_profile, template
                )
                return optimized_questions[:question_count]
            except Exception as e:
                logger.error(f"AI question optimization failed: {e}")
        
        # Fallback to rule-based selection
        return self._rule_based_question_selection(relevant_questions, student_profile, question_count)
    
    async def _ai_optimize_questions(self,
                                   questions: List[AssessmentQuestion],
                                   student_profile: StudentProfile,
                                   template: Dict[str, Any]) -> List[AssessmentQuestion]:
        """Use AI to optimize question selection for individual student"""
        
        # Prepare context for AI
        student_context = {
            "grade_level": student_profile.grade_level.value,
            "learning_style": student_profile.learning_style.value,
            "confusion_patterns": list(student_profile.confusion_patterns.keys())[:3],
            "success_patterns": list(student_profile.success_patterns.keys())[:3]
        }
        
        question_summaries = [
            {
                "id": q.question_id,
                "topic": q.topic,
                "difficulty": q.difficulty.value,
                "type": q.question_type.value,
                "points": q.points
            }
            for q in questions
        ]
        
        optimization_prompt = f"""Optimize assessment question selection for personalized learning:

STUDENT PROFILE:
- Grade Level: {student_context["grade_level"]}
- Learning Style: {student_context["learning_style"]}
- Areas of Confusion: {", ".join(student_context["confusion_patterns"])}
- Areas of Success: {", ".join(student_context["success_patterns"])}

ASSESSMENT GOAL:
- Type: {template["assessment_type"]}
- Subject: {template["subject"]}
- Target Questions: {template["question_count"]}
- Duration: {template["duration_minutes"]} minutes

AVAILABLE QUESTIONS:
{json.dumps(question_summaries, indent=2)}

Select the optimal {template["question_count"]} questions that:
1. Match the student's current ability level
2. Address known confusion areas for growth
3. Build on success patterns for confidence
4. Progress logically in difficulty
5. Fit within the time constraint

Return JSON array of question IDs in recommended order:
{{"selected_questions": ["question_id1", "question_id2", ...]}}"""

        try:
            response = self.gemini_client.models.generate_content(
                model="gemini-2.5-flash",
                contents=optimization_prompt
            )
            
            response_text = response.text
            
            # Parse AI response
            if response_text.strip().startswith('{'):
                selection_data = json.loads(response_text)
            else:
                import re
                json_match = re.search(r'```json\s*(\{.*?\})\s*```', response_text, re.DOTALL)
                if json_match:
                    selection_data = json.loads(json_match.group(1))
                else:
                    raise ValueError("Could not parse AI response")
            
            selected_ids = selection_data.get("selected_questions", [])
            
            # Return questions in AI-recommended order
            questions_dict = {q.question_id: q for q in questions}
            optimized_questions = []
            
            for question_id in selected_ids:
                if question_id in questions_dict:
                    optimized_questions.append(questions_dict[question_id])
            
            # Fill remaining slots if needed
            used_ids = set(selected_ids)
            remaining_questions = [q for q in questions if q.question_id not in used_ids]
            while len(optimized_questions) < template["question_count"] and remaining_questions:
                optimized_questions.append(remaining_questions.pop(0))
            
            return optimized_questions
            
        except Exception as e:
            logger.error(f"Error in AI question optimization: {e}")
            return self._rule_based_question_selection(questions, student_profile, template["question_count"])
    
    def _rule_based_question_selection(self, 
                                     questions: List[AssessmentQuestion],
                                     student_profile: StudentProfile,
                                     target_count: int) -> List[AssessmentQuestion]:
        """Rule-based question selection as fallback"""
        
        # Sort questions by relevance to student
        def relevance_score(question: AssessmentQuestion) -> float:
            score = 0.0
            
            # Boost questions in confusion areas
            if question.topic in student_profile.confusion_patterns:
                score += 0.3
            
            # Boost questions in success areas for confidence
            if question.topic in student_profile.success_patterns:
                score += 0.2
            
            # Prefer intermediate difficulty
            if question.difficulty == DifficultyLevel.INTERMEDIATE:
                score += 0.1
            
            # Prefer multiple choice for quick assessment
            if question.question_type == QuestionType.MULTIPLE_CHOICE:
                score += 0.05
            
            return score
        
        sorted_questions = sorted(questions, key=relevance_score, reverse=True)
        return sorted_questions[:target_count]
    
    def _generate_fallback_questions(self, template: Dict[str, Any]) -> List[AssessmentQuestion]:
        """Generate fallback questions when question bank is empty"""
        
        fallback_questions = []
        subject = template["subject"]
        topics = template.get("topics", ["general"])
        
        for i in range(min(template["question_count"], 5)):
            question = AssessmentQuestion(
                question_id=f"fallback_{subject}_{i+1}",
                question_type=QuestionType.MULTIPLE_CHOICE,
                subject=subject,
                topic=topics[i % len(topics)],
                difficulty=DifficultyLevel.INTERMEDIATE,
                question_text=f"Sample {subject} question {i+1} for topic: {topics[i % len(topics)]}",
                options=["Option A", "Option B", "Option C", "Option D"],
                correct_answer="Option A",
                explanation="This is a sample question for demonstration purposes.",
                points=1
            )
            fallback_questions.append(question)
        
        return fallback_questions
    
    async def _select_standard_questions(self, 
                                       template: Dict[str, Any],
                                       student_profile: StudentProfile) -> List[AssessmentQuestion]:
        """Select questions for non-adaptive assessments"""
        
        subject = template["subject"]
        question_count = template["question_count"]
        topics = template["topics"]
        
        available_questions = self.question_banks.get(subject, [])
        
        if not available_questions:
            return self._generate_fallback_questions(template)
        
        # Filter by topics and distribute evenly
        topic_questions = {}
        for topic in topics:
            topic_questions[topic] = [
                q for q in available_questions 
                if q.topic == topic
            ]
        
        selected_questions = []
        questions_per_topic = question_count // len(topics)
        
        for topic, questions in topic_questions.items():
            if questions:
                selected_questions.extend(questions[:questions_per_topic])
        
        # Fill remaining slots
        while len(selected_questions) < question_count and available_questions:
            for question in available_questions:
                if question not in selected_questions:
                    selected_questions.append(question)
                    if len(selected_questions) >= question_count:
                        break
        
        return selected_questions[:question_count]
    
    def _get_personalization_factors(self, student_profile: StudentProfile) -> List[str]:
        """Get list of personalization factors applied to assessment"""
        
        factors = [f"Grade level: {student_profile.grade_level.value}"]
        factors.append(f"Learning style: {student_profile.learning_style.value}")
        
        if student_profile.confusion_patterns:
            factors.append(f"Addresses confusion in: {', '.join(list(student_profile.confusion_patterns.keys())[:2])}")
        
        if student_profile.success_patterns:
            factors.append(f"Builds on success in: {', '.join(list(student_profile.success_patterns.keys())[:2])}")
        
        return factors
    
    async def start_assessment(self, assessment_id: str) -> Dict[str, Any]:
        """Start an assessment session"""
        
        if assessment_id not in self.active_assessments:
            raise ValueError("Assessment not found")
        
        assessment = self.active_assessments[assessment_id]
        
        if assessment["status"] != AssessmentStatus.NOT_STARTED:
            raise ValueError(f"Assessment already {assessment['status'].value}")
        
        # Start the assessment
        assessment["status"] = AssessmentStatus.IN_PROGRESS
        assessment["start_time"] = datetime.now()
        
        # Return first question
        first_question = assessment["questions"][0] if assessment["questions"] else None
        
        return {
            "assessment_id": assessment_id,
            "status": "started",
            "title": assessment["title"],
            "description": assessment["description"],
            "total_questions": len(assessment["questions"]),
            "duration_minutes": assessment["duration_minutes"],
            "adaptive": assessment["adaptive"],
            "current_question": self._format_question_for_display(first_question) if first_question else None,
            "progress": {
                "current": 1,
                "total": len(assessment["questions"]),
                "percentage": 0
            }
        }
    
    def _format_question_for_display(self, question: AssessmentQuestion) -> Dict[str, Any]:
        """Format question for student display (hide correct answers)"""
        
        return {
            "question_id": question.question_id,
            "question_type": question.question_type.value,
            "question_text": question.question_text,
            "options": question.options,
            "points": question.points,
            "time_limit_seconds": question.time_limit_seconds,
            "media_attachments": question.media_attachments,
            "topic": question.topic,
            "difficulty": question.difficulty.value
        }
    
    async def submit_response(self, 
                            assessment_id: str,
                            question_id: str,
                            response_data: Dict[str, Any]) -> Dict[str, Any]:
        """Submit student response to assessment question"""
        
        if assessment_id not in self.active_assessments:
            raise ValueError("Assessment not found")
        
        assessment = self.active_assessments[assessment_id]
        
        if assessment["status"] != AssessmentStatus.IN_PROGRESS:
            raise ValueError("Assessment not in progress")
        
        # Create student response
        response = StudentResponse(
            response_id=f"resp_{datetime.now().strftime('%Y%m%d%H%M%S')}_{uuid.uuid4().hex[:6]}",
            question_id=question_id,
            student_id=assessment["student_id"],
            response_text=response_data.get("response_text"),
            selected_options=response_data.get("selected_options"),
            response_time_seconds=response_data.get("response_time_seconds", 0),
            confidence_level=response_data.get("confidence_level"),
            work_shown=response_data.get("work_shown"),
            media_response=response_data.get("media_response"),
            timestamp=datetime.now()
        )
        
        # Store response
        assessment["student_responses"][question_id] = response
        
        # Evaluate response
        question = next(
            (q for q in assessment["questions"] if q.question_id == question_id),
            None
        )
        
        if question:
            evaluation = await self._evaluate_response(response, question)
        else:
            evaluation = {"correct": False, "score": 0, "feedback": "Question not found"}
        
        # Update progress
        assessment["current_question"] += 1
        
        # Determine next question or completion
        if assessment["current_question"] >= len(assessment["questions"]):
            # Assessment completed
            return await self._complete_assessment(assessment_id)
        else:
            # Get next question
            if assessment["adaptive"]:
                next_question = await self._get_adaptive_next_question(assessment, evaluation)
            else:
                next_question = assessment["questions"][assessment["current_question"]]
            
            return {
                "status": "question_submitted",
                "evaluation": evaluation,
                "next_question": self._format_question_for_display(next_question),
                "progress": {
                    "current": assessment["current_question"] + 1,
                    "total": len(assessment["questions"]),
                    "percentage": ((assessment["current_question"] + 1) / len(assessment["questions"])) * 100
                }
            }
    
    async def _evaluate_response(self, 
                               response: StudentResponse,
                               question: AssessmentQuestion) -> Dict[str, Any]:
        """Evaluate student response using AI and rule-based methods"""
        
        # Basic correctness check
        is_correct = False
        score = 0
        
        if question.question_type == QuestionType.MULTIPLE_CHOICE:
            if response.selected_options and question.correct_answer:
                is_correct = response.selected_options[0] == question.correct_answer
                score = question.points if is_correct else 0
        
        elif question.question_type == QuestionType.SHORT_ANSWER:
            if response.response_text and question.correct_answer:
                # Normalize answers for comparison
                student_answer = response.response_text.strip().lower()
                correct_answer = question.correct_answer.strip().lower()
                is_correct = student_answer == correct_answer
                score = question.points if is_correct else 0
        
        elif question.question_type == QuestionType.MATHEMATICAL:
            if response.response_text and question.correct_answer:
                # Use AI for mathematical answer evaluation
                if self.gemini_client:
                    try:
                        ai_evaluation = await self._ai_evaluate_math_response(
                            question, response.response_text
                        )
                        is_correct = ai_evaluation["correct"]
                        score = ai_evaluation["score"]
                    except Exception:
                        # Fallback to string comparison
                        is_correct = response.response_text.strip() == question.correct_answer.strip()
                        score = question.points if is_correct else 0
        
        # Generate feedback
        feedback = self._generate_response_feedback(question, response, is_correct, score)
        
        return {
            "correct": is_correct,
            "score": score,
            "max_score": question.points,
            "feedback": feedback,
            "explanation": question.explanation if not is_correct else None,
            "response_time": response.response_time_seconds
        }
    
    async def _ai_evaluate_math_response(self, 
                                       question: AssessmentQuestion,
                                       student_response: str) -> Dict[str, Any]:
        """Use AI to evaluate mathematical responses"""
        
        evaluation_prompt = f"""Evaluate this mathematical response:

QUESTION: {question.question_text}
CORRECT ANSWER: {question.correct_answer}
STUDENT RESPONSE: {student_response}

Determine if the student's response is mathematically equivalent to the correct answer.
Consider different valid forms (e.g., 0.5 = 1/2, 6 = 6.0).

Return JSON:
{{
  "correct": true/false,
  "score": number (0 to {question.points}),
  "reasoning": "explanation of evaluation"
}}"""

        try:
            response = self.gemini_client.models.generate_content(
                model="gemini-2.5-flash",
                contents=evaluation_prompt
            )
            
            response_text = response.text
            
            # Parse AI response
            if response_text.strip().startswith('{'):
                evaluation = json.loads(response_text)
            else:
                import re
                json_match = re.search(r'```json\s*(\{.*?\})\s*```', response_text, re.DOTALL)
                if json_match:
                    evaluation = json.loads(json_match.group(1))
                else:
                    raise ValueError("Could not parse AI evaluation")
            
            return evaluation
            
        except Exception as e:
            logger.error(f"AI math evaluation failed: {e}")
            return {
                "correct": False,
                "score": 0,
                "reasoning": "Could not evaluate response"
            }
    
    def _generate_response_feedback(self, 
                                  question: AssessmentQuestion,
                                  response: StudentResponse,
                                  is_correct: bool,
                                  score: int) -> str:
        """Generate personalized feedback for student response"""
        
        if is_correct:
            positive_feedback = [
                "Excellent work!",
                "Perfect! You've got it!",
                "Great job!",
                "Correct! Well done!",
                "Outstanding!"
            ]
            import random
            return random.choice(positive_feedback)
        else:
            # Provide constructive feedback
            if question.question_type == QuestionType.MULTIPLE_CHOICE:
                return f"Not quite right. The correct answer is {question.correct_answer}. {question.explanation}"
            elif question.question_type == QuestionType.MATHEMATICAL:
                return f"Let me help you with this. {question.explanation}"
            else:
                return f"Good attempt! {question.explanation}"
    
    async def _get_adaptive_next_question(self, 
                                        assessment: Dict[str, Any],
                                        last_evaluation: Dict[str, Any]) -> AssessmentQuestion:
        """Get next question for adaptive assessment based on performance"""
        
        # Simple adaptive logic - can be enhanced with Phase 3 engines
        current_performance = self._calculate_current_performance(assessment)
        
        remaining_questions = assessment["questions"][assessment["current_question"]:]
        
        if not remaining_questions:
            return None
        
        # Adjust difficulty based on performance
        if current_performance > 0.8:  # High performance - increase difficulty
            harder_questions = [
                q for q in remaining_questions 
                if q.difficulty in [DifficultyLevel.ADVANCED, DifficultyLevel.EXPERT]
            ]
            if harder_questions:
                return harder_questions[0]
        
        elif current_performance < 0.5:  # Low performance - decrease difficulty
            easier_questions = [
                q for q in remaining_questions
                if q.difficulty in [DifficultyLevel.BEGINNER, DifficultyLevel.ELEMENTARY]
            ]
            if easier_questions:
                return easier_questions[0]
        
        # Default to next question
        return remaining_questions[0]
    
    def _calculate_current_performance(self, assessment: Dict[str, Any]) -> float:
        """Calculate current performance score for adaptive adjustments"""
        
        if not assessment["student_responses"]:
            return 0.5  # Neutral starting point
        
        total_score = 0
        max_possible = 0
        
        for question_id, response in assessment["student_responses"].items():
            # This would need to access stored evaluation results
            # For now, simulate based on response quality
            question = next(
                (q for q in assessment["questions"] if q.question_id == question_id),
                None
            )
            if question:
                max_possible += question.points
                # Simulate score based on response presence
                if hasattr(response, 'response_text') and response.response_text:
                    total_score += question.points * 0.7  # Rough estimation
        
        return total_score / max_possible if max_possible > 0 else 0.5
    
    async def _complete_assessment(self, assessment_id: str) -> Dict[str, Any]:
        """Complete assessment and generate comprehensive results"""
        
        assessment = self.active_assessments[assessment_id]
        assessment["status"] = AssessmentStatus.COMPLETED
        assessment["end_time"] = datetime.now()
        
        # Calculate results
        results = await self._calculate_comprehensive_results(assessment)
        
        # Store results
        self.assessment_results[assessment_id] = results
        
        # Check for certification eligibility
        certification = await self._check_certification_eligibility(assessment, results)
        
        # Update analytics
        self._update_assessment_analytics(assessment, results)
        
        return {
            "status": "completed",
            "assessment_id": assessment_id,
            "results": {
                "total_score": results.total_score,
                "percentage_score": results.percentage_score,
                "questions_correct": results.questions_correct,
                "questions_total": len(assessment["questions"]),
                "time_taken_minutes": results.time_taken_minutes,
                "difficulty_analysis": results.difficulty_analysis,
                "topic_breakdown": results.topic_breakdown,
                "learning_gaps": results.learning_gaps,
                "strengths": results.strengths,
                "recommendations": results.recommendations
            },
            "certification": certification,
            "next_steps": self._generate_next_steps(results)
        }
    
    async def _calculate_comprehensive_results(self, assessment: Dict[str, Any]) -> AssessmentResult:
        """Calculate comprehensive assessment results with analytics"""
        
        total_score = 0
        max_possible_score = 0
        questions_correct = 0
        topic_scores = {}
        difficulty_scores = {}
        
        # Process each response
        for question in assessment["questions"]:
            max_possible_score += question.points
            
            # Initialize topic and difficulty tracking
            if question.topic not in topic_scores:
                topic_scores[question.topic] = {"correct": 0, "total": 0, "score": 0, "max_score": 0}
            if question.difficulty.value not in difficulty_scores:
                difficulty_scores[question.difficulty.value] = {"correct": 0, "total": 0, "score": 0, "max_score": 0}
            
            topic_scores[question.topic]["total"] += 1
            topic_scores[question.topic]["max_score"] += question.points
            difficulty_scores[question.difficulty.value]["total"] += 1
            difficulty_scores[question.difficulty.value]["max_score"] += question.points
            
            # Check if question was answered correctly
            response = assessment["student_responses"].get(question.question_id)
            if response:
                # Re-evaluate for final scoring
                evaluation = await self._evaluate_response(response, question)
                
                total_score += evaluation["score"]
                
                if evaluation["correct"]:
                    questions_correct += 1
                    topic_scores[question.topic]["correct"] += 1
                    difficulty_scores[question.difficulty.value]["correct"] += 1
                
                topic_scores[question.topic]["score"] += evaluation["score"]
                difficulty_scores[question.difficulty.value]["score"] += evaluation["score"]
        
        # Calculate percentages and analytics
        percentage_score = (total_score / max_possible_score * 100) if max_possible_score > 0 else 0
        
        # Time analysis
        time_taken = (assessment["end_time"] - assessment["start_time"]).total_seconds() / 60
        
        # Generate learning insights
        learning_gaps = []
        strengths = []
        
        for topic, scores in topic_scores.items():
            accuracy = scores["correct"] / scores["total"] if scores["total"] > 0 else 0
            if accuracy < 0.6:
                learning_gaps.append(topic)
            elif accuracy > 0.8:
                strengths.append(topic)
        
        # Generate recommendations
        recommendations = self._generate_learning_recommendations(
            topic_scores, difficulty_scores, percentage_score
        )
        
        # Create result object
        result = AssessmentResult(
            result_id=f"result_{assessment['assessment_id']}",
            assessment_id=assessment["assessment_id"],
            student_id=assessment["student_id"],
            total_score=total_score,
            percentage_score=percentage_score,
            time_taken_minutes=time_taken,
            questions_answered=len(assessment["student_responses"]),
            questions_correct=questions_correct,
            difficulty_analysis=difficulty_scores,
            topic_breakdown=topic_scores,
            learning_gaps=learning_gaps,
            strengths=strengths,
            recommendations=recommendations
        )
        
        return result
    
    def _generate_learning_recommendations(self, 
                                        topic_scores: Dict[str, Any],
                                        difficulty_scores: Dict[str, Any],
                                        percentage_score: float) -> List[str]:
        """Generate personalized learning recommendations"""
        
        recommendations = []
        
        # Topic-based recommendations
        for topic, scores in topic_scores.items():
            accuracy = scores["correct"] / scores["total"] if scores["total"] > 0 else 0
            if accuracy < 0.5:
                recommendations.append(f"Focus on {topic} - review foundational concepts")
            elif accuracy < 0.7:
                recommendations.append(f"Practice more {topic} problems to build confidence")
        
        # Difficulty-based recommendations
        for difficulty, scores in difficulty_scores.items():
            accuracy = scores["correct"] / scores["total"] if scores["total"] > 0 else 0
            if difficulty == "advanced" and accuracy > 0.8:
                recommendations.append("Excellent work on advanced problems - ready for expert level")
            elif difficulty == "beginner" and accuracy < 0.6:
                recommendations.append("Strengthen fundamental skills with additional practice")
        
        # Overall performance recommendations
        if percentage_score >= 90:
            recommendations.append("Outstanding performance! Consider advanced coursework")
        elif percentage_score >= 75:
            recommendations.append("Good work! Focus on identified gaps for mastery")
        elif percentage_score >= 60:
            recommendations.append("Solid foundation. Additional practice in weak areas recommended")
        else:
            recommendations.append("Consider reviewing core concepts with additional support")
        
        return recommendations[:5]  # Limit to top 5 recommendations
    
    async def _check_certification_eligibility(self, 
                                             assessment: Dict[str, Any],
                                             results: AssessmentResult) -> Optional[Dict[str, Any]]:
        """Check if student qualifies for any certifications"""
        
        # Check each certification requirement
        for cert_id, cert_config in self.certification_requirements.items():
            requirements = cert_config["requirements"]
            
            # Check score requirement
            if results.percentage_score < requirements["min_score_percentage"]:
                continue
            
            # Check assessment type
            if assessment["assessment_type"] != requirements.get("assessment_type"):
                continue
            
            # Check topic coverage
            required_topics = set(requirements.get("required_topics", []))
            covered_topics = set(results.topic_breakdown.keys())
            
            if not required_topics.issubset(covered_topics):
                continue
            
            # Student qualifies - generate certificate
            certificate = await self._generate_certificate(cert_id, cert_config, assessment, results)
            return certificate
        
        return None
    
    async def _generate_certificate(self, 
                                  cert_id: str,
                                  cert_config: Dict[str, Any],
                                  assessment: Dict[str, Any],
                                  results: AssessmentResult) -> Dict[str, Any]:
        """Generate official certificate for qualified student"""
        
        certificate_id = f"cert_{datetime.now().strftime('%Y%m%d')}_{uuid.uuid4().hex[:12]}"
        issue_date = datetime.now()
        expiry_date = issue_date + timedelta(days=cert_config["requirements"]["validity_months"] * 30)
        
        certificate = {
            "certificate_id": certificate_id,
            "certification_type": cert_id,
            "title": cert_config["title"],
            "description": cert_config["description"],
            "student_id": assessment["student_id"],
            "assessment_id": assessment["assessment_id"],
            "issue_date": issue_date.isoformat(),
            "expiry_date": expiry_date.isoformat(),
            "score_achieved": results.percentage_score,
            "badge_image": cert_config["badge_image"],
            "verification_url": cert_config["verification_url"].replace("{certificate_id}", certificate_id),
            "digital_signature": self._generate_digital_signature(certificate_id, assessment["student_id"])
        }
        
        # Save certificate
        cert_file = self.certifications_dir / f"{certificate_id}.json"
        with open(cert_file, 'w') as f:
            json.dump(certificate, f, indent=2)
        
        # Update analytics
        if cert_id not in self.assessment_analytics["certification_counts"]:
            self.assessment_analytics["certification_counts"][cert_id] = 0
        self.assessment_analytics["certification_counts"][cert_id] += 1
        
        logger.info(f"Certificate generated: {certificate_id} for student {assessment['student_id']}")
        
        return certificate
    
    def _generate_digital_signature(self, certificate_id: str, student_id: str) -> str:
        """Generate digital signature for certificate verification"""
        
        import hashlib
        signature_data = f"{certificate_id}:{student_id}:{datetime.now().date().isoformat()}"
        return hashlib.sha256(signature_data.encode()).hexdigest()[:16]
    
    def _generate_next_steps(self, results: AssessmentResult) -> List[str]:
        """Generate personalized next steps based on assessment results"""
        
        next_steps = []
        
        if results.percentage_score >= 85:
            next_steps.extend([
                "Explore advanced topics in your strong areas",
                "Consider taking a certification assessment",
                "Help peers with concepts you've mastered"
            ])
        elif results.percentage_score >= 70:
            next_steps.extend([
                "Review topics with lower scores",
                "Practice similar problems for reinforcement",
                "Seek additional explanations for challenging concepts"
            ])
        else:
            next_steps.extend([
                "Focus on fundamental concepts first",
                "Consider additional tutoring or support",
                "Practice basic problems before advancing"
            ])
        
        # Add specific topic recommendations
        if results.learning_gaps:
            next_steps.append(f"Priority focus: {', '.join(results.learning_gaps[:2])}")
        
        return next_steps[:4]  # Limit to 4 next steps
    
    def _update_assessment_analytics(self, assessment: Dict[str, Any], results: AssessmentResult):
        """Update assessment analytics with new results"""
        
        template_id = assessment["template_id"]
        
        # Update completion rates
        if template_id not in self.assessment_analytics["completion_rates"]:
            self.assessment_analytics["completion_rates"][template_id] = []
        
        completion_rate = results.questions_answered / len(assessment["questions"])
        self.assessment_analytics["completion_rates"][template_id].append(completion_rate)
        
        # Update average scores
        if template_id not in self.assessment_analytics["average_scores"]:
            self.assessment_analytics["average_scores"][template_id] = []
        
        self.assessment_analytics["average_scores"][template_id].append(results.percentage_score)
        
        # Update time analytics
        if template_id not in self.assessment_analytics["time_analytics"]:
            self.assessment_analytics["time_analytics"][template_id] = []
        
        self.assessment_analytics["time_analytics"][template_id].append(results.time_taken_minutes)
    
    async def get_assessment_results(self, assessment_id: str) -> Optional[Dict[str, Any]]:
        """Get comprehensive results for completed assessment"""
        
        if assessment_id not in self.assessment_results:
            return None
        
        results = self.assessment_results[assessment_id]
        
        return {
            "assessment_id": assessment_id,
            "student_id": results.student_id,
            "completion_status": "completed",
            "score_summary": {
                "total_score": results.total_score,
                "percentage": results.percentage_score,
                "questions_correct": results.questions_correct,
                "time_taken_minutes": results.time_taken_minutes
            },
            "detailed_analysis": {
                "topic_breakdown": results.topic_breakdown,
                "difficulty_analysis": results.difficulty_analysis,
                "learning_gaps": results.learning_gaps,
                "strengths": results.strengths
            },
            "recommendations": results.recommendations,
            "certification": results.certification_earned
        }
    
    async def get_student_assessment_history(self, student_id: str) -> Dict[str, Any]:
        """Get comprehensive assessment history for a student"""
        
        student_results = [
            result for result in self.assessment_results.values()
            if result.student_id == student_id
        ]
        
        if not student_results:
            return {
                "student_id": student_id,
                "assessment_count": 0,
                "message": "No assessment history found"
            }
        
        # Calculate aggregate statistics
        avg_score = statistics.mean([r.percentage_score for r in student_results])
        total_time = sum([r.time_taken_minutes for r in student_results])
        
        # Identify learning trends
        scores_over_time = [(r.assessment_id, r.percentage_score) for r in student_results]
        
        return {
            "student_id": student_id,
            "assessment_count": len(student_results),
            "performance_summary": {
                "average_score": avg_score,
                "highest_score": max([r.percentage_score for r in student_results]),
                "total_time_minutes": total_time,
                "assessments_completed": len(student_results)
            },
            "learning_trends": {
                "scores_over_time": scores_over_time,
                "improvement_rate": self._calculate_improvement_rate(scores_over_time),
                "consistent_strengths": self._identify_consistent_patterns(student_results, "strengths"),
                "persistent_gaps": self._identify_consistent_patterns(student_results, "learning_gaps")
            },
            "certifications_earned": [
                r.certification_earned for r in student_results
                if r.certification_earned
            ],
            "recommendations": self._generate_aggregate_recommendations(student_results)
        }
    
    def _calculate_improvement_rate(self, scores_over_time: List[Tuple[str, float]]) -> str:
        """Calculate learning improvement rate"""
        
        if len(scores_over_time) < 2:
            return "insufficient_data"
        
        first_half = scores_over_time[:len(scores_over_time)//2]
        second_half = scores_over_time[len(scores_over_time)//2:]
        
        avg_first = statistics.mean([score for _, score in first_half])
        avg_second = statistics.mean([score for _, score in second_half])
        
        improvement = avg_second - avg_first
        
        if improvement > 10:
            return "strong_improvement"
        elif improvement > 5:
            return "moderate_improvement"
        elif improvement > -5:
            return "stable_performance"
        else:
            return "declining_performance"
    
    def _identify_consistent_patterns(self, results: List[AssessmentResult], pattern_type: str) -> List[str]:
        """Identify consistent patterns across multiple assessments"""
        
        pattern_counts = {}
        
        for result in results:
            patterns = getattr(result, pattern_type, [])
            for pattern in patterns:
                if pattern not in pattern_counts:
                    pattern_counts[pattern] = 0
                pattern_counts[pattern] += 1
        
        # Return patterns that appear in at least 50% of assessments
        threshold = len(results) * 0.5
        consistent_patterns = [
            pattern for pattern, count in pattern_counts.items()
            if count >= threshold
        ]
        
        return consistent_patterns
    
    def _generate_aggregate_recommendations(self, results: List[AssessmentResult]) -> List[str]:
        """Generate recommendations based on aggregate assessment history"""
        
        if not results:
            return []
        
        avg_score = statistics.mean([r.percentage_score for r in results])
        recent_results = results[-3:]  # Last 3 assessments
        
        recommendations = []
        
        # Overall performance recommendations
        if avg_score >= 85:
            recommendations.append("Consistently excellent performance - consider advanced coursework")
        elif avg_score >= 70:
            recommendations.append("Good overall performance with room for targeted improvement")
        else:
            recommendations.append("Focus on fundamental skills development")
        
        # Trend-based recommendations
        if len(recent_results) >= 2:
            recent_trend = recent_results[-1].percentage_score - recent_results[-2].percentage_score
            if recent_trend > 10:
                recommendations.append("Great improvement trend - keep up the excellent work!")
            elif recent_trend < -10:
                recommendations.append("Recent decline noted - consider additional support")
        
        # Pattern-based recommendations
        consistent_gaps = self._identify_consistent_patterns(results, "learning_gaps")
        if consistent_gaps:
            recommendations.append(f"Persistent focus needed on: {', '.join(consistent_gaps[:2])}")
        
        return recommendations[:4]
    
    async def get_assessment_analytics(self) -> Dict[str, Any]:
        """Get comprehensive assessment system analytics"""
        
        return {
            "system_statistics": self.assessment_analytics,
            "template_performance": {
                template_id: {
                    "average_completion_rate": statistics.mean(completions) if completions else 0,
                    "average_score": statistics.mean(self.assessment_analytics["average_scores"].get(template_id, [0])),
                    "average_time_minutes": statistics.mean(self.assessment_analytics["time_analytics"].get(template_id, [0]))
                }
                for template_id, completions in self.assessment_analytics["completion_rates"].items()
            },
            "certification_summary": self.assessment_analytics["certification_counts"],
            "active_assessments": len(self.active_assessments),
            "system_health": {
                "question_banks_loaded": len(self.question_banks),
                "templates_available": len(self.assessment_templates),
                "certifications_available": len(self.certification_requirements),
                "ai_integration": self.gemini_client is not None
            }
        }
    
    def is_healthy(self) -> bool:
        """Check if assessment system is healthy"""
        return (
            len(self.question_banks) > 0 and
            len(self.assessment_templates) > 0 and
            len(self.certification_requirements) > 0 and
            len(self.active_assessments) < 1000  # Reasonable limit
        )
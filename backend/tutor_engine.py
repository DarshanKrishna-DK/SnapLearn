"""
Tutor Engine for SnapLearn AI
Handles AI tutoring logic using the Google Gemini API only
"""

import os
import logging
import json
from typing import Dict, List, Any, Optional
from datetime import datetime

from models import (
    ExplanationResponse, 
    AssessmentResponse, 
    StudentProfile, 
    BoardScript, 
    BoardStep
)

from utils import schedule_async_init
from llm_service import get_llm_service

logger = logging.getLogger(__name__)

class TutorEngine:
    """Handles AI tutoring logic with Gemini API (see llm_service)"""
    
    def __init__(self):
        self.llm = get_llm_service()
        self.prompts_dir = "../prompts"
        
        # Load prompt templates
        self._load_prompts()
        
        logger.info("TutorEngine initialized with LLM service (Gemini API)")
    
    def _load_prompts(self):
        """Load prompt templates from files"""
        try:
            os.makedirs(self.prompts_dir, exist_ok=True)
            
            # Create default prompts if they don't exist
            self._create_default_prompts()
            
            # Load prompts
            self.prompts = {}
            
            prompt_files = {
                "explain": "explain.txt",
                "assess": "assess.txt",
                "confusion_detection": "confusion_detection.txt",
                "style_adaptation": "style_adaptation.txt"
            }
            
            for prompt_name, filename in prompt_files.items():
                prompt_path = os.path.join(self.prompts_dir, filename)
                if os.path.exists(prompt_path):
                    with open(prompt_path, 'r', encoding='utf-8') as f:
                        self.prompts[prompt_name] = f.read()
                else:
                    logger.warning(f"Prompt file not found: {filename}")
                    self.prompts[prompt_name] = self._get_default_prompt(prompt_name)
            
            logger.info("Prompt templates loaded successfully")
            
        except Exception as e:
            logger.error(f"Error loading prompts: {str(e)}")
            self._create_fallback_prompts()
    
    def _create_default_prompts(self):
        """Create default prompt templates"""
        prompts = {
            "explain.txt": """You are an expert AI tutor providing personalized explanations. 

STUDENT CONTEXT:
- Student ID: {student_id}
- Grade Level: {grade_level}
- Language: {language}
- Learning Style: {learning_style}
- Previous Confusion Areas: {confusion_patterns}
- Success Areas: {success_patterns}
- Explanation Style Preference: {explanation_style}

QUESTION: {question}

Your task is to provide a clear, grade-appropriate explanation with visual diagrams and create an animated blackboard script.

RESPONSE FORMAT (JSON):
{{
  "explanation_text": "Main explanation in natural language",
  "mermaid_diagrams": [
    {{
      "title": "Diagram title",
      "description": "What this diagram shows",
      "mermaid_code": "graph TD\\n    A[Start] --> B[Process]\\n    B --> C[End]",
      "diagram_type": "flowchart|sequence|mindmap|timeline|class|state"
    }}
  ],
  "board_script": {{
    "steps": [
      {{
        "step": 1,
        "content": "Content to display",
        "type": "title|body|equation|highlight|diagram|mermaid",
        "mermaid_code": "Optional Mermaid diagram code for this step",
        "draw_duration_ms": 1000
      }}
    ],
    "total_duration_ms": 8000,
    "background_color": "#000000",
    "text_color": "#FFFFFF"
  }},
  "difficulty_level": "easy|medium|hard",
  "key_concepts": ["concept1", "concept2"],
  "follow_up_questions": ["question1", "question2"],
  "confidence_score": 0.95
}}

PRODUCTION-GRADE GUIDELINES:
1. Match the student's grade level and learning style precisely
2. Use simple language for lower grades, more complex for higher grades
3. Create board_script with 6-10 comprehensive animation steps
4. Include worked examples and step-by-step breakdowns
5. Generate relevant Mermaid diagrams for visual learners:
   - Flowcharts for processes and procedures
   - Mind maps for concept relationships  
   - Sequence diagrams for step-by-step processes
   - Class diagrams for categorization
   - State diagrams for changes over time
6. Adapt to previous confusion/success patterns
7. Use the student's preferred language
8. Make animations engaging with appropriate timing (longer for complex concepts)
9. Ensure diagrams are age-appropriate and support the explanation
10. Use proper Mermaid syntax and clear, readable diagram structures

Generate your response:""",

            "assess.txt": """You are an expert AI tutor assessing student answers.

STUDENT CONTEXT:
- Student ID: {student_id}
- Grade Level: {grade_level}
- Learning Profile: {learning_profile}

QUESTION: {question}
STUDENT ANSWER: {student_answer}
EXPECTED ANSWER: {expected_answer}

Your task is to assess the student's answer and provide constructive feedback.

RESPONSE FORMAT (JSON):
{{
  "is_correct": true/false,
  "confidence_score": 0.95,
  "feedback": "Detailed feedback for the student",
  "mistakes_identified": ["mistake1", "mistake2"],
  "suggestions": ["suggestion1", "suggestion2"],
  "next_explanation_style": "visual|verbal|worked_example|conceptual"
}}

ASSESSMENT GUIDELINES:
1. Look for partial understanding, not just correct/incorrect
2. Identify specific misconceptions
3. Provide encouraging, constructive feedback
4. Suggest specific areas for improvement
5. Recommend the best explanation style for re-teaching
6. Consider grade-appropriate expectations

Generate your assessment:""",

            "confusion_detection.txt": """You are an AI tutor detecting student confusion patterns.

STUDENT INTERACTION HISTORY:
{interaction_history}

CURRENT QUESTION: {question}
STUDENT RESPONSE: {student_response}

Analyze the student's response for signs of confusion and recommend the best teaching approach.

RESPONSE FORMAT (JSON):
{{
  "confusion_detected": true/false,
  "confusion_level": "low|medium|high",
  "confusion_areas": ["area1", "area2"],
  "recommended_approach": "slow_down|visual_aids|worked_examples|different_method",
  "explanation_style": "visual|auditory|kinesthetic|reading_writing"
}}

Generate your analysis:""",

            "style_adaptation.txt": """You are an AI tutor adapting explanation styles based on student needs.

STUDENT PROFILE:
- Grade Level: {grade_level}
- Learning Style: {learning_style}
- Recent Performance: {recent_performance}
- Confusion Areas: {confusion_areas}

TOPIC: {topic}
REQUESTED STYLE: {requested_style}

Create a personalized explanation using the requested style.

RESPONSE FORMAT (JSON):
{{
  "adapted_explanation": "Explanation using the requested style",
  "board_script": {{
    "steps": [...],
    "total_duration_ms": 5000
  }},
  "style_rationale": "Why this style works for this student"
}}

Generate your adapted explanation:"""
        }
        
        for filename, content in prompts.items():
            filepath = os.path.join(self.prompts_dir, filename)
            if not os.path.exists(filepath):
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(content)
    
    def _get_default_prompt(self, prompt_name: str) -> str:
        """Get fallback prompt if file not found"""
        defaults = {
            "explain": "Explain this topic clearly for a {grade_level} student: {question}",
            "assess": "Assess this answer: {student_answer} for question: {question}",
            "confusion_detection": "Analyze this student response for confusion: {student_response}",
            "style_adaptation": "Adapt this explanation for {learning_style} learner: {topic}"
        }
        return defaults.get(prompt_name, "Please help with: {question}")
    
    def _create_fallback_prompts(self):
        """Create minimal fallback prompts"""
        self.prompts = {
            "explain": "Explain this clearly for grade {grade_level}: {question}",
            "assess": "Assess this answer: {student_answer}",
            "confusion_detection": "Check for confusion in: {student_response}",
            "style_adaptation": "Adapt explanation for: {topic}"
        }
    
    async def generate_explanation(self, question: str, student_profile: StudentProfile, 
                                 grade_level: str, language: str) -> ExplanationResponse:
        """Generate personalized explanation for student question"""
        try:
            # Build personalized prompt
            prompt = self._build_explanation_prompt(question, student_profile, grade_level, language)
            
            # Call LLM (Gemini API)
            response_text = await self.llm.generate(
                prompt=prompt,
                temperature=0.7,
                max_tokens=1500,
            )
            
            # Parse response
            result = self._parse_explanation_response(response_text)
            
            return ExplanationResponse(**result)
            
        except Exception as e:
            logger.error(f"Error generating explanation: {str(e)}")
            return self._create_fallback_explanation(question, grade_level)
    
    def _build_explanation_prompt(self, question: str, student_profile: StudentProfile, 
                                grade_level: str, language: str) -> str:
        """Build personalized prompt for explanation"""
        try:
            # Extract student context
            confusion_patterns = ", ".join(student_profile.confusion_patterns.keys()) if student_profile.confusion_patterns else "None identified"
            success_patterns = ", ".join(student_profile.success_patterns.keys()) if student_profile.success_patterns else "None identified"
            
            # Format the prompt
            formatted_prompt = self.prompts["explain"].format(
                student_id=student_profile.student_id,
                grade_level=grade_level,
                language=language,
                learning_style=student_profile.learning_style.value,
                confusion_patterns=confusion_patterns,
                success_patterns=success_patterns,
                explanation_style=student_profile.explanation_style_preference,
                question=question
            )
            
            return formatted_prompt
            
        except Exception as e:
            logger.error(f"Error building prompt: {str(e)}")
            return f"Please explain this for a grade {grade_level} student: {question}"
    
    def _parse_explanation_response(self, response_text: str) -> Dict[str, Any]:
        """Parse production-grade Gemini response with Mermaid diagram support"""
        try:
            # Try to parse as JSON first
            if response_text.strip().startswith('{'):
                parsed = json.loads(response_text)
                return self._validate_and_enhance_response(parsed)
            
            # If not JSON, extract JSON from markdown code blocks
            import re
            json_match = re.search(r'```json\s*(\{.*?\})\s*```', response_text, re.DOTALL)
            if json_match:
                parsed = json.loads(json_match.group(1))
                return self._validate_and_enhance_response(parsed)
            
            # If still no JSON, create structured response from text
            return self._create_structured_response_from_text(response_text)
            
        except Exception as e:
            logger.error(f"Error parsing response: {str(e)}")
            return self._create_structured_response_from_text(response_text)

    def _validate_and_enhance_response(self, parsed: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and enhance response with production-grade defaults"""
        # Ensure mermaid_diagrams field exists
        if "mermaid_diagrams" not in parsed:
            parsed["mermaid_diagrams"] = []
        
        # Validate board script steps have mermaid support
        if "board_script" in parsed and "steps" in parsed["board_script"]:
            for step in parsed["board_script"]["steps"]:
                if "mermaid_code" not in step:
                    step["mermaid_code"] = None
                    
        return parsed
    
    def _create_structured_response_from_text(self, text: str) -> Dict[str, Any]:
        """Create structured response from plain text"""
        # Create basic board script from text
        steps = []
        lines = text.split('\n')
        
        step_num = 1
        for line in lines[:6]:  # Limit to first 6 lines
            if line.strip():
                step_type = "title" if step_num == 1 else "body"
                steps.append({
                    "step": step_num,
                    "content": line.strip(),
                    "type": step_type,
                    "draw_duration_ms": 1500 if step_type == "title" else 1000
                })
                step_num += 1
        
        board_script = {
            "steps": steps,
            "total_duration_ms": sum(step["draw_duration_ms"] for step in steps),
            "background_color": "#000000",
            "text_color": "#FFFFFF"
        }
        
        return {
            "explanation_text": text,
            "mermaid_diagrams": [],  # Production-grade: always include mermaid field
            "board_script": board_script,
            "difficulty_level": "medium",
            "key_concepts": ["General concept"],
            "follow_up_questions": ["Can you give me another example?"],
            "confidence_score": 0.8
        }
    
    async def assess_answer(self, question: str, student_answer: str, 
                          student_profile: StudentProfile, expected_answer: str = None) -> AssessmentResponse:
        """Assess student's answer and provide feedback"""
        try:
            if not self.llm:
                return self._create_fallback_assessment(student_answer)
            prompt = self._build_assessment_prompt(question, student_answer, student_profile, expected_answer)
            response_text = await self.llm.generate(prompt=prompt, max_tokens=1500)
            result = self._parse_assessment_response(response_text)
            
            return AssessmentResponse(**result)
            
        except Exception as e:
            logger.error(f"Error assessing answer: {str(e)}")
            return self._create_fallback_assessment(student_answer)
    
    def _build_assessment_prompt(self, question: str, student_answer: str, 
                               student_profile: StudentProfile, expected_answer: str = None) -> str:
        """Build prompt for answer assessment"""
        try:
            learning_profile = {
                "grade_level": student_profile.grade_level.value,
                "learning_style": student_profile.learning_style.value,
                "confusion_patterns": list(student_profile.confusion_patterns.keys())
            }
            
            formatted_prompt = self.prompts["assess"].format(
                student_id=student_profile.student_id,
                grade_level=student_profile.grade_level.value,
                learning_profile=json.dumps(learning_profile),
                question=question,
                student_answer=student_answer,
                expected_answer=expected_answer or "Not provided"
            )
            
            return formatted_prompt
            
        except Exception as e:
            logger.error(f"Error building assessment prompt: {str(e)}")
            return f"Assess this answer: {student_answer} for question: {question}"
    
    def _parse_assessment_response(self, response_text: str) -> Dict[str, Any]:
        """Parse assessment response"""
        try:
            # Try to parse as JSON
            if response_text.strip().startswith('{'):
                return json.loads(response_text)
            
            # Extract JSON from markdown
            import re
            json_match = re.search(r'```json\s*(\{.*?\})\s*```', response_text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group(1))
            
            # Fallback to text analysis
            return self._analyze_answer_from_text(response_text)
            
        except Exception as e:
            logger.error(f"Error parsing assessment: {str(e)}")
            return self._analyze_answer_from_text(response_text)
    
    def _analyze_answer_from_text(self, text: str) -> Dict[str, Any]:
        """Analyze answer from plain text response"""
        text_lower = text.lower()
        
        # Simple correctness detection
        is_correct = any(word in text_lower for word in ["correct", "right", "good", "yes"])
        
        return {
            "is_correct": is_correct,
            "confidence_score": 0.7,
            "feedback": text,
            "mistakes_identified": ["Need more detailed analysis"],
            "suggestions": ["Please review the concept again"],
            "next_explanation_style": "visual"
        }
    
    def _create_fallback_explanation(self, question: str, grade_level: str) -> ExplanationResponse:
        """Create fallback explanation when API fails"""
        fallback_steps = [
            {
                "step": 1,
                "content": f"Let's explore: {question}",
                "type": "title",
                "draw_duration_ms": 1500
            },
            {
                "step": 2,
                "content": "This is a great question for your grade level!",
                "type": "body",
                "draw_duration_ms": 1000
            },
            {
                "step": 3,
                "content": "Let me break this down step by step...",
                "type": "body",
                "draw_duration_ms": 1000
            }
        ]
        
        board_script = BoardScript(
            steps=[BoardStep(**step) for step in fallback_steps],
            total_duration_ms=3500
        )
        
        return ExplanationResponse(
            explanation_text=f"I'd be happy to help explain this topic for a grade {grade_level} student. Due to a technical issue, I'm providing a basic response. Please try again for a full personalized explanation.",
            board_script=board_script,
            difficulty_level="medium",
            key_concepts=["General understanding"],
            follow_up_questions=["Would you like me to explain this differently?"],
            confidence_score=0.5
        )
    
    def _create_fallback_assessment(self, student_answer: str) -> AssessmentResponse:
        """Create fallback assessment when API fails"""
        return AssessmentResponse(
            is_correct=True,  # Optimistic fallback
            confidence_score=0.5,
            feedback="Thank you for your answer! Due to a technical issue, I cannot provide detailed feedback right now. Please try submitting your answer again.",
            mistakes_identified=[],
            suggestions=["Please resubmit for detailed feedback"],
            next_explanation_style="visual"
        )
    
    async def detect_confusion(self, question: str, student_response: str, 
                             interaction_history: List[Dict]) -> Dict[str, Any]:
        """Detect confusion patterns in student responses"""
        try:
            if not self.llm:
                return {"confusion_detected": False}
            prompt = self.prompts["confusion_detection"].format(
                interaction_history=json.dumps(interaction_history[-5:]),  # Last 5 interactions
                question=question,
                student_response=student_response
            )
            text = await self.llm.generate(prompt=prompt, max_tokens=1000)
            return self._parse_json_response(text, {
                "confusion_detected": False,
                "confusion_level": "low",
                "confusion_areas": [],
                "recommended_approach": "continue",
                "explanation_style": "visual"
            })
            
        except Exception as e:
            logger.error(f"Error detecting confusion: {str(e)}")
            return {"confusion_detected": False}
    
    async def adapt_explanation_style(self, topic: str, student_profile: StudentProfile, 
                                    requested_style: str) -> Dict[str, Any]:
        """Adapt explanation to different learning style"""
        try:
            if not self.llm:
                return {"adapted_explanation": f"Basic explanation of {topic}"}
            prompt = self.prompts["style_adaptation"].format(
                grade_level=student_profile.grade_level.value,
                learning_style=student_profile.learning_style.value,
                recent_performance="Average",  # Could be enhanced with actual data
                confusion_areas=list(student_profile.confusion_patterns.keys()),
                topic=topic,
                requested_style=requested_style
            )
            text = await self.llm.generate(prompt=prompt, max_tokens=2000)
            return self._parse_json_response(text, {
                "adapted_explanation": f"Explanation of {topic} using {requested_style} approach",
                "board_script": {"steps": [], "total_duration_ms": 0},
                "style_rationale": f"This {requested_style} approach should help with understanding"
            })
            
        except Exception as e:
            logger.error(f"Error adapting explanation style: {str(e)}")
            return {"adapted_explanation": f"Basic explanation of {topic}"}
    
    def _parse_json_response(self, response_text: str, fallback: Dict[str, Any]) -> Dict[str, Any]:
        """Parse JSON response with fallback"""
        try:
            if response_text.strip().startswith('{'):
                return json.loads(response_text)
            
            import re
            json_match = re.search(r'```json\s*(\{.*?\})\s*```', response_text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group(1))
            
            return fallback
            
        except Exception:
            return fallback
    
    def is_healthy(self) -> bool:
        """Gemini is configured and prompts are loaded."""
        if not self.prompts:
            return False
        try:
            return self.llm is not None and self.llm.is_healthy()
        except Exception:
            return False
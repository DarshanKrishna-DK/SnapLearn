"""
Conversation Engine for SnapLearn AI - Phase 3
Manages multi-turn conversations with context, difficulty adaptation, and learning optimization
"""

import os
import logging
import json
import asyncio
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime, timedelta
from enum import Enum
import uuid

from models import (
    StudentProfile, 
    ExplanationResponse, 
    AssessmentResponse,
    GradeLevel, 
    LanguageCode,
    BoardScript,
    BoardStep
)

logger = logging.getLogger(__name__)

class ConversationState(str, Enum):
    """States of the tutoring conversation"""
    STARTING = "starting"
    EXPLAINING = "explaining"
    ASSESSING = "assessing"
    CONFUSED = "confused"
    ADAPTING = "adapting"
    COMPLETED = "completed"
    PAUSED = "paused"

class DifficultyLevel(str, Enum):
    """Difficulty levels for adaptive learning"""
    VERY_EASY = "very_easy"
    EASY = "easy" 
    MEDIUM = "medium"
    HARD = "hard"
    VERY_HARD = "very_hard"

class ExplanationStyle(str, Enum):
    """Different explanation approaches"""
    VISUAL = "visual"
    VERBAL = "verbal"
    STEP_BY_STEP = "step_by_step"
    CONCEPTUAL = "conceptual"
    PRACTICAL = "practical"
    ANALOGICAL = "analogical"

class ConversationEngine:
    """Advanced multi-turn conversation engine with adaptive learning"""
    
    def __init__(self):
        self.gemini_client = None
        self.conversations = {}  # In-memory conversation storage
        self.interaction_cache = {}  # Cache Gemini interaction IDs
        
        # Learning analytics
        self.confusion_patterns = {}
        self.success_patterns = {}
        self.adaptation_history = {}
        
        # Initialize Gemini Interactions API
        asyncio.create_task(self._init_gemini())
    
    async def _init_gemini(self):
        """Initialize Gemini Interactions API client"""
        try:
            from google import genai
            
            api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
            if not api_key:
                logger.error("Gemini API key not found for conversation engine")
                return
            
            self.gemini_client = genai.Client(api_key=api_key)
            logger.info("Conversation engine: Gemini Interactions API initialized")
            
        except ImportError:
            logger.error("Google GenAI library not installed for conversation engine")
        except Exception as e:
            logger.error(f"Error initializing Gemini for conversation engine: {str(e)}")
    
    async def start_conversation(self, 
                               student_id: str, 
                               initial_question: str,
                               student_profile: StudentProfile,
                               context: Optional[str] = None) -> Dict[str, Any]:
        """Start a new tutoring conversation"""
        try:
            conversation_id = str(uuid.uuid4())
            
            # Initialize conversation state
            conversation = {
                "id": conversation_id,
                "student_id": student_id,
                "state": ConversationState.STARTING,
                "current_topic": initial_question,
                "difficulty_level": self._determine_initial_difficulty(student_profile),
                "explanation_style": self._determine_explanation_style(student_profile),
                "turn_count": 0,
                "created_at": datetime.now().isoformat(),
                "last_activity": datetime.now().isoformat(),
                "student_profile_snapshot": student_profile.dict(),
                "conversation_history": [],
                "learning_objectives": [],
                "confusion_indicators": [],
                "success_indicators": [],
                "gemini_interaction_id": None
            }
            
            # Store conversation
            self.conversations[conversation_id] = conversation
            
            # Generate initial explanation using Gemini Interactions API
            initial_response = await self._generate_adaptive_explanation(
                conversation,
                initial_question,
                context
            )
            
            # Update conversation with initial interaction
            conversation["state"] = ConversationState.EXPLAINING
            conversation["turn_count"] = 1
            conversation["last_activity"] = datetime.now().isoformat()
            
            # Add to conversation history
            conversation["conversation_history"].append({
                "turn": 1,
                "type": "student_question",
                "content": initial_question,
                "timestamp": datetime.now().isoformat()
            })
            
            conversation["conversation_history"].append({
                "turn": 1,
                "type": "ai_explanation", 
                "content": initial_response,
                "timestamp": datetime.now().isoformat()
            })
            
            return {
                "conversation_id": conversation_id,
                "response": initial_response,
                "state": conversation["state"],
                "turn_count": conversation["turn_count"],
                "learning_insights": self._generate_learning_insights(conversation)
            }
            
        except Exception as e:
            logger.error(f"Error starting conversation: {str(e)}")
            raise
    
    async def continue_conversation(self, 
                                  conversation_id: str,
                                  student_input: str,
                                  input_type: str = "question") -> Dict[str, Any]:
        """Continue an existing conversation with context awareness"""
        try:
            if conversation_id not in self.conversations:
                raise ValueError(f"Conversation {conversation_id} not found")
            
            conversation = self.conversations[conversation_id]
            conversation["turn_count"] += 1
            conversation["last_activity"] = datetime.now().isoformat()
            
            # Add student input to history
            conversation["conversation_history"].append({
                "turn": conversation["turn_count"],
                "type": f"student_{input_type}",
                "content": student_input,
                "timestamp": datetime.now().isoformat()
            })
            
            # Analyze student input for confusion/understanding
            analysis = await self._analyze_student_input(conversation, student_input, input_type)
            
            # Update conversation state based on analysis
            self._update_conversation_state(conversation, analysis)
            
            # Generate appropriate response based on current state
            response = await self._generate_contextual_response(conversation, student_input, analysis)
            
            # Add AI response to history
            conversation["conversation_history"].append({
                "turn": conversation["turn_count"],
                "type": "ai_response",
                "content": response,
                "analysis": analysis,
                "timestamp": datetime.now().isoformat()
            })
            
            # Update learning patterns
            self._update_learning_patterns(conversation, analysis)
            
            return {
                "conversation_id": conversation_id,
                "response": response,
                "state": conversation["state"],
                "turn_count": conversation["turn_count"],
                "analysis": analysis,
                "learning_insights": self._generate_learning_insights(conversation),
                "recommendations": self._generate_study_recommendations(conversation)
            }
            
        except Exception as e:
            logger.error(f"Error continuing conversation: {str(e)}")
            raise
    
    async def assess_student_answer(self, 
                                  conversation_id: str,
                                  question: str,
                                  student_answer: str) -> Dict[str, Any]:
        """Assess student answer with detailed feedback and adaptation"""
        try:
            conversation = self.conversations[conversation_id]
            conversation["state"] = ConversationState.ASSESSING
            
            # Generate comprehensive assessment using Gemini
            assessment = await self._generate_detailed_assessment(
                conversation, question, student_answer
            )
            
            # Update conversation based on assessment
            self._process_assessment_results(conversation, assessment)
            
            # Determine next steps
            next_action = self._determine_next_action(conversation, assessment)
            
            return {
                "conversation_id": conversation_id,
                "assessment": assessment,
                "next_action": next_action,
                "state": conversation["state"],
                "learning_insights": self._generate_learning_insights(conversation)
            }
            
        except Exception as e:
            logger.error(f"Error assessing student answer: {str(e)}")
            raise
    
    async def adapt_explanation_style(self, 
                                    conversation_id: str,
                                    new_style: str,
                                    reason: str) -> Dict[str, Any]:
        """Adapt explanation style based on student needs"""
        try:
            conversation = self.conversations[conversation_id]
            old_style = conversation["explanation_style"]
            
            conversation["explanation_style"] = new_style
            conversation["state"] = ConversationState.ADAPTING
            
            # Log adaptation
            adaptation_log = {
                "timestamp": datetime.now().isoformat(),
                "from_style": old_style,
                "to_style": new_style,
                "reason": reason,
                "turn": conversation["turn_count"]
            }
            
            if "adaptations" not in conversation:
                conversation["adaptations"] = []
            conversation["adaptations"].append(adaptation_log)
            
            # Re-explain current topic with new style
            current_topic = conversation["current_topic"]
            adapted_explanation = await self._generate_style_adapted_explanation(
                conversation, current_topic, new_style
            )
            
            return {
                "conversation_id": conversation_id,
                "adapted_explanation": adapted_explanation,
                "adaptation_log": adaptation_log,
                "state": conversation["state"]
            }
            
        except Exception as e:
            logger.error(f"Error adapting explanation style: {str(e)}")
            raise
    
    async def _generate_adaptive_explanation(self, 
                                           conversation: Dict[str, Any],
                                           question: str,
                                           context: Optional[str] = None) -> ExplanationResponse:
        """Generate explanation using Gemini Interactions API with full context"""
        try:
            if not self.gemini_client:
                raise Exception("Gemini client not initialized")
            
            # Build comprehensive system instruction
            system_instruction = self._build_tutoring_system_instruction(conversation)
            
            # Prepare input with full context
            input_text = self._prepare_contextual_input(conversation, question, context)
            
            # Create Gemini interaction
            interaction = self.gemini_client.interactions.create(
                model="gemini-3-flash-preview",
                input=input_text,
                system_instruction=system_instruction,
                previous_interaction_id=conversation.get("gemini_interaction_id"),
                generation_config={
                    "temperature": 0.7,
                    "top_p": 0.8,
                    "max_output_tokens": 2048
                }
            )
            
            # Store interaction ID for conversation continuity
            conversation["gemini_interaction_id"] = interaction.id
            
            # Parse response into structured format
            response_text = interaction.outputs[-1].text
            explanation_data = await self._parse_explanation_response(response_text, conversation)
            
            return ExplanationResponse(**explanation_data)
            
        except Exception as e:
            logger.error(f"Error generating adaptive explanation: {str(e)}")
            return self._create_fallback_explanation(question)
    
    def _build_tutoring_system_instruction(self, conversation: Dict[str, Any]) -> str:
        """Build comprehensive system instruction for AI tutor"""
        student_profile = conversation["student_profile_snapshot"]
        
        return f"""You are an expert AI tutor specializing in personalized, adaptive education. Your role is to provide exceptional learning experiences through multi-turn conversations.

STUDENT CONTEXT:
- Grade Level: {student_profile['grade_level']}
- Learning Style: {student_profile['learning_style']}
- Current Difficulty: {conversation['difficulty_level']}
- Explanation Style: {conversation['explanation_style']}
- Language: {student_profile['preferred_language']}
- Conversation Turn: {conversation['turn_count']}

STUDENT LEARNING PATTERNS:
- Success Areas: {', '.join(list(student_profile.get('success_patterns', {}).keys())[:3])}
- Challenge Areas: {', '.join(list(student_profile.get('confusion_patterns', {}).keys())[:3])}

CONVERSATION CONTEXT:
- Current Topic: {conversation['current_topic']}
- State: {conversation['state']}
- Turn Count: {conversation['turn_count']}

TUTORING PRINCIPLES:
1. Personalization: Adapt to the student's learning style and grade level
2. Progressive Disclosure: Build understanding step by step
3. Active Learning: Encourage questions and participation
4. Mistake-Friendly: Frame errors as learning opportunities
5. Engagement: Use examples relevant to the student's interests

RESPONSE FORMAT:
Your response should be in JSON format with:
{{
  "explanation_text": "Main explanation content",
  "board_script": {{
    "steps": [
      {{"step": 1, "content": "Step content", "type": "title|body|equation|highlight", "draw_duration_ms": 1000}}
    ],
    "total_duration_ms": 5000,
    "background_color": "#1a1a1a",
    "text_color": "#ffffff"
  }},
  "difficulty_level": "current difficulty assessment",
  "key_concepts": ["concept1", "concept2"],
  "follow_up_questions": ["question1", "question2"],
  "confidence_score": 0.95,
  "learning_objectives": ["objective1", "objective2"],
  "confusion_check": "question to verify understanding",
  "style_notes": "explanation of why this style was chosen"
}}

Always maintain empathy, patience, and encouragement in your explanations."""
    
    def _prepare_contextual_input(self, 
                                conversation: Dict[str, Any], 
                                current_input: str,
                                context: Optional[str] = None) -> str:
        """Prepare input with full conversation context"""
        
        # Get recent conversation history for context
        recent_history = conversation["conversation_history"][-6:]  # Last 3 turns
        
        context_parts = []
        
        if context:
            context_parts.append(f"Additional Context: {context}")
        
        if recent_history:
            context_parts.append("Recent Conversation:")
            for item in recent_history:
                context_parts.append(f"- {item['type']}: {item['content']}")
        
        context_parts.append(f"Current Input: {current_input}")
        
        return "\n".join(context_parts)
    
    async def _analyze_student_input(self, 
                                   conversation: Dict[str, Any],
                                   student_input: str, 
                                   input_type: str) -> Dict[str, Any]:
        """Analyze student input for understanding, confusion, engagement"""
        try:
            if not self.gemini_client:
                return self._create_basic_analysis(student_input)
            
            analysis_prompt = f"""Analyze this student input for learning indicators:

STUDENT INPUT: {student_input}
INPUT TYPE: {input_type}

CONVERSATION CONTEXT:
- Grade Level: {conversation['student_profile_snapshot']['grade_level']}
- Current Topic: {conversation['current_topic']}
- Turn: {conversation['turn_count']}
- Difficulty: {conversation['difficulty_level']}

Please analyze and respond in JSON format:
{{
  "understanding_level": "high|medium|low",
  "confusion_indicators": ["specific confusion signs"],
  "engagement_level": "high|medium|low",
  "misconceptions": ["identified misconceptions"],
  "strengths_shown": ["demonstrated strengths"],
  "suggested_difficulty": "very_easy|easy|medium|hard|very_hard",
  "suggested_style": "visual|verbal|step_by_step|conceptual|practical|analogical",
  "confidence_score": 0.85,
  "next_action": "continue|assess|clarify|reteach|advance"
}}"""

            interaction = self.gemini_client.interactions.create(
                model="gemini-3.1-flash-lite-preview", 
                input=analysis_prompt,
                previous_interaction_id=conversation.get("analysis_interaction_id"),
                generation_config={
                    "temperature": 0.3,
                    "max_output_tokens": 512
                }
            )
            
            # Store analysis interaction ID
            conversation["analysis_interaction_id"] = interaction.id
            
            response_text = interaction.outputs[-1].text
            return json.loads(response_text)
            
        except Exception as e:
            logger.error(f"Error analyzing student input: {str(e)}")
            return self._create_basic_analysis(student_input)
    
    def _create_basic_analysis(self, student_input: str) -> Dict[str, Any]:
        """Create basic analysis when AI analysis fails"""
        # Simple keyword-based analysis
        confusion_words = ["confused", "don't understand", "help", "stuck", "lost"]
        engagement_words = ["interesting", "cool", "wow", "more", "another"]
        
        has_confusion = any(word in student_input.lower() for word in confusion_words)
        has_engagement = any(word in student_input.lower() for word in engagement_words)
        
        return {
            "understanding_level": "low" if has_confusion else "medium",
            "confusion_indicators": ["expressed confusion"] if has_confusion else [],
            "engagement_level": "high" if has_engagement else "medium",
            "misconceptions": [],
            "strengths_shown": [],
            "suggested_difficulty": "easy" if has_confusion else "medium",
            "suggested_style": "step_by_step",
            "confidence_score": 0.6,
            "next_action": "clarify" if has_confusion else "continue"
        }
    
    def _update_conversation_state(self, 
                                 conversation: Dict[str, Any], 
                                 analysis: Dict[str, Any]):
        """Update conversation state based on analysis"""
        
        # Update confusion indicators
        if analysis["confusion_indicators"]:
            conversation["confusion_indicators"].extend(analysis["confusion_indicators"])
            if analysis["understanding_level"] == "low":
                conversation["state"] = ConversationState.CONFUSED
        
        # Update success indicators
        if analysis["strengths_shown"]:
            conversation["success_indicators"].extend(analysis["strengths_shown"])
        
        # Adapt difficulty if suggested
        if analysis["suggested_difficulty"] != conversation["difficulty_level"]:
            conversation["difficulty_level"] = analysis["suggested_difficulty"]
        
        # Adapt explanation style if needed
        if analysis["suggested_style"] != conversation["explanation_style"]:
            conversation["explanation_style"] = analysis["suggested_style"]
    
    async def _generate_contextual_response(self, 
                                          conversation: Dict[str, Any],
                                          student_input: str,
                                          analysis: Dict[str, Any]) -> ExplanationResponse:
        """Generate response based on conversation state and analysis"""
        
        # Determine response type based on state and analysis
        if conversation["state"] == ConversationState.CONFUSED:
            return await self._generate_clarification_response(conversation, student_input, analysis)
        elif analysis["next_action"] == "assess":
            return await self._generate_assessment_question(conversation, student_input)
        elif analysis["next_action"] == "advance":
            return await self._generate_advanced_content(conversation, student_input)
        else:
            return await self._generate_adaptive_explanation(conversation, student_input)
    
    async def _generate_clarification_response(self, 
                                             conversation: Dict[str, Any],
                                             student_input: str,
                                             analysis: Dict[str, Any]) -> ExplanationResponse:
        """Generate clarification when student is confused"""
        
        clarification_prompt = f"""The student is confused about: {conversation['current_topic']}

Student said: "{student_input}"
Confusion indicators: {', '.join(analysis['confusion_indicators'])}
Misconceptions: {', '.join(analysis.get('misconceptions', []))}

Generate a clarifying explanation that:
1. Addresses the specific confusion
2. Uses simpler language
3. Provides concrete examples
4. Breaks down into smaller steps
5. Includes a confidence check question

Use the {conversation['explanation_style']} style and {conversation['difficulty_level']} difficulty."""
        
        return await self._generate_adaptive_explanation(conversation, clarification_prompt)
    
    def _determine_initial_difficulty(self, student_profile: StudentProfile) -> str:
        """Determine initial difficulty based on student profile"""
        
        # Analyze success/confusion patterns
        total_success = sum(student_profile.success_patterns.values())
        total_confusion = sum(student_profile.confusion_patterns.values())
        
        if total_success + total_confusion == 0:
            # New student - start with grade-appropriate medium
            return DifficultyLevel.MEDIUM
        
        success_rate = total_success / (total_success + total_confusion)
        
        if success_rate > 0.8:
            return DifficultyLevel.HARD
        elif success_rate > 0.6:
            return DifficultyLevel.MEDIUM
        elif success_rate > 0.4:
            return DifficultyLevel.EASY
        else:
            return DifficultyLevel.VERY_EASY
    
    def _determine_explanation_style(self, student_profile: StudentProfile) -> str:
        """Determine initial explanation style based on learning preferences"""
        
        learning_style_mapping = {
            "visual": ExplanationStyle.VISUAL,
            "auditory": ExplanationStyle.VERBAL,
            "kinesthetic": ExplanationStyle.PRACTICAL,
            "reading_writing": ExplanationStyle.STEP_BY_STEP,
            "mixed": ExplanationStyle.CONCEPTUAL
        }
        
        return learning_style_mapping.get(
            student_profile.learning_style, 
            ExplanationStyle.CONCEPTUAL
        )
    
    def _generate_learning_insights(self, conversation: Dict[str, Any]) -> Dict[str, Any]:
        """Generate insights about student's learning progress"""
        
        history = conversation["conversation_history"]
        
        # Calculate engagement metrics
        student_turns = [h for h in history if h["type"].startswith("student_")]
        ai_turns = [h for h in history if h["type"].startswith("ai_")]
        
        avg_response_length = sum(len(turn["content"]) for turn in student_turns) / max(len(student_turns), 1)
        
        insights = {
            "total_turns": len(history),
            "student_engagement": "high" if avg_response_length > 50 else "medium" if avg_response_length > 20 else "low",
            "confusion_count": len(conversation.get("confusion_indicators", [])),
            "success_count": len(conversation.get("success_indicators", [])),
            "current_difficulty": conversation["difficulty_level"],
            "current_style": conversation["explanation_style"],
            "adaptations_made": len(conversation.get("adaptations", [])),
            "session_duration": self._calculate_session_duration(conversation),
            "learning_trajectory": self._assess_learning_trajectory(conversation)
        }
        
        return insights
    
    def _generate_study_recommendations(self, conversation: Dict[str, Any]) -> List[str]:
        """Generate personalized study recommendations"""
        
        recommendations = []
        
        # Based on confusion patterns
        if len(conversation.get("confusion_indicators", [])) > 2:
            recommendations.append(f"Review the basics of {conversation['current_topic']} with simpler examples")
            recommendations.append("Practice similar problems at an easier difficulty level")
        
        # Based on success patterns  
        if len(conversation.get("success_indicators", [])) > 3:
            recommendations.append(f"Try more challenging problems related to {conversation['current_topic']}")
            recommendations.append("Explore advanced applications of these concepts")
        
        # Based on engagement
        if conversation["turn_count"] > 10:
            recommendations.append("Take a short break - you've been learning actively!")
            recommendations.append("Review what you've learned before moving to new topics")
        
        # Style-based recommendations
        style = conversation["explanation_style"]
        if style == ExplanationStyle.VISUAL:
            recommendations.append("Look for diagrams and visual aids for this topic")
        elif style == ExplanationStyle.PRACTICAL:
            recommendations.append("Find real-world applications to practice these concepts")
        
        return recommendations[:5]  # Return top 5 recommendations
    
    async def get_conversation_summary(self, conversation_id: str) -> Dict[str, Any]:
        """Get comprehensive conversation summary"""
        try:
            if conversation_id not in self.conversations:
                raise ValueError(f"Conversation {conversation_id} not found")
            
            conversation = self.conversations[conversation_id]
            
            return {
                "conversation_id": conversation_id,
                "student_id": conversation["student_id"],
                "topic": conversation["current_topic"],
                "state": conversation["state"],
                "duration": self._calculate_session_duration(conversation),
                "turn_count": conversation["turn_count"],
                "learning_insights": self._generate_learning_insights(conversation),
                "key_concepts_covered": conversation.get("learning_objectives", []),
                "adaptations_made": conversation.get("adaptations", []),
                "final_difficulty": conversation["difficulty_level"],
                "final_style": conversation["explanation_style"],
                "recommendations": self._generate_study_recommendations(conversation)
            }
            
        except Exception as e:
            logger.error(f"Error generating conversation summary: {str(e)}")
            raise
    
    def _calculate_session_duration(self, conversation: Dict[str, Any]) -> int:
        """Calculate session duration in minutes"""
        start_time = datetime.fromisoformat(conversation["created_at"])
        end_time = datetime.fromisoformat(conversation["last_activity"])
        duration = (end_time - start_time).total_seconds() / 60
        return int(duration)
    
    def _assess_learning_trajectory(self, conversation: Dict[str, Any]) -> str:
        """Assess overall learning trajectory"""
        
        confusion_count = len(conversation.get("confusion_indicators", []))
        success_count = len(conversation.get("success_indicators", []))
        adaptations = len(conversation.get("adaptations", []))
        
        if success_count > confusion_count * 2:
            return "strong_progress"
        elif success_count > confusion_count:
            return "steady_progress"
        elif adaptations > 2:
            return "adaptive_learning"
        elif confusion_count > success_count * 2:
            return "needs_support"
        else:
            return "mixed_progress"
    
    async def pause_conversation(self, conversation_id: str) -> Dict[str, Any]:
        """Pause a conversation for later resumption"""
        if conversation_id in self.conversations:
            self.conversations[conversation_id]["state"] = ConversationState.PAUSED
            self.conversations[conversation_id]["paused_at"] = datetime.now().isoformat()
            
            return {"conversation_id": conversation_id, "status": "paused"}
        
        raise ValueError(f"Conversation {conversation_id} not found")
    
    async def resume_conversation(self, conversation_id: str) -> Dict[str, Any]:
        """Resume a paused conversation"""
        if conversation_id in self.conversations:
            conversation = self.conversations[conversation_id]
            conversation["state"] = ConversationState.EXPLAINING
            conversation["resumed_at"] = datetime.now().isoformat()
            
            return {
                "conversation_id": conversation_id, 
                "status": "resumed",
                "summary": await self.get_conversation_summary(conversation_id)
            }
        
        raise ValueError(f"Conversation {conversation_id} not found")
    
    def is_healthy(self) -> bool:
        """Check if conversation engine is healthy"""
        return self.gemini_client is not None
"""
Adaptive Quiz System for SnapLearn AI
Generates grade-appropriate quizzes that adapt to student performance
"""

import random
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime, timezone
from student_profile import DifficultyLevel, LearningStyle

@dataclass
class QuizQuestion:
    id: str
    question: str
    options: List[str]
    correct_answer: int  # Index of correct option
    explanation: str
    topic: str
    grade_level: str
    difficulty: DifficultyLevel

@dataclass
class QuizResponse:
    question_id: str
    selected_answer: int
    is_correct: bool
    time_taken_seconds: int

@dataclass
class Quiz:
    id: str
    title: str
    topic: str
    grade_level: str
    difficulty: DifficultyLevel
    questions: List[QuizQuestion]
    time_limit_minutes: int

class QuizGenerator:
    """Generates adaptive quizzes based on student profile and grade level"""
    
    def __init__(self):
        # Sample question bank - in a real implementation, this would be a database
        self.question_bank = self._initialize_question_bank()
    
    def _initialize_question_bank(self) -> Dict[str, List[QuizQuestion]]:
        """Initialize sample question bank organized by grade and topic"""
        bank = {}
        
        # Grade 2 Math Questions
        bank["2_math"] = [
            QuizQuestion(
                id="2m_001",
                question="What is 5 + 3?",
                options=["6", "7", "8", "9"],
                correct_answer=2,
                explanation="5 + 3 = 8. We can count: 5, 6, 7, 8.",
                topic="Addition",
                grade_level="2",
                difficulty=DifficultyLevel.EASY
            ),
            QuizQuestion(
                id="2m_002",
                question="If you have 12 apples and eat 4, how many do you have left?",
                options=["6", "7", "8", "9"],
                correct_answer=2,
                explanation="12 - 4 = 8. Subtraction means taking away.",
                topic="Subtraction",
                grade_level="2",
                difficulty=DifficultyLevel.MEDIUM
            ),
        ]
        
        # Grade 4 Math Questions
        bank["4_math"] = [
            QuizQuestion(
                id="4m_001",
                question="What is 24 × 6?",
                options=["144", "146", "124", "164"],
                correct_answer=0,
                explanation="24 × 6 = 144. You can break this down as (20 × 6) + (4 × 6) = 120 + 24 = 144.",
                topic="Multiplication",
                grade_level="4",
                difficulty=DifficultyLevel.MEDIUM
            ),
            QuizQuestion(
                id="4m_002",
                question="What is the area of a rectangle with length 8 units and width 5 units?",
                options=["13 square units", "26 square units", "40 square units", "45 square units"],
                correct_answer=2,
                explanation="Area = length × width = 8 × 5 = 40 square units.",
                topic="Geometry",
                grade_level="4",
                difficulty=DifficultyLevel.HARD
            ),
        ]
        
        # Grade 5 Science Questions
        bank["5_science"] = [
            QuizQuestion(
                id="5s_001",
                question="What happens to water when it reaches 100°C (212°F)?",
                options=["It freezes", "It boils", "It melts", "Nothing happens"],
                correct_answer=1,
                explanation="At 100°C (212°F), water reaches its boiling point and turns into water vapor (steam).",
                topic="Water Cycle",
                grade_level="5",
                difficulty=DifficultyLevel.EASY
            ),
            QuizQuestion(
                id="5s_002",
                question="Which process involves plants using sunlight to make food?",
                options=["Respiration", "Photosynthesis", "Digestion", "Circulation"],
                correct_answer=1,
                explanation="Photosynthesis is the process where plants use sunlight, water, and carbon dioxide to make glucose (food) and oxygen.",
                topic="Plant Biology",
                grade_level="5",
                difficulty=DifficultyLevel.MEDIUM
            ),
        ]
        
        # Grade 7 Math Questions
        bank["7_math"] = [
            QuizQuestion(
                id="7m_001",
                question="Solve for x: 2x + 5 = 15",
                options=["x = 4", "x = 5", "x = 6", "x = 10"],
                correct_answer=1,
                explanation="2x + 5 = 15. Subtract 5 from both sides: 2x = 10. Divide by 2: x = 5.",
                topic="Algebra",
                grade_level="7",
                difficulty=DifficultyLevel.MEDIUM
            ),
            QuizQuestion(
                id="7m_002",
                question="What is the probability of rolling a 3 on a fair six-sided die?",
                options=["1/2", "1/3", "1/6", "3/6"],
                correct_answer=2,
                explanation="There is 1 favorable outcome (rolling a 3) out of 6 possible outcomes, so the probability is 1/6.",
                topic="Probability",
                grade_level="7",
                difficulty=DifficultyLevel.HARD
            ),
        ]
        
        return bank
    
    def generate_quiz(
        self,
        grade_level: str,
        topic: str = "math",
        difficulty: DifficultyLevel = DifficultyLevel.MEDIUM,
        num_questions: int = 5,
        student_weaknesses: List[str] = None
    ) -> Quiz:
        """Generate an adaptive quiz based on parameters"""
        
        # Get question key
        question_key = f"{grade_level}_{topic.lower()}"
        available_questions = self.question_bank.get(question_key, [])
        
        if not available_questions:
            # Fallback to grade 4 math if no questions available
            available_questions = self.question_bank.get("4_math", [])
        
        # Filter by difficulty if not adaptive
        if difficulty != DifficultyLevel.ADAPTIVE:
            available_questions = [q for q in available_questions if q.difficulty == difficulty]
        
        # Prioritize student weaknesses
        if student_weaknesses:
            weakness_questions = [q for q in available_questions if q.topic in student_weaknesses]
            if weakness_questions:
                available_questions = weakness_questions + available_questions
        
        # Select questions (avoiding duplicates)
        selected_questions = []
        used_questions = set()
        
        for _ in range(min(num_questions, len(available_questions))):
            available = [q for q in available_questions if q.id not in used_questions]
            if not available:
                break
            
            question = random.choice(available)
            selected_questions.append(question)
            used_questions.add(question.id)
        
        # Generate quiz
        quiz_id = f"quiz_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{random.randint(100, 999)}"
        
        return Quiz(
            id=quiz_id,
            title=f"Grade {grade_level} {topic.capitalize()} Quiz",
            topic=topic,
            grade_level=grade_level,
            difficulty=difficulty,
            questions=selected_questions,
            time_limit_minutes=min(len(selected_questions) * 2, 15)  # 2 minutes per question, max 15 minutes
        )
    
    def grade_quiz(
        self,
        quiz: Quiz,
        responses: List[QuizResponse]
    ) -> Dict[str, Any]:
        """Grade quiz responses and return detailed results"""
        
        results = {
            "quiz_id": quiz.id,
            "total_questions": len(quiz.questions),
            "correct_answers": 0,
            "incorrect_answers": 0,
            "score_percentage": 0.0,
            "total_time_seconds": sum(r.time_taken_seconds for r in responses),
            "question_results": [],
            "mistakes": [],
            "strengths_demonstrated": [],
            "areas_for_improvement": []
        }
        
        # Create response lookup
        response_map = {r.question_id: r for r in responses}
        
        # Grade each question
        for question in quiz.questions:
            response = response_map.get(question.id)
            if not response:
                continue
            
            question_result = {
                "question_id": question.id,
                "question": question.question,
                "correct_answer": question.options[question.correct_answer],
                "student_answer": question.options[response.selected_answer] if response.selected_answer < len(question.options) else "No answer",
                "is_correct": response.is_correct,
                "explanation": question.explanation,
                "topic": question.topic,
                "time_taken_seconds": response.time_taken_seconds
            }
            
            results["question_results"].append(question_result)
            
            if response.is_correct:
                results["correct_answers"] += 1
                if question.topic not in results["strengths_demonstrated"]:
                    results["strengths_demonstrated"].append(question.topic)
            else:
                results["incorrect_answers"] += 1
                results["mistakes"].append({
                    "question_id": question.id,
                    "topic": question.topic,
                    "difficulty": question.difficulty.value,
                    "student_answer": question.options[response.selected_answer] if response.selected_answer < len(question.options) else "No answer",
                    "correct_answer": question.options[question.correct_answer],
                    "explanation": question.explanation
                })
                if question.topic not in results["areas_for_improvement"]:
                    results["areas_for_improvement"].append(question.topic)
        
        # Calculate score
        if results["total_questions"] > 0:
            results["score_percentage"] = (results["correct_answers"] / results["total_questions"]) * 100
        
        return results

# Global instance
quiz_generator = QuizGenerator()
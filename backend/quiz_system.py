"""
Adaptive Quiz System for SnapLearn AI
Quizzes are generated in real time with the Google Gemini API from the topic and grade.
"""

import json
import re
import random
import logging
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime

from fastapi import HTTPException

from student_profile import DifficultyLevel
from llm_service import get_llm_service

logger = logging.getLogger(__name__)


@dataclass
class QuizQuestion:
    id: str
    question: str
    options: List[str]
    correct_answer: int
    explanation: str
    topic: str
    grade_level: str
    difficulty: DifficultyLevel
    blooms_level: Optional[str] = None
    cognitive_demand: Optional[str] = None


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
    """Generates quizzes in real time via the configured LLM."""

    @staticmethod
    def normalize_topic_key(topic: str) -> str:
        """Map free text to a simple subject key for copy or logging."""
        t = (topic or "math").strip().lower()
        if any(
            s in t
            for s in (
                "science",
                "biology",
                "chemistry",
                "physics",
                "water",
                "plant",
                "photosynth",
            )
        ):
            return "science"
        if any(
            s in t
            for s in (
                "math",
                "algebra",
                "arithmetic",
                "fraction",
                "geometry",
                "multipl",
                "divis",
                "add",
                "subtract",
                "equation",
                "probability",
                "area",
                "number",
            )
        ):
            return "math"
        return "math"

    @staticmethod
    def _normalize_grade(grade_level: str) -> str:
        g = (grade_level or "4").strip()
        g = re.sub(r"(?i)^grade\s*", "", g)
        return (g or "4")[:8]

    @staticmethod
    def _str_to_difficulty(s: str, fallback: DifficultyLevel) -> DifficultyLevel:
        t = (s or "").lower().strip()
        for level in DifficultyLevel:
            if level == DifficultyLevel.ADAPTIVE:
                continue
            if level.value == t:
                return level
        return fallback

    @staticmethod
    def _grade_pacing(grade: str) -> str:
        gl = QuizGenerator._normalize_grade(grade).lower()
        if gl in ("k", "0") or re.match(r"^1$|^2$", gl):
            return "Grades K through 2: one short sentence per stem, only concrete and familiar ideas, 4 very distinct options."
        if re.match(r"^3$|^4$", gl):
            return "Grades 3 to 4: one or two short sentences, light reasoning, number sense and short word problems, age-appropriate vocabulary."
        if re.match(r"^5$|^6$", gl):
            return "Grades 5 to 6: multi-step reasoning, compare or explain, word problems, still standard school vocabulary only."
        return "Grades 7 to 8: deeper concepts, more abstract stems if still fair for the grade, multi-step and justified distractors that are plausible but wrong."

    @staticmethod
    def _blooms_taxonomy_levels(grade: str, difficulty: str) -> str:
        """Generate Bloom's taxonomy guidance based on grade and difficulty level"""
        gl = QuizGenerator._normalize_grade(grade).lower()
        
        # Base cognitive levels by grade
        if gl in ("k", "0", "1", "2"):
            base_levels = "Focus on REMEMBERING (recall facts) and UNDERSTANDING (explain ideas). Avoid analysis or evaluation."
        elif gl in ("3", "4"):
            base_levels = "Mix REMEMBERING, UNDERSTANDING, and basic APPLYING (use knowledge in familiar situations)."
        elif gl in ("5", "6"):
            base_levels = "Include REMEMBERING, UNDERSTANDING, APPLYING, and simple ANALYZING (break down information, compare)."
        else:  # 7-8 and above
            base_levels = "Use all levels: REMEMBERING, UNDERSTANDING, APPLYING, ANALYZING, and basic EVALUATING (make judgments, critique)."
        
        # Adjust based on difficulty
        if difficulty == "easy":
            emphasis = "Emphasize lower-order thinking: primarily REMEMBERING and UNDERSTANDING."
        elif difficulty == "medium":
            emphasis = "Balance lower and higher-order thinking: UNDERSTANDING and APPLYING with some ANALYZING."
        else:  # hard
            emphasis = "Focus on higher-order thinking: ANALYZING, EVALUATING, and age-appropriate CREATING."
        
        return f"BLOOM'S TAXONOMY GUIDANCE: {base_levels} {emphasis} Each question should clearly target one cognitive level."

    @staticmethod
    def _parse_quiz_json_block(raw: str) -> dict:
        t = (raw or "").strip()
        if not t or t.startswith("Error generating content"):
            raise ValueError("empty or error response")
        m = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", t, re.IGNORECASE)
        if m:
            t = m.group(1).strip()
        i0, i1 = t.find("{"), t.rfind("}")
        if i0 < 0 or i1 < i0:
            raise ValueError("no JSON object found")
        return json.loads(t[i0 : i1 + 1])

    @staticmethod
    def _valid_question(d: dict) -> bool:
        q = d.get("question", "").strip()
        opts = d.get("options") or d.get("choices")
        if not q or not isinstance(opts, list) or len(opts) < 2:
            return False
        if len(opts) != 4:
            return False
        s = {str(x).strip() for x in opts if str(x).strip()}
        if len(s) < 4:
            return False
        ca = d.get("correct_answer", d.get("answer_index", d.get("correct_index")))
        if not isinstance(ca, int) or not (0 <= ca < 4):
            return False
        ex = d.get("explanation", d.get("reason", ""))
        if not (ex or "").strip():
            return False
        return True

    @staticmethod
    def _rows_to_questions(
        rows: List[dict],
        grade: str,
        default_diff: DifficultyLevel,
        base_topic: str,
    ) -> List[QuizQuestion]:
        out: List[QuizQuestion] = []
        for n, d in enumerate(rows, start=1):
            if not QuizGenerator._valid_question(d):
                continue
            opts = [str(x).strip() for x in d["options"]]
            if len(set(opts)) < 4:
                continue
            ca = int(d["correct_answer"] if "correct_answer" in d else d.get("answer_index", d.get("correct_index", 0)))
            sub = (d.get("subtopic") or d.get("sub_topic") or base_topic).strip() or base_topic
            per_d = default_diff
            if "difficulty" in d:
                per_d = QuizGenerator._str_to_difficulty(str(d["difficulty"]), default_diff)
            qid = f"q_{n}_{random.randint(100, 999)}"
            out.append(
                QuizQuestion(
                    id=qid,
                    question=(d.get("question") or "").strip(),
                    options=opts,
                    correct_answer=ca,
                    explanation=(d.get("explanation") or d.get("reason") or "").strip(),
                    topic=sub,
                    grade_level=grade,
                    difficulty=per_d,
                    blooms_level=(d.get("blooms_level") or "understanding").strip().lower(),
                    cognitive_demand=(d.get("cognitive_demand") or "").strip(),
                )
            )
        return out

    async def generate_quiz_async(
        self,
        grade_level: str,
        topic: str,
        num_questions: int,
        effective_difficulty: DifficultyLevel,
        student_weaknesses: Optional[List[str]] = None,
    ) -> Quiz:
        """
        Real-time multi-choice quiz for the given topic, scoped to the grade band and target difficulty.
        """
        n = max(1, min(10, int(num_questions)))
        g = self._normalize_grade(grade_level)
        subject_hint = self.normalize_topic_key(topic)
        weaknesses = (student_weaknesses or [])[:6]
        wf = (", ".join(weaknesses)) if weaknesses else "none given"

        system = (
            "You are an expert K through 8 curriculum writer with deep knowledge of Bloom's Taxonomy. "
            "You create pedagogically sound assessments that measure different cognitive levels appropriately. "
            "You output only valid minified JSON with no backticks, no comments, and no text before or after the JSON object."
        )
        
        blooms_guidance = self._blooms_taxonomy_levels(g, effective_difficulty.value)
        
        user = f"""Build a {n}-item multiple choice quiz following Bloom's Taxonomy principles.
TOPIC: {topic.strip() or "general review"}
BROAD SUBJECT HINT: {subject_hint} (the quiz must stay on the topic, not a random other subject)
STUDENT GRADE (all stems and solutions must be appropriate for this level): {g}
{self._grade_pacing(g)}

{blooms_guidance}

PRODUCTION QUALITY REQUIREMENTS:
- Each question targets a specific Bloom's level (include level in metadata)
- Four distinct, plausible options with exactly one correct answer (index 0-3)
- Distractors based on common misconceptions or partial understanding
- Clear, unambiguous language appropriate for the grade level
- Explanations that reinforce learning, not just correctness

REQUIRED DIFFICULTY TARGET FOR THIS SET: {effective_difficulty.value}
When "easy": Focus on recall and basic understanding
When "medium": Include application and analysis appropriate for grade  
When "hard": Challenge with evaluation and synthesis within grade limits

AREAS THE STUDENT SHOULD PRACTICE: {wf}

Output one JSON object only, with this exact shape (double quotes, valid JSON):
{{
  "title": "string",
  "questions": [
    {{
      "question": "string",
      "options": ["string", "string", "string", "string"],
      "correct_answer": 0,
      "explanation": "Clear explanation that reinforces learning and addresses common misconceptions",
      "subtopic": "short label",
      "difficulty": "{effective_difficulty.value}",
      "blooms_level": "remembering|understanding|applying|analyzing|evaluating|creating",
      "cognitive_demand": "Brief description of thinking required"
    }}
  ]
}}"""

        llm = get_llm_service()
        raw = await llm.generate(
            prompt=user,
            system_prompt=system,
            temperature=0.35,
            max_tokens=4500,
        )
        if not raw or raw.strip().startswith("Error generating content"):
            logger.error("LLM could not build quiz: %s", (raw or "")[:500])
            raise HTTPException(
                status_code=503,
                detail="The quiz could not be generated. Set GOOGLE_API_KEY or GEMINI_API_KEY in backend .env, "
                "confirm GEMINI_MODEL, billing, and network, then try again.",
            )
        data = None
        for attempt in (1, 2):
            try:
                data = self._parse_quiz_json_block(raw)
                break
            except Exception as e:
                if attempt == 1:
                    logger.warning("First quiz JSON parse failed, retrying with repair prompt: %s", e)
                    repair = f"""The following text is invalid JSON or wrong shape. Return ONLY a valid minified JSON object
with "title" and "questions" as specified earlier (same {n} questions, topic {topic}, grade {g}, difficulty {effective_difficulty.value}).

FAULTY OUTPUT:
{raw[:12000]}

If you must infer missing fields, do so, but do not add markdown."""
                    raw = await llm.generate(
                        prompt=repair,
                        system_prompt=system,
                        temperature=0.2,
                        max_tokens=4500,
                    )
                else:
                    logger.error("Quiz JSON still invalid: %s", e)
        if not data or not isinstance(data, dict):
            raise HTTPException(status_code=503, detail="The model returned a quiz in an unexpected format. Please try again.")

        rows = data.get("questions")
        if not isinstance(rows, list) or not rows:
            raise HTTPException(status_code=503, detail="The model did not return any questions. Please try a shorter or clearer topic.")

        selected = self._rows_to_questions(
            [x for x in rows if isinstance(x, dict)],
            g,
            effective_difficulty,
            topic.strip() or "General",
        )
        if len(selected) < n:
            logger.warning("Model returned %d valid of %d requested; retrying with stricter prompt is possible", len(selected), n)
        if len(selected) < max(1, n // 2 if n else 0):
            raise HTTPException(
                status_code=503,
                detail="The model could not form enough well-formed items. Simplify the topic and try again.",
            )

        quiz_id = f"quiz_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{random.randint(100, 999)}"
        title = (data.get("title") or f"Grade {g} {topic}").strip()
        tlim = min(max(len(selected) * 2, 3), 25)

        return Quiz(
            id=quiz_id,
            title=title,
            topic=topic.strip() or "general",
            grade_level=g,
            difficulty=effective_difficulty,
            questions=selected,
            time_limit_minutes=tlim,
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
        response_map = {r.question_id: r for r in responses}

        for question in quiz.questions:
            response = response_map.get(question.id)
            if not response:
                continue
            n_opts = len(question.options)
            sel = response.selected_answer
            in_range = isinstance(sel, int) and 0 <= sel < n_opts
            is_correct = in_range and (sel == question.correct_answer)
            question_result = {
                "question_id": question.id,
                "question": question.question,
                "correct_answer": question.options[question.correct_answer],
                "student_answer": question.options[sel] if in_range else "No answer",
                "is_correct": is_correct,
                "explanation": question.explanation,
                "topic": question.topic,
                "time_taken_seconds": response.time_taken_seconds
            }
            results["question_results"].append(question_result)
            if is_correct:
                results["correct_answers"] += 1
                if question.topic not in results["strengths_demonstrated"]:
                    results["strengths_demonstrated"].append(question.topic)
            else:
                results["incorrect_answers"] += 1
                results["mistakes"].append({
                    "question_id": question.id,
                    "topic": question.topic,
                    "difficulty": question.difficulty.value,
                    "student_answer": (
                        question.options[response.selected_answer] if
                        0 <= response.selected_answer < len(question.options) else
                        "No answer"
                    ),
                    "correct_answer": question.options[question.correct_answer],
                    "explanation": question.explanation
                })
                if question.topic not in results["areas_for_improvement"]:
                    results["areas_for_improvement"].append(question.topic)
        if results["total_questions"] > 0:
            results["score_percentage"] = (results["correct_answers"] / results["total_questions"]) * 100
        return results


# Global instance
quiz_generator = QuizGenerator()

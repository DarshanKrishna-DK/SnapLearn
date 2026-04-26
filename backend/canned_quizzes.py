"""
Canned multiple-choice sets for high-signal topics (no LLM). Used when the UI topic matches.
"""
from __future__ import annotations

import random
import re
from datetime import datetime
from typing import List, Optional, Tuple

from student_profile import DifficultyLevel
from quiz_system import Quiz, QuizQuestion, QuizGenerator

Row = Tuple[str, List[str], int, str, str]


def _topic_key(topic: str) -> Optional[str]:
    x = (topic or "").lower()
    if re.search(r"\bmatrices?\b|matrix\b", x):
        return "matrices"
    if re.search(r"factorial", x):
        return "factorials"
    return None


# (stem, [A,B,C,D], correct_index, explanation, subtopic)
MATRICES_BANK: List[Row] = [
    (
        "A matrix is best described as:",
        ["A rectangular array of numbers", "A single list of values only", "A circle of equations", "A function with no input"],
        0,
        "A matrix is a rectangular arrangement of numbers (or symbols) in rows and columns.",
        "definition",
    ),
    (
        "The entry in row 2, column 1 of [[10, 20], [30, 40]] is:",
        ["30", "20", "40", "10"],
        0,
        "Row index then column: second row, first column is 30.",
        "indexing",
    ),
    (
        "If A is 2x3 and B is 3x2, the product AB has shape:",
        ["2x2", "3x3", "2x3", "3x2"],
        0,
        "Multiply (m x n) by (n x p) gives m x p: here 2x2.",
        "multiplication size",
    ),
    (
        "The 2x2 identity matrix I satisfies I M = for any compatible M:",
        ["M", "0", "2M", "M transposed only"],
        0,
        "I acts as the multiplicative identity, leaving M unchanged on the left (when dimensions allow).",
        "identity",
    ),
    (
        "det([[2, 0], [0, 3]]) equals:",
        ["6", "5", "0", "1"],
        0,
        "For a diagonal matrix, det is the product of the diagonal: 2 * 3 = 6.",
        "determinant",
    ),
    (
        "[[1, 2], [0, 1]] + [[1, 0], [0, 1]] equals:",
        ["[[2, 2], [0, 2]]", "[[1, 2], [0, 1]]", "[[0, 2], [0, 0]]", "[[1, 0], [0, 1]]"],
        0,
        "Add corresponding entries: (1+1), (2+0), (0+0), (1+1).",
        "addition",
    ),
    (
        "A zero matrix 2x2 added to any 2x2 matrix M gives:",
        ["M", "2M", "0", "A matrix of all ones"],
        0,
        "Adding the zero matrix element-wise leaves M unchanged.",
        "addition",
    ),
    (
        "Rows and columns of a 3x4 matrix A are numbered starting at:",
        ["1 for both in most textbook conventions", "0 and 0 only in programming", "3 and 4", "1 for rows, 0 for columns always"],
        0,
        "In math, row/column labels usually start at 1 unless a context uses 0-based indexing; here we mean standard 1-based math indexing.",
        "conventions",
    ),
    (
        "A square matrix A has an inverse (when it exists) such that:",
        ["A * A^(-1) = I and A^(-1) * A = I (under sizes that match)", "A^2 = 0", "A is always all ones", "det(A) = 0 always"],
        0,
        "Inverses compose with the identity on both sides for invertible square matrices.",
        "inverse",
    ),
    (
        "Which of these is true for 2x2 real matrices in general (without extra conditions)?",
        ["AB can differ from BA for some A and B", "AB always equals BA for every A and B", "Matrix product is never defined", "You can only add matrices of different sizes"],
        0,
        "Matrix multiplication is not commutative in general; a classic counterexample exists in 2x2.",
        "commutativity",
    ),
]

FACTORIALS_BANK: List[Row] = [
    (
        "5! equals:",
        ["120", "60", "20", "24"],
        0,
        "5! = 1 * 2 * 3 * 4 * 5 = 120.",
        "definition",
    ),
    (
        "0! is defined as:",
        ["1", "0", "undefined", "10"],
        0,
        "By convention, 0! = 1, consistent with the empty product.",
        "definition",
    ),
    (
        "6! / 5! equals:",
        ["6", "1", "5", "30"],
        0,
        "6! / 5! = 6 in one cancellation step.",
        "simplify",
    ),
    (
        "(3!)(3!) =",
        ["36", "6", "9", "12"],
        0,
        "3! = 6, and 6 * 6 = 36.",
        "arithmetic",
    ),
    (
        "Which grows fastest for large positive integers n?",
        ["n!", "2^n", "n^2", "n"],
        0,
        "Factorial dominates typical exponentials in growth rate in the long run.",
        "growth",
    ),
    (
        "1! * 2! * 3! =",
        ["12", "6", "3", "36"],
        0,
        "1 * 2 * 6 = 12.",
        "arithmetic",
    ),
    (
        "4! is equal to the number of permutations of 4 distinct objects, which is:",
        ["24", "4", "10", "16"],
        0,
        "4! = 24 linear orderings of 4 distinct items.",
        "permutations",
    ),
    (
        "For positive integers, (n+1)! / n! =",
        ["n+1", "n", "1", "n!"],
        0,
        "(n+1)! = (n+1) * n! so the ratio is n+1.",
        "algebra",
    ),
    (
        "10! ends with this many trailing zeros in base 10 (count only at the end):",
        ["2", "0", "1", "3"],
        0,
        "10! = 2^8 * 3^4 * 5^2 * 7^1; count pairs of 2*5: two 5s, so 2 trailing zeros in base 10 (3628800).",
        "trailing zeros",
    ),
    (
        "7! =",
        ["5040", "42", "720", "100"],
        0,
        "7! = 5040.",
        "arithmetic",
    ),
]


def build_canned_quiz(topic: str, num_questions: int, grade_level: str) -> Optional[Quiz]:
    which = _topic_key(topic)
    if not which:
        return None
    n = max(1, min(10, int(num_questions)))
    bank = MATRICES_BANK if which == "matrices" else FACTORIALS_BANK
    g = QuizGenerator._normalize_grade(grade_level)
    if n > len(bank):
        chosen = (bank * ((n // len(bank)) + 1))[:n]
    else:
        chosen = bank[:n]
    qlist: List[QuizQuestion] = []
    for i, row in enumerate(chosen):
        q, opts, ca, ex, sub = row
        qlist.append(
            QuizQuestion(
                id=f"{which}_q_{i+1}",
                question=q,
                options=list(opts),
                correct_answer=ca,
                explanation=ex,
                topic=sub,
                grade_level=g,
                difficulty=DifficultyLevel.MEDIUM,
                blooms_level="understanding",
                cognitive_demand="recall and light reasoning",
            )
        )
    quiz_id = f"quiz_canned_{which}_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{random.randint(100, 999)}"
    title = "Checkpoint: Matrices" if which == "matrices" else "Checkpoint: Factorials"
    tlim = min(max(len(qlist) * 2, 3), 25)
    return Quiz(
        id=quiz_id,
        title=title,
        topic=topic.strip() or which,
        grade_level=g,
        difficulty=DifficultyLevel.MEDIUM,
        questions=qlist,
        time_limit_minutes=tlim,
    )

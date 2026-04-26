"""
In-memory store for generated quizzes so /api/quiz/submit grades the same items the user saw.
"""

from __future__ import annotations

from typing import Dict, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from quiz_system import Quiz

_store: Dict[str, "Quiz"] = {}


def put(quiz: "Quiz") -> None:
    if quiz and getattr(quiz, "id", None):
        _store[quiz.id] = quiz


def get(quiz_id: str) -> Optional["Quiz"]:
    return _store.get(quiz_id) if quiz_id else None


def pop(quiz_id: str) -> Optional["Quiz"]:
    return _store.pop(quiz_id, None) if quiz_id else None

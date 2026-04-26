"""Load SnapSnap demo state helpers from the repository without package install."""
import sys
from pathlib import Path

_root = Path(__file__).resolve().parent.parent
_snp = _root / "SnapSnap" / "mock_scripts"
if _snp.is_dir() and str(_snp) not in sys.path:
    sys.path.insert(0, str(_snp))

from demo_presentation_state import (  # noqa: E402
    try_unlock_after_quiz,
    reset_student_presentation_state,
)

__all__ = ["try_unlock_after_quiz", "reset_student_presentation_state"]

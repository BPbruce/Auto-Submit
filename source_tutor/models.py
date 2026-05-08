from __future__ import annotations

from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from typing import Any, Literal


QuestionType = Literal["single_choice", "multi_choice", "true_false", "explain"]
Difficulty = Literal["easy", "medium", "hard"]


@dataclass
class Evidence:
    file_path: str
    start_line: int
    end_line: int
    code_snippet: str


@dataclass
class CodeChunk:
    file_path: str
    chunk_type: Literal["class", "function", "module"]
    name: str
    start_line: int
    end_line: int
    source: str


@dataclass
class Question:
    question_type: QuestionType
    question: str
    options: list[str]
    answer: str
    explanation: str
    evidence: Evidence
    difficulty: Difficulty
    concept: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class SessionRecord:
    file_path: str
    concept: str
    question: str
    user_answer: str
    is_correct: bool
    error_reason: str
    review_count: int = 0
    marked_unknown: bool = False
    timestamp: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat(timespec="seconds")
    )

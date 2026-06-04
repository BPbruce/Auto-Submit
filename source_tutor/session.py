from __future__ import annotations

import json
from collections import Counter
from dataclasses import asdict
from pathlib import Path
from typing import Any

from .models import Question, SessionRecord


class SessionStore:
    def __init__(self, path: str = ".source_tutor/session.json") -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if not self.path.exists():
            self.path.write_text("[]", encoding="utf-8")

    def add_record(self, record: SessionRecord) -> None:
        data = self.load_all()
        data.append(asdict(record))
        self.path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

    def load_all(self) -> list[dict[str, Any]]:
        return json.loads(self.path.read_text(encoding="utf-8"))

    def build_record(self, question: Question, user_answer: str, is_correct: bool, error_reason: str = "") -> SessionRecord:
        return SessionRecord(
            file_path=question.evidence.file_path,
            concept=question.concept,
            question=question.question,
            user_answer=user_answer,
            is_correct=is_correct,
            error_reason=error_reason,
        )

    def review_candidates(self) -> list[dict[str, Any]]:
        data = self.load_all()
        wrong = [r for r in data if not r.get("is_correct", False)]
        unknown = [r for r in data if r.get("marked_unknown", False)]
        return wrong + unknown

    def stats(self) -> dict[str, Any]:
        """Return aggregate learning progress for the current session file."""
        records = self.load_all()
        total = len(records)
        correct = sum(1 for record in records if record.get("is_correct", False))
        wrong = total - correct
        marked_unknown = sum(1 for record in records if record.get("marked_unknown", False))
        accuracy = round(correct / total * 100, 1) if total else 0.0

        concepts = Counter(record.get("concept", "未分类") or "未分类" for record in records)
        files = Counter(record.get("file_path", "未知文件") or "未知文件" for record in records)

        return {
            "total": total,
            "correct": correct,
            "wrong": wrong,
            "marked_unknown": marked_unknown,
            "accuracy": accuracy,
            "concepts": concepts.most_common(),
            "files": files.most_common(),
            "latest": records[-1] if records else None,
        }

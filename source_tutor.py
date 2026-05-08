from __future__ import annotations

import argparse

from source_tutor.chunker import CodeChunker
from source_tutor.cli import run_quiz, run_review
from source_tutor.loader import load_python_files, read_text
from source_tutor.question_generator import RuleBasedQuestionGenerator
from source_tutor.session import SessionStore


def build_questions(path: str):
    files = load_python_files(path)
    chunker = CodeChunker()
    generator = RuleBasedQuestionGenerator()
    questions = []
    for file in files:
        source = read_text(file)
        chunks = chunker.chunk_file(file, source)
        for chunk in chunks:
            questions.extend(generator.generate(chunk))
    return questions


def main() -> None:
    parser = argparse.ArgumentParser(description="源码学习交互器（MVP）")
    sub = parser.add_subparsers(dest="command")
    review_parser = sub.add_parser("review", help="进入复习模式")
    review_parser.add_argument("--session", default=".source_tutor/session.json")

    parser.add_argument("--path", help="源码文件/目录路径")
    parser.add_argument("--session", default=".source_tutor/session.json")
    args = parser.parse_args()

    store = SessionStore(args.session)

    if args.command == "review":
        run_review(SessionStore(args.session))
        return

    if not args.path:
        parser.error("普通学习模式必须提供 --path")

    questions = build_questions(args.path)
    if not questions:
        print("没有找到可学习的 Python 源码。")
        return

    run_quiz(questions, store)


if __name__ == "__main__":
    main()

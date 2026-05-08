from pathlib import Path

from source_tutor.chunker import CodeChunker
from source_tutor.loader import read_text
from source_tutor.question_generator import RuleBasedQuestionGenerator


def test_chunk_and_question_generation():
    file_path = Path(__file__).resolve().parents[1] / "source_tutor" / "models.py"
    source = read_text(file_path)
    chunks = CodeChunker().chunk_file(file_path, source)
    assert chunks

    questions = RuleBasedQuestionGenerator().generate(chunks[0])
    assert questions
    assert questions[0].evidence.file_path.endswith("models.py")

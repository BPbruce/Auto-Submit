from source_tutor.models import SessionRecord
from source_tutor.session import SessionStore


def test_session_stats_summarizes_records(tmp_path):
    store = SessionStore(str(tmp_path / "session.json"))
    store.add_record(
        SessionRecord(
            file_path="demo.py",
            concept="function_signature",
            question="函数参数是什么？",
            user_answer="A",
            is_correct=True,
            error_reason="",
        )
    )
    store.add_record(
        SessionRecord(
            file_path="demo.py",
            concept="return",
            question="是否包含 return？",
            user_answer="B",
            is_correct=False,
            error_reason="答案与源码证据不一致",
            marked_unknown=True,
        )
    )

    stats = store.stats()

    assert stats["total"] == 2
    assert stats["correct"] == 1
    assert stats["wrong"] == 1
    assert stats["marked_unknown"] == 1
    assert stats["accuracy"] == 50.0
    assert stats["concepts"] == [("function_signature", 1), ("return", 1)]
    assert stats["files"] == [("demo.py", 2)]
    assert stats["latest"]["question"] == "是否包含 return？"

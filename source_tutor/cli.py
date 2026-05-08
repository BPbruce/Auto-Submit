from __future__ import annotations

from collections import deque

from .models import Question
from .session import SessionStore


def _show_question(i: int, q: Question) -> None:
    print(f"\n【问题 {i}｜{q.difficulty}｜concept: {q.concept}】")
    print(q.question)
    for idx, option in zip(["A", "B", "C", "D"], q.options):
        print(f"{idx}. {option}")


def run_quiz(questions: list[Question], store: SessionStore) -> None:
    queue = deque(questions)
    i = 1
    while queue:
        q = queue[0]
        _show_question(i, q)
        user = input("请选择（A/B/C/D，hint/source/why/next/quit）> ").strip()

        if user.lower() == "quit":
            print("已退出，学习记录已保存。")
            break
        if user.lower() in {"why", "解释"}:
            print(f"解释：{q.explanation}")
            continue
        if user.lower() == "hint":
            print(f"提示：请关注 {q.evidence.file_path}:{q.evidence.start_line}-{q.evidence.end_line} 的定义与语句。")
            continue
        if user.lower() == "source":
            print(q.evidence.code_snippet)
            continue
        if user.lower() == "next":
            queue.popleft()
            i += 1
            continue

        is_correct = user.upper() == q.answer
        if is_correct:
            print("回答正确。")
            print(q.explanation)
            rec = store.build_record(q, user, True)
        else:
            print("这题有个常见误区：容易把局部变量作用和函数目的混淆。")
            print(f"正确答案：{q.answer}。{q.explanation}")
            rec = store.build_record(q, user, False, error_reason="答案与源码证据不一致")
        store.add_record(rec)
        queue.popleft()
        i += 1


def run_review(store: SessionStore) -> None:
    candidates = store.review_candidates()
    if not candidates:
        print("暂无需要复习的题目。")
        return
    print("复习优先队列（错题/标记不懂）：")
    for idx, item in enumerate(candidates, start=1):
        print(f"{idx}. [{item['concept']}] {item['question']} | 你的答案: {item['user_answer']}")

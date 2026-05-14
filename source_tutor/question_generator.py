from __future__ import annotations

import ast
from abc import ABC, abstractmethod

from .models import CodeChunk, Evidence, Question


UNSURE = "无法从当前源码片段可靠判断"


class BaseQuestionGenerator(ABC):
    @abstractmethod
    def generate(self, chunk: CodeChunk) -> list[Question]:
        raise NotImplementedError


class RuleBasedQuestionGenerator(BaseQuestionGenerator):
    def generate(self, chunk: CodeChunk) -> list[Question]:
        questions: list[Question] = []
        questions.append(self._main_purpose(chunk))

        parsed = ast.parse(chunk.source)
        fn = next((n for n in ast.walk(parsed) if isinstance(n, ast.FunctionDef)), None)
        if fn:
            questions.append(self._function_args(chunk, fn))
            questions.append(self._return_question(chunk, fn))

        return questions

    def _evidence(self, chunk: CodeChunk) -> Evidence:
        return Evidence(
            file_path=chunk.file_path,
            start_line=chunk.start_line,
            end_line=chunk.end_line,
            code_snippet=chunk.source,
        )

    def _main_purpose(self, chunk: CodeChunk) -> Question:
        opts = [
            f"定义了一个{chunk.chunk_type}，名称是 {chunk.name}",
            "执行了网络请求并下载参数",
            "删除了磁盘上的临时文件",
            "无法从当前源码片段可靠判断",
        ]
        return Question(
            question_type="single_choice",
            question=f"这个代码片段的主要作用是什么？（{chunk.name}）",
            options=opts,
            answer="A",
            explanation=(
                f"依据 {chunk.file_path}:{chunk.start_line}-{chunk.end_line}，该片段声明了 {chunk.chunk_type} {chunk.name}。"
            ),
            evidence=self._evidence(chunk),
            difficulty="easy",
            concept=chunk.chunk_type,
        )

    def _function_args(self, chunk: CodeChunk, fn: ast.FunctionDef) -> Question:
        args = [a.arg for a in fn.args.args]
        answer_text = ", ".join(args) if args else "无参数"
        wrong = "输入参数仅包含 data"
        options = [f"参数包含：{answer_text}", wrong, UNSURE, "参数未知且不可见"]
        return Question(
            question_type="single_choice",
            question=f"函数 {fn.name} 的输入参数最符合下面哪项？",
            options=options,
            answer="A",
            explanation=(
                f"依据源码行 {chunk.start_line}-{chunk.end_line} 的函数签名可直接读取参数列表：{answer_text}。"
            ),
            evidence=self._evidence(chunk),
            difficulty="medium",
            concept="function_signature",
        )

    def _return_question(self, chunk: CodeChunk, fn: ast.FunctionDef) -> Question:
        has_return = any(isinstance(n, ast.Return) for n in ast.walk(fn))
        answer = "A" if has_return else "B"
        options = ["该函数包含 return 语句", "该函数不包含 return 语句", UNSURE, "该函数会抛出异常后退出"]
        explanation = (
            f"依据 {chunk.file_path}:{chunk.start_line}-{chunk.end_line} 中的函数体扫描 return 节点得到结论。"
            + ("这是基于源码的推断。" if has_return else "")
        )
        return Question(
            question_type="true_false",
            question=f"判断：函数 {fn.name} 是否显式包含 return 语句？",
            options=options,
            answer=answer,
            explanation=explanation,
            evidence=self._evidence(chunk),
            difficulty="easy",
            concept="return",
        )


class LLMQuestionGenerator(BaseQuestionGenerator):
    def generate(self, chunk: CodeChunk) -> list[Question]:
        raise NotImplementedError("预留给未来的 LLM 接口实现。")

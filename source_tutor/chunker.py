from __future__ import annotations

import ast
from pathlib import Path

from .models import CodeChunk


class CodeChunker:
    def chunk_file(self, file_path: Path, source: str) -> list[CodeChunk]:
        tree = ast.parse(source)
        lines = source.splitlines()
        chunks: list[CodeChunk] = []

        for node in tree.body:
            if isinstance(node, ast.ClassDef):
                chunks.append(self._build_chunk(file_path, source, lines, node, "class"))
            elif isinstance(node, ast.FunctionDef):
                chunks.append(self._build_chunk(file_path, source, lines, node, "function"))

        if not chunks:
            chunks.append(
                CodeChunk(
                    file_path=str(file_path),
                    chunk_type="module",
                    name=file_path.stem,
                    start_line=1,
                    end_line=len(lines),
                    source=source,
                )
            )
        return chunks

    def _build_chunk(self, file_path: Path, source: str, lines: list[str], node: ast.AST, chunk_type: str) -> CodeChunk:
        start = getattr(node, "lineno", 1)
        end = getattr(node, "end_lineno", start)
        snippet = "\n".join(lines[start - 1 : end])
        name = getattr(node, "name", file_path.stem)
        return CodeChunk(
            file_path=str(file_path),
            chunk_type=chunk_type,
            name=name,
            start_line=start,
            end_line=end,
            source=snippet,
        )

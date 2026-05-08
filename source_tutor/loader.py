from __future__ import annotations

from pathlib import Path


def load_python_files(path: str) -> list[Path]:
    target = Path(path).expanduser().resolve()
    if not target.exists():
        raise FileNotFoundError(f"Path not found: {target}")

    if target.is_file():
        return [target] if target.suffix == ".py" else []

    return sorted(p for p in target.rglob("*.py") if p.is_file())


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")

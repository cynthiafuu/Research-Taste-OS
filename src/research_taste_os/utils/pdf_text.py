from __future__ import annotations

from pathlib import Path


def read_text_source(path_or_text: str | None) -> str:
    if not path_or_text:
        return ""
    path = Path(path_or_text)
    if path.exists() and path.is_file():
        if path.suffix.lower() in {".txt", ".md"}:
            return path.read_text(errors="ignore")
        raise SystemExit("MVP supports direct text, .txt, or .md input. Paste PDF text or add PDF parsing later.")
    return path_or_text
